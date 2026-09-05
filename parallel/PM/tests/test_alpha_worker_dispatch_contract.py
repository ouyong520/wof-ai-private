import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL_PATH = Path(__file__).resolve().parents[1] / "tools" / "alpha_worker_dispatch_contract.py"
SPEC = importlib.util.spec_from_file_location("alpha_worker_dispatch_contract", TOOL_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def stage(n=1):
    return f"ALPHA_EXAMPLE_WORKER_{n}"


def prompt_text(stage_id, manifest_path="parallel/PM/DISPATCH_MANIFESTS/EXAMPLE.json", **overrides):
    values = {
        "stageId": stage_id,
        "dedupProtocol": "v2",
        "dedupKey": f"alpha.example.worker-{stage_id.rsplit('_', 1)[-1].lower()}",
        "dedupMode": "exclusive",
        "resultProtocol": MODULE.RESULT_PROTOCOL,
        "resultJsonPath": MODULE.result_contract(stage_id)["resultJsonPath"],
        "resultMdPath": MODULE.result_contract(stage_id)["resultMdPath"],
        "terminalCommitPrefix": MODULE.result_contract(stage_id)["terminalCommitPrefix"],
        "dispatchManifestPath": manifest_path,
    }
    values.update(overrides)
    header = "\n".join(f"{k}: `{v}`" for k, v in values.items() if v is not None)
    return header + "\n\n# Example\n\nTerminal reporting must follow `" + MODULE.FEEDBACK_PROTOCOL_PATH + "`.\n"


def worker(n=1, **overrides):
    sid = stage(n)
    contract = MODULE.result_contract(sid)
    item = {
        "stageId": sid,
        "promptPath": f"parallel/PM/ALPHA_EXAMPLE_WORKER_{n}_START_PROMPT.md",
        "dedupKey": f"alpha.example.worker-{n}",
        "dedupProtocol": "v2",
        "dedupMode": "exclusive",
        "resultProtocol": MODULE.RESULT_PROTOCOL,
        **contract,
    }
    item.update(overrides)
    return item


def manifest(count=1):
    return {
        "schema": MODULE.MANIFEST_SCHEMA,
        "dispatchId": f"ALPHA_EXAMPLE_{count}_WORKER",
        "repository": "ouyong520/wof-ai-private",
        "authorityPath": "parallel/PM/ALPHA_EXAMPLE_DISPATCH.md",
        "immutable": True,
        "workers": [worker(i) for i in range(1, count + 1)],
    }


class PromptValidationTests(unittest.TestCase):
    def test_valid_prompt(self):
        self.assertEqual([], MODULE.validate_prompt_text(prompt_text(stage())))

    def test_missing_required_prompt_metadata_rejected(self):
        for field in (
            "stageId",
            "dedupProtocol",
            "dedupKey",
            "dedupMode",
            "resultJsonPath",
            "resultMdPath",
            "terminalCommitPrefix",
            "resultProtocol",
        ):
            text = prompt_text(stage(), **{field: None})
            errors = MODULE.validate_prompt_text(text)
            self.assertTrue(any(field in error for error in errors), (field, errors))

    def test_deterministic_result_path_mismatch_rejected(self):
        errors = MODULE.validate_prompt_text(
            prompt_text(stage(), resultJsonPath="parallel/PM/RESULTS/WRONG_RESULT.json")
        )
        self.assertTrue(any("resultJsonPath" in error and "expected" in error for error in errors))

    def test_missing_terminal_reporting_protocol_rejected(self):
        text = prompt_text(stage()).replace(MODULE.FEEDBACK_PROTOCOL_PATH, "parallel/PM/OTHER.md")
        errors = MODULE.validate_prompt_text(text)
        self.assertTrue(any("terminalReporting" in error for error in errors))

    def test_optional_manifest_link_mismatch_rejected(self):
        errors = MODULE.validate_prompt_text(
            prompt_text(stage()),
            manifest_path="parallel/PM/DISPATCH_MANIFESTS/OTHER.json",
        )
        self.assertTrue(any("dispatchManifestPath" in error for error in errors))

    def test_independent_validation_requires_slot_metadata(self):
        errors = MODULE.validate_prompt_text(prompt_text(stage(), dedupMode="independent-validation"))
        self.assertTrue(any("independentValidationGroup" in error for error in errors))
        self.assertTrue(any("independentValidationKey" in error for error in errors))


class ManifestValidationTests(unittest.TestCase):
    def test_valid_solo_two_three_worker_manifests(self):
        for count in (1, 2, 3):
            self.assertEqual([], MODULE.validate_manifest_data(manifest(count)), count)

    def test_bootstrap_draft_manifest_is_accepted_when_worker_contract_is_complete(self):
        data = manifest(1)
        data["schema"] = "wof-alpha-dispatch-manifest-v1-draft"
        data["workers"][0].pop("dedupProtocol")
        data["workers"][0].pop("dedupMode")
        self.assertEqual([], MODULE.validate_manifest_data(data))

    def test_malformed_manifest_worker_entry_rejected(self):
        data = manifest(1)
        data["workers"] = ["not-an-object"]
        errors = MODULE.validate_manifest_data(data)
        self.assertTrue(any("must be an object" in error for error in errors))

    def test_duplicate_result_json_collision_rejected(self):
        data = manifest(2)
        data["workers"][1]["resultJsonPath"] = data["workers"][0]["resultJsonPath"]
        errors = MODULE.validate_manifest_data(data)
        self.assertTrue(any("duplicate RESULT.json path" in error for error in errors))

    def test_duplicate_result_md_collision_rejected(self):
        data = manifest(2)
        data["workers"][1]["resultMdPath"] = data["workers"][0]["resultMdPath"]
        errors = MODULE.validate_manifest_data(data)
        self.assertTrue(any("duplicate RESULT.md path" in error for error in errors))

    def test_shared_mutable_status_dashboard_rejected(self):
        data = manifest(2)
        for item in data["workers"]:
            item["statusPath"] = "parallel/PM/STATUS/dispatch.json"
        errors = MODULE.validate_manifest_data(data)
        self.assertTrue(any("shared mutable worker status/dashboard path" in error for error in errors))

    def test_global_dashboard_rejected(self):
        data = manifest(1)
        data["dashboardPath"] = "parallel/PM/STATUS/global.json"
        errors = MODULE.validate_manifest_data(data)
        self.assertTrue(any("global mutable status/dashboard" in error for error in errors))

    def test_immutable_manifest_required(self):
        data = manifest(1)
        data["immutable"] = False
        errors = MODULE.validate_manifest_data(data)
        self.assertTrue(any("immutable" in error for error in errors))

    def test_four_workers_rejected(self):
        errors = MODULE.validate_manifest_data(manifest(4))
        self.assertTrue(any("worker count must be 1, 2, or 3" in error for error in errors))


class DispatchValidationTests(unittest.TestCase):
    def test_manifest_prompt_membership_and_exact_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "parallel/PM/DISPATCH_MANIFESTS/EXAMPLE.json"
            manifest_path.parent.mkdir(parents=True)
            data = manifest(2)
            manifest_path.write_text(json.dumps(data), encoding="utf-8")
            for i, item in enumerate(data["workers"], start=1):
                prompt_path = root / item["promptPath"]
                prompt_path.parent.mkdir(parents=True, exist_ok=True)
                prompt_path.write_text(prompt_text(stage(i)), encoding="utf-8")
            self.assertEqual([], MODULE.validate_dispatch(manifest_path, root))

    def test_manifest_prompt_stage_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "parallel/PM/DISPATCH_MANIFESTS/EXAMPLE.json"
            manifest_path.parent.mkdir(parents=True)
            data = manifest(1)
            manifest_path.write_text(json.dumps(data), encoding="utf-8")
            prompt_path = root / data["workers"][0]["promptPath"]
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt_text("ALPHA_DIFFERENT_WORKER"), encoding="utf-8")
            errors = MODULE.validate_dispatch(manifest_path, root)
            self.assertTrue(any("manifest/prompt mismatch" in error for error in errors))

    def test_cli_machine_readable_output(self):
        proc = subprocess.run(
            [sys.executable, str(TOOL_PATH), "derive", stage()],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual("wof-alpha-dispatch-contract-validation-v1", payload["schema"])
        self.assertEqual(MODULE.result_contract(stage()), payload["contract"])


if __name__ == "__main__":
    unittest.main()
