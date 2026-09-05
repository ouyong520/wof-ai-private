from __future__ import annotations

from typing import Any

from .canonical_actor_generation_registry import CanonicalActorGenerationRegistry
from .canonical_overlay_runtime_bridge import CanonicalOverlayRuntimeBridge
from .probe import WORLD_SHA256
from .render_object_anchor import AuthorityBinding

SCHEMA = "wof-alpha-canonical-runtime-coordinator-v1"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}


class CanonicalRuntimeCoordinatorError(RuntimeError):
    pass


class CanonicalRuntimeCoordinator:
    """Own the normal AlphaRuntime P12 -> P10 -> P9/P8/P11 canonical lifecycle.

    W3 is deliberately an explicit producer seam: this class never discovers,
    polls, or guesses a render-object frame. Identity/generation is resolved by
    P12 and all spatial authority is resolved by P10's deterministic anchor.
    """

    def __init__(self, verified_text) -> None:
        self._registry = CanonicalActorGenerationRegistry()
        self._bridge = CanonicalOverlayRuntimeBridge(verified_text)
        self._client: Any | None = None
        self._page_target_id: str | None = None
        self._authority_key: str | None = None
        self._runtime_epoch: str | None = None
        self._world_sha256: str | None = None
        self._renderer_epoch: str | None = None
        self._capability_present = False
        self._active = False
        self._state = "SUPPRESSED"
        self._reason = "NOT_ACTIVE"
        self._error: str | None = None
        self._frame_state = "WAITING"
        self._frame_reason = "NO_FRAME"
        self._descriptor_count = 0
        self._latest_ingest_state = "SUPPRESSED"
        self._latest_ingest_reason = "NO_INGEST"
        self._renderer_source_proven_in_latest_frame = False

    def activate(
        self,
        client: Any,
        page_target_id: str,
        *,
        authority_key: str,
        runtime_epoch: str,
        world_sha256: str,
        capability_present: bool,
    ) -> dict[str, Any]:
        self.revoke("CANONICAL_RUNTIME_REBOUND")
        if not isinstance(page_target_id, str) or not page_target_id:
            raise CanonicalRuntimeCoordinatorError("canonical page target id is required")
        if not isinstance(authority_key, str) or not authority_key:
            raise CanonicalRuntimeCoordinatorError("canonical authority key is required")
        if not isinstance(runtime_epoch, str) or len(runtime_epoch) < 16:
            raise CanonicalRuntimeCoordinatorError("canonical runtime epoch is invalid")
        if world_sha256 != WORLD_SHA256:
            raise CanonicalRuntimeCoordinatorError("canonical World identity does not match accepted World")
        if capability_present is not True:
            raise CanonicalRuntimeCoordinatorError("package-selected canonical HUD capability is not present")

        self._client = client
        self._page_target_id = page_target_id
        self._authority_key = authority_key
        self._runtime_epoch = runtime_epoch
        self._world_sha256 = world_sha256
        self._capability_present = True
        self._active = True
        self._state = "WAITING"
        self._reason = "WAITING_FOR_W3_FRAME_SOURCE_QUALIFICATION"
        self._error = None
        self._frame_state = "WAITING"
        self._frame_reason = "WAITING_FOR_W3_FRAME"
        self._descriptor_count = 0
        self._latest_ingest_state = "SUPPRESSED"
        self._latest_ingest_reason = "WAITING_FOR_W3_FRAME"
        self._renderer_source_proven_in_latest_frame = False
        return self.status()

    def _clear_bridge(self, reason: str) -> None:
        try:
            self._bridge.revoke(reason)
        except Exception:
            pass

    def _suppress(self, reason: str, *, frame_state: str = "SUPPRESSED") -> dict[str, Any]:
        self._clear_bridge(reason)
        self._state = "SUPPRESSED"
        self._reason = reason
        self._error = None
        self._frame_state = frame_state
        self._frame_reason = reason
        self._descriptor_count = 0
        self._latest_ingest_state = "SUPPRESSED"
        self._latest_ingest_reason = reason
        return self.status()

    def _fatal(self, reason: str, exc: BaseException) -> dict[str, Any]:
        self._clear_bridge(reason)
        self._state = "ERROR"
        self._reason = reason
        self._error = str(exc)
        self._frame_state = "SUPPRESSED"
        self._frame_reason = reason
        self._latest_ingest_state = "SUPPRESSED"
        self._latest_ingest_reason = reason
        return self.status()

    def ingest_frame(
        self,
        frame: dict[str, Any],
        *,
        sample_at: int | float,
        requested_actors: Any = None,
    ) -> dict[str, Any]:
        if not self._active or self._client is None:
            self._state = "SUPPRESSED"
            self._reason = "CANONICAL_RUNTIME_NOT_ACTIVE"
            return self.status()
        if self._capability_present is not True:
            return self._suppress("CANONICAL_HUD_CAPABILITY_MISSING")
        if not isinstance(frame, dict):
            return self._suppress("FRAME_SCHEMA_INVALID")
        if frame.get("worldSha256") != self._world_sha256:
            return self._suppress("STALE_AUTHORITY_OR_WORLD_IDENTITY")
        if frame.get("authorityKey") != self._authority_key or frame.get("runtimeEpoch") != self._runtime_epoch:
            return self._suppress("STALE_AUTHORITY_OR_RUNTIME_EPOCH")

        renderer_epoch = frame.get("rendererEpoch")
        if not isinstance(renderer_epoch, str) or len(renderer_epoch) < 16:
            return self._suppress("RENDERER_EPOCH_INVALID")

        if self._renderer_epoch is not None and renderer_epoch != self._renderer_epoch:
            self._clear_bridge("RENDERER_EPOCH_CHANGED")
        self._renderer_epoch = renderer_epoch

        source = frame.get("rendererSource")
        self._renderer_source_proven_in_latest_frame = bool(
            isinstance(source, dict) and source.get("proven") is True
        )
        binding = AuthorityBinding(
            authority_key=self._authority_key,
            runtime_epoch=self._runtime_epoch,
            renderer_epoch=renderer_epoch,
            world_sha256=self._world_sha256,
        )

        registry = self._registry.resolve(
            frame,
            binding,
            requestedActors=requested_actors,
        )
        self._frame_state = str(registry.get("state") or "SUPPRESSED")
        self._frame_reason = str(registry.get("reason") or ("READY" if self._frame_state == "READY" else "REGISTRY_SUPPRESSED"))
        descriptors = registry.get("descriptors")
        self._descriptor_count = len(descriptors) if isinstance(descriptors, list) else 0
        if self._frame_state != "READY" or not isinstance(descriptors, list):
            return self._suppress(
                str(registry.get("reason") or "ACTOR_GENERATION_REGISTRY_SUPPRESSED")
            )

        try:
            bridge_status = self._bridge.status()
            wanted = {
                "authorityKey": binding.authority_key,
                "runtimeEpoch": binding.runtime_epoch,
                "rendererEpoch": binding.renderer_epoch,
                "worldSha256": binding.world_sha256,
            }
            if (
                bridge_status.get("bound") is not True
                or bridge_status.get("authorityBinding") != wanted
                or bridge_status.get("pageTargetId") != self._page_target_id
            ):
                self._bridge.bind(self._client, self._page_target_id, binding)
            bridge_status = self._bridge.ingest_frame(
                frame,
                descriptors,
                sample_at=sample_at,
            )
        except Exception as exc:
            return self._fatal("CANONICAL_BRIDGE_OR_CDP_ERROR", exc)

        if bridge_status.get("error"):
            return self._fatal(
                "CANONICAL_BRIDGE_OR_CDP_ERROR",
                CanonicalRuntimeCoordinatorError(str(bridge_status.get("error"))),
            )
        if bridge_status.get("bound") is not True:
            return self._fatal(
                "CANONICAL_BRIDGE_UNEXPECTEDLY_UNBOUND",
                CanonicalRuntimeCoordinatorError(str(bridge_status.get("reason") or "unbound")),
            )

        self._latest_ingest_state = str(bridge_status.get("state") or "SUPPRESSED")
        self._latest_ingest_reason = str(bridge_status.get("reason") or self._latest_ingest_state)
        ready_count = int(bridge_status.get("readyRecordCount") or 0)
        suppressed_count = int(bridge_status.get("suppressedRecordCount") or 0)

        payload = bridge_status.get("lastPayload")
        suppression_reasons: list[str] = []
        if isinstance(payload, dict):
            for row in payload.get("records") or []:
                anchor = row.get("canonicalAnchor") if isinstance(row, dict) else None
                if isinstance(anchor, dict) and anchor.get("state") == "SUPPRESSED":
                    reason = anchor.get("reason")
                    if isinstance(reason, str) and reason and reason not in suppression_reasons:
                        suppression_reasons.append(reason)

        if suppressed_count:
            self._state = "SUPPRESSED"
            self._reason = suppression_reasons[0] if suppression_reasons else self._latest_ingest_reason
        elif ready_count:
            self._state = "READY"
            self._reason = "CANONICAL_ANCHORS_READY"
        else:
            self._state = "SUPPRESSED"
            self._reason = "NO_CANONICAL_ACTORS_IN_FRAME"
        self._error = None
        return self.status()

    def suppress(self, reason: str = "CANONICAL_W3_SOURCE_UNAVAILABLE") -> dict[str, Any]:
        if not self._active:
            self._state = "SUPPRESSED"
            self._reason = str(reason or "CANONICAL_W3_SOURCE_UNAVAILABLE")
            return self.status()
        return self._suppress(str(reason or "CANONICAL_W3_SOURCE_UNAVAILABLE"))

    def revoke(self, reason: str = "CANONICAL_RUNTIME_REVOKED") -> dict[str, Any]:
        self._clear_bridge(reason)
        self._client = None
        self._page_target_id = None
        self._authority_key = None
        self._runtime_epoch = None
        self._world_sha256 = None
        self._renderer_epoch = None
        self._capability_present = False
        self._active = False
        self._state = "SUPPRESSED"
        self._reason = str(reason or "CANONICAL_RUNTIME_REVOKED")
        self._error = None
        self._frame_state = "WAITING"
        self._frame_reason = self._reason
        self._descriptor_count = 0
        self._latest_ingest_state = "SUPPRESSED"
        self._latest_ingest_reason = self._reason
        self._renderer_source_proven_in_latest_frame = False
        return self.status()

    def status(self) -> dict[str, Any]:
        bridge = self._bridge.status()
        hud = bridge.get("hud") if isinstance(bridge, dict) else None
        return {
            "schema": SCHEMA,
            "state": self._state,
            "reason": self._reason,
            "error": self._error,
            "active": self._active,
            "stackInstalled": True,
            "capabilityPresent": self._capability_present,
            "bound": bridge.get("bound") is True,
            "pageTargetId": self._page_target_id,
            "authorityKey": self._authority_key,
            "runtimeEpoch": self._runtime_epoch,
            "rendererEpoch": self._renderer_epoch,
            "worldSha256": self._world_sha256,
            "frameResolution": {
                "state": self._frame_state,
                "reason": self._frame_reason,
                "descriptorCount": self._descriptor_count,
            },
            "latestIngest": {
                "state": self._latest_ingest_state,
                "reason": self._latest_ingest_reason,
                "recordCount": int(bridge.get("recordCount") or 0),
                "readyRecordCount": int(bridge.get("readyRecordCount") or 0),
                "suppressedRecordCount": int(bridge.get("suppressedRecordCount") or 0),
                "hudState": hud.get("state") if isinstance(hud, dict) else None,
                "hudReason": hud.get("reason") if isinstance(hud, dict) else None,
            },
            "rendererSourceProvenInLatestFrame": self._renderer_source_proven_in_latest_frame,
            "legacySpatialFallback": False,
            "positionAuthority": bridge.get("positionAuthority"),
            "bridge": bridge,
            **SAFETY,
        }
