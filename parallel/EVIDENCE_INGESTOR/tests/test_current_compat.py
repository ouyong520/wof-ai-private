import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import run as R


class CurrentCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.results = Path(self.tmp.name) / "WOF_RESULTS"
        self.results.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, payload):
        p = self.results / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return p

    def test_current_toolkit_v2_regression_is_known(self):
        self.write(
            "regression_20260901_120000/regression_summary.json",
            {
                "toolkit": "wof-windows-operator-toolkit-v2-cn",
                "overall": "PASS",
                "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
                "checks": [],
            },
        )
        summary, _, _, _ = R.core.ingest(self.results)
        row = summary["files"][0]
        self.assertEqual(row["kind"], "REGRESSION_SUMMARY")
        self.assertEqual(row["checks"]["knownVersion"], "PASS")
        self.assertNotIn("UNKNOWN_SCHEMA", summary["anomalyCodes"])
        self.assertEqual(summary["overall"], "PASS")

    def test_current_toolkit_v2_diagnostics_is_known(self):
        self.write(
            "diagnostics_20260901_120001/diagnostics_summary.json",
            {
                "toolkit": "wof-windows-operator-toolkit-v2-cn",
                "platform": "Windows",
                "python": "3.12",
                "components": {},
                "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
            },
        )
        summary, _, _, _ = R.core.ingest(self.results)
        row = summary["files"][0]
        self.assertEqual(row["kind"], "DIAGNOSTICS_SUMMARY")
        self.assertEqual(row["checks"]["knownVersion"], "PASS")
        self.assertNotIn("UNKNOWN_SCHEMA", summary["anomalyCodes"])

    def test_one_click_cmd_uses_current_entry(self):
        text = (ROOT / "RUN_EVIDENCE_INGESTOR.cmd").read_text(encoding="utf-8")
        self.assertIn('"%HERE%\\run.py" --package', text)


if __name__ == "__main__":
    unittest.main()
