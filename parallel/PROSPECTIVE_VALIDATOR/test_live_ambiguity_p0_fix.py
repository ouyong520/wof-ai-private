from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

import live_validator_v2 as v2

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "live_unique_to_shared_worker.json"


class FakeSession:
    def __init__(self) -> None:
        self.drains = 0
        self.stop_calls = 0
        self.closed = False

    def evaluate(self, script: str, timeout: float = 0.0):
        if ".drain()" in script:
            self.drains += 1
            return {"ok": True}
        if ".stop()" in script:
            self.stop_calls += 1
            return {"ok": True, "events": [{"forbidden": "must-not-ingest"}]}
        return {"ok": True}

    def close(self) -> None:
        self.closed = True


class FakeClient:
    def __init__(self, targets):
        self._targets = list(targets)

    def targets(self):
        return list(self._targets)


class FakeEndpoint:
    def __init__(self, rooms, targets, last_discovery: float) -> None:
        self.host = "127.0.0.1"
        self.port = 9222
        self.label = "fixture-endpoint"
        self.rooms = rooms
        self.client = FakeClient(targets)
        self.last_discovery = last_discovery

    def connect(self) -> bool:
        return True

    def close_client(self) -> None:
        return None


class FakeCandidate:
    def __init__(self, page_id: str, worker_id: str) -> None:
        self.page = {"targetId": page_id}
        self.target = {"targetId": worker_id}
        self.closed = False

    def close(self) -> None:
        self.closed = True


def make_room(page_id: str, worker_id: str):
    return SimpleNamespace(
        page_id=page_id,
        discovery_path="page-autoattach",
        room_id=f"room-{worker_id}",
        target_id=worker_id,
        started_at="fixture",
        pending=[],
        session=FakeSession(),
    )


class LiveAmbiguityP0FixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.saved = {
            "discover_candidates": v2.discover_candidates,
            "ambiguous_page_ids": v2.ambiguous_page_ids,
            "room_liveness_reason": v2.room_liveness_reason,
            "discovery_status_zh": v2.discovery_status_zh,
        }
        v2.room_liveness_reason = lambda **_kwargs: None
        v2.discovery_status_zh = lambda _diag: "fixture-status"

    def tearDown(self) -> None:
        for name, value in self.saved.items():
            setattr(v2, name, value)

    def validator(self):
        validator = v2.LiveValidatorV2.__new__(v2.LiveValidatorV2)
        validator._last_discovery_message = {}
        validator.traces = []
        validator.ingested = []
        validator.finalized = []
        validator._announce = lambda _endpoint, _message: None
        validator.attach_candidate = lambda _endpoint, _candidate: None
        validator.ingest = lambda room, _payload: validator.ingested.append(room.room_id)

        def finalize(endpoint, tid, reason, remote):
            room = endpoint.rooms.pop(tid, None)
            if room is not None:
                validator.finalized.append((tid, reason, remote))
                room.session.close()

        validator.finalize_room = finalize
        return validator

    def test_unique_to_shared_worker_finalizes_before_any_drain(self) -> None:
        initial = self.fixture["initial"]
        transition = self.fixture["transition"]
        poll = self.fixture["adversarialPoll"]
        room = make_room(
            initial["connectedRoom"]["pageTargetId"],
            initial["connectedRoom"]["workerTargetId"],
        )
        endpoint = FakeEndpoint(
            {room.target_id: room},
            [
                {"targetId": room.page_id, "type": "page"},
                {"targetId": transition["newPageTargetId"], "type": "page"},
                {"targetId": room.target_id, "type": "shared_worker"},
            ],
            float(initial["lastTopologyAudit"]),
        )

        def discover(_client, _targets, **kwargs):
            self.assertEqual(kwargs["skip_page_ids"], set(), "live pages must never be skipped before evidence ingest")
            return [], {"ambiguousPageIds": [room.page_id, transition["newPageTargetId"]]}

        v2.discover_candidates = discover
        v2.ambiguous_page_ids = lambda diag: set(diag.get("ambiguousPageIds", []))

        validator = self.validator()
        validator.discover_and_poll(endpoint, float(poll["t"]))

        self.assertEqual(room.session.drains, 0)
        self.assertEqual(validator.ingested, [])
        self.assertEqual(
            validator.finalized,
            [(room.target_id, "worker-association-ambiguous", False)],
        )
        self.assertEqual(v2.AUDIT_LIVE_TOPOLOGY_INTERVAL, 0.0)

    def test_two_distinct_workers_remain_independent_and_drain_after_positive_reproof(self) -> None:
        room_a = make_room("page-a", "worker-a")
        room_b = make_room("page-b", "worker-b")
        endpoint = FakeEndpoint(
            {"worker-a": room_a, "worker-b": room_b},
            [
                {"targetId": "page-a", "type": "page"},
                {"targetId": "page-b", "type": "page"},
                {"targetId": "worker-a", "type": "worker"},
                {"targetId": "worker-b", "type": "worker"},
            ],
            100.0,
        )
        v2.discover_candidates = lambda _client, _targets, **kwargs: (
            [FakeCandidate("page-a", "worker-a"), FakeCandidate("page-b", "worker-b")],
            {},
        )
        v2.ambiguous_page_ids = lambda _diag: set()

        validator = self.validator()
        validator.discover_and_poll(endpoint, 105.0)

        self.assertEqual(validator.finalized, [])
        self.assertEqual(room_a.session.drains, 1)
        self.assertEqual(room_b.session.drains, 1)
        self.assertEqual(set(validator.ingested), {"room-worker-a", "room-worker-b"})

    def test_failed_topology_reproof_censors_instead_of_deferring_buffered_evidence(self) -> None:
        room = make_room("page-a", "worker-a")
        endpoint = FakeEndpoint(
            {"worker-a": room},
            [{"targetId": "page-a", "type": "page"}, {"targetId": "worker-a", "type": "worker"}],
            100.0,
        )

        def fail_discovery(*_args, **_kwargs):
            raise RuntimeError("fixture topology scan failure")

        v2.discover_candidates = fail_discovery
        v2.ambiguous_page_ids = lambda _diag: set()

        validator = self.validator()
        validator.discover_and_poll(endpoint, 105.0)

        self.assertEqual(room.session.drains, 0)
        self.assertEqual(validator.ingested, [])
        self.assertEqual(
            validator.finalized,
            [("worker-a", "worker-association-unverified", False)],
        )

    def test_remote_cleanup_payload_is_never_ingested_without_a_fresh_audit(self) -> None:
        room = make_room("page-a", "worker-a")
        endpoint = SimpleNamespace(rooms={"worker-a": room})
        validator = v2.LiveValidatorV2.__new__(v2.LiveValidatorV2)
        validator.traces = []
        validator.ingested = []
        validator.ingest = lambda _room, payload: validator.ingested.append(payload)

        v2.LiveValidatorV2.finalize_room(
            validator,
            endpoint,
            "worker-a",
            "validator-stopped",
            remote=True,
        )

        self.assertEqual(room.session.stop_calls, 1)
        self.assertEqual(validator.ingested, [])
        self.assertTrue(room.session.closed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
