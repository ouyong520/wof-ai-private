from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

EVIDENCE_SCHEMA = "wof-native-player-marker-direct-evidence-v1"
RESULT_SCHEMA = "wof-native-player-marker-anchor-qualification-v1"
PROOF_SCHEMA = "wof-renderer-source-proof-v1"
ANCHOR_SCHEMA = "wof-native-player-marker-anchor-v1"
NATIVE_WIDTH = 384
NATIVE_HEIGHT = 224
MIN_DIRECT_SAMPLES = 3
QUALIFIED = "QUALIFIED_CANDIDATE"
REJECTED = "REJECTED"
_ALLOWED_DERIVATIONS = frozenset({"SOURCE_TRACED_POINTER", "DIRECT_RENDER_HOOK", "EXPORTED_RENDERER_POINTER"})
_ALLOWED_PLAYERS = frozenset({"P1", "P2", "P3"})
_LABELS = {"P1": "1P", "P2": "2P", "P3": "3P"}


@dataclass(frozen=True)
class ExpectedBinding:
    runtime_epoch: str
    renderer_epoch: str
    authority_key: str

    def valid(self) -> bool:
        return all(isinstance(v, str) and len(v) >= 1 for v in (self.runtime_epoch, self.renderer_epoch, self.authority_key))


def _reject(reason: str, *, details: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema": RESULT_SCHEMA,
        "state": REJECTED,
        "reason": reason,
        "details": sorted(set(details or [])),
        "rendererSourceProof": None,
        "anchor": None,
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


def _point(value: Any) -> dict[str, float] | None:
    if not isinstance(value, dict):
        return None
    try:
        x, y = float(value["x"]), float(value["y"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (isfinite(x) and isfinite(y)):
        return None
    if not (0.0 <= x <= NATIVE_WIDTH and 0.0 <= y <= NATIVE_HEIGHT):
        return None
    return {"x": x, "y": y}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _source_contract(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = evidence.get("directSource")
    if not isinstance(source, dict):
        return ["DIRECT_SOURCE_MISSING"]
    if source.get("derivationKind") not in _ALLOWED_DERIVATIONS:
        errors.append("DIRECT_SOURCE_DERIVATION_UNQUALIFIED")
    if source.get("guessed") is not False:
        errors.append("DIRECT_SOURCE_GUESSED_OR_UNSPECIFIED")
    if source.get("displayedFrameCausalLink") is not True:
        errors.append("DISPLAYED_FRAME_CAUSAL_LINK_MISSING")
    if source.get("coordinateAuthority") != "NATIVE_RENDERER_OBJECT_384X224":
        errors.append("NATIVE_COORDINATE_AUTHORITY_MISSING")
    if source.get("screenshotCoordinatesUsed") is not False:
        errors.append("SCREENSHOT_COORDINATES_FORBIDDEN")
    if source.get("ocrCoordinatesUsed") is not False:
        errors.append("OCR_COORDINATES_FORBIDDEN")
    if source.get("templateCoordinatesUsed") is not False:
        errors.append("TEMPLATE_COORDINATES_FORBIDDEN")
    if source.get("worldProjectionCoordinatesUsed") is not False:
        errors.append("WORLD_PROJECTION_COORDINATES_FORBIDDEN")
    trace = source.get("sourceTrace")
    if not isinstance(trace, list) or len(trace) < 2 or any(not _nonempty(item) for item in trace):
        errors.append("SOURCE_TRACE_INCOMPLETE")
    for field in ("instrumentationId", "hookSite"):
        if not _nonempty(source.get(field)):
            errors.append(f"DIRECT_SOURCE_{field.upper()}_MISSING")
    return errors


def _binding_errors(row: dict[str, Any], binding: ExpectedBinding) -> list[str]:
    errors = []
    if row.get("runtimeEpoch") != binding.runtime_epoch:
        errors.append("RUNTIME_EPOCH_MISMATCH")
    if row.get("rendererEpoch") != binding.renderer_epoch:
        errors.append("RENDERER_EPOCH_MISMATCH")
    if row.get("authorityKey") != binding.authority_key:
        errors.append("AUTHORITY_KEY_MISMATCH")
    return errors


def _normalize_marker(marker: Any, *, player: str, generation: int) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(marker, dict):
        return None, ["MARKER_MALFORMED"]
    errors: list[str] = []
    if marker.get("player") != player or marker.get("generation") != generation:
        errors.append("MARKER_ACTOR_GENERATION_MISMATCH")
    association = marker.get("actorAssociation")
    if not isinstance(association, dict):
        errors.append("ACTOR_ASSOCIATION_MISSING")
    else:
        if association.get("player") != player or association.get("generation") != generation:
            errors.append("ACTOR_ASSOCIATION_MISMATCH")
        if association.get("explicit") is not True or association.get("generationBound") is not True:
            errors.append("ACTOR_ASSOCIATION_NOT_EXPLICIT_GENERATION_BOUND")
        if association.get("ambiguous") is not False or association.get("candidateCount") != 1:
            errors.append("ACTOR_ASSOCIATION_AMBIGUOUS")
        if association.get("guessed") is not False:
            errors.append("ACTOR_ASSOCIATION_GUESSED_OR_UNSPECIFIED")
    if marker.get("labelSemantic") != _LABELS[player]:
        errors.append("PLAYER_LABEL_SEMANTIC_MISMATCH")
    if not _nonempty(marker.get("clusterKey")):
        errors.append("CLUSTER_KEY_MISSING")
    join = marker.get("clusterJoin")
    if not isinstance(join, dict) or join.get("explicit") is not True or join.get("guessed") is not False:
        errors.append("CLUSTER_JOIN_NOT_EXPLICIT")
    elif join.get("key") != marker.get("clusterKey"):
        errors.append("CLUSTER_JOIN_KEY_MISMATCH")

    members = marker.get("members")
    if not isinstance(members, list) or not members:
        errors.append("MARKER_MEMBERS_MISSING")
        return None, sorted(set(errors))
    seen_keys: set[str] = set()
    normalized: list[dict[str, Any]] = []
    arrow_members: list[dict[str, Any]] = []
    for member in members:
        if not isinstance(member, dict):
            errors.append("MARKER_MEMBER_MALFORMED")
            continue
        key = member.get("memberKey")
        if not _nonempty(key):
            errors.append("MARKER_MEMBER_KEY_MISSING")
            continue
        if key in seen_keys:
            errors.append("DUPLICATE_MARKER_MEMBER_KEY")
            continue
        seen_keys.add(key)
        role = member.get("semanticRole")
        if not _nonempty(role):
            errors.append("MARKER_MEMBER_ROLE_MISSING")
            continue
        if member.get("clusterKey") != marker.get("clusterKey"):
            errors.append("MARKER_MEMBER_CLUSTER_KEY_MISMATCH")
        if member.get("guessed") is not False:
            errors.append("MARKER_MEMBER_GUESSED_OR_UNSPECIFIED")
        anchor_point = _point(member.get("anchorPoint")) if role == "DOWN_ARROW" else None
        if role == "DOWN_ARROW":
            if anchor_point is None:
                errors.append("DOWN_ARROW_NATIVE_ANCHOR_MISSING_OR_INVALID")
            else:
                arrow_members.append({"memberKey": key, "anchorPoint": anchor_point})
        normalized.append({"memberKey": key, "semanticRole": role, "clusterKey": member.get("clusterKey")})
    if len(arrow_members) != 1:
        errors.append("DOWN_ARROW_MEMBER_AMBIGUOUS_OR_MISSING")
    if errors:
        return None, sorted(set(errors))
    normalized.sort(key=lambda row: (row["semanticRole"], row["memberKey"]))
    arrow = arrow_members[0]
    return {
        "clusterKey": marker["clusterKey"],
        "player": player,
        "generation": generation,
        "labelSemantic": marker["labelSemantic"],
        "members": normalized,
        "anchorMemberKey": arrow["memberKey"],
        "anchorPoint": arrow["anchorPoint"],
    }, []


def qualify_native_player_marker(evidence: dict[str, Any], *, player: str, generation: int, binding: ExpectedBinding) -> dict[str, Any]:
    """Qualify a direct native marker capture. Never promotes structural/visual-only evidence."""
    if not binding.valid():
        return _reject("EXPECTED_BINDING_INVALID")
    if player not in _ALLOWED_PLAYERS or not isinstance(generation, int) or isinstance(generation, bool) or generation < 0:
        return _reject("PLAYER_OR_GENERATION_INVALID")
    if not isinstance(evidence, dict) or evidence.get("schema") != EVIDENCE_SCHEMA:
        return _reject("EVIDENCE_SCHEMA_INVALID")
    if evidence.get("nativeWidth") != NATIVE_WIDTH or evidence.get("nativeHeight") != NATIVE_HEIGHT:
        return _reject("NATIVE_COORDINATE_CONTRACT_MISMATCH")
    top_binding_errors = _binding_errors(evidence, binding)
    if top_binding_errors:
        return _reject("STALE_OR_MIXED_AUTHORITY_BINDING", details=top_binding_errors)
    source_errors = _source_contract(evidence)
    if source_errors:
        return _reject("DIRECT_DISPLAYED_FRAME_SOURCE_UNPROVEN", details=source_errors)

    samples = evidence.get("samples")
    if not isinstance(samples, list) or len(samples) < MIN_DIRECT_SAMPLES:
        return _reject("DIRECT_FRAME_SAMPLE_COUNT_INSUFFICIENT")

    generations: list[int] = []
    normalized_markers: list[dict[str, Any]] = []
    seen_display_frames: set[str] = set()
    seen_submissions: set[str] = set()
    sample_errors: list[str] = []
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            sample_errors.append(f"SAMPLE_{index}_MALFORMED")
            continue
        for err in _binding_errors(sample, binding):
            sample_errors.append(f"SAMPLE_{index}_{err}")
        fg = sample.get("frameGeneration")
        if not isinstance(fg, int) or isinstance(fg, bool) or fg < 0:
            sample_errors.append(f"SAMPLE_{index}_FRAME_GENERATION_INVALID")
        else:
            generations.append(fg)
        display_id, submission_id = sample.get("displayedFrameId"), sample.get("submissionId")
        if not _nonempty(display_id) or not _nonempty(submission_id):
            sample_errors.append(f"SAMPLE_{index}_CAUSAL_IDS_MISSING")
        else:
            if display_id in seen_display_frames:
                sample_errors.append(f"SAMPLE_{index}_DUPLICATE_DISPLAYED_FRAME_ID")
            if submission_id in seen_submissions:
                sample_errors.append(f"SAMPLE_{index}_DUPLICATE_SUBMISSION_ID")
            seen_display_frames.add(display_id)
            seen_submissions.add(submission_id)
        association = sample.get("actorAssociation")
        if not isinstance(association, dict) or association.get("player") != player or association.get("generation") != generation:
            sample_errors.append(f"SAMPLE_{index}_GENERATION_ASSOCIATION_MISMATCH")
        markers = sample.get("markers")
        if not isinstance(markers, list):
            sample_errors.append(f"SAMPLE_{index}_MARKERS_MALFORMED")
            continue
        matches = [m for m in markers if isinstance(m, dict) and m.get("player") == player and m.get("generation") == generation]
        if len(matches) != 1:
            sample_errors.append(f"SAMPLE_{index}_DUPLICATE_OR_MISSING_PLAYER_MARKER")
            continue
        normalized, errors = _normalize_marker(matches[0], player=player, generation=generation)
        sample_errors.extend(f"SAMPLE_{index}_{err}" for err in errors)
        if normalized is not None:
            normalized_markers.append(normalized)
    if sample_errors:
        return _reject("DIRECT_MARKER_SAMPLE_REJECTED", details=sample_errors)
    if any(a >= b for a, b in zip(generations, generations[1:])):
        return _reject("FRAME_GENERATION_NOT_STRICTLY_MONOTONIC")
    if len(normalized_markers) != len(samples):
        return _reject("DIRECT_MARKER_SAMPLE_REJECTED")

    signature = lambda m: (
        m["clusterKey"],
        tuple((row["semanticRole"], row["memberKey"]) for row in m["members"]),
        m["anchorMemberKey"],
    )
    signatures = {signature(marker) for marker in normalized_markers}
    if len(signatures) != 1:
        return _reject("MARKER_CLUSTER_IDENTITY_CHANGED_OR_AMBIGUOUS")

    source = evidence["directSource"]
    final_marker = normalized_markers[-1]
    proof = {
        "schema": PROOF_SCHEMA,
        "proofClass": "DIRECT_DISPLAYED_FRAME_RENDER_OBJECT",
        "displayedFrameCausalLink": True,
        "coordinateAuthority": "NATIVE_RENDERER_OBJECT_384X224",
        "addressDerivation": {"kind": source["derivationKind"], "guessed": False},
        "screenshotCoordinatesUsed": False,
        "worldProjectionCoordinatesUsed": False,
        "actorAssociation": {"explicit": True, "generationBound": True, "ambiguous": False},
        "runtimeEpoch": binding.runtime_epoch,
        "rendererEpoch": binding.renderer_epoch,
        "authorityKey": binding.authority_key,
        "sourceTrace": list(source["sourceTrace"]),
        "directFrameSamples": len(samples),
        "frameGenerationMonotonic": True,
        "nativePlayerMarker": {
            "player": player,
            "generation": generation,
            "labelSemantic": final_marker["labelSemantic"],
            "clusterKey": final_marker["clusterKey"],
            "anchorMemberKey": final_marker["anchorMemberKey"],
            "memberKeys": [row["memberKey"] for row in final_marker["members"]],
        },
    }
    return {
        "schema": RESULT_SCHEMA,
        "state": QUALIFIED,
        "reason": "DIRECT_NATIVE_PLAYER_MARKER_CONTRACT_SATISFIED",
        "rendererSourceProof": proof,
        "anchor": {
            "schema": ANCHOR_SCHEMA,
            "player": player,
            "generation": generation,
            "x": final_marker["anchorPoint"]["x"],
            "y": final_marker["anchorPoint"]["y"],
            "nativeWidth": NATIVE_WIDTH,
            "nativeHeight": NATIVE_HEIGHT,
            "clusterKey": final_marker["clusterKey"],
            "anchorMemberKey": final_marker["anchorMemberKey"],
            "runtimeEpoch": binding.runtime_epoch,
            "rendererEpoch": binding.renderer_epoch,
            "authorityKey": binding.authority_key,
        },
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }
