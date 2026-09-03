from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wof_launcher import browser


class OwnerMenu6BrowserReuseW1Tests(unittest.TestCase):
    def test_stale_game_url_sources_are_not_navigation_authority(self):
        with tempfile.TemporaryDirectory() as td:
            fleet = Path(td) / "WOF Future Danger" / "Fleet"
            fleet.mkdir(parents=True)
            (fleet / "settings.json").write_text(
                json.dumps({"gameUrl": "https://stale.example/rom-error"}),
                encoding="utf-8",
            )
            with patch.dict(
                os.environ,
                {"LOCALAPPDATA": td, "WOF_GAME_URL": "https://stale-env.example/rom-error"},
                clear=False,
            ):
                self.assertEqual(browser.known_owner_game_url(None), (None, None))
                self.assertEqual(
                    browser.known_owner_game_url("https://owner-explicit.example/wof"),
                    ("https://owner-explicit.example/wof", "explicit"),
                )

    def test_attach_only_guard_cannot_launch_or_restore_browser(self):
        with patch.dict(os.environ, {"WOF_ALPHA_MENU6_ATTACH_ONLY": "1"}, clear=False):
            self.assertIsNone(browser.find_browser("auto", explicit="C:/fake/chrome.exe"))
            with self.assertRaisesRegex(RuntimeError, "attach/reuse-only"):
                browser.launch_debug_browser(Path("C:/fake/chrome.exe"), restore_last_session=True)

    def test_existing_real_wof_endpoint_is_selected_for_reuse(self):
        entry_path = Path(__file__).resolve().parents[1] / "render_authority_measurement_entry.py"
        endpoint = SimpleNamespace(
            host="127.0.0.1",
            port=9333,
            browser="Chrome/151.0",
            websocket_url="ws://127.0.0.1:9333/devtools/browser/existing",
            http_base="http://127.0.0.1:9333",
        )
        fleet_instance = SimpleNamespace(instance_id=7, host="127.0.0.1", port=9333)
        choice = SimpleNamespace(
            page={"targetId": "page-real-wof", "url": "https://owner.example/wof"},
            worker={"targetId": "worker-real-wof"},
            worker_probe={"moduleOk": True, "heapOk": True},
            identity={"ok": True, "sha256": "world"},
            reason="EXACT_WORLD_921031",
        )
        closed = []

        class FakeClient:
            def __init__(self, websocket_url, timeout=5.0):
                self.websocket_url = websocket_url
            def connect(self):
                return None
            def close(self):
                closed.append(self.websocket_url)

        package = types.ModuleType("wof_launcher");package.__path__=[]
        discovery = types.ModuleType("wof_launcher.discovery_v2")
        discovery.IDENTITY_PROBE = None
        discovery.discover = lambda client, identity_cache=None: choice
        browser_mod = types.ModuleType("wof_launcher.browser")
        browser_mod.BrowserEndpoint = object
        browser_mod.probe_endpoint_diagnostic = lambda host, port: ((endpoint, None) if port == 9333 else (None, None))
        cdp_mod = types.ModuleType("wof_launcher.cdp");cdp_mod.CdpClient = FakeClient
        fleet_mod = types.ModuleType("wof_launcher.fleet");fleet_mod.discover_fleet_instances = lambda _path, live_only=True: [fleet_instance]
        probe_mod = types.ModuleType("wof_launcher.probe_v2");probe_mod.IDENTITY_PROBE = object()
        reentry_mod = types.ModuleType("wof_launcher.reentry_discovery");reentry_mod.recover_page_only = lambda client, found, identity_cache=None: found
        ui_mod = types.ModuleType("wof_launcher.render_measurement_ui");ui_mod.MeasurementPublisher = object;ui_mod.MeasurementTrayApp = object
        state_mod = types.ModuleType("wof_launcher.state");state_mod.StatusStore = object
        fake_modules = {
            "wof_launcher": package,
            "wof_launcher.discovery_v2": discovery,
            "wof_launcher.browser": browser_mod,
            "wof_launcher.cdp": cdp_mod,
            "wof_launcher.fleet": fleet_mod,
            "wof_launcher.probe_v2": probe_mod,
            "wof_launcher.reentry_discovery": reentry_mod,
            "wof_launcher.render_measurement_ui": ui_mod,
            "wof_launcher.state": state_mod,
        }
        package.discovery_v2 = discovery
        with patch.dict(sys.modules, fake_modules, clear=False):
            spec = importlib.util.spec_from_file_location("w1_entry_fixture", entry_path)
            self.assertIsNotNone(spec);self.assertIsNotNone(spec.loader)
            module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            selected, source, diagnostic = module._probe_reusable_wof("127.0.0.1", 9223)
        self.assertIs(selected, endpoint)
        self.assertEqual(source, "existing-browser-fleet-7")
        self.assertEqual(diagnostic["pageTargetId"], "page-real-wof")
        self.assertFalse(diagnostic["browserLaunchAttempted"])
        self.assertFalse(diagnostic["navigationAttempted"])
        self.assertTrue(diagnostic["staleGameUrlIgnored"])
        self.assertEqual(closed, [endpoint.websocket_url])

    def test_no_wof_path_is_stable_waiting_before_runner(self):
        entry = (Path(__file__).resolve().parents[1] / "render_authority_measurement_entry.py").read_text(encoding="utf-8")
        self.assertIn('publisher.publish(\n                        "WAITING_FOR_WOF"', entry)
        self.assertIn('os.environ[ATTACH_ONLY_ENV]="1"', entry)
        self.assertIn('runner.run(root,output_root,endpoint.host,endpoint.port', entry)
        self.assertIn('args.browser,args.browser_path,None', entry)
        self.assertNotIn("launch_debug_browser", entry)
        self.assertNotIn("known_owner_game_url", entry)
        self.assertNotIn("Page.navigate", entry)

    def test_root_cmd_opens_original_chinese_toolbox_and_menu6_owns_alpha_entry(self):
        repo = Path(__file__).resolve().parents[3]
        cmd = (repo / "WOF_一键工具.cmd").read_text(encoding="utf-8")
        owner = (repo / "parallel" / "OPTOOLKIT" / "owner_zh_cn.py").read_text(encoding="utf-8")
        self.assertIn("owner_zh_cn.py", cmd)
        self.assertIn("直接打开中文工具箱", cmd)
        self.assertNotIn(":alpha_checkout", cmd)
        self.assertNotIn("render_authority_measurement_entry.py", cmd)
        self.assertIn('"6 Run Live Proof": "6 打开 WOF 头顶显示"', owner)
        self.assertIn('entry = self.root / "parallel/PYLAUNCH/render_authority_measurement_entry.py"', owner)
        self.assertIn("只读模式：开启 / 游戏内存写入：0 / 输入注入：关闭。", owner)


if __name__ == "__main__":
    unittest.main()
