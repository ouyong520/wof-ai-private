from __future__ import annotations

import unittest

from wof_launcher.cdp import CdpError, CdpSession, READ_ONLY_METHODS
from wof_launcher.discovery_v2 import discover
from wof_launcher.probe import WORLD_SHA256

GOOD_LIGHT = {
    "moduleOk": True,
    "heapOk": True,
    "moduleKey": "m",
    "heapBytes": 0x200000,
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
}
GOOD_ID = {
    "ok": True,
    "sha256": WORLD_SHA256,
    "reason": "exact World 921031 full CPU-logical SHA-256",
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
}


class FrameTreeFakeClient:
    def __init__(self, targets, frame_ids):
        self.targets = targets
        self.frame_ids = frame_ids
        self.sessions = {}
        self.next_session = 1
        self.methods = []

    def attach(self, target_id):
        sid = f"s{self.next_session}"
        self.next_session += 1
        self.sessions[sid] = target_id
        return CdpSession(self, target_id, sid)

    def event_cursor(self):
        return 0

    def wait_for_events(self, cursor, *, timeout, predicate=None):
        return cursor, []

    def request(self, method, params=None, *, session_id=None, timeout=None):
        self.methods.append(method)
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
        if method == "Runtime.evaluate":
            target_id = self.sessions.get(session_id)
            expression = str(params.get("expression") or "")
            if "gameSurface" in expression:
                return {"result": {"value": {"gameSurface": True, "readOnly": True}}}
            if "ramWithinHeap" in expression:
                return {"result": {"value": GOOD_LIGHT if target_id == "worker" else {"moduleOk": False}}}
            if "const EXPECTED=" in expression:
                return {"result": {"value": GOOD_ID if target_id == "worker" else {"ok": False, "reason": "wrong World"}}}
            return {"result": {"value": None}}
        if method == "Page.getFrameTree":
            target_id = self.sessions.get(session_id)
            ids = self.frame_ids.get(target_id)
            if not ids:
                raise CdpError("no frame tree")
            if isinstance(ids, str):
                ids = [ids]
            return {
                "frameTree": {
                    "frame": {"id": ids[0]},
                    "childFrames": [{"frame": {"id": frame_id}} for frame_id in ids[1:]],
                }
            }
        raise CdpError(method)


class ParentFrameAuthorityTests(unittest.TestCase):
    @staticmethod
    def _targets(parent_frame_id="frame-b", *, parent_id=None, opener_id=None):
        worker = {
            "targetId": "worker",
            "type": "worker",
            "url": "blob:https://b.example/runtime",
            "parentFrameId": parent_frame_id,
        }
        if parent_id is not None:
            worker["parentId"] = parent_id
        if opener_id is not None:
            worker["openerId"] = opener_id
        return [
            {"targetId": "page-a", "type": "page", "url": "https://a.example/wof"},
            {"targetId": "page-b", "type": "page", "url": "https://b.example/wof"},
            worker,
        ]

    def test_discover_consumes_unique_parent_frame_from_page_get_frame_tree(self):
        client = FrameTreeFakeClient(
            self._targets(),
            {"page-a": ["frame-a"], "page-b": ["frame-b"]},
        )
        choice = discover(client)

        self.assertEqual("worker", choice.worker["targetId"])
        self.assertEqual("page-b", choice.page["targetId"])
        self.assertEqual("direct-worker", choice.diagnostics["path"])
        self.assertIn("Page.getFrameTree", client.methods)
        self.assertIn("frame-b", next(row for row in choice.diagnostics["pageSignals"] if row["targetId"] == "page-b")["frameIds"])

    def test_child_frame_id_maps_to_owning_page(self):
        client = FrameTreeFakeClient(
            self._targets(parent_frame_id="child-b"),
            {"page-a": ["frame-a", "child-a"], "page-b": ["frame-b", "child-b"]},
        )
        choice = discover(client)
        self.assertEqual("page-b", choice.page["targetId"])

    def test_duplicate_parent_frame_mapping_fails_closed(self):
        client = FrameTreeFakeClient(
            self._targets(parent_frame_id="frame-shared"),
            {"page-a": ["frame-shared"], "page-b": ["frame-shared"]},
        )
        choice = discover(client)

        self.assertIsNone(choice.page)
        self.assertIsNone(choice.worker)
        self.assertIn("association is ambiguous", choice.reason)

    def test_parent_id_remains_higher_authority_than_parent_frame(self):
        client = FrameTreeFakeClient(
            self._targets(parent_frame_id="frame-b", parent_id="page-a"),
            {"page-a": ["frame-a"], "page-b": ["frame-b"]},
        )
        choice = discover(client)
        self.assertEqual("page-a", choice.page["targetId"])

    def test_read_only_allowlist_adds_only_frame_introspection_surface(self):
        self.assertIn("Page.getFrameTree", READ_ONLY_METHODS)
        self.assertNotIn("Input.dispatchKeyEvent", READ_ONLY_METHODS)
        self.assertNotIn("Runtime.callFunctionOn", READ_ONLY_METHODS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
