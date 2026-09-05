import unittest

from wof_launcher.cdp import CdpError, CdpSession
from wof_launcher.discovery_v2 import _deduplicate_targets, _direct_page, discover


GOOD_LIGHT = {
    "moduleOk": True,
    "heapOk": True,
    "moduleKey": "m",
    "heapBytes": 123,
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
}
GOOD_ID = {
    "ok": True,
    "sha256": "a" * 64,
    "reason": "exact World identity fixture",
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
}


class FakeClient:
    def __init__(self, targets, *, page=None, light=None, identity=None, stale=None, frame_ids=None):
        self.targets = targets
        self.page = page or {}
        self.light = light or {}
        self.identity = identity or {}
        self.stale = set(stale or [])
        self.frame_ids = frame_ids or {}
        self.sessions = {}
        self.next = 1

    def attach(self, tid):
        if tid in self.stale:
            raise CdpError("stale target")
        sid = f"s{self.next}"
        self.next += 1
        self.sessions[sid] = tid
        return CdpSession(self, tid, sid)

    def event_cursor(self):
        return 0

    def wait_for_events(self, cursor, *, timeout, predicate=None):
        return cursor, []

    def request(self, method, params=None, *, session_id=None, timeout=None):
        params = params or {}
        if method == "Target.getTargets":
            return {"targetInfos": self.targets}
        if method == "Target.detachFromTarget":
            self.sessions.pop(params.get("sessionId"), None)
            return {}
        if method == "Target.setAutoAttach":
            return {}
        if method == "Runtime.enable":
            return {}
        if method == "Page.getFrameTree":
            tid = self.sessions.get(session_id)
            root = {"frame": {"id": f"root-{tid}"}}
            ids = list(self.frame_ids.get(tid, []))
            if ids:
                root["childFrames"] = [{"frame": {"id": frame_id}} for frame_id in ids]
            return {"frameTree": root}
        if method == "Runtime.evaluate":
            tid = self.sessions.get(session_id)
            expr = params.get("expression", "")
            if "gameSurface" in expr:
                value = self.page.get(tid, {"gameSurface": False, "readOnly": True})
            elif "ramWithinHeap" in expr:
                value = self.light.get(tid, {"moduleOk": False, "heapOk": False, "readOnly": True, "ramWrites": 0, "inputInjection": False})
            elif "const EXPECTED=" in expr:
                value = self.identity.get(tid, {"ok": False, "reason": "wrong World", "readOnly": True, "ramWrites": 0, "inputInjection": False})
            else:
                value = None
            return {"result": {"value": value}}
        raise CdpError(method)


class P31PageAssociationAuthorityTests(unittest.TestCase):
    def test_parent_id_selects_same_page_independent_of_input_order(self):
        p1 = {"targetId": "p1", "type": "page", "wofPageProbe": {"gameSurface": True}}
        p2 = {"targetId": "p2", "type": "page", "wofPageProbe": {"gameSurface": True}}
        worker = {"targetId": "w", "type": "worker", "parentId": "p2"}
        self.assertEqual("p2", _direct_page(worker, [p1, p2])["targetId"])
        self.assertEqual("p2", _direct_page(worker, [p2, p1])["targetId"])

    def test_parent_frame_id_is_authoritative(self):
        p1 = {"targetId": "p1", "type": "page", "cdpFrameIds": ["f1"]}
        p2 = {"targetId": "p2", "type": "page", "cdpFrameIds": ["f2"]}
        worker = {"targetId": "w", "type": "worker", "parentFrameId": "f2"}
        self.assertEqual("p2", _direct_page(worker, [p1, p2])["targetId"])

    def test_parent_id_outranks_parent_frame_without_order_guessing(self):
        p1 = {"targetId": "p1", "type": "page", "cdpFrameIds": ["f1"]}
        p2 = {"targetId": "p2", "type": "page", "cdpFrameIds": ["f2"]}
        worker = {"targetId": "w", "type": "worker", "parentId": "p1", "parentFrameId": "f2"}
        self.assertEqual("p1", _direct_page(worker, [p2, p1])["targetId"])

    def test_unique_runtime_game_surface_can_disambiguate_but_url_alone_cannot(self):
        p1 = {"targetId": "p1", "type": "page", "url": "https://host/wof", "wofPageProbe": {"gameSurface": True}}
        p2 = {"targetId": "p2", "type": "page", "url": "https://host/wof/help", "wofPageProbe": {"gameSurface": False}}
        worker = {"targetId": "w", "type": "worker"}
        self.assertEqual("p1", _direct_page(worker, [p2, p1])["targetId"])
        url_only = [
            {"targetId": "p1", "type": "page", "url": "https://host/wof"},
            {"targetId": "p2", "type": "page", "url": "https://host/help"},
        ]
        self.assertIsNone(_direct_page(worker, url_only))

    def test_identical_duplicate_target_collapses_without_order_selection(self):
        p = {"targetId": "p", "type": "page", "url": "https://host/wof"}
        targets, rejected, conflicts = _deduplicate_targets([p, dict(p)])
        self.assertEqual(["p"], [t["targetId"] for t in targets])
        self.assertEqual([], conflicts)
        self.assertEqual("duplicate-targetId-identical", rejected[0]["reason"])

    def test_conflicting_duplicate_target_id_is_rejected_fail_closed(self):
        p1 = {"targetId": "p", "type": "page", "url": "https://host/wof"}
        p2 = {"targetId": "p", "type": "page", "url": "https://stale.example/wof"}
        targets, rejected, conflicts = _deduplicate_targets([p1, p2])
        self.assertEqual([], targets)
        self.assertEqual(["p"], conflicts)
        self.assertEqual("conflicting-duplicate-targetId", rejected[-1]["reason"])
        choice = discover(FakeClient([p1, p2]))
        self.assertIsNone(choice.page)
        self.assertIn("conflicting duplicate CDP target identities", choice.reason)
        self.assertEqual("target-identity-conflict", choice.diagnostics["path"])

    def test_stale_page_target_is_rejected_before_authoritative_worker_link(self):
        stale = {"targetId": "old", "type": "page", "url": "https://host/wof"}
        live = {"targetId": "live", "type": "page", "url": "https://host/wof"}
        worker = {"targetId": "w", "type": "worker", "url": "blob:https://host/runtime", "parentId": "live"}
        choice = discover(
            FakeClient(
                [stale, live, worker],
                stale={"old"},
                page={"live": {"gameSurface": True}},
                light={"w": GOOD_LIGHT},
                identity={"w": GOOD_ID},
            ),
            identity_timeout=0.1,
        )
        self.assertEqual("live", choice.page["targetId"])
        self.assertEqual("w", choice.worker["targetId"])
        self.assertEqual("direct-worker", choice.diagnostics["path"])
        self.assertTrue(any(row.get("targetId") == "old" and row.get("reason") == "stale-or-unattachable-page-target" for row in choice.diagnostics["rejectedTargets"]))

    def test_two_live_game_pages_without_authority_remain_fail_closed(self):
        p1 = {"targetId": "p1", "type": "page", "url": "https://a/wof", "wofPageProbe": {"gameSurface": True}}
        p2 = {"targetId": "p2", "type": "page", "url": "https://b/wof", "wofPageProbe": {"gameSurface": True}}
        worker = {"targetId": "w", "type": "worker"}
        self.assertIsNone(_direct_page(worker, [p1, p2]))
        self.assertIsNone(_direct_page(worker, [p2, p1]))


if __name__ == "__main__":
    unittest.main()
