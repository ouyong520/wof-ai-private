import unittest
from unittest.mock import patch

from wof_launcher.browser import is_loopback_host, probe_endpoint, websocket_matches_endpoint


class EndpointHardeningTests(unittest.TestCase):
    def test_remote_host_rejected_before_probe(self):
        with patch("wof_launcher.browser._http_json") as http_json:
            self.assertIsNone(probe_endpoint("192.168.1.10", 9223))
            http_json.assert_not_called()

    def test_cross_port_websocket_rejected(self):
        payload={"Browser":"Chromium","webSocketDebuggerUrl":"ws://127.0.0.1:9333/devtools/browser/x"}
        with patch("wof_launcher.browser._http_json", return_value=payload):
            self.assertIsNone(probe_endpoint("127.0.0.1", 9223))

    def test_loopback_alias_websocket_accepted(self):
        payload={"Browser":"Chromium","webSocketDebuggerUrl":"ws://127.0.0.1:9223/devtools/browser/x"}
        with patch("wof_launcher.browser._http_json", return_value=payload):
            endpoint=probe_endpoint("localhost", 9223)
        self.assertIsNotNone(endpoint)
        self.assertEqual(9223, endpoint.port)

    def test_ipv6_loopback_is_allowed(self):
        self.assertTrue(is_loopback_host("::1"))
        self.assertTrue(websocket_matches_endpoint("ws://[::1]:9223/devtools/browser/x", "::1", 9223))

    def test_remote_returned_websocket_rejected(self):
        payload={"Browser":"Chromium","webSocketDebuggerUrl":"ws://10.0.0.2:9223/devtools/browser/x"}
        with patch("wof_launcher.browser._http_json", return_value=payload):
            self.assertIsNone(probe_endpoint("localhost", 9223))


if __name__ == "__main__":
    unittest.main()
