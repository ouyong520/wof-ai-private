from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import post_promotion_verify as m


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Fixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.repo = root / "repo"
        self.results = root / "results"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "p23@test.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "P23 Test"], check=True)
        for rel in m.REQUIRED_W1_FILES:
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(rel + "\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "rollback"], check=True)
        self.rollback = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True).strip()
        (self.repo / "candidate_marker.txt").write_text("candidate\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "candidate"], check=True)
        self.target = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True).strip()
        self.package = "fixture.package"
        self.identity = {
            "worldSha256": "w" * 64,
            "pageTargetId": "page-1",
            "workerTargetId": "worker-1",
            "authorityKey": "authority-1",
            "runtimeEpoch": "runtime-1",
            "rendererEpoch": "renderer-1",
            "rendererAuthority": "renderer-authority-1",
        }
        self.candidate = self.repo / "candidate.json"
        write_json(self.candidate, {
            "schema": "wof-owner-oneclick-package-v1",
            "sourceCommit": self.target,
            "packageVersion": self.package,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False},
            "components": {"canonicalProductConvergence": {"legacySpatialFallback": False, "alphaLivePromoted": False}},
        })
        self.attestation = self.repo / "candidate.attestation.json"
        write_json(self.attestation, {
            "schema": "wof-alpha-final-canonical-candidate-attestation-v1",
            "version": 1,
            "sourceCommit": self.target,
            "packageVersion": self.package,
            "candidateSha256": sha(self.candidate),
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False},
        })
        self.candidate_sha = sha(self.candidate)
        self.attestation_sha = sha(self.attestation)
        self.p17 = self.results / m.DEFAULT_P17_NAME
        self.p17_raw = {
            "schema": m.P17_BUNDLE_SCHEMA,
            "version": 1,
            "automaticDecision": "READY_FOR_OWNER_VISUAL_CONFIRMATION",
            "visibleProof": "NOT_PROVEN",
            "ownerVisualConfirmationRequired": True,
            "candidate": {"sourceCommit": self.target, "packageVersion": self.package, "contentSha256": self.candidate_sha},
            "w3Qualification": {"status": "PASS", "identity": self.identity, "canonicalProducerReadiness": {"ready": True, "rendererSource": {"proven": True}}},
            "p16CanonicalRuntime": {"canonicalState": "HUD_INGEST_ACCEPTED", "visibleProof": "NOT_PROVEN", "identity": self.identity},
            "p18DrawEvidence": {"evidenceState": "CANONICAL_DRAW_ACKNOWLEDGED", "visibleProof": "NOT_PROVEN", "identity": self.identity},
            "identityConsistency": {"consistent": True, "mismatches": []},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "alphaLiveMoved": False},
        }
        write_json(self.p17, self.p17_raw)
        self.p16 = self.results / m.DEFAULT_P16_NAME
        write_json(self.p16, {
            "schema": m.P16_SCHEMA,
            "version": 1,
            "packageVersion": self.package,
            "canonical": {"state": "HUD_INGEST_ACCEPTED"},
            "world": {"sha256": self.identity["worldSha256"], "pageTargetId": self.identity["pageTargetId"], "workerTargetId": self.identity["workerTargetId"]},
            "runtime": {"authorityKey": self.identity["authorityKey"], "epoch": self.identity["runtimeEpoch"], "rendererEpoch": self.identity["rendererEpoch"], "rendererAuthority": self.identity["rendererAuthority"]},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        })
        self.p18 = self.results / m.DEFAULT_P18_NAME
        write_json(self.p18, {
            "schema": m.P18_SCHEMA,
            "version": 1,
            "packageVersion": self.package,
            "evidenceState": "CANONICAL_DRAW_ACKNOWLEDGED",
            "identity": self.identity,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        })
        self.visual = self.results / "visual.json"
        write_json(self.visual, {
            "schema": m.P20_RECEIPT_SCHEMA,
            "version": 1,
            "fixtureMode": False,
            "promotionEligible": True,
            "ownerVisualVerdict": "PASS",
            "ownerAnswer": "YES",
            "visualProof": "OWNER_VISUAL_PASS",
            "candidateSourceCommit": self.target,
            "packageVersion": self.package,
            "candidateSha256": self.candidate_sha,
            "candidateAttestationSha256": self.attestation_sha,
            "acceptanceBundleSha256": sha(self.p17),
            "identity": self.identity,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "alphaLiveMoved": False, "forcePushAllowed": False},
        })
        self.plan = self.results / "plan.json"
        core = {
            "fromAlphaLiveCommit": self.rollback,
            "toCandidateCommit": self.target,
            "packageVersion": self.package,
            "candidateSha256": self.candidate_sha,
            "candidateAttestationSha256": self.attestation_sha,
            "acceptanceBundleSha256": sha(self.p17),
            "visualReceiptSha256": sha(self.visual),
            "identity": self.identity,
            "rollback": {"previousCommit": self.rollback, "preserveW1LastKnownGoodBehavior": True},
            "fastForwardRequired": True,
            "compareAndSwapExpectedOld": self.rollback,
            "requiredW1Files": list(m.REQUIRED_W1_FILES),
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False, "forcePushAllowed": False, "alphaLiveMovedAtPlan": False},
        }
        self.plan_hash = m._canonical_hash(core)
        write_json(self.plan, {"schema": m.P20_PLAN_SCHEMA, "version": 1, "state": "READY", "planCore": core, "planHash": self.plan_hash})
        self.promotion_result = self.results / "promotion.json"
        write_json(self.promotion_result, {
            "schema": m.P20_RESULT_SCHEMA,
            "version": 1,
            "state": "PROMOTED",
            "planHash": self.plan_hash,
            "fromAlphaLiveCommit": self.rollback,
            "toCandidateCommit": self.target,
            "alphaLiveMoved": True,
            "forcePushUsed": False,
            "fastForwardOnly": True,
        })
        self.p22 = self.results / m.P22_DEFAULT_NAME
        write_json(self.p22, {
            "schema": "wof-alpha-dynamic-state-coverage-v1",
            "candidateSourceCommit": self.target,
            "packageVersion": self.package,
            "candidateSha256": self.candidate_sha,
            "identity": self.identity,
            "coreAcceptanceSummary": {"status": "OBSERVED_PROVEN"},
            "coverageMatrix": [
                {"name": "P1 movement", "status": "OBSERVED_PROVEN"},
                {"name": "DEATH", "status": "NOT_OBSERVED"},
            ],
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False},
        })
        self.w3 = self.results / "W3_PASS.json"
        write_json(self.w3, {
            "schema": m.W3_SCHEMA,
            "status": "PASS",
            "captureIdentity": self.identity,
        })
        self.feedback = self.root / "LATEST_ALPHA_FEEDBACK.txt"
        self.feedback.write_text(f"status=RUNNING\nalphaLiveCommit={self.target}\ncurrentSha={self.target}\n", encoding="utf-8")
        self.launcher = self.repo / "WOF_ALPHA_TEST.cmd"
        self.post = self.results / m.DEFAULT_POST_CONFIRMATION
        write_json(self.post, {
            "schema": m.POST_ACCEPTANCE_SCHEMA,
            "version": 1,
            "fixtureMode": True,
            "realWofPostPromotionAcceptance": "FIXTURE_ONLY",
            "ownerConfirmation": "PASS",
            "promotedCommit": self.target,
            "managedRepoHead": self.target,
            "packageVersion": self.package,
            "candidateSha256": self.candidate_sha,
            "promotionPlanHash": self.plan_hash,
            "promotionResultSha256": sha(self.promotion_result),
            "identity": self.identity,
            "p22EvidenceSha256": sha(self.p22),
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False},
        })

    def args(self, **updates):
        base = dict(
            repo_root=self.repo,
            candidate_path=self.candidate,
            attestation_path=self.attestation,
            p17_path=self.p17,
            p16_path=self.p16,
            p18_path=self.p18,
            visual_receipt_path=self.visual,
            promotion_plan_path=self.plan,
            promotion_result_path=self.promotion_result,
            observed_alpha_live=self.target,
            remote="origin",
            live_branch="alpha-live",
            managed_repo=self.repo,
            launcher=self.launcher,
            feedback_path=self.feedback,
            p22_path=self.p22,
            w3_path=self.w3,
            post_confirmation_path=self.post,
            observed_at_utc="2026-09-05T00:00:00Z",
        )
        base.update(updates)
        return base


class PostPromotionVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_waiting_w3_live_pass(self):
        raw = copy.deepcopy(self.fx.p17_raw)
        raw["automaticDecision"] = "W3_INCONCLUSIVE"
        raw["w3Qualification"]["status"] = "INCONCLUSIVE"
        raw["w3Qualification"]["canonicalProducerReadiness"]["ready"] = False
        write_json(self.fx.p17, raw)
        with self.assertRaises(m.WaitingError) as ctx:
            m.verify_release(**self.fx.args())
        self.assertEqual(ctx.exception.state, m.WAITING_FOR_W3_LIVE_PASS)

    def test_waiting_owner_visual_pass(self):
        with self.assertRaises(m.WaitingError) as ctx:
            m.verify_release(**self.fx.args(visual_receipt_path=None))
        self.assertEqual(ctx.exception.state, m.WAITING_FOR_OWNER_VISUAL_PASS)

    def test_exact_candidate_promotion_alpha_live_match_waits_for_permanent_channel(self):
        with self.assertRaises(m.WaitingError) as ctx:
            m.verify_release(**self.fx.args(managed_repo=self.fx.root / "missing-live-repo"))
        self.assertEqual(ctx.exception.state, m.WAITING_FOR_PERMANENT_CHANNEL_CONFIRMATION)

    def test_missing_promotion_waits(self):
        with self.assertRaises(m.WaitingError) as ctx:
            m.verify_release(**self.fx.args(promotion_result_path=None))
        self.assertEqual(ctx.exception.state, m.WAITING_FOR_PROMOTION)

    def test_stale_plan_result_rejected(self):
        raw = json.loads(self.fx.promotion_result.read_text(encoding="utf-8"))
        raw["planHash"] = "0" * 64
        write_json(self.fx.promotion_result, raw)
        with self.assertRaises(m.MismatchError):
            m.verify_release(**self.fx.args())

    def test_staging_repo_never_counts_as_permanent(self):
        staging = self.fx.root / "WOF_ALPHA_STAGING" / "fixture"
        staging.parent.mkdir(parents=True)
        subprocess.run(["git", "clone", "-q", str(self.fx.repo), str(staging)], check=True)
        with self.assertRaises(m.MismatchError):
            m.verify_permanent_channel(staging, staging / "WOF_ALPHA_TEST.cmd", self.fx.feedback, self.fx.target, self.fx.package)

    def test_rollback_metadata_consistency(self):
        raw = json.loads(self.fx.plan.read_text(encoding="utf-8"))
        raw["planCore"]["rollback"]["previousCommit"] = self.fx.target
        raw["planHash"] = m._canonical_hash(raw["planCore"])
        write_json(self.fx.plan, raw)
        with self.assertRaises(m.MismatchError):
            m.verify_release(**self.fx.args())

    def test_fixture_confirmation_cannot_reach_final_complete(self):
        with self.assertRaises(m.WaitingError) as ctx:
            m.verify_release(**self.fx.args())
        self.assertEqual(ctx.exception.state, m.WAITING_FOR_POST_PROMOTION_ACCEPTANCE)

    def test_safety_invariant_fail_closed(self):
        raw = json.loads(self.fx.p22.read_text(encoding="utf-8"))
        raw["safety"]["readOnly"] = False
        write_json(self.fx.p22, raw)
        with self.assertRaises(m.MismatchError):
            m.verify_release(**self.fx.args())

    def test_rare_not_observed_gap_is_preserved(self):
        p22 = m.read_p22(self.fx.p22, {"sourceCommit": self.fx.target, "packageVersion": self.fx.package, "candidateSha256": self.fx.candidate_sha}, self.fx.identity)
        self.assertIn("DEATH", p22["coverageGaps"])

    def test_deterministic_hash_excludes_observation_timestamp(self):
        a = m._waiting_output(m.WAITING_FOR_PROMOTION, "promotion missing", "2026-01-01T00:00:00Z")
        b = m._waiting_output(m.WAITING_FOR_PROMOTION, "promotion missing", "2026-02-02T00:00:00Z")
        self.assertEqual(a["verification"]["receiptHash"], b["verification"]["receiptHash"])
        self.assertNotEqual(a["verification"]["observedAtUtc"], b["verification"]["observedAtUtc"])


if __name__ == "__main__":
    unittest.main()
