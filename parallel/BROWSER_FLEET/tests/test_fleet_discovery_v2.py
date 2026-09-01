from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "fleet_discovery_v2.py"
SPEC = importlib.util.spec_from_file_location("fleet_discovery_v2_under_test", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class FakeClient:
    def __init__(self, targets, probes=None, events=None):
        self.targets = targets
        self.probes = probes or {}
        self.events = list(events or [])
        self.sessions = {}
        self.wait_done = False

    def request(self, method, params=None, *, session_id=None, timeout=None):
        params = params or {}
        if method == "Target.getTargets":
            return {"targetInfos": self.targets}
        if method == "Target.attachToTarget":
            tid = str(params.get("targetId"))
            sid = f"direct:{tid}"
            self.sessions[sid] = tid
            return {"sessionId": sid}
        if method in {"Runtime.enable", "Target.setAutoAttach", "Target.detachFromTarget"}:
            return {}
        if method == "Runtime.evaluate":
            tid = self.sessions.get(session_id, session_id)
            probe = self.probes.get(tid, {})
            return {"result": {"value": probe}}
        raise AssertionError(method)

    def attach(self, target_id):
        sid = f"direct:{target_id}"
        self.sessions[sid] = target_id
        return mod.CdpSession(self, target_id, sid)

    def event_cursor(self):
        return 0

    def wait_for_events(self, cursor, *, timeout, predicate=None):
        if self.wait_done:
            return cursor, []
        self.wait_done = True
        for event in self.events:
            params = event.get("params") or {}
            sid = str(params.get("sessionId") or "")
            info = params.get("targetInfo") or {}
            if sid:
                self.sessions[sid] = str(info.get("targetId") or "")
        rows = [event for event in self.events if predicate is None or predicate(event)]
        return len(self.events), rows


PAGE = {"targetId": "p1", "type": "page", "url": "https://example.invalid/wof", "title": "WOF"}
PAGE_PROBE = {"gameSurface": True, "href": PAGE["url"], "title": "WOF"}
MODULE_OK = {"moduleOk": True, "heapOk": True, "heapBytes": 1234}


class DiscoveryV2Tests(unittest.TestCase):
    def test_direct_worker_backward_compatibility(self):
        worker = {"targetId": "w1", "type": "worker", "url": "https://x/gstyphoon-main.js"}
        result = mod.discover_fleet_status(FakeClient([PAGE, worker], {"p1": PAGE_PROBE}), settle_seconds=0)
        self.assertTrue(result.page_ok)
        self.assertTrue(result.worker_ok)
        self.assertEqual(result.worker_count, 1)
        self.assertEqual(result.path, "direct-worker-url-hint")

    def test_url_mismatch_but_related_runtime(self):
        worker = {"targetId": "w2", "type": "worker", "url": "blob:https://example.invalid/123"}
        event = {"sessionId": "direct:p1", "method": "Target.attachedToTarget", "params": {"sessionId": "child:w2", "targetInfo": worker}}
        result = mod.discover_fleet_status(FakeClient([PAGE], {"p1": PAGE_PROBE, "w2": MODULE_OK}, [event]), settle_seconds=0.01)
        self.assertTrue(result.worker_ok)
        self.assertEqual(result.path, "page-autoattach-module")

    def test_related_target_only(self):
        worker = {"targetId": "w3", "type": "worker", "url": "https://cdn.invalid/runtime.js"}
        event = {"sessionId": "direct:p1", "method": "Target.attachedToTarget", "params": {"sessionId": "child:w3", "targetInfo": worker}}
        result = mod.discover_fleet_status(FakeClient([PAGE], {"p1": PAGE_PROBE, "w3": MODULE_OK}, [event]), settle_seconds=0.01)
        self.assertEqual(result.worker_count, 1)
        self.assertEqual(result.topology_count, 1)

    def test_iframe_to_worker(self):
        iframe = {"targetId": "f1", "type": "iframe", "url": "https://example.invalid/frame"}
        worker = {"targetId": "w4", "type": "worker", "url": "https://cdn.invalid/runtime-v4.js"}
        events = [
            {"sessionId": "direct:p1", "method": "Target.attachedToTarget", "params": {"sessionId": "child:f1", "targetInfo": iframe}},
            {"sessionId": "child:f1", "method": "Target.attachedToTarget", "params": {"sessionId": "child:w4", "targetInfo": worker}},
        ]
        result = mod.discover_fleet_status(FakeClient([PAGE], {"p1": PAGE_PROBE, "w4": MODULE_OK}, events), settle_seconds=0.01)
        self.assertTrue(result.worker_ok)
        self.assertEqual(result.topology_count, 2)

    def test_reload_recreated_worker_is_not_stale(self):
        old = {"targetId": "old", "type": "worker", "url": "https://x/gstyphoon-old.js"}
        first = mod.discover_fleet_status(FakeClient([PAGE, old], {"p1": PAGE_PROBE}), settle_seconds=0)
        self.assertTrue(first.worker_ok)
        second = mod.discover_fleet_status(FakeClient([PAGE], {"p1": PAGE_PROBE}), settle_seconds=0)
        self.assertFalse(second.worker_ok)
        new = {"targetId": "new", "type": "worker", "url": "https://x/runtime-new.js"}
        third = mod.discover_fleet_status(FakeClient([PAGE, new], {"p1": PAGE_PROBE, "new": MODULE_OK}), settle_seconds=0)
        self.assertTrue(third.worker_ok)
        self.assertEqual(third.path, "direct-worker-module")


if __name__ == "__main__":
    unittest.main()
