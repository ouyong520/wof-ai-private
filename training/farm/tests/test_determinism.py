from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from training.farm.adapter import (
    CoreFrameInput,
    RuntimeCapabilityError,
    TrainingFarmAdapter,
)
from training.farm.determinism import (
    DeterminismContractError,
    PROOF_SCOPE_FIXTURE,
    parse_action_sequence,
    run_determinism,
)
from training.farm.fake_backend import DeterministicFakeBackend
from training.farm.identity import build_fixture_runtime_identity


def fixture_steps():
    path = Path(__file__).resolve().parents[1] / "determinism_actions.example.json"
    return parse_action_sequence(json.loads(path.read_text(encoding="utf-8")))


class DivergingBackend(DeterministicFakeBackend):
    def __init__(self):
        self._load_count = 0
        super().__init__()

    def load_state(self, state: bytes) -> None:
        super().load_state(state)
        self._load_count += 1

    def step_frame(self, frame_input: CoreFrameInput) -> None:
        super().step_frame(frame_input)
        if self._load_count >= 2 and self._frame == 4:
            self._ram[31] ^= 0x01


class LoadFailureBackend(DeterministicFakeBackend):
    def load_state(self, state: bytes) -> None:
        raise RuntimeCapabilityError("fixture load failure")


class RoundtripStateMismatchBackend(DeterministicFakeBackend):
    def __init__(self):
        self._loaded = False
        super().__init__()

    def load_state(self, state: bytes) -> None:
        super().load_state(state)
        self._loaded = True

    def save_state(self) -> bytes:
        state = super().save_state()
        if self._loaded:
            return state[:-1] + bytes([state[-1] ^ 0x01])
        return state


class DeterminismTests(unittest.TestCase):
    def test_fixture_replay_passes_and_is_not_real_proof(self):
        steps = fixture_steps()
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            result = run_determinism(
                adapter,
                steps,
                horizon=8,
                repetitions=3,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["reasonCode"], "DETERMINISM_MATCH")
        self.assertFalse(result["realWofProof"])
        self.assertEqual(result["repetitionsCompleted"], 3)
        self.assertEqual(len(result["repetitions"][0]["checkpoints"]), 8)

    def test_exact_first_ram_divergence_is_reported(self):
        steps = fixture_steps()
        with TrainingFarmAdapter(DivergingBackend()) as adapter:
            result = run_determinism(
                adapter,
                steps,
                horizon=8,
                repetitions=3,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["reasonCode"], "DETERMINISM_MISMATCH")
        self.assertEqual(result["firstDivergence"]["kind"], "RAM")
        self.assertEqual(result["firstDivergence"]["frame"], 4)

    def test_identity_change_invalidates_comparison(self):
        steps = fixture_steps()
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            baseline = build_fixture_runtime_identity(adapter)
            calls = {"count": 0}

            def provider():
                calls["count"] += 1
                value = copy.deepcopy(baseline)
                if calls["count"] >= 5:
                    value["farmCandidateSha256"] = "0" * 64
                return value

            result = run_determinism(
                adapter,
                steps,
                horizon=8,
                repetitions=3,
                identity_provider=provider,
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["reasonCode"], "IDENTITY_CHANGED")

    def test_malformed_identity_is_structured_error(self):
        steps = fixture_steps()
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            result = run_determinism(
                adapter,
                steps,
                horizon=8,
                repetitions=2,
                identity_provider=lambda: {"sourceNamespace": "stable-retro-fbneo"},
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["reasonCode"], "INVALID_RUNTIME_IDENTITY")
        self.assertEqual(result["firstDivergence"]["kind"], "IDENTITY")

    def test_load_failure_and_savestate_hash_mismatch_fail_closed(self):
        steps = fixture_steps()
        with TrainingFarmAdapter(LoadFailureBackend()) as adapter:
            result = run_determinism(
                adapter,
                steps,
                horizon=8,
                repetitions=2,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["reasonCode"], "RUNTIME_OPERATION_FAILED")

        with TrainingFarmAdapter(RoundtripStateMismatchBackend()) as adapter:
            result = run_determinism(
                adapter,
                steps,
                horizon=8,
                repetitions=2,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                proof_scope=PROOF_SCOPE_FIXTURE,
            )
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["reasonCode"], "SAVESTATE_HASH_MISMATCH")

    def test_horizon_and_repetition_are_strict(self):
        steps = fixture_steps()
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            provider = lambda: build_fixture_runtime_identity(adapter)
            with self.assertRaises(DeterminismContractError):
                run_determinism(
                    adapter,
                    steps,
                    horizon="8",
                    repetitions=3,
                    identity_provider=provider,
                    proof_scope=PROOF_SCOPE_FIXTURE,
                )
            with self.assertRaises(DeterminismContractError):
                run_determinism(
                    adapter,
                    steps,
                    horizon=8,
                    repetitions=True,
                    identity_provider=provider,
                    proof_scope=PROOF_SCOPE_FIXTURE,
                )

    def test_action_json_rejects_coercible_and_partial_inputs(self):
        base = json.loads(
            (Path(__file__).resolve().parents[1] / "determinism_actions.example.json")
            .read_text(encoding="utf-8")
        )
        bad_player = copy.deepcopy(base)
        bad_player[0]["inputs"][0]["player"] = "0"
        with self.assertRaises(DeterminismContractError):
            parse_action_sequence(bad_player)

        bad_button = copy.deepcopy(base)
        bad_button[0]["inputs"][0]["pressed"] = [True]
        with self.assertRaises(DeterminismContractError):
            parse_action_sequence(bad_button)

        missing_neutral = copy.deepcopy(base)
        missing_neutral[0]["inputs"] = missing_neutral[0]["inputs"][:1]
        with self.assertRaises(DeterminismContractError):
            parse_action_sequence(missing_neutral)

    def test_action_sequence_must_exactly_cover_horizon(self):
        steps = fixture_steps()
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            with self.assertRaises(DeterminismContractError):
                run_determinism(
                    adapter,
                    steps,
                    horizon=9,
                    repetitions=2,
                    identity_provider=lambda: build_fixture_runtime_identity(adapter),
                    proof_scope=PROOF_SCOPE_FIXTURE,
                )


if __name__ == "__main__":
    unittest.main()
