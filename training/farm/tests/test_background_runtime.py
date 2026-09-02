from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from training.farm.background_runtime import (
    ForegroundFriendlyController,
    LoadSample,
    PolicyError,
    PriorityStatus,
    RuntimePolicy,
    RuntimeState,
    apply_background_priority,
    build_diagnostic,
    default_policy,
    load_policy,
    scan_no_host_input_authority,
)


class BackgroundRuntimeTests(unittest.TestCase):
    def test_policy_roundtrip_and_hash_are_deterministic(self):
        policy = default_policy()
        self.assertEqual(RuntimePolicy.from_dict(policy.to_dict()), policy)
        self.assertEqual(policy.sha256(), RuntimePolicy.from_dict(json.loads(policy.canonical_json())).sha256())
        self.assertEqual(len(policy.sha256()), 64)

    def test_unknown_and_coercible_policy_fields_rejected(self):
        raw = default_policy().to_dict()
        raw["unknown"] = 1
        with self.assertRaises(PolicyError):
            RuntimePolicy.from_dict(raw)
        raw = default_policy().to_dict()
        raw["headless"] = 1
        with self.assertRaises(PolicyError):
            RuntimePolicy.from_dict(raw)
        raw = default_policy().to_dict()
        raw["resourceBudget"]["configuredWorkerCeiling"] = True
        with self.assertRaises(PolicyError):
            RuntimePolicy.from_dict(raw)

    def test_worker_ceiling_bounds_include_one_and_ten(self):
        raw = default_policy().to_dict()
        raw["resourceBudget"].update({
            "configuredWorkerCeiling": 1,
            "foregroundActiveWorkerTarget": 1,
            "idleWorkerTarget": 1,
            "pressureHighWorkerTarget": 1,
        })
        self.assertEqual(RuntimePolicy.from_dict(raw).resource_budget.configured_worker_ceiling, 1)
        self.assertEqual(default_policy().resource_budget.configured_worker_ceiling, 10)
        for bad in (0, 11):
            raw = default_policy().to_dict()
            raw["resourceBudget"]["configuredWorkerCeiling"] = bad
            with self.assertRaises(PolicyError):
                RuntimePolicy.from_dict(raw)

    def test_manual_pause_is_zero_target(self):
        ctl = ForegroundFriendlyController(default_policy().resource_budget)
        decision = ctl.evaluate(LoadSample(100, False, 10, 10, True))
        self.assertEqual(decision.state, RuntimeState.MANUAL_PAUSE)
        self.assertEqual(decision.allowed_worker_target, 0)

    def test_hysteresis_and_scale_up_cooldown(self):
        ctl = ForegroundFriendlyController(default_policy().resource_budget)
        self.assertEqual(ctl.evaluate(LoadSample(0, False, 20, 20)).state, RuntimeState.IDLE)
        self.assertEqual(ctl.evaluate(LoadSample(100, True, 20, 20)).state, RuntimeState.FOREGROUND_ACTIVE)
        self.assertEqual(ctl.evaluate(LoadSample(200, True, 95, 20)).state, RuntimeState.PRESSURE_HIGH)
        self.assertEqual(ctl.evaluate(LoadSample(300, True, 75, 20)).reason, "PRESSURE_HYSTERESIS")
        still = ctl.evaluate(LoadSample(600, True, 60, 20))
        self.assertEqual(still.state, RuntimeState.PRESSURE_HIGH)
        self.assertTrue(still.reason.startswith("SCALE_UP_COOLDOWN:"))
        self.assertEqual(ctl.evaluate(LoadSample(5200, True, 60, 20)).state, RuntimeState.FOREGROUND_ACTIVE)
        self.assertEqual(ctl.evaluate(LoadSample(5300, False, 20, 20)).state, RuntimeState.FOREGROUND_ACTIVE)
        self.assertEqual(ctl.evaluate(LoadSample(10200, False, 20, 20)).state, RuntimeState.IDLE)

    def test_non_monotonic_sample_rejected(self):
        ctl = ForegroundFriendlyController(default_policy().resource_budget)
        ctl.evaluate(LoadSample(5, False, 0, 0))
        with self.assertRaises(PolicyError):
            ctl.evaluate(LoadSample(4, False, 0, 0))

    def test_windows_priority_success_and_failure_are_structured(self):
        called = []
        status = apply_background_priority(platform_name="Windows", windows_setter=lambda: called.append(True))
        self.assertTrue(status.applied)
        self.assertEqual(called, [True])

        def fail():
            raise PermissionError("blocked")

        status = apply_background_priority(platform_name="Windows", windows_setter=fail)
        self.assertTrue(status.attempted)
        self.assertFalse(status.applied)
        self.assertIn("PermissionError", status.detail)

    def test_linux_priority_mock(self):
        writes = []
        status = apply_background_priority(platform_name="Linux", posix_getter=lambda: 0,
                                           posix_setter=lambda value: writes.append(value))
        self.assertTrue(status.applied)
        self.assertEqual(writes, [10])

    def test_safety_guard_detects_host_input_import_and_focus_symbol(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "safe.py").write_text("import os\n", encoding="utf-8")
            bad = root / "bad.py"
            bad.write_text("import pyautogui\ndef f(x):\n    return x.SendInput()\n", encoding="utf-8")
            status = scan_no_host_input_authority([root / "safe.py", bad])
            self.assertFalse(status.passed)
            symbols = {item.symbol for item in status.violations}
            self.assertIn("pyautogui", symbols)
            self.assertIn("SendInput", symbols)

    def test_example_policy_loads_with_unicode_space_parentheses_path(self):
        policy = default_policy()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "三国 10训 (runtime policy).json"
            path.write_text(json.dumps(policy.to_dict(), ensure_ascii=False), encoding="utf-8")
            self.assertEqual(load_policy(path).sha256(), policy.sha256())

    def test_rom_free_diagnostic_never_claims_proof_or_launch(self):
        with tempfile.TemporaryDirectory() as td:
            safe = Path(td) / "runtime.py"
            safe.write_text("import os\n", encoding="utf-8")
            safety = scan_no_host_input_authority([safe])
        result = build_diagnostic(
            default_policy(), LoadSample(0, True, 30, 30),
            priority_status=PriorityStatus("TestOS", "background", False, False, "stub", "test"),
            safety_status=safety,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["realWofProof"])
        self.assertFalse(result["r0_5Authorized"])
        self.assertFalse(result["realWorkerExecutionStarted"])
        self.assertEqual(result["controllerDecision"]["realWorkersStarted"], 0)


if __name__ == "__main__":
    unittest.main()
