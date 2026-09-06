from __future__ import annotations
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import p43_bounded_zero_click_live_diagnostic as h


def b(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


class FakeGit:
    def __init__(self, blobs, trees=None, commits=None):
        self.blobs = blobs
        self.trees = trees or {}
        self.commits = set(commits or [k[0] for k in blobs])

    def commit_exists(self, commit):
        return commit in self.commits

    def read_blob(self, commit, rel):
        try:
            return self.blobs[(commit, rel)]
        except KeyError:
            raise h.DiagnosticError(f"missing blob {commit}:{rel}")

    def tree(self, commit):
        return self.trees.get(commit, "f" * 40)


class P43Tests(unittest.TestCase):
    def binding_fixture(self):
        meta = "a" * 40
        source = "b" * 40
        cand_path = "candidate.json"
        att_path = "attestation.json"
        man_path = "manifest.json"
        ptr_path = "pointer.json"
        prov_path = "provenance.json"
        candidate = {
            "schema": "wof-owner-oneclick-package-v1",
            "sourceCommit": source,
            "packageVersion": "v1",
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        }
        att = {
            "schema": "wof-alpha-final-canonical-candidate-attestation-v1",
            "sourceCommit": source,
            "packageVersion": "v1",
            "candidatePath": cand_path,
        }
        man = {"schema": "m", "sourceCommit": source, "packageVersion": "v1"}
        cb, mb = b(candidate), b(man)
        att["candidateSha256"] = h.sha256_bytes(cb)
        ab = b(att)
        ptr = {
            "schema": "wof-alpha-latest-final-canonical-candidate-v1",
            "version": 1,
            "state": "READY",
            "sourceCommit": source,
            "packageVersion": "v1",
            "candidatePath": cand_path,
            "candidateSha256": h.sha256_bytes(cb),
            "attestationPath": att_path,
            "attestationSha256": h.sha256_bytes(ab),
            "manifestPath": man_path,
            "manifestSha256": h.sha256_bytes(mb),
            "selectedFileCount": 4,
            "alphaLiveMoved": False,
            "alphaLivePromoted": False,
            "promotionPerformed": False,
        }
        pb = b(ptr)
        prov = {
            "schema": "p",
            "sourceCommit": source,
            "packageVersion": "v1",
            "pointerPath": ptr_path,
            "pointerSha256": h.sha256_bytes(pb),
            "candidatePath": cand_path,
            "candidateSha256": h.sha256_bytes(cb),
            "attestationPath": att_path,
            "attestationSha256": h.sha256_bytes(ab),
            "manifestPath": man_path,
            "manifestSha256": h.sha256_bytes(mb),
            "alphaLiveMoved": False,
            "promotionPerformed": False,
            "runtimePins": {"candidateFiles": []},
        }
        blobs = {
            (meta, ptr_path): pb,
            (meta, prov_path): b(prov),
            (meta, cand_path): cb,
            (meta, att_path): ab,
            (meta, man_path): mb,
        }
        return FakeGit(blobs, commits={meta, source}), meta, source, ptr_path, prov_path, blobs

    def test_exact_candidate_binding_records_hash_and_blob(self):
        git, meta, source, ptr, prov, blobs = self.binding_fixture()
        out = h.verify_candidate_binding(git, metadata_commit=meta, source_commit=source, pointer_path=ptr, provenance_path=prov)
        self.assertEqual("PASS", out["state"])
        self.assertEqual(source, out["sourceCommit"])
        self.assertEqual(h.sha256_bytes(blobs[(meta, "candidate.json")]), out["candidate"]["sha256"])
        self.assertEqual(h.git_blob_sha(blobs[(meta, "candidate.json")]), out["candidate"]["gitBlobSha"])
        self.assertEqual("v1", out["packageVersion"])

    def test_candidate_sha_mismatch_fails_closed(self):
        git, meta, source, ptr, prov, blobs = self.binding_fixture()
        pointer = json.loads(blobs[(meta, ptr)])
        pointer["candidateSha256"] = "0" * 64
        badpb = b(pointer)
        provenance = json.loads(blobs[(meta, prov)])
        provenance["pointerSha256"] = h.sha256_bytes(badpb)
        blobs[(meta, ptr)] = badpb
        blobs[(meta, prov)] = b(provenance)
        with self.assertRaisesRegex(h.DiagnosticError, "candidate SHA-256 mismatch"):
            h.verify_candidate_binding(git, metadata_commit=meta, source_commit=source, pointer_path=ptr, provenance_path=prov)

    def test_gate_timeline_answers_first_failure_and_prior_success(self):
        g = h.GateLedger()
        g.transition("CANDIDATE_BINDING", "PASS", "ok")
        g.transition("ASSOCIATION", "PASS", "ok")
        g.transition("P16", "BLOCKED", "missing")
        g.transition("P36", "BLOCKED", "not reached")
        first = g.first_failure()
        self.assertEqual("P16", first["gate"])
        self.assertEqual(["CANDIDATE_BINDING", "ASSOCIATION"], g.passed_before_first_failure())

    def test_p16_exact_association_and_runtime_binding(self):
        binding = {"packageVersion": "v1"}
        assoc = {"pageTargetId": "page-a", "workerTargetId": "worker-a"}
        raw = {
            "schema": h.P16_SCHEMA,
            "version": 1,
            "packageVersion": "v1",
            "visibleProof": "NOT_PROVEN",
            "world": {"accepted": True, "sha256": h.EXPECTED_WORLD_SHA256, "pageTargetId": "page-a", "workerTargetId": "worker-a"},
            "runtime": {"epoch": "runtime-1234567890", "rendererEpoch": "renderer-1234567890", "authorityKey": "auth", "rendererAuthority": {"kind": "x"}},
            "canonical": {"state": "HUD_INGEST_ACCEPTED", "reason": "ok"},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        }
        ok, reason, identity = h.validate_p16(raw, binding, assoc)
        self.assertTrue(ok)
        self.assertEqual("USABLE", reason)
        self.assertEqual("auth", identity["authorityKey"])
        raw["world"]["pageTargetId"] = "wrong"
        ok, reason, _ = h.validate_p16(raw, binding, assoc)
        self.assertFalse(ok)
        self.assertEqual("P16_PAGE_TARGET_MISMATCH", reason)

    def test_p17_preserves_actual_decision_instead_of_generic_mismatch(self):
        binding = {"sourceCommit": "b" * 40, "packageVersion": "v1", "candidate": {"sha256": "c" * 64}}
        base = {
            "schema": h.P17_SCHEMA,
            "candidate": {"sourceCommit": "b" * 40, "packageVersion": "v1", "contentSha256": "c" * 64},
            "visibleProof": "NOT_PROVEN",
            "safety": {"alphaLiveMoved": False},
        }
        raw = dict(base, automaticDecision="W3_INCONCLUSIVE")
        self.assertEqual(("BLOCKED", "W3_INCONCLUSIVE"), h.validate_p17(raw, binding))
        raw = dict(base, automaticDecision="READY_FOR_OWNER_VISUAL_CONFIRMATION")
        self.assertEqual(("PASS", "READY_FOR_OWNER_VISUAL_CONFIRMATION"), h.validate_p17(raw, binding))
        raw = dict(base, automaticDecision="FAILED_EVIDENCE_MISMATCH")
        self.assertEqual(("FAIL", "FAILED_EVIDENCE_MISMATCH"), h.validate_p17(raw, binding))

    def test_p39_summary_records_visible_stale_lost_ambiguous_reacquire(self):
        raw = {
            "schema": "wof-alpha-auto-baseline-visible-hud-v1",
            "state": "READY",
            "enabled": True,
            "visiblePlayers": ["P1"],
            "controller": {
                "visibleFresh": False,
                "state": "STALE_OR_UNAVAILABLE",
                "tracks": {
                    "P1": {"state": "TRACKED", "reacquireCount": 2, "x": 10, "y": 20},
                    "P2": {"state": "LOST", "reacquireCount": 1},
                    "P3": {"state": "AMBIGUOUS", "reacquireCount": 0, "ambiguityReason": "MULTIPLE"},
                },
            },
            "rendererSourceProof": None,
            "productAuthority": "NONE_DIAGNOSTIC_ONLY",
        }
        out = h.summarize_p39(raw)
        self.assertEqual(h.P37_CLASSIFICATION, out["classification"])
        self.assertTrue(out["players"]["P1"]["visible"])
        self.assertTrue(out["players"]["P1"]["stale"])
        self.assertEqual(2, out["players"]["P1"]["reacquireCount"])
        self.assertTrue(out["players"]["P2"]["lost"])
        self.assertTrue(out["players"]["P3"]["ambiguous"])
        self.assertFalse(out["authorityEligible"])

    def test_p42_absence_and_present_are_explicit(self):
        absent = h.classify_p42_snapshot({"present": False, "searched": ["X"]})
        self.assertEqual("P42_CORRELATION_PROBE_NOT_PRESENT", absent["state"])
        present = h.classify_p42_snapshot({"present": True, "surface": "WOFCorrelationProbe", "bundle": {"schema": h.P42_SCHEMA}})
        self.assertEqual("P42_CORRELATION_PROBE_PRESENT", present["state"])
        self.assertFalse(present["authorityEligible"])

    def test_actor_generation_pairs_use_only_explicit_generation_bound_events(self):
        bundle = {"events": [
            {"actorAssociation": {"player": "P2", "generation": "g2", "explicit": True, "generationBound": True}},
            {"actorAssociation": {"player": "P1", "generation": "g1", "explicit": True, "generationBound": True}},
            {"actorAssociation": {"player": "P1", "generation": "guess", "explicit": False, "generationBound": True}},
            {"actorAssociation": {"player": "P3", "generation": "g3", "explicit": True, "generationBound": False}},
        ]}
        self.assertEqual([("P1", "g1"), ("P2", "g2")], h.actor_generation_pairs(bundle))

    def test_raw_log_archive_is_bounded_and_hashed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.log"
            source.write_bytes(b"0123456789")
            out = root / "out"
            out.mkdir()
            rec = h.archive_file(out, source, "raw/log.log", max_bytes=4)
            self.assertTrue(rec["truncated"])
            self.assertEqual(6, rec["sourceOffset"])
            self.assertEqual(b"6789", (out / "raw/log.log").read_bytes())
            self.assertEqual(hashlib.sha256(b"6789").hexdigest(), rec["sha256"])

    def test_human_receipt_directly_answers_first_failure(self):
        receipt = {
            "schema": h.RECEIPT_SCHEMA,
            "candidateBinding": {"sourceCommit": "b" * 40, "packageVersion": "v1"},
            "firstFailingGate": {"gate": "P36_SOURCE_GATE", "state": "BLOCKED", "reason": "EXACT_DIRECT_RENDERER_SOURCE_SURFACE_NOT_EXPOSED"},
            "passedBeforeFirstFailure": ["CANDIDATE_BINDING", "P16_GATE", "P9_GATE"],
            "p42": {"state": "P42_CORRELATION_PROBE_NOT_PRESENT"},
            "p36": {"teardownReason": "P43_BOUNDED_TEARDOWN"},
            "safety": {"alphaLiveMoved": False},
            "gateTimeline": [],
            "artifacts": {},
        }
        text = h.build_human_receipt(receipt)
        self.assertIn("P36_SOURCE_GATE", text)
        self.assertIn("CANDIDATE_BINDING, P16_GATE, P9_GATE", text)
        self.assertIn("P42_CORRELATION_PROBE_NOT_PRESENT", text)

    def test_p36_raw_source_probe_contains_rejection_reason_contract(self):
        expr = h._p36_source_discovery_expr()
        self.assertIn("rejectionReasons", expr)
        self.assertIn("DIRECT_SOURCE_DERIVATION_UNQUALIFIED", expr)
        self.assertIn("SOURCE_TRACE_INCOMPLETE", expr)
        self.assertIn("ownerSelectionRequired", expr)


if __name__ == "__main__":
    unittest.main()
