import unittest

from wof_launcher.cdp import CdpClient, CdpError
from wof_launcher.probe import WORLD_SHA256, choose_unique_supported_worker, is_gstyphoon_worker


class DiscoveryTests(unittest.TestCase):
    def test_gstyphoon_worker_url(self):
        self.assertTrue(is_gstyphoon_worker({"type": "worker", "url": "https://x/a/gstyphoon123.js"}))
        self.assertTrue(is_gstyphoon_worker({"type": "worker", "url": "https://x/gstyphoon.js?v=4"}))
        self.assertFalse(is_gstyphoon_worker({"type": "worker", "url": "https://x/other.js"}))
        self.assertFalse(is_gstyphoon_worker({"type": "page", "url": "https://x/gstyphoon.js"}))

    def test_unique_supported_worker(self):
        rows = [
            ({"targetId": "a"}, {"moduleOk": True}, {"ok": True, "sha256": WORLD_SHA256}),
            ({"targetId": "b"}, {"moduleOk": True}, {"ok": False}),
        ]
        chosen = choose_unique_supported_worker(rows)
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen[0]["targetId"], "a")

    def test_ambiguous_supported_worker_fails_closed(self):
        rows = [
            ({"targetId": "a"}, {"moduleOk": True}, {"ok": True}),
            ({"targetId": "b"}, {"moduleOk": True}, {"ok": True}),
        ]
        self.assertIsNone(choose_unique_supported_worker(rows))

    def test_cdp_method_allowlist_blocks_input(self):
        client = CdpClient("ws://invalid")
        with self.assertRaises(CdpError):
            client.request("Input.dispatchKeyEvent", {"type": "keyDown", "key": "A"})


if __name__ == "__main__":
    unittest.main()
