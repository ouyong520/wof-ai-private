from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import analyzer


class AnalyzerTests(unittest.TestCase):
    def test_single_state_never_resolves(self) -> None:
        ds = analyzer.Dataset()
        ds.identity_shas.add(analyzer.WORLD_SHA256)
        for i in range(2):
            for attack in (4704, 4712):
                ds.add_trace({
                    "roomId": f"r-{attack}-{i}",
                    "slot": i,
                    "type": 18,
                    "activeAttack": attack,
                    "candidateSeen": True,
                    "candidateStateIndexes": [0],
                    "candidateFirstLeadMs": 50,
                    "candidateLastLeadMs": 40,
                    "targetStable": True,
                    "sideStable": True,
                    "retargets": [],
                    "states": [{"signature": analyzer.CANDIDATE_SIG}],
                }, "test")
        result = analyzer.analyze(ds, min_per_outcome=2, min_sequence_support=2)
        self.assertEqual(result["t18"]["verdict"], "insufficient")
        self.assertFalse(result["t18"]["prospectiveValidator"]["worthEntering"])

    def test_repeated_exclusive_ordered_tail_resolves(self) -> None:
        ds = analyzer.Dataset()
        ds.identity_shas.add(analyzer.WORLD_SHA256)
        sig_a = "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736"
        sig_b = "S0/A2/B0|BODY4728|FE8b660|NX8b204|Vffff|TM3|P6C4736"
        for i in range(2):
            ds.add_trace(analyzer.synthetic_trace(4704, sig_a, room=f"a{i}"), "test")
            ds.add_trace(analyzer.synthetic_trace(4712, sig_b, room=f"b{i}"), "test")
        result = analyzer.analyze(ds, min_per_outcome=2, min_sequence_support=2)
        self.assertEqual(result["t18"]["verdict"], "resolved")
        self.assertTrue(result["t18"]["prospectiveValidator"]["worthEntering"])
        self.assertIn(result["t18"]["strongestDiscriminator"]["feature"], {
            "exact_tail2", "tm_tail2", "exact_pair", "tm_pair"
        })

    def test_target_side_instability_blocks_resolution(self) -> None:
        ds = analyzer.Dataset()
        ds.identity_shas.add(analyzer.WORLD_SHA256)
        sig_a = "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736"
        sig_b = "S0/A2/B0|BODY4728|FE8b660|NX8b204|Vffff|TM3|P6C4736"
        ds.add_trace(analyzer.synthetic_trace(4704, sig_a, room="a0"), "test")
        ds.add_trace(analyzer.synthetic_trace(4704, sig_a, room="a1", stable=False), "test")
        ds.add_trace(analyzer.synthetic_trace(4712, sig_b, room="b0"), "test")
        ds.add_trace(analyzer.synthetic_trace(4712, sig_b, room="b1"), "test")
        result = analyzer.analyze(ds, min_per_outcome=2, min_sequence_support=2)
        self.assertEqual(result["t18"]["verdict"], "insufficient")

    def test_wrong_identity_blocks_resolution(self) -> None:
        ds = analyzer.Dataset()
        ds.identity_shas.add("deadbeef")
        sig_a = "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736"
        sig_b = "S0/A2/B0|BODY4728|FE8b660|NX8b204|Vffff|TM3|P6C4736"
        for i in range(2):
            ds.add_trace(analyzer.synthetic_trace(4704, sig_a, room=f"a{i}"), "test")
            ds.add_trace(analyzer.synthetic_trace(4712, sig_b, room=f"b{i}"), "test")
        result = analyzer.analyze(ds, min_per_outcome=2, min_sequence_support=2)
        self.assertEqual(result["t18"]["verdict"], "insufficient")
        self.assertFalse(result["identity"]["ok"])

    def test_merged_preferred_and_room_supplements_t23_rare(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "run-test"
            merged = {
                "schema": analyzer.RECORDER_SCHEMA,
                "runId": run_id,
                "status": "complete",
                "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
                "counts": {"enemySamples": 100, "t18Samples": 10, "t18CandidateCycles": 0, "t23Cycles": 1},
                "coverage": {
                    "playerCountHist": [0, 1, 2, 3],
                    "targetSamples": {"P1": 5},
                    "enemyTypeSamplesTop": [{"key": "T18", "count": 10}],
                    "activeAttackFrequencyTop": [{"key": "T18|A4704", "count": 1}],
                    "sceneTypeSetTop": [{"key": "T18", "count": 2}],
                },
                "t18CandidateEvidence": [],
                "rooms": [{"roomId": "r1", "identitySha256": analyzer.WORLD_SHA256}],
            }
            room = {
                "schema": analyzer.RECORDER_SCHEMA,
                "runId": run_id,
                "roomId": "r1",
                "status": "complete",
                "identity": {"sha256": analyzer.WORLD_SHA256},
                "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
                "diagnostics": {
                    "enemySamples": 100,
                    "rareDescriptorAttack": {"T18|X->A4704": 2},
                },
                "t18": {"candidateTraces": []},
                "t23": {"traces": [{"roomId": "r1", "activeAttack": 5888, "states": []}]},
                "rareDescriptorAttackEdges": [],
            }
            (root / "merged.json").write_text(json.dumps(merged), encoding="utf-8")
            (root / "room.json").write_text(json.dumps(room), encoding="utf-8")
            ds = analyzer.build_dataset([str(root)])
            self.assertEqual(ds.counts["enemySamples"], 100)
            self.assertEqual(len(ds.t23_traces), 1)
            self.assertEqual(ds.rare_edges["T18|X->A4704"], 2)

    def test_zero_target_coverage_writes_insufficient(self) -> None:
        ds = analyzer.Dataset()
        ds.identity_shas.add(analyzer.WORLD_SHA256)
        result = analyzer.analyze(ds, min_per_outcome=2, min_sequence_support=2)
        self.assertEqual(result["t18"]["verdictZh"], "仍不足")
        self.assertEqual(result["t18"]["distribution"], {"A4704": 0, "A4712": 0})

    def test_identical_per_room_traces_remain_room_isolated_and_rare_not_doubled(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            trace = analyzer.synthetic_trace(4704, "S0/A6/B4|BODY4728|FE1|NX2|V3|TM2|P6C4", room="ignored")
            trace.pop("roomId", None)
            for idx in (1, 2):
                room = {
                    "schema": analyzer.RECORDER_SCHEMA,
                    "runId": "same-run",
                    "roomId": f"room-{idx}",
                    "status": "complete",
                    "identity": {"sha256": analyzer.WORLD_SHA256},
                    "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
                    "diagnostics": {
                        "t18": {"samples": 1, "candidateCycles": 1, "candidateSamples": 1},
                        "rareDescriptorAttack": {"T18|X->A4704": 2},
                    },
                    "t18": {"candidateTraces": [trace]},
                    "t23": {"traces": []},
                    "rareDescriptorAttackEdges": [{"type": 18, "preActiveSignature": "X", "attack": 4704}],
                }
                (root / f"room-{idx}.json").write_text(json.dumps(room), encoding="utf-8")
            ds = analyzer.build_dataset([str(root)])
            self.assertEqual(len(ds.traces), 2)
            self.assertEqual({tr["roomId"] for tr in ds.traces}, {"room-1", "room-2"})
            self.assertEqual(ds.rare_edges["T18|X->A4704"], 4)

    def test_partial_fleet_plus_available_child_does_not_double_counts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            child = {
                "schema": analyzer.RECORDER_SCHEMA,
                "runId": "child-1",
                "status": "complete",
                "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
                "counts": {"enemySamples": 100},
                "coverage": {},
                "t18CandidateEvidence": [],
                "rooms": [{"roomId": "r1", "identitySha256": analyzer.WORLD_SHA256}],
            }
            fleet = {
                "schema": analyzer.FLEET_SCHEMA,
                "runId": "fleet-1",
                "status": "complete",
                "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
                "counts": {"enemySamples": 200},
                "t18CandidateEvidence": [],
                "rooms": [
                    {"roomId": "r1", "identitySha256": analyzer.WORLD_SHA256},
                    {"roomId": "r2", "identitySha256": analyzer.WORLD_SHA256},
                ],
                "childRuns": [
                    {"fleetInstanceId": 1, "runId": "child-1"},
                    {"fleetInstanceId": 2, "runId": "child-2"},
                ],
            }
            (root / "child-1.json").write_text(json.dumps(child), encoding="utf-8")
            (root / "fleet.json").write_text(json.dumps(fleet), encoding="utf-8")
            ds = analyzer.build_dataset([str(root)])
            self.assertEqual(ds.counts["enemySamples"], 200)
            self.assertEqual(len(ds.inputs), 1)
            self.assertEqual(ds.inputs[0]["kind"], "fleet")

    def test_missing_safety_metadata_is_a_resolution_blocker(self) -> None:
        ds = analyzer.Dataset()
        ds.identity_shas.add(analyzer.WORLD_SHA256)
        ds.check_safety({}, "missing")
        sig_a = "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736"
        sig_b = "S0/A2/B0|BODY4728|FE8b660|NX8b204|Vffff|TM3|P6C4736"
        for i in range(2):
            ds.add_trace(analyzer.synthetic_trace(4704, sig_a, room=f"a{i}"), "test")
            ds.add_trace(analyzer.synthetic_trace(4712, sig_b, room=f"b{i}"), "test")
        result = analyzer.analyze(ds, min_per_outcome=2, min_sequence_support=2)
        self.assertEqual(result["t18"]["verdict"], "insufficient")
        self.assertTrue(result["safety"]["inputSafetyViolations"])


if __name__ == "__main__":
    unittest.main()
