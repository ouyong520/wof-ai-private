from __future__ import annotations

import contextlib
import io
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDER = ROOT / "WOF052L_RECORDER"
sys.path.insert(0, str(RECORDER))

import discovery_v2_sync as discovery
import hardening_v2 as hardening

WORLD = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"


class IdentitySession:
    def __init__(self, payload, *, session_id="", client=None):
        self.payload = payload
        self.session_id = session_id
        self.client = client
        self.identity_calls = 0

    def request(self, method, params=None, timeout=None):
        return {}

    def evaluate(self, expression, await_promise=False, timeout=8.0):
        if expression == "LIGHT":
            return {"moduleOk": True, "heapOk": True, "ramWithinHeap": True}
        if expression == "IDENTITY":
            self.identity_calls += 1
            return self.payload
        raise AssertionError(expression)


def identity_manager():
    return types.SimpleNamespace(
        _wof052l_recorder_module=types.SimpleNamespace(WORLD_SHA256=WORLD, LIGHT_PROBE="LIGHT"),
        _wof052l_identity_probe_js="IDENTITY",
        _wof052l_identity_cache={},
    )


class Candidate:
    def __init__(self, worker_id, page_id):
        self.target = {"targetId": worker_id}
        self.page = {"targetId": page_id}
        self.closed = False

    def close(self):
        self.closed = True


class Room:
    def __init__(self, worker_id, page_id, path="page-autoattach"):
        self.target = {"targetId": worker_id, "discoveryPath": path}
        self.page = {"targetId": page_id}


def topology(*pairs):
    return {
        "relatedPages": [
            {
                "page": {"targetId": page},
                "path": "page-autoattach",
                "probedWorkers": [{"target": {"targetId": worker}, "status": "supported"}],
                "supportedObserved": 1,
                "supportedCount": 1,
                "ambiguous": False,
            }
            for worker, page in pairs
        ],
        "directWorkers": [],
        "crossPageWorkerAmbiguities": [],
        "candidateCount": len(pairs),
    }


def manager_class(live_pairs):
    pages = sorted({page for _, page in live_pairs})

    class Manager:
        def __init__(self):
            self.client = types.SimpleNamespace(
                closed=False,
                targets=lambda: [
                    {"targetId": page, "type": "page", "url": f"https://example.invalid/{page}"}
                    for page in pages
                ],
            )
            self.live = {worker: Room(worker, page) for worker, page in live_pairs}
            self._last_discovery = 0.0
            self._wof052l_last_live_topology_audit = 95.0
            self._wof052l_last_topology = {}
            self._wof052l_last_discovery_message = None
            self.timeline = []
            self.evidence_polls = 0

        def _browser_lost(self):
            self.timeline.append(("browser-lost",))

        def _finalize_target(self, target_id, reason, try_remote):
            self.timeline.append(("finalize", target_id, reason))
            self.live.pop(target_id, None)

        def poll_rooms(self, now):
            self.timeline.append(("poll", now, tuple(sorted(self.live))))
            if self.live:
                self.evidence_polls += 1

    return Manager


def install_guard(Manager, original_discover_candidates, announcements=None):
    announcements = announcements if announcements is not None else []

    def attach_candidate(manager, candidate, now, topo):
        candidate.close()

    fake_discovery = types.SimpleNamespace(
        discover_candidates=original_discover_candidates,
        _announce=lambda manager, message: announcements.append(message),
        _discovery_status=lambda topo: "无可准入候选；继续安全等待。",
        _attach_candidate=attach_candidate,
        _sync_base_overrides=lambda: None,
    )
    fake_recorder = types.SimpleNamespace(RecorderManager=Manager, DISCOVERY_INTERVAL=1.0)
    hardening._install_discovery_hardening(fake_recorder, fake_discovery)
    return fake_discovery, announcements


class FreshIndependentQA(unittest.TestCase):
    def test_01_live_live_shared_worker_inside_old_interval_finalizes_before_poll(self):
        Manager = manager_class((("shared", "p1"), ("other", "p2")))
        skips = []

        def scan(manager, targets, *, skip_page_ids=None):
            skipped = set(skip_page_ids or set())
            skips.append(skipped)
            if "p2" not in skipped:
                return [Candidate("shared", "p2")], topology()
            return [], topology()

        install_guard(Manager, scan)
        m = Manager()
        m.discover(100.0)
        m.poll_rooms(100.0)
        self.assertEqual(skips[0], set())
        self.assertEqual(m.live, {})
        poll_i = next(i for i, row in enumerate(m.timeline) if row[0] == "poll")
        finalize_is = [i for i, row in enumerate(m.timeline) if row[0] == "finalize"]
        self.assertTrue(finalize_is and max(finalize_is) < poll_i)
        self.assertEqual(m.evidence_polls, 0)

    def test_02_poll_between_proof_epochs_cannot_collect(self):
        Manager = manager_class((("w1", "p1"),))

        def scan(manager, targets, *, skip_page_ids=None):
            return [Candidate("w1", "p1")], topology(("w1", "p1"))

        install_guard(Manager, scan)
        m = Manager()
        m.discover(100.0)
        m.poll_rooms(100.0)
        self.assertEqual(m.evidence_polls, 1)
        m.discover(100.2)
        m.poll_rooms(100.2)
        self.assertEqual(m.evidence_polls, 1)
        self.assertEqual(len([x for x in m.timeline if x[0] == "poll"]), 1)

    def test_03_discovery_exception_fails_closed_without_later_buffered_evidence(self):
        Manager = manager_class((("w1", "p1"),))
        announcements = []

        def scan(manager, targets, *, skip_page_ids=None):
            raise RuntimeError("synthetic discovery failure")

        install_guard(Manager, scan, announcements)
        m = Manager()
        m.discover(100.0)
        m.poll_rooms(100.0)
        self.assertEqual(m.live, {})
        self.assertEqual(m.evidence_polls, 0)
        self.assertIsNone(getattr(m, "_wof052l_live_topology_reproof_token", None))
        self.assertTrue(any("实时拓扑复核失败" in x for x in announcements))

    def test_04_missing_exact_current_pair_finalizes_fail_closed(self):
        Manager = manager_class((("w1", "p1"),))

        def scan(manager, targets, *, skip_page_ids=None):
            return [], {
                "relatedPages": [{
                    "page": {"targetId": "p1"},
                    "probedWorkers": [{"target": {"targetId": "w1"}, "status": "probe-error"}],
                    "supportedObserved": 0,
                    "supportedCount": 0,
                    "ambiguous": False,
                }],
                "directWorkers": [],
                "candidateCount": 0,
            }

        install_guard(Manager, scan)
        m = Manager()
        m.discover(100.0)
        m.poll_rooms(100.0)
        self.assertEqual(m.live, {})
        self.assertIn(("finalize", "w1", hardening.LIVE_TOPOLOGY_REPROOF_FAILED), m.timeline)
        self.assertEqual(m.evidence_polls, 0)

    def test_05_reused_target_new_runtime_wrong_world_fresh_probes_and_rejects(self):
        m = identity_manager()
        target = {"targetId": "same-id", "type": "worker"}
        first = IdentitySession({"ok": True, "identity": {"ok": True, "sha256": WORLD}}, session_id="s1", client=object())
        wrong = IdentitySession({"ok": False, "identity": {"ok": False, "sha256": "0" * 64}}, session_id="s2", client=object())
        self.assertEqual(discovery._probe_session(m, first, target)[2], "supported")
        self.assertEqual(discovery._probe_session(m, wrong, target)[2], "wrong-identity")
        self.assertEqual((first.identity_calls, wrong.identity_calls), (1, 1))

    def test_06_reused_target_correct_recreated_runtime_must_fresh_probe(self):
        m = identity_manager()
        target = {"targetId": "same-id", "type": "worker"}
        a = IdentitySession({"ok": True, "identity": {"ok": True, "sha256": WORLD}}, session_id="s1", client=object())
        b = IdentitySession({"ok": True, "identity": {"ok": True, "sha256": WORLD}}, session_id="s2", client=object())
        self.assertEqual(discovery._probe_session(m, a, target)[2], "supported")
        self.assertEqual(discovery._probe_session(m, b, target)[2], "supported")
        self.assertEqual((a.identity_calls, b.identity_calls), (1, 1))

    def test_07_same_live_cdp_session_reuses_only_its_own_authority(self):
        m = identity_manager()
        target = {"targetId": "stable", "type": "worker"}
        client = object()
        s = IdentitySession({"ok": True, "identity": {"ok": True, "sha256": WORLD}}, session_id="session-stable", client=client)
        self.assertEqual(discovery._probe_session(m, s, target)[2], "supported")
        self.assertEqual(discovery._probe_session(m, s, target)[2], "supported")
        self.assertEqual(s.identity_calls, 1)
        replacement = IdentitySession({"ok": False, "identity": {"ok": False, "sha256": "f" * 64}}, session_id="session-new", client=client)
        self.assertEqual(discovery._probe_session(m, replacement, target)[2], "wrong-identity")
        self.assertEqual(replacement.identity_calls, 1)

    def test_08_two_distinct_pages_workers_stay_independent_and_admissible(self):
        Manager = manager_class((("w1", "p1"), ("w2", "p2")))

        def scan(manager, targets, *, skip_page_ids=None):
            return [Candidate("w1", "p1"), Candidate("w2", "p2")], topology(("w1", "p1"), ("w2", "p2"))

        install_guard(Manager, scan)
        m = Manager()
        m.discover(100.0)
        m.poll_rooms(100.0)
        self.assertEqual(set(m.live), {"w1", "w2"})
        self.assertEqual(m.evidence_polls, 1)
        self.assertFalse(any(row[0] == "finalize" for row in m.timeline))

    def test_09_explicit_endpoint_cross_port_drift_has_no_fallover(self):
        requested = []
        candidate_ports_calls = []
        rec = types.SimpleNamespace()
        rec.launch_debug_browser = lambda *a, **k: None
        rec.http_json = lambda url: requested.append(url) or {"Browser": "Chromium", "webSocketDebuggerUrl": "ws://127.0.0.1:9555/devtools/browser/x"}
        rec.candidate_ports = lambda arg: candidate_ports_calls.append(arg) or [9555, 9666]
        rec.BrowserEndpoint = lambda host, port, label, websocket_url: types.SimpleNamespace(host=host, port=port, label=label, websocket_url=websocket_url)
        hardening._install_endpoint_guard(rec)
        self.assertIsNone(rec.find_endpoint("127.0.0.1", 9444))
        self.assertEqual(requested, ["http://127.0.0.1:9444/json/version"])
        self.assertEqual(candidate_ports_calls, [])
        self.assertEqual(rec._WOF052L_LAST_ENDPOINT_REJECTION["reason"], "returned-websocket-cross-port")
        self.assertEqual(
            {k: rec._WOF052L_LAST_ENDPOINT_REJECTION[k] for k in ("readOnly", "ramWrites", "inputInjection")},
            {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        )

    def test_10_ambiguity_finalization_preserves_accounting_autosave_and_unrelated_room(self):
        class M: pass
        rec = types.SimpleNamespace(RecorderManager=M)
        hardening._install_recorder_owner_ux(rec)
        m = M()
        m.output_dir = Path("/tmp/wof-accounting")
        m.completed = []
        m.room_files = []
        m.live = {}

        class Capture:
            def __init__(self, room_id, worker, page):
                self.room_id = room_id
                self.target = {"targetId": worker}
                self.page = {"targetId": page}
                self.final_file = m.output_dir / f"{room_id}.json"
                self.calls = 0
            def finalize(self, reason, try_remote):
                self.calls += 1
                return {"startedAt": "a", "finalizedAt": "b", "diagnostics": {"t18": {"candidateCycles": 3}}}

        bad = Capture("bad-room", "shared", "p1")
        good = Capture("good-room", "good", "p9")
        m.live = {"shared": bad, "good": good}
        topo = {"crossPageWorkerAmbiguities": [{"status": hardening.CROSS_PAGE_AMBIGUITY, "workerTargetId": "shared", "pageTargetIds": ["p1", "p2"]}]}
        with contextlib.redirect_stdout(io.StringIO()):
            finalized = hardening.finalize_cross_page_ambiguous_live(m, topo)
        self.assertEqual(finalized, ["shared"])
        self.assertEqual(set(m.live), {"good"})
        self.assertEqual(bad.calls, 1)
        self.assertEqual(good.calls, 0)
        self.assertEqual(len(m.completed), 1)
        self.assertEqual(m.room_files[0]["roomId"], "bad-room")
        self.assertEqual(m.room_files[0]["file"], "bad-room.json")

    def test_11_chinese_owner_failure_text_and_exact_world_sha_authority(self):
        Manager = manager_class((("w1", "p1"),))
        announcements = []
        def scan(manager, targets, *, skip_page_ids=None):
            return [], topology()
        install_guard(Manager, scan, announcements)
        m = Manager()
        m.discover(100.0)
        joined = "\n".join(announcements)
        self.assertIn("实时拓扑无法重新证明唯一 Worker↔页面归属", joined)
        self.assertIn("相关房间已先完成并停止继续收证据", joined)
        self.assertIn(hardening.LIVE_TOPOLOGY_REPROOF_FAILED, joined)
        recorder = types.SimpleNamespace(WORLD_SHA256=WORLD)
        self.assertTrue(discovery._base._identity_ok(recorder, {"ok": True, "identity": {"sha256": WORLD}}))
        self.assertFalse(discovery._base._identity_ok(recorder, {"ok": True, "identity": {"sha256": "0" * 64}}))

    def test_12_safety_contract_and_no_new_dangerous_wrapper_capabilities(self):
        rejection = types.SimpleNamespace()
        hardening._endpoint_rejection(rejection, "127.0.0.1", 9444, "synthetic")
        self.assertEqual(rejection._WOF052L_LAST_ENDPOINT_REJECTION["readOnly"], True)
        self.assertEqual(rejection._WOF052L_LAST_ENDPOINT_REJECTION["ramWrites"], 0)
        self.assertEqual(rejection._WOF052L_LAST_ENDPOINT_REJECTION["inputInjection"], False)

        source = "\n".join((RECORDER / name).read_text(encoding="utf-8") for name in (
            "discovery_v2_sync.py", "hardening_v2.py", "hardening_v2_base.py"
        ))
        forbidden = (
            "URL.createObjectURL(",
            "new Blob(",
            "Input.dispatchKeyEvent",
            "Input.dispatchMouseEvent",
            "Input.insertText",
            "window.Worker =",
            "window.Worker=",
        )
        self.assertFalse(any(token in source for token in forbidden))
        self.assertIn("只读模式开启 / 游戏内存写入 0 / 无游戏输入注入 / 不替换 window.Worker", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
