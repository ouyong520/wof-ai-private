#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import repository_preflight_current as current
import test_repository_preflight as fixtures


class AcceptanceCurrentMandatoryGateTests(unittest.TestCase):
    def test_player_head_requirement_makes_integration_mandatory_and_current(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            requirement = root / current.PLAYER_HEAD_REQUIREMENT
            requirement.parent.mkdir(parents=True, exist_ok=True)
            requirement.write_text("AUTHORITATIVE ALPHA V1 PRODUCT REQUIREMENT", encoding="utf-8")

            blobs = {"product/alpha/wof_alpha_player_head_warning.js": "current"}
            resolve = lambda rel: blobs[rel]

            ok, detail = current._check_player_head_warning(root, resolve)
            self.assertFalse(ok)
            self.assertIn("缺少", detail)

            claim_path = root / current.PLAYER_HEAD_CLAIM
            claim_path.parent.mkdir(parents=True, exist_ok=True)
            claim_path.write_text(json.dumps({
                "state": "COMPLETE",
                "result": current.PLAYER_HEAD_PASS,
                "productBlobs": {
                    "product/alpha/wof_alpha_player_head_warning.js": "current"
                },
            }, ensure_ascii=False), encoding="utf-8")

            ok, detail = current._check_player_head_warning(root, resolve)
            self.assertTrue(ok, detail)

            blobs["product/alpha/wof_alpha_player_head_warning.js"] = "drifted"
            ok, detail = current._check_player_head_warning(root, resolve)
            self.assertFalse(ok)
            self.assertIn("blob 已漂移", detail)

    def test_head_labels_blocked_v2_is_superseded_by_current_v3_pass(self):
        fixture = fixtures.AcceptanceSupersedingGatePolicyTests(
            methodName="test_historical_formal_blocked_is_superseded_by_current_pass"
        )
        fixture.setUp()
        try:
            qa_v2 = fixture._read(current.base.HEAD_LABEL_QA_CLAIM)
            qa_v2.update({
                "state": "BLOCKED",
                "result": "BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V2 — historical blocker",
            })
            fixture._write(current.base.HEAD_LABEL_QA_CLAIM, qa_v2)
            fixture._write(
                "parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3.json",
                {
                    "state": "COMPLETE",
                    "result": "PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V3 — DRAWING-BUFFER EPOCH FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED",
                    "evidence": {"helperBlob": "labels-current"},
                },
            )
            ok, blockers, gates = current.release_gate(
                fixture.root, fixture._blob, run_offline=False
            )
            self.assertTrue(ok, blockers)
            head = next(g for g in gates if g["name"] == "enemyTargetHeadLabels")
            self.assertTrue(head["pass"])
            self.assertIn("V3", head["tail"])
        finally:
            fixture.tearDown()

    def test_formal_blocked_v1_is_superseded_by_current_v2_pass(self):
        fixture = fixtures.AcceptanceSupersedingGatePolicyTests(
            methodName="test_historical_formal_blocked_is_superseded_by_current_pass"
        )
        fixture.setUp()
        try:
            fixture.blobs["product/alpha/wof_alpha_enemy_head_projection.json"] = "projection-current"
            formal_v1 = fixture._read(current.base.FORMAL_CLAIM)
            formal_v1.update({"state": "BLOCKED", "result": "BLOCKED"})
            fixture._write(current.base.FORMAL_CLAIM, formal_v1)
            fixture._write(
                "parallel/PM/STAGE_CLAIMS/ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION_V2.json",
                {
                    "state": "COMPLETE",
                    "result": "PASS",
                    "audited_blobs": {
                        path: fixture.blobs[path]
                        for path in current.base.FORMAL_FRESH_PATHS
                    },
                },
            )
            ok, blockers, gates = current.release_gate(
                fixture.root, fixture._blob, run_offline=False
            )
            self.assertTrue(ok, blockers)
            formal = next(g for g in gates if g["name"] == "formalCurrentBlob")
            self.assertTrue(formal["pass"])
            self.assertIn("V2", formal["tail"])
        finally:
            fixture.tearDown()

    def test_old_snapshot_without_requirement_is_not_backfilled(self):
        with tempfile.TemporaryDirectory() as td:
            ok, detail = current._check_player_head_warning(Path(td), lambda rel: "unused")
            self.assertTrue(ok, detail)
            self.assertIn("不反向施加未来 gate", detail)


if __name__ == "__main__":
    unittest.main()
