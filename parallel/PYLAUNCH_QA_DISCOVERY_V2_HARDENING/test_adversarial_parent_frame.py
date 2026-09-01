from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "parallel" / "PYLAUNCH"))

from wof_launcher.cdp import CdpError, CdpSession  # noqa: E402
from wof_launcher.discovery_v2 import discover  # noqa: E402
from wof_launcher.probe import WORLD_SHA256  # noqa: E402

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


class FrameAwareFakeClient:
    """Synthetic CDP endpoint where parentFrameId is enough to disambiguate two WOF pages.

    A correct direct-fallback implementation may obtain the page root frame through
    Page.getFrameTree (or an equivalent execution-context frame map). The current
    implementation never requests either surface, so the available authority is lost.
    """

    def __init__(self) -> None:
        self.targets = [
            {"targetId": "page-a", "type": "page", "url": "https://a.example/wof"},
            {"targetId": "page-b", "type": "page", "url": "https://b.example/wof"},
            {
                "targetId": "worker-b",
                "type": "worker",
                "url": "blob:https://b.example/runtime",
                "parentFrameId": "frame-b",
            },
        ]
        self.sessions: dict[str, str] = {}
        self.next_session = 1
        self.auto_attach_sessions: set[str] = set()
        self.methods: list[str] = []

    def attach(self, target_id: str) -> CdpSession:
        sid = f"s{self.next_session}"
        self.next_session += 1
        self.sessions[sid] = target_id
        return CdpSession(self, target_id, sid)

    def event_cursor(self) -> int:
        return 0

    def wait_for_events(self, cursor: int, *, timeout: float, predicate=None):
        return cursor, []

    def request(self, method: str, params=None, *, session_id=None, timeout=None):
        self.methods.append(method)
        params = params or {}
        if method == "Target.getTargets":
            return {"targetInfos": self.targets}
        if method == "Target.detachFromTarget":
            self.sessions.pop(params.get("sessionId"), None)
            return {}
        if method == "Target.setAutoAttach":
            self.auto_attach_sessions.add(str(session_id))
            return {}
        if method == "Runtime.enable":
            return {}
        if method == "Runtime.evaluate":
            target_id = self.sessions.get(str(session_id))
            expression = str(params.get("expression") or "")
            if "gameSurface" in expression:
                return {"result": {"value": {"gameSurface": True, "readOnly": True}}}
            if "ramWithinHeap" in expression:
                value = GOOD_LIGHT if target_id == "worker-b" else {"moduleOk": False}
                return {"result": {"value": value}}
            if "const EXPECTED=" in expression:
                value = GOOD_ID if target_id == "worker-b" else {"ok": False, "reason": "wrong World"}
                return {"result": {"value": value}}
            return {"result": {"value": None}}
        if method == "Page.getFrameTree":
            target_id = self.sessions.get(str(session_id))
            frame_id = "frame-a" if target_id == "page-a" else "frame-b"
            return {"frameTree": {"frame": {"id": frame_id, "url": f"https://{target_id}.example/wof"}}}
        raise CdpError(method)


class IndependentParentFrameAdversarialTests(unittest.TestCase):
    def test_two_wof_pages_direct_worker_must_use_unique_parent_frame_mapping(self) -> None:
        client = FrameAwareFakeClient()
        choice = discover(client)

        # Contract required by the hardening QA: the real parentFrameId, when uniquely
        # mappable to one page, remains a valid direct Worker parent authority.
        self.assertIsNotNone(choice.worker)
        self.assertIsNotNone(choice.page)
        self.assertEqual("worker-b", choice.worker["targetId"])
        self.assertEqual("page-b", choice.page["targetId"])
        self.assertEqual("frame-b", choice.worker["parentFrameId"])

        # This additionally proves that frame authority was actually consulted rather
        # than accidentally passing because only one WOF page existed.
        self.assertIn("Page.getFrameTree", client.methods)


if __name__ == "__main__":
    unittest.main(verbosity=2)
