#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import alpha_pm_current_dispatch as current


AUTHORITY = "a" * 40
REPOSITORY = "ouyong520/wof-ai-private"


def _worker(slot: int) -> dict:
    stage = f"ALPHA_TEST_WORKER_{slot}"
    return {
        "slot": slot,
        "stageId": stage,
        "promptPath": f"parallel/PM/{stage}_START_PROMPT.md",
        "dedupKey": f"alpha.test.worker-{slot}",
        "resultProtocol": "wof-alpha-worker-result-v1",
        "resultJsonPath": f"parallel/PM/RESULTS/{stage}_RESULT.json",
        "resultMdPath": f"parallel/PM/RESULTS/{stage}_RESULT.md",
        "terminalCommitPrefix": f"WORKER_RESULT {stage}",
    }


def _manifest(dispatch_id: str = "ALPHA_TEST_DISPATCH", workers: int = 3) -> dict:
    return {
        "schema": "wof-alpha-dispatch-manifest-v1",
        "dispatchId": dispatch_id,
        "createdAtUtc": "2026-09-05T05:00:00Z",
        "authorityCommit": AUTHORITY,
        "immutable": True,
        "workers": [_worker(slot) for slot in range(1, workers + 1)],
    }


def _result(worker: dict, state: str) -> dict:
    terminal = state == "COMPLETE"
    blocked = state == "BLOCKED"
    return {
        "schema": "wof-alpha-worker-result-v1",
        "stageId": worker["stageId"],
        "dedupKey": worker["dedupKey"],
        "claimToken": f"claim-token-{worker['slot']}",
        "state": state,
        "verdict": f"worker {worker['slot']} says {state}",
        "startCommit": "b" * 40,
        "implementationCommits": ["c" * 40] if terminal else [],
        "integrationReady": terminal,
        "changedFiles": [f"parallel/PM/example-{worker['slot']}.txt"] if terminal else [],
        "tests": [
            {"name": "focused", "result": "PASS", "detail": "fixture pass"}
        ] if terminal else [],
        "productProof": {
            "status": "NOT_APPLICABLE",
            "classification": "NOT_APPLICABLE",
            "detail": "coordination fixture",
        },
        "ownerGate": {"required": False, "question": None, "reason": None},
        "blocker": (
            {
                "code": "TEST_BLOCKED",
                "detail": "fixture blocker",
                "ownerRequired": False,
                "pmRequired": True,
                "recoveryAllowedByWorker": False,
            }
            if blocked
            else None
        ),
        "nextAction": "fixture next action",
        "evidencePaths": ["parallel/PM/example.txt"] if terminal else [],
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
    }


class CurrentDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "parallel/PM/DISPATCH_MANIFESTS").mkdir(parents=True)
        (self.root / "parallel/PM/RESULTS").mkdir(parents=True)
        self.dispatch_id = "ALPHA_TEST_DISPATCH"
        self.manifest = _manifest(self.dispatch_id)
        self.manifest_path = (
            self.root
            / "parallel/PM/DISPATCH_MANIFESTS"
            / f"{self.dispatch_id}.json"
        )
        self.pointer_path = self.root / "parallel/PM/CURRENT_DISPATCH.json"
        self._write_manifest(self.manifest)
        self.pointer = self._pointer_for_current_manifest()
        self._write_pointer(self.pointer)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_manifest(self, payload: dict) -> None:
        self.manifest_path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    def _manifest_digest(self) -> str:
        return hashlib.sha256(self.manifest_path.read_bytes()).hexdigest()

    def _pointer_for_current_manifest(self) -> dict:
        return {
            "schema": "wof-alpha-current-dispatch-v1",
            "pmOwned": True,
            "repository": REPOSITORY,
            "dispatchId": self.dispatch_id,
            "manifestPath": (
                f"parallel/PM/DISPATCH_MANIFESTS/{self.dispatch_id}.json"
            ),
            "manifestAuthorityCommit": AUTHORITY,
            "manifestSha256": self._manifest_digest(),
            "updatedAtUtc": "2026-09-05T05:01:00Z",
            "revision": 1,
            "previousDispatch": None,
        }

    def _write_pointer(self, payload: dict) -> None:
        self.pointer_path.parent.mkdir(parents=True, exist_ok=True)
        self.pointer_path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    def _write_result(self, slot: int, state: str) -> None:
        worker = self.manifest["workers"][slot - 1]
        path = self.root / worker["resultJsonPath"]
        path.write_text(json.dumps(_result(worker, state), indent=2) + "\n", encoding="utf-8")

    def test_valid_pointer_selects_owner_shorthand_slots_1_and_3(self) -> None:
        summary = current.resolve_current_dispatch(
            self.root, Path("parallel/PM/CURRENT_DISPATCH.json"), slots=[1, 3]
        )
        self.assertEqual(summary["selectedSlots"], [1, 3])
        self.assertEqual([w["state"] for w in summary["workers"]], ["NOT_FINISHED", "NOT_FINISHED"])
        self.assertEqual(summary["pmAction"], "WAIT_FOR_EXACT_RESULT_JSON")

    def test_complete_blocked_and_missing_mix_uses_c2_truth(self) -> None:
        self._write_result(1, "COMPLETE")
        self._write_result(2, "BLOCKED")
        summary = current.resolve_current_dispatch(self.root, self.pointer_path)
        self.assertEqual(summary["counts"]["COMPLETE"], 1)
        self.assertEqual(summary["counts"]["BLOCKED"], 1)
        self.assertEqual(summary["counts"]["NOT_FINISHED"], 1)
        self.assertEqual(summary["pmAction"], "REVIEW_BLOCKER")

    def test_malformed_result_is_invalid_not_inferred(self) -> None:
        worker = self.manifest["workers"][0]
        (self.root / worker["resultJsonPath"]).write_text("{bad", encoding="utf-8")
        summary = current.resolve_current_dispatch(self.root, self.pointer_path, slots=[1])
        self.assertEqual(summary["workers"][0]["state"], "INVALID_RESULT")
        self.assertFalse(summary["allResultsValid"])
        self.assertEqual(summary["pmAction"], "REJECT_INVALID_RESULT")

    def test_missing_pointer_fails_closed(self) -> None:
        self.pointer_path.unlink()
        with self.assertRaises(current.CurrentDispatchError):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_malformed_pointer_fails_closed(self) -> None:
        self.pointer_path.write_text("{bad", encoding="utf-8")
        with self.assertRaises(current.CurrentDispatchError):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_non_pm_owned_pointer_fails_closed(self) -> None:
        pointer = deepcopy(self.pointer)
        pointer["pmOwned"] = False
        self._write_pointer(pointer)
        with self.assertRaisesRegex(current.CurrentDispatchError, "pmOwned"):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_missing_manifest_fails_closed(self) -> None:
        self.manifest_path.unlink()
        with self.assertRaises(current.CurrentDispatchError):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_immutable_false_manifest_fails_closed(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["immutable"] = False
        self._write_manifest(manifest)
        pointer = self._pointer_for_current_manifest()
        self._write_pointer(pointer)
        with self.assertRaisesRegex(current.CurrentDispatchError, "immutable"):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_dispatch_id_mismatch_fails_closed(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["dispatchId"] = "ALPHA_DIFFERENT_DISPATCH"
        self._write_manifest(manifest)
        pointer = self._pointer_for_current_manifest()
        self._write_pointer(pointer)
        with self.assertRaisesRegex(current.CurrentDispatchError, "dispatchId mismatch"):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_repository_mismatch_fails_closed(self) -> None:
        pointer = deepcopy(self.pointer)
        pointer["repository"] = "other/repository"
        self._write_pointer(pointer)
        with self.assertRaisesRegex(current.CurrentDispatchError, "repository mismatch"):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_manifest_path_traversal_fails_closed(self) -> None:
        pointer = deepcopy(self.pointer)
        pointer["manifestPath"] = "parallel/PM/DISPATCH_MANIFESTS/../evil.json"
        self._write_pointer(pointer)
        with self.assertRaisesRegex(current.CurrentDispatchError, "traversal"):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_unsupported_manifest_schema_fails_closed(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["schema"] = "wof-alpha-dispatch-manifest-v99"
        self._write_manifest(manifest)
        pointer = self._pointer_for_current_manifest()
        self._write_pointer(pointer)
        with self.assertRaisesRegex(current.CurrentDispatchError, "schema"):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_unknown_slot_fails_closed(self) -> None:
        with self.assertRaisesRegex(current.CurrentDispatchError, "slot"):
            current.resolve_current_dispatch(self.root, self.pointer_path, slots=[4])

    def test_stale_or_redirected_manifest_hash_fails_closed(self) -> None:
        pointer = deepcopy(self.pointer)
        pointer["manifestSha256"] = "0" * 64
        self._write_pointer(pointer)
        with self.assertRaisesRegex(current.CurrentDispatchError, "stale or redirected"):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_authority_commit_mismatch_fails_closed(self) -> None:
        pointer = deepcopy(self.pointer)
        pointer["manifestAuthorityCommit"] = "d" * 40
        self._write_pointer(pointer)
        with self.assertRaisesRegex(current.CurrentDispatchError, "manifestAuthorityCommit"):
            current.resolve_current_dispatch(self.root, self.pointer_path)

    def test_new_session_reconstructs_state_from_git_files_alone(self) -> None:
        self._write_result(1, "COMPLETE")
        summary = current.resolve_current_dispatch(
            self.root,
            Path("parallel/PM/CURRENT_DISPATCH.json"),
            slots=[1, 2, 3],
        )
        self.assertEqual(summary["dispatchId"], self.dispatch_id)
        self.assertEqual(summary["workers"][0]["state"], "COMPLETE")
        self.assertEqual(summary["workers"][1]["state"], "NOT_FINISHED")
        self.assertEqual(summary["workers"][2]["state"], "NOT_FINISHED")
        self.assertEqual(
            summary["workers"][0]["resultJsonPath"],
            self.manifest["workers"][0]["resultJsonPath"],
        )


if __name__ == "__main__":
    unittest.main()
