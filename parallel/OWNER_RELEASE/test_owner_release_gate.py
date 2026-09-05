from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import owner_release_gate as gate


IDENTITY = {
    "worldSha256": "1" * 64,
    "pageTargetId": "page-1",
    "workerTargetId": "worker-1",
    "authorityKey": "auth-1",
    "runtimeEpoch": "runtime-1",
    "rendererEpoch": "renderer-1",
    "rendererAuthority": "render-auth-1",
}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(repo: Path, *args: str) -> str:
    cp = subprocess.run(["git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return cp.stdout.strip()


class GateFixture:
    def __init__(self, root: Path, source_commit: str = "a" * 40):
        self.root = root
        self.repo = root / "repo"
        self.repo.mkdir(parents=True, exist_ok=True)
        self.out = root / "out"
        self.out.mkdir()
        self.candidate = self.repo / "parallel/OWNER_ONECLICK/CANDIDATES/final.json"
        self.attestation = self.repo / "parallel/OWNER_ONECLICK/CANDIDATES/final.attestation.json"
        self.bundle = self.out / "ALPHA_FINAL_ACCEPTANCE_BUNDLE.json"
        candidate = {
            "schema": "wof-owner-oneclick-package-v1",
            "packageVersion": "alpha-v1-final",
            "sourceCommit": source_commit,
            "components": {"canonicalProductConvergence": {"alphaLivePromoted": False, "legacySpatialFallback": False}},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False},
        }
        write_json(self.candidate, candidate)
        csha = gate._sha256_file(self.candidate)
        attestation = {
            "schema": "wof-alpha-final-canonical-candidate-attestation-v1",
            "version": 1,
            "sourceCommit": source_commit,
            "packageVersion": "alpha-v1-final",
            "candidateManifestPath": "parallel/OWNER_ONECLICK/CANDIDATES/final.json",
            "candidateManifestSha256": csha,
            "w3LiveQualification": "NOT_RUN",
            "ownerVisualAcceptance": "NOT_RUN",
            "alphaLivePromoted": False,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False},
        }
        write_json(self.attestation, attestation)
        bundle = {
            "schema": gate.P17_BUNDLE_SCHEMA,
            "version": 1,
            "generatedAtUtc": "2026-09-05T00:00:00Z",
            "candidate": {"sourceCommit": source_commit, "packageVersion": "alpha-v1-final", "contentSha256": csha},
            "w3Qualification": {"status": "PASS", "identity": {k: IDENTITY[k] for k in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch")}, "canonicalProducerReadiness": {"ready": True, "rendererSource": {"proven": True}}},
            "p16CanonicalRuntime": {"canonicalState": "HUD_INGEST_ACCEPTED", "visibleProof": "NOT_PROVEN", "identity": dict(IDENTITY)},
            "p18DrawEvidence": {"evidenceState": "CANONICAL_DRAW_ACKNOWLEDGED", "visibleProof": "NOT_PROVEN", "identity": {k: IDENTITY[k] for k in ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch", "rendererAuthority")}},
            "identityConsistency": {"consistent": True, "mismatches": []},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedRendererObjectAddress": False, "alphaLiveMoved": False},
            "automaticDecision": gate.P17_READY,
            "visibleProof": "NOT_PROVEN",
            "ownerVisualConfirmationRequired": True,
        }
        write_json(self.bundle, bundle)

    def preflight(self):
        return gate.visual_preflight(self.repo, self.candidate, self.attestation, self.bundle)

    def receipt(self, *, fixture_mode: bool = False, answer: str = "YES") -> Path:
        _, path = gate.record_visual_receipt(self.preflight(), answer=answer, output_dir=self.out, fixture_mode=fixture_mode, recorded_at_utc="2026-09-05T00:00:01Z")
        return path


class OwnerReleaseGateTests(unittest.TestCase):
    def test_visual_pass_fail_waiting_and_fixture_is_ineligible(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            good = GateFixture(root / "good")
            self.assertEqual(good.preflight()["state"], gate.VISUAL_READY)
            receipt, _ = gate.record_visual_receipt(good.preflight(), answer="YES", output_dir=good.out, recorded_at_utc="2026-09-05T00:00:01Z")
            self.assertEqual(receipt["ownerVisualVerdict"], "PASS")
            self.assertTrue(receipt["promotionEligible"])

            fail = GateFixture(root / "fail")
            receipt, _ = gate.record_visual_receipt(fail.preflight(), answer="NO", output_dir=fail.out, recorded_at_utc="2026-09-05T00:00:01Z")
            self.assertEqual(receipt["ownerVisualVerdict"], "FAIL")
            self.assertFalse(receipt["promotionEligible"])

            waiting = GateFixture(root / "waiting")
            raw = json.loads(waiting.bundle.read_text(encoding="utf-8"))
            raw["automaticDecision"] = "W3_INCONCLUSIVE"
            raw["w3Qualification"]["status"] = "INCONCLUSIVE"
            write_json(waiting.bundle, raw)
            self.assertEqual(waiting.preflight()["state"], gate.VISUAL_WAITING)

            fixture = GateFixture(root / "fixture")
            path = fixture.receipt(fixture_mode=True)
            candidate = gate.read_candidate(fixture.repo, fixture.candidate)
            att = gate.read_attestation(fixture.repo, fixture.attestation, candidate)
            _, _, bundle = gate.inspect_bundle(fixture.bundle, candidate)
            with self.assertRaisesRegex(gate.GateError, "fixture/non-eligible"):
                gate.read_receipt(path, candidate=candidate, attestation=att, bundle=bundle)

    def test_candidate_bundle_receipt_mismatch_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            fx = GateFixture(Path(td))
            receipt = fx.receipt()
            raw = json.loads(receipt.read_text(encoding="utf-8"))
            raw["acceptanceBundleSha256"] = "0" * 64
            write_json(receipt, raw)
            candidate = gate.read_candidate(fx.repo, fx.candidate)
            att = gate.read_attestation(fx.repo, fx.attestation, candidate)
            _, _, bundle = gate.inspect_bundle(fx.bundle, candidate)
            with self.assertRaisesRegex(gate.GateError, "receipt mismatch"):
                gate.read_receipt(receipt, candidate=candidate, attestation=att, bundle=bundle)

    def _make_git_fixture(self, root: Path) -> tuple[Path, Path, str, str]:
        repo = root / "repo"
        bare = root / "remote.git"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "p20@example.invalid")
        git(repo, "config", "user.name", "P20 Fixture")
        for rel in gate.REQUIRED_W1_FILES:
            p = repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"fixture {rel}\n", encoding="utf-8")
        (repo / "payload.txt").write_text("A\n", encoding="utf-8")
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "A")
        a = git(repo, "rev-parse", "HEAD")
        (repo / "payload.txt").write_text("B\n", encoding="utf-8")
        git(repo, "commit", "-qam", "B")
        b = git(repo, "rev-parse", "HEAD")
        subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
        git(repo, "push", "-q", str(bare), f"{a}:refs/heads/alpha-live")
        return repo, bare, a, b

    def _artifacts_for_repo(self, root: Path, repo: Path, target: str) -> tuple[Path, Path, Path, Path, Path]:
        out = root / "evidence"
        out.mkdir(parents=True, exist_ok=True)
        candidate = repo / "parallel/OWNER_ONECLICK/CANDIDATES/final.json"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        write_json(candidate, {
            "schema": "wof-owner-oneclick-package-v1", "packageVersion": "git-final", "sourceCommit": target,
            "components": {"canonicalProductConvergence": {"alphaLivePromoted": False, "legacySpatialFallback": False}},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False},
        })
        csha = gate._sha256_file(candidate)
        att = repo / "parallel/OWNER_ONECLICK/CANDIDATES/final.attestation.json"
        write_json(att, {
            "schema": "wof-alpha-final-canonical-candidate-attestation-v1", "version": 1, "sourceCommit": target,
            "packageVersion": "git-final", "candidateManifestPath": "parallel/OWNER_ONECLICK/CANDIDATES/final.json",
            "candidateManifestSha256": csha, "ownerVisualAcceptance": "NOT_RUN", "w3LiveQualification": "NOT_RUN", "alphaLivePromoted": False,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False},
        })
        bundle = out / "ALPHA_FINAL_ACCEPTANCE_BUNDLE.json"
        write_json(bundle, {
            "schema": gate.P17_BUNDLE_SCHEMA, "version": 1, "candidate": {"sourceCommit": target, "packageVersion": "git-final", "contentSha256": csha},
            "w3Qualification": {"status": "PASS", "identity": {k: IDENTITY[k] for k in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch")}, "canonicalProducerReadiness": {"ready": True, "rendererSource": {"proven": True}}},
            "p16CanonicalRuntime": {"canonicalState": "HUD_INGEST_ACCEPTED", "visibleProof": "NOT_PROVEN", "identity": dict(IDENTITY)},
            "p18DrawEvidence": {"evidenceState": "CANONICAL_DRAW_ACKNOWLEDGED", "visibleProof": "NOT_PROVEN", "identity": {k: IDENTITY[k] for k in ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch", "rendererAuthority")}},
            "identityConsistency": {"consistent": True, "mismatches": []},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedRendererObjectAddress": False, "alphaLiveMoved": False},
            "automaticDecision": gate.P17_READY, "visibleProof": "NOT_PROVEN", "ownerVisualConfirmationRequired": True,
        })
        pre = gate.visual_preflight(repo, candidate, att, bundle)
        _, receipt = gate.record_visual_receipt(pre, answer="YES", output_dir=out, fixture_mode=False, recorded_at_utc="2026-09-05T00:00:01Z")
        return candidate, att, bundle, receipt, out

    def test_deterministic_plan_hash_and_required_w1_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, bare, _, target = self._make_git_fixture(root)
            candidate, att, bundle, receipt, _ = self._artifacts_for_repo(root, repo, target)
            p1 = gate.build_promotion_plan(repo, candidate_path=candidate, attestation_path=att, bundle_path=bundle, receipt_path=receipt, remote=str(bare), prepared_at_utc="2026-09-05T00:00:02Z")
            p2 = gate.build_promotion_plan(repo, candidate_path=candidate, attestation_path=att, bundle_path=bundle, receipt_path=receipt, remote=str(bare), prepared_at_utc="2026-09-05T00:09:59Z")
            self.assertEqual(p1["planHash"], p2["planHash"])
            self.assertNotEqual(p1["preparedAtUtc"], p2["preparedAtUtc"])

            git(repo, "rm", "-q", gate.REQUIRED_W1_FILES[0])
            git(repo, "commit", "-qm", "remove required")
            broken = git(repo, "rev-parse", "HEAD")
            c2, a2, b2, r2, _ = self._artifacts_for_repo(root / "broken", repo, broken)
            with self.assertRaisesRegex(gate.GateError, "missing W1"):
                gate.build_promotion_plan(repo, candidate_path=c2, attestation_path=a2, bundle_path=b2, receipt_path=r2, remote=str(bare))

    def test_local_bare_fast_forward_apply_and_stale_cas(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, bare, a, b = self._make_git_fixture(root)
            candidate, att, bundle, receipt, out = self._artifacts_for_repo(root, repo, b)
            plan = gate.build_promotion_plan(repo, candidate_path=candidate, attestation_path=att, bundle_path=bundle, receipt_path=receipt, remote=str(bare), prepared_at_utc="2026-09-05T00:00:02Z")
            plan_path = gate.write_plan(plan, out)
            dry = gate.apply_promotion_plan(repo, plan_path=plan_path, confirm_plan_hash=plan["planHash"], execute=False)
            self.assertEqual(dry["state"], "DRY_RUN_READY")
            self.assertFalse(dry["alphaLiveMoved"])
            result = gate.apply_promotion_plan(repo, plan_path=plan_path, confirm_plan_hash=plan["planHash"], execute=True, output_dir=out)
            self.assertEqual(result["state"], "PROMOTED")
            self.assertFalse(result["forcePushUsed"])
            self.assertEqual(gate.observe_remote_ref(repo, str(bare), "alpha-live"), b)

            (repo / "payload.txt").write_text("C\n", encoding="utf-8")
            git(repo, "commit", "-qam", "C")
            c = git(repo, "rev-parse", "HEAD")
            c_candidate, c_att, c_bundle, c_receipt, c_out = self._artifacts_for_repo(root / "c", repo, c)
            c_plan = gate.build_promotion_plan(repo, candidate_path=c_candidate, attestation_path=c_att, bundle_path=c_bundle, receipt_path=c_receipt, remote=str(bare), prepared_at_utc="2026-09-05T00:00:03Z")
            c_plan_path = gate.write_plan(c_plan, c_out)
            git(repo, "checkout", "-qb", "other", b)
            (repo / "other.txt").write_text("D\n", encoding="utf-8")
            git(repo, "add", "other.txt")
            git(repo, "commit", "-qm", "D")
            d = git(repo, "rev-parse", "HEAD")
            git(repo, "push", "-q", str(bare), f"{d}:refs/heads/alpha-live")
            with self.assertRaisesRegex(gate.GateError, "CAS rejection"):
                gate.apply_promotion_plan(repo, plan_path=c_plan_path, confirm_plan_hash=c_plan["planHash"], execute=True, output_dir=c_out)

    def test_non_fast_forward_and_no_force_contract(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, bare, a, b = self._make_git_fixture(root)
            git(repo, "push", "-q", str(bare), f"{b}:refs/heads/alpha-live")
            git(repo, "checkout", "-qb", "side", a)
            (repo / "side.txt").write_text("side\n", encoding="utf-8")
            git(repo, "add", "side.txt")
            git(repo, "commit", "-qm", "side")
            side = git(repo, "rev-parse", "HEAD")
            candidate, att, bundle, receipt, _ = self._artifacts_for_repo(root / "sidefx", repo, side)
            with self.assertRaisesRegex(gate.GateError, "not a fast-forward descendant"):
                gate.build_promotion_plan(repo, candidate_path=candidate, attestation_path=att, bundle_path=bundle, receipt_path=receipt, remote=str(bare))
            with self.assertRaises(gate.GateError):
                gate._assert_no_force_push_args(["push", "--force", "origin", "x:y"])
            with self.assertRaises(gate.GateError):
                gate._assert_no_force_push_args(["push", "origin", "+x:y"])
            gate._assert_no_force_push_args(["push", "--porcelain", "origin", "x:y"])


if __name__ == "__main__":
    unittest.main()
