from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

from .browser import BrowserEndpoint, find_browser, launch_debug_browser, probe_endpoint, wait_for_endpoint
from .cdp import CdpClient, CdpError
from .discovery_v2 import discover
from .state import StatusStore


class LauncherMonitor:
    def __init__(self, status: StatusStore, *, host: str = "127.0.0.1", port: int = 9223, browser_preference: str = "auto", browser_path: str | None = None, profile_dir: Path | None = None, game_url: str | None = None, auto_launch_browser: bool = True, poll_seconds: float = 1.0, on_change: Callable[[], None] | None = None) -> None:
        self.status = status; self.host = host; self.port = port; self.browser_preference = browser_preference
        self.browser_path = browser_path; self.profile_dir = profile_dir; self.game_url = game_url
        self.auto_launch_browser = auto_launch_browser; self.poll_seconds = poll_seconds; self.on_change = on_change
        self._stop = threading.Event(); self._kick = threading.Event(); self._thread: threading.Thread | None = None
        self._client: CdpClient | None = None; self._endpoint: BrowserEndpoint | None = None; self._browser_process = None
        self._last_worker_id: str | None = None; self._last_identity: dict | None = None; self._identity_cache: dict[str, dict] = {}

    def start(self) -> None:
        if self._thread and self._thread.is_alive(): return
        self._stop.clear(); self._thread = threading.Thread(target=self._run, name="wof-launcher-monitor", daemon=True); self._thread.start()

    def stop(self) -> None:
        self._stop.set(); self._kick.set()
        if self._client: self._client.close()

    def reconnect(self) -> None:
        if self._client: self._client.close()
        self._client = None; self._endpoint = None; self._last_worker_id = None; self._last_identity = None; self._identity_cache.clear()
        self.status.reset_runtime(); self._notify(); self._kick.set()

    def open_game(self) -> None:
        exe = find_browser(self.browser_preference, self.browser_path)
        if not exe:
            self.status.update(state="ERROR", last_error="未找到 Chrome 或 Edge 浏览器。游戏本身没有受到影响。"); self._notify(); return
        self._browser_process = launch_debug_browser(exe, host=self.host, port=self.port, user_data_dir=self.profile_dir, game_url=self.game_url); self._kick.set()

    def _notify(self) -> None:
        if self.on_change:
            try: self.on_change()
            except Exception: pass

    def _ensure_browser(self) -> BrowserEndpoint | None:
        endpoint = probe_endpoint(self.host, self.port)
        if endpoint: return endpoint
        if not self.auto_launch_browser: return None
        if self._browser_process is not None:
            try:
                if self._browser_process.poll() is None: return wait_for_endpoint(self.host, self.port, timeout=2.0)
            except Exception: pass
            self._browser_process = None
        exe = find_browser(self.browser_preference, self.browser_path)
        if not exe:
            self.status.update(state="ERROR", last_error="未找到 Chrome 或 Edge 浏览器。游戏本身没有受到影响。"); self._notify(); return None
        try: self._browser_process = launch_debug_browser(exe, host=self.host, port=self.port, user_data_dir=self.profile_dir, game_url=self.game_url)
        except OSError as exc:
            self.status.update(state="ERROR", last_error=f"启动专用浏览器失败。游戏本身没有受到影响。技术详情：{exc}"); self._notify(); return None
        return wait_for_endpoint(self.host, self.port)

    def _connect(self, endpoint: BrowserEndpoint) -> None:
        if self._client: self._client.close()
        client = CdpClient(endpoint.websocket_url, timeout=5.0); client.connect(); self._client = client; self._endpoint = endpoint
        self.status.update(browser_connected=True, browser_name=endpoint.browser, browser_endpoint=endpoint.http_base, state="WAITING_WOF", last_error=None); self._notify()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                endpoint = self._ensure_browser()
                if not endpoint:
                    self.status.reset_runtime(error="未连接到本机 Chrome/Edge 调试端口。游戏本身没有受到影响。"); self._notify(); self._sleep(); continue
                if not self._client or not self._endpoint or self._endpoint.websocket_url != endpoint.websocket_url: self._connect(endpoint)
                assert self._client is not None
                choice = discover(self._client, identity_cache=self._identity_cache)
                worker_id = str(choice.worker.get("targetId")) if choice.worker else None; identity = choice.identity
                self._last_worker_id = worker_id; self._last_identity = identity
                diagnostics = choice.diagnostics if isinstance(choice.diagnostics, dict) else None
                self.status.update(
                    browser_connected=True, browser_name=endpoint.browser, browser_endpoint=endpoint.http_base,
                    wof_page_found=choice.page is not None, page_target_id=str(choice.page.get("targetId")) if choice.page else None, page_url=str(choice.page.get("url") or "") if choice.page else None,
                    worker_found=choice.worker is not None, worker_target_id=worker_id, worker_url=str(choice.worker.get("url") or "") if choice.worker else None,
                    wasm_module_found=bool(choice.worker_probe and choice.worker_probe.get("moduleOk")), wasm_module_key=str(choice.worker_probe.get("moduleKey")) if choice.worker_probe and choice.worker_probe.get("moduleKey") else None,
                    heap_found=bool(choice.worker_probe and choice.worker_probe.get("heapOk")), heap_bytes=int(choice.worker_probe.get("heapBytes")) if choice.worker_probe and isinstance(choice.worker_probe.get("heapBytes"), int) else None,
                    world_921031=bool(identity and identity.get("ok") is True), identity_sha256=str(identity.get("sha256")) if identity and identity.get("sha256") else None,
                    identity_reason=str(identity.get("reason")) if identity and identity.get("reason") else choice.reason,
                    discovery_path=str(diagnostics.get("path")) if diagnostics and diagnostics.get("path") else None, discovery_diagnostics=diagnostics,
                    read_only=True, ram_writes=0, input_injection=False,
                    state="CONNECTED" if choice.page and choice.worker and identity and identity.get("ok") is True else "WAITING_WOF", last_error=None,
                ); self._notify()
            except (CdpError, OSError, ValueError) as exc:
                if self._client: self._client.close()
                self._client = None; self._endpoint = None; self._last_worker_id = None; self._last_identity = None; self._identity_cache.clear()
                self.status.reset_runtime(error=f"Launcher 与浏览器连接中断。游戏本身没有受到影响。技术详情：{exc}"); self._notify()
            self._sleep()

    def _sleep(self) -> None:
        self._kick.wait(self.poll_seconds); self._kick.clear()
