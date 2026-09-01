import time
import unittest

import discovery_v2 as d

EXPECTED_SHA = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
LIGHT = "LIGHT"
IDENTITY = "IDENTITY"


class FakeSession:
    def __init__(self, client, target_id, session_id):
        self.client = client
        self.target_id = target_id
        self.session_id = session_id
        self.closed = False
        self.methods = []

    def request(self, method, params=None, timeout=None):
        self.methods.append(method)
        return {}

    def evaluate(self, expression, await_promise=False, timeout=8.0):
        behavior = self.client.behavior.get(self.target_id, {})
        if expression == LIGHT:
            return behavior.get("light", {"moduleOk": False, "heapOk": False, "ramWithinHeap": False})
        if expression == IDENTITY:
            return behavior.get("identity", {"ok": False, "reason": "wrong"})
        raise RuntimeError("unexpected expression")

    def close(self):
        self.closed = True


class FakeClient:
    def __init__(self, targets, events=None, behavior=None):
        self.targets_snapshot = list(targets)
        self.events = list(events or [])
        self.behavior = dict(behavior or {})
        self.sessions = []
        self._cursor = 0

    def attach(self, target_id):
        session = FakeSession(self, target_id, f"s-{target_id}-{len(self.sessions)}")
        self.sessions.append(session)
        return session

    def event_cursor(self):
        return self._cursor

    def wait_for_events(self, cursor, *, timeout, predicate=None):
        for seq, event in enumerate(self.events, start=1):
            if seq <= cursor:
                continue
            self._cursor = max(self._cursor, seq)
            if predicate is None or predicate(event):
                return seq, [event]
        time.sleep(min(max(timeout, 0.0), 0.001))
        return max(cursor, self._cursor), []


def sf(client, target_id, session_id):
    session = FakeSession(client, target_id, session_id)
    client.sessions.append(session)
    return session


def good_behavior():
    return {
        "light": {"moduleOk": True, "heapOk": True, "ramWithinHeap": True, "readOnly": True, "ramWrites": 0, "inputInjection": False},
        "identity": {"ok": True, "sha256": EXPECTED_SHA, "readOnly": True, "ramWrites": 0, "inputInjection": False},
    }


def discover(client, **kwargs):
    return d.discover_candidates(
        client,
        client.targets_snapshot,
        session_factory=sf,
        light_probe_js=LIGHT,
        identity_probe_js=IDENTITY,
        expected_sha256=EXPECTED_SHA,
        settle_seconds=0.012,
        **kwargs,
    )


class DiscoveryV2Tests(unittest.TestCase):
    def test_01_direct_worker_backward_compatibility(self):
        targets = [
            {"targetId": "p", "type": "page", "url": "https://game.example/wof"},
            {"targetId": "w", "type": "worker", "url": "https://game.example/gstyphoon.js", "parentId": "p"},
        ]
        client = FakeClient(targets, behavior={"w": good_behavior()})
        rows, diag = discover(client)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].path, "direct-worker")
        self.assertEqual(diag["candidateCount"], 1)
        rows[0].close()

    def test_02_related_target_only(self):
        page = {"targetId": "p", "type": "page", "url": "https://game.example/wof"}
        worker = {"targetId": "w", "type": "worker", "url": "https://cdn.example/runtime-8d1.mjs"}
        events = [{"method": "Target.attachedToTarget", "sessionId": "s-p-0", "params": {"sessionId": "s-worker", "targetInfo": worker}}]
        client = FakeClient([page], events, {"w": good_behavior()})
        rows, diag = discover(client)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].path, "page-autoattach")
        self.assertEqual(diag["relatedPages"][0]["supportedObserved"], 1)
        rows[0].close()

    def test_03_iframe_to_worker_topology(self):
        page = {"targetId": "p", "type": "page", "url": "https://game.example/wof"}
        frame = {"targetId": "f", "type": "iframe", "url": "https://game.example/frame"}
        worker = {"targetId": "w", "type": "shared_worker", "url": "blob:https://game.example/abc"}
        events = [
            {"method": "Target.attachedToTarget", "sessionId": "s-p-0", "params": {"sessionId": "s-frame", "targetInfo": frame}},
            {"method": "Target.attachedToTarget", "sessionId": "s-frame", "params": {"sessionId": "s-worker", "targetInfo": worker}},
        ]
        client = FakeClient([page], events, {"w": good_behavior()})
        rows, diag = discover(client)
        self.assertEqual(len(rows), 1)
        topology = diag["relatedPages"][0]["relatedTopology"]
        self.assertEqual([x["type"] for x in topology], ["iframe", "shared_worker"])
        self.assertGreaterEqual(len(rows[0].owner_sessions), 2)
        rows[0].close()

    def test_04_url_mismatch_but_valid_related_runtime(self):
        page = {"targetId": "p", "type": "page", "url": "https://game.example/wof"}
        worker = {"targetId": "w", "type": "service_worker", "url": "https://cdn.example/assets/a9f3.bundle"}
        events = [{"method": "Target.attachedToTarget", "sessionId": "s-p-0", "params": {"sessionId": "s-worker", "targetInfo": worker}}]
        client = FakeClient([page], events, {"w": good_behavior()})
        rows, _ = discover(client)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].target["url"], worker["url"])
        rows[0].close()

    def test_05_wasm_not_ready_fails_closed(self):
        page = {"targetId": "p", "type": "page"}
        worker = {"targetId": "w", "type": "worker", "url": "blob:x"}
        events = [{"method": "Target.attachedToTarget", "sessionId": "s-p-0", "params": {"sessionId": "s-worker", "targetInfo": worker}}]
        client = FakeClient([page], events, {"w": {"light": {"moduleOk": False, "heapOk": False, "ramWithinHeap": False}}})
        rows, diag = discover(client)
        self.assertEqual(rows, [])
        self.assertEqual(diag["relatedPages"][0]["probedWorkers"][0]["status"], "wasm-not-ready")

    def test_06_wrong_world_identity_fails_closed(self):
        bad = good_behavior()
        bad["identity"] = {"ok": True, "sha256": "0" * 64, "readOnly": True, "ramWrites": 0, "inputInjection": False}
        targets = [{"targetId": "p", "type": "page"}, {"targetId": "w", "type": "worker", "parentId": "p"}]
        client = FakeClient(targets, behavior={"w": bad})
        rows, diag = discover(client)
        self.assertEqual(rows, [])
        self.assertIn("wrong-identity", {x.get("status") for x in diag["directWorkers"]})

    def test_07_ambiguous_workers_fail_closed(self):
        page = {"targetId": "p", "type": "page"}
        w1 = {"targetId": "w1", "type": "worker", "url": "one.js"}
        w2 = {"targetId": "w2", "type": "shared_worker", "url": "two.js"}
        events = [
            {"method": "Target.attachedToTarget", "sessionId": "s-p-0", "params": {"sessionId": "s-w1", "targetInfo": w1}},
            {"method": "Target.attachedToTarget", "sessionId": "s-p-0", "params": {"sessionId": "s-w2", "targetInfo": w2}},
        ]
        client = FakeClient([page], events, {"w1": good_behavior(), "w2": good_behavior()})
        rows, diag = discover(client)
        self.assertEqual(rows, [])
        self.assertTrue(diag["relatedPages"][0]["ambiguous"])
        self.assertEqual(d.ambiguous_page_ids(diag), {"p"})

    def test_08_worker_replacement_reload_liveness(self):
        self.assertEqual(
            d.room_liveness_reason(
                discovery_path="direct-worker", target_id="old", page_id="p",
                current_target_ids={"new", "p"}, current_page_ids={"p"},
            ),
            "worker-closed-or-reloaded",
        )
        self.assertIsNone(
            d.room_liveness_reason(
                discovery_path="page-autoattach", target_id="old", page_id="p",
                current_target_ids={"p"}, current_page_ids={"p"},
            )
        )
        self.assertEqual(
            d.room_liveness_reason(
                discovery_path="page-autoattach", target_id="old", page_id="p",
                current_target_ids=set(), current_page_ids=set(),
            ),
            "page-closed-or-reloaded",
        )

    def test_09_two_and_ten_endpoint_isolation(self):
        sessions = []
        for idx in range(10):
            targets = [
                {"targetId": "p", "type": "page", "browserContextId": f"ctx-{idx}"},
                {"targetId": "w", "type": "worker", "parentId": "p", "browserContextId": f"ctx-{idx}"},
            ]
            client = FakeClient(targets, behavior={"w": good_behavior()})
            rows, diag = discover(client, endpoint_label=f"endpoint-{idx}")
            self.assertEqual(len(rows), 1)
            self.assertEqual(diag["endpointLabel"], f"endpoint-{idx}")
            sessions.append(rows[0].session)
        self.assertEqual(len({id(s.client) for s in sessions[:2]}), 2)
        self.assertEqual(len({id(s.client) for s in sessions}), 10)
        for session in sessions:
            session.close()

    def test_10_discovery_is_explicitly_non_prospective(self):
        client = FakeClient([])
        _, diag = discover(client, endpoint_label="e")
        self.assertEqual(diag["evidenceClass"], "discovery-only")
        self.assertNotEqual(diag["evidenceClass"], "prospective")

    def test_11_read_only_allowlist_has_no_gameplay_input(self):
        self.assertIn("Target.setAutoAttach", d.DISCOVERY_CDP_METHODS)
        self.assertFalse(any(x.startswith("Input.") for x in d.DISCOVERY_CDP_METHODS))
        self.assertNotIn("Runtime.callFunctionOn", d.DISCOVERY_CDP_METHODS)
        self.assertNotIn("Page.addScriptToEvaluateOnNewDocument", d.DISCOVERY_CDP_METHODS)

    def test_12_worker_url_shape_is_not_the_identity_gate(self):
        for url in ["blob:https://x/id", "https://x/hash.123", "https://x/no-extension", "data:text/javascript,x"]:
            self.assertTrue(d._worker_compatible({"type": "worker", "url": url}, related=False))


if __name__ == "__main__":
    unittest.main(verbosity=2)
