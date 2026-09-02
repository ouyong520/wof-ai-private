from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class LauncherStatus:
    browser_connected: bool = False
    browser_name: str | None = None
    browser_endpoint: str | None = None
    wof_page_found: bool = False
    page_target_id: str | None = None
    page_url: str | None = None
    worker_found: bool = False
    worker_target_id: str | None = None
    worker_url: str | None = None
    wasm_module_found: bool = False
    wasm_module_key: str | None = None
    heap_found: bool = False
    heap_bytes: int | None = None
    world_921031: bool = False
    identity_sha256: str | None = None
    identity_reason: str | None = None
    discovery_path: str | None = None
    discovery_diagnostics: dict[str, Any] | None = None
    alpha_requested: bool = False
    alpha_running: bool = False
    alpha_runtime_epoch: str | None = None
    alpha_package_version: str | None = None
    alpha_status: dict[str, Any] | None = None
    alpha_error: str | None = None
    read_only: bool = True
    ram_writes: int = 0
    input_injection: bool = False
    state: str = "DISCONNECTED"
    last_error: str | None = None
    last_update_utc: str = field(default_factory=_utc_now)

    def snapshot(self) -> dict[str, Any]:
        return asdict(self)


class StatusStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self._status = LauncherStatus()

    def get(self) -> LauncherStatus:
        with self._lock:
            return LauncherStatus(**self._status.snapshot())

    def update(self, **changes: Any) -> LauncherStatus:
        with self._lock:
            for key, value in changes.items():
                if not hasattr(self._status, key):
                    raise AttributeError(key)
                setattr(self._status, key, value)
            self._status.last_update_utc = _utc_now()
            return LauncherStatus(**self._status.snapshot())

    def reset_runtime(self, *, error: str | None = None) -> LauncherStatus:
        return self.update(
            browser_connected=False,
            browser_name=None,
            browser_endpoint=None,
            wof_page_found=False,
            page_target_id=None,
            page_url=None,
            worker_found=False,
            worker_target_id=None,
            worker_url=None,
            wasm_module_found=False,
            wasm_module_key=None,
            heap_found=False,
            heap_bytes=None,
            world_921031=False,
            identity_sha256=None,
            identity_reason=None,
            discovery_path=None,
            discovery_diagnostics=None,
            alpha_running=False,
            alpha_runtime_epoch=None,
            alpha_package_version=None,
            alpha_status=None,
            alpha_error=error,
            state="ERROR" if error else "DISCONNECTED",
            last_error=error,
            read_only=True,
            ram_writes=0,
            input_injection=False,
        )
