from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "fleet_manager.py"
SPEC = importlib.util.spec_from_file_location("fleet_manager_v2_under_test", MODULE_PATH)
assert SPEC and SPEC.loader
fm = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = fm
SPEC.loader.exec_module(fm)


class DummyClient:
    urls = []

    def __init__(self, url, timeout=1.5):
        self.url = url
        self.urls.append(url)

    def connect(self):
        pass

    def close(self):
        pass


class FleetManagerV2Tests(unittest.TestCase):
    def make_manager(self, temp):
        return fm.FleetManager(settings_path=Path(temp) / "settings.json", manifest_path=Path(temp) / "instances.json")

    def test_ten_instance_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = self.make_manager(temp)
            manager.settings.base_port = 9600
            with mock.patch.object(fm, "screen_size", return_value=(1920, 1080)), \
                 mock.patch.object(manager, "_resolve_browser", return_value=Path("chrome.exe")), \
                 mock.patch.object(manager, "_start_runtime"), \
                 mock.patch.object(manager, "start_monitor"), \
                 mock.patch.object(fm.time, "sleep"), \
                 mock.patch.object(manager, "refresh_status"):
                manager.start(10)
            values = list(manager.instances.values())
            self.assertEqual([x.port for x in values], list(range(9600, 9610)))
            self.assertEqual(len({str(x.profile_dir) for x in values}), 10)

    def test_stale_missing_endpoint_clears_old_worker(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = self.make_manager(temp)
            runtime = fm.InstanceRuntime(1, 9700, Path(temp) / "p1", (0, 0, 100, 100), None)
            runtime.page_ok = runtime.worker_ok = True
            runtime.worker_count = 1
            manager.instances = {1: runtime}
            with mock.patch.object(fm, "probe_endpoint", return_value=None):
                manager.refresh_status()
            self.assertFalse(runtime.browser_ok)
            self.assertFalse(runtime.page_ok)
            self.assertFalse(runtime.worker_ok)
            self.assertEqual(runtime.worker_count, 0)

    def test_no_cross_port_association(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = self.make_manager(temp)
            runtime = fm.InstanceRuntime(1, 9800, Path(temp) / "p1", (0, 0, 100, 100), None)
            manager.instances = {1: runtime}
            endpoint = SimpleNamespace(
                host="127.0.0.1",
                port=9800,
                browser="Chromium",
                websocket_url="ws://127.0.0.1:9801/devtools/browser/x",
            )
            with mock.patch.object(fm, "probe_endpoint", return_value=endpoint), \
                 mock.patch.object(fm, "CdpClient") as client:
                manager.refresh_status()
            client.assert_not_called()
            self.assertFalse(runtime.worker_ok)
            self.assertIn("crossed fleet port boundary", runtime.last_error)

    def test_each_instance_uses_only_its_own_websocket(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = self.make_manager(temp)
            manager.instances = {
                1: fm.InstanceRuntime(1, 9900, Path(temp) / "p1", (0, 0, 100, 100), None),
                2: fm.InstanceRuntime(2, 9901, Path(temp) / "p2", (0, 0, 100, 100), None),
            }
            endpoints = {
                9900: SimpleNamespace(host="127.0.0.1", port=9900, browser="Chromium", websocket_url="ws://127.0.0.1:9900/devtools/browser/a"),
                9901: SimpleNamespace(host="127.0.0.1", port=9901, browser="Chromium", websocket_url="ws://127.0.0.1:9901/devtools/browser/b"),
            }
            DummyClient.urls = []
            status = SimpleNamespace(page_ok=True, page_count=1, worker_ok=True, worker_count=1, path="direct-worker-module", topology_count=0, reason=None)
            with mock.patch.object(fm, "probe_endpoint", side_effect=lambda host, port: endpoints[port]), \
                 mock.patch.object(fm, "CdpClient", DummyClient), \
                 mock.patch.object(fm, "discover_fleet_status", return_value=status):
                manager.refresh_status()
            self.assertEqual(DummyClient.urls, [endpoints[9900].websocket_url, endpoints[9901].websocket_url])
            self.assertTrue(manager.instances[1].worker_ok)
            self.assertTrue(manager.instances[2].worker_ok)

    def test_one_instance_discovery_failure_does_not_block_other(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = self.make_manager(temp)
            manager.instances = {
                1: fm.InstanceRuntime(1, 9910, Path(temp) / "p1", (0, 0, 100, 100), None),
                2: fm.InstanceRuntime(2, 9911, Path(temp) / "p2", (0, 0, 100, 100), None),
            }
            endpoints = {
                p: SimpleNamespace(host="127.0.0.1", port=p, browser="Chromium", websocket_url=f"ws://127.0.0.1:{p}/devtools/browser/x")
                for p in (9910, 9911)
            }
            ok = SimpleNamespace(page_ok=True, page_count=1, worker_ok=True, worker_count=1, path="related", topology_count=1, reason=None)
            calls = {"n": 0}

            def discover(_client, settle_seconds):
                calls["n"] += 1
                if calls["n"] == 1:
                    raise RuntimeError("room one failed")
                return ok

            with mock.patch.object(fm, "probe_endpoint", side_effect=lambda host, port: endpoints[port]), \
                 mock.patch.object(fm, "CdpClient", DummyClient), \
                 mock.patch.object(fm, "discover_fleet_status", side_effect=discover):
                manager.refresh_status()
            self.assertFalse(manager.instances[1].worker_ok)
            self.assertTrue(manager.instances[2].worker_ok)

    def test_manifest_marks_worker_as_indicator_not_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = self.make_manager(temp)
            runtime = fm.InstanceRuntime(1, 9920, Path(temp) / "p1", (0, 0, 100, 100), None)
            runtime.browser_ok = runtime.page_ok = runtime.worker_ok = True
            runtime.worker_discovery_path = "page-autoattach-module"
            manager.instances = {1: runtime}
            manager.write_manifest()
            payload = json.loads((Path(temp) / "instances.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["workerStatusAuthority"], "cheap-indicator-only")
            self.assertFalse(payload["world921031IdentityAuthoritative"])
            self.assertTrue(payload["readOnly"])
            self.assertEqual(payload["ramWrites"], 0)
            self.assertFalse(payload["inputInjection"])
            self.assertFalse(payload["windowWorkerReplacement"])


if __name__ == "__main__":
    unittest.main()
