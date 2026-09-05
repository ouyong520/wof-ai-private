import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

PM_ROOT = Path(__file__).resolve().parents[1]
TOOLS = PM_ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import alpha_pm_dispatch_builder as builder
import alpha_worker_dispatch_contract as contract


class DispatchBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        authority = self.root / "parallel/PM/AUTHORITY.md"
        authority.parent.mkdir(parents=True)
        authority.write_text("# authority\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def spec(self, count=1):
        return {
            "schema": "wof-alpha-dispatch-spec-v1",
            "dispatchId": f"ALPHA_TEST_{count}_WORKER_V1",
            "createdAtUtc": "2026-09-05T05:16:00Z",
            "authorityPath": "parallel/PM/AUTHORITY.md",
            "authorityCommit": "a" * 40,
            "workers": [
                {
                    "stageId": f"ALPHA_TEST_WORKER_{i}",
                    "dedupKey": f"alpha.test.worker-{i}",
                    "mission": f"exercise worker {i}",
                    "instructions": ["Stay in PM scope."],
                }
                for i in range(1, count + 1)
            ],
        }

    def test_valid_one_two_three_workers(self):
        for count in (1, 2, 3):
            package = builder.render_package(self.spec(count), repo_root=self.root)
            self.assertEqual(count, len(package["manifest"]["workers"]))
            self.assertEqual([], contract.validate_manifest_data(package["manifest"]))

    def test_repeated_render_is_deterministic(self):
        spec = self.spec(3)
        first = builder.canonical_json(builder.render_package(spec, repo_root=self.root))
        second = builder.canonical_json(builder.render_package(copy.deepcopy(spec), repo_root=self.root))
        self.assertEqual(first, second)

    def test_duplicate_stage_and_dedup_fail_closed(self):
        spec = self.spec(2)
        spec["workers"][1]["stageId"] = spec["workers"][0]["stageId"]
        spec["workers"][1]["dedupKey"] = spec["workers"][0]["dedupKey"]
        with self.assertRaises(builder.DispatchSpecError) as ctx:
            builder.render_package(spec, repo_root=self.root)
        text = str(ctx.exception)
        self.assertIn("duplicate", text)
        self.assertIn("dedupKey", text)

    def test_traversal_fails_closed(self):
        spec = self.spec()
        spec["workers"][0]["promptPath"] = "parallel/PM/../ESCAPE.md"
        with self.assertRaises(builder.DispatchSpecError):
            builder.render_package(spec, repo_root=self.root)
        spec = self.spec()
        spec["authorityPath"] = "parallel/PM/../../ESCAPE.md"
        with self.assertRaises(builder.DispatchSpecError):
            builder.render_package(spec, repo_root=self.root)

    def test_existing_target_refused(self):
        package = builder.render_package(self.spec(), repo_root=self.root)
        existing = self.root / package["manifestPath"]
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("occupied", encoding="utf-8")
        with self.assertRaises(builder.DispatchSpecError) as ctx:
            builder.write_package(package, output_root=self.root)
        self.assertIn("already exists", str(ctx.exception))

    def test_malformed_authority_fails_closed(self):
        spec = self.spec()
        spec["authorityCommit"] = "not-a-commit"
        with self.assertRaises(builder.DispatchSpecError):
            builder.render_package(spec, repo_root=self.root)
        spec = self.spec()
        spec["authorityPath"] = "parallel/PM/MISSING.md"
        with self.assertRaises(builder.DispatchSpecError):
            builder.render_package(spec, repo_root=self.root)

    def test_invalid_worker_count(self):
        for count in (0, 4):
            spec = self.spec(1)
            spec["workers"] = [] if count == 0 else self.spec(3)["workers"] + [{"stageId": "ALPHA_TEST_WORKER_4", "dedupKey": "alpha.test.worker-4", "mission": "worker 4"}]
            with self.assertRaises(builder.DispatchSpecError):
                builder.render_package(spec, repo_root=self.root)

    def test_result_path_drift_fails_closed(self):
        spec = self.spec()
        spec["workers"][0]["resultJsonPath"] = "parallel/PM/RESULTS/REDIRECTED_RESULT.json"
        with self.assertRaises(builder.DispatchSpecError) as ctx:
            builder.render_package(spec, repo_root=self.root)
        self.assertIn("resultJsonPath", str(ctx.exception))

    def test_final_manifest_and_prompt_match_existing_validator(self):
        package = builder.render_package(self.spec(3), repo_root=self.root)
        manifest = package["manifest"]
        self.assertEqual([], contract.validate_manifest_data(manifest))
        for index, entry in enumerate(manifest["workers"]):
            prompt = package["prompts"][entry["promptPath"]]
            self.assertEqual([], contract.validate_entry_against_prompt(entry, prompt, index=index, manifest_path=package["manifestPath"]))

    def test_build_writes_create_only_package(self):
        package = builder.render_package(self.spec(2), repo_root=self.root)
        output = self.root / "staging"
        written = builder.write_package(package, output_root=output)
        self.assertEqual(3, len(written))
        manifest = json.loads((output / package["manifestPath"]).read_text(encoding="utf-8"))
        self.assertEqual(package["manifest"], manifest)
        with self.assertRaises(builder.DispatchSpecError):
            builder.write_package(package, output_root=output)

    def test_independent_validation_metadata_round_trip(self):
        spec = self.spec()
        worker = spec["workers"][0]
        worker["dedupMode"] = "independent-validation"
        worker["independentValidationGroup"] = "alpha.validation"
        worker["independentValidationKey"] = "slot-1"
        package = builder.render_package(spec, repo_root=self.root)
        prompt = next(iter(package["prompts"].values()))
        metadata = contract.parse_prompt_metadata(prompt)
        self.assertEqual("alpha.validation", metadata["independentValidationGroup"])
        self.assertEqual("slot-1", metadata["independentValidationKey"])

    def test_chat_handoff_is_short_and_terminal_policy_is_explicit(self):
        package = builder.render_package(self.spec(), repo_root=self.root)
        chat = package["chatHandoffs"][0]
        self.assertIn(package["manifestPath"], chat)
        self.assertIn("COMPLETE / SUBCOMPLETE / 精确 BLOCKED", chat)


if __name__ == "__main__":
    unittest.main()
