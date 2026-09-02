from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from training.farm import real_wof_proof_owner_runner as owner


class RealWofOwnerRunnerTests(unittest.TestCase):
    def _make_repo(self, root: Path) -> tuple[Path, str]:
        repo = root / "repo"
        farm = repo / "training" / "farm"
        farm.mkdir(parents=True)
        for name in owner._SOURCE_GUARD_FILES:
            (farm / name).write_text("{}\n", encoding="utf-8")
        (farm / "determinism.schema.json").write_text(
            json.dumps({
                "type": "object",
                "required": [
                    "schema", "runId", "status", "reasonCode", "message",
                    "proofScope", "realWofProof", "sourceNamespace", "firstDivergence",
                ],
                "properties": {
                    "schema": {"const": "wof-training-farm-determinism-result-v1"},
                    "status": {"enum": ["PASS", "FAIL", "SKIP", "ERROR"]},
                    "sourceNamespace": {"const": "stable-retro-fbneo"},
                },
                "additionalProperties": True,
            }),
            encoding="utf-8",
        )
        (farm / "determinism_actions.example.json").write_text(
            json.dumps([
                {
                    "frames": 8,
                    "inputs": [
                        {"player": 0, "pressed": []},
                        {"player": 1, "pressed": []},
                        {"player": 2, "pressed": []},
                        {"player": 3, "pressed": []},
                    ],
                }
            ]),
            encoding="utf-8",
        )
        guard, _ = owner._source_guard(farm)
        return repo, guard

    def _preflight(self, repo: Path, evidence: Path, guard: str) -> owner.Preflight:
        return owner.Preflight(
            ok=True,
            reason="READY",
            repo_root=repo,
            evidence_root=evidence,
            rom_path=evidence.parent / "external-wof.zip",
            rom_sha256="a" * 64,
            source_guard_sha256=guard,
            dependency={"stable_retro_version": "0.9.8"},
            required_files={},
        )

    @staticmethod
    def _fixture_pass() -> dict[str, object]:
        return {
            "schema": "wof-training-farm-determinism-result-v1",
            "runId": "1" * 32,
            "status": "PASS",
            "reasonCode": "DETERMINISM_MATCH",
            "message": "fixture only",
            "proofScope": "IMPLEMENTATION_FIXTURE",
            "realWofProof": False,
            "sourceNamespace": "stable-retro-fbneo",
            "repetitionsRequired": 3,
            "repetitionsCompleted": 3,
            "horizonFrames": 8,
            "actionSequence": [],
            "actionSequenceSha256": "b" * 64,
            "runtimeIdentity": {},
            "runtimeIdentitySha256": "c" * 64,
            "startStateSha256": "d" * 64,
            "startRamSha256": "e" * 64,
            "repetitions": [],
            "firstDivergence": None,
        }

    def test_missing_prerequisite_is_exact_waiting_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            evidence = root / "evidence"
            pre = owner.Preflight(
                ok=False,
                reason="WOF_ROM_PATH is not set",
                repo_root=repo,
                evidence_root=evidence,
                rom_path=None,
                rom_sha256=None,
                source_guard_sha256=None,
                dependency={},
                required_files={},
            )
            called = False

            def runner(*args):
                nonlocal called
                called = True
                raise AssertionError("subprocess must not run")

            code, summary = owner.run_owner_flow(
                preflight_result=pre, command_runner=runner
            )
            self.assertEqual(code, 2)
            self.assertEqual(summary["state"], "WAITING_PREREQUISITE")
            self.assertIn("WOF_ROM_PATH", summary["detail"])
            self.assertFalse(called)
            evidence_dir = Path(str(summary["evidenceDirectory"]))
            self.assertTrue((evidence_dir / "summary.json").is_file())
            self.assertTrue((evidence_dir / "summary.txt").is_file())

    def test_r02_nonpass_stops_before_r04(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, guard = self._make_repo(root)
            pre = self._preflight(repo, root / "evidence", guard)
            calls: list[list[str]] = []

            def runner(cmd, cwd, env):
                calls.append(list(cmd))
                out = Path(cmd[cmd.index("--output") + 1])
                out.write_text(json.dumps({
                    "schema": "wof-training-farm-determinism-result-v1",
                    "runId": "2" * 32,
                    "status": "FAIL",
                    "reasonCode": "DETERMINISM_MISMATCH",
                    "message": "stub mismatch",
                    "proofScope": "REAL_WOF",
                    "realWofProof": False,
                    "sourceNamespace": "stable-retro-fbneo",
                    "firstDivergence": {"kind": "RAM"},
                }), encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 1, "", "")

            code, summary = owner.run_owner_flow(
                preflight_result=pre, command_runner=runner
            )
            self.assertEqual(code, 3)
            self.assertEqual(summary["state"], "BLOCKED_R0_2_REAL_DETERMINISM")
            self.assertEqual(len(calls), 1)
            self.assertIn("training.farm.determinism", calls[0])

    def test_fixture_pass_cannot_unlock_r04(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, guard = self._make_repo(root)
            pre = self._preflight(repo, root / "evidence", guard)
            calls = 0

            def runner(cmd, cwd, env):
                nonlocal calls
                calls += 1
                out = Path(cmd[cmd.index("--output") + 1])
                out.write_text(json.dumps(self._fixture_pass()), encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, "", "")

            code, summary = owner.run_owner_flow(
                preflight_result=pre, command_runner=runner
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(summary["state"], "BLOCKED_R0_2_REAL_DETERMINISM")
            self.assertEqual(calls, 1)
            self.assertIn("not a real-WOF proof", summary["detail"])

    def test_malformed_r02_pass_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, guard = self._make_repo(root)
            pre = self._preflight(repo, root / "evidence", guard)

            def runner(cmd, cwd, env):
                out = Path(cmd[cmd.index("--output") + 1])
                bad = self._fixture_pass()
                bad["proofScope"] = "REAL_WOF"
                bad["realWofProof"] = True
                del bad["runId"]
                out.write_text(json.dumps(bad), encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, "", "")

            code, summary = owner.run_owner_flow(
                preflight_result=pre, command_runner=runner
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(summary["state"], "BLOCKED_R0_2_REAL_DETERMINISM")
            self.assertIn("required fields missing", summary["detail"])

    def test_r04_partial_cannot_produce_final_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, guard = self._make_repo(root)
            pre = self._preflight(repo, root / "evidence", guard)
            calls = 0
            real_shaped_stub = self._fixture_pass()
            real_shaped_stub["proofScope"] = "REAL_WOF"
            real_shaped_stub["realWofProof"] = True

            def runner(cmd, cwd, env):
                nonlocal calls
                calls += 1
                out = Path(cmd[cmd.index("--output") + 1])
                if calls == 1:
                    out.write_text(json.dumps(real_shaped_stub), encoding="utf-8")
                else:
                    out.write_text(json.dumps({
                        "schema": "wof-training-farm-savestate-fork-result-v1",
                        "runId": "3" * 32,
                        "status": "PARTIAL",
                        "reasonCode": "EXECUTION_LIMIT_REACHED",
                        "message": "stub partial",
                        "proofScope": "REAL_WOF_FORK",
                        "realWofProof": False,
                        "sourceNamespace": "stable-retro-fbneo",
                    }), encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, "", "")

            with mock.patch.object(
                owner, "validate_r02_real_pass", return_value=real_shaped_stub
            ):
                code, summary = owner.run_owner_flow(
                    preflight_result=pre, command_runner=runner
                )
            self.assertEqual(code, 4)
            self.assertEqual(summary["state"], "BLOCKED_R0_4_REAL_FORK_SMOKE")
            self.assertEqual(calls, 2)

    def test_new_runs_never_merge_evidence_directories(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = owner._new_run_dir(root)
            second = owner._new_run_dir(root)
            self.assertNotEqual(first, second)
            self.assertTrue(first.is_dir())
            self.assertTrue(second.is_dir())

    def test_repository_internal_evidence_path_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            inside = repo / "training" / "farm" / "proof"
            self.assertTrue(owner._is_within(inside, repo))
            outside = Path(td) / "outside"
            self.assertFalse(owner._is_within(outside, repo))

    def test_human_verdicts_are_unambiguous(self) -> None:
        self.assertEqual(
            owner._human_verdict({"state": "PASS", "detail": "x"}),
            "PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE",
        )
        self.assertTrue(
            owner._human_verdict(
                {"state": "WAITING_PREREQUISITE", "detail": "missing"}
            ).startswith("WAITING_PREREQUISITE —")
        )
        self.assertTrue(
            owner._human_verdict(
                {"state": "BLOCKED_R0_4_REAL_FORK_SMOKE", "detail": "partial"}
            ).startswith("BLOCKED — R0.4 REAL FORK SMOKE —")
        )


if __name__ == "__main__":
    unittest.main()
