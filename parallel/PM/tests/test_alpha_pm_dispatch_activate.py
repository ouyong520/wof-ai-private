#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import alpha_pm_dispatch_activate as activate


class DispatchActivatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "parallel/PM/DISPATCH_MANIFESTS").mkdir(parents=True)
        (self.root / "parallel/PM/RESULTS").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_dispatch(self, dispatch_id: str, authority: str) -> Path:
        stage = f"{dispatch_id}_STAGE"
        dedup = dispatch_id.lower().replace("_", ".") + ".stage"
        manifest_rel = f"parallel/PM/DISPATCH_MANIFESTS/{dispatch_id}.json"
        prompt_rel = f"parallel/PM/{stage}_START_PROMPT.md"
        result_json = f"parallel/PM/RESULTS/{stage}_RESULT.json"
        result_md = f"parallel/PM/RESULTS/{stage}_RESULT.md"
        prompt = (
            f"stageId: `{stage}`\n"
            "dedupProtocol: `v2`\n"
            f"dedupKey: `{dedup}`\n"
            "dedupMode: `exclusive`\n"
            "resultProtocol: `wof-alpha-worker-result-v1`\n"
            f"resultJsonPath: `{result_json}`\n"
            f"resultMdPath: `{result_md}`\n"
            f"terminalCommitPrefix: `WORKER_RESULT {stage}`\n"
            f"dispatchManifestPath: `{manifest_rel}`\n\n"
            "Follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.\n"
        )
        (self.root / prompt_rel).write_text(prompt, encoding="utf-8")
        payload = {
            "schema": "wof-alpha-dispatch-manifest-v1",
            "dispatchId": dispatch_id,
            "createdAtUtc": "2026-09-05T05:00:00Z",
            "authorityCommit": authority,
            "immutable": True,
            "workers": [
                {
                    "slot": 1,
                    "stageId": stage,
                    "promptPath": prompt_rel,
                    "dedupKey": dedup,
                    "resultProtocol": "wof-alpha-worker-result-v1",
                    "resultJsonPath": result_json,
                    "resultMdPath": result_md,
                    "terminalCommitPrefix": f"WORKER_RESULT {stage}",
                }
            ],
        }
        path = self.root / manifest_rel
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def _write_pointer(self, manifest: Path, revision: int = 1) -> dict[str, object]:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        rel = manifest.relative_to(self.root).as_posix()
        payload = {
            "schema": "wof-alpha-current-dispatch-v1",
            "pmOwned": True,
            "repository": "ouyong520/wof-ai-private",
            "dispatchId": data["dispatchId"],
            "manifestPath": rel,
            "manifestAuthorityCommit": data["authorityCommit"],
            "manifestSha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
            "updatedAtUtc": "2026-09-05T05:05:00Z",
            "revision": revision,
            "previousDispatch": None,
        }
        pointer = self.root / "parallel/PM/CURRENT_DISPATCH.json"
        pointer.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return payload

    def test_clean_plan_from_no_pointer_is_deterministic(self) -> None:
        manifest = self._write_dispatch("TEST_DISPATCH_ONE", "a" * 40)
        kwargs = dict(
            repo_root=self.root,
            manifest_path=manifest,
            at_utc="2026-09-05T06:00:00Z",
            expect_current_absent=True,
        )
        first = activate.build_plan(**kwargs)
        second = activate.build_plan(**kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["operation"], "create")
        self.assertEqual(first["transition"]["revision"], 1)
        self.assertIsNone(first["transition"]["previousDispatch"])
        self.assertEqual(first["writeGuard"]["expectedOldState"], "ABSENT")

    def test_valid_transition_rolls_previous_and_verifies_written_pointer(self) -> None:
        old_manifest = self._write_dispatch("TEST_DISPATCH_ONE", "a" * 40)
        old_pointer = self._write_pointer(old_manifest)
        new_manifest = self._write_dispatch("TEST_DISPATCH_TWO", "b" * 40)
        plan = activate.build_plan(
            repo_root=self.root,
            manifest_path=new_manifest,
            at_utc="2026-09-05T06:01:00Z",
            revision=2,
        )
        self.assertEqual(plan["operation"], "update")
        self.assertEqual(plan["transition"]["revision"], 2)
        previous = plan["transition"]["previousDispatch"]
        self.assertEqual(previous["dispatchId"], old_pointer["dispatchId"])
        self.assertEqual(previous["manifestSha256"], old_pointer["manifestSha256"])
        pointer = self.root / "parallel/PM/CURRENT_DISPATCH.json"
        pointer.write_text(plan["plannedPointerText"], encoding="utf-8")
        verified = activate.verify_activation(
            repo_root=self.root,
            expected_pointer_sha256=plan["plannedPointerSha256"],
            expected_dispatch_id="TEST_DISPATCH_TWO",
            expected_revision=2,
        )
        self.assertTrue(verified["ok"])

    def test_stale_guard_rejects_concurrent_pointer_change(self) -> None:
        old_manifest = self._write_dispatch("TEST_DISPATCH_ONE", "a" * 40)
        self._write_pointer(old_manifest)
        new_manifest = self._write_dispatch("TEST_DISPATCH_TWO", "b" * 40)
        plan = activate.build_plan(
            repo_root=self.root,
            manifest_path=new_manifest,
            at_utc="2026-09-05T06:02:00Z",
        )
        pointer = self.root / "parallel/PM/CURRENT_DISPATCH.json"
        pointer.write_bytes(pointer.read_bytes() + b" ")
        with self.assertRaisesRegex(activate.ActivationError, "concurrent pointer change"):
            activate.check_guard(
                repo_root=self.root,
                expected_old_sha256=plan["writeGuard"]["expectedOldSha256"],
                expect_absent=False,
            )

    def test_revision_regression_is_rejected(self) -> None:
        old_manifest = self._write_dispatch("TEST_DISPATCH_ONE", "a" * 40)
        self._write_pointer(old_manifest)
        new_manifest = self._write_dispatch("TEST_DISPATCH_TWO", "b" * 40)
        with self.assertRaisesRegex(activate.ActivationError, "revision regression"):
            activate.build_plan(
                repo_root=self.root,
                manifest_path=new_manifest,
                at_utc="2026-09-05T06:03:00Z",
                revision=1,
            )


if __name__ == "__main__":
    unittest.main()
