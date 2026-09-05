from __future__ import annotations

import json
from typing import Any, Callable

from .cdp import CdpClient, CdpSession

HUD_SOURCES = (
    "product/alpha/wof_alpha_hud_model.js",
    "product/alpha/wof_alpha_enemy_target_labels.js",
    "product/alpha/wof_alpha_player_head_warning.js",
    "product/alpha/wof_alpha_relative_head_anchor.js",
    "product/alpha/wof_alpha_hud.js",
    "product/alpha/wof_alpha_relative_enemy_overlay.js",
)
SOURCE = "product/alpha/wof_alpha_hud.js"
SCHEMA = "wof-alpha-production-p1-overlay-adapter-v1"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False, "productionOverlayEnabled": True}

FIXED_SMOKE_SCHEMA = "wof-alpha-fixed-draw-smoke-probe-v1"
FIXED_SMOKE_STATUS_KEY = "__WOF_ALPHA_FIXED_DRAW_SMOKE_STATUS_V1"
FIXED_SMOKE_STATES = {
    "HUD_INJECTION_MISSING",
    "GAME_CANVAS_CONTEXT_MISSING",
    "DRAW_HOOK_NOT_FIRING",
    "DRAWING_BUFFER_INVALID",
    "FIXED_TEST_ACTUALLY_DRAWN",
    "DRAW_FAILED",
    "DISABLED",
}

_DIAGNOSTIC_SUPPRESS_EXPR = r"""
(()=>{const b=window.WOFHEADVISUALV3;
if(!b||typeof b.showMarker!=='function')return false;
if(!b.__WOF_ALPHA_PRODUCT_MARKER_ORIGINAL_V1){
  const original=b.showMarker.bind(b);
  Object.defineProperty(b,'__WOF_ALPHA_PRODUCT_MARKER_ORIGINAL_V1',{value:original,configurable:true});
  b.showMarker=function(x,y,_visible){return original(x,y,false);};
}
b.showMarker(0,0,false);
return true;})()
"""


class ProductionP1OverlayError(RuntimeError):
    pass


class ProductionP1Overlay:
    """Feeds verified P1 tracker authority into the maintained Alpha production HUD."""

    def __init__(self, verified_text: Callable[[str], str]) -> None:
        self._verified_text = verified_text
        self._session: CdpSession | None = None
        self._authority_key: str | None = None
        self._runtime_epoch: str | None = None
        self._owns_hud = False
        self._install_mode = "UNBOUND"
        self._draw_baseline = 0
        self._tracker_generation = 0
        self._diagnostic_marker_suppressed = False
        self._last: dict[str, Any] = {
            "schema": SCHEMA,
            "visible": False,
            "drawCount": 0,
            "drawHooked": False,
            "drawnCurrentTracker": False,
            "trackerGeneration": 0,
            "drawBaseline": 0,
            "diagnosticMarkerSuppressed": False,
            "hudSource": SOURCE,
            **SAFETY,
        }

    @staticmethod
    def _validate(remote: Any, authority_key: str, runtime_epoch: str) -> dict[str, Any]:
        if not isinstance(remote, dict) or remote.get("schema") != SCHEMA:
            raise ProductionP1OverlayError("production P1 overlay adapter malformed remote schema")
        if remote.get("authorityKey") != authority_key or remote.get("runtimeEpoch") != runtime_epoch:
            raise ProductionP1OverlayError("production P1 overlay stale/runtime-generation mismatch")
        if remote.get("productionOverlayEnabled") is not True or remote.get("readOnly") is not True or remote.get("ramWrites") != 0 or remote.get("inputInjection") is not False:
            raise ProductionP1OverlayError("production P1 overlay safety boundary mismatch")
        return dict(remote)

    @staticmethod
    def _status_expr(authority_key: str, runtime_epoch: str, call: str) -> str:
        return """(()=>{const h=window.WOFALPHAHUD;if(!h||typeof h.status!=='function')return null;const t=(CALL);const s=h.status();const r=window.WOFALPHARELATIVEENEMY?.status?.()||null;return {schema:SCHEMA,authorityKey:AUTH,runtimeEpoch:EPOCH,productionOverlayEnabled:true,visible:t?.visible===true,drawCount:Number(t?.drawCount||0),drawHooked:s?.drawHooked===true,hudVersion:String(s?.version||''),hudSource:'product/alpha/wof_alpha_hud.js',tracker:t||null,relativeEnemy:r,readOnly:true,ramWrites:0,inputInjection:false};})()""".replace("CALL", call).replace("SCHEMA", json.dumps(SCHEMA)).replace("AUTH", json.dumps(authority_key)).replace("EPOCH", json.dumps(runtime_epoch))

    def _decorate(self, remote: dict[str, Any]) -> dict[str, Any]:
        out = dict(remote)
        draw_count = int(out.get("drawCount") or 0)
        out["trackerGeneration"] = self._tracker_generation
        out["drawBaseline"] = self._draw_baseline
        out["drawnCurrentTracker"] = bool(
            out.get("visible") is True
            and out.get("drawHooked") is True
            and self._tracker_generation > 0
            and draw_count > self._draw_baseline
        )
        out["diagnosticMarkerSuppressed"] = self._diagnostic_marker_suppressed
        return out

    def _suppress_diagnostic_marker(self) -> bool:
        if not self._session:
            return False
        try:
            return self._session.evaluate(_DIAGNOSTIC_SUPPRESS_EXPR, timeout=5.0) is True
        except Exception:
            return False

    def bind(self, client: CdpClient, page_target_id: str, authority_key: str, runtime_epoch: str) -> dict[str, Any]:
        self.dispose()
        self._session = client.attach(page_target_id)
        self._session.request("Runtime.enable")
        binding = {"authorityKey": authority_key, "runtimeEpoch": runtime_epoch}
        try:
            compatible = self._session.evaluate("!!(window.WOFALPHAHUD&&typeof window.WOFALPHAHUD.bindP1HeadTrackerAuthority==='function'&&typeof window.WOFALPHAHUD.setP1HeadTracker==='function'&&typeof window.WOFALPHAHUD.clearP1HeadTrackerAuthority==='function'&&window.WOFALPHARELATIVEENEMY?.version==='wof-alpha-relative-enemy-overlay-v1')", timeout=5.0)
            if compatible is not True:
                prep = f"""(()=>{{const c=window.__WOF_ALPHA_CONFIG,t=window.__WOF_ALPHA_TRANSPORT_V1;const ok=!!(c&&c.release==='wof-alpha-rc3'&&typeof c.session==='string'&&c.session.length>=16&&typeof c.channel==='string'&&t&&t.version==='wof-alpha-safe-transport-v1'&&typeof t.matches==='function');if(ok)return 'PRESERVED_CONFIG';const session={json.dumps(runtime_epoch)},channel={json.dumps('wof-alpha-v3-direct-'+runtime_epoch)};window.__WOF_ALPHA_CONFIG={{release:'wof-alpha-rc3',session,channel}};window.__WOF_ALPHA_TRANSPORT_V1={{version:'wof-alpha-safe-transport-v1',matches:m=>!!m&&m.session===session}};return 'DIRECT_CONFIG';}})()"""
                self._install_mode = str(self._session.evaluate(prep, timeout=5.0) or "DIRECT_CONFIG")
                self._owns_hud = self._install_mode == "DIRECT_CONFIG"
                for rel in HUD_SOURCES:
                    self._session.evaluate(f"(0,eval)({json.dumps(self._verified_text(rel))});true", timeout=15.0)
            else:
                self._install_mode = "EXISTING_PRODUCTION_HUD"
                self._owns_hud = False
            self._diagnostic_marker_suppressed = self._suppress_diagnostic_marker()
            call = f"h.bindP1HeadTrackerAuthority({json.dumps(binding)})"
            remote = self._session.evaluate(self._status_expr(authority_key, runtime_epoch, call), timeout=5.0)
        except Exception as exc:
            self.dispose()
            raise ProductionP1OverlayError(f"maintained Alpha HUD P1 binding failed: {exc}") from exc
        self._authority_key = authority_key
        self._runtime_epoch = runtime_epoch
        validated = self._validate(remote, authority_key, runtime_epoch)
        self._draw_baseline = int(validated.get("drawCount") or 0)
        self._last = self._decorate(validated)
        self._last["installMode"] = self._install_mode
        return self.status()

    def update(self, visual: dict[str, Any], layout: dict[str, Any] | None, frame_size: tuple[int, int], actor_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self._session or not self._authority_key or not self._runtime_epoch:
            return self.status()
        center = visual.get("center") if isinstance(visual, dict) else None
        visible = bool(isinstance(center, list) and len(center) >= 2 and visual.get("state") == "HEAD_TRACKING" and int(visual.get("lostFrames") or 0) == 0 and isinstance(layout, dict))
        was_visible = self._last.get("visible") is True
        if visible and not was_visible:
            self._tracker_generation += 1
            self._draw_baseline = int(self._last.get("drawCount") or 0)
        try:
            if isinstance(actor_snapshot, dict):
                self._session.evaluate(f"window.WOFALPHARELATIVEENEMY?.ingestActorSnapshot?.({json.dumps(actor_snapshot)});true", timeout=3.0)
            if visible:
                fw, fh = max(1, int(frame_size[0])), max(1, int(frame_size[1]))
                css_w, css_h = float(layout.get("width") or 0), float(layout.get("height") or 0)
                payload = {"authorityKey": self._authority_key, "runtimeEpoch": self._runtime_epoch, "visible": True, "x": float(center[0]) * css_w / fw, "y": float(center[1]) * css_h / fh, "seedSource": visual.get("seedSource")}
                call = f"h.setP1HeadTracker({json.dumps(payload)})"
            else:
                reason = str(visual.get("revocationReason") or visual.get("state") or "TRACKER_NOT_VISIBLE") if isinstance(visual, dict) else "TRACKER_NOT_VISIBLE"
                call = f"h.clearP1HeadTracker({json.dumps(reason)})"
            remote = self._session.evaluate(self._status_expr(self._authority_key, self._runtime_epoch, call), timeout=5.0)
            validated = self._validate(remote, self._authority_key, self._runtime_epoch)
            self._last = self._decorate(validated)
            self._last["installMode"] = self._install_mode
        except Exception as exc:
            raise ProductionP1OverlayError(f"maintained Alpha HUD P1 update failed: {exc}") from exc
        return self.status()

    def status(self) -> dict[str, Any]:
        return dict(self._last)

    def visible_and_drawn(self) -> bool:
        return bool(
            self._last.get("visible") is True
            and int(self._last.get("drawCount") or 0) > 0
            and self._last.get("drawHooked") is True
            and self._last.get("drawnCurrentTracker") is True
            and self._last.get("diagnosticMarkerSuppressed") is True
            and self._last.get("readOnly") is True
            and self._last.get("ramWrites") == 0
            and self._last.get("inputInjection") is False
        )

    def dispose(self) -> None:
        if self._session:
            try:
                if self._owns_hud:
                    self._session.evaluate("window.WOFALPHAHUD?.dispose?.();true", timeout=3.0)
                else:
                    self._session.evaluate("window.WOFALPHAHUD?.clearP1HeadTrackerAuthority?.('V3_AUTHORITY_REVOKED');true", timeout=3.0)
            except Exception:
                pass
            try:
                self._session.close()
            except Exception:
                pass
        self._session = None
        self._authority_key = None
        self._runtime_epoch = None
        self._owns_hud = False
        self._install_mode = "UNBOUND"
        self._draw_baseline = 0
        self._tracker_generation = 0
        self._diagnostic_marker_suppressed = False
        self._last = {
            "schema": SCHEMA,
            "visible": False,
            "drawCount": 0,
            "drawHooked": False,
            "drawnCurrentTracker": False,
            "trackerGeneration": 0,
            "drawBaseline": 0,
            "diagnosticMarkerSuppressed": False,
            "hudSource": SOURCE,
            **SAFETY,
        }


class ProductionHudFixedDrawSmoke:
    """Strictly opt-in fixed TEST probe using the maintained production WebGL HUD."""

    def __init__(self, verified_text: Callable[[str], str]) -> None:
        self._verified_text = verified_text
        self._session: CdpSession | None = None
        self._owns_hud = False
        self._install_mode = "UNBOUND"
        self._last = self._base("DISABLED")

    @staticmethod
    def _base(state: str, **extra: Any) -> dict[str, Any]:
        return {
            "schema": FIXED_SMOKE_SCHEMA,
            "state": state,
            "enabled": state != "DISABLED",
            "hudInjected": False,
            "gameCanvasContextPresent": False,
            "drawHooked": False,
            "drawCount": 0,
            "callbackCount": 0,
            "label": "TEST",
            "nativeWidth": 384,
            "nativeHeight": 224,
            "nativeX": 192,
            "nativeY": 112,
            "drawingBuffer": None,
            "lastError": None,
            "hudSource": SOURCE,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            **extra,
        }

    @staticmethod
    def _normalize(remote: Any) -> dict[str, Any]:
        if not isinstance(remote, dict):
            return ProductionHudFixedDrawSmoke._base("HUD_INJECTION_MISSING")
        state = str(remote.get("state") or "HUD_INJECTION_MISSING")
        if state not in FIXED_SMOKE_STATES:
            state = "HUD_INJECTION_MISSING"
        return ProductionHudFixedDrawSmoke._base(
            state,
            enabled=remote.get("enabled") is True,
            hudInjected=remote.get("hudInjected") is True,
            gameCanvasContextPresent=remote.get("gameCanvasContextPresent") is True,
            drawHooked=remote.get("drawHooked") is True,
            drawCount=int(remote.get("drawCount") or 0),
            callbackCount=int(remote.get("callbackCount") or 0),
            nativeWidth=int(remote.get("nativeWidth") or 384),
            nativeHeight=int(remote.get("nativeHeight") or 224),
            nativeX=int(remote.get("nativeX") or 192),
            nativeY=int(remote.get("nativeY") or 112),
            drawingBuffer=remote.get("drawingBuffer"),
            lastError=remote.get("lastError"),
        )

    @staticmethod
    def _remote_status_expr(enable: bool | None = None) -> str:
        action = "h.setFixedDrawSmokeEnabled(true)" if enable is True else "h.setFixedDrawSmokeEnabled(false)" if enable is False else "h.fixedDrawSmokeStatus()"
        return f"""(()=>{{const h=window.WOFALPHAHUD;if(!h||typeof h.fixedDrawSmokeStatus!=='function'||typeof h.setFixedDrawSmokeEnabled!=='function'){{const s=window[{json.dumps(FIXED_SMOKE_STATUS_KEY)}];return s&&s.state==='GAME_CANVAS_CONTEXT_MISSING'?s:null;}}{action};return h.fixedDrawSmokeStatus();}})()"""

    def enable(self, client: CdpClient, page_target_id: str, runtime_epoch: str) -> dict[str, Any]:
        self.dispose()
        self._session = client.attach(page_target_id)
        self._session.request("Runtime.enable")
        try:
            pre = self._session.evaluate(
                "(()=>{const c=window.I_GF1TC||document.getElementById('whathis'),g=window.I_fdC8Q;return {canvas:!!c,context:!!(g&&typeof g.drawArrays==='function')};})()",
                timeout=5.0,
            )
            if not isinstance(pre, dict) or pre.get("canvas") is not True or pre.get("context") is not True:
                self._last = self._base("GAME_CANVAS_CONTEXT_MISSING", enabled=True)
                return self.status()

            compatible = self._session.evaluate(
                "!!(window.WOFALPHAHUD&&typeof window.WOFALPHAHUD.fixedDrawSmokeStatus==='function'&&typeof window.WOFALPHAHUD.setFixedDrawSmokeEnabled==='function')",
                timeout=5.0,
            )
            if compatible is not True:
                prep = f"""(()=>{{const c=window.__WOF_ALPHA_CONFIG,t=window.__WOF_ALPHA_TRANSPORT_V1;const ok=!!(c&&c.release==='wof-alpha-rc3'&&typeof c.session==='string'&&c.session.length>=16&&typeof c.channel==='string'&&t&&t.version==='wof-alpha-safe-transport-v1'&&typeof t.matches==='function');if(ok)return 'PRESERVED_CONFIG';const session={json.dumps(runtime_epoch)},channel={json.dumps('wof-alpha-w2-fixed-smoke-'+runtime_epoch)};window.__WOF_ALPHA_CONFIG={{release:'wof-alpha-rc3',session,channel}};window.__WOF_ALPHA_TRANSPORT_V1={{version:'wof-alpha-safe-transport-v1',matches:m=>!!m&&m.session===session}};return 'DIRECT_CONFIG';}})()"""
                self._install_mode = str(self._session.evaluate(prep, timeout=5.0) or "DIRECT_CONFIG")
                self._owns_hud = self._install_mode == "DIRECT_CONFIG"
                for rel in HUD_SOURCES:
                    self._session.evaluate(f"(0,eval)({json.dumps(self._verified_text(rel))});true", timeout=15.0)
            else:
                self._install_mode = "EXISTING_PRODUCTION_HUD"
                self._owns_hud = False

            remote = self._session.evaluate(self._remote_status_expr(True), timeout=5.0)
            self._last = self._normalize(remote)
            self._last["installMode"] = self._install_mode
            if self._last["state"] == "HUD_INJECTION_MISSING":
                self._last["enabled"] = True
        except Exception as exc:
            remote = None
            try:
                if self._session:
                    remote = self._session.evaluate(self._remote_status_expr(), timeout=3.0)
            except Exception:
                pass
            self._last = self._normalize(remote)
            if self._last["state"] not in {"GAME_CANVAS_CONTEXT_MISSING", "DRAWING_BUFFER_INVALID"}:
                self._last = self._base("HUD_INJECTION_MISSING", enabled=True, lastError=str(exc))
        return self.status()

    def poll(self) -> dict[str, Any]:
        if not self._session:
            return self.status()
        try:
            remote = self._session.evaluate(self._remote_status_expr(), timeout=5.0)
            self._last = self._normalize(remote)
            self._last["installMode"] = self._install_mode
        except Exception as exc:
            self._last = self._base("HUD_INJECTION_MISSING", enabled=True, lastError=str(exc))
        return self.status()

    def status(self) -> dict[str, Any]:
        return dict(self._last)

    def fixed_test_actually_drawn(self) -> bool:
        return bool(
            self._last.get("state") == "FIXED_TEST_ACTUALLY_DRAWN"
            and self._last.get("hudInjected") is True
            and self._last.get("gameCanvasContextPresent") is True
            and self._last.get("drawHooked") is True
            and int(self._last.get("drawCount") or 0) > 0
            and self._last.get("label") == "TEST"
            and self._last.get("nativeWidth") == 384
            and self._last.get("nativeHeight") == 224
            and self._last.get("nativeX") == 192
            and self._last.get("nativeY") == 112
        )

    def dispose(self) -> None:
        if self._session:
            try:
                self._session.evaluate(self._remote_status_expr(False), timeout=3.0)
            except Exception:
                pass
            try:
                if self._owns_hud:
                    self._session.evaluate("window.WOFALPHAHUD?.dispose?.();true", timeout=3.0)
            except Exception:
                pass
            try:
                self._session.close()
            except Exception:
                pass
        self._session = None
        self._owns_hud = False
        self._install_mode = "UNBOUND"
        self._last = self._base("DISABLED")
