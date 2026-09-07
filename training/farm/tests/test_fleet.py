from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from training.farm.fleet import (
    FleetConfig,
    TrainingFarmFleet,
    _ladder_for_target,
    _read_plan,
)
from training.farm.collector_export import discover_current_records


class FleetContractTests(unittest.TestCase):
    def test_default_ladder_is_staged_and_bounded(self) -> None:
        self.assertEqual(_ladder_for_target(10, None), (1, 2, 4, 8, 10))
        self.assertEqual(_ladder_for_target(4, None), (1, 2, 4))
        with self.assertRaises(ValueError):
            _ladder_for_target(10, "1,4,8")
        with self.assertRaises(ValueError):
            _ladder_for_target(10, "1,4,4,10")

    def test_fleet_consumes_existing_r04_plan_without_cross_source_fields(self) -> None:
        plan = _read_plan(None)
        self.assertEqual(plan.fork_set_id, "owner-real-wof-r0.4-smoke-v1")
        self.assertTrue(plan.branches)

    def test_fake_fleet_reaches_ten_and_publishes_source_owned_records(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wof-fleet-test-") as temp:
            root = Path(temp)
            export_root = root / "exports"
            status_root = root / "status"
            config = FleetConfig(
                mode="fake",
                workers=10,
                scale_ladder=(1, 2, 4, 8, 10),
                stage_seconds=0.0,
                run_seconds=1.0,
                export_root=export_root,
                status_root=status_root,
                plan_path=Path("unused-plan-path"),
                rom_path=None,
                publish_every_frames=5,
                heartbeat_every_frames=2,
                max_restarts=1,
                max_frames=20,
            )
            result = TrainingFarmFleet(config, _read_plan(None)).run()

            self.assertEqual(result["state"], "COMPLETE")
            self.assertTrue(result["fixtureOnly"])
            self.assertFalse(result["realRuntimeProof"])
            self.assertEqual([row["target"] for row in result["scaleHistory"]], [1, 2, 4, 8, 10])
            self.assertEqual(result["realWorkerLaunches"], 0)
            self.assertEqual(result["fixtureWorkerLaunches"], 10)
            self.assertFalse(result["writesGameMemory"])
            self.assertFalse(result["inputInjection"])
            self.assertEqual(result["failures"], [])

            records = discover_current_records(export_root, verify_artifacts=True)
            self.assertEqual(len(records), 10)
            self.assertEqual({row["sourceNamespace"] for row in records}, {"stable-retro-fbneo"})
            self.assertEqual({row["health"] for row in records}, {"STOPPED"})
            self.assertEqual({row["active"] for row in records}, {False})
            self.assertEqual(len({row["workerId"] for row in records}), 10)
            self.assertTrue(all("ACTION_RESULT_TRAJECTORY" in row["evidenceKinds"] for row in records))
            self.assertTrue(all(row["safety"]["writesGameMemory"] is False for row in records))


if __name__ == "__main__":
    unittest.main()
