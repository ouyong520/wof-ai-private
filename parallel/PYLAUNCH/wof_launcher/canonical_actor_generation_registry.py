from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .render_object_anchor import AuthorityBinding, NATIVE_HEIGHT, NATIVE_WIDTH

SCHEMA = "wof-canonical-actor-generation-registry-v1"
FRAME_SCHEMA = "wof-render-object-frame-v1"
PLAYER_ACTORS = ("P1", "P2", "P3")
ENEMY_ACTORS = tuple(f"enemy-slot-{index}" for index in range(20))
SUPPORTED_ACTORS = PLAYER_ACTORS + ENEMY_ACTORS
_SUPPORTED_ACTORS = frozenset(SUPPORTED_ACTORS)


def _binding_metadata(binding: AuthorityBinding | None) -> dict[str, Any]:
    if not isinstance(binding, AuthorityBinding):
        return {}
    return {
        "worldSha256": binding.world_sha256,
        "authorityKey": binding.authority_key,
        "runtimeEpoch": binding.runtime_epoch,
        "rendererEpoch": binding.renderer_epoch,
    }


def _suppressed(
    reason: str,
    binding: AuthorityBinding | None = None,
    *,
    actor: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "state": "SUPPRESSED",
        "reason": reason,
        "descriptors": [],
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }
    result.update(_binding_metadata(binding))
    if actor is not None:
        result["failedActor"] = actor
    return result


def _requested_actor_set(requested_actors: Any) -> frozenset[str] | None:
    if requested_actors is None:
        return None
    if isinstance(requested_actors, (str, bytes, bytearray, Mapping)) or not isinstance(requested_actors, Iterable):
        raise ValueError("requestedActors must be an iterable of exact supported actor names")
    requested = list(requested_actors)
    if any(not isinstance(actor, str) or actor not in _SUPPORTED_ACTORS for actor in requested):
        raise ValueError("requestedActors contains an unsupported actor name")
    return frozenset(requested)


def _descriptor_kind(actor: str) -> str:
    return "player" if actor in PLAYER_ACTORS else "enemy"


def resolve(
    frame: dict[str, Any],
    binding: AuthorityBinding,
    requestedActors: Any = None,
) -> dict[str, Any]:
    """Resolve explicit actor/generation identity authority from one W3 frame.

    The operation is stateless and intentionally ignores all spatial data. It never
    selects identity by row order, coordinates, nearest-object heuristics, or prior
    generations.
    """
    if not isinstance(binding, AuthorityBinding) or not binding.valid():
        return _suppressed("AUTHORITY_BINDING_INVALID", binding if isinstance(binding, AuthorityBinding) else None)
    if not isinstance(frame, dict) or frame.get("schema") != FRAME_SCHEMA:
        return _suppressed("FRAME_SCHEMA_INVALID", binding)
    if (
        frame.get("worldSha256") != binding.world_sha256
        or frame.get("authorityKey") != binding.authority_key
        or frame.get("runtimeEpoch") != binding.runtime_epoch
        or frame.get("rendererEpoch") != binding.renderer_epoch
    ):
        return _suppressed("STALE_AUTHORITY_OR_RENDERER_EPOCH", binding)
    if frame.get("nativeWidth") != NATIVE_WIDTH or frame.get("nativeHeight") != NATIVE_HEIGHT:
        return _suppressed("NATIVE_COORDINATE_CONTRACT_MISMATCH", binding)

    try:
        requested = _requested_actor_set(requestedActors)
    except ValueError:
        return _suppressed("REQUESTED_ACTOR_INVALID", binding)

    rows = frame.get("actors")
    if not isinstance(rows, list):
        return _suppressed("ACTOR_ROWS_INVALID", binding)

    by_actor: dict[str, list[dict[str, Any]]] = {actor: [] for actor in SUPPORTED_ACTORS}
    for row in rows:
        if not isinstance(row, dict):
            continue
        actor = row.get("actor")
        if isinstance(actor, str) and actor in _SUPPORTED_ACTORS:
            by_actor[actor].append(row)

    actors_to_resolve = requested if requested is not None else frozenset(
        actor for actor in SUPPORTED_ACTORS if by_actor[actor]
    )
    descriptors: list[dict[str, Any]] = []
    for actor in SUPPORTED_ACTORS:
        if actor not in actors_to_resolve:
            continue
        actor_rows = by_actor[actor]
        if not actor_rows:
            return _suppressed("ACTOR_ASSOCIATION_MISSING", binding, actor=actor)
        if len(actor_rows) != 1:
            generations = {
                row.get("generation")
                for row in actor_rows
                if type(row.get("generation")) is int and row.get("generation") >= 0
            }
            reason = "CONFLICTING_ACTOR_GENERATIONS" if len(generations) > 1 else "DUPLICATE_ACTOR_ROWS"
            return _suppressed(reason, binding, actor=actor)

        row = actor_rows[0]
        generation = row.get("generation")
        if type(generation) is not int or generation < 0:
            return _suppressed("ACTOR_GENERATION_INVALID", binding, actor=actor)
        association = row.get("association")
        if not isinstance(association, dict):
            return _suppressed("ACTOR_ASSOCIATION_UNPROVEN", binding, actor=actor)
        candidate_count = association.get("candidateCount")
        if (
            association.get("proven") is not True
            or association.get("ambiguous") is True
            or type(candidate_count) is not int
            or candidate_count != 1
        ):
            return _suppressed("ACTOR_ASSOCIATION_UNPROVEN", binding, actor=actor)
        if row.get("unsafe") is True:
            return _suppressed(str(row.get("unsafeReason") or "UNSAFE_ACTOR_ROW"), binding, actor=actor)

        descriptors.append({
            "kind": _descriptor_kind(actor),
            "actor": actor,
            "generation": generation,
        })

    result = {
        "schema": SCHEMA,
        "state": "READY",
        "descriptors": descriptors,
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }
    result.update(_binding_metadata(binding))
    return result


class CanonicalActorGenerationRegistry:
    """Narrow stateless facade for callers that prefer an object API."""

    @staticmethod
    def resolve(
        frame: dict[str, Any],
        binding: AuthorityBinding,
        requestedActors: Any = None,
    ) -> dict[str, Any]:
        return resolve(frame, binding, requestedActors=requestedActors)
