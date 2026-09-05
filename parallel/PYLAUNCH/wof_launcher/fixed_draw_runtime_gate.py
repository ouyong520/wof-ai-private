from __future__ import annotations

import json
import os
import secrets
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .browser import (
    find_browser,
    launch_debug_browser,
    probe_endpoint_diagnostic,
    wait_for_endpoint_diagnostic,
)
from .cdp import CdpClient
from .production_p1_overlay import FIXED_SMOKE_STATES, ProductionHudFixedDrawSmoke

FIXED_DRAW_SMOKE_ENV = "WOF_ALPHA_FIXED_DRAW_SMOKE"
FIXED_DRAW_STATUS_FILE = "ALPHA_FIXED_DRAW_STATUS.json"
FIXED_DRAW_STATUS_SCHEMA = "wof-alpha-runtime-fixed-draw-status-v1"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
_NATIVE = {"width": 384, "height": 224, "center": {"x": 192, "y": 112}, "label": "TEST"}

_GAME_CANVAS_CONTEXT_EXPR = r"""(()=>{const c=window.I_GF1TC||document.getElementById('whathis'),g=window.I_fdC8Q;return {canvas:!!c,context:!!(g&&typeof g.drawArrays==='function'),href:String(location.href),title:String(document.title||'')};})()"""


def fixed_draw_gate_enabled(env: dict[str, str] | None = None) -> bool:
    source = os.environ if env is None else env
    return str(source.get(FIXED_DRAW_SMOKE_ENV) or "").strip() == "1"


def _git_dir(root: Path) -> Path | None:
    marker = root / ".git"
    if marker.is_dir():
        return marker
    if not marker.is_file():
        return None
    try:
        text = marker.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text.lower().startswith("gitdir:"):
        return None
    value = text.split(":", 1)[1].strip()
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def _checkout_sha(root: Path) -> str | None:
    git_dir = _git_dir(root)
    if git_dir is None:
        return None
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if len(head) == 40 and all(ch in "0123456789abcdefABCDEF" for ch in head):
        return head.lower()
    if not head.startswith("ref: "):
        return None
    ref = head[5:].strip()
    try:
        value = (git_dir / ref).read_text(encoding="utf-8").strip()
        if len(value) == 40 and all(ch in "0123456789abcdefABCDEF" for ch in value):
            return value.lower()
    except OSError:
        pass
    try:
        for line in (git_dir / "packed-refs").read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or line.startswith("^"):
                continue
            sha, _, name = line.partition(" ")
            if name == ref and len(sha) == 40:
                return sha.lower()
    except OSError:
        pass
    return None


def resolve_release_sha(root: Path, acceptance_sha: str | None = None) -> tuple[str | None, str | None]:
    acceptance = str(acceptance_sha or os.environ.get("WOF_ALPHA_ACCEPTANCE_COMMIT") or "").strip() or None
    checkout = _checkout_sha(root)
    return acceptance or checkout, checkout


def _manual_probe_state(state: str, last_error: str | None = None) -> dict[str, Any]:
    if state not in FIXED_SMOKE_STATES:
        state = "HUD_INJECTION_MISSING"
    return {
        "state": state,
        "enabled": state != "DISABLED",
        "hudInjected": False,
        "gameCanvasContextPresent": False,
        "drawHooked": False,
        "drawCount": 0,
        "callbackCount": 0,
        "drawingBuffer": None,
        "nativeWidth": 384,
        "nativeHeight": 224,
        "nativeX": 192,
        "nativeY": 112,
        "label": "TEST",
        "lastError": last_error,
        **SAFETY,
    }


class FixedDrawRuntimeGate:
    def __init__(
        self,
        root: Path,
        output_root: Path,
        *,
        acceptance_sha: str | None = None,
        smoke_factory: Callable[[Callable[[str], str]], Any] = ProductionHudFixedDrawSmoke,
    ) -> None:
        self.root = root.resolve()
        self.output_root = output_root.resolve()
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.status_path = self.output_root / FIXED_DRAW_STATUS_FILE
        self.release_sha, self.checkout_sha = resolve_release_sha(self.root, acceptance_sha)
        self.acceptance_sha = str(acceptance_sha or os.environ.get("WOF_ALPHA_ACCEPTANCE_COMMIT") or "").strip() or None
        self.runtime_epoch = secrets.token_hex(16)
        self._sequence = 0
        self._smoke = smoke_factory(lambda rel: (self.root / rel).read_text(encoding="utf-8"))
        self._target: dict[str, Any] | None = None

    def _strict_draw_success(self, probe: dict[str, Any]) -> bool:
        buffer = probe.get("drawingBuffer")
        return bool(
            probe.get("state") == "FIXED_TEST_ACTUALLY_DRAWN"
            and probe.get("hudInjected") is True
            and probe.get("gameCanvasContextPresent") is True
            and probe.get("drawHooked") is True
            and int(probe.get("drawCount") or 0) > 0
            and isinstance(buffer, dict)
            and int(buffer.get("width") or 0) > 0
            and int(buffer.get("height") or 0) > 0
            and probe.get("label") == "TEST"
            and int(probe.get("nativeWidth") or 0) == 384
            and int(probe.get("nativeHeight") or 0) == 224
            and int(probe.get("nativeX") or -1) == 192
            and int(probe.get("nativeY") or -1) == 112
            and probe.get("readOnly") is True
            and int(probe.get("ramWrites") or 0) == 0
            and probe.get("inputInjection") is False
        )

    def _compose(self, probe: dict[str, Any], target: dict[str, Any] | None = None) -> dict[str, Any]:
        state = str(probe.get("state") or "HUD_INJECTION_MISSING")
        if state not in FIXED_SMOKE_STATES:
            state = "HUD_INJECTION_MISSING"
        self._sequence += 1
        target = target or self._target or {}
        normalized = {
            "schema": FIXED_DRAW_STATUS_SCHEMA,
            "releaseSha": self.release_sha,
            "acceptanceSha": self.acceptance_sha,
            "checkoutSha": self.checkout_sha,
            "runtimeEpoch": self.runtime_epoch,
            "statusSequence": self._sequence,
            "updatedAt": datetime.now().astimezone().isoformat(timespec="milliseconds"),
            "pageTargetId": target.get("targetId"),
            "pageUrl": target.get("url") or target.get("href"),
            "pageTitle": target.get("title"),
            "fixedSmokeState": state,
            "state": state,
            "enabled": probe.get("enabled") is True,
            "hudInjected": probe.get("hudInjected") is True,
            "gameCanvasContextPresent": probe.get("gameCanvasContextPresent") is True,
            "drawHooked": probe.get("drawHooked") is True,
            "callbackCount": int(probe.get("callbackCount") or 0),
            "drawCount": int(probe.get("drawCount") or 0),
            "drawingBuffer": probe.get("drawingBuffer"),
            "nativeWidth": int(probe.get("nativeWidth") or 384),
            "nativeHeight": int(probe.get("nativeHeight") or 224),
            "nativeX": int(probe.get("nativeX") or 192),
            "nativeY": int(probe.get("nativeY") or 112),
            "native": dict(_NATIVE),
            "label": str(probe.get("label") or "TEST"),
            "lastError": probe.get("lastError"),
            "readOnly": probe.get("readOnly") is True,
            "ramWrites": int(probe.get("ramWrites") or 0),
            "inputInjection": probe.get("inputInjection") is True,
        }
        normalized["drawSuccess"] = self._strict_draw_success(normalized)
        return normalized

    def _write(self, payload: dict[str, Any]) -> dict[str, Any]:
        tmp = self.status_path.with_suffix(self.status_path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.status_path)
        return payload

    def record_probe_status(self, probe: dict[str, Any], target: dict[str, Any] | None = None) -> dict[str, Any]:
        if target is not None:
            self._target = dict(target)
        return self._write(self._compose(dict(probe), target))

    def record_state(
        self,
        state: str,
        *,
        last_error: str | None = None,
        target: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.record_probe_status(_manual_probe_state(state, last_error), target)

    @staticmethod
    def _page_targets(client: CdpClient) -> list[dict[str, Any]]:
        response = client.request("Target.getTargets")
        rows = response.get("targetInfos")
        if not isinstance(rows, list):
            return []
        return [dict(row) for row in rows if isinstance(row, dict) and row.get("type") == "page" and row.get("targetId")]

    @classmethod
    def find_game_canvas_target(cls, client: CdpClient) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        first_page: dict[str, Any] | None = None
        for target in cls._page_targets(client):
            if first_page is None:
                first_page = dict(target)
            session = None
            try:
                session = client.attach(str(target["targetId"]))
                session.request("Runtime.enable")
                remote = session.evaluate(_GAME_CANVAS_CONTEXT_EXPR, timeout=3.0)
                if isinstance(remote, dict):
                    if remote.get("href"):
                        target["href"] = str(remote.get("href"))
                        target["url"] = str(remote.get("href"))
                    if remote.get("title") is not None:
                        target["title"] = str(remote.get("title") or "")
                    if remote.get("canvas") is True and remote.get("context") is True:
                        return target, first_page
            except Exception:
                continue
            finally:
                if session is not None:
                    try:
                        session.close()
                    except Exception:
                        pass
        return None, first_page

    def run_connected(
        self,
        client: CdpClient,
        stop_event: Any,
        *,
        status_callback: Callable[[str, dict[str, Any]], None] | None = None,
        poll_interval: float = 0.25,
    ) -> int:
        bound_target: dict[str, Any] | None = None
        try:
            while not stop_event.is_set():
                if bound_target is None:
                    try:
                        target, first_page = self.find_game_canvas_target(client)
                    except Exception as exc:
                        payload = self.record_state("HUD_INJECTION_MISSING", last_error=f"CDP_TARGET_SCAN_FAILED: {exc}")
                        if status_callback:
                            status_callback("WAITING_FOR_WOF", {"fixedDrawSmoke": payload, "browserConnected": True, "wofPageFound": False})
                        stop_event.wait(poll_interval)
                        continue
                    if target is None:
                        payload = self.record_state(
                            "GAME_CANVAS_CONTEXT_MISSING",
                            last_error="WOF_GAME_CANVAS_CONTEXT_NOT_READY",
                            target=first_page,
                        )
                        if status_callback:
                            status_callback(
                                "WAITING_FOR_WOF",
                                {
                                    "fixedDrawSmoke": payload,
                                    "browserConnected": True,
                                    "wofPageFound": False,
                                    "pageTargetId": payload.get("pageTargetId"),
                                    "pageUrl": payload.get("pageUrl"),
                                },
                            )
                        stop_event.wait(poll_interval)
                        continue
                    bound_target = target
                    self._target = dict(target)
                    try:
                        probe = self._smoke.enable(client, str(target["targetId"]), self.runtime_epoch)
                    except Exception as exc:
                        probe = _manual_probe_state("HUD_INJECTION_MISSING", f"FIXED_SMOKE_ENABLE_FAILED: {exc}")
                    payload = self.record_probe_status(probe, target)
                else:
                    try:
                        probe = self._smoke.poll()
                    except Exception as exc:
                        probe = _manual_probe_state("HUD_INJECTION_MISSING", f"FIXED_SMOKE_POLL_FAILED: {exc}")
                    payload = self.record_probe_status(probe, bound_target)

                if status_callback:
                    status_callback(
                        "RUNNING",
                        {
                            "fixedDrawSmoke": payload,
                            "browserConnected": True,
                            "wofPageFound": True,
                            "pageTargetId": payload.get("pageTargetId"),
                            "pageUrl": payload.get("pageUrl"),
                        },
                    )

                if payload["fixedSmokeState"] in {"GAME_CANVAS_CONTEXT_MISSING", "DISABLED"} or (
                    payload["fixedSmokeState"] == "HUD_INJECTION_MISSING" and payload.get("lastError")
                ):
                    try:
                        self._smoke.dispose()
                    except Exception:
                        pass
                    bound_target = None
                stop_event.wait(poll_interval)
        finally:
            try:
                self._smoke.dispose()
            except Exception:
                pass
            if stop_event.is_set():
                self.record_state("DISABLED", target=bound_target or self._target)
        return 0


def run_fixed_draw_runtime_gate(
    root: Path,
    output_root: Path,
    host: str,
    port: int,
    browser: str,
    browser_path: str | None,
    status_callback: Callable[[str, dict[str, Any]], None] | None,
    stop_event: Any,
    *,
    acceptance_sha: str | None = None,
) -> int:
    gate = FixedDrawRuntimeGate(root, output_root, acceptance_sha=acceptance_sha)
    initial = gate.record_state("HUD_INJECTION_MISSING", last_error="BROWSER_ENDPOINT_PENDING")
    if status_callback:
        status_callback("WAITING_FOR_WOF", {"fixedDrawSmoke": initial, "browserConnected": False, "wofPageFound": False})

    endpoint, rejection = probe_endpoint_diagnostic(host, port)
    if endpoint is None:
        executable = find_browser(browser, browser_path)
        if not executable:
            payload = gate.record_state("HUD_INJECTION_MISSING", last_error="BROWSER_EXECUTABLE_MISSING")
            if status_callback:
                status_callback(
                    "BLOCKED",
                    {
                        "fixedDrawSmoke": payload,
                        "blockedReason": "未找到 Chrome/Edge；fixed TEST gate 无法建立只读浏览器入口。",
                    },
                )
            return 3
        try:
            launch_debug_browser(
                executable,
                host=host,
                port=port,
                user_data_dir=None,
                game_url=None,
                restore_last_session=False,
            )
            endpoint, rejection = wait_for_endpoint_diagnostic(host, port, timeout=15.0)
        except Exception as exc:
            payload = gate.record_state("HUD_INJECTION_MISSING", last_error=f"BROWSER_LAUNCH_FAILED: {exc}")
            if status_callback:
                status_callback(
                    "BLOCKED",
                    {
                        "fixedDrawSmoke": payload,
                        "blockedReason": f"无法启动/复用 fixed TEST gate 浏览器：{exc}",
                    },
                )
            return 4

    if endpoint is None:
        payload = gate.record_state("HUD_INJECTION_MISSING", last_error=rejection or "BROWSER_ENDPOINT_UNAVAILABLE")
        if status_callback:
            status_callback(
                "BLOCKED",
                {
                    "fixedDrawSmoke": payload,
                    "blockedReason": rejection or "fixed TEST gate 浏览器调试端口不可用。",
                },
            )
        return 5

    client = CdpClient(endpoint.websocket_url, timeout=5.0)
    try:
        client.connect()
    except Exception as exc:
        payload = gate.record_state("HUD_INJECTION_MISSING", last_error=f"CDP_CONNECT_FAILED: {exc}")
        if status_callback:
            status_callback(
                "BLOCKED",
                {
                    "fixedDrawSmoke": payload,
                    "blockedReason": f"fixed TEST gate 无法连接本机只读 CDP：{exc}",
                },
            )
        return 6

    if status_callback:
        status_callback(
            "WAITING_FOR_WOF",
            {
                "fixedDrawSmoke": gate.record_state("GAME_CANVAS_CONTEXT_MISSING", last_error="WOF_GAME_CANVAS_CONTEXT_NOT_READY"),
                "browserConnected": True,
                "browserName": endpoint.browser,
                "browserEndpoint": endpoint.http_base,
                "wofPageFound": False,
            },
        )
    try:
        return gate.run_connected(client, stop_event, status_callback=status_callback)
    finally:
        try:
            client.close()
        except Exception:
            pass
