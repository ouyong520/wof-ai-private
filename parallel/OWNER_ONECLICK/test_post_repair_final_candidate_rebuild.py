from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import post_repair_final_candidate_rebuild as rebuild


def git(root: Path, *args: str, check: bool = True) -> str:
    cp = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and cp.returncode:
        raise AssertionError(cp.stderr or cp.stdout)
    return cp.stdout.strip()


def write(root: Path, rel: str, value: object) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


class PostRepairFinalCandidateRebuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory(prefix="p33-post-repair-")
        self.root = Path(self.td.name)
        git(self.root, "init")
        git(self.root, "config", "user.email", "p33@example.invalid")
        git(self.root, "config", "user.name", "P33 Test")

        write(self.root, "fixture.txt", "base\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "base")
        self.primary_branch = git(self.root, "branch", "--show-current")
        self.base = git(self.root, "rev-parse", "HEAD")

        self.synthetic: list[rebuild.RepairRequirement] = []
        for index, original in enumerate(rebuild.REQUIRED_ACCEPTED_REPAIRS, start=1):
            write(self.root, "fixture.txt", f"repair-{index}\n")
            git(self.root, "add", ".")
            git(self.root, "commit", "-m", f"repair {index}")
            tested = git(self.root, "rev-parse", "HEAD")
            self.synthetic.append(
                rebuild.RepairRequirement(
                    original.stage_id,
                    original.dedup_key,
                    tested,
                    original.result_path,
                )
            )

        self.required_patch = mock.patch.object(
            rebuild,
            "REQUIRED_ACCEPTED_REPAIRS",
            tuple(self.synthetic),
        )
        self.required_patch.start()

        git(self.root, "branch", "missing-last", self.synthetic[-2].tested_commit)

        for item in self.synthetic:
            write(
                self.root,
                item.result_path,
                {
                    "schema": "wof-alpha-worker-result-v1",
                    "stageId": item.stage_id,
                    "dedupKey": item.dedup_key,
                    "state": "COMPLETE",
                    "testedCommit": item.tested_commit,
                    "integrationReady": True,
                    "safety": {
                        "readOnly": True,
                        "ramWrites": 0,
                        "inputInjection": False,
                        "alphaLiveMoved": False,
                    },
                    "alphaLiveMoved": False,
                },
            )
        write(
            self.root,
            rebuild.P32_BLOCKED.result_path,
            {
                "schema": "wof-alpha-worker-result-v1",
                "stageId": rebuild.P32_BLOCKED.stage_id,
                "dedupKey": rebuild.P32_BLOCKED.dedup_key,
                "state": "BLOCKED",
                "testedCommit": rebuild.P32_BLOCKED.tested_commit,
                "integrationReady": False,
                "safety": {
                    "readOnly": True,
                    "ramWrites": 0,
                    "inputInjection": False,
                },
                "alphaLiveMoved": False,
                "promotionPerformed": False,
            },
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "terminal repair authority")
        self.source = git(self.root, "rev-parse", "HEAD")

        git(self.root, "checkout", "missing-last")
        for item in self.synthetic:
            write(
                self.root,
                item.result_path,
                {
                    "schema": "wof-alpha-worker-result-v1",
                    "stageId": item.stage_id,
                    "dedupKey": item.dedup_key,
                    "state": "COMPLETE",
                    "testedCommit": item.tested_commit,
                    "integrationReady": True,
                    "safety": {
                        "readOnly": True,
                        "ramWrites": 0,
                        "inputInjection": False,
                        "alphaLiveMoved": False,
                    },
                },
            )
        write(
            self.root,
            rebuild.P32_BLOCKED.result_path,
            {
                "schema": "wof-alpha-worker-result-v1",
                "stageId": rebuild.P32_BLOCKED.stage_id,
                "dedupKey": rebuild.P32_BLOCKED.dedup_key,
                "state": "BLOCKED",
                "testedCommit": rebuild.P32_BLOCKED.tested_commit,
                "integrationReady": False,
                "safety": {
                    "readOnly": True,
                    "ramWrites": 0,
                    "inputInjection": False,
                },
            },
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "authority without last repair ancestry")
        self.missing_source = git(self.root, "rev-parse", "HEAD")
        git(self.root, "checkout", self.primary_branch)

        git(self.root, "branch", "alpha-live", self.base)

        self.out = self.root / "parallel/OWNER_ONECLICK/CANDIDATES/FINAL_CANONICAL"
        self.pointer = self.root / rebuild.DEFAULT_POINTER_REL

    def tearDown(self) -> None:
        self.required_patch.stop()
        self.td.cleanup()

    def _fake_build(self, root: Path, source: str, output_dir: Path, pointer_path: Path) -> dict:
        package = "fixture." + source[:12]
        candidate = {
            "schema": "fixture-candidate",
            "sourceCommit": source,
            "packageVersion": package,
            "generatedAtUtc": "2026-09-05T00:00:00Z",
            "safety": {
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
                "legacySpatialFallback": False,
            },
            "files": [],
        }
        candidate_path = output_dir / f"candidate-{source[:12]}.json"
        candidate_rel = candidate_path.relative_to(root).as_posix()
        candidate_bytes = rebuild.final._json_bytes(candidate)
        candidate_sha = hashlib.sha256(candidate_bytes).hexdigest()
        rebuild.final._atomic_write(candidate_path, candidate_bytes)

        attestation = {
            "schema": "fixture-attestation",
            "sourceCommit": source,
            "packageVersion": package,
            "candidatePath": candidate_rel,
            "candidateSha256": candidate_sha,
            "ownerVisualAcceptance": "NOT_RUN",
            "alphaLivePromoted": False,
            "safety": {
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
            },
        }
        attestation_path = output_dir / f"candidate-{source[:12]}.attestation.json"
        attestation_rel = attestation_path.relative_to(root).as_posix()
        attestation_bytes = rebuild.final._json_bytes(attestation)
        attestation_sha = hashlib.sha256(attestation_bytes).hexdigest()
        rebuild.final._atomic_write(attestation_path, attestation_bytes)

        pointer = {
            "schema": rebuild.final.POINTER_SCHEMA,
            "version": 1,
            "state": "READY",
            "sourceCommit": source,
            "packageVersion": package,
            "candidatePath": candidate_rel,
            "candidateSha256": candidate_sha,
            "attestationPath": attestation_rel,
            "attestationSha256": attestation_sha,
            "alphaLivePromoted": False,
            "ownerVisualAcceptance": "NOT_RUN",
        }
        rebuild.final._atomic_write(pointer_path, rebuild.final._json_bytes(pointer))
        return {
            "state": "READY",
            "emitted": True,
            "sourceCommit": source,
            "packageVersion": package,
            "candidatePath": candidate_rel,
            "candidateSha256": candidate_sha,
            "attestationPath": attestation_rel,
            "attestationSha256": attestation_sha,
            "alphaLivePromoted": False,
        }

    def _fake_verify(self, root: Path, pointer_path: Path) -> dict:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        candidate_path = root / pointer["candidatePath"]
        attestation_path = root / pointer["attestationPath"]
        candidate_sha = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
        attestation_sha = hashlib.sha256(attestation_path.read_bytes()).hexdigest()
        if candidate_sha != pointer["candidateSha256"]:
            raise rebuild.final.CandidateError("latest pointer candidate SHA256 mismatch")
        if attestation_sha != pointer["attestationSha256"]:
            raise rebuild.final.CandidateError("latest pointer attestation SHA256 mismatch")
        return {
            "state": "VERIFIED",
            "sourceCommit": pointer["sourceCommit"],
            "packageVersion": pointer["packageVersion"],
            "candidatePath": pointer["candidatePath"],
            "candidateSha256": candidate_sha,
            "attestationPath": pointer["attestationPath"],
            "attestationSha256": attestation_sha,
            "alphaLivePromoted": False,
        }

    def _patch_base(self):
        return mock.patch.multiple(
            rebuild.final,
            build=mock.Mock(side_effect=self._fake_build),
            verify=mock.Mock(side_effect=self._fake_verify),
        )

    def test_exact_source_containing_all_required_repairs_builds_and_verifies(self) -> None:
        alpha_before = git(self.root, "rev-parse", "alpha-live")
        with self._patch_base():
            result = rebuild.build(self.root, self.source, self.out, self.pointer)
            verified = rebuild.verify(self.root, self.pointer)
        self.assertEqual(result["state"], "VERIFIED")
        self.assertEqual(verified["sourceCommit"], self.source)
        self.assertEqual(verified["requiredTestedCommits"], rebuild._required_map())
        self.assertFalse(verified["p32Required"])
        self.assertEqual(git(self.root, "rev-parse", "alpha-live"), alpha_before)

        pointer = json.loads(self.pointer.read_text(encoding="utf-8"))
        manifest = json.loads((self.root / pointer["manifestPath"]).read_text(encoding="utf-8"))
        self.assertEqual(pointer["requiredTestedCommits"], rebuild._required_map())
        self.assertEqual(set(pointer["requiredTestedCommits"]), {item.stage_id for item in self.synthetic})
        self.assertNotIn(rebuild.P32_BLOCKED.stage_id, pointer["requiredTestedCommits"])
        self.assertEqual(manifest["excludedBlockedRepairs"][0]["stageId"], rebuild.P32_BLOCKED.stage_id)
        self.assertFalse(manifest["excludedBlockedRepairs"][0]["required"])
        self.assertFalse(pointer["alphaLiveMoved"])
        self.assertFalse(pointer["alphaLivePromoted"])
        self.assertFalse(pointer["promotionPerformed"])

    def test_missing_one_required_tested_commit_fails_closed_and_preserves_pointer(self) -> None:
        self.pointer.parent.mkdir(parents=True, exist_ok=True)
        sentinel = b'{"legacy":"sentinel"}\n'
        self.pointer.write_bytes(sentinel)
        with self._patch_base(), self.assertRaises(rebuild.RebuildError) as ctx:
            rebuild.build(self.root, self.missing_source, self.out, self.pointer)
        self.assertIn("SOURCE_COMMIT_MISSING_REQUIRED_TESTED_COMMIT", str(ctx.exception))
        self.assertEqual(self.pointer.read_bytes(), sentinel)

    def test_symbolic_or_abbreviated_source_is_rejected(self) -> None:
        with self.assertRaises(rebuild.RebuildError) as ctx:
            rebuild.build(self.root, "HEAD", self.out, self.pointer)
        self.assertIn("EXACT_SOURCE_COMMIT_REQUIRED", str(ctx.exception))
        with self.assertRaises(rebuild.RebuildError):
            rebuild.build(self.root, self.source[:12], self.out, self.pointer)

    def test_historical_p19_source_is_explicitly_rejected(self) -> None:
        with self.assertRaises(rebuild.RebuildError) as ctx:
            rebuild._assert_not_historical_source(rebuild.HISTORICAL_P19_SOURCE_COMMIT)
        self.assertIn("STALE_P19_SOURCE_COMMIT_REJECTED", str(ctx.exception))

    def test_legacy_pointer_without_post_repair_manifest_is_rejected(self) -> None:
        self.pointer.parent.mkdir(parents=True, exist_ok=True)
        self.pointer.write_text(
            json.dumps(
                {
                    "schema": rebuild.final.POINTER_SCHEMA,
                    "state": "READY",
                    "sourceCommit": self.source,
                    "packageVersion": "fixture",
                    "candidatePath": "old.json",
                    "candidateSha256": "0" * 64,
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaises(rebuild.RebuildError) as ctx:
            rebuild.verify(self.root, self.pointer)
        self.assertIn("STALE_PRE_REPAIR_POINTER_REJECTED", str(ctx.exception))

    def test_manifest_hash_mismatch_is_rejected(self) -> None:
        with self._patch_base():
            rebuild.build(self.root, self.source, self.out, self.pointer)
            pointer = json.loads(self.pointer.read_text(encoding="utf-8"))
            manifest_path = self.root / pointer["manifestPath"]
            manifest_path.write_bytes(manifest_path.read_bytes() + b" ")
            with self.assertRaises(rebuild.RebuildError) as ctx:
                rebuild.verify(self.root, self.pointer)
        self.assertIn("manifest SHA256 exact readback mismatch", str(ctx.exception))

    def test_candidate_sha_mismatch_is_rejected(self) -> None:
        with self._patch_base():
            rebuild.build(self.root, self.source, self.out, self.pointer)
            pointer = json.loads(self.pointer.read_text(encoding="utf-8"))
            candidate_path = self.root / pointer["candidatePath"]
            candidate_path.write_bytes(candidate_path.read_bytes() + b" ")
            with self.assertRaises(rebuild.final.CandidateError):
                rebuild.verify(self.root, self.pointer)

    def test_manifest_source_and_package_mismatch_are_rejected_even_with_updated_hash(self) -> None:
        for field, value in (("sourceCommit", "f" * 40), ("packageVersion", "wrong.package")):
            with self.subTest(field=field):
                with self._patch_base():
                    rebuild.build(self.root, self.source, self.out, self.pointer)
                    pointer = json.loads(self.pointer.read_text(encoding="utf-8"))
                    manifest_path = self.root / pointer["manifestPath"]
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    manifest[field] = value
                    raw = rebuild.final._json_bytes(manifest)
                    manifest_path.write_bytes(raw)
                    pointer["manifestSha256"] = hashlib.sha256(raw).hexdigest()
                    self.pointer.write_bytes(rebuild.final._json_bytes(pointer))
                    with self.assertRaises(rebuild.RebuildError):
                        rebuild.verify(self.root, self.pointer)

    def test_repeated_build_metadata_is_byte_deterministic(self) -> None:
        with self._patch_base():
            first = rebuild.build(self.root, self.source, self.out, self.pointer)
            pointer1 = self.pointer.read_bytes()
            manifest1 = (self.root / first["manifestPath"]).read_bytes()
            second = rebuild.build(self.root, self.source, self.out, self.pointer)
            pointer2 = self.pointer.read_bytes()
            manifest2 = (self.root / second["manifestPath"]).read_bytes()
        self.assertEqual(pointer1, pointer2)
        self.assertEqual(manifest1, manifest2)
        self.assertEqual(first["candidateSha256"], second["candidateSha256"])
        self.assertEqual(first["manifestSha256"], second["manifestSha256"])

    def test_windows_entrypoint_requires_exact_source_and_uses_post_repair_wrapper(self) -> None:
        cmd = Path(__file__).with_name("WOF_ALPHA_BUILD_FINAL_CANONICAL_CANDIDATE.cmd").read_text(
            encoding="utf-8"
        )
        self.assertIn("post_repair_final_candidate_rebuild.py", cmd)
        self.assertIn("%~1", cmd)
        self.assertNotIn("--source HEAD", cmd)


if __name__ == "__main__":
    unittest.main(verbosity=2)
