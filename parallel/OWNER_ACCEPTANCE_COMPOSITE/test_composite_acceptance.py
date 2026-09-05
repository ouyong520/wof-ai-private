from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import composite_acceptance as c

CANDIDATE = {"sourceCommit": "a" * 40, "packageVersion": "2026.09.05.fixture", "candidateSha256": "b" * 64, "attestationSha256": "c" * 64}
IDENTITY = {"worldSha256": c.WORLD_SHA256, "pageTargetId": "page-1", "authorityKey": "authority-1",
            "runtimeEpoch": "runtime-0123456789abcdef", "rendererEpoch": "renderer-0123456789abcdef"}


def anchor(state="READY", x=100, y=70):
    base = {"schema": "wof-render-object-anchor-v1", "state": state, "nativeWidth": 384, "nativeHeight": 224,
            "worldSha256": c.WORLD_SHA256, "authorityKey": IDENTITY["authorityKey"], "runtimeEpoch": IDENTITY["runtimeEpoch"],
            "rendererEpoch": IDENTITY["rendererEpoch"], "readOnly": True, "ramWrites": 0, "inputInjection": False}
    if state == "READY":
        base.update({"anchor": {"x": x, "y": y}, "bodyBounds": {"left": x-8, "top": y-20, "right": x+8, "bottom": y+4}})
    else:
        base["reason"] = "ACTOR_NOT_VISIBLE"
    return base


def status(sequence=1, state="READY", sample_at=1000.0, x=100):
    row = {"kind": "player", "actor": "P1", "generation": 1, "sampleAt": sample_at,
           **{k: IDENTITY[k] for k in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch")},
           "canonicalAnchor": anchor(state, x=x)}
    return {"schema": c.CANONICAL_SCHEMA, "state": "READY", **IDENTITY, "legacySpatialFallback": False,
            "readOnly": True, "ramWrites": 0, "inputInjection": False, "bridge": {"lastPayload": {"sequence": sequence, "records": [row]}}}


class FakeP22:
    def __init__(self): self.cycles = []
    def record_cycle(self, runtime_status, **_): self.cycles.append(json.loads(json.dumps(runtime_status)))


class CompositeTests(unittest.TestCase):
    def test_exact_candidate_run_record(self):
        r = c.new_run_record(CANDIDATE, run_nonce="0123456789abcdef"*2)
        self.assertEqual(r["candidate"]["sourceCommit"], "a"*40); self.assertFalse(r["alphaLiveMoved"])

    def test_ready_feeds_p22_and_p24(self):
        rec = FakeP22(); acc = c.CaptureAccumulator(c.new_run_record(CANDIDATE, run_nonce="1"*32), rec)
        self.assertTrue(acc.consume({"snapshot": {"alpha_status": {"canonicalOverlay": status()}}}))
        self.assertEqual(len(rec.cycles), 1); self.assertEqual(acc.observations[0]["canonicalGeometry"]["coordinateAuthority"], "canonical-render-object-only")

    def test_suppressed_never_carries_coordinates(self):
        obs = c.temporal_observations_from_status(status(state="SUPPRESSED"), first_sample_seq=0)[0]
        self.assertIsNone(obs["canonicalGeometry"])
        bad = status(state="SUPPRESSED"); bad["bridge"]["lastPayload"]["records"][0]["canonicalAnchor"]["anchor"] = {"x": 1, "y": 1}
        with self.assertRaises(c.CompositeError): c.temporal_observations_from_status(bad, first_sample_seq=0)

    def test_duplicate_and_out_of_order_fail_closed(self):
        rec = FakeP22(); run = c.new_run_record(CANDIDATE, run_nonce="2"*32); acc = c.CaptureAccumulator(run, rec)
        self.assertTrue(acc.consume({"snapshot": {"alpha_status": {"canonicalOverlay": status(sequence=2, sample_at=2)}}}))
        self.assertFalse(acc.consume({"snapshot": {"alpha_status": {"canonicalOverlay": status(sequence=2, sample_at=2)}}}))
        self.assertFalse(acc.consume({"snapshot": {"alpha_status": {"canonicalOverlay": status(sequence=1, sample_at=3)}}}))
        self.assertEqual(run["capture"]["duplicateSnapshotsRejected"], 1); self.assertEqual(run["capture"]["outOfOrderSnapshotsRejected"], 1)

    def test_renderer_and_page_replacement_are_explicit(self):
        rec = FakeP22(); run = c.new_run_record(CANDIDATE, run_nonce="3"*32); acc = c.CaptureAccumulator(run, rec)
        acc.consume({"snapshot": {"alpha_status": {"canonicalOverlay": status()}}})
        changed = status(sample_at=4); changed["pageTargetId"] = "page-2"; changed["rendererEpoch"] = "renderer-replaced-123"
        changed["bridge"]["lastPayload"]["records"][0]["rendererEpoch"] = changed["rendererEpoch"]
        changed["bridge"]["lastPayload"]["records"][0]["canonicalAnchor"]["rendererEpoch"] = changed["rendererEpoch"]
        acc.consume({"snapshot": {"alpha_status": {"canonicalOverlay": changed}}})
        self.assertEqual(len(run["identityTransitions"]), 1)

    def test_runtime_override_restores_on_cancel(self):
        class P21: pass
        p21 = P21(); original = lambda *a: ["original"]; replacement = lambda *a: ["replacement"]; p21.build_runtime_command = original
        old_nonce = os.environ.get("WOF_ALPHA_P25_RUN_NONCE"); old_ring = os.environ.get("WOF_ALPHA_P25_STATUS_RING")
        with self.assertRaises(RuntimeError):
            with c.p21_runtime_override(p21, replacement, run_nonce="5"*32, ring_path=Path("ring.json")):
                raise RuntimeError("fixture timeout/cancel")
        self.assertIs(p21.build_runtime_command, original); self.assertEqual(os.environ.get("WOF_ALPHA_P25_RUN_NONCE"), old_nonce); self.assertEqual(os.environ.get("WOF_ALPHA_P25_STATUS_RING"), old_ring)

    def test_p17_candidate_mismatch_rejected(self):
        with self.assertRaises(c.CompositeError): c.validate_p17_candidate({"candidate": {"sourceCommit": "d"*40, "packageVersion": CANDIDATE["packageVersion"], "candidateSha256": CANDIDATE["candidateSha256"]}}, CANDIDATE)

    def test_hash_binding(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"x.json"; p.write_text('{"a":1}\n', encoding="utf-8"); self.assertEqual(c.evidence_ref(p)["sha256"], c.sha256_file(p))

    def test_source_forbidden_scan(self):
        source = Path(c.__file__).read_text(encoding="utf-8")
        for token in ("Page.captureScreenshot", "Stop-Process -Id", "checkout alpha-live", "update-ref refs/heads/alpha-live", 'inputInjection": True'):
            self.assertNotIn(token, source)


if __name__ == "__main__": unittest.main()
