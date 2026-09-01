from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wof_launcher import fleet


class FleetRegistryTests(unittest.TestCase):
    def test_manifest_is_sorted_and_stale_endpoints_are_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "instances.json"
            path.write_text(
                json.dumps(
                    {
                        "version": fleet.FLEET_MANIFEST_VERSION,
                        "instances": [
                            {
                                "id": 2,
                                "host": "127.0.0.1",
                                "port": 9402,
                                "profileDir": "P2",
                            },
                            {
                                "id": 1,
                                "host": "127.0.0.1",
                                "port": 9401,
                                "profileDir": "P1",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                fleet,
                "probe_endpoint",
                side_effect=lambda host, port: object() if port == 9401 else None,
            ):
                live = fleet.discover_fleet_instances(path, live_only=True)
            self.assertEqual([item.instance_id for item in live], [1])
            all_items = fleet.discover_fleet_instances(path, live_only=False)
            self.assertEqual([item.instance_id for item in all_items], [1, 2])

    def test_select_first_or_numbered_instance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "instances.json"
            path.write_text(
                json.dumps(
                    {
                        "version": fleet.FLEET_MANIFEST_VERSION,
                        "instances": [
                            {"id": 3, "host": "127.0.0.1", "port": 9503, "profileDir": "P3"},
                            {"id": 1, "host": "127.0.0.1", "port": 9501, "profileDir": "P1"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            first = fleet.select_fleet_instance(path, live_only=False)
            chosen = fleet.select_fleet_instance(path, instance_id=3, live_only=False)
            missing = fleet.select_fleet_instance(path, instance_id=2, live_only=False)
            self.assertEqual(first.instance_id, 1)
            self.assertEqual(chosen.port, 9503)
            self.assertIsNone(missing)


if __name__ == "__main__":
    unittest.main()
