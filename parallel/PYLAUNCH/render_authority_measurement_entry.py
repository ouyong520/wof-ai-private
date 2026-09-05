from __future__ import annotations

import argparse
import importlib.util
import os
import threading
from pathlib import Path
from typing import Any

from wof_launcher import discovery_v2 as discovery_module
from wof_launcher.browser import probe_endpoint_diagnostic
from wof_launcher.cdp import CdpClient
from wof_launcher.probe_v2 import IDENTITY_PROBE as FIELD_IDENTITY_PROBE
from wof_launcher.reentry_discovery import recover_page_only
from wof_launcher.render_measurement_ui import MeasurementPublisher, MeasurementTrayApp
from wof_launcher.state import StatusStore

ATTACH_ONLY_ENV = "WOF_ALPHA_MENU6_ATTACH_ONLY"
OWNER_NAVIGATES_ENV = "WOF_ALPHA_OWNER_NAVIGATES"


def _load_runner(root: Path):
    runner = root / "parallel/RENDER_AUTHORITY_V3/measurement_runner.py"
    if not runner.is_file():
        raise RuntimeError("render authority V3 measurement runner missing")
    spec = importlib.util.spec_from_file_location("wof_render_authority_v3_runner", runner)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load render authority V3 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _accepted(choice: Any) -> bool:
    return bool(
        choice
        and choice.page
        and choice.worker
        and choice.worker_probe
        and choice.worker_probe.get("moduleOk") is True
        and choice.identity
        and choice.identity.get("ok") is True
    )


def _endpoint_has_exact_wof(host: str, port: int) -> bool:
    endpoint, _ = probe_endpoint_diagnostic(host, port)
    if endpoint is None:
        return False
    client = CdpClient(endpoint.websocket_url, timeout=5.0)
    try:
        client.connect()
        discovery_module.IDENTITY_PROBE = FIELD_IDENTITY_PROBE
        choice = recover_page_only(
            client,
            discovery_module.discover(client, identity_cache={}),
            identity_cache={},
        )
        return _accepted(choice)
    except Exception:
        return False
    finally:
        try:
            client.close()
        except Exception:
            pass


def _choose_runner_port(host: str, preferred: int, owner_navigates: bool = True) -> tuple[int, str]:
    endpoint, _ = probe_endpoint_diagnostic(host, preferred)
    if endpoint is None:
        return preferred, "program-launch-free-port"
    if _endpoint_has_exact_wof(host, preferred):
        return preferred, "reuse-existing-exact-wof"
    if owner_navigates:
        # This is the dedicated Alpha CDP port. During rapid retest we preserve
        # the Owner's browser/tab instead of spawning a new Chrome on every fix.
        return preferred, "reuse-existing-alpha-browser"
    for port in range(preferred + 1, preferred + 11):
        candidate, _ = probe_endpoint_diagnostic(host, port)
        if candidate is None:
            return port, "program-launch-fresh-port"
    raise RuntimeError("no free local CDP port available for program-owned WOF browser")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WOF Render Authority V3 owner-visible entry")
    p.add_argument("--root", required=True)
    p.add_argument("--output-root", required=True)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9223)
    p.add_argument("--browser", choices=["auto", "chrome", "edge"], default="chrome")
    p.add_argument("--browser-path")
    p.add_argument("--game-url")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    store = StatusStore()
    stop = threading.Event()
    publisher = MeasurementPublisher(store)

    def request_stop() -> None:
        stop.set()

    tray = MeasurementTrayApp(store, quit_app=request_stop)
    publisher.on_change = tray.refresh
    source_commit = str(os.environ.get("WOF_ALPHA_ACCEPTANCE_COMMIT") or "").strip()
    source_label = source_commit[:8] if source_commit else "runtime"

    def notify_blocked(reason: object) -> None:
        text = str(reason or "当前路径已 BLOCKED").strip()
        if len(text) > 240:
            text = text[:237] + "..."
        try:
            if tray.icon:
                tray.icon.notify(text, f"WOF Alpha {source_label} BLOCKED")
        except Exception:
            pass

    def forward_status(state: str, payload: dict[str, Any]) -> None:
        publisher.publish(state, **payload)
        if state == "BLOCKED":
            notify_blocked(payload.get("blockedReason"))

    publisher.publish(
        "STARTING",
        browserConnected=False,
        wofPageFound=False,
        workerFound=False,
        wasmFound=False,
        heapFound=False,
        browserLaunchAttempted=False,
        navigationAttempted=False,
        ownerNavigationRequired=True,
        staleGameUrlIgnored=True,
        sourceCommit=source_commit or None,
    )

    result = {"code": None}

    def worker() -> None:
        previous_attach_only = os.environ.get(ATTACH_ONLY_ENV)
        previous_owner_navigates = os.environ.get(OWNER_NAVIGATES_ENV)
        os.environ.pop(ATTACH_ONLY_ENV, None)
        os.environ[OWNER_NAVIGATES_ENV] = "1"
        try:
            runner = _load_runner(root)
            run_port, entry_source = _choose_runner_port(args.host, args.port, owner_navigates=True)
            browser_already_running = entry_source in {"reuse-existing-exact-wof", "reuse-existing-alpha-browser"}
            publisher.publish(
                "WAITING_FOR_WOF",
                browserConnected=browser_already_running,
                wofPageFound=entry_source == "reuse-existing-exact-wof",
                workerFound=False,
                wasmFound=False,
                heapFound=False,
                browserEntrySource=entry_source,
                browserLaunchAttempted=not browser_already_running,
                navigationAttempted=False,
                ownerNavigationRequired=entry_source != "reuse-existing-exact-wof",
                staleGameUrlIgnored=True,
                configuredGameUrl=None,
                browserPort=run_port,
            )
            code = int(
                runner.run(
                    root,
                    output_root,
                    args.host,
                    run_port,
                    args.browser,
                    args.browser_path,
                    None,
                    forward_status,
                    stop,
                )
                or 0
            )
            result["code"] = code
        except Exception as exc:
            reason = f"V3 启动失败：{type(exc).__name__}: {exc}"
            publisher.publish("BLOCKED", blockedReason=reason)
            notify_blocked(reason)
            result["code"] = 12
        finally:
            if previous_attach_only is None:
                os.environ.pop(ATTACH_ONLY_ENV, None)
            else:
                os.environ[ATTACH_ONLY_ENV] = previous_attach_only
            if previous_owner_navigates is None:
                os.environ.pop(OWNER_NAVIGATES_ENV, None)
            else:
                os.environ[OWNER_NAVIGATES_ENV] = previous_owner_navigates

    thread = threading.Thread(target=worker, name="wof-render-authority-v3", daemon=True)
    thread.start()
    try:
        tray.run()
    except ImportError as exc:
        stop.set()
        try:
            import tkinter as tk
            from tkinter import messagebox

            r = tk.Tk()
            r.withdraw()
            messagebox.showerror(
                "WOF Render Authority BLOCKED",
                f"缺少托盘依赖：{exc}\n请重新运行 WOF 一键工具完成依赖安装。",
                parent=r,
            )
            r.destroy()
        except Exception:
            pass
        return 13
    finally:
        stop.set()
        thread.join(timeout=3.0)
    return int(result["code"] or 0)


if __name__ == "__main__":
    raise SystemExit(main())
