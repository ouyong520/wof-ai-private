from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any, Callable

from .cdp import CdpClient
from .discovery_v2 import TargetChoice
from .probe import WORLD_SHA256


PROOF_SCHEMA = "wof-owner-projection-proof-result-v1"
WORKER_SOURCE = "parallel/HUDANCHOR_PROOF/wof_owner_projection_worker.js"
TOP_SOURCE = "parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js"
GL_SOURCE = "parallel/HUDANCHOR_PROOF/wof_hudanchor_gl.js"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
_CAMERA_RE = re.compile(r"^0x([0-9A-Fa-f]{6})$")


class ProjectionRecoveryError(RuntimeError):
    pass


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


class ProjectionRecovery:
    """One-process live proof authority for the unproved Alpha projection profiles.

    The resulting constants are accepted only from the package-selected proof UI read
    directly over the currently accepted CDP page. They are deliberately not loaded
    from an arbitrary serialized file on a later launcher start. This prevents a local
    JSON edit from masquerading as live projection authority.
    """

    def __init__(self, verified_text: Callable[[str], str]) -> None:
        self._verified_text = verified_text
        self._authority_key: str | None = None
        self._page_id: str | None = None
        self._worker_id: str | None = None
        self._profiles: dict[str, dict[str, Any]] | None = None
        self._proof_result: dict[str, Any] | None = None
        self._state = "UNPROVED"
        self._error: str | None = None

    @staticmethod
    def _eval(client: CdpClient, target_id: str, expression: str, *, await_promise: bool = False, timeout: float = 12.0) -> Any:
        session = client.attach(target_id)
        try:
            session.request("Runtime.enable")
            return session.evaluate(expression, await_promise=await_promise, timeout=timeout)
        finally:
            session.close()

    def profiles(self) -> dict[str, dict[str, Any]] | None:
        return None if self._profiles is None else {k: dict(v) for k, v in self._profiles.items()}

    def proof_result(self) -> dict[str, Any] | None:
        return None if self._proof_result is None else json.loads(json.dumps(self._proof_result))

    def status(self) -> dict[str, Any]:
        return {
            "state": self._state,
            "authorityKey": self._authority_key,
            "provedInCurrentLauncherProcess": self._profiles is not None,
            "error": self._error,
            **SAFETY,
        }

    def ensure_started(self, client: CdpClient, choice: TargetChoice, authority_key: str) -> dict[str, Any]:
        if self._profiles is not None:
            self._state = "PROVED_LIVE_PROCESS_AUTHORITY"
            return self.status()
        if self._authority_key == authority_key and self._state == "CALIBRATING":
            return self.status()
        if not choice.page or not choice.worker:
            raise ProjectionRecoveryError("projection proof requires accepted page/Worker pair")
        page_id = str(choice.page.get("targetId") or "")
        worker_id = str(choice.worker.get("targetId") or "")
        if not page_id or not worker_id:
            raise ProjectionRecoveryError("projection proof target id missing")
        self.stop_runtime(client)
        worker_source = self._verified_text(WORKER_SOURCE)
        top_source = self._verified_text(TOP_SOURCE)
        gl_source = self._verified_text(GL_SOURCE)
        try:
            self._eval(client, worker_id, "try{self.WOFOWNERPROJECTION?.stop?.()}catch(_){}; true")
            self._eval(client, worker_id, f"(0,eval)({json.dumps(worker_source)}); true", timeout=15.0)
            top_expr = (
                "(async()=>{try{window.WOFOWNERPROJECTION?.stop?.()}catch(_){};"
                f"window.__WOF_OWNER_PROJECTION_GL_SOURCE={json.dumps(gl_source)};"
                f"(0,eval)({json.dumps(top_source)});"
                "for(let i=0;i<100;i++){if(window.WOFOWNERPROJECTION?.status)return window.WOFOWNERPROJECTION.status();await new Promise(r=>setTimeout(r,20));}"
                "throw new Error('projection proof top did not initialize')})()"
            )
            status = self._eval(client, page_id, top_expr, await_promise=True, timeout=15.0)
        except Exception as exc:
            self._state = "ERROR"
            self._error = str(exc)
            raise ProjectionRecoveryError(str(exc)) from exc
        if not isinstance(status, dict) or status.get("running") is not True:
            self._state = "ERROR"
            self._error = "projection proof top did not enter running state"
            raise ProjectionRecoveryError(self._error)
        self._authority_key = authority_key
        self._page_id = page_id
        self._worker_id = worker_id
        self._state = "CALIBRATING"
        self._error = None
        return self.status()

    def poll(self, client: CdpClient, authority_key: str) -> dict[str, Any]:
        if self._profiles is not None:
            return {**self.status(), "newProfiles": False, "proofResult": self.proof_result()}
        if self._state != "CALIBRATING" or self._authority_key != authority_key or not self._page_id:
            return {**self.status(), "newProfiles": False}
        try:
            status = self._eval(client, self._page_id, "window.WOFOWNERPROJECTION?.status?.()||null")
        except Exception as exc:
            self._state = "ERROR"; self._error = str(exc)
            return {**self.status(), "newProfiles": False}
        if not isinstance(status, dict):
            self._state = "ERROR"; self._error = "projection proof top disappeared"
            return {**self.status(), "newProfiles": False}
        if status.get("terminal") is not True:
            return {**self.status(), "newProfiles": False, "ui": status}
        result = self._eval(client, self._page_id, "window.WOFOWNERPROJECTION?.terminalResult?.()||null")
        try:
            profiles, accepted = self._profiles_from_result(result)
        except ProjectionRecoveryError as exc:
            self._state = "FAILED_LIVE_PROOF"; self._error = str(exc)
            self._proof_result = result if isinstance(result, dict) else {"verdict": "MALFORMED"}
            self.stop_runtime(client, preserve_state=True)
            return {**self.status(), "newProfiles": False, "proofResult": self.proof_result()}
        self._profiles = profiles
        self._proof_result = accepted
        self._state = "PROVED_LIVE_PROCESS_AUTHORITY"
        self._error = None
        self.stop_runtime(client, preserve_state=True)
        return {**self.status(), "newProfiles": True, "proofResult": self.proof_result()}

    def _profiles_from_result(self, result: Any) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
        if not isinstance(result, dict) or result.get("schema") != PROOF_SCHEMA:
            raise ProjectionRecoveryError("live projection proof returned malformed schema")
        if result.get("verdict") != "IMPLEMENTATION_READY":
            raise ProjectionRecoveryError(str(result.get("verdict") or "live projection proof did not pass"))
        boundaries = result.get("boundaries")
        if not isinstance(boundaries, dict) or boundaries.get("readOnly") is not True or boundaries.get("ramWrites") != 0 or boundaries.get("inputInjection") is not False or boundaries.get("guessedConstants") is not False or boundaries.get("syntheticAuthority") is not False:
            raise ProjectionRecoveryError("live projection proof safety boundary mismatch")
        p = result.get("projection")
        if not isinstance(p, dict):
            raise ProjectionRecoveryError("live projection proof projection block missing")
        camera = p.get("camera") if isinstance(p.get("camera"), dict) else {}
        native = p.get("native") if isinstance(p.get("native"), dict) else {}
        match = _CAMERA_RE.fullmatch(str(camera.get("address") or ""))
        if not match:
            raise ProjectionRecoveryError("live projection camera address invalid")
        camera_address = int(match.group(1), 16)
        if camera_address < 0xFF0000 or camera_address >= 0xFFBE00 or ((camera_address - 0xFF0000) & 1):
            raise ProjectionRecoveryError("live projection camera address outside bounded scan")
        if camera.get("read") != "u16be" or camera.get("sign") != 1 or camera.get("scale") != 1:
            raise ProjectionRecoveryError("live projection camera read/sign/scale invalid")
        if native.get("width") != 384 or native.get("height") != 224:
            raise ProjectionRecoveryError("live projection native viewport invalid")
        x_bias = native.get("xBias"); y_bias = native.get("yBias"); y_model = native.get("yModel")
        if not _finite(x_bias) or not _finite(y_bias) or y_model not in {"Y-Z", "Y+Z", "Y"}:
            raise ProjectionRecoveryError("live projection affine constants invalid")
        raw_offsets = p.get("enemyHeadOffsetsByType")
        if not isinstance(raw_offsets, dict) or not raw_offsets:
            raise ProjectionRecoveryError("live projection has no visually confirmed enemy type")
        enemy_offsets: dict[str, float] = {}
        for key, value in raw_offsets.items():
            try: type_id = int(key)
            except Exception as exc: raise ProjectionRecoveryError("enemy type key invalid") from exc
            if str(type_id) != str(key) or not 0 <= type_id < 47 or not _finite(value):
                raise ProjectionRecoveryError("enemy head offset invalid")
            enemy_offsets[str(type_id)] = float(value)
        proof_digest = hashlib.sha256(_canonical_bytes(result)).hexdigest()
        proof_id = "live-" + proof_digest[:24]
        z_scale = -1 if y_model == "Y-Z" else 1 if y_model == "Y+Z" else 0
        # HUDANCHOR's selected yBias is the exact raw floor/Z -> desired head-anchor
        # displacement. Preserve that affine transform exactly; headClearanceNative
        # is zero rather than inventing a second offset decomposition.
        player_profile = {
            "schema": "wof-alpha-player-head-projection-v1",
            "status": "PROVED",
            "activation": "LIVE_PROCESS_BOUND_OWNER_PROOF",
            "projectionKind": "world-camera-floor-z-affine-v1",
            "proofId": proof_id,
            "projectionVersion": "live-v1-" + proof_digest[:16],
            "source": "package-selected owner projection proof",
            "nativeWidth": 384, "nativeHeight": 224,
            "cameraAddress": camera_address, "cameraSign": 1, "cameraScale": 1,
            "worldXScale": 1, "xBias": float(x_bias),
            "floorYScale": 1, "zScale": z_scale, "yBias": float(y_bias),
            "headClearanceNative": 0,
            "validationBounds": {"minX": 0, "maxX": 384, "minY": 0, "maxY": 224},
            "safety": {"failClosed": True, "fixedHudFallback": True, "guessedConstants": False},
        }
        enemy_profile = {
            "schema": "wof-alpha-enemy-head-projection-v1",
            "verdict": "IMPLEMENTATION_READY",
            "proofId": proof_id,
            "romSha256": WORLD_SHA256,
            "nativeWidth": 384, "nativeHeight": 224,
            "cameraAddress": camera_address, "cameraRead": "u16be", "cameraSign": 1, "cameraScale": 1,
            "xBias": float(x_bias), "yModel": y_model,
            "evidence": "package-selected owner projection proof; only visually confirmed live enemy types are enabled",
            "status": "LIVE_PROCESS_BOUND_OWNER_PROOF",
            "enemyHeadOffsetsByType": enemy_offsets,
        }
        accepted = dict(result)
        accepted["proofId"] = proof_id
        accepted["proofDigestSha256"] = proof_digest
        accepted["worldSha256"] = WORLD_SHA256
        accepted["derivedProfiles"] = {"player": player_profile, "enemy": enemy_profile}
        accepted["authorityPersistence"] = "CURRENT_LAUNCHER_PROCESS_ONLY"
        return {"player": player_profile, "enemy": enemy_profile}, accepted

    def stop_runtime(self, client: CdpClient | None = None, *, preserve_state: bool = False) -> None:
        if client and self._worker_id:
            try: self._eval(client, self._worker_id, "try{self.WOFOWNERPROJECTION?.stop?.();true}catch(_){false}")
            except Exception: pass
        if client and self._page_id:
            try: self._eval(client, self._page_id, "try{window.WOFOWNERPROJECTION?.stop?.();true}catch(_){false}")
            except Exception: pass
        self._authority_key = None
        self._page_id = None
        self._worker_id = None
        if not preserve_state and self._profiles is None:
            self._state = "UNPROVED"
            self._error = None
