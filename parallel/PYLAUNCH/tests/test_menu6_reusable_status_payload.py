from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
ENTRY = PYLAUNCH / "render_authority_measurement_entry.py"


def _load_entry():
    spec = importlib.util.spec_from_file_location("render_authority_measurement_entry_under_test", ENTRY)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load render_authority_measurement_entry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Menu6ReusableStatusPayloadTests(unittest.TestCase):
    def test_reusable_payload_merges_browser_source_once(self) -> None:
        entry = _load_entry()
        diagnostic = {
            "browserEntrySource": "existing-pylaunch-cdp",
            "wofPageFound": True,
            "workerFound": True,
            "wasmFound": True,
            "heapFound": True,
        }
        payload = entry._reusable_payload(diagnostic, "existing-pylaunch-cdp")
        self.assertTrue(payload["browserConnected"])
        self.assertEqual("existing-pylaunch-cdp", payload["browserEntrySource"])
        self.assertTrue(payload["wofPageFound"])

    def test_entry_does_not_publish_duplicate_browser_entry_source_keyword(self) -> None:
        text = ENTRY.read_text(encoding="utf-8")
        self.assertNotIn(
            'publisher.publish("WAITING_FOR_WOF",browserConnected=True,browserEntrySource=entry_source,**diagnostic)',
            text,
        )
        self.assertIn(
            'publisher.publish("WAITING_FOR_WOF",**_reusable_payload(diagnostic,entry_source))',
            text,
        )


if __name__ == "__main__":
    unittest.main()
