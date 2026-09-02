#!/usr/bin/env python3
from __future__ import annotations

import unittest

import repository_preflight as rp


class AcceptanceSuccessorSchemaCompatibilityTests(unittest.TestCase):
    def test_head_labels_v2_evidence_helper_blob_is_consumed_as_currentness_pin(self):
        pins = rp._extract_blob_map({
            "evidence": {
                "helperBlob": "helper-sha",
                "projectionBlob": "projection-sha",
            }
        })
        self.assertEqual(pins[rp.HEAD_LABEL_PRODUCT], "helper-sha")
        self.assertEqual(
            pins["product/alpha/wof_alpha_enemy_head_projection.json"],
            "projection-sha",
        )


if __name__ == "__main__":
    unittest.main()
