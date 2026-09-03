from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
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
    last_accepted_authority: dict[str, Any] | None = None
    last_alpha_failure: dict[str, Any] | None = None
    last_calibration_progress: dict[str, Any] | None = None
    significant_events: list[dict[str, Any]] = field(default_factory=list)
    last_update_utc: str = field(default_factory=_utc_now)

    def snapshot(self) -> dict[str, Any]:
        return asdict(self)


class StatusStore:
    EVENT_LIMIT = 96
    CAMERA_EVENT_SEEN_LIMIT = 256

    def __init__(self) -> None:
        self._lock = RLock()
        self._status = LauncherStatus()
        self._last_event_signature: str | None = None
        self._seen_camera_event_ids: list[str] = []
        self._seen_camera_event_set: set[str] = set()

    def get(self) -> LauncherStatus:
        with self._lock:
            return LauncherStatus(**self._status.snapshot())

    @staticmethod
    def _event_signature(kind: str, payload: dict[str, Any]) -> str:
        value = {k: v for k, v in payload.items() if k != "atUtc"}
        return kind + "|" + json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)

    def _append_event_locked(self, kind: str, payload: dict[str, Any]) -> None:
        event = {"kind": kind, "atUtc": _utc_now(), **payload}
        sig = self._event_signature(kind, event)
        if sig == self._last_event_signature:
            return
        self._last_event_signature = sig
        self._status.significant_events = [*self._status.significant_events, event][-self.EVENT_LIMIT :]

    def _append_camera_events_locked(self, timeline: Any) -> None:
        if not isinstance(timeline, list):
            return
        for raw in timeline[-64:]:
            if not isinstance(raw, dict):
                continue
            event_id = raw.get("eventId")
            kind = raw.get("kind")
            if not isinstance(event_id, str) or not event_id or not isinstance(kind, str) or not kind:
                continue
            if event_id in self._seen_camera_event_set:
                continue
            self._seen_camera_event_set.add(event_id)
            self._seen_camera_event_ids.append(event_id)
            if len(self._seen_camera_event_ids) > self.CAMERA_EVENT_SEEN_LIMIT:
                stale = self._seen_camera_event_ids.pop(0)
                self._seen_camera_event_set.discard(stale)
            payload = {k: v for k, v in raw.items() if k not in {"eventId", "kind"}}
            self._append_event_locked("camera-authority-" + kind.lower().replace("_", "-"), {"cameraEventId": event_id, **payload})

    @staticmethod
    def _calibration_progress(alpha_status: dict[str, Any] | None) -> dict[str, Any] | None:
        if not isinstance(alpha_status, dict):
            return None
        recovery = alpha_status.get("projectionRecovery")
        if not isinstance(recovery, dict):
            return None
        ui = recovery.get("ui") if isinstance(recovery.get("ui"), dict) else {}
        quality = ui.get("cameraQuality") if isinstance(ui.get("cameraQuality"), dict) else {}
        raw_quality = ui.get("cameraRawQuality") if isinstance(ui.get("cameraRawQuality"), dict) else {}
        sampling = ui.get("sampling") if isinstance(ui.get("sampling"), dict) else {}
        guidance = ui.get("guidance") if isinstance(ui.get("guidance"), dict) else {}
        checklist = ui.get("checklist") if isinstance(ui.get("checklist"), dict) else {}
        authority = ui.get("cameraAuthority") if isinstance(ui.get("cameraAuthority"), dict) else None
        candidate = ui.get("candidateStability") if isinstance(ui.get("candidateStability"), dict) else None
        timeline = ui.get("authorityTimeline") if isinstance(ui.get("authorityTimeline"), list) else []
        fit = ui.get("fit") if isinstance(ui.get("fit"), dict) else None
        tracker = ui.get("tracker") if isinstance(ui.get("tracker"), dict) else None
        suppression = ui.get("suppression") if isinstance(ui.get("suppression"), list) else []
        enemy_types = ui.get("enemyEvidenceTypes") if isinstance(ui.get("enemyEvidenceTypes"), list) else []
        proof_result = recovery.get("proofResult") if isinstance(recovery.get("proofResult"), dict) else None
        samples = ui.get("samples")
        if not isinstance(samples, int):
            samples = quality.get("samples") if isinstance(quality.get("samples"), int) else None
        sequence = ui.get("lastSequence") if isinstance(ui.get("lastSequence"), int) else ui.get("sequence") if isinstance(ui.get("sequence"), int) else None
        progress = {
            "recoveryState": recovery.get("state"), "error": recovery.get("error"), "samples": samples,
            "targetSamples": quality.get("targetSamples"), "remainingSamples": quality.get("remainingSamples"),
            "cameraReady": quality.get("ready") is True or quality.get("ok") is True, "clickReady": quality.get("clickReady") is True,
            "reason": quality.get("reason"), "conditioning": quality.get("conditioning"),
            "stableSamples": quality.get("stableSamples"), "requiredStableSamples": quality.get("requiredStableSamples"),
            "pausedReason": sampling.get("pausedReason"), "retainedSamples": sampling.get("retainedSamples"),
            "continuable": quality.get("continuable") if "continuable" in quality else sampling.get("continuable"),
            "actionZh": guidance.get("actionZh"), "nextCommandZh": guidance.get("nextCommandZh"),
            "workerSessionId": ui.get("workerSessionId"), "snapshotSequence": sequence, "snapshotId": ui.get("snapshotId"),
            "cameraAuthority": authority, "candidateStability": candidate, "cameraRawQuality": raw_quality or None,
            "authorityTimeline": [x for x in timeline[-64:] if isinstance(x, dict)], "lockRejectReason": ui.get("lockRejectReason"),
            "calibrated": ui.get("calibrated") is True, "pendingCalibration": ui.get("pendingCalibration") is True,
            "terminal": ui.get("terminal") is True, "verdict": ui.get("verdict"), "checklist": checklist,
            "fit": fit, "tracker": tracker,
            "enemyEvidenceTypes": list(enemy_types[-47:]),
            "suppression": [x for x in suppression[-32:] if isinstance(x, dict)],
            "proofResult": proof_result,
        }
        return progress if any(v is not None and v != {} and v != [] and v is not False for v in progress.values()) else None

    def _capture_significant_locked(self) -> None:
        s = self._status
        if s.world_921031 and s.wof_page_found and s.worker_found and s.wasm_module_found and s.heap_found:
            authority = {
                "pageTargetId": s.page_target_id, "pageUrl": s.page_url, "workerTargetId": s.worker_target_id, "workerUrl": s.worker_url,
                "wasmModuleKey": s.wasm_module_key, "heapBytes": s.heap_bytes, "worldSha256": s.identity_sha256,
                "identityReason": s.identity_reason, "discoveryPath": s.discovery_path, "runtimeEpoch": s.alpha_runtime_epoch,
                "packageVersion": s.alpha_package_version, "readOnly": s.read_only, "ramWrites": s.ram_writes, "inputInjection": s.input_injection,
            }
            old = dict(s.last_accepted_authority or {})
            s.last_accepted_authority = {"atUtc": _utc_now(), **authority}
            if {k: v for k, v in old.items() if k != "atUtc"} != authority:
                self._append_event_locked("accepted-authority", authority)

        if s.alpha_error and s.world_921031:
            failure = {
                "error": s.alpha_error, "worldSha256": s.identity_sha256,
                "pageTargetId": s.page_target_id, "workerTargetId": s.worker_target_id,
                "packageVersion": s.alpha_package_version or (s.last_accepted_authority or {}).get("packageVersion"),
                "readOnly": s.read_only, "ramWrites": s.ram_writes, "inputInjection": s.input_injection,
            }
            old = dict(s.last_alpha_failure or {})
            s.last_alpha_failure = {"atUtc": _utc_now(), **failure}
            if {k: v for k, v in old.items() if k != "atUtc"} != failure:
                self._append_event_locked("alpha-failure", failure)

        progress = self._calibration_progress(s.alpha_status)
        if progress is not None:
            s.last_calibration_progress = {"atUtc": _utc_now(), **progress}
            self._append_camera_events_locked(progress.get("authorityTimeline"))
            event_progress = dict(progress)
            sample = event_progress.get("samples")
            event_progress["sampleBucket"] = sample if isinstance(sample, int) and sample < 10 else (sample // 10 * 10 if isinstance(sample, int) else None)
            for key in ("samples", "authorityTimeline", "cameraRawQuality", "fit", "tracker", "suppression", "proofResult"):
                event_progress.pop(key, None)
            self._append_event_locked("calibration-progress", event_progress)

        if s.state in {"ERROR", "DISCONNECTED"} and s.last_accepted_authority is not None:
            self._append_event_locked("runtime-ended-or-disconnected", {"launcherState": s.state, "error": s.last_error})

    def update(self, **changes: Any) -> LauncherStatus:
        with self._lock:
            for key, value in changes.items():
                if not hasattr(self._status, key):
                    raise AttributeError(key)
                setattr(self._status, key, value)
            self._status.last_update_utc = _utc_now()
            self._capture_significant_locked()
            return LauncherStatus(**self._status.snapshot())

    def reset_runtime(self, *, error: str | None = None) -> LauncherStatus:
        return self.update(
            browser_connected=False, browser_name=None, browser_endpoint=None, wof_page_found=False, page_target_id=None, page_url=None,
            worker_found=False, worker_target_id=None, worker_url=None, wasm_module_found=False, wasm_module_key=None, heap_found=False, heap_bytes=None,
            world_921031=False, identity_sha256=None, identity_reason=None, discovery_path=None, discovery_diagnostics=None,
            alpha_running=False, alpha_runtime_epoch=None, alpha_package_version=None, alpha_status=None, alpha_error=error,
            state="ERROR" if error else "DISCONNECTED", last_error=error, read_only=True, ram_writes=0, input_injection=False,
        )
