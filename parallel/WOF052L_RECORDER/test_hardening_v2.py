from __future__ import annotations

import inspect
import io
import types
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass

import discovery_v2_sync as discovery
import hardening_v2 as hardening
import recorder


WORLD = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"


def identity(ok: bool = True, sha: str = WORLD) -> dict:
    return {"ok": ok, "identity": {"ok": ok, "sha256": sha}, "reason": "ok" if ok else "bad"}


class Session:
    def __init__(self, client, target_id: str, session_id: str):
        self.client = client
        self.target_id = target_id
        self.session_id = session_id
        self.closed = False

    def request(self, method, params=None, timeout=None):
        self.client.methods.append((self.target_id, method))
        return {}

    def evaluate(self, expression, await_promise=False, timeout=8):
        self.client.evals.append((self.target_id, expression))
        state = self.client.state.get(self.target_id, {})
        if expression == "LIGHT":
            return state.get("light", {"moduleOk": True, "heapOk": True, "ramWithinHeap": True})
        if expression == "IDENTITY":
            return state.get("identity", identity())
        if expression == "FULL":
            return state.get("full", {"ok": True, "identity": {"sha256": WORLD}})
        return None

    def close(self):
        self.closed = True


class Client:
    def __init__(self, *, state=None, events_by_page=None, targets=None):
        self.state = state or {}
        self.events_by_page = events_by_page or {}
        self.target_rows = targets or []
        self.current_page = None
        self.sent_pages = set()
        self.methods = []
        self.evals = []

    def attach(self, target_id):
        if str(target_id).startswith("p"):
            self.current_page = str(target_id)
        return Session(self, str(target_id), "sid-" + str(target_id))

    def event_cursor(self):
        return 0

    def wait_for_events(self, cursor, *, timeout, predicate=None):
        page = self.current_page
        if not page or page in self.sent_pages:
            return cursor, []
        self.sent_pages.add(page)
        rows = list(self.events_by_page.get(page, []))
        if predicate is not None:
            rows = [row for row in rows if predicate(row)]
        return 1, rows

    def targets(self):
        return list(self.target_rows)


@dataclass
class Endpoint:
    host: str
    port: int


class Manager:
    def __init__(self, client, endpoint=None):
        self.client = client
        self.endpoint = endpoint
        self._wof052l_recorder_module = types.SimpleNamespace(
            WORLD_SHA256=WORLD,
            LIGHT_PROBE="LIGHT",
            CdpSession=Session,
        )
        self._wof052l_identity_probe_js = "IDENTITY"
        self._wof052l_identity_cache = {}
        self.probe_js = "FULL"
        self.live = {}


def page(target_id="p1"):
    return {"targetId": target_id, "type": "page", "url": f"https://example/{target_id}"}


def worker(target_id="w1", url="/gstyphoon.js", worker_type="worker", **extra):
    row = {"targetId": target_id, "type": worker_type, "url": url}
    row.update(extra)
    return row


def attached(parent_page: str, target: dict, session_id=None):
    return {
        "method": "Target.attachedToTarget",
        "sessionId": "sid-" + parent_page,
        "params": {
            "sessionId": session_id or "sid-" + target["targetId"],
            "targetInfo": target,
        },
    }


class FakeCandidate:
    def __init__(self, worker_id: str, page_id: str):
        self.target = {"targetId": worker_id}
        self.page = {"targetId": page_id}
        self.closed = False

    def close(self):
        self.closed = True


class FakeRoom:
    def __init__(self, worker_id: str, page_id: str, path="page-autoattach"):
        self.target = {"targetId": worker_id, "discoveryPath": path}
        self.page = {"targetId": page_id}


class EndpointGuardTests(unittest.TestCase):
    def test_loopback_aliases_and_remote_rejection(self):
        self.assertTrue(hardening.is_loopback_host("127.0.0.1"))
        self.assertTrue(hardening.is_loopback_host("localhost"))
        self.assertTrue(hardening.is_loopback_host("::1"))
        self.assertFalse(hardening.is_loopback_host("192.0.2.10"))

    def test_returned_websocket_must_stay_on_endpoint_port(self):
        self.assertEqual(
            hardening.validate_endpoint_websocket("127.0.0.1", 9223, "ws://localhost:9223/devtools/browser/x"),
            (True, "ok"),
        )
        self.assertEqual(
            hardening.validate_endpoint_websocket("localhost", 9223, "ws://127.0.0.1:9224/devtools/browser/x")[1],
            "returned-websocket-cross-port",
        )
        self.assertEqual(
            hardening.validate_endpoint_websocket("127.0.0.1", 9223, "ws://192.0.2.1:9223/devtools/browser/x")[1],
            "returned-websocket-remote-host",
        )
        self.assertEqual(
            hardening.validate_endpoint_websocket("192.0.2.1", 9223, "ws://127.0.0.1:9223/devtools/browser/x")[1],
            "remote-cdp-host-rejected",
        )

    def test_simulated_10_room_one_endpoint_failure_isolated(self):
        @dataclass(frozen=True)
        class BrowserEndpoint:
            host: str
            port: int
            browser: str
            websocket_url: str

        launched = []

        def http_json(url):
            port = int(url.split(":")[-1].split("/")[0])
            returned_port = 9999 if port == 9305 else port
            return {
                "Browser": "Chromium",
                "webSocketDebuggerUrl": f"ws://localhost:{returned_port}/devtools/browser/{port}",
            }

        fake = types.SimpleNamespace(
            http_json=http_json,
            BrowserEndpoint=BrowserEndpoint,
            launch_debug_browser=lambda *args: launched.append(args),
        )
        hardening._install_endpoint_guard(fake)
        results = [fake.probe_endpoint("127.0.0.1", 9300 + i) for i in range(10)]
        self.assertEqual(sum(row is not None for row in results), 9)
        self.assertIsNone(results[5])
        self.assertEqual(fake._WOF052L_LAST_ENDPOINT_REJECTION["reason"], "returned-websocket-cross-port")
        self.assertIsNone(fake.launch_debug_browser("auto", "192.0.2.1", 9223, None))
        self.assertEqual(launched, [])


class CandidatePolicyTests(unittest.TestCase):
    def test_existing_blob_data_and_hashed_workers_are_not_scheme_rejected(self):
        for url in (
            "blob:https://example/abc",
            "data:text/javascript;base64,Zm9v",
            "https://cdn.example/a1b2c3d4",
            "https://cdn.example/worker-main.mjs?v=9",
        ):
            with self.subTest(url=url):
                self.assertTrue(hardening.worker_compatible(worker(url=url), related=False))

    def test_direct_parent_authority_ignores_misleading_opener(self):
        pages = [page("p1"), page("p2")]
        chosen = hardening.page_for_direct(worker(parentId="p2", openerId="p1"), pages)
        self.assertEqual(chosen["targetId"], "p2")
        self.assertIsNone(hardening.page_for_direct(worker(openerId="p1"), pages))
        self.assertEqual(hardening.page_for_direct(worker(openerId="wrong"), [page("p1")])["targetId"], "p1")

    def test_parent_frame_mapping_precedes_unique_page_fallback(self):
        pages = [
            {**page("p1"), "frameId": "frame-1"},
            {**page("p2"), "frameId": "frame-2"},
        ]
        chosen = hardening.page_for_direct(worker(parentFrameId="frame-2", openerId="p1"), pages)
        self.assertEqual(chosen["targetId"], "p2")


class RelationGraphTests(unittest.TestCase):
    def test_one_page_one_worker_admitted(self):
        manager = types.SimpleNamespace(live={})
        candidate = FakeCandidate("w1", "p1")
        rows, diag = hardening.filter_cross_page_ambiguity(manager, [candidate], {"relatedPages": []})
        self.assertEqual(rows, [candidate])
        self.assertEqual(diag["crossPageAmbiguityCount"], 0)
        self.assertFalse(candidate.closed)

    def test_two_pages_two_distinct_workers_admitted(self):
        manager = types.SimpleNamespace(live={})
        c1, c2 = FakeCandidate("w1", "p1"), FakeCandidate("w2", "p2")
        rows, diag = hardening.filter_cross_page_ambiguity(manager, [c1, c2], {"relatedPages": []})
        self.assertEqual(rows, [c1, c2])
        self.assertEqual(diag["crossPageAmbiguityCount"], 0)

    def test_two_pages_same_shared_worker_admits_none(self):
        manager = types.SimpleNamespace(live={})
        c1, c2 = FakeCandidate("shared", "p1"), FakeCandidate("shared", "p2")
        rows, diag = hardening.filter_cross_page_ambiguity(
            manager,
            [c1, c2],
            {"relatedPages": [{"page": {"targetId": "p1"}}, {"page": {"targetId": "p2"}}]},
        )
        self.assertEqual(rows, [])
        self.assertTrue(c1.closed and c2.closed)
        self.assertEqual(diag["crossPageWorkerAmbiguities"][0]["status"], hardening.CROSS_PAGE_AMBIGUITY)
        self.assertEqual(diag["crossPageWorkerAmbiguities"][0]["pageTargetIds"], ["p1", "p2"])
        self.assertTrue(all(row.get("ambiguityReason") == hardening.CROSS_PAGE_AMBIGUITY for row in diag["relatedPages"]))

    def test_live_relation_is_part_of_endpoint_graph(self):
        manager = types.SimpleNamespace(live={"shared": FakeRoom("shared", "p1")})
        candidate = FakeCandidate("shared", "p2")
        rows, diag = hardening.filter_cross_page_ambiguity(manager, [candidate], {"relatedPages": []})
        self.assertEqual(rows, [])
        self.assertTrue(candidate.closed)
        self.assertEqual(diag["crossPageWorkerAmbiguities"][0]["pageTargetIds"], ["p1", "p2"])

    def test_mid_capture_finalizes_only_affected_room(self):
        calls = []

        class M:
            def __init__(self):
                self.live = {
                    "w1": FakeRoom("w1", "p1"),
                    "w2": FakeRoom("w2", "p3"),
                }

            def _finalize_target(self, target_id, reason, try_remote):
                calls.append((target_id, reason, try_remote))
                self.live.pop(target_id, None)

        topology = {
            "crossPageWorkerAmbiguities": [
                {
                    "status": hardening.CROSS_PAGE_AMBIGUITY,
                    "workerTargetId": "w1",
                    "pageTargetIds": ["p1", "p2"],
                }
            ]
        }
        manager = M()
        finalized = hardening.finalize_cross_page_ambiguous_live(manager, topology)
        self.assertEqual(finalized, ["w1"])
        self.assertEqual(calls, [("w1", hardening.CROSS_PAGE_AMBIGUITY, False)])
        self.assertIn("w2", manager.live)


class DiscoveryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_window = discovery.AUTOATTACH_WINDOW_SECONDS
        discovery.AUTOATTACH_WINDOW_SECONDS = 0.01
        discovery.install(recorder)
        hardening.install(recorder, discovery)

    @classmethod
    def tearDownClass(cls):
        discovery.AUTOATTACH_WINDOW_SECONDS = cls.old_window

    def test_shared_worker_under_two_pages_fails_closed(self):
        events = {
            "p1": [attached("p1", worker("shared", worker_type="shared_worker"))],
            "p2": [attached("p2", worker("shared", worker_type="shared_worker"))],
        }
        manager = Manager(Client(state={"shared": {"identity": identity()}}, events_by_page=events))
        rows, diag = discovery.discover_candidates(manager, [page("p1"), page("p2")])
        self.assertEqual(rows, [])
        self.assertEqual(diag["crossPageAmbiguityCount"], 1)
        self.assertEqual(diag["crossPageWorkerAmbiguities"][0]["status"], hardening.CROSS_PAGE_AMBIGUITY)

    def test_two_pages_two_distinct_exact_workers_remain_independent(self):
        events = {
            "p1": [attached("p1", worker("w1"))],
            "p2": [attached("p2", worker("w2"))],
        }
        manager = Manager(Client(state={"w1": {"identity": identity()}, "w2": {"identity": identity()}}, events_by_page=events))
        rows, diag = discovery.discover_candidates(manager, [page("p1"), page("p2")])
        self.assertEqual({row.target["targetId"] for row in rows}, {"w1", "w2"})
        self.assertEqual(diag["crossPageAmbiguityCount"], 0)
        for row in rows:
            row.close()

    def test_existing_blob_and_data_exact_workers_use_runtime_identity(self):
        for url in ("blob:https://example/worker", "data:text/javascript;base64,Zm9v"):
            with self.subTest(url=url):
                client = Client(state={"w1": {"identity": identity()}})
                manager = Manager(client)
                rows, _ = discovery.discover_candidates(manager, [page("p1"), worker("w1", url=url, parentId="p1")])
                self.assertEqual(len(rows), 1)
                rows[0].close()

    def test_wrong_identity_blob_worker_rejected(self):
        client = Client(state={"w1": {"identity": identity(False, "0" * 64)}})
        manager = Manager(client)
        rows, diag = discovery.discover_candidates(manager, [page("p1"), worker("w1", url="blob:https://example/x", parentId="p1")])
        self.assertEqual(rows, [])
        self.assertTrue(any(row.get("status") == "wrong-identity" for row in diag["directWorkers"]))

    def test_misleading_opener_does_not_choose_page(self):
        client = Client(state={"w1": {"identity": identity()}})
        manager = Manager(client)
        rows, diag = discovery.discover_candidates(
            manager,
            [page("p1"), page("p2"), worker("w1", openerId="p1")],
        )
        self.assertEqual(rows, [])
        self.assertTrue(any(row.get("status") == "page-association-ambiguous" for row in diag["directWorkers"]))

    def test_unique_page_direct_fallback_and_parentid_override(self):
        client = Client(state={"w1": {"identity": identity()}})
        manager = Manager(client)
        rows, _ = discovery.discover_candidates(manager, [page("p1"), worker("w1", openerId="wrong")])
        self.assertEqual(rows[0].page["targetId"], "p1")
        rows[0].close()

        client2 = Client(state={"w2": {"identity": identity()}})
        manager2 = Manager(client2)
        rows2, _ = discovery.discover_candidates(
            manager2,
            [page("p1"), page("p2"), worker("w2", parentId="p2", openerId="p1")],
        )
        self.assertEqual(rows2[0].page["targetId"], "p2")
        rows2[0].close()

    def test_safety_and_world_gate_remain_authoritative(self):
        self.assertEqual(recorder.WORLD_SHA256, WORLD)
        self.assertIn("Target.setAutoAttach", recorder.READ_ONLY_METHODS)
        self.assertFalse(any(str(method).startswith("Input.") for method in recorder.READ_ONLY_METHODS))
        self.assertNotIn("Runtime.callFunctionOn", recorder.READ_ONLY_METHODS)
        self.assertNotIn("Page.addScriptToEvaluateOnNewDocument", recorder.READ_ONLY_METHODS)
        self.assertTrue(getattr(recorder, "_WOF052L_HARDENING_V2_INSTALLED", False))


class OwnerChineseUxTests(unittest.TestCase):
    def test_normal_owner_runtime_methods_do_not_contain_old_english_statuses(self):
        import fleet_recorder

        methods = [
            recorder.RecorderManager.ensure_browser,
            recorder.RecorderManager._finalize_target,
            recorder.RecorderManager.shutdown,
            fleet_recorder.FleetRecorderManager.ensure_browser,
            fleet_recorder.FleetRecorderManager.run_managed,
            fleet_recorder.FleetSupervisor.run,
        ]
        source = "\n".join(inspect.getsource(method) for method in methods)
        for old in (
            "WAITING ",
            "other rooms continue",
            "CDP connect failed safely",
            "Browser OK",
            "WOF-052L fleet recorder #",
            "Stopping fleet recorder",
            "Final merged JSON:",
            " finalized (",
        ):
            self.assertNotIn(old, source)
        for marker in ("等待本机", "浏览器已连接", "技术详情", "已启动", "已完成", "最终合并 JSON"):
            self.assertIn(marker, source)

    def test_endpoint_wait_is_chinese_and_technical_detail_is_second_layer(self):
        import argparse
        import tempfile
        from pathlib import Path

        args = argparse.Namespace(
            cdp_host="192.0.2.1",
            cdp_port=9223,
            no_launch_browser=True,
            browser="auto",
            game_url=None,
        )
        with tempfile.TemporaryDirectory() as temp:
            manager = recorder.RecorderManager(Path(temp), args)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertFalse(manager.ensure_browser())
            text = out.getvalue()
        self.assertIn("已安全拒绝连接", text)
        self.assertIn("技术详情：remote-cdp-host-rejected", text)
        self.assertNotIn("WAITING for Chrome/Edge", text)


if __name__ == "__main__":
    unittest.main()
