from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve()
OPTOOLKIT = HERE.parents[1]
if str(OPTOOLKIT) not in sys.path:
    sys.path.insert(0, str(OPTOOLKIT))

live = importlib.import_module("live_session")


class LiveSessionTests(unittest.TestCase):
    def test_projection_result_is_extracted_from_compact_windows_proof(self):
        result = {"verdict": "IMPLEMENTATION_READY", "proofId": "live-abc"}
        status = {"alphaStatus": {"projectionRecovery": {"proofResult": result}}}
        self.assertEqual(result, live._extract_projection_result(status))

    def test_zip_packages_only_session_tree_and_never_recurses_packages(self):
        with tempfile.TemporaryDirectory(prefix="WOF 中文 结果 ") as td:
            root = Path(td); session = root / "live_session_1"; session.mkdir()
            (session / "WINDOWS_PROOF_STATUS.json").write_text("{}\n", encoding="utf-8")
            nested = root / "packages"; nested.mkdir(); old = nested / "old.zip"; old.write_bytes(b"old")
            out = nested / "new.zip"
            live._zip_session(session, out)
            with zipfile.ZipFile(out) as zf:
                self.assertEqual(["WINDOWS_PROOF_STATUS.json"], zf.namelist())
                self.assertNotIn("old.zip", zf.namelist())

    def test_partial_evidence_files_are_valid_utf8_json(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "SESSION_SUMMARY.json"
            payload = {"partialEvidenceRetained": True, "safety": live.SAFETY, "中文": "保留"}
            live._write_json(p, payload)
            self.assertEqual(payload, json.loads(p.read_text(encoding="utf-8")))

    def test_upload_fails_safe_without_repository_defined_uploader(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); z = root / "result.zip"; z.write_bytes(b"zip")
            status = live._safe_upload(root, z, root / "session")
            self.assertFalse(status["attempted"])
            self.assertEqual("LOCAL_ONLY_NO_REPOSITORY_DEFINED_SECURE_UPLOADER", status["status"])

    def test_safety_contract_is_read_only(self):
        self.assertEqual({"readOnly": True, "ramWrites": 0, "inputInjection": False}, live.SAFETY)


if __name__ == "__main__":
    unittest.main()
