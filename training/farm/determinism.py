"""Single-instance savestate determinism runner and CLI for Training Farm R0.2."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .adapter import CoreAction, CoreFrameInput, TrainingFarmAdapter, TrainingFarmError
from .fake_backend import DeterministicFakeBackend
from .identity import (
    build_fixture_runtime_identity,
    build_real_runtime_identity,
    identities_match_exactly,
    runtime_identity_sha256,
    validate_runtime_identity,
)
from .stable_retro_backend import StableRetroFbneoBackend, dependency_probe

RESULT_SCHEMA = "wof-training-farm-determinism-result-v1"
PROOF_SCOPE_REAL = "REAL_WOF"
PROOF_SCOPE_FIXTURE = "IMPLEMENTATION_FIXTURE"
SOURCE_NAMESPACE = "stable-retro-fbneo"
MAX_HORIZON_FRAMES = 100_000
MAX_REPETITIONS = 100
_CLI_UINT = re.compile(r"[1-9][0-9]*\Z")


class DeterminismContractError(TrainingFarmError):
    """Malformed/coercible deterministic replay request."""


@dataclass(frozen=True)
class ReplayStep:
    frames: int
    frame_input: CoreFrameInput

    def __post_init__(self) -> None:
        _strict_int(self.frames, "frames", 1, MAX_HORIZON_FRAMES)
        if not isinstance(self.frame_input, CoreFrameInput):
            raise TypeError("frame_input must be CoreFrameInput")


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _strict_int(value: object, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DeterminismContractError(f"{field} must be a strict integer")
    if not minimum <= value <= maximum:
        raise DeterminismContractError(f"{field} must be in range {minimum}..{maximum}")
    return value


def parse_action_sequence(value: object) -> tuple[ReplayStep, ...]:
    if type(value) is not list or not value:
        raise DeterminismContractError("action sequence must be a non-empty JSON array")
    steps: list[ReplayStep] = []
    for si, raw in enumerate(value):
        if type(raw) is not dict or set(raw) != {"frames", "inputs"}:
            raise DeterminismContractError(f"action[{si}] must contain exactly frames and inputs")
        frames = _strict_int(raw["frames"], f"action[{si}].frames", 1, MAX_HORIZON_FRAMES)
        inputs = raw["inputs"]
        if type(inputs) is not list or len(inputs) != 4:
            raise DeterminismContractError(f"action[{si}].inputs must contain exactly four player entries")
        actions: list[CoreAction] = []
        for ii, item in enumerate(inputs):
            if type(item) is not dict or set(item) != {"player", "pressed"}:
                raise DeterminismContractError(
                    f"action[{si}].inputs[{ii}] must contain exactly player and pressed"
                )
            player = _strict_int(item["player"], f"action[{si}].inputs[{ii}].player", 0, 3)
            pressed_raw = item["pressed"]
            if type(pressed_raw) is not list:
                raise DeterminismContractError(f"action[{si}].inputs[{ii}].pressed must be a JSON array")
            pressed = tuple(
                _strict_int(button, f"action[{si}].inputs[{ii}].pressed[{bi}]", 0, 4095)
                for bi, button in enumerate(pressed_raw)
            )
            if len(set(pressed)) != len(pressed):
                raise DeterminismContractError(f"action[{si}].inputs[{ii}].pressed has duplicates")
            actions.append(CoreAction(player=player, pressed=pressed))
        if tuple(a.player for a in actions) != (0, 1, 2, 3):
            raise DeterminismContractError(f"action[{si}] must list players exactly in order 0,1,2,3")
        steps.append(ReplayStep(frames, CoreFrameInput(tuple(actions))))  # type: ignore[arg-type]
    return tuple(steps)


def canonical_action_payload(steps: tuple[ReplayStep, ...]) -> list[dict[str, object]]:
    return [
        {
            "frames": step.frames,
            "inputs": [
                {"player": action.player, "pressed": list(action.pressed)}
                for action in step.frame_input.inputs
            ],
        }
        for step in steps
    ]


def action_sequence_sha256(steps: tuple[ReplayStep, ...]) -> str:
    payload = json.dumps(canonical_action_payload(steps), sort_keys=True, separators=(",", ":"))
    return _sha(payload.encode("utf-8"))


def _validate_request(steps: object, horizon: object, repetitions: object) -> tuple[int, int]:
    if not isinstance(steps, tuple) or not steps or any(not isinstance(s, ReplayStep) for s in steps):
        raise DeterminismContractError("steps must be a non-empty tuple of ReplayStep")
    h = _strict_int(horizon, "horizon", 1, MAX_HORIZON_FRAMES)
    r = _strict_int(repetitions, "repetitions", 2, MAX_REPETITIONS)
    action_frames = sum(s.frames for s in steps)
    if action_frames != h:
        raise DeterminismContractError(f"action sequence covers {action_frames} frames but horizon is {h}")
    return h, r


def _base(run_id: str, steps: tuple[ReplayStep, ...], h: int, r: int, scope: str) -> dict[str, object]:
    return {
        "schema": RESULT_SCHEMA,
        "runId": run_id,
        "status": "ERROR",
        "reasonCode": "UNINITIALIZED",
        "message": "",
        "proofScope": scope,
        "realWofProof": False,
        "sourceNamespace": SOURCE_NAMESPACE,
        "repetitionsRequired": r,
        "repetitionsCompleted": 0,
        "horizonFrames": h,
        "actionSequence": canonical_action_payload(steps),
        "actionSequenceSha256": action_sequence_sha256(steps),
        "runtimeIdentity": None,
        "runtimeIdentitySha256": None,
        "startStateSha256": None,
        "startRamSha256": None,
        "repetitions": [],
        "firstDivergence": None,
    }


def _result(base: dict[str, object], status: str, code: str, message: str, divergence: object = None) -> dict[str, object]:
    out = dict(base)
    out.update(status=status, reasonCode=code, message=message, firstDivergence=divergence)
    return out


def _identity_check(
    provider: Callable[[], dict[str, object]], baseline: dict[str, object], require_real: bool
) -> tuple[bool, dict[str, object]]:
    observed = validate_runtime_identity(provider(), require_real_rom=require_real)
    return identities_match_exactly(baseline, observed, require_real_rom=require_real), observed


def run_determinism(
    adapter: TrainingFarmAdapter,
    steps: tuple[ReplayStep, ...],
    *,
    horizon: object,
    repetitions: object,
    identity_provider: Callable[[], dict[str, object]],
    proof_scope: str,
) -> dict[str, object]:
    """Restore one exact state before each repetition and compare exact observables."""
    h, r = _validate_request(steps, horizon, repetitions)
    if proof_scope not in (PROOF_SCOPE_REAL, PROOF_SCOPE_FIXTURE):
        raise DeterminismContractError("proof_scope is invalid")
    require_real = proof_scope == PROOF_SCOPE_REAL
    run_id = uuid.uuid4().hex
    base = _base(run_id, steps, h, r, proof_scope)
    try:
        baseline = validate_runtime_identity(identity_provider(), require_real_rom=require_real)
        base["runtimeIdentity"] = baseline
        base["runtimeIdentitySha256"] = runtime_identity_sha256(baseline, require_real_rom=require_real)
    except (TrainingFarmError, TypeError, ValueError) as exc:
        return _result(
            base,
            "ERROR",
            "INVALID_RUNTIME_IDENTITY",
            f"{type(exc).__name__}: {exc}",
            {"kind": "IDENTITY", "phase": "baseline"},
        )

    try:
        start_ram = adapter.reset()
        start_state = adapter.save_state()
        start_ram_sha, start_state_sha = _sha(start_ram), _sha(start_state)
        base["startRamSha256"], base["startStateSha256"] = start_ram_sha, start_state_sha

        same, observed = _identity_check(identity_provider, baseline, require_real)
        if not same:
            return _result(base, "ERROR", "IDENTITY_CHANGED", "identity changed after start-state save", {
                "kind": "IDENTITY", "phase": "after-start-state-save", "repetition": 0,
                "observedIdentity": observed,
            })

        reps: list[dict[str, object]] = []
        baseline_cp: list[dict[str, object]] | None = None
        baseline_final: str | None = None
        for ri in range(r):
            same, observed = _identity_check(identity_provider, baseline, require_real)
            if not same:
                base["repetitions"], base["repetitionsCompleted"] = reps, len(reps)
                return _result(base, "ERROR", "IDENTITY_CHANGED", "identity changed before repetition", {
                    "kind": "IDENTITY", "phase": "before-repetition", "repetition": ri,
                    "observedIdentity": observed,
                })
            if _sha(start_state) != start_state_sha:
                return _result(base, "ERROR", "START_STATE_HASH_CHANGED", "in-memory starting state hash changed", {
                    "kind": "SAVESTATE", "phase": "before-load", "repetition": ri,
                })

            adapter.load_state(start_state)
            restored_sha = _sha(adapter.read_ram())
            if restored_sha != start_ram_sha:
                return _result(base, "ERROR", "SAVESTATE_RESTORE_RAM_MISMATCH", "restored RAM differs from starting RAM", {
                    "kind": "START_RAM", "repetition": ri,
                    "expectedRamSha256": start_ram_sha, "actualRamSha256": restored_sha,
                })
            roundtrip_sha = _sha(adapter.save_state())
            if roundtrip_sha != start_state_sha:
                return _result(base, "ERROR", "SAVESTATE_HASH_MISMATCH", "savestate changed after exact load/save roundtrip", {
                    "kind": "SAVESTATE", "repetition": ri,
                    "expectedStateSha256": start_state_sha, "actualStateSha256": roundtrip_sha,
                })

            checkpoints: list[dict[str, object]] = []
            frame = 0
            for si, step in enumerate(steps):
                for _ in range(step.frames):
                    frame += 1
                    checkpoints.append({
                        "frame": frame,
                        "actionStep": si,
                        "ramSha256": _sha(adapter.step_frame(step.frame_input)),
                    })
            if frame != h or len(checkpoints) != h:
                return _result(base, "ERROR", "FRAME_COUNT_MISMATCH", "executed frames differ from horizon", {
                    "kind": "FRAME_COUNT", "repetition": ri, "expectedFrames": h, "actualFrames": frame,
                })
            final_sha = _sha(adapter.read_ram())
            if checkpoints[-1]["ramSha256"] != final_sha:
                return _result(base, "ERROR", "FINAL_RAM_CHECKPOINT_MISMATCH", "final RAM differs from last checkpoint", {
                    "kind": "FINAL_RAM", "repetition": ri,
                })
            same, observed = _identity_check(identity_provider, baseline, require_real)
            if not same:
                return _result(base, "ERROR", "IDENTITY_CHANGED", "identity changed after repetition", {
                    "kind": "IDENTITY", "phase": "after-repetition", "repetition": ri,
                    "observedIdentity": observed,
                })

            rep = {
                "index": ri,
                "framesExecuted": frame,
                "restoredRamSha256": restored_sha,
                "roundtripStateSha256": roundtrip_sha,
                "finalRamSha256": final_sha,
                "checkpoints": checkpoints,
            }
            reps.append(rep)
            base["repetitions"], base["repetitionsCompleted"] = reps, len(reps)
            if baseline_cp is None:
                baseline_cp, baseline_final = checkpoints, final_sha
                continue
            if len(checkpoints) != len(baseline_cp):
                return _result(base, "FAIL", "DETERMINISM_MISMATCH", "checkpoint counts diverged", {
                    "kind": "CHECKPOINT_COUNT", "baselineRepetition": 0, "repetition": ri,
                    "baselineCount": len(baseline_cp), "actualCount": len(checkpoints),
                })
            for expected, actual in zip(baseline_cp, checkpoints):
                if expected["ramSha256"] != actual["ramSha256"]:
                    return _result(base, "FAIL", "DETERMINISM_MISMATCH", "RAM checkpoint diverged", {
                        "kind": "RAM", "baselineRepetition": 0, "repetition": ri,
                        "frame": actual["frame"], "actionStep": actual["actionStep"],
                        "baselineRamSha256": expected["ramSha256"],
                        "actualRamSha256": actual["ramSha256"],
                    })
            if final_sha != baseline_final:
                return _result(base, "FAIL", "DETERMINISM_MISMATCH", "final RAM diverged", {
                    "kind": "FINAL_RAM", "baselineRepetition": 0, "repetition": ri,
                    "baselineRamSha256": baseline_final, "actualRamSha256": final_sha,
                })

        if len(reps) != r:
            return _result(base, "ERROR", "MISSING_REPETITION", "not all repetitions completed", {
                "kind": "REPETITION_COUNT", "expected": r, "actual": len(reps),
            })
        base.update(
            status="PASS",
            reasonCode="DETERMINISM_MATCH",
            message="all repetitions matched exact state, horizon, RAM checkpoints, final RAM, and identity",
            realWofProof=require_real,
            firstDivergence=None,
        )
        return base
    except (TrainingFarmError, TypeError, ValueError) as exc:
        return _result(base, "ERROR", "RUNTIME_OPERATION_FAILED", f"{type(exc).__name__}: {exc}")


def _parse_cli_uint(raw: str, field: str, maximum: int) -> int:
    if type(raw) is not str or not _CLI_UINT.fullmatch(raw):
        raise DeterminismContractError(f"{field} must be canonical positive decimal digits")
    value = int(raw)
    if value > maximum:
        raise DeterminismContractError(f"{field} exceeds maximum {maximum}")
    return value


def load_action_sequence(*, actions_path: str | None, actions_json: str | None) -> tuple[ReplayStep, ...]:
    if (actions_path is None) == (actions_json is None):
        raise DeterminismContractError("provide exactly one of --actions or --actions-json")
    try:
        text = Path(actions_path).read_text(encoding="utf-8") if actions_path else actions_json
        assert text is not None
        raw = json.loads(text)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DeterminismContractError(f"failed to load action JSON: {type(exc).__name__}: {exc}") from exc
    return parse_action_sequence(raw)


def prerequisite_skip_result(detail: str, environment: dict[str, object]) -> dict[str, object]:
    return {
        "schema": RESULT_SCHEMA, "runId": uuid.uuid4().hex, "status": "SKIP",
        "reasonCode": "RUNTIME_PREREQUISITE_UNAVAILABLE", "message": detail,
        "proofScope": PROOF_SCOPE_REAL, "realWofProof": False,
        "sourceNamespace": SOURCE_NAMESPACE, "environment": environment, "firstDivergence": None,
    }


def error_result(code: str, message: str) -> dict[str, object]:
    return {
        "schema": RESULT_SCHEMA, "runId": uuid.uuid4().hex, "status": "ERROR",
        "reasonCode": code, "message": message, "proofScope": None,
        "realWofProof": False, "sourceNamespace": SOURCE_NAMESPACE, "firstDivergence": None,
    }


def _emit(result: dict[str, object], output: str | None) -> None:
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    print(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Training Farm R0.2 single-instance savestate determinism replay")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--actions", help="path to strict action-sequence JSON")
    source.add_argument("--actions-json", help="strict action-sequence JSON text")
    parser.add_argument("--horizon", required=True, help="exact emulated frame horizon")
    parser.add_argument("--repetitions", default="3", help="repeat count 2..100 (default 3)")
    parser.add_argument("--fake", action="store_true", help="ROM-free fixture; never real-WOF proof")
    parser.add_argument("--output", help="optional JSON result path")
    args = parser.parse_args(argv)
    try:
        h = _parse_cli_uint(args.horizon, "horizon", MAX_HORIZON_FRAMES)
        r = _parse_cli_uint(args.repetitions, "repetitions", MAX_REPETITIONS)
        if r < 2:
            raise DeterminismContractError("repetitions must be at least 2")
        steps = load_action_sequence(actions_path=args.actions, actions_json=args.actions_json)
        _validate_request(steps, h, r)
    except DeterminismContractError as exc:
        result = error_result("INVALID_CONTRACT", str(exc))
        _emit(result, args.output)
        return 1

    if args.fake:
        try:
            with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
                result = run_determinism(
                    adapter, steps, horizon=h, repetitions=r,
                    identity_provider=lambda: build_fixture_runtime_identity(adapter),
                    proof_scope=PROOF_SCOPE_FIXTURE,
                )
        except TrainingFarmError as exc:
            result = error_result("RUNTIME_OPERATION_FAILED", f"{type(exc).__name__}: {exc}")
        _emit(result, args.output)
        return 0 if result.get("status") == "PASS" else 1

    report = dependency_probe()
    if not report.runtime_ready:
        result = prerequisite_skip_result(report.detail, report.to_dict())
        _emit(result, args.output)
        return 2
    try:
        with TrainingFarmAdapter(StableRetroFbneoBackend()) as adapter:
            result = run_determinism(
                adapter, steps, horizon=h, repetitions=r,
                identity_provider=lambda: build_real_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_REAL,
            )
    except (TrainingFarmError, OSError) as exc:
        result = error_result("RUNTIME_OPERATION_FAILED", f"{type(exc).__name__}: {exc}")
    _emit(result, args.output)
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
