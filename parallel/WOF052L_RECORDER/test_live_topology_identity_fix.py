from __future__ import annotations

import types
import unittest

import discovery_v2_sync as discovery
import hardening_v2 as hardening


WORLD = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"


class IdentitySession:
    def __init__(self, identity_payload, *, session_id="", client=None):
        self.identity_payload = identity_payload
        self.identity_calls = 0
        self.session_id = session_id
        self.client = client

    def request(self, method, params=None, timeout=None):
        return {}

    def evaluate(self, expression, await_promise=False, timeout=8.0):
        if expression == "LIGHT":
            return {"moduleOk": True, "heapOk": True, "ramWithinHeap": True}
        if expression == "IDENTITY":
            self.identity_calls += 1
            return self.identity_payload
        raise AssertionError(f"unexpected expression: {expression}")


def identity_manager():
    return types.SimpleNamespace(
        _wof052l_recorder_module=types.SimpleNamespace(
            WORLD_SHA256=WORLD,
            LIGHT_PROBE="LIGHT",
        ),
        _wof052l_identity_probe_js="IDENTITY",
        _wof052l_identity_cache={},
    )


class IdentityLifecycleTests(unittest.TestCase):
    def test_reused_target_id_new_runtime_must_reprobe_and_reject_wrong_world(self):
        manager = identity_manager()
        target = {"targetId": "worker-reused", "type": "worker"}

        first = IdentitySession(
            {"ok": True, "identity": {"ok": True, "sha256": WORLD}, "reason": "ok"}
        )
        self.assertEqual(discovery._probe_session(manager, first, target)[2], "supported")
        self.assertEqual(first.identity_calls, 1)
        self.assertIn("worker-reused", manager._wof052l_identity_cache)

        replacement = IdentitySession(
            {
                "ok": False,
                "identity": {"ok": False, "sha256": "0" * 64},
                "reason": "wrong-world",
            }
        )
        self.assertEqual(discovery._probe_session(manager, replacement, target)[2], "wrong-identity")
        self.assertEqual(replacement.identity_calls, 1)

    def test_reused_target_id_correct_recreation_reproves_before_readmission(self):
        manager = identity_manager()
        target = {"targetId": "worker-reused", "type": "worker"}

        first = IdentitySession(
            {"ok": True, "identity": {"ok": True, "sha256": WORLD}, "reason": "ok"}
        )
        replacement = IdentitySession(
            {"ok": True, "identity": {"ok": True, "sha256": WORLD}, "reason": "ok"}
        )
        self.assertEqual(discovery._probe_session(manager, first, target)[2], "supported")
        self.assertEqual(discovery._probe_session(manager, replacement, target)[2], "supported")
        self.assertEqual(first.identity_calls, 1)
        self.assertEqual(replacement.identity_calls, 1)

    def test_same_cdp_session_may_reuse_its_own_identity_authority(self):
        manager = identity_manager()
        target = {"targetId": "worker-stable", "type": "worker"}
        client = object()
        session = IdentitySession(
            {"ok": True, "identity": {"ok": True, "sha256": WORLD}, "reason": "ok"},
            session_id="session-1",
            client=client,
        )
        self.assertEqual(discovery._probe_session(manager, session, target)[2], "supported")
        self.assertEqual(discovery._probe_session(manager, session, target)[2], "supported")
        self.assertEqual(session.identity_calls, 1)


class FakeCandidate:
    def __init__(self, worker_id: str, page_id: str):
        self.target = {"targetId": worker_id}
        self.page = {"targetId": page_id}
        self.closed = False

    def close(self):
        self.closed = True


class FakeRoom:
    def __init__(self, worker_id: str, page_id: str):
        self.target = {"targetId": worker_id, "discoveryPath": "page-autoattach"}
        self.page = {"targetId": page_id}


def related_topology(*pairs: tuple[str, str]) -> dict:
    return {
        "relatedPages": [
            {
                "page": {"targetId": page_id},
                "path": "page-autoattach",
                "probedWorkers": [
                    {"target": {"targetId": worker_id}, "status": "supported"}
                ],
                "supportedObserved": 1,
                "supportedCount": 1,
                "ambiguous": False,
            }
            for worker_id, page_id in pairs
        ],
        "directWorkers": [],
        "crossPageWorkerAmbiguities": [],
        "candidateCount": len(pairs),
    }


def make_manager_class(live_pairs: tuple[tuple[str, str], ...]):
    class Manager:
        def __init__(self):
            pages = sorted({page_id for _, page_id in live_pairs})
            self.client = types.SimpleNamespace(
                closed=False,
                targets=lambda: [
                    {"targetId": page_id, "type": "page", "url": f"https://example/{page_id}"}
                    for page_id in pages
                ],
            )
            self._last_discovery = 0.0
            self._wof052l_last_live_topology_audit = 95.0
            self._wof052l_last_topology = {}
            self._wof052l_last_discovery_message = None
            self.live = {
                worker_id: FakeRoom(worker_id, page_id)
                for worker_id, page_id in live_pairs
            }
            self.events = []

        def _browser_lost(self):
            raise AssertionError("browser should remain connected")

        def _finalize_target(self, target_id, reason, try_remote):
            self.events.append(("finalize", target_id, reason, try_remote))
            self.live.pop(target_id, None)

        def poll_rooms(self, now):
            self.events.append(("poll", tuple(sorted(self.live))))

    return Manager


def install_fake_hardening(manager_cls, discover_candidates):
    def attach_candidate(manager, candidate, now, topology):
        candidate.close()

    fake_discovery = types.SimpleNamespace(
        discover_candidates=discover_candidates,
        _worker_compatible=None,
        _page_for_direct=None,
        _announce=lambda manager, message: None,
        _discovery_status=lambda topology: "no candidate",
        _attach_candidate=attach_candidate,
    )
    fake_recorder = types.SimpleNamespace(
        RecorderManager=manager_cls,
        DISCOVERY_INTERVAL=1.0,
    )
    hardening._install_discovery_hardening(fake_recorder, fake_discovery)
    return fake_discovery


class LiveTopologyTests(unittest.TestCase):
    def test_live_live_shared_worker_transition_finalizes_before_next_poll(self):
        Manager = make_manager_class((("shared", "p1"), ("other", "p2")))
        seen_skips = []

        def discover_candidates(manager, targets, *, skip_page_ids=None):
            skipped = set(skip_page_ids or set())
            seen_skips.append(skipped)
            if "p2" not in skipped:
                return [FakeCandidate("shared", "p2")], {
                    "relatedPages": [],
                    "directWorkers": [],
                    "candidateCount": 1,
                }
            return [], {"relatedPages": [], "directWorkers": [], "candidateCount": 0}

        install_fake_hardening(Manager, discover_candidates)
        manager = Manager()
        manager.discover(100.0)
        manager.poll_rooms(100.0)

        self.assertTrue(seen_skips)
        self.assertEqual(seen_skips[0], set(), "already-live pages must be rescanned on a proof epoch")
        self.assertEqual(manager.live, {})
        self.assertEqual(
            next(event for event in manager.events if event[0] == "poll"),
            ("poll", ()),
        )

    def test_two_distinct_workers_remain_independent(self):
        Manager = make_manager_class((("w1", "p1"), ("w2", "p2")))

        def discover_candidates(manager, targets, *, skip_page_ids=None):
            pairs = (("w1", "p1"), ("w2", "p2"))
            return [FakeCandidate(*pair) for pair in pairs], related_topology(*pairs)

        install_fake_hardening(Manager, discover_candidates)
        manager = Manager()
        manager.discover(100.0)
        manager.poll_rooms(100.0)

        self.assertEqual(set(manager.live), {"w1", "w2"})
        self.assertFalse(any(event[0] == "finalize" for event in manager.events))
        self.assertIn(("poll", ("w1", "w2")), manager.events)

    def test_reproof_failure_finalizes_instead_of_deferring_evidence(self):
        Manager = make_manager_class((("w1", "p1"),))

        def discover_candidates(manager, targets, *, skip_page_ids=None):
            return [], {
                "relatedPages": [
                    {
                        "page": {"targetId": "p1"},
                        "probedWorkers": [
                            {"target": {"targetId": "w1"}, "status": "probe-error"}
                        ],
                        "supportedObserved": 0,
                        "supportedCount": 0,
                        "ambiguous": False,
                    }
                ],
                "directWorkers": [],
                "candidateCount": 0,
            }

        install_fake_hardening(Manager, discover_candidates)
        manager = Manager()
        manager.discover(100.0)
        manager.poll_rooms(100.0)

        self.assertEqual(manager.live, {})
        self.assertIn(
            ("finalize", "w1", hardening.LIVE_TOPOLOGY_REPROOF_FAILED, False),
            manager.events,
        )
        self.assertIn(("poll", ()), manager.events)

    def test_poll_between_discovery_epochs_collects_no_evidence(self):
        Manager = make_manager_class((("w1", "p1"),))

        def discover_candidates(manager, targets, *, skip_page_ids=None):
            pair = ("w1", "p1")
            return [FakeCandidate(*pair)], related_topology(pair)

        install_fake_hardening(Manager, discover_candidates)
        manager = Manager()
        manager.discover(100.0)
        manager.poll_rooms(100.0)
        manager.discover(100.2)
        manager.poll_rooms(100.2)

        polls = [event for event in manager.events if event[0] == "poll"]
        self.assertEqual(polls, [("poll", ("w1",))])


if __name__ == "__main__":
    unittest.main(verbosity=2)
