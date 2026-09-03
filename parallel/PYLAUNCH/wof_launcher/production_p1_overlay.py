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
        self._last: dict[str, Any] = {"schema": SCHEMA, "visible": False, "drawCount": 0, "drawHooked": False, "hudSource": SOURCE, **SAFETY}

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
            call = f"h.bindP1HeadTrackerAuthority({json.dumps(binding)})"
            remote = self._session.evaluate(self._status_expr(authority_key, runtime_epoch, call), timeout=5.0)
        except Exception as exc:
            self.dispose()
            raise ProductionP1OverlayError(f"maintained Alpha HUD P1 binding failed: {exc}") from exc
        self._authority_key = authority_key
        self._runtime_epoch = runtime_epoch
        self._last = self._validate(remote, authority_key, runtime_epoch)
        self._last["installMode"] = self._install_mode
        return self.status()

    def update(self, visual: dict[str, Any], layout: dict[str, Any] | None, frame_size: tuple[int, int], actor_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self._session or not self._authority_key or not self._runtime_epoch:
            return self.status()
        center = visual.get("center") if isinstance(visual, dict) else None
        visible = bool(isinstance(center, list) and len(center) >= 2 and visual.get("state") == "HEAD_TRACKING" and int(visual.get("lostFrames") or 0) == 0 and isinstance(layout, dict))
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
            self._last = self._validate(remote, self._authority_key, self._runtime_epoch)
            self._last["installMode"] = self._install_mode
        except Exception as exc:
            raise ProductionP1OverlayError(f"maintained Alpha HUD P1 update failed: {exc}") from exc
        return self.status()

    def status(self) -> dict[str, Any]:
        return dict(self._last)

    def visible_and_drawn(self) -> bool:
        return bool(self._last.get("visible") is True and int(self._last.get("drawCount") or 0) > 0 and self._last.get("drawHooked") is True)

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
        self._last = {"schema": SCHEMA, "visible": False, "drawCount": 0, "drawHooked": False, "hudSource": SOURCE, **SAFETY}
