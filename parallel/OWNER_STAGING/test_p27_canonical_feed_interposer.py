from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("p27_canonical_feed_interposer.py")
spec = importlib.util.spec_from_file_location("p27_canonical_feed_interposer", MODULE_PATH)
assert spec and spec.loader
p27 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p27)

AUTHORITY = "authority:test"
RUNTIME = "1" * 32
RENDERER = "2" * 32
PAGE = "page-1"


def remote(sample_at=1000, *, renderer=RENDERER, p1_generation=3):
    return {
        "schema": p27.CAPTURE_SCHEMA,
        "worldSha256": p27.WORLD_SHA256,
        "authorityKey": AUTHORITY,
        "runtimeEpoch": RUNTIME,
        "rendererEpoch": renderer,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "overlayEnabled": False,
        "rendererSourceQualification": "UNVERIFIED_CANDIDATE_ONLY",
        "actors": {
            "sampleAt": sample_at,
            "players": [
                {"name": "P1", "generation": p1_generation, "x": 101.25, "y": 55.5, "z": 0.0},
                {"name": "P2", "generation": 1, "x": 22.0, "y": 11.0, "z": 0.0},
            ],
            "enemies": [
                {"slot": 4, "generation": 7, "x": 200.0, "y": 90.0, "z": 0.0},
            ],
            "ramBase": 123,
        },
    }


class FakeCoordinator:
    def __init__(self):
        self.active = None
        self.frames = []
        self.revokes = []

    def revoke(self, reason):
        self.revokes.append(reason)
        self.active = None
        return {"schema": p27.CANONICAL_SCHEMA, "active": False}

    def activate(self, _client, page_target_id, *, authority_key, runtime_epoch, world_sha256, capability_present):
        assert capability_present is True
        self.active = {
            "worldSha256": world_sha256,
            "pageTargetId": page_target_id,
            "authorityKey": authority_key,
            "runtimeEpoch": runtime_epoch,
        }
        return {"schema": p27.CANONICAL_SCHEMA, "active": True}

    def ingest_frame(self, frame, *, sample_at):
        self.frames.append((frame, sample_at))
        renderer = frame["rendererEpoch"]
        records = []
        for row in frame["actors"]:
            records.append({
                "kind": row["kind"],
                "actor": row["actor"],
                "generation": row["generation"],
                "sampleAt": sample_at,
                "worldSha256": frame["worldSha256"],
                "authorityKey": frame["authorityKey"],
                "runtimeEpoch": frame["runtimeEpoch"],
                "rendererEpoch": renderer,
                "canonicalAnchor": {
                    "schema": "wof-render-object-anchor-v1",
                    "state": "SUPPRESSED",
                    "reason": "RENDERER_SOURCE_UNPROVEN",
                    "nativeWidth": 384,
                    "nativeHeight": 224,
                    "readOnly": True,
                    "ramWrites": 0,
                    "inputInjection": False,
                },
            })
        return {
            "schema": p27.CANONICAL_SCHEMA,
            "state": "SUPPRESSED",
            "reason": "RENDERER_SOURCE_UNPROVEN",
            "active": True,
            "worldSha256": frame["worldSha256"],
            "pageTargetId": PAGE,
            "authorityKey": frame["authorityKey"],
            "runtimeEpoch": frame["runtimeEpoch"],
            "rendererEpoch": renderer,
            "legacySpatialFallback": False,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "bridge": {"lastPayload": {"records": records}},
        }


class P27CanonicalFeedExposureTests(unittest.TestCase):
    def test_identity_only_frame_never_copies_w3_coordinates(self):
        frame, sample = p27.identity_only_frame(
            remote(),
            world_sha256=p27.WORLD_SHA256,
            authority_key=AUTHORITY,
            runtime_epoch=RUNTIME,
            renderer_epoch=RENDERER,
        )
        self.assertEqual(sample, 1000.0)
        self.assertFalse(frame["rendererSource"]["proven"])
        self.assertEqual([r["actor"] for r in frame["actors"]], ["P1", "P2", "enemy-slot-4"])
        text = repr(frame)
        for forbidden in ("'x':", "'y':", "'z':", "bodyBounds", "'parts':", "candidateRegions"):
            self.assertNotIn(forbidden, text)
        for row in frame["actors"]:
            self.assertTrue(row["association"]["proven"])
            self.assertFalse(row["association"]["ambiguous"])
            self.assertEqual(row["association"]["candidateCount"], 1)

    def test_real_exposure_shape_is_p10_coordinator_not_v3_status(self):
        fake = FakeCoordinator()
        exposure = p27.CanonicalFeedExposure(fake)
        exposure.bind(
            object(), PAGE, world_sha256=p27.WORLD_SHA256,
            authority_key=AUTHORITY, runtime_epoch=RUNTIME, renderer_epoch=RENDERER,
        )
        self.assertTrue(exposure.consume(remote()))
        status = exposure.exposed()
        self.assertEqual(status["schema"], p27.CANONICAL_SCHEMA)
        self.assertEqual(status["pageTargetId"], PAGE)
        self.assertEqual(status["rendererEpoch"], RENDERER)
        records = status["bridge"]["lastPayload"]["records"]
        self.assertEqual(len(records), 3)
        self.assertTrue(all(r["canonicalAnchor"]["state"] == "SUPPRESSED" for r in records))
        self.assertTrue(all("anchor" not in r["canonicalAnchor"] for r in records))

    def test_replay_is_not_accepted_as_a_new_cycle(self):
        fake = FakeCoordinator()
        exposure = p27.CanonicalFeedExposure(fake)
        exposure.bind(
            object(), PAGE, world_sha256=p27.WORLD_SHA256,
            authority_key=AUTHORITY, runtime_epoch=RUNTIME, renderer_epoch=RENDERER,
        )
        self.assertTrue(exposure.consume(remote(1000)))
        self.assertFalse(exposure.consume(remote(1000)))
        self.assertEqual(len(fake.frames), 1)
        self.assertEqual(exposure.metadata()["replayRejected"], 1)

    def test_stale_renderer_epoch_fails_closed_and_clears_old_feed(self):
        fake = FakeCoordinator()
        exposure = p27.CanonicalFeedExposure(fake)
        exposure.bind(
            object(), PAGE, world_sha256=p27.WORLD_SHA256,
            authority_key=AUTHORITY, runtime_epoch=RUNTIME, renderer_epoch=RENDERER,
        )
        self.assertTrue(exposure.consume(remote(1000)))
        with self.assertRaises(p27.CanonicalFeedExposureError):
            exposure.consume(remote(1250, renderer="9" * 32))
        self.assertIsNone(exposure.exposed())
        self.assertIsNone(exposure.identity)
        self.assertIn("P27_CANONICAL_FEED_REJECTED", fake.revokes)

    def test_generation_regression_fails_closed(self):
        fake = FakeCoordinator()
        exposure = p27.CanonicalFeedExposure(fake)
        exposure.bind(
            object(), PAGE, world_sha256=p27.WORLD_SHA256,
            authority_key=AUTHORITY, runtime_epoch=RUNTIME, renderer_epoch=RENDERER,
        )
        self.assertTrue(exposure.consume(remote(1000, p1_generation=3)))
        with self.assertRaises(p27.CanonicalFeedExposureError):
            exposure.consume(remote(1250, p1_generation=2))
        self.assertIsNone(exposure.exposed())

    def test_suppressed_payload_with_coordinates_is_rejected(self):
        status = FakeCoordinator().ingest_frame(
            p27.identity_only_frame(
                remote(), world_sha256=p27.WORLD_SHA256, authority_key=AUTHORITY,
                runtime_epoch=RUNTIME, renderer_epoch=RENDERER,
            )[0],
            sample_at=1000,
        )
        status["bridge"]["lastPayload"]["records"][0]["canonicalAnchor"]["anchor"] = {"x": 1, "y": 2}
        expected = {
            "worldSha256": p27.WORLD_SHA256,
            "pageTargetId": PAGE,
            "authorityKey": AUTHORITY,
            "runtimeEpoch": RUNTIME,
            "rendererEpoch": RENDERER,
        }
        with self.assertRaises(p27.CanonicalFeedExposureError):
            p27.validate_canonical_status(status, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
