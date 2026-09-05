from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from run_long_qualification import finalize_capture
from test_qualification_analyzer import candidate_capture


class LongQualificationRunnerTests(unittest.TestCase):
    def test_offline_finalize_writes_compact_bundle_and_latest_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / "render_authority_dry"
            session.mkdir()
            capture_json = session / "RENDER_AUTHORITY_CAPTURE_RESULT.json"
            capture_json.write_text(json.dumps(candidate_capture()), encoding="utf-8")
            latest = finalize_capture(capture_json, root)
            self.assertEqual(latest["status"], "INCONCLUSIVE")
            self.assertTrue((session / "RENDER_SOURCE_QUALIFICATION.json").is_file())
            self.assertTrue((session / "RENDER_SOURCE_QUALIFICATION.md").is_file())
            self.assertTrue((root / "LATEST_W3_RENDER_SOURCE_QUALIFICATION.json").is_file())
            bundle = Path(latest["qualifiedBundle"])
            self.assertTrue(bundle.is_file())
            with zipfile.ZipFile(bundle) as zf:
                names = set(zf.namelist())
            self.assertIn("RENDER_AUTHORITY_CAPTURE_RESULT.json", names)
            self.assertIn("RENDER_SOURCE_QUALIFICATION.json", names)
            self.assertIn("RENDER_SOURCE_QUALIFICATION.md", names)


if __name__ == "__main__":
    unittest.main()
