from __future__ import annotations

import json
from typing import Any, Callable

from .cdp import CdpClient, CdpSession

SOURCE = "product/alpha/wof_alpha_p1_tracker_overlay.js"
SCHEMA = "wof-alpha-p1-tracker-overlay-v1"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False, "productionOverlayEnabled": True}


class ProductionP1OverlayError(RuntimeError):
    pass


class ProductionP1Overlay:
    """Package-selected production WebGL sink for the bounded P1 head tracker."""

    def __init__(self, verified_text: Callable[[str], str]) -> None:
        self._verified_text = verified_text
        self._session: CdpSession | None = None
        self._authority_key: str | None = None
        self._runtime_epoch: str | None = None
        self._last: dict[str, Any] = {"schema": SCHEMA, "visible": False, "drawCount": 0, **SAFETY}

    @staticmethod
    def _validate(remote: Any, authority_key: str, runtime_epoch: str) -> dict[str, Any]:
        if not isinstance(remote, dict) or remote.get("schema") != SCHEMA:
            raise ProductionP1OverlayError("production P1 overlay malformed remote schema")
        if remote.get("authorityKey") != authority_key or remote.get("runtimeEpoch") != runtime_epoch:
            raise ProductionP1OverlayError("production P1 overlay stale/runtime-generation mismatch")
        if remote.get("productionOverlayEnabled") is not True or remote.get("readOnly") is not True or remote.get("ramWrites") != 0 or remote.get("inputInjection") is not False:
            raise ProductionP1OverlayError("production P1 overlay safety boundary mismatch")
        return dict(remote)

    def bind(self, client: CdpClient, page_target_id: str, authority_key: str, runtime_epoch: str) -> dict[str, Any]:
        self.dispose()
        self._session = client.attach(page_target_id)
        self._session.request("Runtime.enable")
        source = self._verified_text(SOURCE)
        try:
            self._session.evaluate("try{window.WOFALPHAP1TRACKER?.dispose?.()}catch(_){};true", timeout=5.0)
            self._session.evaluate(f"(0,eval)({json.dumps(source)});true", timeout=10.0)
            remote = self._session.evaluate(
                f"window.WOFALPHAP1TRACKER?.bind?.({json.dumps({'authorityKey': authority_key, 'runtimeEpoch': runtime_epoch})})||null",
                timeout=5.0,
            )
        except Exception as exc:
            self.dispose()
            raise ProductionP1OverlayError(f"production P1 overlay install failed: {exc}") from exc
        self._authority_key = authority_key
        self._runtime_epoch = runtime_epoch
        self._last = self._validate(remote, authority_key, runtime_epoch)
        return self.status()

    def update(self, visual: dict[str, Any], layout: dict[str, Any] | None, frame_size: tuple[int, int]) -> dict[str, Any]:
        if not self._session or not self._authority_key or not self._runtime_epoch:
            return self.status()
        center = visual.get("center") if isinstance(visual, dict) else None
        visible = bool(
            isinstance(center, list)
            and len(center) >= 2
            and visual.get("state") == "HEAD_TRACKING"
            and int(visual.get("lostFrames") or 0) == 0
            and isinstance(layout, dict)
        )
        try:
            if visible:
                fw, fh = max(1, int(frame_size[0])), max(1, int(frame_size[1]))
                css_w, css_h = float(layout.get("width") or 0), float(layout.get("height") or 0)
                x = float(center[0]) * css_w / fw
                y = float(center[1]) * css_h / fh
                payload = {
                    "authorityKey": self._authority_key,
                    "runtimeEpoch": self._runtime_epoch,
                    "visible": True,
                    "x": x,
                    "y": y,
                    "label": "P1",
                    "seedSource": visual.get("seedSource"),
                }
                expr = f"window.WOFALPHAP1TRACKER?.setAnchor?.({json.dumps(payload)})||null"
            else:
                reason = str(visual.get("revocationReason") or visual.get("state") or "TRACKER_NOT_VISIBLE") if isinstance(visual, dict) else "TRACKER_NOT_VISIBLE"
                expr = f"window.WOFALPHAP1TRACKER?.hide?.({json.dumps(reason)})||null"
            remote = self._session.evaluate(expr, timeout=5.0)
            self._last = self._validate(remote, self._authority_key, self._runtime_epoch)
        except Exception as exc:
            raise ProductionP1OverlayError(f"production P1 overlay update failed: {exc}") from exc
        return self.status()

    def status(self) -> dict[str, Any]:
        return dict(self._last)

    def visible_and_drawn(self) -> bool:
        return bool(self._last.get("visible") is True and int(self._last.get("drawCount") or 0) > 0 and self._last.get("drawHooked") is True)

    def dispose(self) -> None:
        if self._session:
            try:
                self._session.evaluate("window.WOFALPHAP1TRACKER?.dispose?.();true", timeout=3.0)
            except Exception:
                pass
            try:
                self._session.close()
            except Exception:
                pass
        self._session = None
        self._authority_key = None
        self._runtime_epoch = None
        self._last = {"schema": SCHEMA, "visible": False, "drawCount": 0, **SAFETY}
