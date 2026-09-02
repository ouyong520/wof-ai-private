from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

from .alpha_runtime import AlphaRuntimeError, AlphaRuntimeManager
from .browser import (
    BrowserEndpoint,
    find_browser,
    launch_debug_browser,
    probe_endpoint_diagnostic,
    wait_for_endpoint_diagnostic,
)
from .cdp import CdpClient, CdpError
from . import discovery_v2 as discovery_module
from .discovery_v2 import TargetChoice
from .probe_v2 import IDENTITY_PROBE as FIELD_IDENTITY_PROBE
from .reentry_discovery import recover_page_only
from .runtime_authority import RuntimeAuthorityGuard
from .state import StatusStore


class LauncherMonitor:
    def __init__(self, status: StatusStore, *, host: str = "127.0.0.1", port: int = 9223, browser_preference: str = "auto", browser_path: str | None = None, profile_dir: Path | None = None, game_url: str | None = None, auto_launch_browser: bool = True, poll_seconds: float = 1.0, on_change: Callable[[], None] | None = None, alpha_runtime: AlphaRuntimeManager | None = None) -> None:
        self.status = status; self.host = host; self.port = port; self.browser_preference = browser_preference
        self.browser_path = browser_path; self.profile_dir = profile_dir; self.game_url = game_url
        self.auto_launch_browser = auto_launch_browser; self.poll_seconds = poll_seconds; self.on_change = on_change
        self.alpha_runtime = alpha_runtime
        self._stop = threading.Event(); self._kick = threading.Event(); self._thread: threading.Thread | None = None
        self._client: CdpClient | None = None; self._endpoint: BrowserEndpoint | None = None; self._browser_process = None
        self._last_worker_id: str | None = None; self._last_identity: dict | None = None; self._identity_cache: dict[str, dict] = {}
        self._startup_attestation_error: str | None = None
        self._accepted_choice: TargetChoice | None = None
        self._authority_guard = RuntimeAuthorityGuard()

    def start(self) -> None:
        if self._thread and self._thread.is_alive(): return
        self._stop.clear(); self._thread = threading.Thread(target=self._run, name="wof-launcher-monitor", daemon=True); self._thread.start()

    def stop(self) -> None:
        self._stop.set(); self._kick.set()
        if self.alpha_runtime:
            try: self.alpha_runtime.revoke(self._client)
            except Exception: pass
        if self._client: self._client.close()

    def _invalidate_authority(self) -> None:
        if self.alpha_runtime:
            try: self.alpha_runtime.revoke(self._client)
            except Exception: pass
        if self._client: self._client.close()
        self._client = None; self._endpoint = None; self._last_worker_id = None; self._last_identity = None; self._identity_cache.clear()
        self._accepted_choice = None; self._authority_guard.clear()

    def reconnect(self) -> None:
        self._invalidate_authority(); self._startup_attestation_error = None
        self.status.reset_runtime(); self.status.update(alpha_requested=self.alpha_runtime is not None); self._notify(); self._kick.set()

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
        self._startup_attestation_error = None
        endpoint, rejection = probe_endpoint_diagnostic(self.host, self.port)
        if endpoint: return endpoint
        if rejection:
            self._startup_attestation_error = rejection
            return None
        if not self.auto_launch_browser: return None
        if self._browser_process is not None:
            try:
                if self._browser_process.poll() is None:
                    endpoint, rejection = wait_for_endpoint_diagnostic(self.host, self.port, timeout=2.0)
                    self._startup_attestation_error = rejection
                    return endpoint
            except Exception: pass
            self._browser_process = None
        exe = find_browser(self.browser_preference, self.browser_path)
        if not exe:
            self.status.update(state="ERROR", last_error="未找到 Chrome 或 Edge 浏览器。游戏本身没有受到影响。"); self._notify(); return None
        try: self._browser_process = launch_debug_browser(exe, host=self.host, port=self.port, user_data_dir=self.profile_dir, game_url=self.game_url)
        except OSError as exc:
            self.status.update(state="ERROR", last_error=f"启动专用浏览器失败。游戏本身没有受到影响。技术详情：{exc}"); self._notify(); return None
        endpoint, rejection = wait_for_endpoint_diagnostic(self.host, self.port)
        self._startup_attestation_error = rejection
        return endpoint

    def _connect(self, endpoint: BrowserEndpoint) -> None:
        self._invalidate_authority()
        client = CdpClient(endpoint.websocket_url, timeout=5.0); client.connect(); self._client = client; self._endpoint = endpoint
        self.status.update(browser_connected=True, browser_name=endpoint.browser, browser_endpoint=endpoint.http_base, state="WAITING_WOF", last_error=None, alpha_requested=self.alpha_runtime is not None); self._notify()

    def _fresh_discover(self) -> TargetChoice:
        assert self._client is not None
        discovery_module.IDENTITY_PROBE = FIELD_IDENTITY_PROBE
        choice = discovery_module.discover(self._client, identity_cache=self._identity_cache)
        return recover_page_only(self._client, choice, identity_cache=self._identity_cache)

    @staticmethod
    def _accepted(choice: TargetChoice) -> bool:
        return bool(choice.page and choice.worker and choice.worker_probe and choice.worker_probe.get("moduleOk") is True and choice.identity and choice.identity.get("ok") is True)

    def _choice_for_tick(self) -> tuple[TargetChoice, str | None]:
        assert self._client is not None
        if self._accepted_choice is not None:
            healthy, _reason, diag = self._authority_guard.healthy(self._client, self._accepted_choice)
            if healthy:
                cached = self._accepted_choice
                return TargetChoice(cached.page, cached.worker, cached.worker_probe, cached.identity, None, diag), self._authority_guard.diagnostics().get("runtimeFingerprint")
            if self.alpha_runtime: self.alpha_runtime.revoke(self._client)
            self._accepted_choice = None; self._identity_cache.clear()

        choice = self._fresh_discover()
        if not self._accepted(choice):
            self._authority_guard.clear()
            if self.alpha_runtime: self.alpha_runtime.revoke(self._client)
            return choice, None
        try:
            fingerprint = self._authority_guard.accept(self._client, choice)
        except (CdpError, OSError, ValueError) as exc:
            self._accepted_choice = None; self._identity_cache.clear()
            if self.alpha_runtime: self.alpha_runtime.revoke(self._client)
            diag = dict(choice.diagnostics or {})
            diag.update({"path": "exact-identity-without-runtime-generation", "runtimeFingerprintError": str(exc), "fullIdentityScan": True})
            return TargetChoice(choice.page, choice.worker, choice.worker_probe, choice.identity, f"exact World identity found but runtime generation fingerprint is unavailable: {exc}", diag), None
        self._accepted_choice = choice
        diag = dict(choice.diagnostics or {})
        diag.update({"fullIdentityScan": True, "runtimeFingerprint": fingerprint.key(), "authorityGuard": self._authority_guard.diagnostics()})
        return TargetChoice(choice.page, choice.worker, choice.worker_probe, choice.identity, choice.reason, diag), fingerprint.key()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                endpoint = self._ensure_browser()
                if not endpoint:
                    self._invalidate_authority()
                    error = self._startup_attestation_error or "未连接到本机 Chrome/Edge 调试端口。游戏本身没有受到影响。"
                    self.status.reset_runtime(error=error); self.status.update(alpha_requested=self.alpha_runtime is not None); self._notify(); self._sleep(); continue
                if not self._client or not self._endpoint or self._endpoint.websocket_url != endpoint.websocket_url:
                    self._connect(endpoint)
                else:
                    self._endpoint = endpoint
                assert self._client is not None
                choice, authority_key = self._choice_for_tick()
                worker_id = str(choice.worker.get("targetId")) if choice.worker else None; identity = choice.identity
                self._last_worker_id = worker_id; self._last_identity = identity
                diagnostics = choice.diagnostics if isinstance(choice.diagnostics, dict) else None

                alpha_status: dict | None = None; alpha_error: str | None = None; alpha_running = False
                accepted = self._accepted(choice) and authority_key is not None
                if self.alpha_runtime and accepted:
                    try:
                        alpha_status = self.alpha_runtime.ensure_running(self._client, choice, authority_key)
                        recovery, restart = self.alpha_runtime.poll_projection_recovery(self._client, choice, authority_key)
                        if restart:
                            alpha_status = self.alpha_runtime.ensure_running(self._client, choice, authority_key)
                            recovery, _ = self.alpha_runtime.poll_projection_recovery(self._client, choice, authority_key)
                        if isinstance(alpha_status, dict):
                            alpha_status["projectionRecovery"] = recovery
                        alpha_running = alpha_status.get("running") is True
                    except (AlphaRuntimeError, CdpError, OSError, ValueError) as exc:
                        alpha_error = str(exc); self.alpha_runtime.revoke(self._client)
                elif self.alpha_runtime:
                    self.alpha_runtime.revoke(self._client)

                connected = accepted and (self.alpha_runtime is None or alpha_running)
                reason = str(identity.get("reason")) if identity and identity.get("reason") else choice.reason
                if alpha_error: reason = "Alpha release activation failed: " + alpha_error
                self.status.update(
                    browser_connected=True, browser_name=endpoint.browser, browser_endpoint=endpoint.http_base,
                    wof_page_found=choice.page is not None, page_target_id=str(choice.page.get("targetId")) if choice.page else None, page_url=str(choice.page.get("url") or "") if choice.page else None,
                    worker_found=choice.worker is not None, worker_target_id=worker_id, worker_url=str(choice.worker.get("url") or "") if choice.worker else None,
                    wasm_module_found=bool(choice.worker_probe and choice.worker_probe.get("moduleOk")), wasm_module_key=str(choice.worker_probe.get("moduleKey")) if choice.worker_probe and choice.worker_probe.get("moduleKey") else None,
                    heap_found=bool(choice.worker_probe and choice.worker_probe.get("heapOk")), heap_bytes=int(choice.worker_probe.get("heapBytes")) if choice.worker_probe and isinstance(choice.worker_probe.get("heapBytes"), int) else None,
                    world_921031=bool(identity and identity.get("ok") is True), identity_sha256=str(identity.get("sha256")) if identity and identity.get("sha256") else None,
                    identity_reason=reason,
                    discovery_path=str(diagnostics.get("path")) if diagnostics and diagnostics.get("path") else None, discovery_diagnostics=diagnostics,
                    alpha_requested=self.alpha_runtime is not None, alpha_running=alpha_running,
                    alpha_runtime_epoch=str(alpha_status.get("runtimeEpoch")) if alpha_status and alpha_status.get("runtimeEpoch") else None,
                    alpha_package_version=str(alpha_status.get("packageVersion")) if alpha_status and alpha_status.get("packageVersion") else None,
                    alpha_status=alpha_status, alpha_error=alpha_error,
                    read_only=True, ram_writes=0, input_injection=False,
                    state="CONNECTED" if connected else "WAITING_WOF", last_error=alpha_error,
                ); self._notify()
            except (CdpError, OSError, ValueError) as exc:
                self._invalidate_authority(); self._startup_attestation_error = None
                self.status.reset_runtime(error=f"Launcher 与浏览器连接中断。游戏本身没有受到影响。技术详情：{exc}"); self.status.update(alpha_requested=self.alpha_runtime is not None); self._notify()
            self._sleep()

    def _sleep(self) -> None:
        self._kick.wait(self.poll_seconds); self._kick.clear()
