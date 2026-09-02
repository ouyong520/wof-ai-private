#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import repository_preflight_current as current


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

    def test_old_snapshot_without_requirement_is_not_backfilled(self):
        with tempfile.TemporaryDirectory() as td:
            ok, detail = current._check_player_head_warning(Path(td), lambda rel: "unused")
            self.assertTrue(ok, detail)
            self.assertIn("不反向施加未来 gate", detail)


if __name__ == "__main__":
    unittest.main()
