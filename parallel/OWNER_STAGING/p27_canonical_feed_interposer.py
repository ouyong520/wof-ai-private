from __future__ import annotations

import argparse
import copy
import math
import os
from pathlib import Path
import runpy
import sys
from typing import Any, Mapping, Sequence

CAPTURE_SCHEMA = "wof-render-authority-capture-v2"
CANONICAL_SCHEMA = "wof-alpha-canonical-runtime-coordinator-v1"
FRAME_SCHEMA = "wof-render-object-frame-v1"
WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
NATIVE_WIDTH = 384
NATIVE_HEIGHT = 224
_PLAYER_NAMES = frozenset({"P1", "P2", "P3"})


class CanonicalFeedExposureError(RuntimeError):
    pass


def _exact_text(value: Any, label: str, *, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value) < minimum:
        raise CanonicalFeedExposureError(f"{label} missing or invalid")
    return value


def _generation(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CanonicalFeedExposureError(f"{label} generation missing or invalid")
    return value


def _sample_at(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CanonicalFeedExposureError("W3 actor snapshot sampleAt missing or invalid")
    sample = float(value)
    if not math.isfinite(sample) or sample < 0:
        raise CanonicalFeedExposureError("W3 actor snapshot sampleAt missing or invalid")
    return sample


def _identity_actor_rows(actors: Mapping[str, Any]) -> list[dict[str, Any]]:
    players = actors.get("players")
    enemies = actors.get("enemies")
    if not isinstance(players, list) or not isinstance(enemies, list):
        raise CanonicalFeedExposureError("W3 actor snapshot players/enemies malformed")

    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    for row in players:
        if not isinstance(row, Mapping):
            raise CanonicalFeedExposureError("W3 player identity row malformed")
        actor = row.get("name")
        if actor not in _PLAYER_NAMES or actor in seen:
            raise CanonicalFeedExposureError("W3 player identity is unsupported or duplicated")
        generation = _generation(row.get("generation"), str(actor))
        seen.add(str(actor))
        out.append({
            "kind": "player",
            "actor": str(actor),
            "generation": generation,
            "association": {
                "proven": True,
                "ambiguous": False,
                "candidateCount": 1,
                "basis": "EXACT_RUNTIME_ACTOR_SLOT_GENERATION",
            },
        })

    for row in enemies:
        if not isinstance(row, Mapping):
            raise CanonicalFeedExposureError("W3 enemy identity row malformed")
        slot = row.get("slot")
        if isinstance(slot, bool) or not isinstance(slot, int) or slot < 0 or slot > 19:
            raise CanonicalFeedExposureError("W3 enemy slot identity missing or invalid")
        actor = f"enemy-slot-{slot}"
        if actor in seen:
            raise CanonicalFeedExposureError("W3 enemy slot identity duplicated")
        generation = _generation(row.get("generation"), actor)
        seen.add(actor)
        out.append({
            "kind": "enemy",
            "actor": actor,
            "generation": generation,
            "association": {
                "proven": True,
                "ambiguous": False,
                "candidateCount": 1,
                "basis": "EXACT_RUNTIME_ACTOR_SLOT_GENERATION",
            },
        })
    return out


def identity_only_frame(
    remote: Mapping[str, Any],
    *,
    world_sha256: str,
    authority_key: str,
    runtime_epoch: str,
    renderer_epoch: str,
) -> tuple[dict[str, Any], float]:
    """Translate only W3's exact actor-slot identity/generation into the canonical frame contract.

    No W3 coordinate, candidate region, screenshot, world projection, or structural row is copied.
    Renderer source remains explicitly unproven, so P10 must emit coordinate-free SUPPRESSED anchors.
    """
    if not isinstance(remote, Mapping) or remote.get("schema") != CAPTURE_SCHEMA:
        raise CanonicalFeedExposureError("W3 capture remote schema mismatch")
    expected = {
        "worldSha256": world_sha256,
        "authorityKey": authority_key,
        "runtimeEpoch": runtime_epoch,
        "rendererEpoch": renderer_epoch,
    }
    for key, value in expected.items():
        if remote.get(key) != value:
            raise CanonicalFeedExposureError(f"W3 capture {key} mismatch")
    if (
        remote.get("readOnly") is not True
        or remote.get("ramWrites") != 0
        or remote.get("inputInjection") is not False
        or remote.get("overlayEnabled") is not False
    ):
        raise CanonicalFeedExposureError("W3 capture safety boundary mismatch")

    actors = remote.get("actors")
    if not isinstance(actors, Mapping):
        raise CanonicalFeedExposureError("W3 actor snapshot missing")
    sample = _sample_at(actors.get("sampleAt"))
    rows = _identity_actor_rows(actors)
    frame = {
        "schema": FRAME_SCHEMA,
        **expected,
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "rendererSource": {
            "proven": False,
            "kind": "unverified-capture",
            "qualification": str(remote.get("rendererSourceQualification") or "UNPROVEN"),
            "coordinateAuthority": "NONE",
        },
        "actors": rows,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "identityOnly": True,
    }
    return frame, sample


def validate_canonical_status(status: Mapping[str, Any], expected: Mapping[str, str]) -> dict[str, Any]:
    if not isinstance(status, Mapping) or status.get("schema") != CANONICAL_SCHEMA:
        raise CanonicalFeedExposureError("P10 canonical coordinator status schema mismatch")
    for key in ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch"):
        if status.get(key) != expected.get(key):
            raise CanonicalFeedExposureError(f"P10 canonical coordinator {key} mismatch")
    if (
        status.get("readOnly") is not True
        or status.get("ramWrites") != 0
        or status.get("inputInjection") is not False
        or status.get("legacySpatialFallback") is not False
    ):
        raise CanonicalFeedExposureError("P10 canonical coordinator safety boundary mismatch")

    bridge = status.get("bridge")
    payload = bridge.get("lastPayload") if isinstance(bridge, Mapping) else None
    if payload is not None:
        if not isinstance(payload, Mapping) or not isinstance(payload.get("records"), list):
            raise CanonicalFeedExposureError("P10 canonical payload malformed")
        for row in payload["records"]:
            if not isinstance(row, Mapping):
                raise CanonicalFeedExposureError("P10 canonical record malformed")
            for key in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch"):
                if row.get(key) != expected.get(key):
                    raise CanonicalFeedExposureError(f"P10 canonical record {key} mismatch")
            anchor = row.get("canonicalAnchor")
            if not isinstance(anchor, Mapping) or anchor.get("state") not in {"READY", "SUPPRESSED"}:
                raise CanonicalFeedExposureError("P10 canonical anchor state malformed")
            if anchor.get("state") == "SUPPRESSED":
                for forbidden in ("anchor", "bodyBounds", "position", "legacyAnchor", "fallbackAnchor"):
                    if forbidden in anchor:
                        raise CanonicalFeedExposureError(
                            "P10 SUPPRESSED canonical record carried coordinates"
                        )
    return copy.deepcopy(dict(status))


class CanonicalFeedExposure:
    def __init__(self, coordinator: Any) -> None:
        self.coordinator = coordinator
        self.identity: dict[str, str] | None = None
        self.latest: dict[str, Any] | None = None
        self.last_sample_at: float | None = None
        self.last_signature: tuple[Any, ...] | None = None
        self.last_generation: dict[str, int] = {}
        self.replay_rejected = 0
        self.malformed_rejected = 0
        self.replacement_count = 0
        self.last_error: str | None = None

    def clear(self, reason: str) -> None:
        try:
            self.coordinator.revoke(str(reason or "P27_CANONICAL_FEED_REVOKED"))
        finally:
            self.identity = None
            self.latest = None
            self.last_sample_at = None
            self.last_signature = None
            self.last_generation = {}
            self.last_error = str(reason or "P27_CANONICAL_FEED_REVOKED")

    def bind(
        self,
        client: Any,
        page_target_id: str,
        *,
        world_sha256: str,
        authority_key: str,
        runtime_epoch: str,
        renderer_epoch: str,
    ) -> None:
        expected = {
            "worldSha256": _exact_text(world_sha256, "worldSha256"),
            "pageTargetId": _exact_text(page_target_id, "pageTargetId"),
            "authorityKey": _exact_text(authority_key, "authorityKey"),
            "runtimeEpoch": _exact_text(runtime_epoch, "runtimeEpoch", minimum=16),
            "rendererEpoch": _exact_text(renderer_epoch, "rendererEpoch", minimum=16),
        }
        if expected["worldSha256"] != WORLD_SHA256:
            raise CanonicalFeedExposureError("exact World SHA mismatch")
        if self.identity == expected:
            return
        if self.identity is not None:
            self.replacement_count += 1
        self.clear("P27_CANONICAL_AUTHORITY_REBOUND")
        status = self.coordinator.activate(
            client,
            expected["pageTargetId"],
            authority_key=expected["authorityKey"],
            runtime_epoch=expected["runtimeEpoch"],
            world_sha256=expected["worldSha256"],
            capability_present=True,
        )
        if not isinstance(status, Mapping) or status.get("schema") != CANONICAL_SCHEMA:
            self.clear("P27_CANONICAL_ACTIVATE_MALFORMED")
            raise CanonicalFeedExposureError("P10 canonical coordinator activation malformed")
        self.identity = expected
        self.latest = None
        self.last_error = None

    def consume(self, remote: Mapping[str, Any]) -> bool:
        expected = self.identity
        if expected is None:
            raise CanonicalFeedExposureError("canonical feed has no active exact authority")
        try:
            frame, sample = identity_only_frame(
                remote,
                world_sha256=expected["worldSha256"],
                authority_key=expected["authorityKey"],
                runtime_epoch=expected["runtimeEpoch"],
                renderer_epoch=expected["rendererEpoch"],
            )
            signature = tuple((row["actor"], row["generation"]) for row in frame["actors"])
            if self.last_sample_at is not None:
                if sample < self.last_sample_at:
                    raise CanonicalFeedExposureError("W3 actor snapshot is stale/out-of-order")
                if sample == self.last_sample_at:
                    if signature == self.last_signature:
                        self.replay_rejected += 1
                        return False
                    raise CanonicalFeedExposureError(
                        "W3 actor snapshot changed under a replayed sampleAt"
                    )
            for row in frame["actors"]:
                actor, generation = row["actor"], row["generation"]
                prior = self.last_generation.get(actor)
                if prior is not None and generation < prior:
                    raise CanonicalFeedExposureError(
                        f"W3 actor generation regressed for {actor}"
                    )
            status = self.coordinator.ingest_frame(frame, sample_at=sample)
            checked = validate_canonical_status(status, expected)
        except Exception as exc:
            self.malformed_rejected += 1
            self.clear("P27_CANONICAL_FEED_REJECTED")
            if isinstance(exc, CanonicalFeedExposureError):
                raise
            raise CanonicalFeedExposureError(f"P10 canonical feed ingest failed: {exc}") from exc

        self.latest = checked
        self.last_sample_at = sample
        self.last_signature = signature
        for row in frame["actors"]:
            self.last_generation[row["actor"]] = row["generation"]
        self.last_error = None
        return True

    def exposed(self) -> dict[str, Any] | None:
        return copy.deepcopy(self.latest) if self.latest is not None else None

    def metadata(self) -> dict[str, Any]:
        return {
            "schema": "wof-alpha-p27-canonical-feed-exposure-meta-v1",
            "state": "EXPOSED" if self.latest is not None else "NOT_EXPOSED",
            "identity": copy.deepcopy(self.identity),
            "replayRejected": self.replay_rejected,
            "malformedRejected": self.malformed_rejected,
            "replacementCount": self.replacement_count,
            "lastError": self.last_error,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "legacySpatialFallback": False,
        }


def install_interposer(candidate_root: Path) -> CanonicalFeedExposure:
    root = candidate_root.expanduser().resolve()
    pylaunch = root / "parallel" / "PYLAUNCH"
    if not (pylaunch / "wof_launcher").is_dir():
        raise CanonicalFeedExposureError(f"candidate PYLAUNCH package missing: {pylaunch}")
    if str(pylaunch) not in sys.path:
        sys.path.insert(0, str(pylaunch))

    from wof_launcher.canonical_runtime_coordinator import CanonicalRuntimeCoordinator
    from wof_launcher.render_authority_capture import RenderAuthorityCapture
    from wof_launcher.render_measurement_ui import MeasurementPublisher

    def verified_text(rel: str) -> str:
        path = root / rel
        if not path.is_file():
            raise CanonicalFeedExposureError(f"exact-candidate canonical source missing: {rel}")
        return path.read_text(encoding="utf-8")

    exposure = CanonicalFeedExposure(CanonicalRuntimeCoordinator(verified_text))
    original_ensure = RenderAuthorityCapture.ensure_started
    original_poll = RenderAuthorityCapture.poll
    original_stop = RenderAuthorityCapture.stop_runtime
    original_publish = MeasurementPublisher.publish
    package_version = str(os.environ.get("WOF_ALPHA_ACCEPTANCE_PACKAGE_VERSION") or "").strip() or None

    def ensure_started(capture_self: Any, client: Any, choice: Any, authority_key: str, runtime_epoch: str) -> dict[str, Any]:
        status = original_ensure(capture_self, client, choice, authority_key, runtime_epoch)
        identity = getattr(choice, "identity", None)
        page = getattr(choice, "page", None)
        world = identity.get("sha256") if isinstance(identity, Mapping) else None
        page_target_id = page.get("targetId") if isinstance(page, Mapping) else None
        renderer_epoch = status.get("rendererEpoch") if isinstance(status, Mapping) else None
        try:
            exposure.bind(
                client,
                str(page_target_id or ""),
                world_sha256=str(world or ""),
                authority_key=authority_key,
                runtime_epoch=runtime_epoch,
                renderer_epoch=str(renderer_epoch or ""),
            )
        except Exception:
            exposure.clear("P27_CANONICAL_BIND_FAILED")
        return status

    def poll(capture_self: Any, client: Any, authority_key: str, runtime_epoch: str) -> dict[str, Any]:
        result = original_poll(capture_self, client, authority_key, runtime_epoch)
        remote = result.get("remote") if isinstance(result, Mapping) else None
        if not isinstance(remote, Mapping) or result.get("state") == "ERROR":
            exposure.clear("P27_W3_CAPTURE_UNAVAILABLE")
            return result
        try:
            exposure.consume(remote)
        except CanonicalFeedExposureError:
            pass
        return result

    def stop_runtime(capture_self: Any, client: Any = None) -> None:
        exposure.clear("P27_W3_CAPTURE_STOPPED")
        original_stop(capture_self, client)

    def publish(publisher_self: Any, state: str, **payload: Any) -> None:
        canonical = exposure.exposed()
        prior_payload = getattr(publisher_self, "_payload", None)
        if isinstance(prior_payload, dict):
            prior_payload.pop("canonicalCoordinator", None)
            prior_payload.pop("canonicalOverlay", None)
        routed = dict(payload)
        if canonical is not None:
            routed["canonicalCoordinator"] = canonical
        routed["p27CanonicalFeedExposure"] = exposure.metadata()
        original_publish(publisher_self, state, **routed)

        alpha_status: dict[str, Any] = {
            "renderAuthorityV3": copy.deepcopy(getattr(publisher_self, "_payload", {})),
        }
        update: dict[str, Any] = {
            "alpha_status": alpha_status,
            "alpha_package_version": package_version,
            "alpha_running": False,
            "alpha_runtime_epoch": None,
        }
        if canonical is not None:
            alpha_status["canonicalOverlay"] = canonical
            update["alpha_running"] = canonical.get("active") is True
            update["alpha_runtime_epoch"] = canonical.get("runtimeEpoch")
        publisher_self.store.update(**update)

    RenderAuthorityCapture.ensure_started = ensure_started
    RenderAuthorityCapture.poll = poll
    RenderAuthorityCapture.stop_runtime = stop_runtime
    MeasurementPublisher.publish = publish
    return exposure


def _parse(argv: Sequence[str]) -> tuple[Path, list[str]]:
    values = list(argv)
    if "--" not in values:
        raise CanonicalFeedExposureError("interposer requires -- before the staged runtime command")
    split = values.index("--")
    parser = argparse.ArgumentParser(description="P27 exact-candidate P21 canonical-feed interposer")
    parser.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args(values[:split])
    command = values[split + 1 :]
    if not command:
        raise CanonicalFeedExposureError("staged runtime command missing")
    return args.candidate_root, command


def main(argv: Sequence[str] | None = None) -> int:
    candidate_root, command = _parse(list(argv) if argv is not None else sys.argv[1:])
    install_interposer(candidate_root)
    script = Path(command[0]).expanduser().resolve()
    if not script.is_file():
        raise CanonicalFeedExposureError(f"staged runtime script missing: {script}")
    previous = sys.argv
    sys.argv = [str(script), *command[1:]]
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else (0 if code in (None, "") else 1)
    finally:
        sys.argv = previous
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
