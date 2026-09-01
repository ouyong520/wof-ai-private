from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

QA_DIR = Path(__file__).resolve().parent
PARALLEL = QA_DIR.parent
PYLAUNCH = PARALLEL / "PYLAUNCH"
sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.browser import BrowserEndpoint, probe_endpoint, probe_endpoint_diagnostic, websocket_matches_endpoint
from wof_launcher.monitor import LauncherMonitor
from wof_launcher.state import StatusStore


class FakeClient:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FreshStartupAttestationQA(unittest.TestCase):
    @staticmethod
    def payload(browser: object = "Chrome/136.0", ws: object = "ws://127.0.0.1:9223/devtools/browser/qa") -> dict:
        return {"Browser": browser, "webSocketDebuggerUrl": ws}

    def assert_rejected(self, payload: object, host: str = "127.0.0.1", port: int = 9223) -> None:
        with patch("wof_launcher.browser._http_json", return_value=payload):
            endpoint, reason = probe_endpoint_diagnostic(host, port)
        self.assertIsNone(endpoint)
        self.assertTrue(reason and reason.startswith("启动浏览器校验拒绝："))

    def test_valid_chrome_edge_chromium_loopback_are_accepted(self) -> None:
        cases = (
            ("Chrome/136.0", "127.0.0.1"),
            ("Edg/136.0", "localhost"),
            ("Chromium/136.0", "127.0.0.1"),
        )
        for browser, host in cases:
            ws = f"ws://{host}:9223/devtools/browser/id-1"
            with self.subTest(browser=browser, host=host), patch("wof_launcher.browser._http_json", return_value=self.payload(browser, ws)):
                endpoint = probe_endpoint(host, 9223)
                self.assertIsNotNone(endpoint)
                self.assertEqual(browser, endpoint.browser)

    def test_missing_and_empty_browser_metadata_fail_closed(self) -> None:
        base = {"webSocketDebuggerUrl": "ws://127.0.0.1:9223/devtools/browser/qa"}
        for browser in ("__missing__", None, "", "   "):
            payload = dict(base)
            if browser != "__missing__":
                payload["Browser"] = browser
            with self.subTest(browser=browser):
                self.assert_rejected(payload)

    def test_malformed_product_and_version_shapes_fail_closed(self) -> None:
        bad = (123, {}, "Firefox/130", "Chrome/", "Chrome//136", "Chrome/136 bad", "Chrome/136\tbad", "Chrome/136/extra", "Unknown", "Chrome/ 136")
        for browser in bad:
            with self.subTest(browser=browser):
                self.assert_rejected(self.payload(browser=browser))

    def test_malformed_devtools_version_response_fails_closed(self) -> None:
        with patch("wof_launcher.browser._http_json", side_effect=ValueError("bad json")):
            endpoint, reason = probe_endpoint_diagnostic("127.0.0.1", 9223)
        self.assertIsNone(endpoint)
        self.assertIn("有效 JSON", reason or "")
        for body in ([], "x", 1, None):
            with self.subTest(body=body), patch("wof_launcher.browser._http_json", return_value=body):
                endpoint, reason = probe_endpoint_diagnostic("127.0.0.1", 9223)
                self.assertIsNone(endpoint)
                self.assertIn("JSON 对象", reason or "")

    def test_websocket_host_and_port_mismatch_fail_closed(self) -> None:
        bad = (
            "ws://192.168.1.9:9223/devtools/browser/qa",
            "ws://127.0.0.1:9333/devtools/browser/qa",
            "ws://localhost:9333/devtools/browser/qa",
        )
        for ws in bad:
            with self.subTest(ws=ws):
                self.assert_rejected(self.payload(ws=ws))
        with patch("wof_launcher.browser._http_json") as http_json:
            endpoint, reason = probe_endpoint_diagnostic("192.168.1.9", 9223)
        self.assertIsNone(endpoint)
        self.assertTrue((reason or "").startswith("启动浏览器校验拒绝："))
        http_json.assert_not_called()

    def test_page_worker_and_malformed_browser_websocket_shapes_fail_closed(self) -> None:
        bad = (
            "ws://127.0.0.1:9223/devtools/page/p",
            "ws://127.0.0.1:9223/devtools/worker/w",
            "ws://127.0.0.1:9223/devtools/browser/",
            "ws://127.0.0.1:9223/devtools/browser/a/extra",
            "ws://user@127.0.0.1:9223/devtools/browser/a",
            "ws://127.0.0.1:9223/devtools/browser/a?q=1",
            "ws://127.0.0.1:9223/devtools/browser/a#frag",
        )
        for ws in bad:
            with self.subTest(ws=ws):
                self.assertFalse(websocket_matches_endpoint(ws, "127.0.0.1", 9223))
                self.assert_rejected(self.payload(ws=ws))

    def test_reconnect_reprobes_and_discards_stale_authority(self) -> None:
        old = BrowserEndpoint("127.0.0.1", 9223, "Chrome/135", "ws://127.0.0.1:9223/devtools/browser/stable")
        fresh = BrowserEndpoint("127.0.0.1", 9223, "Edg/136", "ws://127.0.0.1:9223/devtools/browser/stable")
        monitor = LauncherMonitor(StatusStore(), auto_launch_browser=False)
        monitor._endpoint = old
        monitor._identity_cache["same-target"] = {"ok": True}
        monitor._last_worker_id = "same-target"
        monitor._last_identity = {"ok": True}
        with patch("wof_launcher.monitor.probe_endpoint_diagnostic", side_effect=[(old, None), (fresh, None)]) as probe:
            self.assertEqual(old, monitor._ensure_browser())
            monitor.reconnect()
            self.assertIsNone(monitor._endpoint)
            self.assertEqual({}, monitor._identity_cache)
            self.assertIsNone(monitor._last_worker_id)
            self.assertIsNone(monitor._last_identity)
            self.assertEqual(fresh, monitor._ensure_browser())
        self.assertEqual(2, probe.call_count)

    def test_stable_websocket_keeps_only_fresh_metadata(self) -> None:
        ws = "ws://127.0.0.1:9223/devtools/browser/stable"
        old = BrowserEndpoint("127.0.0.1", 9223, "Chrome/135", ws)
        fresh = BrowserEndpoint("127.0.0.1", 9223, "Edg/136", ws)
        monitor = LauncherMonitor(StatusStore(), auto_launch_browser=False)
        monitor._client = FakeClient()
        monitor._endpoint = old
        monitor._ensure_browser = lambda: fresh
        monitor._sleep = lambda: monitor._stop.set()
        choice = SimpleNamespace(page=None, worker=None, worker_probe=None, identity=None, reason="none", diagnostics={})
        with patch("wof_launcher.monitor.discover", return_value=choice):
            monitor._run()
        self.assertEqual(fresh, monitor._endpoint)
        self.assertEqual("Edg/136", monitor.status.get().browser_name)

    def test_rejected_fresh_attestation_invalidates_stale_authority(self) -> None:
        monitor = LauncherMonitor(StatusStore(), auto_launch_browser=False)
        old_client = FakeClient()
        monitor._client = old_client
        monitor._endpoint = BrowserEndpoint("127.0.0.1", 9223, "Chrome/135", "ws://127.0.0.1:9223/devtools/browser/old")
        monitor._identity_cache["same-target"] = {"ok": True}
        monitor._last_worker_id = "same-target"
        monitor._last_identity = {"ok": True}

        def reject() -> None:
            monitor._startup_attestation_error = "启动浏览器校验拒绝：QA fresh rejection。"
            return None

        monitor._ensure_browser = reject
        monitor._sleep = lambda: monitor._stop.set()
        monitor._run()
        status = monitor.status.get()
        self.assertTrue(old_client.closed)
        self.assertIsNone(monitor._client)
        self.assertIsNone(monitor._endpoint)
        self.assertEqual({}, monitor._identity_cache)
        self.assertFalse(status.browser_connected)
        self.assertEqual("ERROR", status.state)
        self.assertIn("QA fresh rejection", status.last_error or "")

    def test_same_target_id_cannot_survive_runtime_generation_reconnect(self) -> None:
        monitor = LauncherMonitor(StatusStore(), auto_launch_browser=False)
        monitor._identity_cache["worker-stable"] = {"ok": True, "sha256": "a" * 64}
        monitor._last_worker_id = "worker-stable"
        monitor._last_identity = {"ok": True}
        monitor.reconnect()
        self.assertEqual({}, monitor._identity_cache)
        self.assertIsNone(monitor._last_worker_id)
        self.assertIsNone(monitor._last_identity)

    def test_rejection_diagnostics_are_chinese_first(self) -> None:
        cases = (
            {"webSocketDebuggerUrl": "ws://127.0.0.1:9223/devtools/browser/a"},
            self.payload(browser="Firefox/130"),
            self.payload(ws="ws://127.0.0.1:9223/devtools/page/a"),
        )
        for payload in cases:
            with self.subTest(payload=payload), patch("wof_launcher.browser._http_json", return_value=payload):
                endpoint, reason = probe_endpoint_diagnostic("127.0.0.1", 9223)
            self.assertIsNone(endpoint)
            self.assertTrue((reason or "").startswith("启动浏览器校验拒绝："))


def load_file_suite(path: Path) -> unittest.TestSuite:
    name = f"qa_loaded_{path.stem}_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load regression file: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module)


def build_suite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(FreshStartupAttestationQA))
    for path in (
        PYLAUNCH / "tests" / "test_startup_attestation.py",
        PYLAUNCH / "tests" / "test_endpoint_hardening.py",
        PYLAUNCH / "tests" / "test_identity_cache_generation.py",
        PARALLEL / "PYLAUNCH_QA_IDENTITY_GENERATION" / "test_startup_attestation_regression.py",
    ):
        suite.addTests(load_file_suite(path))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(build_suite())
    raise SystemExit(0 if result.wasSuccessful() else 1)
