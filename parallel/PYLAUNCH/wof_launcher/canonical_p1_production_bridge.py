from __future__ import annotations

from typing import Any, Callable

from .production_p1_overlay import ProductionP1Overlay
from .render_object_anchor import (
    NATIVE_HEIGHT,
    NATIVE_WIDTH,
    SCHEMA as ANCHOR_SCHEMA,
    AuthorityBinding,
    DeterministicRenderObjectAnchor,
)

SCHEMA = "wof-alpha-canonical-p1-production-bridge-v1"


class CanonicalP1ProductionBridge:
    """Canonical-only P1 render-anchor bridge into the maintained production HUD.

    Position authority comes exclusively from DeterministicRenderObjectAnchor.
    Display layout is used only to scale the canonical 384x224 point into the
    existing maintained HUD API; it is never a position-authority fallback.
    """

    def __init__(
        self,
        verified_text: Callable[[str], str] | None = None,
        *,
        overlay: ProductionP1Overlay | Any | None = None,
    ) -> None:
        if overlay is None:
            if verified_text is None:
                raise ValueError("verified_text is required for the production HUD adapter")
            overlay = ProductionP1Overlay(verified_text)
        self._overlay = overlay
        self._resolver = DeterministicRenderObjectAnchor()
        self._binding: AuthorityBinding | None = None
        self._generation: int | None = None
        self._last_anchor: dict[str, Any] | None = None
        self._last_reason = "NOT_BOUND"

    @staticmethod
    def _valid_generation(generation: Any) -> int:
        if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
            raise ValueError("P1 actor generation must be a non-negative integer")
        return generation

    @staticmethod
    def _valid_layout(layout: Any) -> bool:
        if not isinstance(layout, dict):
            return False
        try:
            width = float(layout.get("width"))
            height = float(layout.get("height"))
        except (TypeError, ValueError):
            return False
        return width > 0.0 and height > 0.0

    def bind(
        self,
        client: Any,
        page_target_id: str,
        binding: AuthorityBinding,
        *,
        generation: int,
    ) -> dict[str, Any]:
        generation = self._valid_generation(generation)
        if not isinstance(binding, AuthorityBinding) or not binding.valid():
            raise ValueError("invalid canonical render-object authority binding")
        self.dispose()
        self._resolver.bind(binding)
        try:
            self._overlay.bind(client, page_target_id, binding.authority_key, binding.runtime_epoch)
        except Exception:
            self._resolver.revoke()
            raise
        self._binding = binding
        self._generation = generation
        self._clear("CANONICAL_WAITING_FOR_READY")
        return self.status()

    def set_generation(self, generation: int) -> dict[str, Any]:
        generation = self._valid_generation(generation)
        if self._generation != generation:
            self._generation = generation
            self._clear("ACTOR_GENERATION_CHANGED")
        return self.status()

    def ingest_frame(self, frame: dict[str, Any], *, layout: dict[str, Any] | None) -> dict[str, Any]:
        binding = self._binding
        generation = self._generation
        if binding is None or generation is None:
            self._last_anchor = None
            self._last_reason = "NO_AUTHORITY_BINDING"
            return self.status()

        resolved = self._resolver.resolve(frame, actor="P1", generation=generation)
        if resolved.get("state") != "READY":
            self._clear(str(resolved.get("reason") or "CANONICAL_SUPPRESSED"))
            return self.status()
        if not self._valid_layout(layout):
            self._clear("DRAWING_SURFACE_LAYOUT_INVALID")
            return self.status()

        anchor = resolved.get("anchor")
        if not isinstance(anchor, dict):
            self._clear("CANONICAL_ANCHOR_INVALID")
            return self.status()
        x = anchor.get("x")
        y = anchor.get("y")
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            self._clear("CANONICAL_ANCHOR_INVALID")
            return self.status()

        # The existing maintained HUD adapter performs only native-surface ->
        # current-canvas scaling here.  The x/y authority remains the exact
        # canonical 384x224 render-object anchor; there is no projection,
        # screenshot/template, click, nearest-sprite, or guessed fallback.
        visual = {
            "state": "HEAD_TRACKING",
            "lostFrames": 0,
            "center": [float(x), float(y)],
            "seedSource": ANCHOR_SCHEMA,
            "canonical": True,
        }
        self._overlay.update(visual, layout, (NATIVE_WIDTH, NATIVE_HEIGHT))
        self._last_anchor = {
            "x": float(x),
            "y": float(y),
            "nativeWidth": NATIVE_WIDTH,
            "nativeHeight": NATIVE_HEIGHT,
        }
        self._last_reason = "READY"
        return self.status()

    def revoke(self, reason: str = "CANONICAL_AUTHORITY_REVOKED") -> dict[str, Any]:
        self._resolver.revoke()
        self._clear(reason)
        self._binding = None
        self._generation = None
        return self.status()

    def _clear(self, reason: str) -> None:
        self._last_anchor = None
        self._last_reason = str(reason or "CANONICAL_SUPPRESSED")
        try:
            self._overlay.update(
                {"state": "SUPPRESSED", "revocationReason": self._last_reason},
                None,
                (NATIVE_WIDTH, NATIVE_HEIGHT),
            )
        except Exception:
            # Never turn a failed hide into a visible fallback.  The maintained
            # overlay itself remains fail-closed on stale/missing tracker input.
            pass

    def status(self) -> dict[str, Any]:
        overlay_status = self._overlay.status() if hasattr(self._overlay, "status") else {}
        binding = self._binding
        ready = self._last_anchor is not None and overlay_status.get("visible") is True
        return {
            "schema": SCHEMA,
            "state": "READY" if ready else "SUPPRESSED",
            "reason": None if ready else self._last_reason,
            "actor": "P1",
            "generation": self._generation,
            "nativeWidth": NATIVE_WIDTH,
            "nativeHeight": NATIVE_HEIGHT,
            "anchor": dict(self._last_anchor) if self._last_anchor else None,
            "authorityKey": binding.authority_key if binding else None,
            "runtimeEpoch": binding.runtime_epoch if binding else None,
            "rendererEpoch": binding.renderer_epoch if binding else None,
            "hud": dict(overlay_status) if isinstance(overlay_status, dict) else {},
            "positionAuthority": ANCHOR_SCHEMA,
            "legacyPositionFallback": False,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }

    def dispose(self) -> None:
        self._resolver.revoke()
        try:
            self._overlay.dispose()
        finally:
            self._binding = None
            self._generation = None
            self._last_anchor = None
            self._last_reason = "DISPOSED"
