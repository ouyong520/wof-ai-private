from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any, Callable

from .cdp import CdpClient
from .discovery_v2 import TargetChoice
from .probe import WORLD_SHA256


PROOF_SCHEMA = "wof-owner-projection-proof-result-v2"
WORKER_SOURCE = "parallel/HUDANCHOR_PROOF/wof_owner_projection_worker.js"
TOP_SOURCE = "parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js"
GL_SOURCE = "parallel/HUDANCHOR_PROOF/wof_hudanchor_gl.js"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
_CAMERA_RE = re.compile(r"^0x([0-9A-Fa-f]{6})$")
_MIN_PAIRED = 36
_MIN_HOLDOUT = 8
_MAX_TRAIN_RMS = 3.25
_MAX_HOLDOUT_RMS = 4.0
_MAX_HOLDOUT_ABS = 8.0
_MIN_ENEMY_SAMPLES = 8
_MAX_ENEMY_MAD = 3.5


class ProjectionRecoveryError(RuntimeError):
    pass


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _range_pair(value: Any, name: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2 or not all(_finite(v) for v in value):
        raise ProjectionRecoveryError(f"live projection {name} envelope invalid")
    lo, hi = float(value[0]), float(value[1])
    if lo > hi:
        raise ProjectionRecoveryError(f"live projection {name} envelope reversed")
    return lo, hi


class ProjectionRecovery:
    """Package-selected live projection proof bound to one accepted runtime authority.

    The proof is deliberately process-local. A result is accepted only from the
    currently installed package-selected Top/Worker proof, and the derived profiles
    are tagged with the exact launcher authority key that produced them. A later
    page/Worker/runtime generation must clear them before Alpha can reactivate.
    """

    def __init__(self, verified_text: Callable[[str], str]) -> None:
        self._verified_text = verified_text
        self._authority_key: str | None = None
        self._page_id: str | None = None
        self._worker_id: str | None = None
        self._profiles: dict[str, dict[str, Any]] | None = None
        self._profile_authority_key: str | None = None
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

    def profiles(self, authority_key: str | None = None) -> dict[str, dict[str, Any]] | None:
        if self._profiles is None:
            return None
        if authority_key is not None and authority_key != self._profile_authority_key:
            if not (self._profile_authority_key is None and self._state == "PROVED_LIVE_PROCESS_AUTHORITY"):
                return None
        return {k: json.loads(json.dumps(v)) for k, v in self._profiles.items()}

    def has_profiles_for(self, authority_key: str) -> bool:
        return self._profiles is not None and (self._profile_authority_key == authority_key or (self._profile_authority_key is None and self._state == "PROVED_LIVE_PROCESS_AUTHORITY"))

    def clear_profiles(self, reason: str = "authority-revoked") -> None:
        if self._profiles is not None:
            self._error = reason
        self._profiles = None
        self._profile_authority_key = None
        self._proof_result = None
        self._state = "UNPROVED"

    def proof_result(self) -> dict[str, Any] | None:
        return None if self._proof_result is None else json.loads(json.dumps(self._proof_result))

    def status(self) -> dict[str, Any]:
        return {
            "state": self._state,
            "authorityKey": self._authority_key,
            "profileAuthorityKey": self._profile_authority_key,
            "provedInCurrentLauncherProcess": self._profiles is not None,
            "error": self._error,
            **SAFETY,
        }

    def ensure_started(self, client: CdpClient, choice: TargetChoice, authority_key: str) -> dict[str, Any]:
        if self.has_profiles_for(authority_key):
            self._state = "PROVED_LIVE_PROCESS_AUTHORITY"
            return self.status()
        if self._profiles is not None and self._profile_authority_key != authority_key:
            self.clear_profiles("accepted runtime authority changed")
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
        if self.has_profiles_for(authority_key):
            return {**self.status(), "newProfiles": False, "proofResult": self.proof_result()}
        if self._profiles is not None and self._profile_authority_key != authority_key:
            self.clear_profiles("accepted runtime authority changed")
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
            profiles, accepted = self._profiles_from_result(result, authority_key)
        except ProjectionRecoveryError as exc:
            self._state = "FAILED_LIVE_PROOF"; self._error = str(exc)
            self._proof_result = result if isinstance(result, dict) else {"verdict": "MALFORMED"}
            self.stop_runtime(client, preserve_state=True)
            return {**self.status(), "newProfiles": False, "proofResult": self.proof_result()}
        self._profiles = profiles
        self._profile_authority_key = authority_key
        self._proof_result = accepted
        self._state = "PROVED_LIVE_PROCESS_AUTHORITY"
        self._error = None
        self.stop_runtime(client, preserve_state=True)
        return {**self.status(), "newProfiles": True, "proofResult": self.proof_result()}

    def _profiles_from_result(self, result: Any, authority_key: str) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
        if not isinstance(result, dict) or result.get("schema") != PROOF_SCHEMA:
            raise ProjectionRecoveryError("live projection proof returned malformed schema")
        if result.get("verdict") != "IMPLEMENTATION_READY":
            raise ProjectionRecoveryError(str(result.get("verdict") or "live projection proof did not pass"))
        boundaries = result.get("boundaries")
        if not isinstance(boundaries, dict) or boundaries.get("readOnly") is not True or boundaries.get("ramWrites") != 0 or boundaries.get("inputInjection") is not False or boundaries.get("guessedConstants") is not False or boundaries.get("syntheticAuthority") is not False:
            raise ProjectionRecoveryError("live projection proof safety boundary mismatch")
        if boundaries.get("ownerModelChoice") is not False or boundaries.get("simultaneousCandidateLabels") is not False or boundaries.get("maxCalibrationClicksPerAuthorityGeneration") != 1:
            raise ProjectionRecoveryError("live projection proof owner simplicity boundary mismatch")

        binding = result.get("authorityBinding")
        if not isinstance(binding, dict) or not isinstance(binding.get("workerSessionId"), str) or not binding.get("workerSessionId"):
            raise ProjectionRecoveryError("live projection authority binding missing worker session")
        for key in ("sequenceStart", "sequenceEnd", "p1LifecycleGeneration", "cameraAuthorityGeneration"):
            if not isinstance(binding.get(key), int) or isinstance(binding.get(key), bool) or binding[key] < 1:
                raise ProjectionRecoveryError(f"live projection authority binding invalid {key}")
        if binding["sequenceEnd"] < binding["sequenceStart"]:
            raise ProjectionRecoveryError("live projection proof sequence window reversed")
        if not isinstance(binding.get("cameraAuthorityId"), str) or not binding["cameraAuthorityId"]:
            raise ProjectionRecoveryError("live projection camera authority id missing")

        cal = result.get("calibration")
        if not isinstance(cal, dict) or cal.get("interactionMode") != "ONE_CLICK_VISUAL_SEED" or cal.get("clickCount") != 1:
            raise ProjectionRecoveryError("live projection interaction budget invalid")
        if not isinstance(cal.get("pairedSampleCount"), int) or cal["pairedSampleCount"] < _MIN_PAIRED:
            raise ProjectionRecoveryError("live projection paired sample count insufficient")
        if not isinstance(cal.get("holdoutSampleCount"), int) or cal["holdoutSampleCount"] < _MIN_HOLDOUT:
            raise ProjectionRecoveryError("live projection holdout sample count insufficient")

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
        if camera.get("read") != "u16be" or camera.get("sign") not in {-1, 1} or not _finite(camera.get("scale")) or float(camera["scale"]) <= 0:
            raise ProjectionRecoveryError("live projection camera read/sign/scale invalid")
        if camera.get("authorityId") != binding.get("cameraAuthorityId") or camera.get("authorityGeneration") != binding.get("cameraAuthorityGeneration") or camera.get("address") != binding.get("cameraAddress"):
            raise ProjectionRecoveryError("live projection camera authority binding mismatch")
        if native.get("width") != 384 or native.get("height") != 224 or native.get("projectionKind") != "world-camera-floor-z-affine-v2":
            raise ProjectionRecoveryError("live projection native viewport/kind invalid")
        for key in ("worldXScale", "xBias", "floorYScale", "zScale", "yBias"):
            if not _finite(native.get(key)):
                raise ProjectionRecoveryError(f"live projection affine constant invalid: {key}")
        if abs(float(native["worldXScale"])) < 0.05 or abs(float(native["floorYScale"])) < 0.05:
            raise ProjectionRecoveryError("live projection affine transform degenerate")

        envelope = p.get("validationEnvelope")
        if not isinstance(envelope, dict):
            raise ProjectionRecoveryError("live projection validation envelope missing")
        world_x = _range_pair(envelope.get("worldX"), "worldX")
        world_y = _range_pair(envelope.get("worldY"), "worldY")
        world_z = _range_pair(envelope.get("worldZ"), "worldZ")
        camera_raw = _range_pair(envelope.get("cameraRaw"), "cameraRaw")
        if world_x[1] - world_x[0] < 16 or world_y[1] - world_y[0] < 6 or world_z[1] - world_z[0] < 6 or camera_raw[1] - camera_raw[0] < 4:
            raise ProjectionRecoveryError("live projection geometric coverage insufficient")

        residuals = p.get("residuals")
        if not isinstance(residuals, dict):
            raise ProjectionRecoveryError("live projection residual evidence missing")
        train_rms = residuals.get("trainRms"); hold_rms = residuals.get("holdoutRms"); hold_max = residuals.get("holdoutMax")
        if not all(_finite(v) for v in (train_rms, hold_rms, hold_max)) or float(train_rms) > _MAX_TRAIN_RMS or float(hold_rms) > _MAX_HOLDOUT_RMS or float(hold_max) > _MAX_HOLDOUT_ABS:
            raise ProjectionRecoveryError("live projection residual gate failed")

        motion = p.get("motionEnvelope")
        if not isinstance(motion, dict) or any(not _finite(motion.get(k)) or float(motion[k]) <= 0 for k in ("worldXStep", "worldYStep", "worldZStep", "cameraRawStep")):
            raise ProjectionRecoveryError("live projection motion envelope invalid")

        raw_offsets = p.get("enemyHeadOffsetsByType")
        raw_enemy_evidence = p.get("enemyHeadEvidenceByType")
        if not isinstance(raw_offsets, dict) or not raw_offsets or not isinstance(raw_enemy_evidence, dict):
            raise ProjectionRecoveryError("live projection has no visually derived enemy head authority")
        enemy_offsets: dict[str, float] = {}
        enemy_evidence: dict[str, Any] = {}
        for key, value in raw_offsets.items():
            try:
                type_id = int(key)
            except Exception as exc:
                raise ProjectionRecoveryError("enemy type key invalid") from exc
            if str(type_id) != str(key) or not 0 <= type_id < 47 or not _finite(value):
                raise ProjectionRecoveryError("enemy head offset invalid")
            ev = raw_enemy_evidence.get(key)
            if not isinstance(ev, dict) or not isinstance(ev.get("sampleCount"), int) or ev["sampleCount"] < _MIN_ENEMY_SAMPLES or not _finite(ev.get("mad")) or float(ev["mad"]) > _MAX_ENEMY_MAD or not isinstance(ev.get("lifecycleGeneration"), int) or ev["lifecycleGeneration"] < 1:
                raise ProjectionRecoveryError("enemy head visual evidence invalid")
            enemy_offsets[key] = float(value)
            enemy_evidence[key] = json.loads(json.dumps(ev))

        proof_digest = hashlib.sha256(_canonical_bytes(result)).hexdigest()
        proof_id = "live-v2-" + proof_digest[:24]
        authority_hash = hashlib.sha256(authority_key.encode("utf-8")).hexdigest()
        authority_binding = json.loads(json.dumps(binding))
        authority_binding["launcherAuthorityKeySha256"] = authority_hash
        common = {
            "proofId": proof_id,
            "source": "package-selected vision-assisted live affine proof v2",
            "nativeWidth": 384,
            "nativeHeight": 224,
            "cameraAddress": camera_address,
            "cameraSign": int(camera["sign"]),
            "cameraScale": float(camera["scale"]),
            "worldXScale": float(native["worldXScale"]),
            "xBias": float(native["xBias"]),
            "floorYScale": float(native["floorYScale"]),
            "zScale": float(native["zScale"]),
            "yBias": float(native["yBias"]),
            "validationEnvelope": json.loads(json.dumps(envelope)),
            "motionEnvelope": json.loads(json.dumps(motion)),
            "proofResiduals": json.loads(json.dumps(residuals)),
            "authorityBinding": authority_binding,
        }
        player_profile = {
            "schema": "wof-alpha-player-head-projection-v1",
            "status": "PROVED",
            "activation": "LIVE_PROCESS_BOUND_OWNER_PROOF_V2",
            "projectionKind": "world-camera-floor-z-affine-v1",
            "projectionVersion": "live-v2-" + proof_digest[:16],
            **common,
            "headClearanceNative": 0,
            "validationBounds": {"minX": 0, "maxX": 384, "minY": 0, "maxY": 224},
            "safety": {"failClosed": True, "fixedHudFallback": True, "guessedConstants": False},
        }
        enemy_profile = {
            "schema": "wof-alpha-enemy-head-projection-v1",
            "verdict": "IMPLEMENTATION_READY",
            "projectionKind": "world-camera-floor-z-affine-v2",
            "romSha256": WORLD_SHA256,
            "cameraRead": "u16be",
            **common,
            "enemyHeadOffsetsByType": enemy_offsets,
            "enemyHeadEvidenceByType": enemy_evidence,
            "status": "LIVE_PROCESS_BOUND_OWNER_PROOF_V2",
        }
        accepted = json.loads(json.dumps(result))
        accepted["proofId"] = proof_id
        accepted["proofDigestSha256"] = proof_digest
        accepted["worldSha256"] = WORLD_SHA256
        accepted["launcherAuthorityKeySha256"] = authority_hash
        accepted["derivedProfiles"] = {"player": player_profile, "enemy": enemy_profile}
        accepted["authorityPersistence"] = "CURRENT_ACCEPTED_RUNTIME_AUTHORITY_ONLY"
        return {"player": player_profile, "enemy": enemy_profile}, accepted

    def stop_runtime(self, client: CdpClient | None = None, *, preserve_state: bool = False) -> None:
        if client and self._worker_id:
            try:
                self._eval(client, self._worker_id, "try{self.WOFOWNERPROJECTION?.stop?.();true}catch(_){false}")
            except Exception:
                pass
        if client and self._page_id:
            try:
                self._eval(client, self._page_id, "try{window.WOFOWNERPROJECTION?.stop?.();true}catch(_){false}")
            except Exception:
                pass
        self._authority_key = None
        self._page_id = None
        self._worker_id = None
        if not preserve_state and self._profiles is None:
            self._state = "UNPROVED"
            self._error = None
