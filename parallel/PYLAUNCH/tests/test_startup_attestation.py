from __future__ import annotations

import unittest
from unittest.mock import patch

from wof_launcher.browser import (
    BrowserEndpoint,
    probe_endpoint,
    probe_endpoint_diagnostic,
    websocket_matches_endpoint,
)
from wof_launcher.monitor import LauncherMonitor
from wof_launcher.state import StatusStore


class StartupAttestationTests(unittest.TestCase):
    @staticmethod
    def _payload(browser: object = "Chrome/136.0.0.0", websocket_url: object = "ws://127.0.0.1:9223/devtools/browser/abc") -> dict:
        return {"Browser": browser, "webSocketDebuggerUrl": websocket_url}

    def test_valid_chrome_browser_metadata_passes(self) -> None:
        with patch("wof_launcher.browser._http_json", return_value=self._payload()):
            endpoint = probe_endpoint("127.0.0.1", 9223)
        self.assertIsNotNone(endpoint)
        self.assertEqual("Chrome/136.0.0.0", endpoint.browser)

    def test_valid_chromium_browser_metadata_passes(self) -> None:
        with patch("wof_launcher.browser._http_json", return_value=self._payload(browser="Chromium/136.0")):
            endpoint = probe_endpoint("localhost", 9223)
        self.assertIsNotNone(endpoint)
        self.assertEqual("Chromium/136.0", endpoint.browser)

    def test_valid_edge_browser_metadata_passes(self) -> None:
        with patch("wof_launcher.browser._http_json", return_value=self._payload(browser="Edg/136.0")):
            endpoint = probe_endpoint("127.0.0.1", 9223)
        self.assertIsNotNone(endpoint)
        self.assertEqual("Edg/136.0", endpoint.browser)

    def test_missing_browser_metadata_fails_closed(self) -> None:
        payload = {"webSocketDebuggerUrl": "ws://127.0.0.1:9223/devtools/browser/abc"}
        with patch("wof_launcher.browser._http_json", return_value=payload):
            endpoint, reason = probe_endpoint_diagnostic("127.0.0.1", 9223)
        self.assertIsNone(endpoint)
        self.assertIn("Browser", reason or "")

    def test_unsupported_browser_metadata_fails_closed(self) -> None:
        with patch("wof_launcher.browser._http_json", return_value=self._payload(browser="Firefox/130")):
            endpoint, reason = probe_endpoint_diagnostic("127.0.0.1", 9223)
        self.assertIsNone(endpoint)
        self.assertIn("Chrome/Chromium/Edge", reason or "")

    def test_malformed_browser_metadata_fails_closed(self) -> None:
        for browser in (123, "", "Chrome/"):
            with self.subTest(browser=browser):
                with patch("wof_launcher.browser._http_json", return_value=self._payload(browser=browser)):
                    self.assertIsNone(probe_endpoint("127.0.0.1", 9223))

    def test_malformed_json_version_fails_closed(self) -> None:
        with patch("wof_launcher.browser._http_json", side_effect=ValueError("bad json")):
            endpoint, reason = probe_endpoint_diagnostic("127.0.0.1", 9223)
        self.assertIsNone(endpoint)
        self.assertIn("有效 JSON", reason or "")

    def test_non_object_json_version_fails_closed(self) -> None:
        with patch("wof_launcher.browser._http_json", return_value=["not", "an", "object"]):
            endpoint, reason = probe_endpoint_diagnostic("127.0.0.1", 9223)
        self.assertIsNone(endpoint)
        self.assertIn("JSON 对象", reason or "")

    def test_page_websocket_masquerading_as_browser_fails_closed(self) -> None:
        payload = self._payload(websocket_url="ws://127.0.0.1:9223/devtools/page/not-browser")
        with patch("wof_launcher.browser._http_json", return_value=payload):
            self.assertIsNone(probe_endpoint("127.0.0.1", 9223))

    def test_worker_websocket_masquerading_as_browser_fails_closed(self) -> None:
        payload = self._payload(websocket_url="ws://127.0.0.1:9223/devtools/worker/not-browser")
        with patch("wof_launcher.browser._http_json", return_value=payload):
            self.assertIsNone(probe_endpoint("127.0.0.1", 9223))

    def test_wrong_port_fails_closed(self) -> None:
        payload = self._payload(websocket_url="ws://127.0.0.1:9333/devtools/browser/abc")
        with patch("wof_launcher.browser._http_json", return_value=payload):
            self.assertIsNone(probe_endpoint("127.0.0.1", 9223))

    def test_remote_configured_host_fails_before_http_probe(self) -> None:
        with patch("wof_launcher.browser._http_json") as http_json:
            endpoint, reason = probe_endpoint_diagnostic("192.168.1.5", 9223)
        self.assertIsNone(endpoint)
        self.assertTrue((reason or "").startswith("启动浏览器校验拒绝："))
        http_json.assert_not_called()

    def test_browser_websocket_shape_rejects_userinfo_query_and_extra_path(self) -> None:
        invalid = (
            "ws://user@127.0.0.1:9223/devtools/browser/abc",
            "ws://127.0.0.1:9223/devtools/browser/abc?x=1",
            "ws://127.0.0.1:9223/devtools/browser/abc/extra",
        )
        for websocket_url in invalid:
            with self.subTest(websocket_url=websocket_url):
                self.assertFalse(websocket_matches_endpoint(websocket_url, "127.0.0.1", 9223))

    def test_reconnect_forces_fresh_attestation_instead_of_reusing_endpoint(self) -> None:
        old = BrowserEndpoint("127.0.0.1", 9223, "Chrome/136", "ws://127.0.0.1:9223/devtools/browser/old")
        fresh = BrowserEndpoint("127.0.0.1", 9223, "Edg/136", "ws://127.0.0.1:9223/devtools/browser/fresh")
        monitor = LauncherMonitor(StatusStore(), auto_launch_browser=False)
        with patch("wof_launcher.monitor.probe_endpoint_diagnostic", side_effect=[(old, None), (fresh, None)]) as probe:
            self.assertEqual(old, monitor._ensure_browser())
            monitor._endpoint = old
            monitor.reconnect()
            self.assertIsNone(monitor._endpoint)
            self.assertEqual(fresh, monitor._ensure_browser())
        self.assertEqual(2, probe.call_count)

    def test_rejection_diagnostic_is_chinese_first(self) -> None:
        with patch("wof_launcher.browser._http_json", return_value=self._payload(browser="Firefox/130")):
            endpoint, reason = probe_endpoint_diagnostic("127.0.0.1", 9223)
        self.assertIsNone(endpoint)
        self.assertTrue((reason or "").startswith("启动浏览器校验拒绝："))


if __name__ == "__main__":
    unittest.main(verbosity=2)
