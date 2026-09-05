from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import exact_candidate_staging_acceptance as p21


def run_git(root: Path, *args: str) -> str:
    cp = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return cp.stdout.strip()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Fixture:
    def __init__(self, root: Path):
        self.root = root
        run_git(root, "init", "-b", "main")
        run_git(root, "config", "user.email", "p21@example.invalid")
        run_git(root, "config", "user.name", "P21 Fixture")
        runtime = root / p21.RUNTIME_REL
        runtime.parent.mkdir(parents=True, exist_ok=True)
        runtime.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
        orchestrator = root / p21.P17_REL
        orchestrator.parent.mkdir(parents=True, exist_ok=True)
        orchestrator.write_text(
            """from pathlib import Path\nimport argparse,hashlib,json,subprocess\np=argparse.ArgumentParser()\np.add_argument('--repo-root');p.add_argument('--output-dir');p.add_argument('--candidate-metadata');p.add_argument('--p16-evidence');p.add_argument('--p18-evidence');p.add_argument('--invoke-w3',action='store_true');p.add_argument('--w3-output-root');p.add_argument('--w3-qualification')\na=p.parse_args()\nrepo=Path(a.repo_root); cand=Path(a.candidate_metadata); raw=json.loads(cand.read_text())\nhead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()\nassert head==raw['sourceCommit']\nout=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)\nif a.invoke_w3 and a.w3_output_root:\n w=Path(a.w3_output_root);w.mkdir(parents=True,exist_ok=True);(w/'LATEST_W3_RENDER_SOURCE_QUALIFICATION.json').write_text(json.dumps({'schema':'wof-w3-long-qualification-latest-v1','qualificationJson':'q.json'}));(w/'q.json').write_text(json.dumps({'schema':'wof-render-source-qualification-v1','status':'INCONCLUSIVE'}))\nh=hashlib.sha256(cand.read_bytes()).hexdigest()\nb={'schema':'wof-alpha-final-acceptance-bundle-v1','candidate':{'sourceCommit':raw['sourceCommit'],'packageVersion':raw['packageVersion'],'contentSha256':h},'automaticDecision':'W3_INCONCLUSIVE' if a.invoke_w3 else 'WAITING_CANONICAL_RUNTIME_EVIDENCE','visibleProof':'NOT_PROVEN','safety':{'alphaLiveMoved':False}}\n(out/'ALPHA_FINAL_ACCEPTANCE_BUNDLE.json').write_text(json.dumps(b))\n""",
            encoding="utf-8",
        )
        extra = root / "product/alpha/wof_alpha_hud.js"
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text("// fixture\n", encoding="utf-8")
        run_git(root, "add", ".")
        run_git(root, "commit", "-m", "candidate source")
        self.source = run_git(root, "rev-parse", "HEAD")
        run_git(root, "branch", "alpha-live", self.source)
        self.blobs = {
            p21.RUNTIME_REL.as_posix(): run_git(root, "rev-parse", f"{self.source}:{p21.RUNTIME_REL.as_posix()}"),
            p21.P17_REL.as_posix(): run_git(root, "rev-parse", f"{self.source}:{p21.P17_REL.as_posix()}"),
            "product/alpha/wof_alpha_hud.js": run_git(root, "rev-parse", f"{self.source}:product/alpha/wof_alpha_hud.js"),
        }
        commits = [self.source]
        stage_rows = {label: {"state": "COMPLETE", "integrationReady": True, "implementationCommits": commits} for label in p21.REQUIRED_STAGES}
        ancestry = [{"stage": label, "commit": self.source, "isAncestor": True} for label in p21.REQUIRED_STAGES]
        self.candidate = {
            "schema": p21.CANDIDATE_SCHEMA,
            "packageVersion": "fixture.package",
            "sourceCommit": self.source,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False},
            "files": [{"path": k, "gitBlobSha": v} for k, v in sorted(self.blobs.items())],
            "components": {"finalCanonicalRelease": {
                "sourceCommit": self.source,
                "resultPins": stage_rows,
                "implementationAncestry": ancestry,
                "criticalRuntimeBlobs": self.blobs,
                "ownerVisualAcceptance": "NOT_RUN",
                "realWofAcceptance": "NOT_RUN",
                "alphaLivePromoted": False,
                "legacySpatialFallback": False,
                "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
            }},
        }
        cpath = root / "parallel/OWNER_ONECLICK/CANDIDATES/FINAL_CANONICAL/candidate.json"
        write_json(cpath, self.candidate)
        att = {
            "schema": p21.ATTESTATION_SCHEMA,
            "version": 1,
            "sourceCommit": self.source,
            "packageVersion": "fixture.package",
            "candidatePath": cpath.relative_to(root).as_posix(),
            "candidateSha256": sha(cpath),
            "stageResults": stage_rows,
            "implementationAncestry": ancestry,
            "criticalRuntimeBlobs": self.blobs,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False},
            "w3LiveQualification": "NOT_RUN",
            "ownerVisualAcceptance": "NOT_RUN",
            "realWofAcceptance": "NOT_RUN",
            "alphaLivePromoted": False,
        }
        apath = cpath.with_suffix(".attestation.json")
        write_json(apath, att)
        pointer = {
            "schema": p21.POINTER_SCHEMA,
            "version": 1,
            "state": "READY",
            "sourceCommit": self.source,
            "packageVersion": "fixture.package",
            "candidatePath": cpath.relative_to(root).as_posix(),
            "candidateSha256": sha(cpath),
            "attestationPath": apath.relative_to(root).as_posix(),
            "attestationSha256": sha(apath),
            "selectedFileCount": len(self.blobs),
            "stageStates": {label: "COMPLETE" for label in p21.REQUIRED_STAGES},
            "w3LiveQualification": "NOT_RUN",
            "ownerVisualAcceptance": "NOT_RUN",
            "alphaLivePromoted": False,
        }
        self.pointer = root / p21.POINTER_REL
        write_json(self.pointer, pointer)


class P21Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.fx = Fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_resolver_exact_candidate(self):
        value = p21.resolve_p19_candidate(self.root)
        self.assertEqual(value["sourceCommit"], self.fx.source)
        self.assertEqual(value["packageVersion"], "fixture.package")
        self.assertEqual(value["criticalRuntimeBlobs"], self.fx.blobs)
        self.assertFalse(value["alphaLivePromoted"])

    def test_missing_p19_fails_closed(self):
        self.fx.pointer.unlink()
        with self.assertRaises(p21.WaitingForP19):
            p21.resolve_p19_candidate(self.root)
        self.assertEqual(run_git(self.root, "rev-parse", "refs/heads/alpha-live"), self.fx.source)

    def test_waiting_receipt_proves_alpha_live_unchanged_without_staging(self):
        self.fx.pointer.unlink()
        before = p21.observe_git_state(self.root)
        output = Path(self.tmp.name) / "waiting-output"
        receipt, rc = p21.run_staged_acceptance(
            repo_root=self.root, pointer_path=None, staging_root=Path(self.tmp.name) / "staging",
            output_root=output, permanent_repo=None, python_exe=sys.executable, browser="chrome",
            host="127.0.0.1", port=9223, evidence_timeout=0, stop_permanent_runtime=False,
        )
        self.assertEqual(rc, 4)
        self.assertEqual(receipt["state"], p21.WAITING_FOR_P19)
        self.assertFalse(receipt["alphaLiveMoved"])
        self.assertFalse((Path(self.tmp.name) / "staging").exists())
        after = p21.observe_git_state(self.root)
        self.assertEqual([], p21.compare_permanent_state(before, after))

    def test_hash_mismatch_is_rejected(self):
        raw = json.loads(self.fx.pointer.read_text())
        raw["candidateSha256"] = "0" * 64
        write_json(self.fx.pointer, raw)
        with self.assertRaisesRegex(p21.StagingError, "SHA-256 mismatch"):
            p21.resolve_p19_candidate(self.root)

    def test_detached_worktree_and_cleanup_never_move_alpha_live(self):
        before = p21.observe_git_state(self.root)
        base = Path(self.tmp.name) / "staging"
        stage = p21.create_staging_worktree(self.root, self.fx.source, base)
        checkout = Path(stage["checkout"])
        self.assertEqual(run_git(checkout, "rev-parse", "HEAD"), self.fx.source)
        detached = subprocess.run(["git", "symbolic-ref", "-q", "HEAD"], cwd=checkout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertNotEqual(detached.returncode, 0)
        during = p21.observe_git_state(self.root)
        self.assertEqual(before["alphaLiveLocal"], during["alphaLiveLocal"])
        p21.cleanup_staging_worktree(self.root, base, Path(stage["runDir"]), checkout)
        # cleanup is intentionally idempotent
        p21.cleanup_staging_worktree(self.root, base, Path(stage["runDir"]), checkout)
        after = p21.observe_git_state(self.root)
        self.assertEqual([], p21.compare_permanent_state(before, after))

    def test_runtime_command_is_exact_staged_root_and_fail_closed_env(self):
        base = Path(self.tmp.name) / "staging"
        stage = p21.create_staging_worktree(self.root, self.fx.source, base)
        checkout = Path(stage["checkout"])
        candidate = p21.resolve_p19_candidate(self.root)
        env = p21.runtime_environment(candidate, {"WOF_ALPHA_FIXED_DRAW_SMOKE": "1", "WOF_ALPHA_CURRENT_MAIN_SOURCE": "1"})
        cmd = p21.build_runtime_command(sys.executable, checkout, Path(self.tmp.name) / "results", "chrome")
        self.assertIn(str(checkout), cmd)
        self.assertEqual(env["WOF_ALPHA_ACCEPTANCE_COMMIT"], self.fx.source)
        self.assertEqual(env["WOF_ALPHA_ACCEPTANCE_MODE"], "STAGED_PREPROMOTION")
        self.assertEqual(env["WOF_ALPHA_OWNER_NAVIGATES"], "1")
        self.assertNotIn("WOF_ALPHA_FIXED_DRAW_SMOKE", env)
        self.assertNotIn("WOF_ALPHA_CURRENT_MAIN_SOURCE", env)
        p21.cleanup_staging_worktree(self.root, base, Path(stage["runDir"]), checkout)

    def test_p17_bridge_binds_same_candidate_and_ref_is_unchanged(self):
        before = p21.observe_git_state(self.root)
        candidate = p21.resolve_p19_candidate(self.root)
        base = Path(self.tmp.name) / "staging"
        stage = p21.create_staging_worktree(self.root, self.fx.source, base)
        checkout = Path(stage["checkout"])
        out = Path(self.tmp.name) / "p17"
        result = p21.run_p17(
            sys.executable, checkout, candidate, out,
            Path(self.tmp.name) / "p16.json", Path(self.tmp.name) / "p18.json",
            invoke_w3=True, w3_output_root=Path(self.tmp.name) / "w3",
        )
        self.assertEqual(result["automaticDecision"], "W3_INCONCLUSIVE")
        self.assertEqual(result["visibleProof"], "NOT_PROVEN")
        p21.cleanup_staging_worktree(self.root, base, Path(stage["runDir"]), checkout)
        after = p21.observe_git_state(self.root)
        self.assertEqual(before["alphaLiveLocal"], after["alphaLiveLocal"])
        self.assertEqual([], p21.compare_permanent_state(before, after))


if __name__ == "__main__":
    unittest.main()
