from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import fleet_recorder


class FleetRecorderManifestTests(unittest.TestCase):
    def test_loads_sorted_localhost_fleet_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "instances.json"
            path.write_text(
                json.dumps(
                    {
                        "version": fleet_recorder.FLEET_MANIFEST_VERSION,
                        "instances": [
                            {"id": 10, "host": "127.0.0.1", "port": 9332, "profileDir": "P10"},
                            {"id": 1, "host": "127.0.0.1", "port": 9323, "profileDir": "P01"},
                            {"id": 99, "host": "192.0.2.1", "port": 9999, "profileDir": "unsafe"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            entries = fleet_recorder.load_fleet_entries(path)
            self.assertEqual([item.instance_id for item in entries], [1, 10])
            self.assertEqual([item.port for item in entries], [9323, 9332])
            self.assertTrue(all(item.host == "127.0.0.1" for item in entries))

    def test_wrong_or_missing_manifest_is_fail_open_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "instances.json"
            self.assertEqual(fleet_recorder.load_fleet_entries(path), [])
            path.write_text(json.dumps({"version": "wrong", "instances": []}), encoding="utf-8")
            self.assertEqual(fleet_recorder.load_fleet_entries(path), [])


if __name__ == "__main__":
    unittest.main()
