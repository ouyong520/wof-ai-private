from __future__ import annotations

import copy
import inspect
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SUT_DIR = HERE.parent / "PROSPECTIVE_VALIDATOR"
if str(SUT_DIR) not in sys.path:
    sys.path.insert(0, str(SUT_DIR))

import discovery_v2 as d  # noqa: E402
import discovery_v2_hardening as h  # noqa: E402
import live_validator_v2_hardened as _hardened_entry  # noqa: F401,E402
import live_validator_v2 as v2  # noqa: E402
import validator  # noqa: E402

TOPOLOGY_FIXTURE = HERE / "fixtures" / "topology_transition_adversarial.json"
CLEANUP_FIXTURE = HERE / "fixtures" / "cleanup_finalization_adversarial.json"
EXPECTED_WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"


class FakeSession:
    def __init__(self, name: str, timeline: list[str], stop_payload: dict | None = None) -> None:
        self.name = name
        self.timeline = timeline
        self.stop_payload = stop_payload or {"ok": True, "events": [], "status": {"pending": []}}
        self.drains = 0
        self.stop_calls = 0
        self.closed = False

    def evaluate(self, script: str, timeout: float = 0.0, **_kwargs):
        if ".drain()" in script:
            self.drains += 1
            self.timeline.append(f"drain:{self.name}")
            return {
                "ok": True,
                "events": [{"kind": "result", "marker": f"admitted:{self.name}"}],
                "status": {"pending": []},
            }
        if ".stop()" in script:
            self.stop_calls += 1
            self.timeline.append(f"stop:{self.name}")
            return copy.deepcopy(self.stop_payload)
        return {"ok": True}

    def close(self) -> None:
        self.closed = True
        self.timeline.append(f"close:{self.name}")


class FakeClient:
    def __init__(self, targets: list[dict]) -> None:
        self._targets = list(targets)

    def targets(self):
        return list(self._targets)


class FakeEndpoint:
    def __init__(self, rooms: dict, targets: list[dict], last_discovery: float) -> None:
        self.host = "127.0.0.1"
        self.port = 9222
        self.label = "fresh-qa-endpoint"
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


def make_room(page_id: str, worker_id: str, timeline: list[str], *, pending: list[dict] | None = None, stop_payload: dict | None = None):
    return SimpleNamespace(
        page_id=page_id,
        discovery_path="page-autoattach",
        room_id=f"room-{worker_id}",
        target_id=worker_id,
        started_at="2026-09-01T00:00:00Z",
        pending=list(pending or []),
        events=[],
        session=FakeSession(worker_id, timeline, stop_payload),
    )


def make_live_validator():
    sut = v2.LiveValidatorV2.__new__(v2.LiveValidatorV2)
    sut._last_discovery_message = {}
    sut.traces = []
    return sut


def gate_manifest() -> dict:
    return {
        "schema": validator.MANIFEST_SCHEMA,
        "promotion": "research-only",
        "id": "fresh-live-ambiguity-qa-gates",
        "rule": {"currentPredicates": [{"path": "state99", "op": "eq", "value": 1}]},
        "outcome": {"expectedAttacks": [100]},
        "windows": {"strictMaxMs": 100, "jitterMaxMs": 150, "lateMaxMs": 250, "hardMissMs": 500},
        "gate": {
            "minProspectiveSignals": 2,
            "minProspectiveRooms": 2,
            "requireZeroHardMiss": True,
            "minDistinctTargets": 2,
            "minObservedTypes": 2,
            "requireLifecycleReset": True,
        },
    }


def gate_trace(room: str, target: int, enemy_type: int, *, lifecycle: bool = False, attack: int = 100, evidence_class: str = "prospective") -> dict:
    return {
        "evidenceClass": evidence_class,
        "roomId": room,
        "activeAttack": attack,
        "leadMs": 50,
        "current": {"state99": 1, "target7E": target, "type": enemy_type},
        "targetStart7E": target,
        "type": enemy_type,
        "lifecycleReset": lifecycle,
    }


class FreshLiveAmbiguityQATests(unittest.TestCase):
    def setUp(self) -> None:
        self.topology = json.loads(TOPOLOGY_FIXTURE.read_text(encoding="utf-8"))
        self.cleanup = json.loads(CLEANUP_FIXTURE.read_text(encoding="utf-8"))
        self.saved_discover = v2.discover_candidates
        self.saved_ambiguous = v2.ambiguous_page_ids

    def tearDown(self) -> None:
        v2.discover_candidates = self.saved_discover
        v2.ambiguous_page_ids = self.saved_ambiguous

    def test_01_transition_between_cycles_has_no_admission_then_finalizes_before_drain(self) -> None:
        times = [row["t"] for row in self.topology["timeline"]]
        timeline: list[str] = []
        shared = make_room("page-live-a", "worker-shared", timeline)
        control = make_room("page-control", "worker-control", timeline)
        endpoint = FakeEndpoint(
            {shared.target_id: shared, control.target_id: control},
            [
                {"targetId": "page-live-a", "type": "page"},
                {"targetId": "page-live-b", "type": "page"},
                {"targetId": "page-control", "type": "page"},
                {"targetId": "worker-shared", "type": "shared_worker"},
                {"targetId": "worker-control", "type": "worker"},
            ],
            times[0],
        )
        sut = make_live_validator()

        # Topology already changed at times[1]. The intermediate poll must not
        # admit evidence because it is not a discovery/admission cycle.
        sut.discover_and_poll(endpoint, times[2])
        self.assertEqual((shared.session.drains, control.session.drains), (0, 0))
        self.assertEqual(sut.traces, [])

        def fresh_scan(_client, _targets, **kwargs):
            self.assertEqual(kwargs.get("skip_page_ids"), set())
            return h.harden_relation_graph(
                [
                    FakeCandidate("page-live-a", "worker-shared"),
                    FakeCandidate("page-live-b", "worker-shared"),
                    FakeCandidate("page-control", "worker-control"),
                ],
                {"candidateCount": 3, "evidenceClass": "discovery-only"},
            )

        v2.discover_candidates = fresh_scan
        v2.ambiguous_page_ids = h.ambiguous_page_ids
        sut.discover_and_poll(endpoint, times[3])

        self.assertNotIn("worker-shared", endpoint.rooms)
        self.assertIn("worker-control", endpoint.rooms)
        self.assertEqual(shared.session.drains, 0)
        self.assertEqual(control.session.drains, 1)
        self.assertEqual([row.get("marker") for row in sut.traces], ["admitted:worker-control"])
        self.assertLess(timeline.index("close:worker-shared"), timeline.index("drain:worker-control"))

    def test_02_unverified_exact_pair_and_scan_failure_both_fail_closed(self) -> None:
        for mode in ("missing-pair", "scan-failure"):
            timeline: list[str] = []
            room = make_room("page-a", "worker-a", timeline)
            endpoint = FakeEndpoint(
                {room.target_id: room},
                [{"targetId": "page-a", "type": "page"}, {"targetId": "worker-a", "type": "worker"}],
                10.0,
            )
            if mode == "missing-pair":
                v2.discover_candidates = lambda _client, _targets, **_kwargs: (
                    [],
                    {"pageCount": 1, "relatedPages": [], "directWorkers": [], "evidenceClass": "discovery-only"},
                )
                v2.ambiguous_page_ids = lambda _diag: set()
            else:
                def fail_scan(*_args, **_kwargs):
                    raise RuntimeError("fresh QA forced topology failure")
                v2.discover_candidates = fail_scan

            sut = make_live_validator()
            sut.discover_and_poll(endpoint, 11.01)
            self.assertEqual(room.session.drains, 0, mode)
            self.assertTrue(room.session.closed, mode)
            self.assertNotIn("worker-a", endpoint.rooms, mode)
            self.assertEqual(sut.traces, [], mode)

    def test_03_remote_cleanup_discards_stop_payload(self) -> None:
        timeline: list[str] = []
        pending = self.cleanup["precondition"]["lastFreshlyAdmittedPending"]
        stop_payload = self.cleanup["remoteStopPayload"]
        room = make_room("page-cleanup", "worker-cleanup", timeline, pending=[pending], stop_payload=stop_payload)
        endpoint = SimpleNamespace(rooms={room.target_id: room})
        sut = make_live_validator()

        v2.LiveValidatorV2.finalize_room(sut, endpoint, room.target_id, "validator-stopped", remote=True)

        self.assertEqual(room.session.stop_calls, 1)
        self.assertEqual(room.session.drains, 0)
        self.assertEqual(len(sut.traces), 1)
        self.assertEqual(sut.traces[0].get("marker"), "prevalidated-pending")
        self.assertTrue(sut.traces[0].get("censored"))
        serialized = json.dumps(sut.traces, sort_keys=True)
        self.assertNotIn("FORBIDDEN-STOP-EVENT", serialized)
        self.assertNotIn("FORBIDDEN-STOP-PENDING", serialized)

    def test_04_actual_control_flow_has_one_real_drain_call_after_all_reproof_guards(self) -> None:
        src = inspect.getsource(v2.LiveValidatorV2.discover_and_poll)
        drain_marker = "globalThis.__WOF_PROSPECTIVE_VALIDATOR.drain()"
        self.assertEqual(v2.AUDIT_LIVE_TOPOLOGY_INTERVAL, 0.0)
        self.assertIn("skip_page_ids=set()", src)
        self.assertEqual(src.count(drain_marker), 1)
        drain_i = src.index(drain_marker)
        self.assertLess(src.index("ambiguous = ambiguous_page_ids(diag)"), drain_i)
        self.assertLess(src.index("proven_pairs ="), drain_i)
        self.assertLess(src.index("if pair not in proven_pairs:"), drain_i)
        finalize_src = inspect.getsource(v2.LiveValidatorV2.finalize_room)
        self.assertIn("globalThis.__WOF_PROSPECTIVE_VALIDATOR.stop()", finalize_src)
        self.assertNotIn("self.ingest", finalize_src)

    def test_05_all_conservative_gates_discovery_separation_and_research_only(self) -> None:
        manifest = gate_manifest()
        rows = [gate_trace("room-a", 0, 9, lifecycle=True), gate_trace("room-b", 4, 33)]
        passed = validator.validate(manifest, rows)
        self.assertEqual(passed["verdict"], "PROSPECTIVE_PASS_RESEARCH_ONLY")
        self.assertFalse(passed["productionPromotionAllowed"])
        self.assertTrue(passed["gate"]["passed"])

        for gate_name in ("minProspectiveSignals", "minProspectiveRooms", "minDistinctTargets", "minObservedTypes"):
            m = copy.deepcopy(manifest)
            m["gate"][gate_name] = 3
            result = validator.validate(m, rows)
            self.assertEqual(result["verdict"], "PROSPECTIVE_FAIL_OR_INSUFFICIENT", gate_name)
            self.assertFalse(result["gate"][gate_name]["passed"], gate_name)

        result = validator.validate(manifest, [gate_trace("room-a", 0, 9), gate_trace("room-b", 4, 33)])
        self.assertFalse(result["gate"]["requireLifecycleReset"]["passed"])
        result = validator.validate(manifest, [gate_trace("room-a", 0, 9, lifecycle=True), gate_trace("room-b", 4, 33, attack=999)])
        self.assertFalse(result["gate"]["requireZeroHardMiss"]["passed"])

        discovery_rows = [dict(row, evidenceClass="discovery") for row in rows]
        result = validator.validate(manifest, discovery_rows)
        self.assertEqual(result["verdict"], "NO_PROSPECTIVE_EVIDENCE")
        self.assertEqual(result["prospective"]["signal"], 0)

        unknown = copy.deepcopy(manifest)
        unknown["gate"]["futureUnknownConservativeGate"] = 1
        with self.assertRaises(validator.ValidationError):
            validator.validate_manifest(unknown)

    def test_06_world_endpoint_association_and_read_only_safety_remain_intact(self) -> None:
        self.assertIn(EXPECTED_WORLD_SHA256, v2.core.IDENTITY_JS)
        self.assertIn("Warriors of Fate (World 921031)", v2.core.IDENTITY_JS)
        if v2.core.recorder_core is not None:
            self.assertEqual(v2.core.recorder_core.WORLD_SHA256, EXPECTED_WORLD_SHA256)

        self.assertTrue(h.websocket_matches_endpoint("ws://localhost:9222/devtools/browser/x", "127.0.0.1", 9222))
        self.assertFalse(h.websocket_matches_endpoint("ws://localhost:9333/devtools/browser/x", "127.0.0.1", 9222))
        self.assertFalse(h.websocket_matches_endpoint("ws://192.168.1.5:9222/devtools/browser/x", "127.0.0.1", 9222))
        self.assertFalse(h.websocket_matches_endpoint("ws://localhost:9222/devtools/browser/x", "192.168.1.5", 9222))

        pages = [
            {"targetId": "page-a", "frameId": "frame-a", "url": "https://example.invalid/not-game"},
            {"targetId": "page-b", "frameId": "frame-b", "url": "https://example.invalid/wof"},
        ]
        self.assertEqual(h.safe_page_for_direct({"parentId": "page-b", "openerId": "page-a"}, pages)["targetId"], "page-b")
        self.assertEqual(h.safe_page_for_direct({"parentFrameId": "frame-b", "openerId": "page-a"}, pages)["targetId"], "page-b")

        self.assertFalse(any(method.startswith("Input.") for method in d.DISCOVERY_CDP_METHODS))
        self.assertNotIn("Runtime.callFunctionOn", d.DISCOVERY_CDP_METHODS)
        self.assertNotIn("Page.addScriptToEvaluateOnNewDocument", d.DISCOVERY_CDP_METHODS)

        attach_src = inspect.getsource(v2.LiveValidatorV2.attach_candidate)
        for marker in ("readOnly", "ramWrites", "inputInjection", "windowWorkerReplacement"):
            self.assertIn(marker, attach_src)
        probe = v2.core.build_probe_js(gate_manifest())
        self.assertIn("readOnly:true", probe)
        self.assertIn("ramWrites:0", probe)
        self.assertIn("inputInjection:false", probe)
        self.assertIn("windowWorkerReplacement:false", probe)
        self.assertNotIn("URL.createObjectURL", probe)


if __name__ == "__main__":
    unittest.main(verbosity=2)
