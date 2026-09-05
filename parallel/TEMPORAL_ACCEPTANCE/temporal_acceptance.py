from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

OBSERVATION_SCHEMA = "wof-alpha-canonical-temporal-observation-v1"
BUNDLE_SCHEMA = "wof-alpha-canonical-temporal-observation-bundle-v1"
REPORT_SCHEMA = "wof-alpha-canonical-temporal-stability-evidence-v1"
REPORT_VERSION = 1
P16_SCHEMA = "wof-alpha-canonical-owner-acceptance-evidence-v1"
P18_SCHEMA = "wof-alpha-canonical-draw-evidence-v1"
P18_HUD_SCHEMA = "wof-alpha-maintained-hud-canonical-draw-evidence-v1"
DEFAULT_OUTPUT_ROOT = Path.home() / "Documents" / "WOF_RESULTS" / "ALPHA_P24_TEMPORAL_ACCEPTANCE"
DEFAULT_JSON_NAME = "ALPHA_CANONICAL_TEMPORAL_CONTINUITY_EVIDENCE.json"
DEFAULT_MD_NAME = "ALPHA_CANONICAL_TEMPORAL_CONTINUITY_EVIDENCE.md"
MAX_OBSERVATIONS = 4096
MAX_REJECTIONS = 512
WORLD_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
PLAYER_RE = re.compile(r"^P[123]$")
ENEMY_RE = re.compile(r"^enemy-slot-(?:[0-9]|1[0-9])$")
ALLOWED_STATES = frozenset({"READY", "SUPPRESSED"})
ALLOWED_PRESENCE = frozenset({"PRESENT", "ABSENT", "UNKNOWN"})
CLASSIFICATIONS = (
    "PROVEN_CONTINUOUS",
    "OBSERVED_WITH_CHURN",
    "SUPPRESSED_SAFELY",
    "STALE_OR_MISMATCH",
    "INSUFFICIENT_EVIDENCE",
    "UNPROVEN",
)
SAFETY = {
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "legacySpatialFallback": False,
    "interpolation": False,
    "oldCoordinateReuse": False,
    "spatialIdentityInference": False,
    "nearestObjectInference": False,
    "rowOrderIdentityInference": False,
    "screenshotProductionCoordinates": False,
    "worldProjectionProductionCoordinates": False,
    "alphaLiveMutation": False,
}


class ObservationError(ValueError):
    pass


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _actor_valid(value: Any) -> bool:
    return isinstance(value, str) and bool(PLAYER_RE.fullmatch(value) or ENEMY_RE.fullmatch(value))


def _authority_from(row: Mapping[str, Any]) -> dict[str, str]:
    world = row.get("worldSha256")
    authority = row.get("authorityKey")
    runtime = row.get("runtimeEpoch")
    renderer = row.get("rendererEpoch")
    if not isinstance(world, str) or WORLD_SHA_RE.fullmatch(world) is None:
        raise ObservationError("WORLD_SHA_INVALID")
    if not isinstance(authority, str) or not authority:
        raise ObservationError("AUTHORITY_KEY_INVALID")
    if not isinstance(runtime, str) or len(runtime) < 16:
        raise ObservationError("RUNTIME_EPOCH_INVALID")
    if not isinstance(renderer, str) or len(renderer) < 16:
        raise ObservationError("RENDERER_EPOCH_INVALID")
    return {
        "worldSha256": world,
        "authorityKey": authority,
        "runtimeEpoch": runtime,
        "rendererEpoch": renderer,
    }


def _epoch_key(row: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row["worldSha256"]),
        str(row["authorityKey"]),
        str(row["runtimeEpoch"]),
        str(row["rendererEpoch"]),
    )


def _identity_key(row: Mapping[str, Any]) -> tuple[str, str, str, str, str, int]:
    epoch = _epoch_key(row)
    return (*epoch, str(row["actor"]), int(row["generation"]))


def normalize_p18_acknowledgement(row: Mapping[str, Any]) -> dict[str, Any]:
    """Copy only P18 fields needed for causal validation; never use coordinates as identity."""
    if not isinstance(row, Mapping):
        raise ObservationError("DRAW_ACK_INVALID")
    out = {
        key: copy.deepcopy(row.get(key))
        for key in (
            "sequence",
            "acknowledgedAt",
            "evidenceGeneration",
            "kind",
            "primitive",
            "completed",
            "actor",
            "generation",
            "authority",
            "sampleIdentity",
            "coordinateAuthority",
            "screenshotAuthority",
            "worldProjectionAuthority",
            "visibleProof",
        )
        if key in row
    }
    return out


def normalize_observation(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ObservationError("OBSERVATION_NOT_OBJECT")
    if raw.get("schema") != OBSERVATION_SCHEMA:
        raise ObservationError("OBSERVATION_SCHEMA_MISMATCH")
    if not _nonnegative_int(raw.get("sampleSeq")):
        raise ObservationError("SAMPLE_SEQUENCE_INVALID")
    if not _nonnegative_int(raw.get("frameSeq")):
        raise ObservationError("FRAME_SEQUENCE_INVALID")
    if not _finite(raw.get("observedAt")):
        raise ObservationError("OBSERVED_AT_INVALID")
    authority = _authority_from(raw)
    actor = raw.get("actor")
    if not _actor_valid(actor):
        raise ObservationError("ACTOR_INVALID")
    generation = raw.get("generation")
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 0:
        raise ObservationError("GENERATION_INVALID")
    state = raw.get("state")
    if state not in ALLOWED_STATES:
        raise ObservationError("STATE_INVALID")
    reason = raw.get("reason")
    if state == "SUPPRESSED" and (not isinstance(reason, str) or not reason):
        raise ObservationError("SUPPRESSION_REASON_REQUIRED")
    if state == "READY" and reason not in (None, "READY", "CANONICAL_ANCHORS_READY"):
        raise ObservationError("READY_REASON_INVALID")
    presence = raw.get("actorPresence", "UNKNOWN")
    if presence not in ALLOWED_PRESENCE:
        raise ObservationError("ACTOR_PRESENCE_INVALID")
    if state == "READY" and presence == "ABSENT":
        raise ObservationError("READY_ACTOR_ABSENT")

    safety = raw.get("safety")
    if not isinstance(safety, Mapping):
        raise ObservationError("SAFETY_MISSING")
    for key, expected in ("readOnly", True), ("ramWrites", 0), ("inputInjection", False):
        if safety.get(key) != expected:
            raise ObservationError("SAFETY_MISMATCH")

    geometry = raw.get("canonicalGeometry")
    if geometry is not None:
        if state != "READY":
            raise ObservationError("SUPPRESSED_GEOMETRY_FORBIDDEN")
        if not isinstance(geometry, Mapping) or geometry.get("coordinateAuthority") != "canonical-render-object-only":
            raise ObservationError("GEOMETRY_AUTHORITY_INVALID")

    transport_sequence = raw.get("transportSequence")
    if transport_sequence is not None and not _nonnegative_int(transport_sequence):
        raise ObservationError("TRANSPORT_SEQUENCE_INVALID")
    canonical_sample_at = raw.get("canonicalSampleAt")
    if canonical_sample_at is not None and not _finite(canonical_sample_at):
        raise ObservationError("CANONICAL_SAMPLE_AT_INVALID")

    acknowledgements = raw.get("drawAcknowledgements", [])
    if not isinstance(acknowledgements, list):
        raise ObservationError("DRAW_ACK_LIST_INVALID")

    out = {
        "schema": OBSERVATION_SCHEMA,
        "sampleSeq": int(raw["sampleSeq"]),
        "frameSeq": int(raw["frameSeq"]),
        "observedAt": float(raw["observedAt"]),
        **authority,
        "actor": actor,
        "generation": generation,
        "state": state,
        "reason": None if state == "READY" else reason,
        "actorPresence": presence,
        "transportSequence": transport_sequence,
        "canonicalSampleAt": float(canonical_sample_at) if canonical_sample_at is not None else None,
        "canonicalGeometry": copy.deepcopy(geometry),
        "drawAcknowledgements": [normalize_p18_acknowledgement(row) for row in acknowledgements],
    }
    return out


def load_observation_input(path: str | os.PathLike[str]) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        return {"schema": BUNDLE_SCHEMA, "observations": [], "sourceEvidence": {}}
    if source.suffix.lower() == ".jsonl" or not stripped.startswith(("[", "{")):
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        return {"schema": BUNDLE_SCHEMA, "observations": rows, "sourceEvidence": {}}
    value = json.loads(text)
    if isinstance(value, list):
        return {"schema": BUNDLE_SCHEMA, "observations": value, "sourceEvidence": {}}
    if not isinstance(value, dict):
        raise ObservationError("INPUT_ROOT_INVALID")
    if value.get("schema") == OBSERVATION_SCHEMA:
        return {"schema": BUNDLE_SCHEMA, "observations": [value], "sourceEvidence": {}}
    if value.get("schema") != BUNDLE_SCHEMA or not isinstance(value.get("observations"), list):
        raise ObservationError("BUNDLE_SCHEMA_MISMATCH")
    return value


def _source_evidence_summary(source: Any) -> dict[str, Any]:
    summary = {
        "p16": {"present": False, "bindingOnly": True, "validBoundary": True, "reason": None},
        "p18": {"snapshotCount": 0, "bindingOnly": True, "validBoundary": True, "reasons": []},
        "continuityCredit": False,
    }
    if not isinstance(source, Mapping):
        return summary
    p16 = source.get("p16")
    if p16 is not None:
        summary["p16"]["present"] = True
        if not isinstance(p16, Mapping) or p16.get("schema") != P16_SCHEMA or p16.get("visibleProof") != "NOT_PROVEN":
            summary["p16"].update(validBoundary=False, reason="P16_BOUNDARY_INVALID")
    p18_rows = source.get("p18Snapshots", [])
    if p18_rows is not None:
        if not isinstance(p18_rows, list):
            summary["p18"].update(validBoundary=False, reasons=["P18_SNAPSHOTS_INVALID"])
        else:
            summary["p18"]["snapshotCount"] = len(p18_rows)
            for row in p18_rows:
                valid = isinstance(row, Mapping) and row.get("schema") == P18_SCHEMA and row.get("visibleProof") == "NOT_PROVEN"
                if not valid:
                    summary["p18"]["validBoundary"] = False
                    summary["p18"]["reasons"].append("P18_BOUNDARY_INVALID")
    return summary


def _reason_rejection(raw: Any, reason: str) -> dict[str, Any]:
    if isinstance(raw, Mapping):
        return {
            "sampleSeq": raw.get("sampleSeq"),
            "frameSeq": raw.get("frameSeq"),
            "actor": raw.get("actor"),
            "generation": raw.get("generation"),
            "reason": reason,
        }
    return {"sampleSeq": None, "frameSeq": None, "actor": None, "generation": None, "reason": reason}


def _validate_ack(
    ack: Mapping[str, Any],
    observation: Mapping[str, Any],
    *,
    seen_ack_keys: set[tuple[Any, ...]],
    ack_generation_state: dict[tuple[Any, ...], dict[str, Any]],
) -> tuple[str, str | None]:
    sequence = ack.get("sequence")
    evidence_generation = ack.get("evidenceGeneration")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        return "STALE", "DRAW_ACK_SEQUENCE_INVALID"
    if not isinstance(evidence_generation, int) or isinstance(evidence_generation, bool) or evidence_generation < 1:
        return "STALE", "DRAW_ACK_EVIDENCE_GENERATION_INVALID"
    if ack.get("completed") is not True or ack.get("visibleProof") != "NOT_PROVEN":
        return "STALE", "DRAW_ACK_PROOF_BOUNDARY_INVALID"
    if ack.get("coordinateAuthority") != "canonical-render-object-only" or ack.get("screenshotAuthority") is not False or ack.get("worldProjectionAuthority") is not False:
        return "STALE", "DRAW_ACK_COORDINATE_AUTHORITY_INVALID"
    if ack.get("actor") != observation["actor"] or ack.get("generation") != observation["generation"]:
        return "STALE", "DRAW_ACK_ACTOR_GENERATION_MISMATCH"
    authority = ack.get("authority")
    expected = {key: observation[key] for key in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch")}
    if not isinstance(authority, Mapping) or any(authority.get(key) != value for key, value in expected.items()):
        return "STALE", "DRAW_ACK_AUTHORITY_MISMATCH"
    if observation["state"] != "READY" or observation["actorPresence"] == "ABSENT":
        return "STALE", "DRAW_ACK_AFTER_SUPPRESSION_OR_ABSENCE"
    sample_identity = ack.get("sampleIdentity")
    if observation.get("transportSequence") is not None:
        if not isinstance(sample_identity, Mapping) or sample_identity.get("transportSequence") != observation["transportSequence"]:
            return "STALE", "DRAW_ACK_TRANSPORT_SEQUENCE_STALE"
    if observation.get("canonicalSampleAt") is not None:
        if not isinstance(sample_identity, Mapping) or sample_identity.get("sampleAt") != observation["canonicalSampleAt"]:
            return "STALE", "DRAW_ACK_SAMPLE_IDENTITY_STALE"

    epoch_actor = (*_epoch_key(observation), observation["actor"])
    generation_state = ack_generation_state.setdefault(epoch_actor, {"current": None, "revoked": set()})
    current_generation = generation_state["current"]
    if current_generation is None:
        generation_state["current"] = evidence_generation
    elif evidence_generation != current_generation:
        if evidence_generation in generation_state["revoked"]:
            return "STALE", "DRAW_ACK_EVIDENCE_GENERATION_REVOKED"
        generation_state["revoked"].add(current_generation)
        generation_state["current"] = evidence_generation

    ack_key = (*_identity_key(observation), evidence_generation, sequence)
    if ack_key in seen_ack_keys:
        return "DUPLICATE", "DRAW_ACK_DUPLICATE"
    seen_ack_keys.add(ack_key)
    return "ACCEPTED", None


def _state_runs(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int, int]:
    if not rows:
        return [], 0, 0, 0
    runs: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    previous_boundary = None
    for row in rows:
        boundary = (_epoch_key(row), row["generation"])
        if current is None or row["state"] != current["state"] or boundary != previous_boundary:
            if current is not None:
                runs.append(current)
            current = {
                "state": row["state"],
                "count": 1,
                "startSeq": row["sampleSeq"],
                "endSeq": row["sampleSeq"],
                "startAt": row["observedAt"],
                "endAt": row["observedAt"],
                "duration": 0.0,
                "boundary": {
                    "worldSha256": row["worldSha256"],
                    "authorityKey": row["authorityKey"],
                    "runtimeEpoch": row["runtimeEpoch"],
                    "rendererEpoch": row["rendererEpoch"],
                    "generation": row["generation"],
                },
            }
        else:
            current["count"] += 1
            current["endSeq"] = row["sampleSeq"]
            current["endAt"] = row["observedAt"]
            current["duration"] = max(0.0, float(current["endAt"]) - float(current["startAt"]))
        previous_boundary = boundary
    if current is not None:
        runs.append(current)

    transitions = 0
    ready_pulses = 0
    suppressed_pulses = 0
    for index, run in enumerate(runs):
        if index > 0 and runs[index - 1]["boundary"] == run["boundary"] and runs[index - 1]["state"] != run["state"]:
            transitions += 1
        if 0 < index < len(runs) - 1 and run["count"] == 1:
            left, right = runs[index - 1], runs[index + 1]
            if left["boundary"] == run["boundary"] == right["boundary"] and left["state"] == right["state"] != run["state"]:
                if run["state"] == "READY":
                    ready_pulses += 1
                else:
                    suppressed_pulses += 1
    return runs, transitions, ready_pulses, suppressed_pulses


def _stream_metrics(rows: list[dict[str, Any]], rejects: list[dict[str, Any]], actor_events: Mapping[str, int]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: row["sampleSeq"])
    runs, transitions, ready_pulses, suppressed_pulses = _state_runs(ordered)
    ready = sum(1 for row in ordered if row["state"] == "READY")
    suppressed = len(ordered) - ready
    suppression = Counter(row["reason"] for row in ordered if row["state"] == "SUPPRESSED")
    longest_ready = max((run["count"] for run in runs if run["state"] == "READY"), default=0)
    span = None
    elapsed = 0.0
    if ordered:
        span = [ordered[0]["sampleSeq"], ordered[-1]["sampleSeq"]]
        elapsed = max(0.0, ordered[-1]["observedAt"] - ordered[0]["observedAt"])
    reject_count = len(rejects)
    stale_rejects = sum(1 for row in rejects if "STALE" in str(row.get("reason")) or "MISMATCH" in str(row.get("reason")))
    if not ordered:
        classification = "STALE_OR_MISMATCH" if stale_rejects else "UNPROVEN"
        reasons = ["NO_ACCEPTED_OBSERVATIONS"]
    elif stale_rejects:
        classification = "STALE_OR_MISMATCH"
        reasons = ["STALE_OR_MISMATCH_INPUT_REJECTED"]
    elif len(ordered) < 2:
        classification = "INSUFFICIENT_EVIDENCE"
        reasons = ["FEWER_THAN_TWO_ACCEPTED_SAMPLES"]
    elif ready == 0:
        classification = "SUPPRESSED_SAFELY"
        reasons = ["NO_READY_DRAW_AUTHORITY", "SUPPRESSIONS_RETAINED"]
    elif transitions or ready_pulses or suppressed_pulses or actor_events.get("generationRollovers", 0) or actor_events.get("runtimeEpochReplacements", 0) or actor_events.get("rendererEpochReplacements", 0) or actor_events.get("disappearances", 0) or actor_events.get("reappearances", 0):
        classification = "OBSERVED_WITH_CHURN"
        reasons = ["TEMPORAL_TRANSITIONS_OBSERVED"]
        if actor_events.get("runtimeEpochReplacements", 0) or actor_events.get("rendererEpochReplacements", 0):
            reasons.append("NO_CROSS_EPOCH_CONTINUITY_CLAIM")
    else:
        classification = "PROVEN_CONTINUOUS"
        reasons = ["ORDERED_EXACT_IDENTITY_READY_SEQUENCE"]

    return {
        "sampleCount": len(ordered),
        "acceptedSequenceSpan": span,
        "readyCount": ready,
        "suppressedCount": suppressed,
        "suppressedByReason": dict(sorted(suppression.items())),
        "stateTransitionCount": transitions,
        "oneSampleReadyPulseCount": ready_pulses,
        "oneSampleSuppressedPulseCount": suppressed_pulses,
        "longestReadyRun": longest_ready,
        "stateRuns": runs,
        "churn": {
            "transitionRatePerAcceptedGap": (transitions / (len(ordered) - 1)) if len(ordered) > 1 else 0.0,
            "transitionRatePerSecond": (transitions / elapsed) if elapsed > 0 else None,
            "thresholdConfigured": False,
        },
        "rejectedObservationCount": reject_count,
        "staleOrMismatchRejectionCount": stale_rejects,
        "classification": classification,
        "reasons": reasons,
    }


def analyze_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(bundle, Mapping) or bundle.get("schema") != BUNDLE_SCHEMA:
        raise ObservationError("BUNDLE_SCHEMA_MISMATCH")
    raw_rows = bundle.get("observations")
    if not isinstance(raw_rows, list):
        raise ObservationError("OBSERVATIONS_LIST_MISSING")
    if len(raw_rows) > MAX_OBSERVATIONS:
        raise ObservationError("OBSERVATION_LIMIT_EXCEEDED")

    accepted: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    seen_sample_seq: set[int] = set()
    last_sample_seq = -1
    last_observed_at = -math.inf
    actor_state: dict[str, dict[str, Any]] = {}
    actor_events: dict[str, Counter[str]] = defaultdict(Counter)
    seen_ack_keys: set[tuple[Any, ...]] = set()
    ack_generation_state: dict[tuple[Any, ...], dict[str, Any]] = {}
    accepted_draw_acks = 0
    stale_draw_acks = 0
    duplicate_draw_acks = 0
    accepted_ack_rows: list[dict[str, Any]] = []

    for raw in raw_rows:
        try:
            row = normalize_observation(raw)
        except ObservationError as exc:
            rejections.append(_reason_rejection(raw, str(exc)))
            continue

        seq = row["sampleSeq"]
        if seq in seen_sample_seq:
            rejections.append(_reason_rejection(row, "DUPLICATE_SAMPLE_SEQUENCE"))
            continue
        if seq <= last_sample_seq:
            rejections.append(_reason_rejection(row, "OUT_OF_ORDER_SAMPLE_SEQUENCE"))
            continue
        if row["observedAt"] < last_observed_at:
            rejections.append(_reason_rejection(row, "OUT_OF_ORDER_OBSERVED_AT"))
            continue
        seen_sample_seq.add(seq)
        last_sample_seq = seq
        last_observed_at = row["observedAt"]

        actor = row["actor"]
        state = actor_state.setdefault(actor, {
            "currentEpoch": None,
            "revokedEpochs": set(),
            "currentGeneration": None,
            "revokedGenerations": defaultdict(set),
            "lastFrameByEpoch": {},
            "presence": "UNKNOWN",
        })
        epoch = _epoch_key(row)
        current_epoch = state["currentEpoch"]

        # Reject replay/order defects before committing any lifecycle mutation.
        last_frame = state["lastFrameByEpoch"].get(epoch)
        if last_frame is not None and row["frameSeq"] == last_frame:
            rejections.append(_reason_rejection(row, "DUPLICATE_FRAME_FOR_ACTOR"))
            continue
        if last_frame is not None and row["frameSeq"] < last_frame:
            rejections.append(_reason_rejection(row, "OUT_OF_ORDER_FRAME_FOR_ACTOR"))
            continue
        if current_epoch is not None and epoch != current_epoch and epoch in state["revokedEpochs"]:
            rejections.append(_reason_rejection(row, "STALE_EPOCH_REAPPEARANCE"))
            continue
        if current_epoch == epoch and state["currentGeneration"] is not None and row["generation"] != state["currentGeneration"]:
            if row["generation"] in state["revokedGenerations"][epoch]:
                rejections.append(_reason_rejection(row, "STALE_GENERATION_REAPPEARANCE"))
                continue

        if current_epoch is None:
            state["currentEpoch"] = epoch
            state["currentGeneration"] = row["generation"]
        elif epoch != current_epoch:
            state["revokedEpochs"].add(current_epoch)
            if epoch[2] != current_epoch[2]:
                actor_events[actor]["runtimeEpochReplacements"] += 1
            if epoch[3] != current_epoch[3]:
                actor_events[actor]["rendererEpochReplacements"] += 1
            state["currentEpoch"] = epoch
            state["currentGeneration"] = row["generation"]
        else:
            current_generation = state["currentGeneration"]
            if row["generation"] != current_generation:
                state["revokedGenerations"][epoch].add(current_generation)
                actor_events[actor]["generationRollovers"] += 1
                state["currentGeneration"] = row["generation"]

        state["lastFrameByEpoch"][epoch] = row["frameSeq"]

        previous_presence = state["presence"]
        presence = row["actorPresence"]
        if previous_presence == "PRESENT" and presence == "ABSENT":
            actor_events[actor]["disappearances"] += 1
        elif previous_presence == "ABSENT" and presence == "PRESENT":
            actor_events[actor]["reappearances"] += 1
        if presence != "UNKNOWN":
            state["presence"] = presence

        accepted.append(row)
        for ack in row["drawAcknowledgements"]:
            status, reason = _validate_ack(ack, row, seen_ack_keys=seen_ack_keys, ack_generation_state=ack_generation_state)
            if status == "ACCEPTED":
                accepted_draw_acks += 1
                accepted_ack_rows.append({
                    "sampleSeq": row["sampleSeq"],
                    "actor": row["actor"],
                    "generation": row["generation"],
                    "sequence": ack.get("sequence"),
                    "evidenceGeneration": ack.get("evidenceGeneration"),
                })
            elif status == "DUPLICATE":
                duplicate_draw_acks += 1
            else:
                stale_draw_acks += 1
                rejections.append(_reason_rejection(row, reason or "STALE_DRAW_ACK"))

    if len(rejections) > MAX_REJECTIONS:
        shown_rejections = rejections[:MAX_REJECTIONS]
        rejections_truncated = len(rejections) - MAX_REJECTIONS
    else:
        shown_rejections = rejections
        rejections_truncated = 0

    rows_by_stream: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    rejects_by_stream: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in accepted:
        rows_by_stream[(row["actor"], row["generation"])].append(row)
    for row in rejections:
        actor, generation = row.get("actor"), row.get("generation")
        if _actor_valid(actor) and isinstance(generation, int) and not isinstance(generation, bool):
            rejects_by_stream[(actor, generation)].append(row)

    stream_keys = sorted(set(rows_by_stream) | set(rejects_by_stream), key=lambda key: (key[0], key[1]))
    streams: list[dict[str, Any]] = []
    for actor, generation in stream_keys:
        metrics = _stream_metrics(rows_by_stream[(actor, generation)], rejects_by_stream[(actor, generation)], actor_events[actor])
        streams.append({"actor": actor, "generation": generation, **metrics})

    actors: list[dict[str, Any]] = []
    for actor in sorted(set(row["actor"] for row in accepted) | {row.get("actor") for row in rejections if _actor_valid(row.get("actor"))}):
        actor_rows = [row for row in accepted if row["actor"] == actor]
        actor_rejects = [row for row in rejections if row.get("actor") == actor]
        events = actor_events[actor]
        metrics = _stream_metrics(actor_rows, actor_rejects, events)
        actors.append({
            "actor": actor,
            **metrics,
            "generationRolloverCount": events.get("generationRollovers", 0),
            "runtimeEpochReplacementCount": events.get("runtimeEpochReplacements", 0),
            "rendererEpochReplacementCount": events.get("rendererEpochReplacements", 0),
            "disappearanceCount": events.get("disappearances", 0),
            "reappearanceCount": events.get("reappearances", 0),
        })

    total_ready = sum(1 for row in accepted if row["state"] == "READY")
    total_suppressed = len(accepted) - total_ready
    suppressions = Counter(row["reason"] for row in accepted if row["state"] == "SUPPRESSED")
    aggregate_runs, aggregate_transitions, aggregate_ready_pulses, aggregate_suppressed_pulses = _state_runs(sorted(accepted, key=lambda row: (row["actor"], row["sampleSeq"])))
    longest_ready = max((run["count"] for run in aggregate_runs if run["state"] == "READY"), default=0)
    classifications = [row["classification"] for row in actors]
    rejection_reasons = Counter(str(row.get("reason")) for row in rejections)
    stale_or_mismatch_rejects = sum(count for reason, count in rejection_reasons.items() if "STALE" in reason or "MISMATCH" in reason)
    duplicate_or_order_rejects = sum(count for reason, count in rejection_reasons.items() if "DUPLICATE" in reason or "OUT_OF_ORDER" in reason)

    source_summary = _source_evidence_summary(bundle.get("sourceEvidence"))
    boundary_invalid = not source_summary["p16"]["validBoundary"] or not source_summary["p18"]["validBoundary"]
    if not accepted and not rejections:
        aggregate_classification = "UNPROVEN"
        aggregate_reasons = ["NO_OBSERVATIONS"]
    elif boundary_invalid or stale_or_mismatch_rejects or stale_draw_acks:
        aggregate_classification = "STALE_OR_MISMATCH"
        aggregate_reasons = ["STALE_OR_MISMATCH_REJECTED_FAIL_CLOSED"]
    elif not actors:
        aggregate_classification = "UNPROVEN"
        aggregate_reasons = ["NO_ACTOR_STREAMS"]
    elif any(value in {"UNPROVEN", "INSUFFICIENT_EVIDENCE"} for value in classifications):
        aggregate_classification = "INSUFFICIENT_EVIDENCE"
        aggregate_reasons = ["AT_LEAST_ONE_ACTOR_STREAM_INSUFFICIENT", "MULTI_ACTOR_STREAMS_NOT_CROSS_REPAIRED"]
    elif total_ready == 0:
        aggregate_classification = "SUPPRESSED_SAFELY"
        aggregate_reasons = ["ALL_ACCEPTED_SAMPLES_SUPPRESSED_FAIL_CLOSED"]
    elif any(value == "OBSERVED_WITH_CHURN" for value in classifications):
        aggregate_classification = "OBSERVED_WITH_CHURN"
        aggregate_reasons = ["TEMPORAL_CHURN_OR_LIFECYCLE_BOUNDARY_OBSERVED", "NO_CROSS_ACTOR_OR_CROSS_EPOCH_REPAIR"]
    else:
        aggregate_classification = "PROVEN_CONTINUOUS"
        aggregate_reasons = ["ALL_ACTOR_STREAMS_INDEPENDENT_AND_EXACTLY_ORDERED"]

    generation_rollovers = sum(row.get("generationRolloverCount", 0) for row in actors)
    runtime_replacements = sum(row.get("runtimeEpochReplacementCount", 0) for row in actors)
    renderer_replacements = sum(row.get("rendererEpochReplacementCount", 0) for row in actors)
    disappearances = sum(row.get("disappearanceCount", 0) for row in actors)
    reappearances = sum(row.get("reappearanceCount", 0) for row in actors)

    return {
        "schema": REPORT_SCHEMA,
        "version": REPORT_VERSION,
        "inputSchema": OBSERVATION_SCHEMA,
        "classificationVocabulary": list(CLASSIFICATIONS),
        "aggregate": {
            "inputSampleCount": len(raw_rows),
            "acceptedSampleCount": len(accepted),
            "acceptedSequenceSpan": [accepted[0]["sampleSeq"], accepted[-1]["sampleSeq"]] if accepted else None,
            "readyCount": total_ready,
            "suppressedCount": total_suppressed,
            "suppressedByReason": dict(sorted(suppressions.items())),
            "stateTransitionCount": sum(row["stateTransitionCount"] for row in actors),
            "oneSampleReadyPulseCount": sum(row["oneSampleReadyPulseCount"] for row in actors),
            "oneSampleSuppressedPulseCount": sum(row["oneSampleSuppressedPulseCount"] for row in actors),
            "longestReadyRun": max((row["longestReadyRun"] for row in actors), default=longest_ready),
            "generationRolloverCount": generation_rollovers,
            "runtimeEpochReplacementCount": runtime_replacements,
            "rendererEpochReplacementCount": renderer_replacements,
            "staleDuplicateOutOfOrderRejectionCount": stale_or_mismatch_rejects + duplicate_or_order_rejects,
            "staleOrMismatchRejectionCount": stale_or_mismatch_rejects,
            "duplicateOrOutOfOrderRejectionCount": duplicate_or_order_rejects,
            "acceptedDrawAcknowledgementCount": accepted_draw_acks,
            "duplicateDrawAcknowledgementCount": duplicate_draw_acks,
            "staleDrawAcknowledgementRejectionCount": stale_draw_acks,
            "actorDisappearanceCount": disappearances,
            "actorReappearanceCount": reappearances,
            "classification": aggregate_classification,
            "reasons": aggregate_reasons,
            "thresholdConfigured": False,
        },
        "actors": actors,
        "actorGenerations": streams,
        "acceptedDrawAcknowledgements": accepted_ack_rows,
        "rejections": shown_rejections,
        "rejectionsTruncated": rejections_truncated,
        "rejectionReasons": dict(sorted(rejection_reasons.items())),
        "sourceEvidence": source_summary,
        "proofBoundary": {
            "crossEpochContinuityClaimed": False,
            "crossActorRepairAllowed": False,
            "coordinatesUsedForIdentity": False,
            "coordinatesUsedForContinuityConfidence": False,
            "drawAcknowledgementImpliesVisibility": False,
            "singleP18SnapshotImpliesTemporalContinuity": False,
            "unrecognizedGameplayStateInference": False,
        },
        "safety": dict(SAFETY),
        "realWofAcceptance": "NOT_RUN",
        "ownerVisualAcceptance": "NOT_RUN",
        "visibleProof": "NOT_PROVEN",
        "alphaLiveMoved": False,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    agg = report["aggregate"]
    lines = [
        "# Alpha V1 P24 Canonical Temporal Stability / Continuity Evidence",
        "",
        f"- Classification: **{agg['classification']}**",
        f"- Accepted samples: {agg['acceptedSampleCount']} / {agg['inputSampleCount']}",
        f"- READY / SUPPRESSED: {agg['readyCount']} / {agg['suppressedCount']}",
        f"- State transitions: {agg['stateTransitionCount']}",
        f"- One-sample READY / SUPPRESSED pulses: {agg['oneSampleReadyPulseCount']} / {agg['oneSampleSuppressedPulseCount']}",
        f"- Longest READY run: {agg['longestReadyRun']}",
        f"- Generation rollovers: {agg['generationRolloverCount']}",
        f"- Runtime / renderer epoch replacements: {agg['runtimeEpochReplacementCount']} / {agg['rendererEpochReplacementCount']}",
        f"- Duplicate/out-of-order rejects: {agg['duplicateOrOutOfOrderRejectionCount']}",
        f"- Accepted / stale draw acknowledgements: {agg['acceptedDrawAcknowledgementCount']} / {agg['staleDrawAcknowledgementRejectionCount']}",
        f"- Actor disappear / reappear: {agg['actorDisappearanceCount']} / {agg['actorReappearanceCount']}",
        "",
        "## Actor streams",
        "",
        "| Actor | Samples | READY | SUPPRESSED | Churn | Longest READY | Gen rollover | Runtime epoch | Renderer epoch | Disappear | Reappear | Classification |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for actor in report.get("actors", []):
        lines.append(
            "| {actor} | {sampleCount} | {readyCount} | {suppressedCount} | {stateTransitionCount} | {longestReadyRun} | {generationRolloverCount} | {runtimeEpochReplacementCount} | {rendererEpochReplacementCount} | {disappearanceCount} | {reappearanceCount} | {classification} |".format(**actor)
        )
    lines.extend([
        "",
        "## Fail-closed boundaries",
        "",
        "P24 never uses coordinates, row order, nearest-object relations, screenshots, projection, interpolation, or cached positions to repair identity or continuity. Epoch/generation boundaries revoke old evidence; P18 draw acknowledgement remains runtime evidence with `visibleProof=NOT_PROVEN` and is not promoted to visual proof.",
        "",
        "Real WOF and Owner visual acceptance were **NOT_RUN**. alpha-live was not moved.",
        "",
    ])
    return "\n".join(lines)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def write_report(report: Mapping[str, Any], output_root: str | os.PathLike[str]) -> tuple[Path, Path]:
    root = Path(output_root).expanduser()
    json_path = root / DEFAULT_JSON_NAME
    md_path = root / DEFAULT_MD_NAME
    json_text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    atomic_write(json_path, json_text)
    atomic_write(md_path, render_markdown(report))
    return json_path, md_path


def _load_json(path: str | os.PathLike[str]) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze passive canonical temporal continuity observations without spatial inference.")
    parser.add_argument("--input", required=True, help="P24 observation JSON/JSONL/bundle")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--p16-evidence", help="Optional P16 snapshot; binding/proof-boundary metadata only")
    parser.add_argument("--p18-evidence", action="append", default=[], help="Optional P18 snapshot; binding/proof-boundary metadata only; repeatable")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    bundle = load_observation_input(args.input)
    source = copy.deepcopy(bundle.get("sourceEvidence")) if isinstance(bundle.get("sourceEvidence"), Mapping) else {}
    if args.p16_evidence:
        source["p16"] = _load_json(args.p16_evidence)
    if args.p18_evidence:
        source["p18Snapshots"] = [_load_json(path) for path in args.p18_evidence]
    bundle["sourceEvidence"] = source
    report = analyze_bundle(bundle)
    json_path, md_path = write_report(report, args.output_root)
    print(json.dumps({
        "state": report["aggregate"]["classification"],
        "json": str(json_path),
        "markdown": str(md_path),
        "acceptedSampleCount": report["aggregate"]["acceptedSampleCount"],
        "rejectedSampleCount": len(report["rejections"]) + report["rejectionsTruncated"],
        "realWofAcceptance": "NOT_RUN",
        "alphaLiveMoved": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["aggregate"]["classification"] not in {"STALE_OR_MISMATCH", "INSUFFICIENT_EVIDENCE", "UNPROVEN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
