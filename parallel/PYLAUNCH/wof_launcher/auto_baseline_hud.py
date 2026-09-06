from __future__ import annotations

import json
import math
from typing import Any, Callable, Mapping

from .cdp import CdpClient, CdpSession

P37_SOURCE = "parallel/AUTO_MARKER_BASELINE/native_marker_auto_acquisition_baseline.js"
ADAPTER_SOURCE = "product/alpha/wof_alpha_auto_baseline_hud_adapter.js"
VISIBLE_SOURCE = "product/alpha/wof_alpha_auto_baseline_visible_hud.js"
P37_TESTED_COMMIT = "64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530"
SCHEMA = "wof-alpha-auto-baseline-visible-hud-v1"
CLASSIFICATION = "UNVERIFIED_AUTO_BASELINE"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}


class AutoBaselineHudError(RuntimeError):
    pass


class AutoBaselineHud:
    """Explicit staging-only bridge from P37 frames into the maintained HUD draw chain.

    This bridge does not capture frames, click avatars, seed players, bind production
    authority, or alter renderer-source qualification. A later bounded harness may feed
    native 384x224 RGBA frames; P37 performs the automatic P1/P2/P3 acquisition.
    """

    def __init__(self, verified_text: Callable[[str], str]) -> None:
        self._verified_text = verified_text
        self._session: CdpSession | None = None
        self._last = self._base("UNBOUND")

    @staticmethod
    def _base(state: str, **extra: Any) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "classification": CLASSIFICATION,
            "p37TestedCommit": P37_TESTED_COMMIT,
            "enabled": False,
            "state": state,
            "zeroClick": True,
            "manualAvatarClickRequired": False,
            "manualPortraitSeedRequired": False,
            "manualSeedRequired": False,
            "manualPlayerSelectionRequired": False,
            "automaticPlayers": ["P1", "P2", "P3"],
            "automaticReacquire": True,
            "nativeWidth": 384,
            "nativeHeight": 224,
            "nativeYAxis": "TOP_LEFT_POSITIVE_DOWN",
            "viewportYInversion": False,
            "rendererSourceProof": None,
            "authorityEligibility": {
                "p29Pass": False,
                "p32NativeMarkerQualification": False,
                "p36RendererSourceTrace": False,
                "p34RetryReadiness": False,
                "promotion": False,
            },
            "promotionEligibility": False,
            "productAuthority": "NONE_DIAGNOSTIC_ONLY",
            "visiblePlayers": [],
            "safety": dict(SAFETY),
            **extra,
        }

    @staticmethod
    def _validate(remote: Any) -> dict[str, Any]:
        if not isinstance(remote, dict) or remote.get("schema") != SCHEMA:
            raise AutoBaselineHudError("P39 diagnostic HUD remote schema invalid")
        if remote.get("classification") != CLASSIFICATION or remote.get("p37TestedCommit") != P37_TESTED_COMMIT:
            raise AutoBaselineHudError("P39 diagnostic HUD P37 identity invalid")
        if remote.get("zeroClick") is not True:
            raise AutoBaselineHudError("P39 zero-click contract invalid")
        for key in ("manualAvatarClickRequired", "manualPortraitSeedRequired", "manualSeedRequired", "manualPlayerSelectionRequired"):
            if remote.get(key) is not False:
                raise AutoBaselineHudError(f"P39 manual interaction boundary invalid: {key}")
        if remote.get("nativeWidth") != 384 or remote.get("nativeHeight") != 224 or remote.get("nativeYAxis") != "TOP_LEFT_POSITIVE_DOWN" or remote.get("viewportYInversion") is not False:
            raise AutoBaselineHudError("P39 native coordinate contract invalid")
        if remote.get("rendererSourceProof") is not None or remote.get("promotionEligibility") is not False or remote.get("productAuthority") != "NONE_DIAGNOSTIC_ONLY":
            raise AutoBaselineHudError("P39 authority boundary invalid")
        eligibility = remote.get("authorityEligibility")
        if not isinstance(eligibility, dict) or any(eligibility.get(k) is not False for k in ("p29Pass", "p32NativeMarkerQualification", "p36RendererSourceTrace", "p34RetryReadiness", "promotion")):
            raise AutoBaselineHudError("P39 authority eligibility must remain false")
        safety = remote.get("safety")
        if not isinstance(safety, dict) or safety.get("readOnly") is not True or safety.get("ramWrites") != 0 or safety.get("inputInjection") is not False:
            raise AutoBaselineHudError("P39 safety boundary invalid")
        return dict(remote)

    @staticmethod
    def _status_expr(action: str = "") -> str:
        action_src = action or ""
        return f"""(()=>{{const h=window.WOFALPHAAUTOBASELINEHUD;if(!h||typeof h.status!=='function')return null;{action_src}return h.status();}})()"""

    def bind(self, client: CdpClient, page_target_id: str) -> dict[str, Any]:
        self.dispose()
        self._session = client.attach(page_target_id)
        self._session.request("Runtime.enable")
        try:
            ready = self._session.evaluate(
                "!!(window.WOFALPHAHUD&&typeof window.WOFALPHAHUD.status==='function'&&window.__WOF_GL_HOOK&&typeof window.__WOF_GL_HOOK.callback==='function')",
                timeout=5.0,
            )
            if ready is not True:
                raise AutoBaselineHudError("maintained Alpha HUD diagnostic draw chain unavailable")
            self._session.evaluate("window.WOFALPHAAUTOBASELINEHUD?.dispose?.();true", timeout=3.0)
            for rel in (P37_SOURCE, ADAPTER_SOURCE, VISIBLE_SOURCE):
                source = self._verified_text(rel)
                self._session.evaluate(f"(0,eval)({json.dumps(source)});true", timeout=15.0)
            remote = self._session.evaluate(
                "(()=>{const f=window.WOFAutoBaselineVisibleHUDP39;if(!f||typeof f.install!=='function')return null;const h=f.install();h.enable();return h.status();})()",
                timeout=5.0,
            )
            self._last = self._validate(remote)
        except Exception as exc:
            self.dispose()
            if isinstance(exc, AutoBaselineHudError):
                raise
            raise AutoBaselineHudError(f"P39 diagnostic HUD bind failed: {exc}") from exc
        return self.status()

    def ingest_frame(self, frame: Mapping[str, Any], timestamp_ms: float) -> dict[str, Any]:
        if not self._session:
            return self.status()
        if not isinstance(frame, Mapping) or not math.isfinite(float(timestamp_ms)):
            raise AutoBaselineHudError("P39 native frame/timestamp invalid")
        payload = json.dumps(dict(frame), separators=(",", ":"))
        call = f"h.ingestFrame({payload},{json.dumps(float(timestamp_ms))});"
        try:
            remote = self._session.evaluate(self._status_expr(call), timeout=8.0)
            self._last = self._validate(remote)
        except Exception as exc:
            if isinstance(exc, AutoBaselineHudError):
                raise
            raise AutoBaselineHudError(f"P39 diagnostic HUD frame ingest failed: {exc}") from exc
        return self.status()

    def refresh(self) -> dict[str, Any]:
        if not self._session:
            return self.status()
        try:
            self._last = self._validate(self._session.evaluate(self._status_expr(), timeout=5.0))
        except Exception as exc:
            if isinstance(exc, AutoBaselineHudError):
                raise
            raise AutoBaselineHudError(f"P39 diagnostic HUD status read failed: {exc}") from exc
        return self.status()

    def disable(self) -> dict[str, Any]:
        if not self._session:
            return self.status()
        try:
            remote = self._session.evaluate(self._status_expr("h.disable('STAGING_GATE_CLOSED');"), timeout=5.0)
            self._last = self._validate(remote)
        except Exception as exc:
            if isinstance(exc, AutoBaselineHudError):
                raise
            raise AutoBaselineHudError(f"P39 diagnostic HUD disable failed: {exc}") from exc
        return self.status()

    def status(self) -> dict[str, Any]:
        return dict(self._last)

    def dispose(self) -> None:
        if self._session:
            try:
                self._session.evaluate("window.WOFALPHAAUTOBASELINEHUD?.dispose?.();true", timeout=3.0)
            except Exception:
                pass
            try:
                self._session.close()
            except Exception:
                pass
        self._session = None
        self._last = self._base("UNBOUND")
