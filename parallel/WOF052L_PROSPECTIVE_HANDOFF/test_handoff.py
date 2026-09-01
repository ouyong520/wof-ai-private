from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import handoff

CANDIDATE = "S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736"
NEXT_A = "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736"
NEXT_B = "S0/A2/B0|BODY4728|FE8b660|NX8b204|Vffff|TM3|P6C4736"


def resolved_analysis(feature="exact_tail2", pattern=None, outcome="A4704"):
    if pattern is None:
        pattern = f"{CANDIDATE} -> {NEXT_A}"
    return {
        "schema": handoff.ANALYSIS_SCHEMA,
        "generatedAt": "2026-09-01T12:00:00Z",
        "safety": {
            "analysisReadOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "productionRuleAutoPromotion": False,
            "inputSafetyViolations": [],
        },
        "identity": {
            "required": handoff.WORLD,
            "requiredSha256": handoff.WORLD_SHA256,
            "observedSha256": [handoff.WORLD_SHA256],
            "known": True,
            "ok": True,
        },
        "t18": {
            "guardrail": {"singleStateA4704SpecificPromotionForbidden": True},
            "verdict": "resolved",
            "distribution": {"A4704": 2, "A4712": 2},
            "thresholds": {
                "minCandidateCyclesPerOutcome": 2,
                "minExclusiveSequenceSupport": 2,
            },
            "prospectiveValidator": {
                "worthEntering": True,
                "candidate": {
                    "outcome": outcome,
                    "feature": feature,
                    "pattern": pattern,
                    "support": 2,
                    "oppositeSupport": 0,
                    "purity": 1.0,
                    "exclusive": True,
                },
            },
        },
    }


class HandoffTests(unittest.TestCase):
    def test_exact_tail2_manifest_is_research_only(self):
        analysis = resolved_analysis()
        ready, reasons, candidate = handoff.evaluate_analysis(analysis)
        self.assertTrue(ready, reasons)
        manifest = handoff.build_manifest(analysis, "a" * 64, candidate, "2026-09-01T12:00:01.000Z")
        self.assertEqual(manifest["promotion"], "research-only")
        self.assertEqual(manifest["outcome"]["expectedAttacks"], [4704])
        self.assertEqual(manifest["rule"]["sequence"]["kind"], "tail2")
        self.assertEqual(manifest["rule"]["sequence"]["states"][0]["signature"], CANDIDATE)
        self.assertEqual(manifest["rule"]["currentPredicates"], [{"path": "type", "op": "eq", "value": 18}])
        self.assertFalse(manifest["safety"]["productionPromotionAllowed"])

    def test_tm_triple_uses_family_matchers(self):
        p = " -> ".join([
            CANDIDATE.replace("TM1", "TM*"),
            NEXT_A.replace("TM2", "TM*"),
            NEXT_B.replace("TM3", "TM*"),
        ])
        analysis = resolved_analysis(feature="tm_triple", pattern=p, outcome="A4712")
        ready, reasons, candidate = handoff.evaluate_analysis(analysis)
        self.assertTrue(ready, reasons)
        manifest = handoff.build_manifest(analysis, "b" * 64, candidate, "2026-09-01T12:00:01.000Z")
        self.assertEqual(manifest["rule"]["sequence"]["kind"], "triple")
        self.assertTrue(all("family" in x for x in manifest["rule"]["sequence"]["states"]))
        self.assertEqual(manifest["outcome"]["expectedAttacks"], [4712])

    def test_insufficient_never_generates_manifest(self):
        analysis = resolved_analysis()
        analysis["t18"]["verdict"] = "insufficient"
        analysis["t18"]["prospectiveValidator"]["worthEntering"] = False
        ready, reasons, _ = handoff.evaluate_analysis(analysis)
        self.assertFalse(ready)
        self.assertTrue(any("仍不足" in x for x in reasons))

    def test_single_state_final_is_rejected(self):
        analysis = resolved_analysis(feature="exact_final", pattern=NEXT_A)
        ready, reasons, _ = handoff.evaluate_analysis(analysis)
        self.assertFalse(ready)
        self.assertTrue(any("ordered" in x for x in reasons))

    def test_opposite_support_blocks_handoff(self):
        analysis = resolved_analysis()
        analysis["t18"]["prospectiveValidator"]["candidate"]["oppositeSupport"] = 1
        ready, reasons, _ = handoff.evaluate_analysis(analysis)
        self.assertFalse(ready)
        self.assertTrue(any("oppositeSupport" in x for x in reasons))

    def test_wrong_identity_blocks_handoff(self):
        analysis = resolved_analysis()
        analysis["identity"]["observedSha256"] = ["deadbeef"]
        analysis["identity"]["ok"] = False
        ready, reasons, _ = handoff.evaluate_analysis(analysis)
        self.assertFalse(ready)
        self.assertTrue(any("identity" in x or "observedSha256" in x for x in reasons))

    def test_prepare_writes_waiting_status_only_when_insufficient(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            analysis_path = root / "analysis.json"
            output_dir = root / "out"
            analysis = resolved_analysis()
            analysis["t18"]["verdict"] = "insufficient"
            analysis["t18"]["prospectiveValidator"]["worthEntering"] = False
            analysis_path.write_text(json.dumps(analysis), encoding="utf-8")
            status, manifest_path = handoff.prepare_from_analysis(analysis_path, output_dir)
            self.assertEqual(status["status"], handoff.WAITING)
            self.assertIsNone(manifest_path)
            self.assertFalse(output_dir.exists())

    def test_prepare_freezes_manifest_and_sha(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            analysis_path = root / "analysis.json"
            output_dir = root / "out"
            analysis_path.write_text(json.dumps(resolved_analysis()), encoding="utf-8")
            status, manifest_path = handoff.prepare_from_analysis(analysis_path, output_dir)
            self.assertEqual(status["status"], handoff.READY)
            self.assertIsNotNone(manifest_path)
            manifest = handoff.load_json(manifest_path)
            self.assertEqual(status["candidate"]["manifestSha256"], handoff.candidate_sha256(manifest))
            self.assertEqual(status["candidate"]["frozenAt"], manifest["provenance"]["handoffFrozenAt"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
