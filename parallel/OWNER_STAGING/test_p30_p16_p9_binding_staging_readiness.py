from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest

from p21_acceptance import EXPECTED_WORLD_SHA256, staged_p16_readiness, wait_for_staged_p16
from p21_candidate import StagingError
from p21_runtime import STAGED_PACKAGE_MANIFEST_ENV, runtime_environment, stage_candidate_manifest


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def usable_p16(package: str = "pkg") -> dict:
    return {
        "schema": "wof-alpha-canonical-owner-acceptance-evidence-v1",
        "version": 1,
        "packageVersion": package,
        "visibleProof": "NOT_PROVEN",
        "world": {
            "accepted": True,
            "sha256": EXPECTED_WORLD_SHA256,
            "pageTargetId": "page-1",
            "workerTargetId": "worker-1",
        },
        "runtime": {
            "epoch": "runtime-1",
            "authorityKey": "authority-1",
            "rendererEpoch": "renderer-1",
            "rendererAuthority": {"source": "displayed-frame", "target": "page-1"},
        },
        "canonical": {"state": "HUD_INGEST_ACCEPTED", "reason": "READY"},
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
    }


class P30StagingReadinessTests(unittest.TestCase):
    def test_exact_candidate_manifest_is_copied_and_bound_outside_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "repo" / "candidate.json"
            manifest = {
                "schema": "wof-owner-oneclick-package-v1",
                "sourceCommit": "a" * 40,
                "packageVersion": "pkg",
                "files": [
                    {"path": "product/alpha/wof_alpha_canonical_anchor_envelope.js", "gitBlobSha": "1" * 40},
                    {"path": "product/alpha/wof_alpha_canonical_overlay_plan.js", "gitBlobSha": "2" * 40},
                ],
            }
            write_json(source, manifest)
            candidate = {
                "candidatePath": str(source),
                "candidateSha256": sha256(source),
                "sourceCommit": "a" * 40,
                "packageVersion": "pkg",
            }
            run_dir = root / "staging" / "run-1"
            run_dir.mkdir(parents=True)
            staged = stage_candidate_manifest(candidate, run_dir)
            self.assertEqual(staged.parent, run_dir)
            self.assertEqual(sha256(staged), candidate["candidateSha256"])
            self.assertEqual(json.loads(staged.read_text())["files"], manifest["files"])
            env = runtime_environment(candidate, {STAGED_PACKAGE_MANIFEST_ENV: "stale"}, package_manifest=staged)
            self.assertEqual(Path(env[STAGED_PACKAGE_MANIFEST_ENV]), staged.resolve())
            self.assertEqual(env["WOF_ALPHA_ACCEPTANCE_COMMIT"], "a" * 40)
            self.assertEqual(env["WOF_ALPHA_ACCEPTANCE_PACKAGE_VERSION"], "pkg")

    def test_candidate_manifest_change_after_verification_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "candidate.json"
            write_json(source, {"schema": "wof-owner-oneclick-package-v1", "sourceCommit": "b" * 40, "packageVersion": "pkg", "files": []})
            candidate = {"candidatePath": str(source), "candidateSha256": sha256(source), "sourceCommit": "b" * 40, "packageVersion": "pkg"}
            source.write_text(source.read_text() + " ", encoding="utf-8")
            run_dir = root / "run"; run_dir.mkdir()
            with self.assertRaisesRegex(StagingError, "changed after candidate verification"):
                stage_candidate_manifest(candidate, run_dir)

    def test_verifying_world_is_never_usable_staged_p16(self):
        raw = usable_p16()
        raw["world"]["accepted"] = False
        raw["canonical"]["state"] = "VERIFYING_WORLD"
        ready, reason = staged_p16_readiness(raw, {"packageVersion": "pkg"})
        self.assertFalse(ready)
        self.assertEqual(reason, "P16_WORLD_NOT_ACCEPTED")

    def test_usable_p16_requires_exact_world_and_complete_runtime_renderer_authority(self):
        base = usable_p16()
        ready, reason = staged_p16_readiness(base, {"packageVersion": "pkg"})
        self.assertTrue(ready)
        self.assertEqual(reason, "USABLE")
        mutations = {
            "wrong world": lambda x: x["world"].__setitem__("sha256", "0" * 64),
            "runtime epoch": lambda x: x["runtime"].__setitem__("epoch", ""),
            "authority key": lambda x: x["runtime"].__setitem__("authorityKey", None),
            "renderer epoch": lambda x: x["runtime"].__setitem__("rendererEpoch", ""),
            "renderer authority": lambda x: x["runtime"].__setitem__("rendererAuthority", {}),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                raw = json.loads(json.dumps(base)); mutate(raw)
                self.assertFalse(staged_p16_readiness(raw, {"packageVersion": "pkg"})[0])

    def test_wait_loop_does_not_copy_early_snapshot_but_copies_usable_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); default = root / "P16.json"; output = root / "staged.json"
            early = usable_p16(); early["world"]["accepted"] = False; early["canonical"]["state"] = "VERIFYING_WORLD"
            write_json(default, early)
            started = time.time() - 0.1
            self.assertIsNone(wait_for_staged_p16(default, output, {"packageVersion": "pkg"}, started, None, 0.0))
            self.assertFalse(output.exists())
            write_json(default, usable_p16())
            result = wait_for_staged_p16(default, output, {"packageVersion": "pkg"}, started, None, 0.0)
            self.assertIsNotNone(result)
            self.assertEqual(result["readiness"], "USABLE")
            self.assertEqual(json.loads(output.read_text())["canonical"]["state"], "HUD_INGEST_ACCEPTED")


if __name__ == "__main__":
    unittest.main()
