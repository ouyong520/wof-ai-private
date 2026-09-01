from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
PYLAUNCH_DIR = HERE.parent / "PYLAUNCH"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(PYLAUNCH_DIR) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH_DIR))

from wof_launcher.browser import find_browser, probe_endpoint
from wof_launcher.cdp import CdpClient
from wof_launcher.fleet import FLEET_MANIFEST_VERSION, default_fleet_root, default_manifest_path
from fleet_discovery_v2 import discover_fleet_status


DEFAULT_BASE_PORT = 9323
DEFAULT_POLL_SECONDS = 2.0
MAX_FLEET = 50


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)


def http_json(url: str, timeout: float = 0.8) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "WOF-Browser-Fleet/0.2"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def screen_size() -> tuple[int, int]:
    if os.name == "nt":
        try:
            user32 = ctypes.windll.user32
            width = int(user32.GetSystemMetrics(0))
            height = int(user32.GetSystemMetrics(1))
            if width > 0 and height > 0:
                return width, height
        except Exception:
            pass
    return 1920, 1080


def grid_layout(count: int, width: int, height: int) -> list[tuple[int, int, int, int]]:
    if count < 1:
        return []
    cols = max(1, math.ceil(math.sqrt(count)))
    rows = max(1, math.ceil(count / cols))
    cell_w = max(1, width // cols)
    cell_h = max(1, height // rows)
    result: list[tuple[int, int, int, int]] = []
    for index in range(count):
        col = index % cols
        row = index // cols
        x = col * cell_w
        y = row * cell_h
        w = cell_w if col < cols - 1 else max(1, width - x)
        h = cell_h if row < rows - 1 else max(1, height - y)
        result.append((x, y, w, h))
    return result


def validate_count(value: int) -> int:
    if value < 1 or value > MAX_FLEET:
        raise ValueError(f"fleet size must be 1..{MAX_FLEET}")
    return value


def endpoint_matches_runtime(runtime_port: int, endpoint: Any) -> bool:
    if str(getattr(endpoint, "host", "")) != "127.0.0.1":
        return False
    try:
        if int(getattr(endpoint, "port", -1)) != runtime_port:
            return False
    except (TypeError, ValueError):
        return False
    try:
        parsed = urlparse(str(getattr(endpoint, "websocket_url", "")))
        ws_port = parsed.port
    except ValueError:
        return False
    return parsed.scheme in {"ws", "wss"} and parsed.hostname in {"127.0.0.1", "localhost", "::1"} and ws_port == runtime_port


@dataclass
class FleetSettings:
    browser: str = "auto"
    browser_path: str | None = None
    game_url: str | None = None
    base_port: int = DEFAULT_BASE_PORT

    @classmethod
    def load(cls, path: Path) -> "FleetSettings":
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls()
        if not isinstance(raw, dict):
            return cls()
        browser = str(raw.get("browser") or "auto").lower()
        if browser not in {"auto", "chrome", "edge"}:
            browser = "auto"
        try:
            port = int(raw.get("basePort", DEFAULT_BASE_PORT))
        except (TypeError, ValueError):
            port = DEFAULT_BASE_PORT
        return cls(
            browser=browser,
            browser_path=str(raw.get("browserPath")) if raw.get("browserPath") else None,
            game_url=str(raw.get("gameUrl")) if raw.get("gameUrl") else None,
            base_port=port,
        )

    def save(self, path: Path) -> None:
        atomic_write_json(
            path,
            {
                "version": "wof-browser-fleet-settings-v1",
                "browser": self.browser,
                "browserPath": self.browser_path,
                "gameUrl": self.game_url,
                "basePort": self.base_port,
            },
        )


@dataclass
class InstanceRuntime:
    instance_id: int
    port: int
    profile_dir: Path
    window: tuple[int, int, int, int]
    game_url: str | None
    process: subprocess.Popen[Any] | None = None
    launched_at: str = field(default_factory=utc_now)
    browser_name: str | None = None
    browser_ok: bool = False
    page_ok: bool = False
    page_count: int = 0
    worker_ok: bool = False
    worker_count: int = 0
    worker_discovery_path: str | None = None
    related_topology_count: int = 0
    worker_detail: str | None = None
    last_error: str | None = None

    @property
    def pid(self) -> int | None:
        return self.process.pid if self.process is not None else None


class FleetManager:
    def __init__(
        self,
        *,
        settings_path: Path | None = None,
        manifest_path: Path | None = None,
        poll_seconds: float = DEFAULT_POLL_SECONDS,
    ) -> None:
        root = default_fleet_root()
        self.settings_path = settings_path or (root / "settings.json")
        self.manifest_path = manifest_path or default_manifest_path()
        self.settings = FleetSettings.load(self.settings_path)
        self.poll_seconds = poll_seconds
        self.run_id = uuid.uuid4().hex[:12]
        self.instances: dict[int, InstanceRuntime] = {}
        self.browser_executable: Path | None = None
        self._stop = threading.Event()
        self._monitor_thread: threading.Thread | None = None
        self._lock = threading.RLock()

    def configure_interactive(self) -> None:
        current = self.settings
        print("WOF Browser Fleet first-time configuration")
        print("Leave URL blank if you want empty WOF-ready browser windows.")
        browser = input(f"Browser [auto/chrome/edge] ({current.browser}): ").strip().lower()
        if browser in {"auto", "chrome", "edge"}:
            current.browser = browser
        url = input(f"WOF game/page URL ({current.game_url or 'blank'}): ").strip()
        if url:
            current.game_url = url
        elif current.game_url is None:
            current.game_url = None
        current.save(self.settings_path)
        self.settings = current
        print(f"Saved: {self.settings_path}")

    def _resolve_browser(self) -> Path:
        if self.browser_executable and self.browser_executable.is_file():
            return self.browser_executable
        executable = find_browser(self.settings.browser, self.settings.browser_path)
        if not executable:
            raise RuntimeError("Chrome/Edge executable not found")
        self.browser_executable = executable
        return executable

    def _profile_for(self, instance_id: int) -> Path:
        return default_fleet_root() / "Profiles" / f"Fleet_{instance_id:02d}"

    def _port_for(self, instance_id: int) -> int:
        return self.settings.base_port + instance_id - 1

    def _launch_args(self, runtime: InstanceRuntime) -> list[str]:
        exe = self._resolve_browser()
        x, y, w, h = runtime.window
        args = [
            str(exe),
            "--new-window",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-session-crashed-bubble",
            "--remote-debugging-address=127.0.0.1",
            f"--remote-debugging-port={runtime.port}",
            f"--user-data-dir={runtime.profile_dir}",
            f"--window-position={x},{y}",
            f"--window-size={w},{h}",
        ]
        args.append(runtime.game_url or "about:blank")
        return args

    def _start_runtime(self, runtime: InstanceRuntime) -> None:
        existing = probe_endpoint("127.0.0.1", runtime.port)
        if existing:
            raise RuntimeError(f"CDP port {runtime.port} is already in use")
        runtime.profile_dir.mkdir(parents=True, exist_ok=True)
        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        runtime.process = subprocess.Popen(
            self._launch_args(runtime),
            close_fds=True,
            creationflags=creationflags,
        )
        runtime.launched_at = utc_now()
        runtime.last_error = None

    def start(self, count: int) -> None:
        count = validate_count(count)
        width, height = screen_size()
        layouts = grid_layout(count, width, height)
        self._resolve_browser()
        if self.settings.base_port < 1024 or self.settings.base_port + count - 1 > 65535:
            raise ValueError("fleet CDP port range must stay within 1024..65535")
        with self._lock:
            self.instances.clear()
            for index in range(count):
                instance_id = index + 1
                runtime = InstanceRuntime(
                    instance_id=instance_id,
                    port=self._port_for(instance_id),
                    profile_dir=self._profile_for(instance_id),
                    window=layouts[index],
                    game_url=self.settings.game_url,
                )
                self.instances[instance_id] = runtime
                try:
                    self._start_runtime(runtime)
                except Exception as exc:
                    runtime.last_error = str(exc)
            time.sleep(1.2)
            self.refresh_status()
            self.write_manifest()
        self.start_monitor()

    def start_monitor(self) -> None:
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._stop.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, name="wof-fleet-monitor", daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self) -> None:
        while not self._stop.wait(self.poll_seconds):
            with self._lock:
                self.refresh_status()
                self.write_manifest()

    @staticmethod
    def _reset_discovery(runtime: InstanceRuntime) -> None:
        runtime.page_ok = False
        runtime.page_count = 0
        runtime.worker_ok = False
        runtime.worker_count = 0
        runtime.worker_discovery_path = None
        runtime.related_topology_count = 0
        runtime.worker_detail = None

    def _refresh_runtime(self, runtime: InstanceRuntime) -> None:
        self._reset_discovery(runtime)
        endpoint = probe_endpoint("127.0.0.1", runtime.port)
        runtime.browser_ok = endpoint is not None
        runtime.browser_name = endpoint.browser if endpoint else None
        if not endpoint:
            if runtime.process is not None and runtime.process.poll() is not None:
                runtime.last_error = f"browser exited ({runtime.process.returncode})"
            else:
                runtime.last_error = "CDP endpoint unavailable"
            return
        if not endpoint_matches_runtime(runtime.port, endpoint):
            runtime.last_error = "CDP websocket endpoint crossed fleet port boundary"
            return

        client: CdpClient | None = None
        try:
            client = CdpClient(endpoint.websocket_url, timeout=1.5)
            client.connect()
            status = discover_fleet_status(client, settle_seconds=0.24)
            runtime.page_ok = status.page_ok
            runtime.page_count = status.page_count
            runtime.worker_ok = status.worker_ok
            runtime.worker_count = status.worker_count
            runtime.worker_discovery_path = status.path
            runtime.related_topology_count = status.topology_count
            runtime.worker_detail = status.reason
            runtime.last_error = None
        except Exception as exc:
            runtime.last_error = f"worker discovery unavailable: {exc}"
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass

    def refresh_status(self) -> None:
        for runtime in self.instances.values():
            try:
                self._refresh_runtime(runtime)
            except Exception as exc:
                self._reset_discovery(runtime)
                runtime.last_error = f"instance status refresh failed: {exc}"

    def restart(self, instance_id: int) -> None:
        runtime = self.instances.get(instance_id)
        if runtime is None:
            raise KeyError(f"unknown fleet instance {instance_id}")
        self.stop_one(instance_id)
        time.sleep(0.4)
        self._start_runtime(runtime)
        self.refresh_status()
        self.write_manifest()

    def stop_one(self, instance_id: int) -> None:
        runtime = self.instances.get(instance_id)
        if runtime is None:
            raise KeyError(f"unknown fleet instance {instance_id}")
        process = runtime.process
        if process is not None and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=4)
            except Exception:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                else:
                    try:
                        process.kill()
                    except Exception:
                        pass
        runtime.browser_ok = False
        self._reset_discovery(runtime)
        self.write_manifest()

    def stop_all(self) -> None:
        for instance_id in list(self.instances):
            try:
                self.stop_one(instance_id)
            except Exception:
                pass
        self.refresh_status()
        self.write_manifest()

    def write_manifest(self) -> None:
        instances = []
        for runtime in sorted(self.instances.values(), key=lambda item: item.instance_id):
            x, y, w, h = runtime.window
            instances.append(
                {
                    "id": runtime.instance_id,
                    "host": "127.0.0.1",
                    "port": runtime.port,
                    "endpoint": f"http://127.0.0.1:{runtime.port}",
                    "browser": runtime.browser_name,
                    "profileDir": str(runtime.profile_dir),
                    "pid": runtime.pid,
                    "managerRunId": self.run_id,
                    "launchedAt": runtime.launched_at,
                    "gameUrl": runtime.game_url,
                    "window": {"x": x, "y": y, "width": w, "height": h},
                    "status": {
                        "browser": "OK" if runtime.browser_ok else "DOWN",
                        "page": "OK" if runtime.page_ok else "WAIT",
                        "pageCount": runtime.page_count,
                        "worker": "OK" if runtime.worker_ok else "WAIT",
                        "workerCount": runtime.worker_count,
                        "workerDiscovery": runtime.worker_discovery_path,
                        "relatedTopologyCount": runtime.related_topology_count,
                        "workerIndicatorOnly": True,
                        "world921031Identity": "NOT_CHECKED",
                        "detail": runtime.worker_detail,
                        "error": runtime.last_error,
                    },
                }
            )
        atomic_write_json(
            self.manifest_path,
            {
                "version": FLEET_MANIFEST_VERSION,
                "updatedAt": utc_now(),
                "managerRunId": self.run_id,
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
                "windowWorkerReplacement": False,
                "workerStatusAuthority": "cheap-indicator-only",
                "world921031IdentityAuthoritative": False,
                "instances": instances,
            },
        )

    def print_status(self) -> None:
        self.refresh_status()
        self.write_manifest()
        print()
        print("WOF Browser Fleet")
        print(f"Browser exe: {self.browser_executable or 'auto'}")
        print(f"Manifest: {self.manifest_path}")
        print("READ ONLY / RAM writes: 0 / input injection: NO / window.Worker replacement: NO")
        print("Worker status is a cheap discovery indicator only; PYLAUNCH World 921031 proof remains authoritative.")
        print("-" * 86)
        print(f"{'#':>2} {'PORT':>5} {'BROWSER':>10} {'PAGE':>6} {'WORKER':>7} {'PID':>7} PROFILE")
        for runtime in sorted(self.instances.values(), key=lambda item: item.instance_id):
            browser = "OK" if runtime.browser_ok else "DOWN"
            page = "OK" if runtime.page_ok else "WAIT"
            worker = "OK" if runtime.worker_ok else "WAIT"
            pid = str(runtime.pid or "-")
            print(
                f"{runtime.instance_id:>2} {runtime.port:>5} {browser:>10} {page:>6} "
                f"{worker:>7} {pid:>7} {runtime.profile_dir.name}"
            )
            if runtime.last_error:
                print(f"   error: {runtime.last_error}")
        print("-" * 86)

    def interactive(self) -> None:
        self.print_status()
        print("Commands: S=status  R=restart one  X=close one  A=close all+exit  Q=quit manager only")
        while True:
            command = input("Fleet> ").strip().lower()
            if command in {"s", "status"}:
                self.print_status()
            elif command in {"r", "restart"}:
                value = input("Instance number: ").strip()
                try:
                    self.restart(int(value))
                except Exception as exc:
                    print(f"Restart failed: {exc}")
                self.print_status()
            elif command in {"x", "close", "stop"}:
                value = input("Instance number: ").strip()
                try:
                    self.stop_one(int(value))
                except Exception as exc:
                    print(f"Close failed: {exc}")
                self.print_status()
            elif command in {"a", "all", "stop-all"}:
                self.stop_all()
                break
            elif command in {"q", "quit"}:
                break
            elif command:
                print("Unknown command.")
        self._stop.set()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WOF Browser Fleet Manager (isolated profiles + localhost CDP)")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start isolated browser instances")
    start.add_argument("count", type=int)
    start.add_argument("--interactive", action="store_true")
    start.add_argument("--game-url")
    start.add_argument("--browser", choices=["auto", "chrome", "edge"])
    start.add_argument("--base-port", type=int)

    sub.add_parser("configure", help="Save browser/game URL defaults")
    sub.add_parser("status", help="Show manifest-backed fleet status")
    return parser.parse_args()


def status_from_manifest(path: Path) -> int:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print(f"No fleet manifest: {path}")
        return 1
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    args = parse_args()
    manager = FleetManager()
    if args.command == "configure":
        manager.configure_interactive()
        return 0
    if args.command == "status":
        return status_from_manifest(manager.manifest_path)
    if args.browser:
        manager.settings.browser = args.browser
    if args.game_url:
        manager.settings.game_url = args.game_url
    if args.base_port:
        manager.settings.base_port = args.base_port
    manager.settings.save(manager.settings_path)
    try:
        manager.start(args.count)
    except (RuntimeError, ValueError) as exc:
        print(f"Fleet start failed: {exc}", file=sys.stderr)
        return 2
    if args.interactive:
        try:
            manager.interactive()
        except KeyboardInterrupt:
            print()
            print("Manager stopped; browser windows were left running.")
            manager._stop.set()
    else:
        manager.print_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
