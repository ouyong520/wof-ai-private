from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence

SCHEMA = "wof-alpha-dynamic-actor-state-coverage-v1"
VERSION = 1
INPUT_SCHEMA = "wof-alpha-p22-cycle-bundle-v1"
P21_RECEIPT_SCHEMA = "wof-alpha-p21-prepromotion-staging-receipt-v1"
CANONICAL_COORDINATOR_SCHEMA = "wof-alpha-canonical-runtime-coordinator-v1"
CANONICAL_BRIDGE_SCHEMA = "wof-alpha-canonical-overlay-runtime-bridge-v1"
CANONICAL_TRANSPORT_SCHEMA = "wof-alpha-canonical-anchor-runtime-envelope-input-v1"
CANONICAL_ANCHOR_SCHEMA = "wof-render-object-anchor-v1"
P18_SCHEMA = "wof-alpha-canonical-draw-evidence-v1"
SEMANTIC_SCHEMA = "wof-alpha-v2"
SEMANTIC_RELEASE = "wof-alpha-rc3"
ACCEPTED_WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
NATIVE_WIDTH = 384
NATIVE_HEIGHT = 224
DEFAULT_LEDGER_LIMIT = 256
MAX_LEDGER_LIMIT = 2048
OUTPUT_JSON = "ALPHA_DYNAMIC_STATE_COVERAGE.json"
OUTPUT_MD = "ALPHA_DYNAMIC_STATE_COVERAGE.md"

STATUS_OBSERVED_PROVEN = "OBSERVED_PROVEN"
STATUS_OBSERVED_PARTIAL = "OBSERVED_PARTIAL"
STATUS_NOT_OBSERVED = "NOT_OBSERVED"
STATUS_UNPROVEN_SIGNAL = "UNPROVEN_SIGNAL"
STATUS_SUPPRESSED_SAFELY = "SUPPRESSED_SAFELY"
ALLOWED_MATRIX_STATUSES = frozenset({
    STATUS_OBSERVED_PROVEN,
    STATUS_OBSERVED_PARTIAL,
    STATUS_NOT_OBSERVED,
    STATUS_UNPROVEN_SIGNAL,
    STATUS_SUPPRESSED_SAFELY,
})
PLAYER_ACTORS = ("P1", "P2", "P3")
PLAYER_SET = frozenset(PLAYER_ACTORS)
ENEMY_RE = re.compile(r"^enemy-slot-(?:[0-9]|1[0-9])$")
TARGET_CODE_TO_PLAYER = {0: "P1", 4: "P2", 8: "P3"}
TARGET_PLAYER_TO_LABEL = {"P1": "1P", "P2": "2P", "P3": "3P"}
RARE_NAMED_STATES = ("HIT", "DOWN", "RECOVERY", "JUMP", "DEATH")
VISIBILITY_SUPPRESSION_REASONS = frozenset({
    "VISIBLE_BODY_BOUNDS_UNAVAILABLE", "OFFSCREEN", "ACTOR_OFFSCREEN",
    "BODY_OUTSIDE_NATIVE_SURFACE", "NO_VISIBLE_BODY_PARTS",
})
IDENTITY_SUPPRESSION_REASONS = frozenset({
    "AMBIGUOUS_ACTOR_ASSOCIATION", "ACTOR_ASSOCIATION_MISSING",
    "ACTOR_ASSOCIATION_UNPROVEN", "CONFLICTING_ACTOR_GENERATIONS",
    "DUPLICATE_ACTOR_ROWS", "STALE_AUTHORITY_OR_RENDERER_EPOCH",
    "STALE_AUTHORITY_OR_RUNTIME_EPOCH", "STALE_AUTHORITY_OR_WORLD_IDENTITY",
})
SAFETY = {
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "legacySpatialFallback": False,
    "screenshotProductionCoordinates": False,
    "worldProjectionProductionCoordinates": False,
    "guessedAddresses": False,
    "identityFromCoordinates": False,
    "visibleProof": "NOT_PROVEN",
}


class CoverageError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _actor_kind(actor: str) -> str | None:
    if actor in PLAYER_SET:
        return "player"
    if ENEMY_RE.fullmatch(actor):
        return "enemy"
    return None


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _safe(value: Mapping[str, Any], where: str) -> None:
    if value.get("readOnly") is not True or value.get("ramWrites") != 0 or value.get("inputInjection") is not False:
        raise CoverageError(f"{where} violates read-only safety boundary")


def _candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    source = candidate.get("sourceCommit")
    package = candidate.get("packageVersion")
    digest = candidate.get("candidateSha256") or candidate.get("contentSha256") or candidate.get("sha256")
    if not isinstance(source, str) or re.fullmatch(r"[0-9a-f]{40}", source) is None:
        raise CoverageError("exact candidate sourceCommit is required")
    if not isinstance(package, str) or not package:
        raise CoverageError("exact candidate packageVersion is required")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise CoverageError("exact candidate sha256 is required")
    out = {"sourceCommit": source, "packageVersion": package, "candidateSha256": digest}
    for key in ("candidatePath", "attestationSha256"):
        if isinstance(candidate.get(key), str):
            out[key] = candidate[key]
    return out


def candidate_from_p21_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(receipt, Mapping) or receipt.get("schema") != P21_RECEIPT_SCHEMA or receipt.get("version") != 1:
        raise CoverageError("P21 receipt schema/version mismatch")
    if receipt.get("alphaLiveMoved") is not False:
        raise CoverageError("P21 receipt reports alpha-live mutation")
    safety = receipt.get("safety")
    if not isinstance(safety, Mapping):
        raise CoverageError("P21 receipt safety missing")
    _safe(safety, "P21 receipt")
    if safety.get("legacySpatialFallback") is not False:
        raise CoverageError("P21 receipt legacy spatial fallback boundary invalid")
    raw = receipt.get("candidate")
    if not isinstance(raw, Mapping):
        raise CoverageError("P21 receipt candidate missing")
    return _candidate(raw)


def _identity(canonical: Mapping[str, Any]) -> dict[str, Any] | None:
    fields = {
        "worldSha256": canonical.get("worldSha256"),
        "pageTargetId": canonical.get("pageTargetId"),
        "authorityKey": canonical.get("authorityKey"),
        "runtimeEpoch": canonical.get("runtimeEpoch"),
        "rendererEpoch": canonical.get("rendererEpoch"),
    }
    if all(v is None for v in fields.values()):
        return None
    if fields["worldSha256"] != ACCEPTED_WORLD_SHA256:
        raise CoverageError("canonical status is not exact World 921031")
    if not isinstance(fields["pageTargetId"], str) or not fields["pageTargetId"]:
        raise CoverageError("canonical pageTargetId missing")
    if not isinstance(fields["authorityKey"], str) or not fields["authorityKey"]:
        raise CoverageError("canonical authorityKey missing")
    if not isinstance(fields["runtimeEpoch"], str) or len(fields["runtimeEpoch"]) < 16:
        raise CoverageError("canonical runtimeEpoch invalid")
    if fields["rendererEpoch"] is not None and (not isinstance(fields["rendererEpoch"], str) or len(fields["rendererEpoch"]) < 16):
        raise CoverageError("canonical rendererEpoch invalid")
    return fields


def _identity_key(identity: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(identity.get(k) for k in ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch"))


def _canonical_status(runtime_status: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(runtime_status, Mapping):
        raise CoverageError("runtime status must be an object")
    if runtime_status.get("schema") == CANONICAL_COORDINATOR_SCHEMA:
        canonical = dict(runtime_status)
    else:
        _safe(runtime_status, "AlphaRuntime status")
        if runtime_status.get("packageVersion") not in {None, candidate["packageVersion"]}:
            raise CoverageError("runtime packageVersion does not match exact candidate")
        raw = runtime_status.get("canonicalOverlay")
        if not isinstance(raw, Mapping):
            raise CoverageError("AlphaRuntime status missing canonicalOverlay")
        canonical = dict(raw)
    if canonical.get("schema") != CANONICAL_COORDINATOR_SCHEMA:
        raise CoverageError("canonical coordinator schema mismatch")
    _safe(canonical, "canonical coordinator")
    if canonical.get("legacySpatialFallback") is not False:
        raise CoverageError("canonical coordinator reports legacy spatial fallback")
    if canonical.get("positionAuthority") not in {None, CANONICAL_ANCHOR_SCHEMA}:
        raise CoverageError("canonical coordinator position authority mismatch")
    return canonical


def _bounds(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping):
        raise CoverageError("READY bodyBounds missing")
    try:
        l, t, r, b = (float(value[k]) for k in ("left", "top", "right", "bottom"))
    except (KeyError, TypeError, ValueError) as exc:
        raise CoverageError("bodyBounds malformed") from exc
    if not all(math.isfinite(v) for v in (l, t, r, b)) or not (0 <= l < r <= NATIVE_WIDTH and 0 <= t < b <= NATIVE_HEIGHT):
        raise CoverageError("bodyBounds outside native 384x224")
    return {"left": l, "top": t, "right": r, "bottom": b}


def _point(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping) or not _finite(value.get("x")) or not _finite(value.get("y")):
        raise CoverageError("READY anchor malformed")
    x, y = float(value["x"]), float(value["y"])
    if not (0 <= x <= NATIVE_WIDTH and 0 <= y <= NATIVE_HEIGHT):
        raise CoverageError("anchor outside native 384x224")
    return {"x": x, "y": y}


def _record(row: Mapping[str, Any], identity: Mapping[str, Any]) -> dict[str, Any]:
    actor, kind, generation, sample = row.get("actor"), row.get("kind"), row.get("generation"), row.get("sampleAt")
    if not isinstance(actor, str) or kind != _actor_kind(actor):
        raise CoverageError("canonical record actor/kind invalid")
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 0:
        raise CoverageError("canonical generation invalid")
    if not _finite(sample) or float(sample) < 0:
        raise CoverageError("canonical sampleAt invalid")
    for key in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch"):
        if row.get(key) != identity.get(key):
            raise CoverageError(f"canonical record {key} mismatch")
    anchor = row.get("canonicalAnchor")
    if not isinstance(anchor, Mapping) or anchor.get("schema") != CANONICAL_ANCHOR_SCHEMA:
        raise CoverageError("P10 canonical anchor missing")
    _safe(anchor, "P10 canonical anchor")
    if anchor.get("nativeWidth") != NATIVE_WIDTH or anchor.get("nativeHeight") != NATIVE_HEIGHT:
        raise CoverageError("native coordinate contract mismatch")
    state = anchor.get("state")
    if state == "READY":
        if anchor.get("actor") != actor or anchor.get("generation") != generation:
            raise CoverageError("READY actor/generation mismatch")
        for key in ("authorityKey", "runtimeEpoch", "rendererEpoch"):
            if anchor.get(key) != identity.get(key):
                raise CoverageError(f"READY anchor {key} mismatch")
        if anchor.get("worldSha256") is not None and anchor.get("worldSha256") != identity.get("worldSha256"):
            raise CoverageError("READY anchor world mismatch")
        point, bounds, reason = _point(anchor.get("anchor")), _bounds(anchor.get("bodyBounds")), None
    elif state == "SUPPRESSED":
        if isinstance(anchor.get("anchor"), Mapping) or isinstance(anchor.get("bodyBounds"), Mapping):
            raise CoverageError("SUPPRESSED anchor carried coordinates")
        point, bounds, reason = None, None, str(anchor.get("reason") or "SUPPRESSED")
    else:
        raise CoverageError("canonical anchor state invalid")
    return {
        "actor": actor, "kind": kind, "generation": generation, "sampleAt": float(sample),
        "canonicalState": state, "suppressionReason": reason, "anchor": point, "bodyBounds": bounds,
    }


def _records(canonical: Mapping[str, Any], identity: Mapping[str, Any]) -> list[dict[str, Any]]:
    bridge = canonical.get("bridge")
    if not isinstance(bridge, Mapping) or bridge.get("schema") != CANONICAL_BRIDGE_SCHEMA:
        raise CoverageError("canonical bridge missing")
    _safe(bridge, "canonical bridge")
    if bridge.get("legacyPositionFallback") is not False or bridge.get("positionAuthority") != CANONICAL_ANCHOR_SCHEMA:
        raise CoverageError("canonical bridge spatial boundary invalid")
    binding = bridge.get("authorityBinding")
    if not isinstance(binding, Mapping):
        if bridge.get("bound") is False and canonical.get("state") in {"SUPPRESSED", "WAITING"}:
            return []
        raise CoverageError("canonical bridge binding missing")
    for key in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch"):
        if binding.get(key) != identity.get(key):
            raise CoverageError(f"bridge binding {key} mismatch")
    payload = bridge.get("lastPayload")
    if payload is None:
        return []
    if not isinstance(payload, Mapping) or payload.get("schema") != CANONICAL_TRANSPORT_SCHEMA:
        raise CoverageError("canonical payload schema mismatch")
    pb = payload.get("authorityBinding")
    if not isinstance(pb, Mapping):
        raise CoverageError("canonical payload binding missing")
    for key in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch"):
        if pb.get(key) != identity.get(key):
            raise CoverageError(f"payload binding {key} mismatch")
    rows = payload.get("records")
    if not isinstance(rows, list):
        raise CoverageError("canonical records missing")
    return [_record(row, identity) for row in rows if isinstance(row, Mapping)]


def _draw(draw: Any, identity: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    if draw is None:
        return [], None
    if not isinstance(draw, Mapping) or draw.get("schema") != P18_SCHEMA or draw.get("version") != 1:
        raise CoverageError("P18 schema/version mismatch")
    _safe(draw, "P18 draw evidence")
    if draw.get("visibleProof") != "NOT_PROVEN":
        raise CoverageError("P18 visible-proof boundary invalid")
    safety = draw.get("safety")
    if not isinstance(safety, Mapping):
        raise CoverageError("P18 safety missing")
    _safe(safety, "P18 safety")
    if safety.get("legacySpatialFallback") is not False or safety.get("screenshotProductionCoordinates") is not False or safety.get("worldProjectionProductionCoordinates") is not False:
        raise CoverageError("P18 spatial boundary invalid")
    observed = draw.get("identity")
    if not isinstance(observed, Mapping):
        return [], "P18_IDENTITY_UNAVAILABLE"
    for key in ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch"):
        if observed.get(key) != identity.get(key):
            return [], f"P18_STALE_IDENTITY:{key}"
    evidence_generation = draw.get("evidenceGeneration")
    if not isinstance(evidence_generation, int) or isinstance(evidence_generation, bool) or evidence_generation < 1:
        raise CoverageError("P18 evidenceGeneration invalid")
    rows = draw.get("acknowledgements")
    if not isinstance(rows, list):
        raise CoverageError("P18 acknowledgements missing")
    clean, previous = [], -1
    for row in rows:
        if not isinstance(row, Mapping):
            raise CoverageError("P18 acknowledgement invalid")
        seq = row.get("sequence")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq <= previous:
            raise CoverageError("P18 acknowledgement sequence invalid")
        previous = seq
        if row.get("completed") is not True or row.get("coordinateAuthority") != "canonical-render-object-only" or row.get("visibleProof") != "NOT_PROVEN":
            raise CoverageError("P18 acknowledgement boundary invalid")
        authority = row.get("authority")
        if not isinstance(authority, Mapping):
            raise CoverageError("P18 acknowledgement authority missing")
        for key in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch"):
            if authority.get(key) != identity.get(key):
                raise CoverageError(f"P18 acknowledgement {key} mismatch")
        actor, generation = row.get("actor"), row.get("generation")
        sample_identity = row.get("sampleIdentity")
        sample_at = sample_identity.get("sampleAt") if isinstance(sample_identity, Mapping) else None
        clean.append({
            "sequence": seq,
            "evidenceGeneration": evidence_generation,
            "kind": row.get("kind"),
            "actor": actor if isinstance(actor, str) and _actor_kind(actor) else None,
            "generation": generation if isinstance(generation, int) and not isinstance(generation, bool) and generation >= 0 else None,
            "sampleAt": float(sample_at) if _finite(sample_at) else None,
            "label": row.get("label") if isinstance(row.get("label"), str) else None,
            "sourceId": row.get("sourceId") if isinstance(row.get("sourceId"), str) else None,
        })
    return clean, None


def _semantic(envelopes: Any, identity: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    if envelopes is None:
        return [], []
    if isinstance(envelopes, Mapping) or isinstance(envelopes, (str, bytes, bytearray)) or not isinstance(envelopes, Sequence):
        raise CoverageError("semantic envelopes must be a list")
    events, stale = [], []
    for raw in envelopes:
        if not isinstance(raw, Mapping) or raw.get("schema") != SEMANTIC_SCHEMA or raw.get("release") != SEMANTIC_RELEASE:
            raise CoverageError("semantic envelope schema/release mismatch")
        _safe(raw, "semantic envelope")
        if raw.get("runtimeEpoch") != identity.get("runtimeEpoch"):
            stale.append("SEMANTIC_STALE_RUNTIME_EPOCH")
            continue
        kind = raw.get("kind")
        if kind == "player-head-spatial":
            players = raw.get("players")
            if not isinstance(players, Mapping):
                raise CoverageError("player semantic players missing")
            sample = raw.get("sampleAt") if _finite(raw.get("sampleAt")) else raw.get("sentAt")
            for actor in PLAYER_ACTORS:
                row = players.get(actor)
                if isinstance(row, Mapping) and row.get("present") in {True, False}:
                    events.append({
                        "kind": "player-presence", "actor": actor, "present": bool(row["present"]),
                        "sampleAt": float(sample) if _finite(sample) else None,
                        "source": "wof-alpha-field-adapter-v1/player-head-spatial",
                    })
        elif kind == "enemy-target-markers":
            if raw.get("semanticProjectionIndependent") is not True:
                raise CoverageError("enemy target semantic is not projection-independent")
            markers = raw.get("markers")
            if not isinstance(markers, list):
                raise CoverageError("enemy target markers missing")
            for marker in markers:
                if not isinstance(marker, Mapping):
                    continue
                actor, code, target = marker.get("sourceId"), marker.get("target7E"), marker.get("target")
                expected = TARGET_CODE_TO_PLAYER.get(code) if isinstance(code, int) and not isinstance(code, bool) else None
                if isinstance(actor, str) and ENEMY_RE.fullmatch(actor) and expected is not None and target == expected:
                    sample = marker.get("sampleAt")
                    events.append({
                        "kind": "enemy-target", "actor": actor, "targetCode": code, "target": target,
                        "sampleAt": float(sample) if _finite(sample) else None,
                        "source": "wof-alpha-field-adapter-v1/enemy-target-markers",
                    })
    return events, stale


def _anchor_tuple(value: Mapping[str, Any] | None) -> tuple[float, float] | None:
    return (float(value["x"]), float(value["y"])) if isinstance(value, Mapping) else None


def _bounds_tuple(value: Mapping[str, Any] | None) -> tuple[float, float, float, float] | None:
    return tuple(float(value[k]) for k in ("left", "top", "right", "bottom")) if isinstance(value, Mapping) else None


def _changed(a: tuple[float, ...] | None, b: tuple[float, ...] | None, eps: float = 0.01) -> bool:
    return a is not None and b is not None and len(a) == len(b) and any(abs(x - y) > eps for x, y in zip(a, b))


def _matrix(mid: str, status: str, detail: str, sequences: Iterable[int] = ()) -> dict[str, Any]:
    if status not in ALLOWED_MATRIX_STATUSES:
        raise CoverageError(f"invalid matrix status {status}")
    return {"id": mid, "status": status, "detail": detail, "evidenceSequences": sorted({int(v) for v in sequences})}


@dataclass(frozen=True)
class _TrackKey:
    identity: tuple[Any, ...]
    actor: str
    generation: int


class DynamicActorStateCoverageRecorder:
    def __init__(self, candidate: Mapping[str, Any], *, ledger_limit: int = DEFAULT_LEDGER_LIMIT) -> None:
        self.candidate = _candidate(candidate)
        if not isinstance(ledger_limit, int) or isinstance(ledger_limit, bool) or not 1 <= ledger_limit <= MAX_LEDGER_LIMIT:
            raise CoverageError(f"ledger_limit must be 1..{MAX_LEDGER_LIMIT}")
        self.ledger_limit = ledger_limit
        self._cycles: list[dict[str, Any]] = []
        self._stale: list[dict[str, Any]] = []
        self._suppression: list[dict[str, Any]] = []
        self._active_identity: tuple[Any, ...] | None = None
        self._retired_identities: set[tuple[Any, ...]] = set()
        self._latest_generation: dict[tuple[tuple[Any, ...], str], int] = {}
        self._retired_generations: dict[tuple[tuple[Any, ...], str], set[int]] = {}
        self._seen_draw_ack: set[tuple[tuple[Any, ...], int, int]] = set()
        self._sequence = 0

    def _append(self, target: list[dict[str, Any]], row: dict[str, Any]) -> None:
        target.append(row)
        if len(target) > self.ledger_limit:
            del target[: len(target) - self.ledger_limit]

    def _stale_event(self, seq: int, reason: str, **detail: Any) -> None:
        self._append(self._stale, {"sequence": seq, "reason": reason, **_copy(detail)})

    def _suppress_event(self, seq: int, reason: str, **detail: Any) -> None:
        self._append(self._suppression, {"sequence": seq, "reason": reason, **_copy(detail)})

    def record_cycle(
        self,
        runtime_status: Mapping[str, Any],
        *,
        draw_evidence: Mapping[str, Any] | None = None,
        semantic_envelopes: Sequence[Mapping[str, Any]] | None = None,
        observed_at_ms: int | float | None = None,
    ) -> dict[str, Any]:
        canonical = _canonical_status(runtime_status, self.candidate)
        self._sequence += 1
        seq = self._sequence
        observed = seq if observed_at_ms is None else observed_at_ms
        if not _finite(observed) or float(observed) < 0:
            raise CoverageError("observed_at_ms invalid")
        identity = _identity(canonical)
        cycle: dict[str, Any] = {
            "sequence": seq,
            "observedAtMs": float(observed),
            "canonicalState": str(canonical.get("state") or "SUPPRESSED"),
            "canonicalReason": str(canonical.get("reason") or "UNKNOWN"),
            "identity": _copy(identity) if identity else None,
            "records": [], "semanticEvents": [], "drawLinks": [],
        }
        if identity is None or identity.get("rendererEpoch") is None:
            self._suppress_event(seq, cycle["canonicalReason"], scope="runtime", actor=None)
            self._append(self._cycles, cycle)
            return _copy(cycle)

        ident_key = _identity_key(identity)
        if self._active_identity is None:
            self._active_identity = ident_key
        elif ident_key != self._active_identity:
            if ident_key in self._retired_identities:
                self._stale_event(seq, "EPOCH_REENTRY_AFTER_REPLACEMENT", identity=identity)
                cycle["rejectedAsStaleIdentity"] = True
                self._append(self._cycles, cycle)
                return _copy(cycle)
            self._retired_identities.add(self._active_identity)
            cycle["identityReplacement"] = {"from": list(self._active_identity), "to": list(ident_key)}
            self._active_identity = ident_key

        records = _records(canonical, identity)
        semantic, semantic_stale = _semantic(semantic_envelopes, identity)
        cycle["semanticEvents"] = semantic
        for reason in semantic_stale:
            self._stale_event(seq, reason, identity=identity)
        draw_rows, draw_stale = _draw(draw_evidence, identity)
        if draw_stale:
            self._stale_event(seq, draw_stale, identity=identity)
            draw_rows = []

        accepted: list[dict[str, Any]] = []
        for record in records:
            actor, generation = record["actor"], record["generation"]
            actor_key = (ident_key, actor)
            previous = self._latest_generation.get(actor_key)
            retired = self._retired_generations.setdefault(actor_key, set())
            if previous is None:
                self._latest_generation[actor_key] = generation
            elif generation != previous:
                if generation in retired:
                    if record["canonicalState"] == "READY":
                        self._stale_event(seq, "STALE_ACTOR_GENERATION_AFTER_REPLACEMENT", actor=actor, generation=generation, currentGeneration=previous, identity=identity)
                        continue
                    self._suppress_event(seq, record["suppressionReason"] or "STALE_GENERATION_SUPPRESSED", actor=actor, generation=generation, identity=identity)
                else:
                    retired.add(previous)
                    self._latest_generation[actor_key] = generation
                    record["generationReplacementFrom"] = previous
            if record["canonicalState"] == "SUPPRESSED":
                self._suppress_event(seq, record["suppressionReason"] or "SUPPRESSED", actor=actor, generation=generation, identity=identity)
            accepted.append(record)

        for record in accepted:
            for ack in draw_rows:
                ack_key = (ident_key, int(ack["evidenceGeneration"]), int(ack["sequence"]))
                if ack_key in self._seen_draw_ack:
                    continue
                if ack.get("actor") == record["actor"] and ack.get("generation") == record["generation"] and ack.get("sampleAt") is not None and abs(float(ack["sampleAt"]) - float(record["sampleAt"])) <= 0.001:
                    cycle["drawLinks"].append({
                        "ackSequence": ack["sequence"], "evidenceGeneration": ack["evidenceGeneration"],
                        "kind": ack.get("kind"), "actor": record["actor"], "generation": record["generation"],
                        "sampleAt": record["sampleAt"], "label": ack.get("label"), "sourceId": ack.get("sourceId"),
                    })
                    self._seen_draw_ack.add(ack_key)
        cycle["records"] = accepted
        self._append(self._cycles, cycle)
        return _copy(cycle)

    def _all_records(self) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        return [(cycle, record) for cycle in self._cycles for record in cycle.get("records") or []]

    def _tracks(self) -> list[dict[str, Any]]:
        grouped: dict[_TrackKey, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
        for cycle, record in self._all_records():
            identity = cycle.get("identity")
            if isinstance(identity, Mapping):
                key = _TrackKey(_identity_key(identity), record["actor"], record["generation"])
                grouped.setdefault(key, []).append((cycle, record))
        tracks = []
        for key in sorted(grouped, key=lambda k: (str(k.identity), k.actor, k.generation)):
            rows = sorted(grouped[key], key=lambda item: item[0]["sequence"])
            ready = [(c, r) for c, r in rows if r["canonicalState"] == "READY"]
            suppressed = [(c, r) for c, r in rows if r["canonicalState"] == "SUPPRESSED"]
            moves, body_changes, vertical = [], [], []
            for (pc, pr), (cc, cr) in zip(ready, ready[1:]):
                pa, ca = _anchor_tuple(pr.get("anchor")), _anchor_tuple(cr.get("anchor"))
                pb, cb = _bounds_tuple(pr.get("bodyBounds")), _bounds_tuple(cr.get("bodyBounds"))
                if _changed(pa, ca): moves.append(cc["sequence"])
                if _changed(pb, cb): body_changes.append(cc["sequence"])
                if pa is not None and ca is not None and abs(pa[1] - ca[1]) > 0.01: vertical.append(cc["sequence"])
            reentries, waiting = [], False
            for cycle, record in rows:
                if record["canonicalState"] == "SUPPRESSED" and record.get("suppressionReason") in VISIBILITY_SUPPRESSION_REASONS:
                    waiting = True
                elif waiting and record["canonicalState"] == "READY":
                    reentries.append(cycle["sequence"]); waiting = False
            links = [link for cycle, _ in rows for link in cycle.get("drawLinks") or [] if link.get("actor") == key.actor and link.get("generation") == key.generation]
            tracks.append({
                "actor": key.actor, "kind": _actor_kind(key.actor), "generation": key.generation,
                "identity": {"worldSha256": key.identity[0], "pageTargetId": key.identity[1], "authorityKey": key.identity[2], "runtimeEpoch": key.identity[3], "rendererEpoch": key.identity[4]},
                "firstSequence": rows[0][0]["sequence"], "lastSequence": rows[-1][0]["sequence"],
                "sampleCount": len(rows), "readySampleCount": len(ready), "suppressedSampleCount": len(suppressed),
                "movement": {"observed": bool(moves), "changeSequences": moves},
                "bodyGeometryChange": {"observed": bool(body_changes), "changeSequences": body_changes},
                "genericVerticalMovement": {"observed": bool(vertical), "changeSequences": vertical, "namedJumpState": "UNPROVEN_SIGNAL"},
                "visibilitySuppressionReentry": {"observed": bool(reentries), "reentrySequences": reentries},
                "drawAcknowledgementCount": len(links),
                "drawAcknowledgementSequences": sorted({int(v["ackSequence"]) for v in links}),
            })
        return tracks

    def _semantic_events(self, kind: str | None = None) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        return [(cycle, event) for cycle in self._cycles for event in cycle.get("semanticEvents") or [] if kind is None or event.get("kind") == kind]

    def _presence_matrix(self) -> list[dict[str, Any]]:
        events = self._semantic_events("player-presence")
        out = []
        for actor in PLAYER_ACTORS:
            rows = [(c, e) for c, e in events if e.get("actor") == actor]
            states, seqs = [bool(e["present"]) for _, e in rows], [c["sequence"] for c, _ in rows]
            if actor == "P1":
                out.append(_matrix("player.P1_active", STATUS_OBSERVED_PROVEN if any(states) else STATUS_NOT_OBSERVED, "Exact lifecycle semantic observed P1 active; spatial fields were ignored." if any(states) else "No exact P1 active lifecycle semantic captured.", seqs))
            else:
                joined = any(a is False and b is True for a, b in zip(states, states[1:]))
                left = any(a is True and b is False for a, b in zip(states, states[1:]))
                out.append(_matrix(f"player.{actor}_join", STATUS_OBSERVED_PROVEN if joined else (STATUS_OBSERVED_PARTIAL if any(states) else STATUS_NOT_OBSERVED), "Exact inactive->active transition observed." if joined else ("Actor observed active but join edge not captured." if any(states) else "No join edge observed."), seqs))
                out.append(_matrix(f"player.{actor}_leave", STATUS_OBSERVED_PROVEN if left else STATUS_NOT_OBSERVED, "Exact active->inactive transition observed." if left else "No leave edge observed.", seqs))
        identity_suppressed = [e for e in self._suppression if e.get("reason") in IDENTITY_SUPPRESSION_REASONS]
        out.append(_matrix("player.identity_contradiction_or_ambiguity", STATUS_SUPPRESSED_SAFELY if identity_suppressed else STATUS_NOT_OBSERVED, "Ambiguous/conflicting identity was suppressed without coordinates." if identity_suppressed else "No contradictory identity event observed.", (e["sequence"] for e in identity_suppressed)))
        return out

    def _movement_matrix(self, tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        p1_moves = [t for t in tracks if t["actor"] == "P1" and t["movement"]["observed"]]
        p1_body = [t for t in tracks if t["actor"] == "P1" and t["bodyGeometryChange"]["observed"]]
        vertical = [t for t in tracks if t["genericVerticalMovement"]["observed"]]
        reentries = [t for t in tracks if t["visibilitySuppressionReentry"]["observed"]]
        return [
            _matrix("movement.P1_same_generation_anchor_change", STATUS_OBSERVED_PROVEN if p1_moves else STATUS_NOT_OBSERVED, "P1 P10 anchor changed inside the same actor/generation track." if p1_moves else "No same-generation P1 anchor movement captured.", (s for t in p1_moves for s in t["movement"]["changeSequences"])),
            _matrix("animation.P1_renderer_body_geometry_change", STATUS_OBSERVED_PROVEN if p1_body else STATUS_NOT_OBSERVED, "P1 renderer-qualified P10 bodyBounds changed in the same generation." if p1_body else "No same-generation P1 bodyBounds change captured.", (s for t in p1_body for s in t["bodyGeometryChange"]["changeSequences"])),
            _matrix("vertical.generic_canonical_movement", STATUS_OBSERVED_PARTIAL if vertical else STATUS_NOT_OBSERVED, "Generic canonical vertical movement observed; not renamed JUMP." if vertical else "No generic vertical canonical movement captured.", (s for t in vertical for s in t["genericVerticalMovement"]["changeSequences"])),
            _matrix("visibility.offscreen_suppression_reentry", STATUS_OBSERVED_PROVEN if reentries else STATUS_NOT_OBSERVED, "Explicit visibility/body suppression followed by READY on the same actor/generation." if reentries else "No explicit visibility suppression->reentry captured.", (s for t in reentries for s in t["visibilitySuppressionReentry"]["reentrySequences"])),
        ]

    def _generation_matrix(self) -> list[dict[str, Any]]:
        replacements = [(cycle["sequence"], record) for cycle in self._cycles for record in cycle.get("records") or [] if "generationReplacementFrom" in record]
        player = [(s, r) for s, r in replacements if r.get("kind") == "player"]
        enemy = [(s, r) for s, r in replacements if r.get("kind") == "enemy"]
        stale = [e for e in self._stale if e.get("reason") == "STALE_ACTOR_GENERATION_AFTER_REPLACEMENT"]
        return [
            _matrix("generation.player_rebuild", STATUS_OBSERVED_PROVEN if player else STATUS_NOT_OBSERVED, "Player generation changed; a fresh generation track was opened." if player else "No player generation rebuild observed.", (s for s, _ in player)),
            _matrix("generation.enemy_rebuild", STATUS_OBSERVED_PROVEN if enemy else STATUS_NOT_OBSERVED, "Enemy generation changed; a fresh generation track was opened." if enemy else "No enemy generation rebuild observed.", (s for s, _ in enemy)),
            _matrix("generation.stale_old_generation_ready", STATUS_SUPPRESSED_SAFELY if stale else STATUS_NOT_OBSERVED, "READY evidence from a retired generation was rejected." if stale else "No stale retired-generation READY evidence presented.", (e["sequence"] for e in stale)),
        ]

    def _enemy_matrix(self, tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        target_events = self._semantic_events("enemy-target")
        by_actor: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
        for cycle, event in target_events:
            by_actor.setdefault(event["actor"], []).append((cycle, event))
        switches = []
        for rows in by_actor.values():
            last = None
            for cycle, event in sorted(rows, key=lambda x: x[0]["sequence"]):
                target = event["target"]
                if last is not None and target != last:
                    switches.append(cycle["sequence"])
                last = target
        matching, mismatches = [], []
        for cycle in self._cycles:
            target = {e["actor"]: e["target"] for e in cycle.get("semanticEvents") or [] if e.get("kind") == "enemy-target"}
            for link in cycle.get("drawLinks") or []:
                actor = link.get("actor")
                if link.get("kind") != "enemy-target-label" or not isinstance(actor, str) or ENEMY_RE.fullmatch(actor) is None:
                    continue
                wanted = target.get(actor)
                if wanted is not None and link.get("label") == TARGET_PLAYER_TO_LABEL.get(wanted): matching.append(cycle["sequence"])
                elif wanted is not None: mismatches.append(cycle["sequence"])
        enemy_tracks = [t for t in tracks if t["kind"] == "enemy"]
        seqs = sorted({c["sequence"] for c, _ in target_events})
        if target_events:
            presence_status, presence_detail = STATUS_OBSERVED_PROVEN, "Projection-independent exact enemy target semantic observed; this proves presence/target, not the precise spawn edge."
        elif enemy_tracks:
            presence_status, presence_detail = STATUS_OBSERVED_PARTIAL, "Canonical enemy actor track observed without projection-independent target semantic."
        else:
            presence_status, presence_detail = STATUS_NOT_OBSERVED, "No enemy actor/target evidence captured."
        if matching and not mismatches:
            continuity_status = STATUS_OBSERVED_PROVEN if len(matching) >= 2 else STATUS_OBSERVED_PARTIAL
            continuity_detail = "Current enemy actor/generation draw acknowledgement matched exact 0/4/8 target semantic and 1P/2P/3P label."
        elif mismatches:
            continuity_status, continuity_detail = STATUS_UNPROVEN_SIGNAL, "Enemy target semantic and label acknowledgement disagreed; no continuity PASS granted."
        else:
            continuity_status, continuity_detail = STATUS_NOT_OBSERVED, "No same-cycle target semantic + current-generation label acknowledgement linkage captured."
        return [
            _matrix("enemy.semantic_presence", presence_status, presence_detail, seqs),
            _matrix("enemy.spawn_edge", STATUS_OBSERVED_PARTIAL if target_events else STATUS_NOT_OBSERVED, "Enemy presence observed, but first sighting is not promoted to an exact spawn edge." if target_events else "No enemy spawn edge observed.", seqs[:1]),
            _matrix("enemy.disappear_edge", STATUS_NOT_OBSERVED, "Later absence is not sufficient to name disappearance without an explicit lifecycle signal."),
            _matrix("enemy.target_switch_0_4_8", STATUS_OBSERVED_PROVEN if switches else STATUS_NOT_OBSERVED, "Same enemy slot changed exact target semantic among 0/4/8 -> P1/P2/P3." if switches else "No exact target switch observed.", switches),
            _matrix("enemy.target_label_current_generation_continuity", continuity_status, continuity_detail, matching + mismatches),
        ]

    def _replacement_matrix(self) -> list[dict[str, Any]]:
        replacements = [c for c in self._cycles if isinstance(c.get("identityReplacement"), Mapping)]
        stale = [e for e in self._stale if str(e.get("reason", "")).startswith("P18_STALE_IDENTITY") or e.get("reason") == "EPOCH_REENTRY_AFTER_REPLACEMENT"]
        return [
            _matrix("runtime.renderer_or_runtime_replacement", STATUS_OBSERVED_PROVEN if replacements else STATUS_NOT_OBSERVED, "Authority/runtime/renderer identity changed; prior identity retired and fresh track namespace opened." if replacements else "No runtime/renderer replacement observed.", (c["sequence"] for c in replacements)),
            _matrix("runtime.stale_cross_epoch_evidence", STATUS_SUPPRESSED_SAFELY if stale else STATUS_NOT_OBSERVED, "Cross-epoch stale evidence was rejected and never merged." if stale else "No stale cross-epoch evidence presented.", (e["sequence"] for e in stale)),
        ]

    def build_report(self, *, generated_at_utc: str | None = None) -> dict[str, Any]:
        tracks = self._tracks()
        matrix = self._presence_matrix() + self._movement_matrix(tracks) + self._generation_matrix() + self._enemy_matrix(tracks) + self._replacement_matrix()
        for rare in RARE_NAMED_STATES:
            matrix.append(_matrix(f"named_state.{rare}", STATUS_UNPROVEN_SIGNAL, f"No maintained exact semantic classifier for {rare} is consumed; geometry/motion is not renamed {rare}."))
        by_id = {row["id"]: row for row in matrix}
        enemies = by_id["enemy.semantic_presence"]["status"] in {STATUS_OBSERVED_PROVEN, STATUS_OBSERVED_PARTIAL}
        requirements = [
            {"id": "core.P1_move", "required": True, "status": by_id["movement.P1_same_generation_anchor_change"]["status"], "sourceMatrixId": "movement.P1_same_generation_anchor_change"},
            {"id": "core.P1_body_geometry_change", "required": True, "status": by_id["animation.P1_renderer_body_geometry_change"]["status"], "sourceMatrixId": "animation.P1_renderer_body_geometry_change"},
            {"id": "core.enemy_target_label_continuity_when_enemy_present", "required": enemies, "status": by_id["enemy.target_label_current_generation_continuity"]["status"], "sourceMatrixId": "enemy.target_label_current_generation_continuity"},
        ]
        core_ready = all(not req["required"] or req["status"] == STATUS_OBSERVED_PROVEN for req in requirements)
        gaps = [{"id": row["id"], "status": row["status"], "detail": row["detail"]} for row in matrix if row["status"] in {STATUS_NOT_OBSERVED, STATUS_UNPROVEN_SIGNAL, STATUS_OBSERVED_PARTIAL}]
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "generatedAtUtc": generated_at_utc or _utc_now(),
            "candidate": _copy(self.candidate),
            "evidence": {"cycleCount": len(self._cycles), "ledgerLimit": self.ledger_limit, "bounded": True, "cycles": _copy(self._cycles)},
            "tracks": tracks,
            "coverageMatrix": matrix,
            "coreAcceptance": {
                "state": "CORE_COVERAGE_READY" if core_ready else "CORE_COVERAGE_INCOMPLETE",
                "requirements": requirements,
                "rareStatesRequired": False,
                "detail": "Rare named states do not block the small core; missing/unsafe signals remain explicit gaps rather than invented PASS.",
            },
            "gaps": gaps,
            "staleEvidence": _copy(self._stale),
            "suppressionEvidence": _copy(self._suppression),
            "drawLinkage": {
                "linkedAcknowledgementCount": sum(len(c.get("drawLinks") or []) for c in self._cycles),
                "proofBoundary": "P18 acknowledgement proves maintained primitive execution only; it is not visible correctness.",
            },
            "invariants": {
                "identityNeverDerivedFromCoordinates": True,
                "nativeSurface384x224Only": True,
                "legacyScreenshotProjectionPositionUsed": False,
                "targetOrPresenceAuthorizedPosition": False,
                "crossEpochEvidenceMerged": False,
                "retiredGenerationReadyAccepted": False,
                "drawAcknowledgementTreatedAsVisibleProof": False,
                "rareNamedStatesGuessed": False,
                "deterministicFixedInput": True,
            },
            "realWofAcceptance": "NOT_RUN",
            "ownerVisualAcceptance": "NOT_RUN",
            "visibleProof": "NOT_PROVEN",
            "safety": dict(SAFETY),
        }


def render_markdown(report: Mapping[str, Any]) -> str:
    core = report.get("coreAcceptance") if isinstance(report.get("coreAcceptance"), Mapping) else {}
    matrix = report.get("coverageMatrix") if isinstance(report.get("coverageMatrix"), list) else []
    candidate = report.get("candidate") if isinstance(report.get("candidate"), Mapping) else {}
    lines = [
        "# Alpha V1 P22 Dynamic Actor State Coverage", "",
        f"- Candidate: `{candidate.get('sourceCommit')}` / `{candidate.get('packageVersion')}`",
        f"- Core automatic coverage: **{core.get('state')}**",
        f"- Real WOF acceptance: **{report.get('realWofAcceptance')}**",
        f"- Owner visual acceptance: **{report.get('ownerVisualAcceptance')}**",
        f"- Visible proof: **{report.get('visibleProof')}**", "",
        "## Coverage Matrix", "", "| Coverage | Status | Evidence |", "|---|---|---|",
    ]
    for row in matrix:
        detail = str(row.get("detail") or "").replace("|", "\\|").replace("\n", " ")
        seqs = ",".join(str(v) for v in row.get("evidenceSequences") or []) or "-"
        lines.append(f"| `{row.get('id')}` | **{row.get('status')}** | seq={seqs}; {detail} |")
    lines += ["", "## Core Acceptance", ""]
    for req in core.get("requirements") or []:
        lines.append(f"- `{req.get('id')}` — **{req.get('status')}** ({'required' if req.get('required') else 'not-required-this-run'})")
    lines += [
        "", "## Fail-Closed Boundary", "",
        "- Coordinates/body bounds are accepted only from P10 `wof-render-object-anchor-v1` READY records on native 384x224.",
        "- P2/P3 presence and enemy target 0/4/8 semantics use maintained field-adapter semantics only; world/projection coordinates are ignored.",
        "- Stale runtime/renderer identities and retired generations are never merged into current tracks.",
        "- P18 draw acknowledgement is primitive-execution evidence only; it never becomes visible PASS.",
        "- HIT/DOWN/RECOVERY/JUMP/DEATH remain `UNPROVEN_SIGNAL` without a maintained exact semantic classifier.",
        "", "## Gaps", "",
    ]
    gaps = report.get("gaps") if isinstance(report.get("gaps"), list) else []
    lines.extend([f"- `{g.get('id')}` — **{g.get('status')}**: {g.get('detail')}" for g in gaps] or ["- None in the bounded automatic matrix."])
    lines += ["", "## Safety", "", "Read-only; RAM writes 0; input injection false; no guessed addresses; no screenshot/world-projection production coordinates; no identity from coordinates; alpha-live is not touched by P22.", ""]
    return "\n".join(lines)


def atomic_write_outputs(output_dir: Path, report: Mapping[str, Any]) -> tuple[Path, Path]:
    output_dir = Path(output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = ((output_dir / OUTPUT_JSON, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"), (output_dir / OUTPUT_MD, render_markdown(report)))
    for path, data in outputs:
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(output_dir))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(data); handle.flush(); os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name): os.unlink(temp_name)
    return outputs[0][0], outputs[1][0]


def analyze_bundle(bundle: Mapping[str, Any], *, ledger_limit: int = DEFAULT_LEDGER_LIMIT, generated_at_utc: str | None = None) -> dict[str, Any]:
    if not isinstance(bundle, Mapping) or bundle.get("schema") != INPUT_SCHEMA or bundle.get("version") != 1:
        raise CoverageError("P22 input bundle schema/version mismatch")
    receipt = bundle.get("p21Receipt")
    if not isinstance(receipt, Mapping):
        raise CoverageError("P22 input requires exact P21 receipt")
    recorder = DynamicActorStateCoverageRecorder(candidate_from_p21_receipt(receipt), ledger_limit=ledger_limit)
    cycles = bundle.get("cycles")
    if not isinstance(cycles, list):
        raise CoverageError("P22 cycles must be a list")
    for cycle in cycles:
        if not isinstance(cycle, Mapping) or not isinstance(cycle.get("runtimeStatus"), Mapping):
            raise CoverageError("P22 cycle runtimeStatus missing")
        recorder.record_cycle(
            cycle["runtimeStatus"],
            draw_evidence=cycle.get("drawEvidence") if isinstance(cycle.get("drawEvidence"), Mapping) else None,
            semantic_envelopes=cycle.get("semanticEnvelopes") if isinstance(cycle.get("semanticEnvelopes"), list) else None,
            observed_at_ms=cycle.get("observedAtMs"),
        )
    return recorder.build_report(generated_at_utc=generated_at_utc)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Passive fail-closed Alpha P22 dynamic actor state coverage analyzer.")
    p.add_argument("--input", type=Path, required=True, help="P21/P17 same-session canonical evidence bundle; no manual coordinates")
    p.add_argument("--output-dir", type=Path, default=Path.home() / "Documents" / "WOF_RESULTS")
    p.add_argument("--ledger-limit", type=int, default=DEFAULT_LEDGER_LIMIT)
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        bundle = json.loads(args.input.expanduser().read_text(encoding="utf-8-sig"))
        report = analyze_bundle(bundle, ledger_limit=args.ledger_limit)
        json_path, md_path = atomic_write_outputs(args.output_dir, report)
    except (OSError, ValueError, CoverageError) as exc:
        print(f"P22_FAIL_CLOSED: {type(exc).__name__}: {exc}")
        return 2
    print(f"state={report['coreAcceptance']['state']}")
    print(f"visibleProof={report['visibleProof']}")
    print(f"json={json_path}")
    print(f"markdown={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
