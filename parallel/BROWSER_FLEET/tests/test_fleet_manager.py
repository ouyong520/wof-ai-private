from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "fleet_manager.py"
SPEC = importlib.util.spec_from_file_location("fleet_manager_under_test", MODULE_PATH)
assert SPEC and SPEC.loader
fleet_manager = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = fleet_manager
SPEC.loader.exec_module(fleet_manager)


class FleetManagerOfflineTests(unittest.TestCase):
    def test_grid_layout_ten_is_bounded_and_unique(self) -> None:
        rects = fleet_manager.grid_layout(10, 1920, 1080)
        self.assertEqual(len(rects), 10)
        self.assertEqual(len(set(rects)), 10)
        for x, y, w, h in rects:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertGreaterEqual(w, 320)
            self.assertGreaterEqual(h, 240)
            self.assertLessEqual(x + w, 1920)
            self.assertLessEqual(y + h, 1080)

    def test_count_guard(self) -> None:
        self.assertEqual(fleet_manager.validate_count(10), 10)
        with self.assertRaises(ValueError):
            fleet_manager.validate_count(0)
        with self.assertRaises(ValueError):
            fleet_manager.validate_count(fleet_manager.MAX_FLEET + 1)

    def test_settings_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "settings.json"
            settings = fleet_manager.FleetSettings(
                browser="edge",
                game_url="https://example.invalid/wof",
                base_port=9400,
            )
            settings.save(path)
            loaded = fleet_manager.FleetSettings.load(path)
            self.assertEqual(loaded.browser, "edge")
            self.assertEqual(loaded.game_url, "https://example.invalid/wof")
            self.assertEqual(loaded.base_port, 9400)

    def test_start_builds_isolated_profiles_and_ports_without_worker_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            manager = fleet_manager.FleetManager(
                settings_path=temp_path / "settings.json",
                manifest_path=temp_path / "instances.json",
            )
            manager.settings.base_port = 9500
            with mock.patch.object(fleet_manager, "screen_size", return_value=(1920, 1080)), \
                 mock.patch.object(manager, "_resolve_browser", return_value=Path("chrome.exe")), \
                 mock.patch.object(manager, "_start_runtime"), \
                 mock.patch.object(manager, "start_monitor"), \
                 mock.patch.object(fleet_manager.time, "sleep"):
                manager.start(3)
            values = list(manager.instances.values())
            self.assertEqual([item.port for item in values], [9500, 9501, 9502])
            self.assertEqual(len({str(item.profile_dir) for item in values}), 3)
            payload = json.loads((temp_path / "instances.json").read_text(encoding="utf-8"))
            self.assertTrue(payload["readOnly"])
            self.assertEqual(payload["ramWrites"], 0)
            self.assertFalse(payload["inputInjection"])
            self.assertFalse(payload["windowWorkerReplacement"])


if __name__ == "__main__":
    unittest.main()
