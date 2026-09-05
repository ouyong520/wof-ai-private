from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Iterable

from .probe import WORLD_SHA256

SCHEMA = "wof-render-object-anchor-v1"
NATIVE_WIDTH = 384
NATIVE_HEIGHT = 224
_ALLOWED_SOURCE_KINDS = frozenset({"exact-cps1-buffered-object", "renderer-side-equivalent"})
_BODY_ROLES = frozenset({"body", "body-tile", "actor-body"})


@dataclass(frozen=True)
class AuthorityBinding:
    authority_key: str
    runtime_epoch: str
    renderer_epoch: str
    world_sha256: str = WORLD_SHA256

    def valid(self) -> bool:
        return (
            self.world_sha256 == WORLD_SHA256
            and len(self.authority_key) > 0
            and len(self.runtime_epoch) >= 16
            and len(self.renderer_epoch) >= 16
        )


def _rect(value: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(value, dict):
        return None
    try:
        left = float(value["left"])
        top = float(value["top"])
        right = float(value["right"])
        bottom = float(value["bottom"])
    except (KeyError, TypeError, ValueError):
        return None
    if not all(isfinite(v) for v in (left, top, right, bottom)):
        return None
    if right <= left or bottom <= top:
        return None
    return left, top, right, bottom


def visible_body_bounds(parts: Iterable[dict[str, Any]]) -> dict[str, float] | None:
    """Union only renderer-qualified body parts; weapon/effect/projectile parts are ignored."""
    rects: list[tuple[float, float, float, float]] = []
    for part in parts:
        if not isinstance(part, dict) or part.get("role") not in _BODY_ROLES:
            continue
        rect = _rect(part.get("bounds"))
        if rect is None:
            continue
        l, t, r, b = rect
        l = max(0.0, min(float(NATIVE_WIDTH), l))
        r = max(0.0, min(float(NATIVE_WIDTH), r))
        t = max(0.0, min(float(NATIVE_HEIGHT), t))
        b = max(0.0, min(float(NATIVE_HEIGHT), b))
        if r > l and b > t:
            rects.append((l, t, r, b))
    if not rects:
        return None
    return {
        "left": min(v[0] for v in rects),
        "top": min(v[1] for v in rects),
        "right": max(v[2] for v in rects),
        "bottom": max(v[3] for v in rects),
    }


def canonical_anchor(bounds: dict[str, float], clearance: float = 4.0) -> dict[str, float] | None:
    rect = _rect(bounds)
    if rect is None:
        return None
    left, top, right, _bottom = rect
    x = (left + right) / 2.0
    y = top - max(0.0, float(clearance))
    if x < 0.0 or x > NATIVE_WIDTH:
        return None
    return {"x": x, "y": max(0.0, min(float(NATIVE_HEIGHT), y))}


class DeterministicRenderObjectAnchor:
    """Fail-closed canonical 384x224 anchor consumer for a proven renderer/object producer."""

    def __init__(self) -> None:
        self._binding: AuthorityBinding | None = None

    def bind(self, binding: AuthorityBinding) -> None:
        if not binding.valid():
            raise ValueError("invalid exact World/runtime/renderer binding")
        self._binding = binding

    def revoke(self) -> None:
        self._binding = None

    def resolve(self, frame: dict[str, Any], *, actor: str = "P1", generation: int) -> dict[str, Any]:
        binding = self._binding
        if binding is None:
            return self._suppressed("NO_AUTHORITY_BINDING")
        if not isinstance(frame, dict) or frame.get("schema") != "wof-render-object-frame-v1":
            return self._suppressed("FRAME_SCHEMA_INVALID")
        if (
            frame.get("worldSha256") != binding.world_sha256
            or frame.get("authorityKey") != binding.authority_key
            or frame.get("runtimeEpoch") != binding.runtime_epoch
            or frame.get("rendererEpoch") != binding.renderer_epoch
        ):
            return self._suppressed("STALE_AUTHORITY_OR_RENDERER_EPOCH")
        if frame.get("nativeWidth") != NATIVE_WIDTH or frame.get("nativeHeight") != NATIVE_HEIGHT:
            return self._suppressed("NATIVE_COORDINATE_CONTRACT_MISMATCH")
        source = frame.get("rendererSource")
        if not isinstance(source, dict) or source.get("proven") is not True or source.get("kind") not in _ALLOWED_SOURCE_KINDS:
            return self._suppressed("RENDERER_SOURCE_UNPROVEN")

        actors = [
            row
            for row in (frame.get("actors") or [])
            if isinstance(row, dict) and row.get("actor") == actor and row.get("generation") == generation
        ]
        if len(actors) != 1:
            return self._suppressed("AMBIGUOUS_ACTOR_ASSOCIATION" if actors else "ACTOR_ASSOCIATION_MISSING")
        row = actors[0]
        association = row.get("association")
        if (
            not isinstance(association, dict)
            or association.get("proven") is not True
            or association.get("ambiguous") is True
            or association.get("candidateCount") != 1
        ):
            return self._suppressed("ACTOR_ASSOCIATION_UNPROVEN")
        if row.get("unsafe") is True:
            return self._suppressed(str(row.get("unsafeReason") or "UNSAFE_FRAME"))

        parts = row.get("parts")
        bounds = visible_body_bounds(parts) if isinstance(parts, list) else None
        if bounds is None:
            bounds = row.get("bodyBounds") if isinstance(row.get("bodyBounds"), dict) else None
        anchor = canonical_anchor(bounds) if bounds else None
        if anchor is None:
            return self._suppressed("VISIBLE_BODY_BOUNDS_UNAVAILABLE")
        return {
            "schema": SCHEMA,
            "state": "READY",
            "actor": actor,
            "generation": generation,
            "nativeWidth": NATIVE_WIDTH,
            "nativeHeight": NATIVE_HEIGHT,
            "anchor": anchor,
            "bodyBounds": bounds,
            "authorityKey": binding.authority_key,
            "runtimeEpoch": binding.runtime_epoch,
            "rendererEpoch": binding.renderer_epoch,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }

    @staticmethod
    def _suppressed(reason: str) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "state": "SUPPRESSED",
            "reason": reason,
            "nativeWidth": NATIVE_WIDTH,
            "nativeHeight": NATIVE_HEIGHT,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }
