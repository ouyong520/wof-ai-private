import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL_PATH = Path(__file__).resolve().parents[1] / "tools" / "alpha_worker_result.py"
SPEC = importlib.util.spec_from_file_location("alpha_worker_result", TOOL_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def complete_result():
    return {
        "schema": "wof-alpha-worker-result-v1",
        "stageId": "ALPHA_EXAMPLE_STAGE",
        "dedupKey": "alpha.example.stage",
        "claimToken": "0123456789abcdef",
        "state": "COMPLETE",
        "verdict": "The owned coordination module is implemented and focused tests pass.",
        "startCommit": "1" * 40,
        "implementationCommits": ["2" * 40],
        "integrationReady": True,
        "changedFiles": ["parallel/PM/tools/example.py"],
        "tests": [
            {
                "name": "focused unit",
                "result": "PASS",
                "detail": "Validated the owned protocol behavior.",
            }
        ],
        "productProof": {
            "status": "NOT_APPLICABLE",
            "classification": "NOT_APPLICABLE",
            "detail": "Coordination-only work has no Owner-visible product claim.",
        },
        "ownerGate": {"required": False, "question": None, "reason": None},
        "blocker": None,
        "nextAction": "PM may integrate this worker result.",
        "evidencePaths": ["parallel/PM/tests/test_example.py"],
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
    }


class ResultProtocolTests(unittest.TestCase):
    def test_valid_complete(self):
        self.assertEqual([], MODULE.validate_result(complete_result()))

    def test_valid_subcomplete(self):
        data = complete_result()
        data.update(
            state="SUBCOMPLETE",
            implementationCommits=[],
            integrationReady=False,
            changedFiles=[],
            tests=[],
            evidencePaths=[],
        )
        data["productProof"] = {
            "status": "NOT_PROVEN",
            "classification": "NOT_PROVEN",
            "detail": "Implementation evidence is not terminal yet.",
        }
        self.assertEqual([], MODULE.validate_result(data))

    def test_valid_blocked(self):
        data = complete_result()
        data.update(
            state="BLOCKED",
            implementationCommits=[],
            integrationReady=False,
            changedFiles=[],
            tests=[],
            evidencePaths=[],
        )
        data["blocker"] = {
            "code": "DEDUP_OWNERSHIP_LOST",
            "detail": "Canonical claim token no longer matches this worker.",
            "ownerRequired": False,
            "pmRequired": True,
            "recoveryAllowedByWorker": False,
        }
        data["productProof"] = {
            "status": "NOT_PROVEN",
            "classification": "NOT_PROVEN",
            "detail": "No terminal product proof exists because execution is blocked.",
        }
        self.assertEqual([], MODULE.validate_result(data))

    def test_deterministic_paths(self):
        self.assertEqual(
            {
                "json": "parallel/PM/RESULTS/ALPHA_EXAMPLE_STAGE_RESULT.json",
                "md": "parallel/PM/RESULTS/ALPHA_EXAMPLE_STAGE_RESULT.md",
            },
            MODULE.result_paths("ALPHA_EXAMPLE_STAGE"),
        )
        self.assertEqual(
            [],
            MODULE.verify_result_paths(
                "ALPHA_EXAMPLE_STAGE",
                "parallel/PM/RESULTS/ALPHA_EXAMPLE_STAGE_RESULT.json",
                "parallel/PM/RESULTS/ALPHA_EXAMPLE_STAGE_RESULT.md",
            ),
        )

    def test_path_mismatch_rejected(self):
        errors = MODULE.verify_result_paths(
            "ALPHA_EXAMPLE_STAGE",
            "parallel/PM/RESULTS/WRONG_RESULT.json",
            "parallel/PM/RESULTS/ALPHA_EXAMPLE_STAGE_RESULT.md",
        )
        self.assertTrue(any("$.resultJsonPath" in error for error in errors))

    def test_missing_required_field_rejected(self):
        for field in (
            "stageId",
            "state",
            "implementationCommits",
            "changedFiles",
            "tests",
            "productProof",
            "ownerGate",
            "blocker",
            "nextAction",
            "safety",
        ):
            with self.subTest(field=field):
                data = complete_result()
                del data[field]
                errors = MODULE.validate_result(data)
                self.assertTrue(any(f".{field}:" in error for error in errors), errors)

    def test_unsupported_state_rejected(self):
        data = complete_result()
        data["state"] = "DONE"
        errors = MODULE.validate_result(data)
        self.assertTrue(any("unsupported value 'DONE'" in error for error in errors))

    def test_complete_without_terminal_evidence_rejected(self):
        data = complete_result()
        data["implementationCommits"] = []
        data["changedFiles"] = []
        data["tests"] = []
        data["evidencePaths"] = []
        data["integrationReady"] = False
        errors = MODULE.validate_result(data)
        self.assertTrue(any("$.implementationCommits" in error for error in errors))
        self.assertTrue(any("$.changedFiles" in error for error in errors))
        self.assertTrue(any("$.tests" in error for error in errors))
        self.assertTrue(any("$.evidencePaths" in error for error in errors))
        self.assertTrue(any("$.integrationReady" in error for error in errors))

    def test_complete_with_fail_rejected(self):
        data = complete_result()
        data["tests"][0]["result"] = "FAIL"
        errors = MODULE.validate_result(data)
        self.assertTrue(any("COMPLETE cannot contain FAIL" in error for error in errors))

    def test_product_proof_classification_required(self):
        data = complete_result()
        data["productProof"] = {
            "status": "PROVEN",
            "detail": "Claims maintained renderer output without naming proof class.",
        }
        errors = MODULE.validate_result(data)
        self.assertTrue(any("$.productProof.classification: missing" in error for error in errors))

    def test_false_green_proven_with_unproven_classification_rejected(self):
        data = complete_result()
        data["productProof"] = {
            "status": "PROVEN",
            "classification": "NOT_PROVEN",
            "detail": "Incorrectly elevates implementation state to product proof.",
        }
        errors = MODULE.validate_result(data)
        self.assertTrue(any("PROVEN requires explicit" in error for error in errors))

    def test_proof_classes_remain_distinct(self):
        for classification in (
            "IMPLEMENTATION_PROOF",
            "MACHINE_DRAW_PROOF",
            "OWNER_VISUAL_PROOF",
        ):
            with self.subTest(classification=classification):
                data = complete_result()
                data["productProof"] = {
                    "status": "PROVEN",
                    "classification": classification,
                    "detail": f"Explicit {classification} evidence.",
                }
                self.assertEqual([], MODULE.validate_result(data))

    def test_blocked_requires_machine_code_and_flags(self):
        data = complete_result()
        data["state"] = "BLOCKED"
        data["integrationReady"] = False
        data["blocker"] = {"detail": "vague"}
        errors = MODULE.validate_result(data)
        for field in ("code", "ownerRequired", "pmRequired", "recoveryAllowedByWorker"):
            self.assertTrue(any(f"$.blocker.{field}: missing" in error for error in errors), errors)

    def test_owner_required_blocker_requires_owner_gate(self):
        data = complete_result()
        data["state"] = "BLOCKED"
        data["integrationReady"] = False
        data["blocker"] = {
            "code": "OWNER_VISUAL_REQUIRED",
            "detail": "Machine proof exists; visual confirmation is still required.",
            "ownerRequired": True,
            "pmRequired": False,
            "recoveryAllowedByWorker": False,
        }
        errors = MODULE.validate_result(data)
        self.assertTrue(any("$.ownerGate.required" in error for error in errors))

    def test_cli_validate_and_paths(self):
        data = complete_result()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(TOOL_PATH), "validate", str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertIn("VALID ALPHA_EXAMPLE_STAGE COMPLETE", proc.stdout)

        proc = subprocess.run(
            [sys.executable, str(TOOL_PATH), "paths", "ALPHA_EXAMPLE_STAGE"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        parsed = json.loads(proc.stdout)
        self.assertEqual(
            "parallel/PM/RESULTS/ALPHA_EXAMPLE_STAGE_RESULT.json",
            parsed["json"],
        )


if __name__ == "__main__":
    unittest.main()
