import importlib.util
import json
import tempfile
import sys
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve()
SPEC = importlib.util.spec_from_file_location("ingestor", HERE.parents[1] / "ingestor.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class IngestorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "WOF_RESULTS"
        self.root.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write_json(self, rel, payload):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return p

    def pylaunch(self, **overrides):
        payload = {
            "schema": "wof-python-launcher-windows-proof-v1",
            "automatedResult": "PASS",
            "checks": {"World 921031": "OK"},
            "worldSha256": M.WORLD_SHA256,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "lastUpdateUtc": "2026-09-01T12:00:00Z",
        }
        payload.update(overrides)
        return payload

    def test_pylaunch_pass_and_world_identity(self):
        self.write_json("live_proof_20260901_120000/WINDOWS_PROOF_STATUS.json", self.pylaunch())
        summary, _, _, _ = M.ingest(self.root)
        self.assertEqual(summary["overall"], "PASS")
        row = summary["files"][0]
        self.assertEqual(row["tool"], "PYLAUNCH")
        self.assertEqual(row["checks"]["world921031"], "PASS")
        self.assertEqual(row["checks"]["ramWritesZero"], "PASS")

    def test_bad_json_does_not_block_good_file(self):
        bad = self.root / "broken.json"
        bad.write_text("{broken", encoding="utf-8")
        self.write_json("proof.json", self.pylaunch())
        summary, _, _, _ = M.ingest(self.root)
        self.assertEqual(summary["counts"]["files"], 2)
        self.assertEqual(summary["counts"]["unknownOrBroken"], 1)
        self.assertIn("BROKEN_JSON", summary["anomalyCodes"])

    def test_duplicate_is_detected_but_not_error(self):
        p = self.pylaunch()
        self.write_json("a.json", p)
        self.write_json("b.json", p)
        summary, _, _, _ = M.ingest(self.root)
        self.assertEqual(summary["counts"]["duplicates"], 1)
        self.assertEqual(summary["overall"], "PASS")

    def test_ram_write_violation_is_critical(self):
        self.write_json("proof.json", self.pylaunch(ramWrites=1))
        summary, _, _, _ = M.ingest(self.root)
        self.assertEqual(summary["overall"], "FAIL")
        self.assertEqual(summary["counts"]["critical"], 1)
        self.assertIn("RAM_WRITES_NONZERO", summary["anomalyCodes"])

    def test_world_mismatch_is_critical(self):
        self.write_json("proof.json", self.pylaunch(worldSha256="0" * 64))
        summary, _, _, _ = M.ingest(self.root)
        self.assertEqual(summary["overall"], "FAIL")
        self.assertIn("WORLD_IDENTITY_MISMATCH", summary["anomalyCodes"])

    def test_recorder_merged_known_schema(self):
        payload = {
            "schema": "wof-052l-recorder-v1",
            "runId": "run-1",
            "status": "complete",
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
            "identityPolicy": {"required": "Warriors of Fate (World 921031)", "sha256": M.WORLD_SHA256},
            "counts": {},
            "rooms": [],
        }
        self.write_json("recorder/runs/run-1.json", payload)
        summary, _, _, _ = M.ingest(self.root)
        row = summary["files"][0]
        self.assertEqual(row["kind"], "WOF052L_MERGED")
        self.assertEqual(row["checks"]["world921031"], "PASS")

    def test_browser_fleet_no_world_required(self):
        payload = {
            "version": "wof-browser-fleet-v1",
            "managerRunId": "fleet123",
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "instances": [],
        }
        self.write_json("diagnostics_20260901_120000/browser_fleet/instances.json", payload)
        summary, _, _, _ = M.ingest(self.root)
        row = summary["files"][0]
        self.assertEqual(row["tool"], "Browser Fleet")
        self.assertEqual(row["checks"]["world921031"], "NOT_APPLICABLE")
        self.assertEqual(summary["overall"], "PASS")

    def test_unknown_schema_is_warning(self):
        self.write_json("new_tool.json", {"schema": "future-v9", "x": 1})
        summary, _, _, _ = M.ingest(self.root)
        self.assertEqual(summary["overall"], "ATTENTION")
        self.assertIn("UNKNOWN_SCHEMA", summary["anomalyCodes"])

    def test_generated_folder_is_excluded_on_second_run(self):
        self.write_json("proof.json", self.pylaunch())
        first, _, _, _ = M.ingest(self.root)
        second, _, _, _ = M.ingest(self.root)
        self.assertEqual(first["counts"]["files"], 1)
        self.assertEqual(second["counts"]["files"], 1)

    def test_package_contains_summary_and_unique_evidence(self):
        self.write_json("proof.json", self.pylaunch())
        summary, sp, tp, package = M.ingest(self.root, make_package=True)
        self.assertIsNotNone(package)
        with zipfile.ZipFile(package) as z:
            names = set(z.namelist())
        self.assertIn("SUMMARY.json", names)
        self.assertIn("结果汇总.txt", names)
        self.assertIn("PACKAGE_MANIFEST.json", names)
        self.assertIn("evidence/proof.json", names)
        self.assertEqual(summary["overall"], "PASS")

    def test_log_is_indexed(self):
        p = self.root / "diagnostics_20260901_120000/toolkit.log"
        p.parent.mkdir(parents=True)
        p.write_text("hello", encoding="utf-8")
        summary, _, _, _ = M.ingest(self.root)
        self.assertEqual(summary["files"][0]["kind"], "TOOLKIT_LOG")

    def test_alpha_regression_is_recognized_and_world_checked(self):
        payload = {
            "artifact": "wof-alpha-rc5",
            "tests": "PASS",
            "supportedIdentity": "wof / World 921031",
            "goldenSha256": M.WORLD_SHA256,
            "blockers": {"readOnly": True, "inputInjection": False},
        }
        self.write_json("diagnostics_20260901_120000/known_status/alpha_regression_result.json", payload)
        summary, _, _, _ = M.ingest(self.root)
        row = summary["files"][0]
        self.assertEqual(row["kind"], "ALPHA_REGRESSION_RESULT")
        self.assertEqual(row["checks"]["world921031"], "PASS")
        self.assertEqual(summary["overall"], "PASS")

    def test_alpha_qa_is_recognized(self):
        payload = {
            "artifact": "wof-alpha-rc5-independent-qa-retest",
            "preservedRc4SafetyGates": {
                "exactWorld921031Full1MiBSha256Gate": True,
                "goldenSha256": M.WORLD_SHA256,
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
            },
        }
        self.write_json("diagnostics_20260901_120000/known_status/ALPHAQA_RC5_result.json", payload)
        summary, _, _, _ = M.ingest(self.root)
        row = summary["files"][0]
        self.assertEqual(row["tool"], "Alpha QA")
        self.assertEqual(row["checks"]["world921031"], "PASS")
        self.assertEqual(summary["overall"], "PASS")


if __name__ == "__main__":
    unittest.main()
