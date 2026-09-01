from __future__ import annotations

import unittest

from wof_launcher.cdp import CdpError, CdpSession
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
WRONG_ID = {
    "ok": False,
    "sha256": "0" * 64,
    "reason": "full CPU-logical SHA-256 mismatch after runtime generation change",
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
}


class GenerationClient:
    """Two instances represent distinct browser/CDP connection generations."""

    def __init__(self, identity):
        self.identity = identity
        self.sessions = {}
        self.next_session = 1
        self.identity_eval_calls = 0
        self.targets = [
            {"targetId": "page-a", "type": "page", "url": "https://a.example/wof"},
            {"targetId": "page-b", "type": "page", "url": "https://b.example/wof"},
            {
                "targetId": "worker-stable",
                "type": "worker",
                "url": "blob:https://b.example/runtime-generation",
                "parentFrameId": "frame-b",
            },
        ]

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
            target_id = self.sessions.get(session_id)
            if target_id == "page-a":
                return {"frameTree": {"frame": {"id": "frame-a"}}}
            if target_id == "page-b":
                return {
                    "frameTree": {
                        "frame": {"id": "root-b"},
                        "childFrames": [{"frame": {"id": "frame-b"}}],
                    }
                }
            raise CdpError("frame tree requested on non-page target")
        if method == "Runtime.evaluate":
            target_id = self.sessions.get(session_id)
            expression = str(params.get("expression") or "")
            if "gameSurface" in expression:
                return {"result": {"value": {"gameSurface": True, "readOnly": True}}}
            if "ramWithinHeap" in expression:
                return {"result": {"value": GOOD_LIGHT if target_id == "worker-stable" else {"moduleOk": False}}}
            if "const EXPECTED=" in expression:
                self.identity_eval_calls += 1
                return {"result": {"value": self.identity}}
            return {"result": {"value": None}}
        raise CdpError(method)


class FreshGenerationAuthorityQa(unittest.TestCase):
    def test_new_cdp_generation_cannot_reuse_old_exact_identity_for_same_target_id(self):
        # This is intentionally a two-generation fixture, unlike the implementation
        # tests that only prune a cache entry after its targetId disappears.
        identity_cache = {}

        generation_1 = GenerationClient(GOOD_ID)
        first = discover(generation_1, identity_cache=identity_cache)
        self.assertEqual("page-b", first.page["targetId"])
        self.assertTrue(first.identity["ok"])
        self.assertEqual(1, generation_1.identity_eval_calls)
        self.assertIn("worker-stable", identity_cache)

        # Simulate a browser/CDP reconnect with a fresh runtime generation. The
        # target id is deliberately reused while the actual World identity is now
        # wrong. A fresh exact-identity probe must be required before authority can
        # be granted in this new connection/session generation.
        generation_2 = GenerationClient(WRONG_ID)
        second = discover(generation_2, identity_cache=identity_cache)

        self.assertEqual(
            1,
            generation_2.identity_eval_calls,
            "fresh CDP/runtime generation must re-probe exact World identity",
        )
        self.assertFalse(
            second.identity and second.identity.get("ok") is True,
            "stale exact World identity must not remain authoritative after reconnect",
        )
        self.assertIsNone(second.worker)


if __name__ == "__main__":
    unittest.main(verbosity=2)
