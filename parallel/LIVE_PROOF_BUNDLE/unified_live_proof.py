from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "wof-unified-windows-live-proof-v1"
STOP_CONDITION = "UNIFIED LIVE PROOF READY — ONE OWNER WOF RUN REMAINS"
ADMISSION_MARKERS = (
    "World 921031 已确认 / Discovery V2 / 只读模式",
    "World 921031 已确认 / 只读模式",
)
FATAL_MARKERS = (
    "WOF-052L 采集器没有正常完成",
    "已安全拒绝采集",
)
READINESS = {
    "pylaunch": "FIX READY - one real Windows proof remains",
    "browserFleet": "BROWSER FLEET DISCOVERY V2 READY",
    "recorder": "DISCOVERY V2 repository-ready",
    "longCapture": "READY FOR 10-ROOM LONG CAPTURE",
    "analysis": "repository-ready",
}

# PYLAUNCH and Recorder both normally publish/update at about 1 Hz.
# Keep a few missed polls of tolerance, but never let stale success retain authority.
PYLAUNCH_FRESHNESS_SECONDS = 8.0
RECORDER_FRESHNESS_SECONDS = 8.0
PROCESS_FRESHNESS_SECONDS = 2.0
CLOCK_SKEW_TOLERANCE_SECONDS = 2.0
GENERATION_ADVANCE_WAIT_SECONDS = 5.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def local_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def choose_free_port(start: int = 9423, end: int = 9499) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                pass
    raise RuntimeError("没有可用的本机 Proof CDP 端口（9423..9499）")


def _parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _age_seconds(value: Any, *, now: datetime | None = None) -> float | None:
    parsed = _parse_utc(value)
    if parsed is None:
        return None
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    else:
        current = current.astimezone(timezone.utc)
    return (current - parsed).total_seconds()


def normalize_fleet(manifest: dict[str, Any] | None) -> dict[str, Any]:
    out = {
        "available": False,
        "browser": False,
        "page": False,
        "workerIndicator": False,
        "workerAuthority": "cheap-indicator-only",
        "world921031Authoritative": False,
        "readOnly": None,
        "ramWrites": None,
        "inputInjection": None,
        "windowWorkerReplacement": None,
        "detail": None,
        "instance": None,
    }
    if not manifest:
        return out
    rows = manifest.get("instances")
    row = rows[0] if isinstance(rows, list) and rows and isinstance(rows[0], dict) else {}
    st = row.get("status") if isinstance(row.get("status"), dict) else {}
    out.update({
        "available": bool(row),
        "browser": st.get("browser") == "OK",
        "page": st.get("page") == "OK",
        "workerIndicator": st.get("worker") == "OK",
        "workerAuthority": manifest.get("workerStatusAuthority"),
        "world921031Authoritative": bool(manifest.get("world921031IdentityAuthoritative")),
        "readOnly": manifest.get("readOnly"),
        "ramWrites": manifest.get("ramWrites"),
        "inputInjection": manifest.get("inputInjection"),
        "windowWorkerReplacement": manifest.get("windowWorkerReplacement"),
        "detail": st.get("detail") or st.get("error"),
        "instance": {
            "id": row.get("id"), "host": row.get("host"), "port": row.get("port"),
            "profileDir": row.get("profileDir"), "pid": row.get("pid"),
            "workerDiscovery": st.get("workerDiscovery"),
            "relatedTopologyCount": st.get("relatedTopologyCount"),
        } if row else None,
    })
    return out


def normalize_pylaunch(
    proof: dict[str, Any] | None,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    out = {
        "available": False,
        # automatedPass is retained as historical/diagnostic positive evidence.
        "automatedPass": False,
        # currentAutomatedPass is the only success authority used by readiness.
        "currentAutomatedPass": False,
        "browser": False,
        "page": False,
        "worker": False,
        "wasmHeap": False,
        "world921031": False,
        "readOnly": None,
        "ramWrites": None,
        "inputInjection": None,
        "worldSha256": None,
        "identityReason": None,
        "discoveryPath": None,
        "lastError": None,
        "targetTopology": None,
        "lastUpdateUtc": None,
        "freshnessKnown": False,
        "fresh": False,
        "ageSeconds": None,
        "freshnessLimitSeconds": PYLAUNCH_FRESHNESS_SECONDS,
        "freshnessReason": "proof unavailable",
        "authorityGeneration": None,
    }
    if not proof:
        return out

    c = proof.get("checks") if isinstance(proof.get("checks"), dict) else {}
    raw_pass = proof.get("automatedResult") == "PASS"
    last_update = proof.get("lastUpdateUtc")
    age = _age_seconds(last_update, now=now)
    freshness_known = age is not None
    fresh = bool(
        freshness_known
        and age is not None
        and -CLOCK_SKEW_TOLERANCE_SECONDS <= age <= PYLAUNCH_FRESHNESS_SECONDS
    )
    if not freshness_known:
        freshness_reason = "lastUpdateUtc 缺失或格式错误"
    elif age is not None and age < -CLOCK_SKEW_TOLERANCE_SECONDS:
        freshness_reason = "lastUpdateUtc 位于不可接受的未来时间"
    elif age is not None and age > PYLAUNCH_FRESHNESS_SECONDS:
        freshness_reason = "PYLAUNCH 当前成功证据已过期"
    else:
        freshness_reason = "current"

    out.update({
        "available": True,
        "automatedPass": raw_pass,
        "currentAutomatedPass": bool(raw_pass and fresh),
        "browser": c.get("Browser") == "OK",
        "page": c.get("WOF page") == "OK",
        "worker": c.get("Worker") == "OK",
        "wasmHeap": c.get("WASM / heap") == "OK",
        "world921031": c.get("World 921031") == "OK",
        "readOnly": proof.get("readOnly"),
        "ramWrites": proof.get("ramWrites"),
        "inputInjection": proof.get("inputInjection"),
        "worldSha256": proof.get("worldSha256"),
        "identityReason": proof.get("identityReason"),
        "discoveryPath": proof.get("discoveryPath"),
        "lastError": proof.get("lastError"),
        "targetTopology": proof.get("targetTopology"),
        "lastUpdateUtc": last_update,
        "freshnessKnown": freshness_known,
        "fresh": fresh,
        "ageSeconds": round(age, 3) if age is not None else None,
        "freshnessReason": freshness_reason,
        "authorityGeneration": last_update if freshness_known else None,
    })
    return out


def _trusted_fleet_supervisor_heartbeat(text: str) -> bool:
    """Match only the exact periodic status emitted by FleetSupervisor.run()."""
    prefix = "Fleet entries "
    middle = " | Recorder workers "
    suffix = " | READ ONLY / RAM writes 0"
    if not text.startswith(prefix) or not text.endswith(suffix):
        return False
    body = text[len(prefix):-len(suffix)]
    parts = body.split(middle)
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return False
    entries, workers = int(parts[0]), int(parts[1])
    return entries >= 1 and workers >= 1


@dataclass
class RecorderEvidence:
    # Current admission authority. A fatal event explicitly revokes these fields.
    admitted: bool = False
    admission_line: str | None = None
    fatal: bool = False
    fatal_line: str | None = None
    generation: int = 0
    admission_generation: int | None = None
    fatal_generation: int | None = None

    # Generic child stdout is diagnostic only. It must never renew authority.
    output_generation: int = 0
    admission_output_generation: int | None = None
    last_output_utc: str | None = None
    _last_diagnostic_output_monotonic: float | None = field(default=None, repr=False)

    # Trusted authority heartbeat/admission generation. Keep the historical
    # _last_output_monotonic field name as the internal authority freshness
    # clock so existing repository fixtures that explicitly age it stay valid.
    authority_generation: int = 0
    admission_authority_generation: int | None = None
    last_authority_utc: str | None = None
    last_authority_kind: str | None = None
    last_heartbeat_line: str | None = None
    _last_output_monotonic: float | None = field(default=None, repr=False)

    # Historical evidence is retained for diagnostics but never satisfies readiness.
    ever_admitted: bool = False
    last_admission_line: str | None = None
    ever_fatal: bool = False
    last_fatal_line: str | None = None
    lines: list[str] = field(default_factory=list)

    def _advance_authority(self, kind: str, line: str) -> None:
        self.authority_generation += 1
        self.last_authority_utc = utc_now()
        self.last_authority_kind = kind
        self._last_output_monotonic = time.monotonic()
        if kind == "supervisor-heartbeat":
            self.last_heartbeat_line = line

    @property
    def current_fresh(self) -> bool:
        if self._last_output_monotonic is None:
            return False
        age = max(0.0, time.monotonic() - self._last_output_monotonic)
        return age <= RECORDER_FRESHNESS_SECONDS

    @property
    def output_age_seconds(self) -> float | None:
        if self._last_diagnostic_output_monotonic is None:
            return None
        return round(max(0.0, time.monotonic() - self._last_diagnostic_output_monotonic), 3)

    @property
    def authority_age_seconds(self) -> float | None:
        if self._last_output_monotonic is None:
            return None
        return round(max(0.0, time.monotonic() - self._last_output_monotonic), 3)

    @property
    def current_healthy(self) -> bool:
        return self.admitted and not self.fatal and self.current_fresh

    @property
    def current_health(self) -> str:
        if self.fatal:
            return "FATAL"
        if self.admitted and not self.current_fresh:
            return "STALE"
        if self.admitted:
            return "HEALTHY"
        return "WAITING"

    def feed(self, line: str) -> None:
        text = line.strip()
        if not text:
            return

        # Every non-empty fragment remains available as diagnostics, but this
        # generic path deliberately does not touch authority freshness.
        self.output_generation += 1
        self.last_output_utc = utc_now()
        self._last_diagnostic_output_monotonic = time.monotonic()
        self.lines.append(text)
        self.lines[:] = self.lines[-120:]

        # Revocation wins even if malformed text happens to contain a positive marker.
        if any(mark in text for mark in FATAL_MARKERS):
            self.generation += 1
            self.fatal = True
            self.fatal_line = text
            self.fatal_generation = self.generation
            self.admitted = False
            self.admission_line = None
            self.admission_generation = None
            self.admission_output_generation = None
            self.admission_authority_generation = None
            self.ever_fatal = True
            self.last_fatal_line = text
            return

        if any(mark in text for mark in ADMISSION_MARKERS):
            self.generation += 1
            self.admitted = True
            self.admission_line = text
            self.admission_generation = self.generation
            self.admission_output_generation = self.output_generation
            self.fatal = False
            self.fatal_line = None
            self.ever_admitted = True
            self.last_admission_line = text
            self._advance_authority("admission", text)
            self.admission_authority_generation = self.authority_generation
            return

        # The only non-admission freshness renewal is the exact FleetSupervisor
        # periodic status line from fleet_recorder.py, and only while an existing
        # admission is still the current, non-revoked identity authority.
        if self.admitted and not self.fatal and _trusted_fleet_supervisor_heartbeat(text):
            self._advance_authority("supervisor-heartbeat", text)


def _valid_exit_code(value: Any) -> bool:
    return value is None or (isinstance(value, int) and not isinstance(value, bool))


def normalize_process_health(process_state: dict[str, Any] | None) -> dict[str, Any]:
    required_fields = (
        "observedAtUtc",
        "observationGeneration",
        "launcherRequired",
        "recorderRequired",
        "launcherLive",
        "recorderLive",
        "launcherExitCode",
        "recorderExitCode",
    )
    state = dict(process_state) if isinstance(process_state, dict) else {}
    missing = [name for name in required_fields if name not in state]
    malformed: list[str] = []

    if process_state is None:
        malformed.append("process mapping unavailable")
    elif not isinstance(process_state, dict):
        malformed.append("process mapping is not an object")

    launcher_required = state.get("launcherRequired")
    recorder_required = state.get("recorderRequired")
    launcher_live = state.get("launcherLive")
    recorder_live = state.get("recorderLive")
    launcher_exit = state.get("launcherExitCode")
    recorder_exit = state.get("recorderExitCode")
    generation = state.get("observationGeneration")
    observed = state.get("observedAtUtc")

    for name, value in (
        ("launcherRequired", launcher_required),
        ("recorderRequired", recorder_required),
        ("launcherLive", launcher_live),
        ("recorderLive", recorder_live),
    ):
        if name in state and not isinstance(value, bool):
            malformed.append(f"{name} must be boolean")

    if "launcherExitCode" in state and not _valid_exit_code(launcher_exit):
        malformed.append("launcherExitCode must be integer or null")
    if "recorderExitCode" in state and not _valid_exit_code(recorder_exit):
        malformed.append("recorderExitCode must be integer or null")
    if "observationGeneration" in state and (
        not isinstance(generation, int) or isinstance(generation, bool) or generation <= 0
    ):
        malformed.append("observationGeneration must be positive integer")

    age = _age_seconds(observed)
    if "observedAtUtc" in state and age is None:
        malformed.append("observedAtUtc must be timezone-aware ISO-8601")

    # Explicit live facts and exit facts must agree.
    if isinstance(launcher_live, bool) and _valid_exit_code(launcher_exit):
        if launcher_live and launcher_exit is not None:
            malformed.append("launcherLive conflicts with launcherExitCode")
        if launcher_required is True and launcher_live is False and launcher_exit is None:
            malformed.append("launcher exit code missing for non-live required launcher")
    if isinstance(recorder_live, bool) and _valid_exit_code(recorder_exit):
        if recorder_live and recorder_exit is not None:
            malformed.append("recorderLive conflicts with recorderExitCode")
        if recorder_required is True and recorder_live is False and recorder_exit is None:
            malformed.append("recorder exit code missing for non-live required recorder")

    health_known = bool(not missing and not malformed)
    current = bool(
        health_known
        and age is not None
        and -CLOCK_SKEW_TOLERANCE_SECONDS <= age <= PROCESS_FRESHNESS_SECONDS
    )
    if not health_known:
        freshness_reason = "process health mapping 不完整或格式错误"
    elif age is not None and age < -CLOCK_SKEW_TOLERANCE_SECONDS:
        freshness_reason = "process observation 位于不可接受的未来时间"
    elif age is not None and age > PROCESS_FRESHNESS_SECONDS:
        freshness_reason = "process observation 已过期"
    else:
        freshness_reason = "current"

    healthy = bool(
        health_known
        and current
        and launcher_required is True
        and recorder_required is True
        and launcher_live is True
        and recorder_live is True
    )
    state.update({
        "healthKnown": health_known,
        "current": current,
        "missingFields": missing,
        "malformedReasons": malformed,
        "observedAgeSeconds": round(age, 3) if age is not None else None,
        "freshnessLimitSeconds": PROCESS_FRESHNESS_SECONDS,
        "freshnessReason": freshness_reason,
        "launcherRequired": launcher_required,
        "recorderRequired": recorder_required,
        "launcherLive": launcher_live,
        "recorderLive": recorder_live,
        "launcherExitCode": launcher_exit,
        "recorderExitCode": recorder_exit,
        "healthy": healthy,
    })
    return state


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def current_blockers(
    blockers: list[str],
    recorder: RecorderEvidence,
    process_state: dict[str, Any] | None,
    pylaunch: dict[str, Any] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    effective = list(blockers)
    process = normalize_process_health(process_state)

    if recorder.fatal:
        detail = recorder.fatal_line or recorder.last_fatal_line or "Recorder 当前处于 fatal 状态"
        _append_unique(effective, "Recorder 致命状态：" + detail)
    elif recorder.admitted and not recorder.current_fresh:
        _append_unique(effective, "Recorder 当前成功证据已过期；旧 admission 仅保留用于诊断")

    if process_state is not None and not process.get("healthKnown"):
        _append_unique(effective, "PYLAUNCH/Recorder 子进程健康信息不完整或格式错误")
    elif process.get("healthKnown") and not process.get("current"):
        _append_unique(effective, "PYLAUNCH/Recorder 子进程健康观测已过期")
    elif process.get("healthKnown"):
        positive_child_success = bool(
            (pylaunch and pylaunch.get("automatedPass") is True) or recorder.admitted
        )
        if (
            positive_child_success
            and (
                process.get("launcherRequired") is not True
                or process.get("recorderRequired") is not True
            )
        ):
            _append_unique(effective, "统一验证要求 PYLAUNCH 与 Recorder 两个子进程都必须显式 required")
        if process.get("launcherRequired") is True and process.get("launcherLive") is False:
            _append_unique(effective, f"PYLAUNCH 子进程已退出（code={process.get('launcherExitCode')}）")
        if process.get("recorderRequired") is True and process.get("recorderLive") is False:
            _append_unique(effective, f"Recorder 子进程已退出（code={process.get('recorderExitCode')}）")

    if pylaunch and pylaunch.get("automatedPass") is True and pylaunch.get("fresh") is not True:
        reason = pylaunch.get("freshnessReason") or "PYLAUNCH 当前成功证据 freshness 未知"
        _append_unique(effective, "PYLAUNCH PASS 不能作为当前 authority：" + str(reason))
    return effective, process


def safety_ok(fleet: dict[str, Any], pylaunch: dict[str, Any], recorder: RecorderEvidence) -> bool:
    return bool(
        fleet.get("readOnly") is True and fleet.get("ramWrites") == 0
        and fleet.get("inputInjection") is False and fleet.get("windowWorkerReplacement") is False
        and pylaunch.get("readOnly") is True and pylaunch.get("ramWrites") == 0
        and pylaunch.get("inputInjection") is False and recorder.current_healthy
    )


def automated_ready(
    fleet: dict[str, Any],
    pylaunch: dict[str, Any],
    recorder: RecorderEvidence,
    process_state: dict[str, Any] | None = None,
    blockers: list[str] | None = None,
) -> bool:
    effective_blockers, process = current_blockers(
        list(blockers or []), recorder, process_state, pylaunch
    )
    return bool(
        not effective_blockers and process.get("healthy") is True
        and fleet.get("browser") and fleet.get("page") and fleet.get("workerIndicator")
        and fleet.get("workerAuthority") == "cheap-indicator-only"
        and fleet.get("world921031Authoritative") is False
        and pylaunch.get("currentAutomatedPass") is True
        and pylaunch.get("world921031")
        and recorder.current_healthy
        and safety_ok(fleet, pylaunch, recorder)
    )


def build_status(
    *,
    run_id: str,
    run_dir: Path,
    fleet_manifest: dict[str, Any] | None,
    pylaunch_proof: dict[str, Any] | None,
    recorder: RecorderEvidence,
    playability: str,
    stage: str,
    blockers: list[str],
    process_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    fleet = normalize_fleet(fleet_manifest)
    pylaunch = normalize_pylaunch(pylaunch_proof, now=now)
    effective_blockers, process = current_blockers(blockers, recorder, process_state, pylaunch)
    auto = automated_ready(fleet, pylaunch, recorder, process_state, effective_blockers)
    owner_prompt_eligible = auto and playability == "NOT_READY"
    passed = bool(not effective_blockers and auto and playability == "CONFIRMED")
    result = "BLOCKED" if effective_blockers else ("PASS" if passed else "WAITING")
    summary = (
        "真人短验证通过：已具备 10 房间长采集条件。不会自动开始长采集。"
        if passed else
        "真人短验证已阻断；已保留未受影响分支的正证据和精确 blocker。"
        if effective_blockers else
        "正在等待 WOF / Worker / WASM / World 921031 / Recorder 当前准入。"
    )
    safe = safety_ok(fleet, pylaunch, recorder)
    return {
        "schema": SCHEMA,
        "runId": run_id,
        "updatedAtUtc": utc_now(),
        "stage": stage,
        "repository": {
            "result": "PASS",
            "liveProofClaimed": False,
            "readiness": READINESS,
            "stopCondition": STOP_CONDITION,
        },
        "freshnessPolicy": {
            "pylaunchMaxAgeSeconds": PYLAUNCH_FRESHNESS_SECONDS,
            "recorderAuthorityMaxAgeSeconds": RECORDER_FRESHNESS_SECONDS,
            "recorderOutputMaxAgeSeconds": RECORDER_FRESHNESS_SECONDS,
            "processObservationMaxAgeSeconds": PROCESS_FRESHNESS_SECONDS,
            "generationAdvanceWaitSeconds": GENERATION_ADVANCE_WAIT_SECONDS,
        },
        "live": {
            "result": result,
            "automatedChecksReady": auto,
            "ownerPromptEligible": owner_prompt_eligible,
            "ownerPlayabilityConfirmation": playability,
            "fleetDiscoveryV2": fleet,
            "pylaunchAuthoritativeProof": pylaunch,
            "recorderDiscoveryV2Admission": {
                "admitted": recorder.admitted,
                "evidence": recorder.admission_line,
                "fatal": recorder.fatal,
                "fatalEvidence": recorder.fatal_line,
                "currentHealth": recorder.current_health,
                "currentFresh": recorder.current_fresh,
                "lastAuthorityUtc": recorder.last_authority_utc,
                "authorityAgeSeconds": recorder.authority_age_seconds,
                "authorityGeneration": recorder.authority_generation,
                "admissionAuthorityGeneration": recorder.admission_authority_generation,
                "lastAuthorityKind": recorder.last_authority_kind,
                "lastHeartbeatEvidence": recorder.last_heartbeat_line,
                "lastOutputUtc": recorder.last_output_utc,
                "outputAgeSeconds": recorder.output_age_seconds,
                "outputGeneration": recorder.output_generation,
                "admissionOutputGeneration": recorder.admission_output_generation,
                "freshnessLimitSeconds": RECORDER_FRESHNESS_SECONDS,
                "generation": recorder.generation,
                "admissionGeneration": recorder.admission_generation,
                "fatalGeneration": recorder.fatal_generation,
                "history": {
                    "everAdmitted": recorder.ever_admitted,
                    "lastAdmissionEvidence": recorder.last_admission_line,
                    "everFatal": recorder.ever_fatal,
                    "lastFatalEvidence": recorder.last_fatal_line,
                },
                "recentOutput": recorder.lines[-30:],
            },
            "safety": {
                "pass": safe,
                "readOnly": True if safe else None,
                "ramWrites": 0 if safe else None,
                "inputInjection": False if safe else None,
                "workerReplacement": False,
                "blobWorker": False,
            },
            "processes": process,
            "blockers": effective_blockers,
        },
        "overallResult": result,
        "tenRoomLongCaptureReady": passed,
        "longCaptureAutoStarted": False,
        "ownerSummaryZh": summary,
        "ownerReturn": {
            "json": str(run_dir / "UNIFIED_LIVE_PROOF_STATUS.json"),
            "alternative": "最终中文状态截图",
        },
    }


def authority_generation_snapshot(status: dict[str, Any]) -> dict[str, Any]:
    live = status.get("live") if isinstance(status.get("live"), dict) else {}
    pylaunch = (
        live.get("pylaunchAuthoritativeProof")
        if isinstance(live.get("pylaunchAuthoritativeProof"), dict) else {}
    )
    recorder = (
        live.get("recorderDiscoveryV2Admission")
        if isinstance(live.get("recorderDiscoveryV2Admission"), dict) else {}
    )
    processes = live.get("processes") if isinstance(live.get("processes"), dict) else {}
    return {
        "pylaunch": pylaunch.get("authorityGeneration"),
        "recorder": recorder.get("authorityGeneration"),
        "process": processes.get("observationGeneration"),
    }


def authority_generations_advanced(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> bool:
    before_py = previous.get("pylaunch")
    after_py = current.get("pylaunch")
    before_rec = previous.get("recorder")
    after_rec = current.get("recorder")
    before_proc = previous.get("process")
    after_proc = current.get("process")
    return bool(
        isinstance(before_py, str) and isinstance(after_py, str) and after_py != before_py
        and isinstance(before_rec, int) and not isinstance(before_rec, bool)
        and isinstance(after_rec, int) and not isinstance(after_rec, bool)
        and after_rec > before_rec
        and isinstance(before_proc, int) and not isinstance(before_proc, bool)
        and isinstance(after_proc, int) and not isinstance(after_proc, bool)
        and after_proc > before_proc
    )


def reader(
    proc: subprocess.Popen[str],
    prefix: str,
    evidence: RecorderEvidence | None,
    q: "queue.Queue[tuple[str, str]]",
) -> None:
    if proc.stdout is None:
        return

    # Recorder supervisor heartbeat uses '\r' + flush without '\n'. Read by
    # character so that heartbeat is visible to freshness logic instead of
    # being trapped indefinitely by line iteration.
    buf: list[str] = []

    def emit() -> None:
        if not buf:
            return
        line = "".join(buf)
        buf.clear()
        if evidence is not None:
            evidence.feed(line)
        q.put((prefix, line))

    while True:
        ch = proc.stdout.read(1)
        if not ch:
            break
        if ch in {"\r", "\n"}:
            emit()
            continue
        buf.append(ch)
        if len(buf) >= 16384:
            emit()
    emit()


def start_child(cmd: list[str], cwd: Path) -> subprocess.Popen[str]:
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0
    return subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        creationflags=flags,
    )


def stop_child(proc: subprocess.Popen[str] | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        if os.name == "nt" and hasattr(signal, "CTRL_BREAK_EVENT"):
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            proc.wait(timeout=8)
            return
    except Exception:
        pass
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def run_live(root: Path) -> int:
    fleet_dir = root / "parallel" / "BROWSER_FLEET"
    py_dir = root / "parallel" / "PYLAUNCH"
    rec_dir = root / "parallel" / "WOF052L_RECORDER"
    for p in (fleet_dir, py_dir, rec_dir):
        sys.path.insert(0, str(p))
    from fleet_owner_zh_cn import ChineseFleetManager

    local = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("TEMP") or ".")
    base = local / "WOF Future Danger" / "UnifiedLiveProof"
    run_id = f"{local_stamp()}-{uuid.uuid4().hex[:6]}"
    run_dir = base / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    status_path = run_dir / "UNIFIED_LIVE_PROOF_STATUS.json"
    latest = base / "UNIFIED_LIVE_PROOF_STATUS.json"
    manifest = run_dir / "fleet" / "instances.json"
    settings = run_dir / "fleet" / "settings.json"
    profiles = run_dir / "fleet" / "Profiles"
    pyproof = run_dir / "PYLAUNCH_WINDOWS_PROOF_STATUS.json"
    rec_out = run_dir / "recorder"
    evidence = RecorderEvidence()
    blockers: list[str] = []
    q: "queue.Queue[tuple[str, str]]" = queue.Queue()
    playability = "NOT_READY"
    pyproc: subprocess.Popen[str] | None = None
    recproc: subprocess.Popen[str] | None = None
    terminal: dict[str, Any] | None = None
    process_generation = 0

    class ProofFleet(ChineseFleetManager):
        def _profile_for(self, instance_id: int) -> Path:
            return profiles / f"Proof_{instance_id:02d}"

    mgr = ProofFleet(settings_path=settings, manifest_path=manifest, poll_seconds=1.0)
    mgr.settings.base_port = choose_free_port()
    mgr.settings.browser = "auto"
    mgr.settings.game_url = None
    mgr.settings.save(settings)

    def process_snapshot() -> dict[str, Any]:
        nonlocal process_generation
        process_generation += 1
        launcher_exit = pyproc.poll() if pyproc is not None else None
        recorder_exit = recproc.poll() if recproc is not None else None
        return {
            "observedAtUtc": utc_now(),
            "observationGeneration": process_generation,
            "launcherRequired": pyproc is not None,
            "recorderRequired": recproc is not None,
            "launcherLive": bool(pyproc is not None and launcher_exit is None),
            "recorderLive": bool(recproc is not None and recorder_exit is None),
            "launcherExitCode": launcher_exit,
            "recorderExitCode": recorder_exit,
            "fleetManifest": str(manifest),
        }

    def observe_failures() -> None:
        if pyproc is not None and pyproc.poll() is not None:
            _append_unique(blockers, f"PYLAUNCH 子进程已退出（code={pyproc.returncode}）")
        if recproc is not None and recproc.poll() is not None:
            _append_unique(blockers, f"Recorder 子进程已退出（code={recproc.returncode}）")
        if evidence.fatal:
            detail = evidence.fatal_line or evidence.last_fatal_line or "未知 fatal"
            _append_unique(blockers, "Recorder 致命状态：" + detail)

    def drain_queue() -> None:
        while True:
            try:
                prefix, line = q.get_nowait()
            except queue.Empty:
                break
            if any(x in line for x in ("已确认", "失败", "ERROR", "拒绝")):
                print(f"[{prefix}] {line}")

    def persist(stage: str, *, playability_override: str | None = None) -> dict[str, Any]:
        value = build_status(
            run_id=run_id,
            run_dir=run_dir,
            fleet_manifest=load_json(manifest),
            pylaunch_proof=load_json(pyproof),
            recorder=evidence,
            playability=playability if playability_override is None else playability_override,
            stage=stage,
            blockers=list(blockers),
            process_state=process_snapshot(),
        )
        atomic_write_json(status_path, value)
        try:
            shutil.copy2(status_path, latest)
        except OSError:
            pass
        return value

    def retain_dynamic_blockers(value: dict[str, Any]) -> None:
        live = value.get("live") if isinstance(value.get("live"), dict) else {}
        for item in live.get("blockers") or []:
            if isinstance(item, str):
                _append_unique(blockers, item)

    def wait_for_new_current_generation(
        previous: dict[str, Any],
        stage: str,
    ) -> tuple[dict[str, Any], bool]:
        deadline = time.monotonic() + GENERATION_ADVANCE_WAIT_SECONDS
        latest_value = persist(stage, playability_override="NOT_READY")
        while True:
            drain_queue()
            observe_failures()
            latest_value = persist(stage, playability_override="NOT_READY")
            if latest_value["live"]["blockers"] or not latest_value["live"]["automatedChecksReady"]:
                retain_dynamic_blockers(latest_value)
                return latest_value, False
            if authority_generations_advanced(
                previous, authority_generation_snapshot(latest_value)
            ):
                return latest_value, True
            if time.monotonic() >= deadline:
                _append_unique(
                    blockers,
                    "PYLAUNCH/Recorder 当前成功证据未在 freshness gate 内产生新代次；按 fail-closed 阻断",
                )
                return latest_value, False
            time.sleep(0.2)

    print("\n============================================================")
    print("  WOF 统一 Windows 真人短验证")
    print("============================================================")
    print("只读模式：开启 | RAM writes: 0 | input injection: none")
    print("不需要 DevTools / Worker Console / 粘贴 JavaScript。")
    persist("STARTING")
    try:
        print("正在启动 1 个专用 WOF 浏览器房间...")
        mgr.start(1)
        mgr.print_status()
        persist("BROWSER_STARTED")
        pyproc = start_child(
            [
                sys.executable, "-u", str(py_dir / "launcher.py"),
                "--fleet-instance", "1", "--fleet-manifest", str(manifest),
                "--no-tray", "--proof-json", str(pyproof),
            ],
            py_dir,
        )
        recproc = start_child(
            [
                sys.executable, "-u", str(rec_dir / "owner_v2_zh_cn.py"),
                "--output-dir", str(rec_out), "--fleet-manifest", str(manifest),
                "--no-launch-browser",
            ],
            rec_dir,
        )
        threading.Thread(
            target=reader, args=(pyproc, "PYLAUNCH", None, q), daemon=True
        ).start()
        threading.Thread(
            target=reader, args=(recproc, "RECORDER", evidence, q), daemon=True
        ).start()
        print("请在专用浏览器中正常进入一个 WOF 房间，其他检查自动完成。")
        last = 0.0

        while True:
            drain_queue()
            observe_failures()

            if time.monotonic() - last >= 2:
                f = normalize_fleet(load_json(manifest))
                p = normalize_pylaunch(load_json(pyproof))
                print(
                    "\rBrowser:%s | Page:%s | Fleet Worker:%s | World:%s | Recorder:%s      "
                    % (
                        "OK" if f["browser"] else "WAIT",
                        "OK" if f["page"] else "WAIT",
                        "OK" if f["workerIndicator"] else "WAIT",
                        "OK" if p["world921031"] and p["fresh"] else "WAIT",
                        "OK" if evidence.current_healthy else "WAIT",
                    ),
                    end="",
                    flush=True,
                )
                last = time.monotonic()

            value = persist("LIVE_WAITING")
            if value["live"]["ownerPromptEligible"]:
                # A stale-but-still-within-age-window PASS is not enough.
                # Require a newer PYLAUNCH proof generation and a newer trusted
                # Recorder authority heartbeat before the Owner prompt is reachable.
                before_prompt = authority_generation_snapshot(value)
                gate, advanced = wait_for_new_current_generation(
                    before_prompt, "PLAYABILITY_GATE"
                )
                if not advanced or not gate["live"]["ownerPromptEligible"]:
                    retain_dynamic_blockers(gate)
                    terminal = persist("BLOCKED")
                    break

                print("\n\n自动只读验证当前全部通过。")
                ans = input("当前 WOF 房间仍能正常运行？正常输入 Y，异常输入 N：").strip().lower()
                playability = "CONFIRMED" if ans in {"y", "yes", "是", "正常"} else "FAILED"
                if playability == "FAILED":
                    _append_unique(blockers, "Owner 确认游戏运行异常")
                    terminal = persist("BLOCKED")
                    break

                # Require another new generation after the Owner answer. This
                # closes the live-but-hung window where a recently written PASS
                # might still be under the age threshold.
                after_prompt_baseline = authority_generation_snapshot(gate)
                recheck_wait, advanced = wait_for_new_current_generation(
                    after_prompt_baseline, "FINAL_FRESHNESS_GATE"
                )
                if not advanced:
                    retain_dynamic_blockers(recheck_wait)
                    terminal = persist("BLOCKED")
                    break

                observe_failures()
                recheck = persist("FINAL_RECHECK")
                if not recheck["live"]["automatedChecksReady"]:
                    retain_dynamic_blockers(recheck)
                    _append_unique(blockers, "Owner 确认期间自动检查不再保持当前 PASS")
                terminal = persist("COMPLETE" if not blockers else "BLOCKED")
                break

            if value["live"]["blockers"]:
                retain_dynamic_blockers(value)
                terminal = persist("BLOCKED")
                break
            time.sleep(0.5)

    except KeyboardInterrupt:
        _append_unique(blockers, "Owner 中断了真人短验证")
        terminal = persist("INTERRUPTED")
    except Exception as exc:
        _append_unique(blockers, f"统一真人短验证错误：{exc}")
        terminal = persist("BLOCKED")
    finally:
        stop_child(recproc)
        stop_child(pyproc)
        try:
            mgr._stop.set()
            mgr.stop_all()
        except Exception:
            pass

    final = terminal or persist("BLOCKED")
    # Do not recompute from the post-cleanup Fleet manifest; preserve terminal evidence.
    atomic_write_json(status_path, final)
    try:
        shutil.copy2(status_path, latest)
    except OSError:
        pass
    print("\n============================================================")
    print("PASS - 已具备 10 房间长采集条件" if final["overallResult"] == "PASS" else "真人短验证未通过")
    print("自动开始长采集：否")
    print("JSON：" + str(status_path))
    print("============================================================")
    try:
        if os.name == "nt":
            os.startfile(run_dir)  # type: ignore[attr-defined]
    except Exception:
        pass
    return 0 if final["overallResult"] == "PASS" else 2


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WOF 统一 Windows 真人短验证")
    p.add_argument("--project-root", required=True)
    return p.parse_args()


def main() -> int:
    root = Path(parse_args().project_root).expanduser().resolve()
    required = [
        root / "parallel" / "PYLAUNCH" / "launcher.py",
        root / "parallel" / "BROWSER_FLEET" / "fleet_owner_zh_cn.py",
        root / "parallel" / "WOF052L_RECORDER" / "owner_v2_zh_cn.py",
    ]
    if any(not p.is_file() for p in required):
        print("缺少统一真人短验证所需的 WOF 工具文件")
        return 3
    return run_live(root)


if __name__ == "__main__":
    raise SystemExit(main())
