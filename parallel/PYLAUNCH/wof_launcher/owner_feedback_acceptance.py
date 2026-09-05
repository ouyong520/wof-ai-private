from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "wof-alpha-owner-feedback-v1"
OUTPUT_NAME = "LATEST_ALPHA_FEEDBACK.txt"
FIXED_STATUS_NAME = "ALPHA_FIXED_DRAW_STATUS.json"
FIXED_MODE = "fixed-draw-first-gate"
EXPECTED_ORIGIN = "git@wof-alpha-github:ouyong520/wof-ai-private.git"
MAX_FIXED_STATUS_AGE_SECONDS = 60.0
MAX_UPDATE_FETCH_AGE_SECONDS = 30.0
NATIVE = (384, 224, 192, 112, "TEST")

ROUTING_STATES = {
    "BOOTSTRAP_NOT_READY",
    "UPDATE_CHANNEL_NOT_READY",
    "LIVE_MODE_NOT_FIXED_DRAW",
    "RUNTIME_NOT_STARTED",
    "HUD_INJECTION_MISSING",
    "GAME_CANVAS_CONTEXT_MISSING",
    "DRAW_HOOK_NOT_FIRING",
    "DRAWING_BUFFER_INVALID",
    "DRAW_FAILED",
    "MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL",
    "READY_FOR_OWNER_FIXED_TEST",
    "FEEDBACK_INPUT_MALFORMED",
}
FAILURE_STATES = {
    "HUD_INJECTION_MISSING",
    "GAME_CANVAS_CONTEXT_MISSING",
    "DRAW_HOOK_NOT_FIRING",
    "DRAWING_BUFFER_INVALID",
    "DRAW_FAILED",
}
READY_STATES = {"READY", "ARMED", "READY_FOR_OWNER_FIXED_TEST"}
_SHA = re.compile(r"^[0-9a-fA-F]{7,64}$")


@dataclass(frozen=True)
class SourceSnapshot:
    data: Mapping[str, Any] | None
    path: Path
    age_seconds: float | None = None
    error: str | None = None


def _value(data: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return None


def _bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
        return value.strip().lower() == "true"
    return None


def _uint(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        out = int(value)
    except (TypeError, ValueError):
        return None
    return out if out >= 0 else None


def _release_sha(data: Mapping[str, Any]) -> str | None:
    raw = _value(data, "currentReleaseSha", "alphaLiveCommit", "currentSha", "releaseSha", "acceptanceSha")
    if raw is None:
        return None
    text = str(raw).strip()
    return text.lower() if _SHA.fullmatch(text) else None


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
    path = Path(text.split(":", 1)[1].strip())
    return path if path.is_absolute() else (root / path).resolve()


def _common_git_dir(git_dir: Path) -> Path:
    try:
        raw = (git_dir / "commondir").read_text(encoding="utf-8").strip()
    except OSError:
        return git_dir
    path = Path(raw)
    return path if path.is_absolute() else (git_dir / path).resolve()


def _head_sha(root: Path) -> str | None:
    git_dir = _git_dir(root)
    if git_dir is None:
        return None
    common = _common_git_dir(git_dir)
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if len(head) == 40 and _SHA.fullmatch(head):
        return head.lower()
    if not head.startswith("ref: "):
        return None
    ref = head[5:].strip()
    for base in (git_dir, common):
        try:
            value = (base / ref).read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if len(value) == 40 and _SHA.fullmatch(value):
            return value.lower()
    try:
        packed = (common / "packed-refs").read_text(encoding="utf-8").splitlines()
    except OSError:
        packed = []
    for line in packed:
        if line.startswith(("#", "^")):
            continue
        sha, _, name = line.partition(" ")
        if name == ref and len(sha) == 40 and _SHA.fullmatch(sha):
            return sha.lower()
    return None


def _repo_readiness(root: Path, launcher: Mapping[str, Any]) -> tuple[bool, bool]:
    git_dir = _git_dir(root)
    if git_dir is None:
        return False, False
    common = _common_git_dir(git_dir)
    release = _release_sha(launcher)
    managed = release is not None and _head_sha(root) == release
    try:
        origin_ok = EXPECTED_ORIGIN in (common / "config").read_text(encoding="utf-8")
        fetch_head = common / "FETCH_HEAD"
        fetch_age = max(0.0, datetime.now(timezone.utc).timestamp() - fetch_head.stat().st_mtime)
        alpha_live_seen = "alpha-live" in fetch_head.read_text(encoding="utf-8", errors="replace")
    except OSError:
        origin_ok = False
        fetch_age = float("inf")
        alpha_live_seen = False
    status = str(_value(launcher, "status") or "").strip().upper()
    explicit_bad = status in {"SSH_UPDATE_UNAVAILABLE", "UPDATE_APPLY_FAILED", "RELEASE_REJECTED"}
    update = bool(
        managed
        and origin_ok
        and alpha_live_seen
        and fetch_age <= MAX_UPDATE_FETCH_AGE_SECONDS
        and not explicit_bad
    )
    return managed, update


def _buffer(fixed: Mapping[str, Any]) -> tuple[int | None, int | None]:
    raw = _value(fixed, "drawingBuffer", "drawing_buffer")
    if isinstance(raw, Mapping):
        return _uint(raw.get("width")), _uint(raw.get("height"))
    return _uint(_value(fixed, "drawingBufferWidth")), _uint(_value(fixed, "drawingBufferHeight"))


def _last_error(fixed: Mapping[str, Any]) -> str | None:
    raw = _value(fixed, "lastError", "last_error")
    if raw is None:
        return None
    text = str(raw).strip()
    return None if text in {"", "NONE", "None", "null"} else text


def _fixed_evidence(fixed: Mapping[str, Any]) -> dict[str, Any]:
    dbw, dbh = _buffer(fixed)
    runtime = _bool(_value(fixed, "runtimeReady", "runtime_ready"))
    return {
        "runtimeReady": True if runtime is None else runtime,
        "fixedSmokeState": str(_value(fixed, "fixedSmokeState", "state") or "").strip() or None,
        "hudInjected": _bool(_value(fixed, "hudInjected")),
        "gameCanvasContextPresent": _bool(_value(fixed, "gameCanvasContextPresent")),
        "drawHooked": _bool(_value(fixed, "drawHooked")),
        "callbackCount": _uint(_value(fixed, "callbackCount")),
        "drawCount": _uint(_value(fixed, "drawCount")),
        "drawingBufferWidth": dbw,
        "drawingBufferHeight": dbh,
        "nativeWidth": _uint(_value(fixed, "nativeWidth")),
        "nativeHeight": _uint(_value(fixed, "nativeHeight")),
        "nativeX": _uint(_value(fixed, "nativeX")),
        "nativeY": _uint(_value(fixed, "nativeY")),
        "label": str(_value(fixed, "label") or "").strip() or None,
        "lastError": _last_error(fixed),
        "readOnly": _bool(_value(fixed, "readOnly")),
        "ramWrites": _uint(_value(fixed, "ramWrites")),
        "inputInjection": _bool(_value(fixed, "inputInjection")),
    }


def classify(
    launcher: Mapping[str, Any] | None,
    fixed: Mapping[str, Any] | None,
    *,
    fixed_age_seconds: float | None = 0.0,
    fixed_source_error: str | None = None,
) -> tuple[str, str, dict[str, Any]]:
    evidence: dict[str, Any] = {
        "currentReleaseSha": None,
        "liveMode": None,
        "managedRepoReady": None,
        "updateChannelReady": None,
        "runtimeReady": False,
        "fixedSmokeState": None,
        "hudInjected": None,
        "gameCanvasContextPresent": None,
        "drawHooked": None,
        "callbackCount": None,
        "drawCount": None,
        "drawingBufferWidth": None,
        "drawingBufferHeight": None,
        "nativeWidth": None,
        "nativeHeight": None,
        "nativeX": None,
        "nativeY": None,
        "label": None,
        "lastError": None,
        "machineDrawProof": False,
    }
    if not isinstance(launcher, Mapping):
        return "BOOTSTRAP_NOT_READY", "launcher feedback is missing/unreadable", evidence

    release = _release_sha(launcher)
    live_mode = str(_value(launcher, "liveMode", "live_mode") or "").strip() or None
    managed = _bool(_value(launcher, "managedRepoReady"))
    update = _bool(_value(launcher, "updateChannelReady"))
    evidence.update(currentReleaseSha=release, liveMode=live_mode, managedRepoReady=managed, updateChannelReady=update)
    if release is None or managed is not True:
        return "BOOTSTRAP_NOT_READY", "managed release is not explicitly ready", evidence
    if update is not True:
        return "UPDATE_CHANNEL_NOT_READY", "alpha-live fetch heartbeat/update channel is not ready", evidence
    if live_mode != FIXED_MODE:
        return "LIVE_MODE_NOT_FIXED_DRAW", f"liveMode={live_mode or 'missing'}", evidence

    if fixed_source_error or fixed_age_seconds is None or fixed_age_seconds > MAX_FIXED_STATUS_AGE_SECONDS:
        detail = fixed_source_error or "missing/stale fixed status"
        return "RUNTIME_NOT_STARTED", detail, evidence
    if not isinstance(fixed, Mapping):
        return "RUNTIME_NOT_STARTED", "fixed-smoke status is missing/unreadable", evidence

    core = _fixed_evidence(fixed)
    evidence.update({key: core[key] for key in evidence if key in core})
    if core["runtimeReady"] is not True:
        return "RUNTIME_NOT_STARTED", "Alpha runtime did not report ready", evidence
    state = core["fixedSmokeState"]
    if state is None:
        return "FEEDBACK_INPUT_MALFORMED", "fixed-smoke state is missing", evidence
    if state in FAILURE_STATES:
        return state, f"fixed-smoke probe reported {state}", evidence
    if state == "DISABLED":
        return "DRAW_HOOK_NOT_FIRING", "fixed mode selected but fixed smoke is disabled", evidence

    required = (
        "hudInjected", "gameCanvasContextPresent", "drawHooked", "callbackCount", "drawCount",
        "nativeWidth", "nativeHeight", "nativeX", "nativeY", "label", "readOnly", "ramWrites", "inputInjection",
    )
    if any(core[name] is None for name in required):
        return "FEEDBACK_INPUT_MALFORMED", "potentially-green status is missing typed evidence", evidence
    if core["drawingBufferWidth"] is None or core["drawingBufferHeight"] is None:
        return "DRAWING_BUFFER_INVALID", "drawing buffer metadata is missing", evidence
    if core["drawingBufferWidth"] <= 0 or core["drawingBufferHeight"] <= 0:
        return "DRAWING_BUFFER_INVALID", "drawing buffer dimensions are invalid", evidence
    if core["hudInjected"] is not True:
        return "HUD_INJECTION_MISSING", "HUD injection proof is false", evidence
    if core["gameCanvasContextPresent"] is not True:
        return "GAME_CANVAS_CONTEXT_MISSING", "game canvas/context proof is false", evidence
    if core["drawHooked"] is not True:
        return "DRAW_HOOK_NOT_FIRING", "draw hook proof is false", evidence
    if core["lastError"] is not None:
        return "DRAW_FAILED", "lastError is present", evidence

    native_ok = (
        core["nativeWidth"], core["nativeHeight"], core["nativeX"], core["nativeY"], core["label"]
    ) == NATIVE
    safety_ok = core["readOnly"] is True and core["ramWrites"] == 0 and core["inputInjection"] is False
    if not native_ok or not safety_ok:
        return "DRAW_FAILED", "fixed native/safety contract mismatch", evidence

    if state == "FIXED_TEST_ACTUALLY_DRAWN":
        if core["callbackCount"] <= 0 or core["drawCount"] <= 0:
            return "DRAW_HOOK_NOT_FIRING", "drawn state lacks positive callback/draw counts", evidence
        evidence["machineDrawProof"] = True
        return (
            "MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL",
            "machine draw proof present; human visual confirmation is intentionally not inferred",
            evidence,
        )
    if state in READY_STATES:
        return "READY_FOR_OWNER_FIXED_TEST", "coherent P1+P2 fixed-test candidate is armed", evidence
    return "FEEDBACK_INPUT_MALFORMED", f"unknown fixed-smoke state: {state}", evidence


def _parse_text(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip():
            out[key.strip()] = value.strip()
    return out


def load_launcher_snapshot(results_dir: Path, repo_root: Path | None = None) -> SourceSnapshot:
    path = results_dir / OUTPUT_NAME
    try:
        data = _parse_text(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return SourceSnapshot(None, path, error="missing")
    except (OSError, UnicodeError) as exc:
        return SourceSnapshot(None, path, error=f"unreadable: {exc.__class__.__name__}")
    if not data:
        return SourceSnapshot(None, path, error="malformed: no key/value fields")
    managed, update = _repo_readiness((repo_root or _default_repo_root()).resolve(), data)
    data["managedRepoReady"] = managed
    data["updateChannelReady"] = update
    return SourceSnapshot(data, path)


def load_fixed_snapshot(results_dir: Path) -> SourceSnapshot:
    path = results_dir / FIXED_STATUS_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return SourceSnapshot(None, path, error="missing")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return SourceSnapshot(None, path, error=f"malformed: {exc.__class__.__name__}")
    if not isinstance(data, Mapping):
        return SourceSnapshot(None, path, error="malformed: root is not an object")
    try:
        age = max(0.0, datetime.now(timezone.utc).timestamp() - path.stat().st_mtime)
    except OSError:
        age = None
    return SourceSnapshot(data, path, age_seconds=age)


def _fmt(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def render_feedback(
    classification: str,
    reason: str,
    evidence: Mapping[str, Any],
    *,
    fixed_status_path: Path,
    fixed_age_seconds: float | None,
    generated_at: datetime | None = None,
) -> str:
    if classification not in ROUTING_STATES:
        raise ValueError(classification)
    now = generated_at or datetime.now(timezone.utc)
    dbw, dbh = evidence.get("drawingBufferWidth"), evidence.get("drawingBufferHeight")
    buffer_text = "unknown" if dbw is None or dbh is None else f"{dbw}x{dbh}"
    last_error = evidence.get("lastError")
    lines = [
        "WOF Alpha Owner Feedback",
        f"artifactSchema={SCHEMA}",
        f"generatedAt={now.isoformat().replace('+00:00', 'Z')}",
        f"currentReleaseSha={_fmt(evidence.get('currentReleaseSha'))}",
        "alphaLive=alpha-live",
        f"liveMode={_fmt(evidence.get('liveMode'))}",
        f"managedRepoReady={_fmt(evidence.get('managedRepoReady'))}",
        f"updateChannelReady={_fmt(evidence.get('updateChannelReady'))}",
        f"runtimeReady={_fmt(evidence.get('runtimeReady'))}",
        f"fixedSmokeStatusPath={fixed_status_path}",
        f"fixedSmokeSourceAgeSeconds={_fmt(None if fixed_age_seconds is None else round(fixed_age_seconds, 3))}",
        f"fixedSmokeState={_fmt(evidence.get('fixedSmokeState'))}",
        f"hudInjected={_fmt(evidence.get('hudInjected'))}",
        f"gameCanvasContextPresent={_fmt(evidence.get('gameCanvasContextPresent'))}",
        f"drawHooked={_fmt(evidence.get('drawHooked'))}",
        f"callbackCount={_fmt(evidence.get('callbackCount'))}",
        f"drawCount={_fmt(evidence.get('drawCount'))}",
        f"drawingBuffer={buffer_text}",
        f"native={_fmt(evidence.get('nativeWidth'))}x{_fmt(evidence.get('nativeHeight'))}",
        f"center={_fmt(evidence.get('nativeX'))},{_fmt(evidence.get('nativeY'))}",
        f"label={_fmt(evidence.get('label'))}",
        f"lastError={'NONE' if last_error is None else _fmt(last_error)}",
        f"machineDrawProof={'PRESENT' if evidence.get('machineDrawProof') is True else 'ABSENT'}",
        "ownerVisualConfirmation=NOT_RECORDED",
        f"routingClassification={classification}",
        f"routingReason={reason}",
    ]
    return "\n".join(lines) + "\n"


def write_feedback(results_dir: Path, repo_root: Path | None = None) -> tuple[Path, str]:
    results_dir.mkdir(parents=True, exist_ok=True)
    launcher = load_launcher_snapshot(results_dir, repo_root=repo_root)
    fixed = load_fixed_snapshot(results_dir)
    state, reason, evidence = classify(
        launcher.data,
        fixed.data,
        fixed_age_seconds=fixed.age_seconds,
        fixed_source_error=fixed.error,
    )
    output = results_dir / OUTPUT_NAME
    text = render_feedback(state, reason, evidence, fixed_status_path=fixed.path, fixed_age_seconds=fixed.age_seconds)
    fd, temp_name = tempfile.mkstemp(prefix=".LATEST_ALPHA_FEEDBACK.", suffix=".tmp", dir=results_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temp_name, output)
    finally:
        try:
            Path(temp_name).unlink(missing_ok=True)
        except OSError:
            pass
    return output, state


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_results_dir() -> Path:
    return Path.home() / "Documents" / "WOF_RESULTS"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate Alpha Owner feedback without DevTools or manual internal-file selection.")
    parser.add_argument("--results-dir", type=Path, default=_default_results_dir())
    args = parser.parse_args(argv)
    path, state = write_feedback(args.results_dir)
    print(path)
    print(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
