#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("pm_stage_dedup_v2.py")
spec = importlib.util.spec_from_file_location("pm_stage_dedup_v2", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class CanonicalDedupProtocolTests(unittest.TestCase):
    def meta(
        self,
        stage: str,
        key: str = "pm.same-logical-task",
        mode: str = "exclusive",
        group: str | None = None,
        validation_key: str | None = None,
    ):
        lines = [
            f"stageId: `{stage}`",
            "dedupProtocol: `v2`",
            f"dedupKey: `{key}`",
            f"dedupMode: `{mode}`",
        ]
        if group is not None:
            lines.append(f"independentValidationGroup: `{group}`")
        if validation_key is not None:
            lines.append(f"independentValidationKey: `{validation_key}`")
        return mod.parse_prompt_metadata("\n".join(lines))

    def claim(self, store, metadata, token, prompt="parallel/PM/T_START_PROMPT.md"):
        return mod.attempt_claim_for_test(
            store,
            metadata,
            prompt_path=prompt,
            owner=f"owner-{token}",
            claim_token=token,
            start_commit=f"head-{token}",
        )

    def test_same_stage_same_dedup_only_one_owner(self):
        store = mod.MemoryCreateOnlyStore()
        metadata = self.meta("SAME_STAGE_V1")
        self.assertEqual(self.claim(store, metadata, "a"), "CLAIM ACQUIRED — WORK STARTED")
        self.assertEqual(self.claim(store, metadata, "b"), "ALREADY CLAIMED — SAFE TO CLOSE")

    def test_different_stage_ids_same_dedup_only_one_owner(self):
        store = mod.MemoryCreateOnlyStore()
        a = self.meta("FIRST_STAGE_V1")
        b = self.meta("ACCIDENTAL_COPY_DIFFERENT_STAGE_V9")
        self.assertEqual(a.canonical_claim_path, b.canonical_claim_path)
        self.assertEqual(self.claim(store, a, "a", "parallel/PM/A_START_PROMPT.md"), "CLAIM ACQUIRED — WORK STARTED")
        self.assertEqual(self.claim(store, b, "b", "parallel/PM/B_START_PROMPT.md"), "ALREADY CLAIMED — SAFE TO CLOSE")

    def test_losing_claimant_exits_before_task_work(self):
        store = mod.MemoryCreateOnlyStore()
        a = self.meta("OWNER_STAGE_V1")
        b = self.meta("LOSER_STAGE_V2")
        self.assertEqual(self.claim(store, a, "owner"), "CLAIM ACQUIRED — WORK STARTED")
        task_work_calls = []
        outcome = self.claim(store, b, "loser")
        if outcome == "CLAIM ACQUIRED — WORK STARTED":
            task_work_calls.append("ran")
        self.assertEqual(outcome, "ALREADY CLAIMED — SAFE TO CLOSE")
        self.assertEqual(task_work_calls, [])

    def test_completed_equivalent_work_returns_already_complete(self):
        store = mod.MemoryCreateOnlyStore()
        metadata = self.meta("COMPLETE_STAGE_V1")
        path = metadata.canonical_claim_path
        payload = mod.build_canonical_claim(
            metadata,
            prompt_path="parallel/PM/A_START_PROMPT.md",
            owner="winner",
            claim_token="winner-token",
            start_commit="head",
        )
        payload["state"] = "COMPLETE"
        store.force_write_for_test(path, payload)
        self.assertEqual(self.claim(store, metadata, "new-token"), "ALREADY COMPLETE — SAFE TO CLOSE")

    def test_explicit_independent_cross_checks_get_distinct_authorized_locks(self):
        store = mod.MemoryCreateOnlyStore()
        a = self.meta(
            "QA_CROSSCHECK_A_V1",
            key="alpha.feature.qa",
            mode="independent-validation",
            group="release-crosscheck",
            validation_key="opinion-a",
        )
        b = self.meta(
            "QA_CROSSCHECK_B_V1",
            key="alpha.feature.qa",
            mode="independent-validation",
            group="release-crosscheck",
            validation_key="opinion-b",
        )
        copied_a = self.meta(
            "QA_CROSSCHECK_A_COPY_V2",
            key="alpha.feature.qa",
            mode="independent-validation",
            group="release-crosscheck",
            validation_key="opinion-a",
        )
        self.assertNotEqual(a.canonical_claim_path, b.canonical_claim_path)
        self.assertEqual(a.canonical_claim_path, copied_a.canonical_claim_path)
        self.assertEqual(self.claim(store, a, "a"), "CLAIM ACQUIRED — WORK STARTED")
        self.assertEqual(self.claim(store, b, "b"), "CLAIM ACQUIRED — WORK STARTED")
        self.assertEqual(self.claim(store, copied_a, "copy"), "ALREADY CLAIMED — SAFE TO CLOSE")

    def test_active_or_stale_claim_cannot_be_stolen(self):
        store = mod.MemoryCreateOnlyStore()
        metadata = self.meta("STALE_OWNER_V1")
        self.assertEqual(self.claim(store, metadata, "old-owner"), "CLAIM ACQUIRED — WORK STARTED")
        before = store.read(metadata.canonical_claim_path)
        self.assertEqual(self.claim(store, metadata, "new-owner"), "ALREADY CLAIMED — SAFE TO CLOSE")
        after = store.read(metadata.canonical_claim_path)
        self.assertEqual(before, after)
        self.assertEqual(after["claimToken"], "old-owner")
        self.assertEqual(after["state"], "ACTIVE")

    def test_missing_or_malformed_metadata_fails_closed(self):
        malformed = [
            "stageId: `MISSING_ALL_V1`",
            "\n".join(
                [
                    "stageId: `BAD_PROTOCOL_V1`",
                    "dedupProtocol: `v1`",
                    "dedupKey: `valid.key`",
                    "dedupMode: `exclusive`",
                ]
            ),
            "\n".join(
                [
                    "stageId: `BAD_KEY_V1`",
                    "dedupProtocol: `v2`",
                    "dedupKey: `UPPER CASE`",
                    "dedupMode: `exclusive`",
                ]
            ),
            "\n".join(
                [
                    "stageId: `MISSING_IV_SLOT_V1`",
                    "dedupProtocol: `v2`",
                    "dedupKey: `valid.qa-key`",
                    "dedupMode: `independent-validation`",
                    "independentValidationGroup: `group-a`",
                ]
            ),
        ]
        for text in malformed:
            with self.subTest(text=text):
                with self.assertRaises(mod.DedupProtocolError):
                    mod.parse_prompt_metadata(text)

    def test_ownership_re_read_requires_exact_claim_token(self):
        metadata = self.meta("TOKEN_VERIFY_V1")
        payload = mod.build_canonical_claim(
            metadata,
            prompt_path="parallel/PM/T_START_PROMPT.md",
            owner="owner",
            claim_token="right-token",
            start_commit="head",
        )
        with self.assertRaises(mod.DedupProtocolError):
            mod.verify_claim_ownership(
                payload,
                metadata,
                prompt_path="parallel/PM/T_START_PROMPT.md",
                claim_token="wrong-token",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
