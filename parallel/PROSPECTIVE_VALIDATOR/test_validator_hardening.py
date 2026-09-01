import copy
import unittest

import validator


class ValidatorHardeningTests(unittest.TestCase):
    def manifest(self):
        return {
            "schema": validator.MANIFEST_SCHEMA,
            "promotion": "research-only",
            "id": "hardening-test",
            "rule": {"currentPredicates": [{"path": "state99", "op": "eq", "value": 1}]},
            "outcome": {"expectedAttacks": [100]},
            "windows": {"strictMaxMs": 100, "jitterMaxMs": 150, "lateMaxMs": 250, "hardMissMs": 500},
            "gate": {
                "minProspectiveSignals": 2,
                "minProspectiveRooms": 2,
                "requireZeroHardMiss": True,
                "minDistinctTargets": 2,
                "minObservedTypes": 2,
                "requireLifecycleReset": True,
            },
        }

    def trace(self, room, target, enemy_type, *, lifecycle=False, attack=100):
        return {
            "evidenceClass": "prospective",
            "roomId": room,
            "activeAttack": attack,
            "leadMs": 50,
            "current": {"state99": 1, "target7E": target, "type": enemy_type},
            "targetStart7E": target,
            "type": enemy_type,
            "lifecycleReset": lifecycle,
        }

    def full_set(self):
        return [
            self.trace("room-a", 0, 9, lifecycle=True),
            self.trace("room-b", 4, 33),
        ]

    def test_all_declared_gates_satisfied_is_research_only_pass(self):
        result = validator.validate(self.manifest(), self.full_set())
        self.assertEqual(result["verdict"], "PROSPECTIVE_PASS_RESEARCH_ONLY")
        self.assertFalse(result["productionPromotionAllowed"])
        for name in validator.SUPPORTED_GATES:
            self.assertIn("required", result["gate"][name])
            self.assertIn("observed", result["gate"][name])
            self.assertTrue(result["gate"][name]["passed"])

    def test_target_shortfall_is_insufficient(self):
        rows = [self.trace("room-a", 0, 9, lifecycle=True), self.trace("room-b", 0, 33)]
        result = validator.validate(self.manifest(), rows)
        self.assertEqual(result["verdict"], "PROSPECTIVE_FAIL_OR_INSUFFICIENT")
        self.assertFalse(result["gate"]["minDistinctTargets"]["passed"])

    def test_observed_type_shortfall_is_insufficient(self):
        rows = [self.trace("room-a", 0, 9, lifecycle=True), self.trace("room-b", 4, 9)]
        result = validator.validate(self.manifest(), rows)
        self.assertEqual(result["verdict"], "PROSPECTIVE_FAIL_OR_INSUFFICIENT")
        self.assertFalse(result["gate"]["minObservedTypes"]["passed"])

    def test_lifecycle_reset_shortfall_is_insufficient(self):
        rows = [self.trace("room-a", 0, 9), self.trace("room-b", 4, 33)]
        result = validator.validate(self.manifest(), rows)
        self.assertEqual(result["verdict"], "PROSPECTIVE_FAIL_OR_INSUFFICIENT")
        self.assertFalse(result["gate"]["requireLifecycleReset"]["passed"])

    def test_zero_hard_miss_still_enforced(self):
        rows = self.full_set()
        rows[1]["activeAttack"] = 999
        result = validator.validate(self.manifest(), rows)
        self.assertEqual(result["verdict"], "PROSPECTIVE_FAIL_OR_INSUFFICIENT")
        self.assertFalse(result["gate"]["requireZeroHardMiss"]["passed"])

    def test_unknown_gate_fails_closed(self):
        manifest = copy.deepcopy(self.manifest())
        manifest["gate"]["futureConservativeGate"] = 1
        with self.assertRaises(validator.ValidationError):
            validator.validate_manifest(manifest)

    def test_discovery_rows_never_satisfy_new_gates(self):
        rows = self.full_set()
        for row in rows:
            row["evidenceClass"] = "discovery"
        result = validator.validate(self.manifest(), rows)
        self.assertEqual(result["verdict"], "NO_PROSPECTIVE_EVIDENCE")
        self.assertEqual(result["prospective"]["signal"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
