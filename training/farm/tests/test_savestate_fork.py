from __future__ import annotations

import copy
import json
import unittest

from training.farm.adapter import CoreFrameInput, TrainingFarmAdapter
from training.farm.fake_backend import DeterministicFakeBackend
from training.farm.identity import build_fixture_runtime_identity
from training.farm.savestate_fork import (
    ForkContractError,
    PROOF_SCOPE_FIXTURE,
    checkpoint_frames,
    fork_plan_authority_sha256,
    parse_fork_plan,
    run_fork_set,
)


def neutral_inputs():
    return [
        {"player": 0, "pressed": []},
        {"player": 1, "pressed": []},
        {"player": 2, "pressed": []},
        {"player": 3, "pressed": []},
    ]


def branch(branch_id: str, button: int | None = None, horizon: int = 8):
    inputs = neutral_inputs()
    if button is not None:
        inputs[0]["pressed"] = [button]
    return {
        "branchId": branch_id,
        "horizonFrames": horizon,
        "actions": [{"frames": horizon, "inputs": inputs}],
        "metadata": {"label": f"human-{branch_id}"},
    }


def plan_value(branches=None):
    return {
        "schema": "wof-training-farm-savestate-fork-plan-v1",
        "forkSetId": "fixture-fork-set",
        "root": {"rootId": "root-a", "expectedSavestateSha256": None},
        "repetitions": 3,
        "branches": branches or [branch("branch-b", 1), branch("branch-a", 0), branch("branch-neutral")],
    }


class DivergingBackend(DeterministicFakeBackend):
    def __init__(self):
        self._load_count = 0
        super().__init__()

    def load_state(self, state: bytes) -> None:
        super().load_state(state)
        self._load_count += 1

    def step_frame(self, frame_input: CoreFrameInput) -> None:
        super().step_frame(frame_input)
        self._ram[31] = self._load_count & 0xFF


class IdentityDriftBackend(DeterministicFakeBackend):
    def __init__(self):
        self._drifted = False
        super().__init__()

    def step_frame(self, frame_input: CoreFrameInput) -> None:
        super().step_frame(frame_input)
        self._drifted = True

    def runtime_identity_components(self):
        value = super().runtime_identity_components()
        if self._drifted:
            value["coreName"] = "fixture-drifted"
        return value


class ForkTests(unittest.TestCase):
    def test_plan_is_strict_and_order_independent(self):
        raw = plan_value()
        parsed = parse_fork_plan(raw)
        self.assertEqual([b.branch_id for b in parsed.branches], ["branch-a", "branch-b", "branch-neutral"])
        reversed_raw = copy.deepcopy(raw)
        reversed_raw["branches"] = list(reversed(reversed_raw["branches"]))
        self.assertEqual(
            fork_plan_authority_sha256(parsed),
            fork_plan_authority_sha256(parse_fork_plan(reversed_raw)),
        )

        duplicate = copy.deepcopy(raw)
        duplicate["branches"][1]["branchId"] = duplicate["branches"][0]["branchId"]
        with self.assertRaises(ForkContractError):
            parse_fork_plan(duplicate)

        coercible = copy.deepcopy(raw)
        coercible["branches"][0]["horizonFrames"] = "8"
        with self.assertRaises(ForkContractError):
            parse_fork_plan(coercible)

        mismatch = copy.deepcopy(raw)
        mismatch["branches"][0]["horizonFrames"] = 9
        with self.assertRaises(ForkContractError):
            parse_fork_plan(mismatch)

        bad_player = copy.deepcopy(raw)
        bad_player["branches"][0]["actions"][0]["inputs"][0]["player"] = "0"
        with self.assertRaises(ForkContractError):
            parse_fork_plan(bad_player)

        bad_button = copy.deepcopy(raw)
        bad_button["branches"][0]["actions"][0]["inputs"][0]["pressed"] = [True]
        with self.assertRaises(ForkContractError):
            parse_fork_plan(bad_button)

    def test_fixture_fork_is_deterministic_and_isolated(self):
        plan = parse_fork_plan(plan_value())
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            result = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["reasonCode"], "FORK_SET_DETERMINISTIC")
        self.assertTrue(result["deterministic"])
        self.assertFalse(result["realWofProof"])
        self.assertEqual(result["branchesCompleted"], 3)
        self.assertEqual(result["rootAuthority"]["sourceNamespace"], "stable-retro-fbneo")
        self.assertEqual(result["rootAuthority"]["rootLogicalFrame"], 0)
        self.assertEqual(result["rootAuthority"]["inputIsolationMode"], "explicit-all-player-mask-every-frame")
        for item in result["branches"]:
            self.assertTrue(item["deterministic"])
            self.assertEqual(item["repetitionsCompleted"], 3)
            fingerprints = {outcome["outcomeFingerprintSha256"] for outcome in item["outcomes"]}
            self.assertEqual(len(fingerprints), 1)
            for outcome in item["outcomes"]:
                self.assertEqual(outcome["rootSavestateSha256"], result["rootAuthority"]["rootSavestateSha256"])
                self.assertEqual(outcome["restoredRamSha256"], result["rootAuthority"]["rootRamSha256"])

        finals = {item["branchId"]: item["outcomes"][0]["finalRamSha256"] for item in result["branches"]}
        self.assertNotEqual(finals["branch-a"], finals["branch-neutral"])
        self.assertNotEqual(finals["branch-b"], finals["branch-neutral"])

        single = parse_fork_plan(plan_value([branch("branch-neutral")]))
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            standalone = run_fork_set(
                adapter,
                single,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(
            finals["branch-neutral"],
            standalone["branches"][0]["outcomes"][0]["finalRamSha256"],
        )

    def test_nondeterministic_branch_fails_with_first_checkpoint(self):
        plan = parse_fork_plan(plan_value([branch("branch-a", 0)]))
        with TrainingFarmAdapter(DivergingBackend()) as adapter:
            result = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "FAIL")
        item = result["branches"][0]
        self.assertEqual(item["status"], "FAIL")
        self.assertEqual(item["reasonCode"], "BRANCH_NON_DETERMINISTIC")
        self.assertEqual(item["firstDivergence"]["kind"], "RAM_CHECKPOINT")
        self.assertEqual(item["firstDivergence"]["frame"], 1)

    def test_runtime_identity_drift_cannot_pass(self):
        plan = parse_fork_plan(plan_value([branch("branch-a", 0)]))
        with TrainingFarmAdapter(IdentityDriftBackend()) as adapter:
            result = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["branches"][0]["status"], "ERROR")
        self.assertEqual(result["branches"][0]["reasonCode"], "BRANCH_EXECUTION_FAILED")

    def test_partial_result_resumes_only_matching_authority(self):
        plan = parse_fork_plan(plan_value([branch("branch-a", 0), branch("branch-b", 1)]))
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            partial = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
                max_new_branches=1,
            )
        self.assertEqual(partial["status"], "PARTIAL")
        self.assertEqual(partial["reasonCode"], "EXECUTION_LIMIT_REACHED")
        self.assertEqual(partial["branchesCompleted"], 1)

        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            resumed = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
                resume_result=partial,
            )
        self.assertEqual(resumed["status"], "PASS")
        self.assertEqual(resumed["resume"]["acceptedBranchIds"], ["branch-a"])
        by_id = {item["branchId"]: item for item in resumed["branches"]}
        self.assertTrue(by_id["branch-a"]["reusedFromResume"])
        self.assertFalse(by_id["branch-b"]["reusedFromResume"])

        tampered = copy.deepcopy(partial)
        tampered["branches"][0]["actionSequenceSha256"] = "0" * 64
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            rejected = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
                resume_result=tampered,
            )
        self.assertEqual(rejected["status"], "ERROR")
        self.assertEqual(rejected["reasonCode"], "INVALID_RESUME_RESULT")

        extra_field = copy.deepcopy(partial)
        extra_field["notInPublishedSchema"] = True
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            rejected_extra = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
                resume_result=extra_field,
            )
        self.assertEqual(rejected_extra["status"], "ERROR")
        self.assertEqual(rejected_extra["reasonCode"], "INVALID_RESUME_RESULT")

        tampered_root = copy.deepcopy(partial)
        tampered_root["rootAuthority"]["runtimeIdentitySha256"] = "0" * 64
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            rejected_root = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
                resume_result=tampered_root,
            )
        self.assertEqual(rejected_root["status"], "ERROR")
        self.assertEqual(rejected_root["reasonCode"], "INVALID_RESUME_RESULT")

        duplicate_nonpass = copy.deepcopy(partial)
        failed_row = duplicate_nonpass["branches"][0]
        failed_row["status"] = "FAIL"
        failed_row["reasonCode"] = "BRANCH_NON_DETERMINISTIC"
        failed_row["message"] = "fixture malformed duplicate row"
        failed_row["deterministic"] = False
        duplicate_nonpass["branches"] = [failed_row, copy.deepcopy(failed_row)]
        duplicate_nonpass["branchesAttempted"] = 2
        duplicate_nonpass["branchesCompleted"] = 0
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            rejected_duplicate = run_fork_set(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
                resume_result=duplicate_nonpass,
            )
        self.assertEqual(rejected_duplicate["status"], "ERROR")
        self.assertEqual(rejected_duplicate["reasonCode"], "INVALID_RESUME_RESULT")

        changed = copy.deepcopy(plan_value([branch("branch-a", 2), branch("branch-b", 1)]))
        changed_plan = parse_fork_plan(changed)
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            rejected_plan = run_fork_set(
                adapter,
                changed_plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
                resume_result=partial,
            )
        self.assertEqual(rejected_plan["status"], "ERROR")
        self.assertEqual(rejected_plan["reasonCode"], "INVALID_RESUME_RESULT")

    def test_checkpoint_set_is_bounded_and_contains_final_frame(self):
        plan = parse_fork_plan(plan_value([branch("long", 0, horizon=1000)]))
        frames = checkpoint_frames(plan.branches[0])
        self.assertLessEqual(len(frames), 64)
        self.assertEqual(frames[-1], 1000)
        self.assertEqual(tuple(sorted(set(frames))), frames)


if __name__ == "__main__":
    unittest.main()
