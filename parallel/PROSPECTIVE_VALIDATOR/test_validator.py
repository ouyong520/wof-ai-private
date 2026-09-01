import unittest
from pathlib import Path

import validator

HERE = Path(__file__).resolve().parent


class ValidatorTests(unittest.TestCase):
    def manifest(self, name):
        return validator.load_json(HERE / "manifests" / name)

    def corpus(self, name="mock_corpus.json"):
        return validator.load_json(HERE / "fixtures" / name)

    def test_t18_tail2_and_gate(self):
        m = self.manifest("t18_body4728_ordered_tail.example.json")
        traces = validator.unified_traces(self.corpus(), "mock")
        result = validator.validate(m, traces)
        self.assertEqual(result["prospective"]["signal"], 2)
        self.assertEqual(result["prospective"]["strict"], 1)
        self.assertEqual(result["prospective"]["jitter"], 1)
        self.assertEqual(result["verdict"], "PROSPECTIVE_PASS_RESEARCH_ONLY")
        self.assertFalse(result["productionPromotionAllowed"])

    def test_t23_tail3_timer_normalized(self):
        m = self.manifest("t23_a5888_body4936_tail3.example.json")
        traces = validator.unified_traces(self.corpus(), "mock")
        result = validator.validate(m, traces)
        self.assertEqual(result["prospective"]["signal"], 2)
        self.assertEqual(result["prospective"]["strict"], 1)
        self.assertEqual(result["prospective"]["jitter"], 1)
        self.assertEqual(result["prospective"]["attacks"], {"A5888": 2})

    def test_current_level_predicate(self):
        m = self.manifest("current_level.example.json")
        traces = validator.unified_traces(self.corpus(), "mock")
        result = validator.validate(m, traces)
        self.assertEqual(result["prospective"]["signal"], 1)
        self.assertEqual(result["prospective"]["strict"], 1)

    def test_discovery_never_satisfies_prospective_gate(self):
        m = self.manifest("t18_body4728_ordered_tail.example.json")
        traces = validator.unified_traces(self.corpus("mock_discovery.json"), "old")
        result = validator.validate(m, traces)
        self.assertEqual(result["discovery"]["signal"], 1)
        self.assertEqual(result["prospective"]["signal"], 0)
        self.assertEqual(result["verdict"], "NO_PROSPECTIVE_EVIDENCE")

    def test_wrong_attack_is_hard_miss(self):
        m = self.manifest("t18_body4728_ordered_tail.example.json")
        tr = dict(validator.unified_traces(self.corpus(), "mock")[0])
        tr["activeAttack"] = 4712
        result = validator.validate(m, [tr])
        self.assertEqual(result["prospective"]["hardMiss"], 1)
        self.assertEqual(result["verdict"], "PROSPECTIVE_FAIL_OR_INSUFFICIENT")

    def test_recorder_adapter_defaults_to_discovery(self):
        payload = {
            "schema": "wof-052l-recorder-v1", "runId": "r1",
            "t18CandidateEvidence": [{"activeAttack": 4704, "candidateLastLeadMs": 70, "states": [
                {"signature": "S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736"},
                {"signature": "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736"}
            ]}]
        }
        rows = validator.recorder_traces(payload, "rec")
        self.assertEqual(rows[0]["evidenceClass"], "discovery")
        result = validator.validate(self.manifest("t18_body4728_ordered_tail.example.json"), rows)
        self.assertEqual(result["discovery"]["signal"], 1)
        self.assertEqual(result["prospective"]["signal"], 0)

    def test_manifest_forbids_production_promotion(self):
        m = self.manifest("current_level.example.json")
        m["promotion"] = "production"
        with self.assertRaises(validator.ValidationError):
            validator.validate_manifest(m)

    def test_session_freeze_marks_new_recorder_room_prospective(self):
        m = self.manifest("t18_body4728_ordered_tail.example.json")
        session = validator.make_session(m, "2026-09-01T12:00:00.000Z")
        payload = {"schema": "wof-052l-recorder-v1", "roomId": "new-room", "startedAt": "2026-09-01T12:00:01.000Z", "t18": {"candidateTraces": [{"activeAttack": 4704, "candidateLastLeadMs": 70, "states": [
            {"signature": "S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736"},
            {"signature": "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736"}
        ]}]}}
        rows = validator.recorder_traces(payload, "new", session)
        self.assertEqual(rows[0]["evidenceClass"], "prospective")

    def test_session_freeze_keeps_old_recorder_room_discovery(self):
        m = self.manifest("t18_body4728_ordered_tail.example.json")
        session = validator.make_session(m, "2026-09-01T12:00:00.000Z")
        payload = {"schema": "wof-052l-recorder-v1", "roomId": "old-room", "startedAt": "2026-09-01T11:59:59.000Z", "t18": {"candidateTraces": [{"activeAttack": 4704, "candidateLastLeadMs": 70, "states": [
            {"signature": "S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736"},
            {"signature": "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736"}
        ]}]}}
        rows = validator.recorder_traces(payload, "old", session)
        self.assertEqual(rows[0]["evidenceClass"], "discovery")

    def test_session_hash_rejects_manifest_mutation(self):
        m = self.manifest("current_level.example.json")
        session = validator.make_session(m, "2026-09-01T12:00:00.000Z")
        m["outcome"]["expectedAttacks"] = [9999]
        with self.assertRaises(validator.ValidationError):
            validator.validate_session(session, m)

    def test_no_active_timeout_is_hard_miss(self):
        m = self.manifest("current_level.example.json")
        trace = {"evidenceClass": "prospective", "roomId": "timeout", "activeAttack": None, "leadMs": 1200, "hardMissReason": "no-active-before-timeout", "states": [{"signature": "S0/A4/B0|BODY7512|FE84868|NX83c56|V1|TM4|P6C0"}]}
        result = validator.validate(m, [trace])
        self.assertEqual(result["prospective"]["hardMiss"], 1)
        self.assertEqual(result["prospective"]["censored"], 0)

    def test_censored_signal_is_counted(self):
        m = self.manifest("current_level.example.json")
        trace = {"evidenceClass": "prospective", "roomId": "closed", "activeAttack": None, "leadMs": 40, "censored": True, "states": [{"signature": "S0/A4/B0|BODY7512|FE84868|NX83c56|V1|TM4|P6C0"}]}
        result = validator.validate(m, [trace])
        self.assertEqual(result["prospective"]["censored"], 1)
        self.assertEqual(result["prospective"]["hardMiss"], 0)


if __name__ == "__main__":
    unittest.main()
