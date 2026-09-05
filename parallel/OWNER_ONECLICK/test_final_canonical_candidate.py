from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import final_canonical_candidate as final


def git(root: Path, *args: str) -> str:
    cp = subprocess.run(["git", *args], cwd=root, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if cp.returncode:
        raise AssertionError(cp.stderr or cp.stdout)
    return cp.stdout.strip()


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class FinalCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory(prefix="p19-final-candidate-")
        self.root = Path(self.td.name)
        git(self.root, "init")
        git(self.root, "config", "user.email", "p19@example.invalid")
        git(self.root, "config", "user.name", "P19 Test")
        for path in final.critical_paths():
            write(self.root, path, f"fixture:{path}\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "p15 implementation")
        self.p15 = git(self.root, "rev-parse", "HEAD")
        write(self.root, final.P16_RUNTIME_PATHS[0], "p16 owner status\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "p16 implementation")
        self.p16 = git(self.root, "rev-parse", "HEAD")
        write(self.root, final.P17_RUNTIME_PATHS[0], "p17 orchestrator\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "p17 implementation")
        self.p17 = git(self.root, "rev-parse", "HEAD")
        write(self.root, final.P18_RUNTIME_PATHS[0], "p18 hud draw ack\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "p18 implementation")
        self.p18 = git(self.root, "rev-parse", "HEAD")
        self._write_result("P15", self.p15, alpha_live=self.p15)
        self._write_result("P16", self.p16)
        self._write_result("P17", self.p17)
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "p15 p16 p17 results")
        self.pre_p18_result = git(self.root, "rev-parse", "HEAD")
        self._write_result("P18", self.p18)
        w3 = {"schema": "wof-alpha-worker-result-v1", "stageId": "ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2", "state": "SUBCOMPLETE", "integrationReady": False, "productProof": {"status": "LIVE_EVIDENCE_REQUIRED", "classification": "INCONCLUSIVE"}, "blocker": "one bounded Owner sample", "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False}}
        write(self.root, final.W3_RESULT, json.dumps(w3))
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "p18 and w3 results")
        self.source = git(self.root, "rev-parse", "HEAD")
        git(self.root, "branch", "alpha-live", self.p15)
        self.out = self.root / "parallel/OWNER_ONECLICK/CANDIDATES/FINAL_CANONICAL"
        self.pointer = self.root / final.DEFAULT_POINTER_REL

    def tearDown(self) -> None:
        self.td.cleanup()

    def _write_result(self, label: str, commit: str, alpha_live: str | None = None) -> None:
        spec = next(row for row in final.STAGES if row[0] == label)
        value = {"schema": "wof-alpha-worker-result-v1", "stageId": spec[1], "dedupKey": spec[2], "state": "COMPLETE", "integrationReady": True, "implementationCommits": [commit], "realWofAcceptance": "NOT_RUN", "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False, "alphaLiveMoved": False}}
        if label == "P18":
            value["drawEvidence"] = {"visibleProof": "NOT_PROVEN"}
        if alpha_live:
            value["alphaLiveCommitObserved"] = alpha_live
        write(self.root, spec[3], json.dumps(value))

    def _fake_manifest(self, root: Path, source: str, canonical_candidate: bool = False) -> dict:
        files = [{"path": path, "gitBlobSha": final._blob_at(root, source, path)} for path in final.refresh.CANONICAL_STACK_PATHS]
        return {"schema": final.refresh.SCHEMA, "packageVersion": "fixture." + source[:12], "sourceCommit": source, "generatedAtUtc": "2026-09-05T00:00:00Z", "generator": final.refresh.GENERATOR, "selectionPolicy": final.refresh.CANONICAL_SELECTION_POLICY, "baseUrl": f"https://example.invalid/{source}/", "components": {"canonicalProductConvergence": {"sourceCommit": source, "chain": "P12->P10->P9/P8->P11", "legacySpatialFallback": False, "alphaLivePromoted": False, "realWofAcceptance": "NOT_RUN", "files": list(final.refresh.CANONICAL_STACK_PATHS)}}, "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False}, "files": sorted(files, key=lambda row: row["path"])}

    def _patch_refresh(self):
        return mock.patch.multiple(final.refresh, generate_manifest=mock.Mock(side_effect=self._fake_manifest), verify_publishable_manifest=mock.Mock(return_value=None))

    def test_missing_p18_is_fail_closed_and_does_not_move_latest_pointer(self) -> None:
        self.pointer.parent.mkdir(parents=True, exist_ok=True)
        self.pointer.write_text("sentinel\n", encoding="utf-8")
        with self._patch_refresh():
            result = final.build(self.root, self.pre_p18_result, self.out, self.pointer)
        self.assertEqual(result["state"], "WAITING_FOR_P18")
        self.assertFalse(result["emitted"])
        self.assertEqual(self.pointer.read_text(encoding="utf-8"), "sentinel\n")
        self.assertFalse(self.out.exists())

    def test_complete_build_is_deterministic_pins_all_stages_and_verifies(self) -> None:
        with self._patch_refresh():
            first = final.build(self.root, self.source, self.out, self.pointer)
            c1 = (self.root / first["candidatePath"]).read_bytes()
            a1 = (self.root / first["attestationPath"]).read_bytes()
            second = final.build(self.root, self.source, self.out, self.pointer)
            c2 = (self.root / second["candidatePath"]).read_bytes()
            a2 = (self.root / second["attestationPath"]).read_bytes()
            verified = final.verify(self.root, self.pointer)
        self.assertEqual(c1, c2)
        self.assertEqual(a1, a2)
        self.assertEqual(first["candidateSha256"], second["candidateSha256"])
        self.assertEqual(first["w3LiveQualification"], "INCONCLUSIVE")
        candidate = json.loads(c1)
        release = candidate["components"]["finalCanonicalRelease"]
        self.assertEqual(set(release["resultPins"]), {"P15", "P16", "P17", "P18"})
        self.assertTrue(all(row["isAncestor"] for row in release["implementationAncestry"]))
        self.assertEqual(set(final.critical_paths()), set(release["criticalRuntimeBlobs"]))
        self.assertEqual(verified["state"], "VERIFIED")
        self.assertFalse(verified["alphaLivePromoted"])
        self.assertEqual(git(self.root, "rev-parse", "alpha-live"), self.p15)

    def test_nonancestor_implementation_commit_is_rejected(self) -> None:
        bad = json.loads((self.root / final.P17_RESULT).read_text(encoding="utf-8"))
        bad["implementationCommits"] = ["f" * 40]
        write(self.root, final.P17_RESULT, json.dumps(bad))
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "bad ancestry fixture")
        bad_source = git(self.root, "rev-parse", "HEAD")
        with self._patch_refresh(), self.assertRaises(final.CandidateError) as ctx:
            final.build(self.root, bad_source, self.out, self.pointer)
        self.assertIn("not an ancestor", str(ctx.exception))

    def test_blob_integrity_rejects_mutated_pin(self) -> None:
        with self._patch_refresh():
            built = final.build(self.root, self.source, self.out, self.pointer)
        candidate = json.loads((self.root / built["candidatePath"]).read_text(encoding="utf-8"))
        candidate["files"][0]["gitBlobSha"] = "0" * 40
        with self.assertRaises(final.CandidateError) as ctx:
            final.verify_manifest_blobs(self.root, candidate)
        self.assertIn("blob mismatch", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
