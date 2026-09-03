from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any, Mapping, Sequence

EXACT_WORLD_SHA = "921031"
SCHEMA = "alpha-v3-w2-zero-click-acquisition-v1"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}

DEFAULT_MIN_CONFIDENCE = 0.72
DEFAULT_AMBIGUITY_MARGIN = 0.08
_ALLOWED_VISUAL_SOURCES = frozenset({"canvas", "hud", "sprite", "tile", "render-object"})
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def screenshot_digest(png_bytes: bytes) -> str:
    """Stable read-only evidence key for a captured canvas PNG."""
    return "sha256:" + hashlib.sha256(bytes(png_bytes)).hexdigest()


@dataclass(frozen=True)
class HeadSeed:
    center_x: float
    center_y: float
    box: tuple[float, float, float, float]
    p1_type: int
    p1_generation: int
    canvas_digest: str
    source: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "center": [self.center_x, self.center_y],
            "box": list(self.box),
            "p1Type": self.p1_type,
            "p1Generation": self.p1_generation,
            "canvasDigest": self.canvas_digest,
            "source": self.source,
        }


@dataclass(frozen=True)
class AcquisitionResult:
    ok: bool
    confidence: float
    reason: str
    character_type: int | None = None
    p1_generation: int | None = None
    head_seed: HeadSeed | None = None
    ambiguity_margin: float | None = None
    evidence_sources: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "ok": self.ok,
            "confidence": self.confidence,
            "reason": self.reason,
            "characterType": self.character_type,
            "p1Generation": self.p1_generation,
            "headSeed": self.head_seed.as_dict() if self.head_seed else None,
            "ambiguityMargin": self.ambiguity_margin,
            "evidenceSources": list(self.evidence_sources),
            **SAFETY,
        }


def _failure(
    reason: str,
    *,
    confidence: float = 0.0,
    character_type: int | None = None,
    generation: int | None = None,
    margin: float | None = None,
    sources: Sequence[str] = (),
) -> AcquisitionResult:
    return AcquisitionResult(
        ok=False,
        confidence=max(0.0, min(1.0, float(confidence))),
        reason=reason,
        character_type=character_type,
        p1_generation=generation,
        head_seed=None,
        ambiguity_margin=margin,
        evidence_sources=tuple(sorted(set(sources))),
    )


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


def _confidence(row: Mapping[str, Any]) -> float:
    value = _float(row.get("confidence"))
    return max(0.0, min(1.0, value if value is not None else 0.0))


def _rank_unique(
    rows: Sequence[Mapping[str, Any]],
    *,
    minimum: float,
    ambiguity_margin: float,
    missing_reason: str,
    low_reason: str,
    ambiguous_reason: str,
) -> tuple[Mapping[str, Any] | None, AcquisitionResult | None, float | None]:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        return None, _failure(missing_reason), None
    usable = [row for row in rows if isinstance(row, Mapping)]
    if not usable:
        return None, _failure(missing_reason), None
    ranked = sorted(usable, key=lambda row: (-_confidence(row), repr(sorted(row.items()))))
    best_conf = _confidence(ranked[0])
    if best_conf < minimum:
        return None, _failure(low_reason, confidence=best_conf), None
    if len(ranked) == 1:
        return ranked[0], None, 1.0
    second_conf = _confidence(ranked[1])
    margin = best_conf - second_conf
    if margin < ambiguity_margin:
        return None, _failure(ambiguous_reason, confidence=best_conf, margin=margin), margin
    return ranked[0], None, margin


def _canvas_contract(canvas: Mapping[str, Any]) -> tuple[int, int, str] | None:
    width = _int(canvas.get("width"))
    height = _int(canvas.get("height"))
    digest = str(canvas.get("screenshotDigest") or "").strip()
    if width is None or height is None or width <= 0 or height <= 0 or not _SHA256_RE.fullmatch(digest):
        return None
    return width, height, digest


def _head_geometry(row: Mapping[str, Any], width: int, height: int) -> tuple[float, float, tuple[float, float, float, float]] | None:
    center = row.get("center")
    box = row.get("box")
    if not isinstance(center, Sequence) or isinstance(center, (str, bytes)) or len(center) != 2:
        return None
    if not isinstance(box, Sequence) or isinstance(box, (str, bytes)) or len(box) != 4:
        return None
    cx, cy = _float(center[0]), _float(center[1])
    values = tuple(_float(v) for v in box)
    if cx is None or cy is None or any(v is None for v in values):
        return None
    x1, y1, x2, y2 = (float(v) for v in values if v is not None)
    if not (0.0 <= x1 < x2 <= float(width) and 0.0 <= y1 < y2 <= float(height)):
        return None
    if not (x1 <= cx <= x2 and y1 <= cy <= y2):
        return None
    return cx, cy, (x1, y1, x2, y2)


def _sources(*rows: Mapping[str, Any]) -> tuple[str, ...]:
    out: set[str] = set()
    for row in rows:
        raw = row.get("evidenceSources")
        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
            out.update(str(value) for value in raw if str(value) in _ALLOWED_VISUAL_SOURCES)
        source = str(row.get("source") or "")
        if source in _ALLOWED_VISUAL_SOURCES:
            out.add(source)
    return tuple(sorted(out))


def acquire_zero_click_p1_head(
    *,
    world_sha256: str,
    p1_lifecycle: Mapping[str, Any] | None,
    canvas: Mapping[str, Any] | None,
    hud_identity_candidates: Sequence[Mapping[str, Any]],
    scene_head_candidates: Sequence[Mapping[str, Any]],
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    ambiguity_margin: float = DEFAULT_AMBIGUITY_MARGIN,
) -> AcquisitionResult:
    """Fail-closed P1 identity/head adjudication for W1's read-only visual candidates.

    This module intentionally does not capture pixels, inject input, or infer a projection.
    W1 (or another read-only evidence producer) supplies HUD and scene/head candidates;
    W2 binds them to exact-World P1 type + lifecycle generation and emits a seed only
    when one identity/head chain is safely unique.
    """
    if str(world_sha256) != EXACT_WORLD_SHA:
        return _failure("WORLD_MISMATCH")
    if not isinstance(p1_lifecycle, Mapping):
        return _failure("P1_LIFECYCLE_MISSING")
    if p1_lifecycle.get("active") is not True or p1_lifecycle.get("alive") is False:
        return _failure("P1_NOT_ACTIVE")
    p1_type = _int(p1_lifecycle.get("type"))
    generation = _int(p1_lifecycle.get("generation"))
    if p1_type is None or p1_type <= 0:
        return _failure("P1_IDENTITY_UNRESOLVED")
    if generation is None or generation <= 0:
        return _failure("P1_GENERATION_UNRESOLVED", character_type=p1_type)
    if not isinstance(canvas, Mapping):
        return _failure("CANVAS_EVIDENCE_MISSING", character_type=p1_type, generation=generation)
    canvas_contract = _canvas_contract(canvas)
    if canvas_contract is None:
        return _failure("CANVAS_EVIDENCE_INVALID", character_type=p1_type, generation=generation)
    width, height, digest = canvas_contract

    hud, error, hud_margin = _rank_unique(
        hud_identity_candidates,
        minimum=min_confidence,
        ambiguity_margin=ambiguity_margin,
        missing_reason="HUD_IDENTITY_MISSING",
        low_reason="HUD_IDENTITY_LOW_CONFIDENCE",
        ambiguous_reason="HUD_IDENTITY_AMBIGUOUS",
    )
    if error is not None:
        return AcquisitionResult(
            **{**error.__dict__, "character_type": p1_type, "p1_generation": generation}
        )
    assert hud is not None
    hud_type = _int(hud.get("characterType"))
    if hud_type != p1_type:
        return _failure(
            "HUD_PORTRAIT_REJECTED",
            confidence=_confidence(hud),
            character_type=p1_type,
            generation=generation,
            margin=hud_margin,
            sources=_sources(hud),
        )

    scene, error, scene_margin = _rank_unique(
        scene_head_candidates,
        minimum=min_confidence,
        ambiguity_margin=ambiguity_margin,
        missing_reason="SCENE_P1_MISSING",
        low_reason="NO_SAFE_HEAD_SEED",
        ambiguous_reason="AMBIGUOUS_SCENE_P1_HEAD",
    )
    if error is not None:
        return AcquisitionResult(
            **{**error.__dict__, "character_type": p1_type, "p1_generation": generation}
        )
    assert scene is not None
    scene_conf = _confidence(scene)
    if str(scene.get("actor") or "") != "P1":
        return _failure("REJECTED_WRONG_ACTOR", confidence=scene_conf, character_type=p1_type, generation=generation, margin=scene_margin, sources=_sources(hud, scene))
    if _int(scene.get("characterType")) != p1_type:
        return _failure("SCENE_IDENTITY_CONFLICT", confidence=scene_conf, character_type=p1_type, generation=generation, margin=scene_margin, sources=_sources(hud, scene))
    if _int(scene.get("p1Generation")) != generation:
        return _failure("STALE_P1_GENERATION", confidence=scene_conf, character_type=p1_type, generation=generation, margin=scene_margin, sources=_sources(hud, scene))
    if scene.get("coarsePriorConsistent") is False:
        return _failure("SCENE_COARSE_PRIOR_CONFLICT", confidence=scene_conf, character_type=p1_type, generation=generation, margin=scene_margin, sources=_sources(hud, scene))

    hud_key = str(hud.get("identityKey") or "").strip()
    scene_key = str(scene.get("identityKey") or "").strip()
    if hud_key and scene_key and hud_key != scene_key:
        return _failure("HUD_SCENE_IDENTITY_CONFLICT", confidence=min(_confidence(hud), scene_conf), character_type=p1_type, generation=generation, margin=scene_margin, sources=_sources(hud, scene))

    sources = _sources(hud, scene)
    if "canvas" not in sources or "hud" not in sources:
        return _failure("VISUAL_EVIDENCE_INCOMPLETE", confidence=min(_confidence(hud), scene_conf), character_type=p1_type, generation=generation, margin=scene_margin, sources=sources)
    if not ({"sprite", "tile", "render-object"} & set(sources)) and scene.get("coarsePriorConsistent") is not True:
        return _failure("SCENE_AUTHORITY_UNVERIFIED", confidence=min(_confidence(hud), scene_conf), character_type=p1_type, generation=generation, margin=scene_margin, sources=sources)

    geometry = _head_geometry(scene, width, height)
    if geometry is None:
        return _failure("HEAD_SEED_OUT_OF_BOUNDS", confidence=scene_conf, character_type=p1_type, generation=generation, margin=scene_margin, sources=sources)
    cx, cy, box = geometry
    confidence = min(_confidence(hud), scene_conf)
    margin_values = [value for value in (hud_margin, scene_margin) if value is not None]
    final_margin = min(margin_values) if margin_values else None
    seed = HeadSeed(
        center_x=cx,
        center_y=cy,
        box=box,
        p1_type=p1_type,
        p1_generation=generation,
        canvas_digest=digest,
        source=str(scene.get("source") or "zero-click-evidence"),
    )
    return AcquisitionResult(
        ok=True,
        confidence=confidence,
        reason="SAFE_UNIQUE",
        character_type=p1_type,
        p1_generation=generation,
        head_seed=seed,
        ambiguity_margin=final_margin,
        evidence_sources=sources,
    )
