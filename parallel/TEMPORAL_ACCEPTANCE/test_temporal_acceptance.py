from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import temporal_acceptance as p24

WORLD = "a" * 64
AUTH = "authority-p24"
RUNTIME_A = "runtime-epoch-aaaaaaaa"
RUNTIME_B = "runtime-epoch-bbbbbbbb"
RENDER_A = "renderer-epoch-aaaaaaaa"
RENDER_B = "renderer-epoch-bbbbbbbb"


def obs(seq, frame, actor="P1", generation=1, state="READY", *, observed=None, runtime=RUNTIME_A, renderer=RENDER_A,
        presence="PRESENT", reason=None, geometry=True, transport=None, canonical_sample=None, acks=None):
    row = {
        "schema": p24.OBSERVATION_SCHEMA,
        "sampleSeq": seq,
        "frameSeq": frame,
        "observedAt": float(seq if observed is None else observed),
        "worldSha256": WORLD,
        "authorityKey": AUTH,
        "runtimeEpoch": runtime,
        "rendererEpoch": renderer,
        "actor": actor,
        "generation": generation,
        "state": state,
        "reason": reason if state == "SUPPRESSED" else None,
        "actorPresence": presence,
        "transportSequence": transport,
        "canonicalSampleAt": canonical_sample,
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        "drawAcknowledgements": list(acks or []),
    }
    if geometry and state == "READY":
        row["canonicalGeometry"] = {
            "coordinateAuthority": "canonical-render-object-only",
            "anchor": {"x": seq * 1000000, "y": -seq * 900000},
            "bodyBounds": {"left": -999999 + seq, "top": 0, "right": 999999 + seq, "bottom": 1},
        }
    return row


def ack(sequence, generation=1, *, renderer=RENDER_A, runtime=RUNTIME_A, transport=None, sample_at=None, evidence_generation=1):
    return {
        "sequence": sequence,
        "acknowledgedAt": 1000 + sequence,
        "evidenceGeneration": evidence_generation,
        "kind": "player-danger-warning",
        "primitive": "warningTex",
        "completed": True,
        "actor": "P1",
        "generation": generation,
        "authority": {
            "worldSha256": WORLD,
            "authorityKey": AUTH,
            "runtimeEpoch": runtime,
            "rendererEpoch": renderer,
        },
        "sampleIdentity": {"transportSequence": transport, "sampleAt": sample_at},
        "coordinateAuthority": "canonical-render-object-only",
        "screenshotAuthority": False,
        "worldProjectionAuthority": False,
        "visibleProof": "NOT_PROVEN",
        "nativeX": 42,
        "nativeY": 24,
    }


def bundle(rows, source=None):
    return {"schema": p24.BUNDLE_SCHEMA, "observations": rows, "sourceEvidence": source or {}}


class TemporalAcceptanceTests(unittest.TestCase):
    def test_same_generation_ready_is_continuous_without_speed_limit(self):
        report = p24.analyze_bundle(bundle([obs(1, 10), obs(2, 11), obs(3, 12)]))
        self.assertEqual(report["aggregate"]["classification"], "PROVEN_CONTINUOUS")
        self.assertEqual(report["aggregate"]["longestReadyRun"], 3)
        self.assertFalse(report["proofBoundary"]["coordinatesUsedForContinuityConfidence"])
        self.assertFalse(report["proofBoundary"]["coordinatesUsedForIdentity"])

    def test_generation_rollover_revokes_old_generation_and_stale_ack(self):
        first_ack = ack(1, generation=1, transport=10, sample_at=1.5)
        stale_ack = ack(2, generation=1, transport=11, sample_at=2.5)
        rows = [
            obs(1, 10, generation=1, transport=10, canonical_sample=1.5, acks=[first_ack]),
            obs(2, 11, generation=2, transport=11, canonical_sample=2.5, acks=[stale_ack]),
            obs(3, 12, generation=1),
        ]
        report = p24.analyze_bundle(bundle(rows))
        self.assertEqual(report["aggregate"]["generationRolloverCount"], 1)
        self.assertEqual(report["aggregate"]["acceptedDrawAcknowledgementCount"], 1)
        self.assertEqual(report["aggregate"]["staleDrawAcknowledgementRejectionCount"], 1)
        self.assertEqual(report["rejectionReasons"]["STALE_GENERATION_REAPPEARANCE"], 1)
        self.assertEqual(report["aggregate"]["classification"], "STALE_OR_MISMATCH")

    def test_runtime_and_renderer_replacement_invalidate_old_epoch(self):
        rows = [
            obs(1, 1),
            obs(2, 1, runtime=RUNTIME_B, renderer=RENDER_B),
            obs(3, 2, runtime=RUNTIME_A, renderer=RENDER_A),
        ]
        report = p24.analyze_bundle(bundle(rows))
        self.assertEqual(report["aggregate"]["runtimeEpochReplacementCount"], 1)
        self.assertEqual(report["aggregate"]["rendererEpochReplacementCount"], 1)
        self.assertEqual(report["rejectionReasons"]["STALE_EPOCH_REAPPEARANCE"], 1)
        self.assertFalse(report["proofBoundary"]["crossEpochContinuityClaimed"])

    def test_churn_and_single_frame_suppressed_pulse_are_reported_not_smoothed(self):
        rows = [
            obs(1, 1),
            obs(2, 2, state="SUPPRESSED", reason="ACTOR_ASSOCIATION_UNPROVEN", presence="PRESENT", geometry=False),
            obs(3, 3),
        ]
        report = p24.analyze_bundle(bundle(rows))
        self.assertEqual(report["aggregate"]["oneSampleSuppressedPulseCount"], 1)
        self.assertEqual(report["aggregate"]["stateTransitionCount"], 2)
        self.assertEqual(report["aggregate"]["classification"], "OBSERVED_WITH_CHURN")
        self.assertFalse(report["aggregate"]["thresholdConfigured"])
        self.assertFalse(report["safety"]["interpolation"])
        self.assertFalse(report["safety"]["oldCoordinateReuse"])

    def test_duplicate_and_out_of_order_frames_do_not_raise_coverage(self):
        rows = [
            obs(1, 10),
            obs(2, 10),
            obs(3, 9),
            obs(4, 11),
            obs(4, 12),
        ]
        report = p24.analyze_bundle(bundle(rows))
        self.assertEqual(report["aggregate"]["acceptedSampleCount"], 2)
        self.assertEqual(report["rejectionReasons"]["DUPLICATE_FRAME_FOR_ACTOR"], 1)
        self.assertEqual(report["rejectionReasons"]["OUT_OF_ORDER_FRAME_FOR_ACTOR"], 1)
        self.assertEqual(report["rejectionReasons"]["DUPLICATE_SAMPLE_SEQUENCE"], 1)

    def test_rejected_duplicate_frame_cannot_advance_generation_state(self):
        rows = [
            obs(1, 10, generation=1),
            obs(2, 10, generation=2),
            obs(3, 11, generation=1),
        ]
        report = p24.analyze_bundle(bundle(rows))
        self.assertEqual(report["rejectionReasons"]["DUPLICATE_FRAME_FOR_ACTOR"], 1)
        self.assertEqual(report["aggregate"]["generationRolloverCount"], 0)
        by_actor = {row["actor"]: row for row in report["actors"]}
        self.assertEqual(by_actor["P1"]["readyCount"], 2)

    def test_actor_disappear_reappear_is_explicit_and_fail_closed(self):
        rows = [
            obs(1, 1, presence="PRESENT"),
            obs(2, 2, state="SUPPRESSED", reason="ACTOR_NOT_PRESENT", presence="ABSENT", geometry=False),
            obs(3, 3, presence="PRESENT"),
        ]
        report = p24.analyze_bundle(bundle(rows))
        self.assertEqual(report["aggregate"]["actorDisappearanceCount"], 1)
        self.assertEqual(report["aggregate"]["actorReappearanceCount"], 1)
        self.assertEqual(report["aggregate"]["classification"], "OBSERVED_WITH_CHURN")

    def test_multi_actor_independence_never_cross_repairs_insufficient_stream(self):
        rows = [
            obs(1, 1, actor="P1"),
            obs(2, 2, actor="P1"),
            obs(3, 1, actor="P2"),
        ]
        report = p24.analyze_bundle(bundle(rows))
        by_actor = {row["actor"]: row for row in report["actors"]}
        self.assertEqual(by_actor["P1"]["classification"], "PROVEN_CONTINUOUS")
        self.assertEqual(by_actor["P2"]["classification"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(report["aggregate"]["classification"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(report["proofBoundary"]["crossActorRepairAllowed"])

    def test_duplicate_draw_ack_is_not_counted_twice(self):
        repeated = ack(7, transport=50, sample_at=5.0)
        rows = [
            obs(1, 1, transport=50, canonical_sample=5.0, acks=[repeated]),
            obs(2, 2, transport=50, canonical_sample=5.0, acks=[repeated]),
        ]
        report = p24.analyze_bundle(bundle(rows))
        self.assertEqual(report["aggregate"]["acceptedDrawAcknowledgementCount"], 1)
        self.assertEqual(report["aggregate"]["duplicateDrawAcknowledgementCount"], 1)
        self.assertEqual(report["aggregate"]["staleDrawAcknowledgementRejectionCount"], 0)

    def test_p16_p18_snapshots_are_binding_only_and_do_not_create_continuity(self):
        source = {
            "p16": {"schema": p24.P16_SCHEMA, "visibleProof": "NOT_PROVEN"},
            "p18Snapshots": [{"schema": p24.P18_SCHEMA, "visibleProof": "NOT_PROVEN"}],
        }
        report = p24.analyze_bundle(bundle([], source))
        self.assertEqual(report["aggregate"]["classification"], "UNPROVEN")
        self.assertFalse(report["sourceEvidence"]["continuityCredit"])
        self.assertFalse(report["proofBoundary"]["singleP18SnapshotImpliesTemporalContinuity"])

    def test_deterministic_cli_output_and_jsonl_loader(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_path = root / "evidence.jsonl"
            input_path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in [obs(1, 1), obs(2, 2)]) + "\n", encoding="utf-8")
            loaded = p24.load_observation_input(input_path)
            report_a = p24.analyze_bundle(loaded)
            report_b = p24.analyze_bundle(loaded)
            self.assertEqual(report_a, report_b)
            out_a = root / "a"
            out_b = root / "b"
            p24.write_report(report_a, out_a)
            p24.write_report(report_b, out_b)
            self.assertEqual((out_a / p24.DEFAULT_JSON_NAME).read_bytes(), (out_b / p24.DEFAULT_JSON_NAME).read_bytes())
            self.assertEqual((out_a / p24.DEFAULT_MD_NAME).read_bytes(), (out_b / p24.DEFAULT_MD_NAME).read_bytes())

    def test_suppressed_geometry_is_rejected_and_alpha_live_safety_is_false(self):
        bad = obs(1, 1, state="SUPPRESSED", reason="STALE", geometry=False)
        bad["canonicalGeometry"] = {"coordinateAuthority": "canonical-render-object-only", "anchor": {"x": 1, "y": 2}}
        report = p24.analyze_bundle(bundle([bad]))
        self.assertEqual(report["aggregate"]["acceptedSampleCount"], 0)
        self.assertEqual(report["rejectionReasons"]["SUPPRESSED_GEOMETRY_FORBIDDEN"], 1)
        self.assertFalse(report["safety"]["alphaLiveMutation"])
        self.assertFalse(report["alphaLiveMoved"])


if __name__ == "__main__":
    unittest.main()
