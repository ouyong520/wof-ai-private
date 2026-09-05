from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from final_retry_readiness import (
    BLOCKED,
    DEFAULT_REQUIREMENTS,
    READY,
    evaluate_readiness,
)


class FakeGit:
    def __init__(self, existing: set[str], ancestors: set[tuple[str, str]]):
        self.existing = set(existing)
        self.ancestors = set(ancestors)

    def commit_exists(self, sha: str) -> bool:
        return sha in self.existing

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        return (ancestor, descendant) in self.ancestors


class FinalRetryReadinessTests(unittest.TestCase):
    SOURCE = "f" * 40
    TESTED = {
        requirement.stage_id: f"{index + 1:x}" * 40
        for index, requirement in enumerate(DEFAULT_REQUIREMENTS)
    }

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_json(self, relative: str, value: dict, *, compact: bool = False) -> bytes:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if compact:
            text = json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
        else:
            text = json.dumps(value, indent=2, sort_keys=True) + "\n"
        raw = text.encode("utf-8")
        path.write_bytes(raw)
        return raw

    def _seed_stage(
        self,
        requirement,
        *,
        state: str = "COMPLETE",
        claim_state: str | None = None,
        token: str | None = None,
        canonical_token: str | None = None,
        stage_token: str | None = None,
        include_result: bool = True,
        integration_ready: bool | None = None,
        blocker: dict | None = None,
        alpha_live_moved: bool = False,
    ) -> None:
        stage_id = requirement.stage_id
        tested = self.TESTED[stage_id]
        token = token or f"token-{stage_id}"
        canonical_token = canonical_token or token
        stage_token = stage_token or token
        claim_state = claim_state or state
        if integration_ready is None:
            integration_ready = state == "COMPLETE"

        if include_result:
            self._write_json(
                requirement.result_path,
                {
                    "schema": "wof-alpha-worker-result-v1",
                    "stageId": stage_id,
                    "dedupKey": requirement.dedup_key,
                    "claimToken": token,
                    "state": state,
                    "testedCommit": tested,
                    "integrationReady": integration_ready,
                    "blocker": blocker,
                    "productProof": {
                        "status": "NOT_PROVEN" if state != "COMPLETE" else "PROVEN",
                        "detail": "fixture",
                    },
                    "alphaLiveMoved": alpha_live_moved,
                    "safety": {"alphaLiveMoved": alpha_live_moved},
                },
            )

        self._write_json(
            requirement.canonical_claim_path,
            {
                "schema": "wof-pm-dedup-claim-v2",
                "dedupProtocol": "v2",
                "dedupKey": requirement.dedup_key,
                "effectiveDedupKey": requirement.dedup_key,
                "dedupMode": "exclusive",
                "stageId": stage_id,
                "claimToken": canonical_token,
                "state": claim_state,
                "testedCommit": tested,
                "resultPath": requirement.result_path,
            },
        )
        self._write_json(
            requirement.stage_claim_path,
            {
                "schema": "wof-pm-stage-claim-v2",
                "stageId": stage_id,
                "dedupKey": requirement.dedup_key,
                "effectiveDedupKey": requirement.dedup_key,
                "canonicalClaimPath": requirement.canonical_claim_path,
                "claimToken": stage_token,
                "state": claim_state,
                "testedCommit": tested,
                "resultPath": requirement.result_path,
            },
        )

    def _seed_all_complete(self) -> None:
        for requirement in DEFAULT_REQUIREMENTS:
            self._seed_stage(requirement)

    def _seed_candidate(
        self,
        *,
        source: str | None = None,
        candidate_moved: bool = False,
        manifest_moved: bool = False,
        candidate_sha_override: str | None = None,
        manifest_sha_override: str | None = None,
        required_map: dict[str, str] | None = None,
    ) -> None:
        source = source or self.SOURCE
        package_version = "2026.09.06.fixture"
        candidate_path = "parallel/OWNER_ONECLICK/CANDIDATES/FINAL_CANONICAL/fixture.json"
        manifest_path = (
            "parallel/OWNER_ONECLICK/CANDIDATES/FINAL_CANONICAL/fixture.manifest.json"
        )
        candidate_raw = self._write_json(
            candidate_path,
            {
                "schema": "wof-alpha-final-canonical-candidate-v2-fixture",
                "sourceCommit": source,
                "packageVersion": package_version,
                "alphaLiveMoved": candidate_moved,
                "alphaLivePromoted": False,
            },
            compact=True,
        )
        manifest_raw = self._write_json(
            manifest_path,
            {
                "schema": "wof-alpha-final-canonical-manifest-v1-fixture",
                "sourceCommit": source,
                "packageVersion": package_version,
                "alphaLiveMoved": manifest_moved,
                "promotionPerformed": False,
            },
            compact=True,
        )
        candidate_sha = hashlib.sha256(candidate_raw).hexdigest()
        manifest_sha = hashlib.sha256(manifest_raw).hexdigest()
        self._write_json(
            "parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json",
            {
                "schema": "wof-alpha-latest-final-canonical-candidate-v2-fixture",
                "state": "READY",
                "sourceCommit": source,
                "packageVersion": package_version,
                "candidatePath": candidate_path,
                "candidateSha256": candidate_sha_override or candidate_sha,
                "manifestPath": manifest_path,
                "manifestSha256": manifest_sha_override or manifest_sha,
                "requiredTestedCommits": required_map
                if required_map is not None
                else dict(self.TESTED),
                "alphaLiveMoved": False,
                "alphaLivePromoted": False,
            },
        )

    def _all_good_git(self, *, omit_ancestor_stage: str | None = None) -> FakeGit:
        existing = {self.SOURCE, *self.TESTED.values()}
        ancestors = {
            (tested, self.SOURCE)
            for stage_id, tested in self.TESTED.items()
            if stage_id != omit_ancestor_stage
        }
        return FakeGit(existing, ancestors)

    def _codes(self, result: dict) -> list[str]:
        return [item["code"] for item in result["blockers"]]

    def test_exact_terminal_chain_and_exact_containing_candidate_is_ready(self) -> None:
        self._seed_all_complete()
        self._seed_candidate()
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        self.assertEqual(READY, result["state"])
        self.assertTrue(result["readyForOneBoundedOwnerRetry"])
        self.assertEqual(1, result["ownerRetryBudget"])
        self.assertFalse(result["promotionAuthorized"])
        self.assertFalse(result["alphaLiveMoveAuthorized"])
        self.assertEqual([], result["blockers"])

    def test_p29_p30_complete_but_p31_p32_active_is_blocked_and_progress_cannot_substitute(self) -> None:
        self._seed_stage(DEFAULT_REQUIREMENTS[0])
        self._seed_stage(DEFAULT_REQUIREMENTS[1])
        for requirement in DEFAULT_REQUIREMENTS[2:]:
            self._seed_stage(
                requirement,
                state="ACTIVE",
                claim_state="ACTIVE",
                include_result=False,
                integration_ready=False,
            )
            self._write_json(
                f"parallel/PM/PROGRESS/{requirement.stage_id}_PROGRESS.json",
                {
                    "schema": "wof-alpha-worker-progress-v1",
                    "stageId": requirement.stage_id,
                    "workState": "TERMINAL",
                    "selfCheckState": "PASS",
                },
            )
        self._seed_candidate()
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        self.assertEqual(BLOCKED, result["state"])
        self.assertFalse(result["readyForOneBoundedOwnerRetry"])
        missing = [
            item
            for item in result["blockers"]
            if item["code"] == "MISSING_TERMINAL_RESULT"
        ]
        self.assertEqual(2, len(missing))

    def test_stale_candidate_missing_one_required_tested_commit_is_blocked(self) -> None:
        self._seed_all_complete()
        self._seed_candidate()
        missing_stage = DEFAULT_REQUIREMENTS[-1].stage_id
        result = evaluate_readiness(
            self.root,
            git_probe=self._all_good_git(omit_ancestor_stage=missing_stage),
        )

        self.assertEqual(BLOCKED, result["state"])
        ancestry = [
            item
            for item in result["blockers"]
            if item["code"] == "SOURCE_COMMIT_MISSING_REQUIRED_TESTED_COMMIT"
        ]
        self.assertEqual([missing_stage], [item["stageId"] for item in ancestry])

    def test_claim_token_mismatch_is_blocked(self) -> None:
        self._seed_all_complete()
        target = DEFAULT_REQUIREMENTS[1]
        self._seed_stage(target, canonical_token="wrong-token")
        self._seed_candidate()
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        self.assertIn("CLAIM_TOKEN_MISMATCH", self._codes(result))
        self.assertFalse(result["readyForOneBoundedOwnerRetry"])

    def test_non_complete_claim_state_is_blocked(self) -> None:
        self._seed_all_complete()
        target = DEFAULT_REQUIREMENTS[2]
        self._seed_stage(target, state="COMPLETE", claim_state="ACTIVE")
        self._seed_candidate()
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        self.assertIn("CLAIM_STATE_MISMATCH", self._codes(result))
        self.assertFalse(result["readyForOneBoundedOwnerRetry"])

    def test_p32_blocked_live_dependency_metadata_is_preserved_not_rewritten_to_pass(self) -> None:
        self._seed_all_complete()
        target = DEFAULT_REQUIREMENTS[-1]
        blocker = {
            "code": "NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN",
            "detail": "missing direct renderer causal edge",
            "ownerRequired": False,
            "pmRequired": True,
        }
        self._seed_stage(
            target,
            state="BLOCKED",
            claim_state="BLOCKED",
            integration_ready=False,
            blocker=blocker,
        )
        self._seed_candidate()
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        stage = result["stages"][target.stage_id]
        self.assertEqual(BLOCKED, result["state"])
        self.assertEqual("BLOCKED", stage["terminalState"])
        self.assertEqual(blocker, stage["terminalBlocker"])
        self.assertFalse(stage["accepted"])
        self.assertIn("UPSTREAM_TERMINAL_STATE_NOT_ACCEPTED", self._codes(result))

    def test_alpha_live_moved_true_anywhere_before_retry_is_blocked(self) -> None:
        self._seed_all_complete()
        self._seed_candidate(manifest_moved=True)
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        self.assertEqual(BLOCKED, result["state"])
        self.assertIn("ALPHA_LIVE_MOVED_BEFORE_RETRY", self._codes(result))

    def test_manifest_hash_mismatch_is_blocked(self) -> None:
        self._seed_all_complete()
        self._seed_candidate(manifest_sha_override="0" * 64)
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        self.assertEqual(BLOCKED, result["state"])
        self.assertIn("MANIFEST_SHA256_MISMATCH", self._codes(result))

    def test_candidate_hash_mismatch_is_blocked(self) -> None:
        self._seed_all_complete()
        self._seed_candidate(candidate_sha_override="0" * 64)
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        self.assertEqual(BLOCKED, result["state"])
        self.assertIn("CANDIDATE_SHA256_MISMATCH", self._codes(result))

    def test_candidate_required_tested_commit_pin_mismatch_is_blocked(self) -> None:
        self._seed_all_complete()
        required_map = dict(self.TESTED)
        target = DEFAULT_REQUIREMENTS[0].stage_id
        required_map[target] = "a" * 40
        self._seed_candidate(required_map=required_map)
        result = evaluate_readiness(self.root, git_probe=self._all_good_git())

        self.assertEqual(BLOCKED, result["state"])
        self.assertIn(
            "CANDIDATE_REQUIRED_TESTED_COMMIT_MISMATCH", self._codes(result)
        )


if __name__ == "__main__":
    unittest.main()
