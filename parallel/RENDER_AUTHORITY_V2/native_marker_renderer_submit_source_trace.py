from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from native_player_marker_anchor_qualification import (
    EVIDENCE_SCHEMA,
    ExpectedBinding,
    QUALIFIED,
    qualify_native_player_marker,
)

SOURCE_SCHEMA = "wof-native-marker-renderer-submit-source-v1"
EVENT_SCHEMA = "wof-native-marker-renderer-submit-event-v1"
BUNDLE_SCHEMA = "wof-native-marker-renderer-submit-source-trace-v1"
RESULT_SCHEMA = "wof-native-marker-renderer-submit-proof-producer-v1"
BLOCKER = "NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN"
NATIVE_WIDTH = 384
NATIVE_HEIGHT = 224
MIN_DIRECT_SAMPLES = 3
MAX_EVENTS = 96
_ALLOWED_PLAYERS = frozenset({"P1", "P2", "P3"})
_LABELS = {"P1": "1P", "P2": "2P", "P3": "3P"}
_ALLOWED_DERIVATIONS = frozenset({"SOURCE_TRACED_POINTER", "DIRECT_RENDER_HOOK", "EXPORTED_RENDERER_POINTER"})


@dataclass(frozen=True)
class ProducerBinding:
    runtime_epoch: str
    renderer_epoch: str
    authority_key: str

    def valid(self) -> bool:
        return all(isinstance(v, str) and bool(v) for v in (
            self.runtime_epoch, self.renderer_epoch, self.authority_key
        ))

    def p32(self) -> ExpectedBinding:
        return ExpectedBinding(self.runtime_epoch, self.renderer_epoch, self.authority_key)


def _blocked(reason: str, *, details: Iterable[str] = ()) -> dict[str, Any]:
    return {
        "schema": RESULT_SCHEMA,
        "state": "BLOCKED",
        "reason": reason,
        "details": sorted(set(str(v) for v in details if str(v))),
        "blocker": BLOCKER,
        "evidence": None,
        "qualification": None,
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "ownerSelectionRequired": False,
        "manualSeedRequired": False,
    }


def _rejected(reason: str, *, details: Iterable[str] = ()) -> dict[str, Any]:
    out = _blocked(reason, details=details)
    out["state"] = "REJECTED"
    return out


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _source_errors(source: Any) -> list[str]:
    if not isinstance(source, dict):
        return ["DIRECT_SOURCE_MISSING"]
    errors: list[str] = []
    if source.get("schema") != SOURCE_SCHEMA:
        errors.append("DIRECT_SOURCE_SCHEMA_INVALID")
    if source.get("derivationKind") not in _ALLOWED_DERIVATIONS:
        errors.append("DIRECT_SOURCE_DERIVATION_UNQUALIFIED")
    if source.get("guessed") is not False:
        errors.append("DIRECT_SOURCE_GUESSED_OR_UNSPECIFIED")
    if source.get("displayedFrameCausalLink") is not True:
        errors.append("DISPLAYED_FRAME_CAUSAL_LINK_MISSING")
    if source.get("coordinateAuthority") != "NATIVE_RENDERER_OBJECT_384X224":
        errors.append("NATIVE_COORDINATE_AUTHORITY_MISSING")
    for field in (
        "screenshotCoordinatesUsed",
        "ocrCoordinatesUsed",
        "templateCoordinatesUsed",
        "worldProjectionCoordinatesUsed",
    ):
        if source.get(field) is not False:
            errors.append(f"{field.upper()}_FORBIDDEN")
    trace = source.get("sourceTrace")
    if not isinstance(trace, list) or len(trace) < 2 or any(not _nonempty(v) for v in trace):
        errors.append("SOURCE_TRACE_INCOMPLETE")
    for field in ("instrumentationId", "hookSite"):
        if not _nonempty(source.get(field)):
            errors.append(f"DIRECT_SOURCE_{field.upper()}_MISSING")
    if source.get("readOnly") is not True or source.get("ramWrites") != 0 or source.get("inputInjection") is not False:
        errors.append("DIRECT_SOURCE_SAFETY_BOUNDARY_INVALID")
    if source.get("ownerSelectionRequired") is not False:
        errors.append("OWNER_SELECTION_FORBIDDEN")
    if source.get("manualSeedRequired") is not False:
        errors.append("MANUAL_SEED_FORBIDDEN")
    return errors


def _event_binding_errors(event: dict[str, Any], binding: ProducerBinding) -> list[str]:
    errors: list[str] = []
    if event.get("runtimeEpoch") != binding.runtime_epoch:
        errors.append("RUNTIME_EPOCH_MISMATCH")
    if event.get("rendererEpoch") != binding.renderer_epoch:
        errors.append("RENDERER_EPOCH_MISMATCH")
    if event.get("authorityKey") != binding.authority_key:
        errors.append("AUTHORITY_KEY_MISMATCH")
    return errors


def _event_matches(event: Any, player: str, generation: int) -> bool:
    if not isinstance(event, dict):
        return False
    association = event.get("actorAssociation")
    return (
        isinstance(association, dict)
        and association.get("player") == player
        and association.get("generation") == generation
    )


def produce_native_marker_proof(
    bundle: dict[str, Any],
    *,
    player: str,
    generation: int,
    binding: ProducerBinding,
) -> dict[str, Any]:
    """Convert only explicit source-traced renderer-submit events into the existing P32 contract.

    Arrival order, timing, structural HEAP, screenshots, OCR, templates, nearest-object
    and world-projection data are never consulted for marker identity or coordinates.
    """
    if not isinstance(binding, ProducerBinding) or not binding.valid():
        return _rejected("EXPECTED_BINDING_INVALID")
    if player not in _ALLOWED_PLAYERS or type(generation) is not int or generation < 0:
        return _rejected("PLAYER_OR_GENERATION_INVALID")
    if not isinstance(bundle, dict) or bundle.get("schema") != BUNDLE_SCHEMA:
        return _blocked("SOURCE_TRACE_BUNDLE_SCHEMA_INVALID")
    if bundle.get("readOnly") is not True or bundle.get("ramWrites") != 0 or bundle.get("inputInjection") is not False:
        return _rejected("SOURCE_TRACE_SAFETY_BOUNDARY_INVALID")
    if bundle.get("ownerSelectionRequired") is not False or bundle.get("manualSeedRequired") is not False:
        return _rejected("ZERO_CLICK_CONTRACT_VIOLATED")
    source = bundle.get("source")
    source_errors = _source_errors(source)
    if source_errors:
        return _blocked("DIRECT_DISPLAYED_FRAME_SOURCE_UNAVAILABLE", details=source_errors)

    events = bundle.get("events")
    if not isinstance(events, list):
        return _blocked("DIRECT_RENDERER_SUBMIT_EVENTS_MISSING")
    if len(events) > MAX_EVENTS:
        return _rejected("BOUNDED_EVENT_LIMIT_EXCEEDED")

    matching = [event for event in events if _event_matches(event, player, generation)]
    if len(matching) < MIN_DIRECT_SAMPLES:
        return _blocked(
            "DIRECT_FRAME_SAMPLE_COUNT_INSUFFICIENT",
            details=[f"have={len(matching)}", f"need={MIN_DIRECT_SAMPLES}"],
        )

    validated: list[dict[str, Any]] = []
    event_errors: list[str] = []
    for index, event in enumerate(matching):
        if not isinstance(event, dict) or event.get("schema") != EVENT_SCHEMA:
            event_errors.append(f"EVENT_{index}_SCHEMA_INVALID")
            continue
        for error in _event_binding_errors(event, binding):
            event_errors.append(f"EVENT_{index}_{error}")
        if event.get("displayedFrameCausalLink") is not True:
            event_errors.append(f"EVENT_{index}_DISPLAYED_FRAME_CAUSAL_LINK_MISSING")
        if event.get("coordinateAuthority") != "NATIVE_RENDERER_OBJECT_384X224":
            event_errors.append(f"EVENT_{index}_NATIVE_COORDINATE_AUTHORITY_MISSING")
        if event.get("guessed") is not False:
            event_errors.append(f"EVENT_{index}_GUESSED_OR_UNSPECIFIED")
        association = event.get("actorAssociation")
        if not isinstance(association, dict):
            event_errors.append(f"EVENT_{index}_ACTOR_ASSOCIATION_MISSING")
        else:
            if association.get("player") != player or association.get("generation") != generation:
                event_errors.append(f"EVENT_{index}_ACTOR_GENERATION_MISMATCH")
            if association.get("explicit") is not True or association.get("generationBound") is not True:
                event_errors.append(f"EVENT_{index}_ACTOR_ASSOCIATION_NOT_EXPLICIT")
            if association.get("ambiguous") is not False or association.get("candidateCount") != 1:
                event_errors.append(f"EVENT_{index}_ACTOR_ASSOCIATION_AMBIGUOUS")
            if association.get("guessed") is not False:
                event_errors.append(f"EVENT_{index}_ACTOR_ASSOCIATION_GUESSED")
        marker = event.get("marker")
        if not isinstance(marker, dict):
            event_errors.append(f"EVENT_{index}_MARKER_MISSING")
            continue
        if marker.get("player") != player or marker.get("generation") != generation:
            event_errors.append(f"EVENT_{index}_MARKER_ACTOR_GENERATION_MISMATCH")
        if marker.get("labelSemantic") != _LABELS[player]:
            event_errors.append(f"EVENT_{index}_PLAYER_LABEL_SEMANTIC_MISMATCH")
        fg = event.get("frameGeneration")
        if type(fg) is not int or fg < 0:
            event_errors.append(f"EVENT_{index}_FRAME_GENERATION_INVALID")
        if not _nonempty(event.get("displayedFrameId")) or not _nonempty(event.get("submissionId")):
            event_errors.append(f"EVENT_{index}_CAUSAL_IDS_MISSING")
        validated.append(event)
    if event_errors:
        return _rejected("DIRECT_RENDERER_SUBMIT_EVENT_REJECTED", details=event_errors)

    # Deterministic ordering is by explicit renderer frame generation only. It is not
    # used to choose marker identity; identity was already exact player+generation.
    validated.sort(key=lambda row: row["frameGeneration"])
    selected = validated[:MIN_DIRECT_SAMPLES]
    if len({row["frameGeneration"] for row in selected}) != len(selected):
        return _rejected("DUPLICATE_FRAME_GENERATION")
    if len({row["displayedFrameId"] for row in selected}) != len(selected):
        return _rejected("DUPLICATE_DISPLAYED_FRAME_ID")
    if len({row["submissionId"] for row in selected}) != len(selected):
        return _rejected("DUPLICATE_SUBMISSION_ID")

    samples = []
    for event in selected:
        samples.append({
            "runtimeEpoch": binding.runtime_epoch,
            "rendererEpoch": binding.renderer_epoch,
            "authorityKey": binding.authority_key,
            "frameGeneration": event["frameGeneration"],
            "displayedFrameId": event["displayedFrameId"],
            "submissionId": event["submissionId"],
            "actorAssociation": {"player": player, "generation": generation},
            "markers": [event["marker"]],
        })

    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "runtimeEpoch": binding.runtime_epoch,
        "rendererEpoch": binding.renderer_epoch,
        "authorityKey": binding.authority_key,
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "directSource": {
            "derivationKind": source["derivationKind"],
            "guessed": False,
            "displayedFrameCausalLink": True,
            "coordinateAuthority": "NATIVE_RENDERER_OBJECT_384X224",
            "screenshotCoordinatesUsed": False,
            "ocrCoordinatesUsed": False,
            "templateCoordinatesUsed": False,
            "worldProjectionCoordinatesUsed": False,
            "sourceTrace": list(source["sourceTrace"]),
            "instrumentationId": source["instrumentationId"],
            "hookSite": source["hookSite"],
        },
        "samples": samples,
    }
    qualification = qualify_native_player_marker(
        evidence,
        player=player,
        generation=generation,
        binding=binding.p32(),
    )
    if qualification.get("state") != QUALIFIED:
        return _rejected(
            "EXISTING_P32_QUALIFIER_REJECTED_PRODUCER_EVIDENCE",
            details=[str(qualification.get("reason") or "UNKNOWN")],
        )
    return {
        "schema": RESULT_SCHEMA,
        "state": "READY_FOR_BOUNDED_LIVE_VERIFICATION",
        "reason": "DIRECT_SOURCE_TRACE_PRODUCED_EXISTING_P32_CONTRACT",
        "blocker": None,
        "evidence": evidence,
        "qualification": qualification,
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "ownerSelectionRequired": False,
        "manualSeedRequired": False,
    }
