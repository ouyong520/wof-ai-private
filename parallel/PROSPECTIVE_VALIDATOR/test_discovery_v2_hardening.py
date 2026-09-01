import unittest

import discovery_v2_hardening as h


class DummyCandidate:
    def __init__(self, page_id, worker_id):
        self.page = {"targetId": page_id}
        self.target = {"targetId": worker_id}
        self.closed = False

    def close(self):
        self.closed = True


class DiscoveryV2HardeningTests(unittest.TestCase):
    def test_shared_worker_under_two_pages_is_rejected_globally(self):
        a = DummyCandidate("page-a", "worker-shared")
        b = DummyCandidate("page-b", "worker-shared")
        rows, diag = h.harden_relation_graph([a, b], {"candidateCount": 2, "evidenceClass": "discovery-only"})
        self.assertEqual(rows, [])
        self.assertTrue(a.closed and b.closed)
        self.assertEqual(h.ambiguous_page_ids(diag), {"page-a", "page-b"})
        self.assertEqual(diag["crossPageAmbiguities"][0]["status"], h.CROSS_PAGE_STATUS)
        self.assertEqual(diag["crossPageAmbiguities"][0]["evidenceClass"], "discovery-only")

    def test_two_pages_two_distinct_workers_are_independent(self):
        a = DummyCandidate("page-a", "worker-a")
        b = DummyCandidate("page-b", "worker-b")
        rows, diag = h.harden_relation_graph([a, b], {"candidateCount": 2})
        self.assertEqual(rows, [a, b])
        self.assertEqual(diag["candidateCount"], 2)
        self.assertEqual(diag["crossPageAmbiguities"], [])

    def test_direct_fallback_never_uses_opener_as_parent_authority(self):
        pages = [
            {"targetId": "wrong", "url": "https://example.invalid/not-game"},
            {"targetId": "wof", "url": "https://example.invalid/wof"},
        ]
        page = h.safe_page_for_direct({"openerId": "wrong"}, pages)
        self.assertEqual(page["targetId"], "wof")
        self.assertIsNone(h.safe_page_for_direct({"openerId": "wrong"}, [
            {"targetId": "a", "url": "https://example.invalid/other"},
            {"targetId": "b", "url": "https://example.invalid/other2"},
        ]))

    def test_parent_id_remains_authoritative(self):
        pages = [{"targetId": "a", "url": "x"}, {"targetId": "b", "url": "y"}]
        self.assertEqual(h.safe_page_for_direct({"parentId": "b", "openerId": "a"}, pages)["targetId"], "b")

    def test_endpoint_must_be_loopback_and_same_port(self):
        self.assertTrue(h.websocket_matches_endpoint("ws://localhost:9222/devtools/browser/x", "127.0.0.1", 9222))
        self.assertTrue(h.websocket_matches_endpoint("ws://[::1]:9222/devtools/browser/x", "localhost", 9222))
        self.assertFalse(h.websocket_matches_endpoint("ws://localhost:9333/devtools/browser/x", "127.0.0.1", 9222))
        self.assertFalse(h.websocket_matches_endpoint("ws://192.168.1.5:9222/devtools/browser/x", "127.0.0.1", 9222))
        self.assertFalse(h.websocket_matches_endpoint("ws://localhost:9222/devtools/browser/x", "192.168.1.5", 9222))


if __name__ == "__main__":
    unittest.main(verbosity=2)
