from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import endurance_sim


class EnduranceSimulationTests(unittest.TestCase):
    def test_full_required_matrix_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wof052l-endurance-test-") as td:
            out = Path(td)
            matrix = endurance_sim.run_matrix(out, repo_root=None)
            self.assertEqual(matrix["status"], "PASS")
            self.assertEqual(matrix["summary"], {"total": 16, "passed": 16, "failed": 0})
            self.assertEqual(matrix["stopCondition"], "WOF052L 10-ROOM ENDURANCE SIM READY")
            self.assertEqual(matrix["contracts"]["recorderSchema"], "wof-052l-recorder-v1")
            self.assertEqual(matrix["contracts"]["fleetSchema"], "wof-052l-fleet-supervisor-v1")
            self.assertTrue((out / "ENDURANCE_MATRIX.json").is_file())

    def test_machine_matrix_round_trips(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wof052l-endurance-json-") as td:
            out = Path(td)
            endurance_sim.run_matrix(out, repo_root=None)
            payload = json.loads((out / "ENDURANCE_MATRIX.json").read_text(encoding="utf-8"))
            self.assertEqual(len(payload["results"]), 16)
            self.assertTrue(all(row["pass"] for row in payload["results"]))
            safety = next(row for row in payload["results"] if row["scenario"] == "read-only-safety-assertions")
            self.assertEqual(safety["failedAssertions"], [])


if __name__ == "__main__":
    unittest.main()
