from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import dynamic_actor_state_coverage as p22

WORLD = p22.ACCEPTED_WORLD_SHA256
SOURCE = "0752796369f1687435a1b1647e66ea0b5ab07688"
CANDIDATE_SHA = "d7835982ef3210b605c0f90b25e859bf013c7d16be541f7f09f6ba7d4410a150"
PACKAGE = "2026.09.05.0752796369f1"
AUTH = "authority-exact-001"
RUN1 = "runtimeepoch000000000000000000001"
REN1 = "rendererepoch0000000000000000001"
RUN2 = "runtimeepoch000000000000000000002"
REN2 = "rendererepoch0000000000000000002"
PAGE = "page-exact-1"


def candidate():
    return {"sourceCommit": SOURCE, "packageVersion": PACKAGE, "candidateSha256": CANDIDATE_SHA}


def receipt():
    return {
        "schema": p22.P21_RECEIPT_SCHEMA,
        "version": 1,
        "candidate": candidate(),
        "alphaLiveMoved": False,
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False},
    }


def ready(actor, generation, sample, x, y, bounds, *, runtime=RUN1, renderer=REN1, authority=AUTH):
    return {
        "kind": "player" if actor in p22.PLAYER_SET else "enemy",
        "actor": actor,
        "generation": generation,
        "sampleAt": sample,
        "worldSha256": WORLD,
        "authorityKey": authority,
        "runtimeEpoch": runtime,
        "rendererEpoch": renderer,
        "canonicalAnchor": {
            "schema": p22.CANONICAL_ANCHOR_SCHEMA,
            "state": "READY",
            "actor": actor,
            "generation": generation,
            "nativeWidth": 384,
            "nativeHeight": 224,
            "anchor": {"x": x, "y": y},
            "bodyBounds": dict(bounds),
            "authorityKey": authority,
            "runtimeEpoch": runtime,
            "rendererEpoch": renderer,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        },
    }


def suppressed(actor, generation, sample, reason, *, runtime=RUN1, renderer=REN1, authority=AUTH):
    return {
        "kind": "player" if actor in p22.PLAYER_SET else "enemy",
        "actor": actor,
        "generation": generation,
        "sampleAt": sample,
        "worldSha256": WORLD,
        "authorityKey": authority,
        "runtimeEpoch": runtime,
        "rendererEpoch": renderer,
        "canonicalAnchor": {
            "schema": p22.CANONICAL_ANCHOR_SCHEMA,
            "state": "SUPPRESSED",
            "reason": reason,
            "nativeWidth": 384,
            "nativeHeight": 224,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        },
    }


def status(records, *, runtime=RUN1, renderer=REN1, page=PAGE, authority=AUTH, state="READY", reason="CANONICAL_ANCHORS_READY"):
    binding = {"worldSha256": WORLD, "authorityKey": authority, "runtimeEpoch": runtime, "rendererEpoch": renderer}
    return {
        "schema": p22.CANONICAL_COORDINATOR_SCHEMA,
        "state": state,
        "reason": reason,
        "active": True,
        "bound": True,
        "pageTargetId": page,
        "authorityKey": authority,
        "runtimeEpoch": runtime,
        "rendererEpoch": renderer,
        "worldSha256": WORLD,
        "legacySpatialFallback": False,
        "positionAuthority": p22.CANONICAL_ANCHOR_SCHEMA,
        "bridge": {
            "schema": p22.CANONICAL_BRIDGE_SCHEMA,
            "state": state if state in {"READY", "SUPPRESSED"} else "SUPPRESSED",
            "reason": reason,
            "bound": True,
            "pageTargetId": page,
            "authorityBinding": binding,
            "positionAuthority": p22.CANONICAL_ANCHOR_SCHEMA,
            "legacyPositionFallback": False,
            "lastPayload": {"schema": p22.CANONICAL_TRANSPORT_SCHEMA, "authorityBinding": binding, "records": records},
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        },
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


def player_semantic(sample, *, p1=True, p2=False, p3=False, runtime=RUN1):
    return {
        "schema": p22.SEMANTIC_SCHEMA,
        "kind": "player-head-spatial",
        "release": p22.SEMANTIC_RELEASE,
        "runtimeEpoch": runtime,
        "sampleAt": sample,
        "players": {
            "P1": {"present": p1, "x": 9999, "y": -9999, "z": 123},
            "P2": {"present": p2, "x": 1, "y": 2, "z": 3},
            "P3": {"present": p3, "x": 4, "y": 5, "z": 6},
        },
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


def enemy_semantic(actor, code, sample, *, runtime=RUN1):
    return {
        "schema": p22.SEMANTIC_SCHEMA,
        "kind": "enemy-target-markers",
        "release": p22.SEMANTIC_RELEASE,
        "runtimeEpoch": runtime,
        "semanticProjectionIndependent": True,
        "markers": [{
            "sourceId": actor,
            "target7E": code,
            "target": p22.TARGET_CODE_TO_PLAYER[code],
            "sampleAt": sample,
            "enemyX": 777,
            "enemyY": 888,
            "enemyZ": 999,
        }],
        "projection": {"legacy": True},
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


def ack(seq, actor, generation, sample, *, label="1P", runtime=RUN1, renderer=REN1, authority=AUTH):
    return {
        "sequence": seq,
        "kind": "enemy-target-label",
        "actor": actor,
        "generation": generation,
        "sampleIdentity": {"sampleAt": sample},
        "label": label,
        "sourceId": actor,
        "nativeX": 100 + seq,
        "nativeY": 50 + seq,
        "completed": True,
        "coordinateAuthority": "canonical-render-object-only",
        "authority": {"worldSha256": WORLD, "authorityKey": authority, "runtimeEpoch": runtime, "rendererEpoch": renderer},
        "visibleProof": "NOT_PROVEN",
    }


def draw(rows, *, runtime=RUN1, renderer=REN1, page=PAGE, authority=AUTH):
    return {
        "schema": p22.P18_SCHEMA,
        "version": 1,
        "evidenceGeneration": 1,
        "identity": {"worldSha256": WORLD, "pageTargetId": page, "authorityKey": authority, "runtimeEpoch": runtime, "rendererEpoch": renderer},
        "acknowledgements": rows,
        "visibleProof": "NOT_PROVEN",
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "legacySpatialFallback": False,
            "screenshotProductionCoordinates": False,
            "worldProjectionProductionCoordinates": False,
        },
    }


def matrix(report):
    return {row["id"]: row for row in report["coverageMatrix"]}


class FocusedP22Tests(unittest.TestCase):
    def test_move_body_enemy_continuity_deterministic_and_rare_unproven(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate())
        p1a = {"left": 90, "top": 60, "right": 110, "bottom": 100}
        p1b = {"left": 94, "top": 56, "right": 116, "bottom": 102}
        enemy = {"left": 180, "top": 70, "right": 204, "bottom": 108}
        r.record_cycle(status([ready("P1", 1, 100, 100, 56, p1a), ready("enemy-slot-2", 5, 100, 192, 66, enemy)]), semantic_envelopes=[player_semantic(100), enemy_semantic("enemy-slot-2", 0, 100)], draw_evidence=draw([ack(1, "enemy-slot-2", 5, 100)]), observed_at_ms=100)
        r.record_cycle(status([ready("P1", 1, 200, 105, 52, p1b), ready("enemy-slot-2", 5, 200, 196, 66, enemy)]), semantic_envelopes=[player_semantic(200), enemy_semantic("enemy-slot-2", 0, 200)], draw_evidence=draw([ack(1, "enemy-slot-2", 5, 100), ack(2, "enemy-slot-2", 5, 200)]), observed_at_ms=200)
        a = r.build_report(generated_at_utc="fixed")
        self.assertEqual(a, r.build_report(generated_at_utc="fixed"))
        m = matrix(a)
        self.assertEqual(m["movement.P1_same_generation_anchor_change"]["status"], p22.STATUS_OBSERVED_PROVEN)
        self.assertEqual(m["animation.P1_renderer_body_geometry_change"]["status"], p22.STATUS_OBSERVED_PROVEN)
        self.assertEqual(m["enemy.target_label_current_generation_continuity"]["status"], p22.STATUS_OBSERVED_PROVEN)
        self.assertEqual(a["coreAcceptance"]["state"], "CORE_COVERAGE_READY")
        for named in p22.RARE_NAMED_STATES:
            self.assertEqual(m[f"named_state.{named}"]["status"], p22.STATUS_UNPROVEN_SIGNAL)
        text = json.dumps(a, sort_keys=True)
        for forbidden in ('"enemyX"', '"enemyY"', '"enemyZ"', '"projection"'):
            self.assertNotIn(forbidden, text)
        self.assertEqual(a["visibleProof"], "NOT_PROVEN")
        self.assertEqual(a["realWofAcceptance"], "NOT_RUN")

    def test_p2_p3_join_leave_presence_only(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate())
        b = {"left": 20, "top": 20, "right": 40, "bottom": 60}
        for i, pair in enumerate(((False, False), (True, True), (False, False)), 1):
            sample = i * 100
            r.record_cycle(status([ready("P1", 1, sample, 30 + i, 16, b)]), semantic_envelopes=[player_semantic(sample, p2=pair[0], p3=pair[1])], observed_at_ms=sample)
        m = matrix(r.build_report(generated_at_utc="fixed"))
        for actor in ("P2", "P3"):
            self.assertEqual(m[f"player.{actor}_join"]["status"], p22.STATUS_OBSERVED_PROVEN)
            self.assertEqual(m[f"player.{actor}_leave"]["status"], p22.STATUS_OBSERVED_PROVEN)

    def test_retired_generation_ready_rejected(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate())
        b = {"left": 10, "top": 10, "right": 30, "bottom": 50}
        r.record_cycle(status([ready("P1", 1, 100, 20, 6, b)]), observed_at_ms=100)
        r.record_cycle(status([ready("P1", 2, 200, 25, 6, b)]), observed_at_ms=200)
        stale = r.record_cycle(status([ready("P1", 1, 300, 30, 6, b)]), observed_at_ms=300)
        self.assertEqual(stale["records"], [])
        m = matrix(r.build_report(generated_at_utc="fixed"))
        self.assertEqual(m["generation.player_rebuild"]["status"], p22.STATUS_OBSERVED_PROVEN)
        self.assertEqual(m["generation.stale_old_generation_ready"]["status"], p22.STATUS_SUPPRESSED_SAFELY)

    def test_renderer_replacement_and_stale_p18_fail_closed(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate())
        b = {"left": 10, "top": 10, "right": 30, "bottom": 50}
        r.record_cycle(status([ready("P1", 1, 100, 20, 6, b)]), observed_at_ms=100)
        r.record_cycle(status([ready("P1", 1, 200, 22, 6, b, runtime=RUN2, renderer=REN2)], runtime=RUN2, renderer=REN2), draw_evidence=draw([ack(1, "P1", 1, 100)], runtime=RUN1, renderer=REN1), observed_at_ms=200)
        old = r.record_cycle(status([ready("P1", 1, 300, 24, 6, b)]), observed_at_ms=300)
        self.assertTrue(old.get("rejectedAsStaleIdentity"))
        report = r.build_report(generated_at_utc="fixed")
        m = matrix(report)
        self.assertEqual(m["runtime.renderer_or_runtime_replacement"]["status"], p22.STATUS_OBSERVED_PROVEN)
        self.assertEqual(m["runtime.stale_cross_epoch_evidence"]["status"], p22.STATUS_SUPPRESSED_SAFELY)
        self.assertEqual(report["drawLinkage"]["linkedAcknowledgementCount"], 0)

    def test_offscreen_suppression_reentry(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate())
        b = {"left": 60, "top": 40, "right": 80, "bottom": 90}
        r.record_cycle(status([ready("P1", 1, 100, 70, 36, b)]), observed_at_ms=100)
        r.record_cycle(status([suppressed("P1", 1, 200, "VISIBLE_BODY_BOUNDS_UNAVAILABLE")], state="SUPPRESSED", reason="VISIBLE_BODY_BOUNDS_UNAVAILABLE"), observed_at_ms=200)
        r.record_cycle(status([ready("P1", 1, 300, 74, 36, b)]), observed_at_ms=300)
        self.assertEqual(matrix(r.build_report(generated_at_utc="fixed"))["visibility.offscreen_suppression_reentry"]["status"], p22.STATUS_OBSERVED_PROVEN)

    def test_enemy_target_switch_and_no_guessed_disappearance(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate())
        b = {"left": 150, "top": 50, "right": 180, "bottom": 100}
        r.record_cycle(status([ready("enemy-slot-3", 9, 100, 165, 46, b)]), semantic_envelopes=[enemy_semantic("enemy-slot-3", 0, 100)], draw_evidence=draw([ack(1, "enemy-slot-3", 9, 100, label="1P")]), observed_at_ms=100)
        r.record_cycle(status([ready("enemy-slot-3", 9, 200, 167, 46, b)]), semantic_envelopes=[enemy_semantic("enemy-slot-3", 4, 200)], draw_evidence=draw([ack(1, "enemy-slot-3", 9, 100, label="1P"), ack(2, "enemy-slot-3", 9, 200, label="2P")]), observed_at_ms=200)
        m = matrix(r.build_report(generated_at_utc="fixed"))
        self.assertEqual(m["enemy.target_switch_0_4_8"]["status"], p22.STATUS_OBSERVED_PROVEN)
        self.assertEqual(m["enemy.disappear_edge"]["status"], p22.STATUS_NOT_OBSERVED)

    def test_cumulative_p18_ack_dedup(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate())
        b = {"left": 150, "top": 50, "right": 180, "bottom": 100}
        s = status([ready("enemy-slot-4", 2, 100, 165, 46, b)])
        sem = [enemy_semantic("enemy-slot-4", 0, 100)]
        d = draw([ack(1, "enemy-slot-4", 2, 100)])
        r.record_cycle(s, semantic_envelopes=sem, draw_evidence=d, observed_at_ms=100)
        r.record_cycle(s, semantic_envelopes=sem, draw_evidence=d, observed_at_ms=110)
        report = r.build_report(generated_at_utc="fixed")
        self.assertEqual(report["drawLinkage"]["linkedAcknowledgementCount"], 1)
        self.assertEqual(matrix(report)["enemy.target_label_current_generation_continuity"]["status"], p22.STATUS_OBSERVED_PARTIAL)

    def test_bounded_ledger(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate(), ledger_limit=3)
        b = {"left": 10, "top": 10, "right": 30, "bottom": 50}
        for i in range(1, 8):
            r.record_cycle(status([ready("P1", 1, i * 100, 20 + i, 6, b)]), observed_at_ms=i * 100)
        report = r.build_report(generated_at_utc="fixed")
        self.assertEqual(report["evidence"]["cycleCount"], 3)
        self.assertEqual([c["sequence"] for c in report["evidence"]["cycles"]], [5, 6, 7])

    def test_legacy_and_suppressed_coordinate_fail_closed(self):
        r = p22.DynamicActorStateCoverageRecorder(candidate())
        b = {"left": 10, "top": 10, "right": 30, "bottom": 50}
        bad = status([ready("P1", 1, 100, 20, 6, b)])
        bad["bridge"]["legacyPositionFallback"] = True
        with self.assertRaises(p22.CoverageError): r.record_cycle(bad, observed_at_ms=100)
        bad_row = suppressed("P1", 1, 100, "VISIBLE_BODY_BOUNDS_UNAVAILABLE")
        bad_row["canonicalAnchor"]["anchor"] = {"x": 1, "y": 2}
        with self.assertRaises(p22.CoverageError): r.record_cycle(status([bad_row]), observed_at_ms=100)

    def test_bundle_outputs(self):
        b = {"left": 10, "top": 10, "right": 30, "bottom": 50}
        bundle = {"schema": p22.INPUT_SCHEMA, "version": 1, "p21Receipt": receipt(), "cycles": [{"observedAtMs": 100, "runtimeStatus": status([ready("P1", 1, 100, 20, 6, b)]), "semanticEnvelopes": [player_semantic(100)]}]}
        report = p22.analyze_bundle(bundle, generated_at_utc="fixed")
        with tempfile.TemporaryDirectory() as td:
            jp, mp = p22.atomic_write_outputs(Path(td), report)
            self.assertEqual(json.loads(jp.read_text())["visibleProof"], "NOT_PROVEN")
            self.assertIn("UNPROVEN_SIGNAL", mp.read_text())

    def test_windows_wrapper_contract(self):
        text = (Path(__file__).with_name("WOF_ALPHA_DYNAMIC_STATE_COVERAGE.cmd")).read_text(encoding="utf-8").lower()
        self.assertIn("wof_alpha_p22_input", text)
        self.assertIn("dynamic_actor_state_coverage.py", text)
        for forbidden in ("update-ref", "git push", "alpha-live", "capturescreenshot", "devtools"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
