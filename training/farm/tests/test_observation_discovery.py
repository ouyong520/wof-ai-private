from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from training.farm.adapter import (
    RamBlockSnapshot,
    RuntimeCapabilityError,
    TrainingFarmAdapter,
)
from training.farm.determinism import (
    PROOF_SCOPE_REAL,
    RESULT_SCHEMA as R0_2_RESULT_SCHEMA,
    action_sequence_sha256,
    canonical_action_payload,
    parse_action_sequence,
)
from training.farm.fake_backend import DeterministicFakeBackend
from training.farm.identity import (
    PINNED_STABLE_RETRO,
    build_fixture_runtime_identity,
    runtime_identity_sha256,
    validate_runtime_identity,
)
from training.farm.observation_discovery import (
    AUTHORITY_FIXTURE,
    ObservationContractError,
    build_memory_layout_identity,
    evaluate_r02_proof_gate,
    parse_observation_plan,
    run_observation_discovery,
)


def fixture_plan_raw() -> dict[str, object]:
    path = Path(__file__).resolve().parents[1] / "observation_plan.example.json"
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_plan():
    return parse_observation_plan(fixture_plan_raw())


class OverlapBackend(DeterministicFakeBackend):
    def read_ram_blocks(self) -> tuple[RamBlockSnapshot, ...]:
        blocks = super().read_ram_blocks()
        return (
            RamBlockSnapshot(blocks[0].base_address, blocks[0].data),
            RamBlockSnapshot(blocks[0].base_address + 8, blocks[1].data),
        )


class LayoutDriftBackend(DeterministicFakeBackend):
    def __init__(self):
        self._loads = 0
        super().__init__()

    def load_state(self, state: bytes) -> None:
        super().load_state(state)
        self._loads += 1

    def read_ram_blocks(self) -> tuple[RamBlockSnapshot, ...]:
        blocks = super().read_ram_blocks()
        if self._loads:
            return (
                blocks[0],
                RamBlockSnapshot(blocks[1].base_address + 0x100, blocks[1].data),
            )
        return blocks


def synthetic_real_identity(adapter: TrainingFarmAdapter) -> dict[str, object]:
    identity = build_fixture_runtime_identity(adapter)
    identity["runtimeKind"] = "real-wof"
    identity["stableRetroVersion"] = PINNED_STABLE_RETRO
    identity["romIdentityKind"] = "sha256-external-rom"
    identity["romSha256"] = "1" * 64
    backend = dict(identity["backend"])
    backend["backendName"] = "SyntheticRealBackendForTest"
    backend["coreName"] = "FBNeo"
    identity["backend"] = backend
    return validate_runtime_identity(identity, require_real_rom=True)


def synthetic_r02_pass(runtime_identity: dict[str, object]) -> dict[str, object]:
    raw_actions = [
        {
            "frames": 1,
            "inputs": [
                {"player": 0, "pressed": []},
                {"player": 1, "pressed": []},
                {"player": 2, "pressed": []},
                {"player": 3, "pressed": []},
            ],
        }
    ]
    steps = parse_action_sequence(raw_actions)
    action_sha = action_sequence_sha256(steps)
    runtime_sha = runtime_identity_sha256(runtime_identity, require_real_rom=True)
    checkpoint = {"frame": 1, "actionStep": 0, "ramSha256": "2" * 64}
    repetitions = [
        {
            "index": index,
            "framesExecuted": 1,
            "restoredRamSha256": "3" * 64,
            "roundtripStateSha256": "4" * 64,
            "finalRamSha256": "2" * 64,
            "checkpoints": [dict(checkpoint)],
        }
        for index in range(2)
    ]
    return {
        "schema": R0_2_RESULT_SCHEMA,
        "runId": "a" * 32,
        "status": "PASS",
        "reasonCode": "DETERMINISM_MATCH",
        "message": "test-only real-shaped proof",
        "proofScope": PROOF_SCOPE_REAL,
        "realWofProof": True,
        "sourceNamespace": "stable-retro-fbneo",
        "repetitionsRequired": 2,
        "repetitionsCompleted": 2,
        "horizonFrames": 1,
        "actionSequence": canonical_action_payload(steps),
        "actionSequenceSha256": action_sha,
        "runtimeIdentity": runtime_identity,
        "runtimeIdentitySha256": runtime_sha,
        "startStateSha256": "4" * 64,
        "startRamSha256": "3" * 64,
        "repetitions": repetitions,
        "firstDivergence": None,
    }


class ObservationDiscoveryTests(unittest.TestCase):
    def test_address_aware_layout_is_stable_and_overlap_rejected(self):
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            adapter.reset()
            blocks = adapter.read_ram_blocks()
            self.assertEqual([block.base_address for block in blocks], [0x1000, 0x2000])
            self.assertEqual([block.length for block in blocks], [16, 16])
            identity = build_fixture_runtime_identity(adapter)
            first = build_memory_layout_identity(identity, blocks, require_real=False)
            second = build_memory_layout_identity(
                identity, adapter.read_ram_blocks(), require_real=False
            )
            self.assertEqual(first, second)
            self.assertEqual(first["sourceNamespace"], "stable-retro-fbneo")

        with TrainingFarmAdapter(OverlapBackend()) as adapter:
            adapter.reset()
            with self.assertRaises(RuntimeCapabilityError):
                adapter.read_ram_blocks()

    def test_plan_rejects_coercible_horizon_checkpoint_and_player(self):
        raw = fixture_plan_raw()
        bad = copy.deepcopy(raw)
        bad["horizonFrames"] = "4"
        with self.assertRaises(ObservationContractError):
            parse_observation_plan(bad)

        bad = copy.deepcopy(raw)
        bad["captureFrames"] = [0, 2, 1, 4]
        with self.assertRaises(ObservationContractError):
            parse_observation_plan(bad)

        bad = copy.deepcopy(raw)
        bad["baselineActions"][0]["inputs"][0]["player"] = True
        with self.assertRaises(ObservationContractError):
            parse_observation_plan(bad)

    def test_controlled_fixture_capture_ranks_synthetic_candidate(self):
        plan = fixture_plan()
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            result = run_observation_discovery(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                real_runtime=False,
            )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["reasonCode"], "IMPLEMENTATION_FIXTURE_PASS")
        self.assertEqual(result["authorityClassification"], AUTHORITY_FIXTURE)
        self.assertFalse(result["semanticMappingUnlocked"])
        self.assertGreater(result["candidateCountTotal"], 0)
        top = result["rankedCandidateChanges"][0]
        self.assertEqual(top["blockBaseAddress"], 0x1000)
        self.assertEqual(top["offsetWithinBlock"], 8)
        self.assertEqual(top["sourceNativeAddress"], 0x1008)
        self.assertEqual(top["widthBytes"], 1)
        self.assertFalse(top["changedInBaselineControl"])

    def test_layout_drift_fails_closed(self):
        plan = fixture_plan()
        with TrainingFarmAdapter(LayoutDriftBackend()) as adapter:
            result = run_observation_discovery(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                real_runtime=False,
            )
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["reasonCode"], "OBSERVATION_DISCOVERY_FAILED")
        self.assertFalse(result["semanticMappingUnlocked"])

    def test_r02_gate_is_strict_and_allows_only_process_id_cross_process_change(self):
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            current = synthetic_real_identity(adapter)
            proof_identity = copy.deepcopy(current)
            proof_identity["processId"] = current["processId"] + 1
            proof = synthetic_r02_pass(proof_identity)
            accepted = evaluate_r02_proof_gate(proof, current)
            self.assertTrue(accepted["accepted"])
            self.assertEqual(accepted["reasonCode"], "R0_2_PROOF_ACCEPTED")

            wrong_rom = copy.deepcopy(proof)
            wrong_runtime = copy.deepcopy(proof_identity)
            wrong_runtime["romSha256"] = "9" * 64
            wrong_rom["runtimeIdentity"] = wrong_runtime
            wrong_rom["runtimeIdentitySha256"] = runtime_identity_sha256(
                wrong_runtime, require_real_rom=True
            )
            rejected = evaluate_r02_proof_gate(wrong_rom, current)
            self.assertFalse(rejected["accepted"])
            self.assertEqual(rejected["reasonCode"], "R0_2_PROOF_IDENTITY_MISMATCH")

            fixture_proof = copy.deepcopy(proof)
            fixture_proof["proofScope"] = "IMPLEMENTATION_FIXTURE"
            fixture_proof["realWofProof"] = False
            rejected = evaluate_r02_proof_gate(fixture_proof, current)
            self.assertFalse(rejected["accepted"])
            self.assertEqual(rejected["reasonCode"], "R0_2_PROOF_INVALID")

    def test_fixture_cannot_masquerade_as_real_even_with_test_only_proof(self):
        plan = fixture_plan()
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            real_identity = synthetic_real_identity(adapter)
            proof = synthetic_r02_pass(real_identity)
            result = run_observation_discovery(
                adapter,
                plan,
                identity_provider=lambda: build_fixture_runtime_identity(adapter),
                real_runtime=False,
                r02_proof=proof,
            )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["authorityClassification"], AUTHORITY_FIXTURE)
        self.assertFalse(result["semanticMappingUnlocked"])
        self.assertFalse(result["proofGate"]["accepted"])
        self.assertEqual(
            result["proofGate"]["reasonCode"], "FIXTURE_CANNOT_USE_REAL_PROOF"
        )


if __name__ == "__main__":
    unittest.main()
