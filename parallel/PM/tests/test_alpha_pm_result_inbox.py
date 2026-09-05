from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "alpha_pm_result_inbox.py"
SPEC = importlib.util.spec_from_file_location("alpha_pm_result_inbox", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
inbox = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = inbox
SPEC.loader.exec_module(inbox)


class AlphaPmResultInboxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "parallel" / "PM" / "RESULTS").mkdir(parents=True)
        (self.root / "parallel" / "PM" / "DISPATCH_MANIFESTS").mkdir(parents=True)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def worker(self, slot: int, stage: str | None = None) -> dict:
        stage_id = stage or f"ALPHA_TEST_WORKER_{slot}"
        return {
            "slot": slot,
            "stageId": stage_id,
            "promptPath": f"parallel/PM/{stage_id}_START_PROMPT.md",
            "dedupKey": f"alpha.test.worker-{slot}",
            "resultProtocol": "wof-alpha-worker-result-v1",
            "resultJsonPath": f"parallel/PM/RESULTS/{stage_id}_RESULT.json",
            "resultMdPath": f"parallel/PM/RESULTS/{stage_id}_RESULT.md",
            "terminalCommitPrefix": f"WORKER_RESULT {stage_id}",
        }

    def manifest(self, workers: list[dict] | None = None) -> dict:
        return {
            "schema": "wof-alpha-dispatch-manifest-v1",
            "dispatchId": "ALPHA_TEST_DISPATCH_V1",
            "createdAtUtc": "2026-09-05T00:00:00Z",
            "authorityCommit": "a" * 40,
            "immutable": True,
            "workers": workers or [self.worker(1), self.worker(2), self.worker(3)],
        }

    def write_manifest(self, payload: dict) -> Path:
        path = (
            self.root
            / "parallel"
            / "PM"
            / "DISPATCH_MANIFESTS"
            / "ALPHA_TEST_DISPATCH_V1.json"
        )
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def result(self, worker: dict, state: str, *, stage_id: str | None = None) -> dict:
        blocked = state == "BLOCKED"
        return {
            "schema": "wof-alpha-worker-result-v1",
            "stageId": stage_id or worker["stageId"],
            "dedupKey": worker["dedupKey"],
            "claimToken": "claim-token",
            "state": state,
            "verdict": f"{worker['stageId']} produced a deterministic fixture result.",
            "startCommit": "b" * 40,
            "implementationCommits": ["c" * 40],
            "integrationReady": state == "COMPLETE",
            "changedFiles": ["parallel/PM/example.txt"],
            "tests": [
                {
                    "name": "focused fixture",
                    "result": "PASS",
                    "detail": "deterministic fixture passed",
                }
            ],
            "productProof": {
                "status": "NOT_APPLICABLE",
                "classification": "NOT_APPLICABLE",
                "detail": "coordination-only fixture",
            },
            "ownerGate": {"required": False, "question": None, "reason": None},
            "blocker": (
                {
                    "code": "FIXTURE_BLOCKER",
                    "detail": "fixture is intentionally blocked",
                    "ownerRequired": False,
                    "pmRequired": True,
                    "recoveryAllowedByWorker": False,
                }
                if blocked
                else None
            ),
            "nextAction": "PM should consume this fixture result.",
            "evidencePaths": ["parallel/PM/example.txt"],
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        }

    def write_result(self, worker: dict, payload: dict) -> None:
        path = self.root.joinpath(*Path(worker["resultJsonPath"]).parts)
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_mixed_dispatch_complete_blocked_not_finished(self) -> None:
        workers = [self.worker(3), self.worker(1), self.worker(2)]
        manifest_path = self.write_manifest(self.manifest(workers))
        by_slot = {worker["slot"]: worker for worker in workers}
        self.write_result(by_slot[1], self.result(by_slot[1], "COMPLETE"))
        self.write_result(by_slot[2], self.result(by_slot[2], "BLOCKED"))

        summary = inbox.build_inbox_summary(self.root, manifest_path)

        self.assertEqual(summary["selectedSlots"], [1, 2, 3])
        self.assertEqual(
            [worker["state"] for worker in summary["workers"]],
            ["COMPLETE", "BLOCKED", "NOT_FINISHED"],
        )
        self.assertEqual(summary["counts"]["COMPLETE"], 1)
        self.assertEqual(summary["counts"]["BLOCKED"], 1)
        self.assertEqual(summary["counts"]["NOT_FINISHED"], 1)
        self.assertTrue(summary["allResultsValid"])
        self.assertFalse(summary["allWorkersTerminal"])
        self.assertEqual(summary["workers"][0]["tests"]["PASS"], 1)
        self.assertEqual(
            summary["workers"][1]["blocker"]["code"], "FIXTURE_BLOCKER"
        )

    def test_malformed_result_is_invalid_result(self) -> None:
        worker = self.worker(1)
        manifest_path = self.write_manifest(self.manifest([worker]))
        path = self.root.joinpath(*Path(worker["resultJsonPath"]).parts)
        path.write_text("{not-json", encoding="utf-8")

        summary = inbox.build_inbox_summary(self.root, manifest_path)

        self.assertEqual(summary["workers"][0]["state"], "INVALID_RESULT")
        self.assertEqual(summary["counts"]["INVALID_RESULT"], 1)
        self.assertFalse(summary["allResultsValid"])

    def test_stage_mismatch_is_invalid_result(self) -> None:
        worker = self.worker(1)
        manifest_path = self.write_manifest(self.manifest([worker]))
        self.write_result(
            worker,
            self.result(worker, "COMPLETE", stage_id="ALPHA_WRONG_WORKER"),
        )

        summary = inbox.build_inbox_summary(self.root, manifest_path)

        self.assertEqual(summary["workers"][0]["state"], "INVALID_RESULT")
        self.assertIn(
            "stageId mismatch",
            summary["workers"][0]["validationErrors"][0],
        )

    def test_unsupported_result_state_is_invalid_result(self) -> None:
        worker = self.worker(1)
        manifest_path = self.write_manifest(self.manifest([worker]))
        payload = self.result(worker, "COMPLETE")
        payload["state"] = "ACTIVE"
        self.write_result(worker, payload)

        summary = inbox.build_inbox_summary(self.root, manifest_path)

        self.assertEqual(summary["workers"][0]["state"], "INVALID_RESULT")
        self.assertIn(
            "unsupported result state",
            summary["workers"][0]["validationErrors"][0],
        )

    def test_duplicate_result_path_fails_manifest_before_cross_field_check(self) -> None:
        first = self.worker(1, "ALPHA_DUP_A")
        second = self.worker(2, "ALPHA_DUP_B")
        second["resultJsonPath"] = first["resultJsonPath"]

        with self.assertRaisesRegex(inbox.ManifestError, "duplicate resultJsonPath"):
            inbox.parse_manifest_payload(self.manifest([first, second]))

    def test_traversal_result_path_fails_closed(self) -> None:
        worker = self.worker(1)
        worker["resultJsonPath"] = "parallel/PM/RESULTS/../escape.json"

        with self.assertRaisesRegex(inbox.ManifestError, "path traversal"):
            inbox.parse_manifest_payload(self.manifest([worker]))

    def test_slot_selection_and_deterministic_summary(self) -> None:
        workers = [self.worker(3), self.worker(1), self.worker(2)]
        manifest_path = self.write_manifest(self.manifest(workers))
        by_slot = {worker["slot"]: worker for worker in workers}
        self.write_result(by_slot[1], self.result(by_slot[1], "COMPLETE"))
        self.write_result(by_slot[3], self.result(by_slot[3], "SUBCOMPLETE"))

        first = inbox.build_inbox_summary(self.root, manifest_path, slots=[3, 1])
        second = inbox.build_inbox_summary(self.root, manifest_path, slots=[1, 3])

        self.assertEqual(first["selectedSlots"], [1, 3])
        self.assertEqual(first, second)
        self.assertEqual(
            json.dumps(first, ensure_ascii=False, separators=(",", ":")),
            json.dumps(second, ensure_ascii=False, separators=(",", ":")),
        )

    def test_unknown_slot_fails_closed(self) -> None:
        manifest_path = self.write_manifest(self.manifest([self.worker(1)]))
        with self.assertRaisesRegex(inbox.ManifestError, "not declared"):
            inbox.build_inbox_summary(self.root, manifest_path, slots=[3])

    def test_manifest_requires_exact_deterministic_result_path(self) -> None:
        worker = self.worker(1)
        worker["resultJsonPath"] = "parallel/PM/RESULTS/OTHER_RESULT.json"
        with self.assertRaisesRegex(inbox.ManifestError, "must be deterministic"):
            inbox.parse_manifest_payload(self.manifest([worker]))


    def test_unsupported_result_protocol_is_invalid_result(self) -> None:
        worker = self.worker(1)
        manifest_path = self.write_manifest(self.manifest([worker]))
        payload = self.result(worker, "COMPLETE")
        payload["schema"] = "wof-alpha-worker-result-v0"
        self.write_result(worker, payload)

        summary = inbox.build_inbox_summary(self.root, manifest_path)

        self.assertEqual(summary["workers"][0]["state"], "INVALID_RESULT")
        self.assertIn(
            "unsupported result protocol",
            summary["workers"][0]["validationErrors"][0],
        )

    def test_repository_template_is_valid_manifest(self) -> None:
        template_path = Path(__file__).resolve().parents[1] / "templates" / "alpha_dispatch_manifest_v1.json"
        payload = json.loads(template_path.read_text(encoding="utf-8"))
        parsed = inbox.parse_manifest_payload(payload)
        self.assertEqual(parsed.dispatch_id, "EXAMPLE_ALPHA_3_WORKER_DISPATCH_V1")
        self.assertEqual([worker.slot for worker in parsed.workers], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
