from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

EXACT_WORLD_SHA = "921031"
ZERO_CLICK_EVIDENCE_SCHEMA = "alpha-v3-runtime-p1-zero-click-evidence-v1"
PRODUCER_SCHEMA = "alpha-v3-w6-semantic-evidence-producer-v1"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}

DEFAULT_MIN_CONFIDENCE = 0.72
DEFAULT_MIN_AMBIGUITY_MARGIN = 0.08
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

# These authority kinds are semantic by contract. Generic palette similarity and
# runtime-lifecycle identity are deliberately absent from this allow-list.
_SEMANTIC_AUTHORITY = {
    "hud-semantic": ("hud", "hud-character-id"),
    "portrait-semantic": ("hud", "portrait-character-id"),
    "tile-semantic": ("hud", "tile", "tile-character-id"),
    "render-semantic": ("hud", "render-object", "render-character-id"),
}
_IDENTITY_AUTHORITY_SOURCE = {
    "hud-semantic": "hud",
    "portrait-semantic": "hud-portrait",
    "tile-semantic": "hud-portrait-tile",
    "render-semantic": "hud-render-semantic",
}
_SCENE_AUTHORITY = {
    "sprite-head": "sprite",
    "tile-head": "tile",
    "render-object-head": "render-object",
    "coarse-prior-head": None,
}
_FORBIDDEN_DERIVATION_MARKERS = ("runtime", "p1-type", "lifecycle-type", "palette", "color")


@dataclass(frozen=True)
class ProducerResult:
    ok: bool
    reason: str
    envelope: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": PRODUCER_SCHEMA,
            "ok": self.ok,
            "reason": self.reason,
            "p1ZeroClickEvidence": self.envelope,
            **SAFETY,
        }


def _failure(reason: str) -> ProducerResult:
    return ProducerResult(ok=False, reason=reason, envelope=None)


def _int(value: Any) -> int | None:
    try:
        out = int(value)
    except (TypeError, ValueError):
        return None
    return out


def _float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if out != out or out in (float("inf"), float("-inf")):
        return None
    return out


def _nonempty(value: Any) -> str | None:
    text = str(value or "").strip()
    return text if text else None


def _confidence_and_margin(row: Mapping[str, Any]) -> tuple[float, float] | None:
    confidence = _float(row.get("confidence"))
    margin = _float(row.get("ambiguityMargin"))
    if confidence is None or margin is None:
        return None
    if not (0.0 <= confidence <= 1.0 and 0.0 <= margin <= 1.0):
        return None
    return confidence, margin


def _binding_matches(
    row: Mapping[str, Any],
    *,
    world_sha256: str,
    authority_key: str,
    runtime_epoch: str,
    layout_key: str,
    p1_generation: int,
) -> bool:
    return (
        str(row.get("worldSha256") or "") == world_sha256
        and str(row.get("authorityKey") or "") == authority_key
        and str(row.get("runtimeEpoch") or "") == runtime_epoch
        and str(row.get("layoutKey") or "") == layout_key
        and _int(row.get("p1Generation")) == p1_generation
    )


def _canvas_contract(canvas: Mapping[str, Any] | None) -> tuple[int, int, str] | None:
    if not isinstance(canvas, Mapping):
        return None
    width = _int(canvas.get("width"))
    height = _int(canvas.get("height"))
    digest = _nonempty(canvas.get("screenshotDigest"))
    if width is None or height is None or width <= 0 or height <= 0:
        return None
    if digest is None or not _SHA256_RE.fullmatch(digest):
        return None
    return width, height, digest


def _geometry(row: Mapping[str, Any], width: int, height: int) -> tuple[list[float], list[float]] | None:
    center = row.get("center")
    box = row.get("box")
    if not isinstance(center, Sequence) or isinstance(center, (str, bytes)) or len(center) != 2:
        return None
    if not isinstance(box, Sequence) or isinstance(box, (str, bytes)) or len(box) != 4:
        return None
    cx = _float(center[0])
    cy = _float(center[1])
    values = [_float(value) for value in box]
    if cx is None or cy is None or any(value is None for value in values):
        return None
    x1, y1, x2, y2 = (float(value) for value in values if value is not None)
    if not (0.0 <= x1 < x2 <= float(width) and 0.0 <= y1 < y2 <= float(height)):
        return None
    if not (x1 <= cx <= x2 and y1 <= cy <= y2):
        return None
    return [float(cx), float(cy)], [x1, y1, x2, y2]


def _semantic_candidate(
    row: Mapping[str, Any],
    *,
    world_sha256: str,
    authority_key: str,
    runtime_epoch: str,
    layout_key: str,
    p1_type: int,
    p1_generation: int,
    min_confidence: float,
    min_ambiguity_margin: float,
) -> tuple[dict[str, Any] | None, str | None]:
    if row.get("proven") is not True:
        return None, "SEMANTIC_IDENTITY_NOT_PROVEN"
    authority_kind = _nonempty(row.get("authorityKind"))
    if authority_kind is None:
        return None, "SEMANTIC_AUTHORITY_MISSING"
    lowered_kind = authority_kind.lower()
    if "palette" in lowered_kind or "color" in lowered_kind:
        return None, "GENERIC_PALETTE_REJECTED"
    authority_spec = _SEMANTIC_AUTHORITY.get(authority_kind)
    if authority_spec is None:
        return None, "SEMANTIC_AUTHORITY_REJECTED"
    if row.get("independentOfRuntimeType") is not True:
        return None, "CIRCULAR_RUNTIME_TYPE_REJECTED"
    derivation = _nonempty(row.get("identityDerivation"))
    expected_derivation = authority_spec[-1]
    if derivation != expected_derivation:
        if derivation and any(marker in derivation.lower() for marker in _FORBIDDEN_DERIVATION_MARKERS):
            return None, "CIRCULAR_OR_NONSEMANTIC_DERIVATION_REJECTED"
        return None, "SEMANTIC_DERIVATION_REJECTED"
    authority_id = _nonempty(row.get("authorityId"))
    identity_key = _nonempty(row.get("identityKey"))
    if authority_id is None or identity_key is None:
        return None, "SEMANTIC_PROVENANCE_INCOMPLETE"
    if not _binding_matches(
        row,
        world_sha256=world_sha256,
        authority_key=authority_key,
        runtime_epoch=runtime_epoch,
        layout_key=layout_key,
        p1_generation=p1_generation,
    ):
        return None, "SEMANTIC_IDENTITY_STALE"
    character_type = _int(row.get("characterType"))
    if character_type is None or character_type <= 0:
        return None, "SEMANTIC_IDENTITY_UNRESOLVED"
    if character_type != p1_type:
        return None, "SEMANTIC_RUNTIME_TYPE_CONFLICT"
    score = _confidence_and_margin(row)
    if score is None:
        return None, "SEMANTIC_CONFIDENCE_INVALID"
    confidence, margin = score
    if confidence < min_confidence:
        return None, "SEMANTIC_IDENTITY_LOW_CONFIDENCE"
    if margin < min_ambiguity_margin or row.get("ambiguous") is True:
        return None, "SEMANTIC_IDENTITY_AMBIGUOUS"

    evidence_sources = sorted(set(authority_spec[:-1]))
    return {
        "characterType": character_type,
        "identityKey": identity_key,
        "confidence": confidence,
        "ambiguityMargin": margin,
        "source": "hud",
        "evidenceSources": evidence_sources,
        "semanticAuthority": True,
        "semanticAuthorityKind": authority_kind,
        "identityDerivation": derivation,
        "independentOfRuntimeType": True,
        "authorityId": authority_id,
        "worldSha256": world_sha256,
        "authorityKey": authority_key,
        "runtimeEpoch": runtime_epoch,
        "p1Generation": p1_generation,
        "layoutKey": layout_key,
    }, None


def _scene_candidate(
    row: Mapping[str, Any],
    *,
    world_sha256: str,
    authority_key: str,
    runtime_epoch: str,
    layout_key: str,
    p1_type: int,
    p1_generation: int,
    identity_key: str,
    canvas_width: int,
    canvas_height: int,
    canvas_digest: str,
    min_confidence: float,
    min_ambiguity_margin: float,
) -> tuple[dict[str, Any] | None, str | None]:
    if row.get("proven") is not True:
        return None, "SCENE_HEAD_NOT_PROVEN"
    authority_kind = _nonempty(row.get("authorityKind"))
    if authority_kind is None:
        return None, "SCENE_AUTHORITY_MISSING"
    if "palette" in authority_kind.lower() or "color" in authority_kind.lower():
        return None, "GENERIC_PALETTE_REJECTED"
    if authority_kind not in _SCENE_AUTHORITY:
        return None, "SCENE_AUTHORITY_REJECTED"
    authority_id = _nonempty(row.get("authorityId"))
    if authority_id is None:
        return None, "SCENE_PROVENANCE_INCOMPLETE"
    if not _binding_matches(
        row,
        world_sha256=world_sha256,
        authority_key=authority_key,
        runtime_epoch=runtime_epoch,
        layout_key=layout_key,
        p1_generation=p1_generation,
    ):
        return None, "SCENE_HEAD_STALE"
    if str(row.get("actor") or "") != "P1":
        return None, "SCENE_ACTOR_CONFLICT"
    character_type = _int(row.get("characterType"))
    if character_type != p1_type:
        return None, "SCENE_RUNTIME_TYPE_CONFLICT"
    scene_identity_key = _nonempty(row.get("identityKey"))
    if scene_identity_key is None or scene_identity_key != identity_key:
        return None, "SEMANTIC_SCENE_IDENTITY_CONFLICT"
    if _nonempty(row.get("canvasDigest")) != canvas_digest:
        return None, "SCENE_CANVAS_STALE"
    score = _confidence_and_margin(row)
    if score is None:
        return None, "SCENE_CONFIDENCE_INVALID"
    confidence, margin = score
    if confidence < min_confidence:
        return None, "SCENE_HEAD_LOW_CONFIDENCE"
    if margin < min_ambiguity_margin or row.get("ambiguous") is True:
        return None, "SCENE_HEAD_AMBIGUOUS"
    geometry = _geometry(row, canvas_width, canvas_height)
    if geometry is None:
        return None, "SCENE_HEAD_GEOMETRY_INVALID"
    center, box = geometry

    spatial_source = _SCENE_AUTHORITY[authority_kind]
    coarse_prior = row.get("coarsePriorConsistent") is True
    if spatial_source is None and not coarse_prior:
        return None, "SCENE_AUTHORITY_UNVERIFIED"
    evidence_sources = {"canvas"}
    if spatial_source is not None:
        evidence_sources.add(spatial_source)

    return {
        "actor": "P1",
        "characterType": p1_type,
        "p1Generation": p1_generation,
        "identityKey": identity_key,
        "center": center,
        "box": box,
        "confidence": confidence,
        "ambiguityMargin": margin,
        "coarsePriorConsistent": coarse_prior,
        "source": spatial_source or "coarse-prior",
        "evidenceSources": sorted(evidence_sources),
        "authorityId": authority_id,
        "authorityKind": authority_kind,
        "canvasDigest": canvas_digest,
        "worldSha256": world_sha256,
        "authorityKey": authority_key,
        "runtimeEpoch": runtime_epoch,
        "layoutKey": layout_key,
    }, None


def _one_mapping(rows: Any, missing_reason: str, ambiguous_reason: str) -> tuple[Mapping[str, Any] | None, str | None]:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        return None, missing_reason
    mappings = [row for row in rows if isinstance(row, Mapping)]
    if not mappings:
        return None, missing_reason
    if len(mappings) != 1:
        return None, ambiguous_reason
    return mappings[0], None


def produce_p1_zero_click_evidence(
    *,
    world_sha256: str,
    authority_key: str,
    runtime_epoch: str,
    layout_key: str,
    p1_lifecycle: Mapping[str, Any] | None,
    canvas: Mapping[str, Any] | None,
    semantic_identity_observations: Sequence[Mapping[str, Any]],
    scene_head_observations: Sequence[Mapping[str, Any]],
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    min_ambiguity_margin: float = DEFAULT_MIN_AMBIGUITY_MARGIN,
) -> ProducerResult:
    """Translate already-proven semantic observations into W2's explicit envelope.

    This module performs no capture, palette search, runtime-type inference, UI work,
    memory access, or authority discovery. The caller must supply one already-proven
    semantic P1 identity observation and one already-proven scene-P1/head observation.
    Any stale, ambiguous, circular, conflicting, or non-semantic input yields no
    `p1ZeroClickEvidence` envelope.
    """
    world_sha256 = str(world_sha256 or "")
    authority_key = str(authority_key or "").strip()
    runtime_epoch = str(runtime_epoch or "").strip()
    layout_key = str(layout_key or "").strip()
    if world_sha256 != EXACT_WORLD_SHA:
        return _failure("WORLD_MISMATCH")
    if not authority_key:
        return _failure("AUTHORITY_KEY_MISSING")
    if not runtime_epoch:
        return _failure("RUNTIME_EPOCH_MISSING")
    if not layout_key:
        return _failure("LAYOUT_KEY_MISSING")
    if not isinstance(p1_lifecycle, Mapping):
        return _failure("P1_LIFECYCLE_MISSING")
    if p1_lifecycle.get("active") is not True or p1_lifecycle.get("alive") is False:
        return _failure("P1_NOT_ACTIVE")
    p1_type = _int(p1_lifecycle.get("type"))
    p1_generation = _int(p1_lifecycle.get("generation"))
    if p1_type is None or p1_type <= 0:
        return _failure("P1_RUNTIME_TYPE_UNRESOLVED")
    if p1_generation is None or p1_generation <= 0:
        return _failure("P1_GENERATION_UNRESOLVED")
    canvas_contract = _canvas_contract(canvas)
    if canvas_contract is None:
        return _failure("CANVAS_EVIDENCE_INVALID")
    canvas_width, canvas_height, canvas_digest = canvas_contract

    semantic_row, error = _one_mapping(
        semantic_identity_observations,
        "SEMANTIC_IDENTITY_MISSING",
        "SEMANTIC_IDENTITY_AMBIGUOUS",
    )
    if error is not None:
        return _failure(error)
    assert semantic_row is not None
    hud_candidate, error = _semantic_candidate(
        semantic_row,
        world_sha256=world_sha256,
        authority_key=authority_key,
        runtime_epoch=runtime_epoch,
        layout_key=layout_key,
        p1_type=p1_type,
        p1_generation=p1_generation,
        min_confidence=min_confidence,
        min_ambiguity_margin=min_ambiguity_margin,
    )
    if error is not None:
        return _failure(error)
    assert hud_candidate is not None

    scene_row, error = _one_mapping(
        scene_head_observations,
        "SCENE_HEAD_MISSING",
        "SCENE_HEAD_AMBIGUOUS",
    )
    if error is not None:
        return _failure(error)
    assert scene_row is not None
    scene_candidate, error = _scene_candidate(
        scene_row,
        world_sha256=world_sha256,
        authority_key=authority_key,
        runtime_epoch=runtime_epoch,
        layout_key=layout_key,
        p1_type=p1_type,
        p1_generation=p1_generation,
        identity_key=str(hud_candidate["identityKey"]),
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        canvas_digest=canvas_digest,
        min_confidence=min_confidence,
        min_ambiguity_margin=min_ambiguity_margin,
    )
    if error is not None:
        return _failure(error)
    assert scene_candidate is not None

    envelope = {
        "schema": ZERO_CLICK_EVIDENCE_SCHEMA,
        "producerSchema": PRODUCER_SCHEMA,
        "producerVerdict": "SAFE_UNIQUE",
        "worldSha256": world_sha256,
        "authorityKey": authority_key,
        "runtimeEpoch": runtime_epoch,
        "layoutKey": layout_key,
        "p1Generation": p1_generation,
        "p1Type": p1_type,
        "canvasDigest": canvas_digest,
        "identityAuthority": {
            "kind": "semantic",
            "source": _IDENTITY_AUTHORITY_SOURCE[str(hud_candidate["semanticAuthorityKind"])],
            "authorityId": hud_candidate["authorityId"],
            "authorityKind": hud_candidate["semanticAuthorityKind"],
            "characterType": p1_type,
            "identityKey": hud_candidate["identityKey"],
            "independentOfRuntimeP1Type": True,
            "derivedFromRuntimeP1Type": False,
            "genericHudPalette": False,
        },
        "hudIdentityCandidates": [hud_candidate],
        "sceneHeadCandidates": [scene_candidate],
        **SAFETY,
    }
    return ProducerResult(ok=True, reason="SAFE_UNIQUE", envelope=envelope)
