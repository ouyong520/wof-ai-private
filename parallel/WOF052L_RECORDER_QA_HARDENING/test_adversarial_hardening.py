from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

RECORDER_DIR = Path(__file__).resolve().parents[1] / "WOF052L_RECORDER"
if str(RECORDER_DIR) not in sys.path:
    sys.path.insert(0, str(RECORDER_DIR))

import discovery_v2_sync as discovery  # noqa: E402
import hardening_v2 as hardening  # noqa: E402


WORLD = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"


class IdentitySession:
    def __init__(self, identity_payload):
        self.identity_payload = identity_payload
        self.identity_calls = 0

    def request(self, method, params=None, timeout=None):
        return {}

    def evaluate(self, expression, await_promise=False, timeout=8.0):
        if expression == "LIGHT":
            return {"moduleOk": True, "heapOk": True, "ramWithinHeap": True}
        if expression == "IDENTITY":
            self.identity_calls += 1
            return self.identity_payload
        raise AssertionError(f"unexpected expression: {expression}")


class StaleIdentityAuthorityAdversarialTests(unittest.TestCase):
    def test_recreated_worker_with_reused_target_id_must_not_inherit_cached_world_authority(self):
        manager = types.SimpleNamespace(
            _wof052l_recorder_module=types.SimpleNamespace(
                WORLD_SHA256=WORLD,
                LIGHT_PROBE="LIGHT",
            ),
            _wof052l_identity_probe_js="IDENTITY",
            _wof052l_identity_cache={},
        )
        target = {"targetId": "worker-reused", "type": "worker", "url": "blob:https://example/worker"}

        first = IdentitySession(
            {"ok": True, "identity": {"ok": True, "sha256": WORLD}, "reason": "ok"}
        )
        _, _, first_status = discovery._probe_session(manager, first, target)
        self.assertEqual(first_status, "supported")
        self.assertEqual(first.identity_calls, 1)
        self.assertIn("worker-reused", manager._wof052l_identity_cache)

        # Adversarial recreation: same targetId, new runtime identity. A stale cache entry
        # must never authorize the replacement Worker without a fresh identity probe.
        replacement = IdentitySession(
            {"ok": False, "identity": {"ok": False, "sha256": "0" * 64}, "reason": "wrong-world"}
        )
        _, _, replacement_status = discovery._probe_session(manager, replacement, target)

        self.assertEqual(
            replacement.identity_calls,
            1,
            "recreated Worker must be identity-probed again instead of inheriting stale authority",
        )
        self.assertEqual(
            replacement_status,
            "wrong-identity",
            "recreated wrong-World Worker must fail closed",
        )


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


class FakeClient:
    closed = False

    def targets(self):
        return [
            {"targetId": "p1", "type": "page", "url": "https://example/p1"},
            {"targetId": "p2", "type": "page", "url": "https://example/p2"},
        ]


class LiveTransitionManager:
    def __init__(self):
        self.client = FakeClient()
        self._last_discovery = 0.0
        self._wof052l_last_live_topology_audit = 95.0
        self._wof052l_last_topology = {}
        self._wof052l_last_discovery_message = None
        self.live = {
            "shared": FakeRoom("shared", "p1"),
            "other": FakeRoom("other", "p2"),
        }
        self.events = []

    def _browser_lost(self):
        raise AssertionError("browser should remain connected in this fixture")

    def _finalize_target(self, target_id, reason, try_remote):
        self.events.append(("finalize", target_id, reason, try_remote))
        self.live.pop(target_id, None)

    def poll_rooms(self, now):
        # This models the real Recorder loop order: discover(now); poll_rooms(now).
        self.events.append(("poll", tuple(sorted(self.live))))


class MidCaptureSharedWorkerTransitionAdversarialTests(unittest.TestCase):
    def test_two_live_pages_shared_worker_transition_must_finalize_before_evidence_polling(self):
        seen_skips = []

        def original_discover_candidates(manager, targets, *, skip_page_ids=None):
            skipped = set(skip_page_ids or set())
            seen_skips.append(skipped)

            # The topology drift exists on already-live p2: it is now also related to
            # exact Worker targetId 'shared', which is already authoritative for p1.
            # If p2 is scanned, hardening.filter_cross_page_ambiguity can see the
            # live relation shared->p1 plus candidate shared->p2 and fail closed.
            if "p2" not in skipped:
                return [FakeCandidate("shared", "p2")], {
                    "relatedPages": [],
                    "directWorkers": [],
                }
            return [], {"relatedPages": [], "directWorkers": []}

        fake_discovery = types.SimpleNamespace(
            discover_candidates=original_discover_candidates,
            _worker_compatible=None,
            _page_for_direct=None,
            _announce=lambda manager, message: None,
            _discovery_status=lambda topology: "no candidate",
            _attach_candidate=lambda manager, candidate, now, topology: (_ for _ in ()).throw(
                AssertionError("ambiguous candidate must never be admitted")
            ),
        )
        fake_recorder = types.SimpleNamespace(
            RecorderManager=LiveTransitionManager,
            DISCOVERY_INTERVAL=1.0,
        )

        hardening._install_discovery_hardening(fake_recorder, fake_discovery)
        manager = LiveTransitionManager()

        # Only five seconds since the last live-page audit. Current hardening uses a
        # 10-second audit cadence here; the safety requirement is stronger: an
        # observed mid-capture cross-page Worker transition must be finalized before
        # the next evidence poll, not after a later audit window.
        manager.discover(100.0)
        manager.poll_rooms(100.0)

        self.assertTrue(seen_skips, "fixture must exercise discovery")
        first_poll = next((event for event in manager.events if event[0] == "poll"), None)
        finalized_before_poll = [event for event in manager.events if event[0] == "finalize"]

        self.assertTrue(
            finalized_before_poll,
            "shared-Worker transition between live pages must finalize affected rooms before evidence polling",
        )
        self.assertEqual(
            first_poll,
            ("poll", ()),
            "no affected live room may remain eligible for evidence polling after ambiguity appears",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
