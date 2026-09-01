from __future__ import annotations

import unittest
from unittest.mock import patch

from wof_launcher.browser import probe_endpoint


class StartupVersionAttestationRegressionTests(unittest.TestCase):
    """Fresh QA repro for the current-head startup /json/version attestation regression."""

    def test_missing_browser_metadata_must_fail_closed(self) -> None:
        payload = {
            "webSocketDebuggerUrl": "ws://127.0.0.1:9223/devtools/browser/repro"
        }
        with patch("wof_launcher.browser._http_json", return_value=payload):
            endpoint = probe_endpoint("127.0.0.1", 9223)
        self.assertIsNone(
            endpoint,
            "startup /json/version without Browser metadata must be rejected, not synthesized as Chromium",
        )

    def test_non_browser_websocket_path_must_fail_closed(self) -> None:
        payload = {
            "Browser": "Chromium/QA",
            "webSocketDebuggerUrl": "ws://127.0.0.1:9223/devtools/page/not-a-browser-endpoint",
        }
        with patch("wof_launcher.browser._http_json", return_value=payload):
            endpoint = probe_endpoint("127.0.0.1", 9223)
        self.assertIsNone(
            endpoint,
            "startup attestation must require the browser-level /devtools/browser/ websocket path",
        )


if __name__ == "__main__":
    unittest.main()
