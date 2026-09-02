from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from training.farm import windows_oneclick_bootstrap as b


def cp(args, rc=0, out="", err=""):
    return subprocess.CompletedProcess(args=list(args), returncode=rc, stdout=out, stderr=err)


def python_probe_output(version=(3, 14, 1), executable="C:/Python314/python.exe"):
    return json.dumps({"version": list(version), "executable": executable})


class BootstrapTests(unittest.TestCase):
    def make_repo(self, base: Path, *, req_pin: str = "0.9.8") -> Path:
        repo = base / "wof-ai-private-main"
        farm = repo / "training/farm"
        farm.mkdir(parents=True)
        (repo / "training/__init__.py").write_text("", encoding="utf-8")
        (farm / "__init__.py").write_text("", encoding="utf-8")
        (farm / "requirements-r0.1.txt").write_text(
            "# authority\nstable-retro==" + req_pin + "\n", encoding="utf-8"
        )
        (farm / "beginner_real_wof_launcher.py").write_text("# launcher\n", encoding="utf-8")
        return repo

    def test_supported_python_boundaries(self):
        self.assertTrue(b._supported((3, 10, 0)))
        self.assertTrue(b._supported((3, 14, 999)))
        self.assertFalse(b._supported((3, 9, 99)))
        self.assertFalse(b._supported((3, 15, 0)))

    def test_strict_python_version_rejects_coercion(self):
        for bad in ([3, "10", 1], [3, True, 1], [3, 10], "3.10.1", [3, 10, -1]):
            with self.subTest(bad=bad):
                with self.assertRaises(b.BootstrapError):
                    b._strict_version(bad)

    def test_discovery_prefers_supported_candidate_over_unsupported_default_python(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            local = base / "三国 10训 (local)"
            def run(command, cwd, env):
                key = tuple(command[:2])
                if key == ("py", "-3.14"):
                    return cp(command, out=python_probe_output((3, 14, 2), "C:/Python314/python.exe"))
                if command[0] == "python":
                    return cp(command, out=python_probe_output((3, 15, 0), "C:/Python315/python.exe"))
                return cp(command, rc=1, err="not found")
            selected, probes = b.discover_python(local_root=local, repo=repo, windows=True, run=run)
            self.assertIsNotNone(selected)
            self.assertEqual(selected.source, "py-3.14")
            path_python = next(p for p in probes if p.source == "PATH-python")
            self.assertFalse(path_python.accepted)
            self.assertEqual(path_python.version[:2], (3, 15))

    def test_unicode_space_parentheses_workspace_layout(self):
        with tempfile.TemporaryDirectory() as td:
            local = Path(td) / "三国 10训 (Owner)"
            layout = b.create_workspace(local)
            self.assertTrue((local / "evidence").is_dir())
            self.assertTrue((local / "ROM").is_dir())
            self.assertEqual(set(layout), set(b.WORKSPACE_DIRS))
            self.assertEqual(list((local / "ROM").iterdir()), [])

    def test_valid_venv_reuse(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            local = base / "local"
            vpy = b.venv_python_path(local, windows=True)
            vpy.parent.mkdir(parents=True)
            vpy.write_text("", encoding="utf-8")
            def run(command, cwd, env):
                return cp(command, out=python_probe_output((3, 12, 7), str(vpy)))
            report = b.inspect_venv(local_root=local, repo=repo, windows=True, run=run)
            self.assertEqual(report.state, "VALID")
            self.assertEqual(report.version, (3, 12, 7))

    def test_broken_and_stale_venv_detected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            broken = base / "broken"
            (broken / ".venv").mkdir(parents=True)
            report = b.inspect_venv(local_root=broken, repo=repo, windows=True, run=lambda *a: None)
            self.assertEqual(report.state, "BROKEN")

            stale = base / "stale"
            vpy = b.venv_python_path(stale, windows=True)
            vpy.parent.mkdir(parents=True)
            vpy.write_text("", encoding="utf-8")
            def run(command, cwd, env):
                return cp(command, out=python_probe_output((3, 15, 0), str(vpy)))
            report = b.inspect_venv(local_root=stale, repo=repo, windows=True, run=run)
            self.assertEqual(report.state, "STALE_UNSUPPORTED")

    def test_venv_creation_uses_selected_command_and_postchecks(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            local = base / "local"
            calls = []
            selected = b.PythonProbe(
                "py-3.12", ("py", "-3.12"), "C:/Python312/python.exe", (3, 12, 8), True, "supported"
            )
            def run(command, cwd, env):
                calls.append(tuple(command))
                if "-m" in command and "venv" in command:
                    vpy = b.venv_python_path(local, windows=True)
                    vpy.parent.mkdir(parents=True, exist_ok=True)
                    vpy.write_text("", encoding="utf-8")
                    return cp(command)
                return cp(command, out=python_probe_output((3, 12, 8), str(b.venv_python_path(local, windows=True))))
            report = b.create_venv(selected, local_root=local, repo=repo, windows=True, run=run)
            self.assertEqual(report.state, "VALID")
            self.assertEqual(calls[0][:4], ("py", "-3.12", "-m", "venv"))
            self.assertEqual(calls[0][-1], str(local / ".venv"))

    def test_requirement_authority_hash_and_pin(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            auth = b.requirement_authority(repo)
            raw = (repo / b.REQUIREMENTS_RELATIVE).read_bytes()
            self.assertEqual(auth.sha256, hashlib.sha256(raw).hexdigest())
            self.assertEqual(auth.requirements_pin, b.PINNED_STABLE_RETRO)
            self.assertTrue(auth.consistent)

    def test_requirement_authority_mismatch_is_fail_closed(self):
        auth = b.RequirementAuthority("requirements.txt", "0" * 64, "0.9.8", "0.9.7", False)
        with self.assertRaisesRegex(b.BootstrapError, "DEPENDENCY_AUTHORITY_MISMATCH"):
            b.sync_dependencies(
                venv_python=Path("C:/x/python.exe"),
                authority=auth,
                repo=Path("."),
                run=lambda *args: cp(args[0]),
            )

    def test_pip_sync_success_and_failure_classification(self):
        auth = b.RequirementAuthority("R:/requirements.txt", "0" * 64, "0.9.8", "0.9.8", True)
        calls = []
        def good(command, cwd, env):
            calls.append(tuple(command))
            return cp(command)
        result = b.sync_dependencies(
            venv_python=Path("C:/venv/python.exe"), authority=auth, repo=Path("R:/repo"), run=good
        )
        self.assertEqual(result["state"], "SYNCED")
        self.assertIn("--requirement", calls[0])

        def network(command, cwd, env):
            return cp(command, rc=1, err="HTTPSConnectionPool: connection timed out")
        with self.assertRaisesRegex(b.BootstrapError, "NETWORK_OR_INDEX_UNAVAILABLE"):
            b.sync_dependencies(
                venv_python=Path("C:/venv/python.exe"), authority=auth, repo=Path("R:/repo"), run=network
            )

        wheel = cp(["pip"], rc=1, err="Failed building wheel for stable-retro")
        self.assertEqual(b.classify_pip_failure(wheel)[0], "WHEEL_OR_BUILD_FAILURE")

    def test_rom_free_dependency_probe_strips_parent_rom_env(self):
        seen_env = {}
        report = {
            "stable_retro_present": True,
            "stable_retro_version": "0.9.8",
            "pinned_version_match": True,
            "fbneo_declared": True,
            "fbneo_zip_mapping": True,
            "platform_supported": True,
        }
        def run(command, cwd, env):
            seen_env.update(env or {})
            return cp(command, out=json.dumps(report))
        result = b.probe_dependencies(
            venv_python=Path("C:/venv/python.exe"),
            repo=Path("R:/repo"),
            run=run,
            base_environment={"WOF_ROM_PATH": "R:/secret/wof.zip", "KEEP": "1"},
        )
        self.assertEqual(result["stable_retro_version"], "0.9.8")
        self.assertNotIn("WOF_ROM_PATH", seen_env)
        self.assertEqual(seen_env["KEEP"], "1")
        auth = b.RequirementAuthority("x", "0"*64, "0.9.8", "0.9.8", True)
        self.assertEqual(b.dependency_readiness(result, auth), (True, "pinned Stable-Retro + FBNeo capability ready"))

    def test_fbneo_probe_failure_propagates(self):
        def run(command, cwd, env):
            return cp(command, rc=7, err="FBNeo core unavailable")
        with self.assertRaisesRegex(b.BootstrapError, "FBNEO_PROBE_EXECUTION_FAILED"):
            b.probe_dependencies(
                venv_python=Path("C:/venv/python.exe"),
                repo=Path("R:/repo"),
                run=run,
                base_environment={},
            )

    def test_exact_stable_retro_version_mismatch_rejected(self):
        auth = b.RequirementAuthority("x", "0"*64, "0.9.8", "0.9.8", True)
        report = {
            "stable_retro_present": True,
            "stable_retro_version": "0.9.7",
            "pinned_version_match": False,
            "fbneo_declared": True,
            "fbneo_zip_mapping": True,
            "platform_supported": True,
        }
        ready, detail = b.dependency_readiness(report, auth)
        self.assertFalse(ready)
        self.assertIn("wrong stable-retro version", detail)

    def test_fbneo_capability_false_is_not_ready(self):
        auth = b.RequirementAuthority("x", "0"*64, "0.9.8", "0.9.8", True)
        report = {
            "stable_retro_present": True,
            "stable_retro_version": "0.9.8",
            "pinned_version_match": True,
            "fbneo_declared": True,
            "fbneo_zip_mapping": False,
            "platform_supported": True,
        }
        ready, detail = b.dependency_readiness(report, auth)
        self.assertFalse(ready)
        self.assertIn("ZIP mapping", detail)

    def test_evidence_root_created_and_repository_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            evidence = b.ensure_evidence_root(base / "evidence outside", repo)
            self.assertTrue(evidence.is_dir())
            with self.assertRaisesRegex(b.BootstrapError, "EVIDENCE_ROOT_UNSAFE"):
                b.ensure_evidence_root(repo / "evidence", repo)

    def test_beginner_launcher_uses_dedicated_venv_python_and_evidence_path(self):
        calls = []
        base_env = {"KEEP": "1"}
        def run(command, cwd, env):
            calls.append((list(command), dict(env or {})))
            return cp(command, rc=9, out="WAITING_PREREQUISITE — mock\n")
        result = b.launch_beginner_proof(
            venv_python=Path("F:/三国/.venv/Scripts/python.exe"),
            repo=Path("F:/三国/wof-ai-private-main"),
            evidence_root=Path("F:/三国/evidence"),
            rom_argument=None,
            allow_unrecorded_rom=False,
            run=run,
            base_environment=base_env,
        )
        self.assertEqual(result.returncode, 9)
        self.assertEqual(calls[0][0][0], "F:/三国/.venv/Scripts/python.exe")
        self.assertIn(b.BEGINNER_LAUNCHER_MODULE, calls[0][0])
        self.assertIn("F:/三国/evidence", calls[0][0])
        self.assertNotIn("WOF_ROM_PATH", calls[0][1])
        self.assertEqual(base_env, {"KEEP": "1"})

    def test_diagnostics_is_rom_free_and_non_mutating(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            local = base / "local"
            def run(command, cwd, env):
                joined = " ".join(command)
                self.assertNotIn("dependency_probe", joined)
                self.assertNotIn("secret.zip", joined)
                if command[:2] == ("py", "-3.14") or list(command[:2]) == ["py", "-3.14"]:
                    return cp(command, out=python_probe_output())
                return cp(command, rc=1, err="missing")
            diag = b._diagnostic(
                repo=repo,
                local_root=local,
                evidence_root=base / "evidence",
                explicit_python=None,
                windows=True,
                run=run,
                environment={"WOF_ROM_PATH": str(base / "secret.zip")},
            )
            self.assertFalse(diag["romAccessed"])
            self.assertFalse(diag["realWofProof"])
            self.assertFalse(diag["r0_5Authorized"])
            self.assertFalse(diag["realWorkerExecutionStarted"])
            self.assertFalse((local / ".venv").exists())
            self.assertEqual(diag["dependencySyncState"], "NOT_RUN_DIAGNOSTICS")

    def test_run_bootstrap_child_failure_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            local = base / "local"
            evidence = local / "evidence"
            vpy = b.venv_python_path(local, windows=True)
            vpy.parent.mkdir(parents=True)
            vpy.write_text("", encoding="utf-8")
            good_probe = {
                "stable_retro_present": True,
                "stable_retro_version": "0.9.8",
                "pinned_version_match": True,
                "fbneo_declared": True,
                "fbneo_zip_mapping": True,
                "platform_supported": True,
            }
            def run(command, cwd, env):
                if "-m" in command and "pip" in command:
                    return cp(command)
                if "-c" in command and "dependency_probe" in command[-1]:
                    return cp(command, out=json.dumps(good_probe))
                if "-c" in command:
                    return cp(command, out=python_probe_output((3, 12, 1), str(vpy)))
                return cp(command, rc=1, err="unexpected")
            with mock.patch.object(
                b,
                "launch_beginner_proof",
                return_value=cp(["child"], rc=7, out="BLOCKED — strict child\n"),
            ):
                rc = b.run_bootstrap(
                    repo=repo,
                    local_root=local,
                    evidence_root=evidence,
                    windows=True,
                    run=run,
                    environment={},
                )
            self.assertEqual(rc, 7)

    def test_prepare_only_never_launches_proof(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = self.make_repo(base)
            local = base / "local"
            evidence = local / "evidence"
            good_probe = {
                "stable_retro_present": True,
                "stable_retro_version": "0.9.8",
                "pinned_version_match": True,
                "fbneo_declared": True,
                "fbneo_zip_mapping": True,
                "platform_supported": True,
            }
            def run(command, cwd, env):
                if "-m" in command and "venv" in command:
                    vpy = b.venv_python_path(local, windows=True)
                    vpy.parent.mkdir(parents=True, exist_ok=True)
                    vpy.write_text("", encoding="utf-8")
                    return cp(command)
                if tuple(command[:2]) == ("py", "-3.14"):
                    return cp(command, out=python_probe_output((3, 14, 0), "C:/Python314/python.exe"))
                if "-m" in command and "pip" in command:
                    return cp(command)
                if "-c" in command and "dependency_probe" in command[-1]:
                    return cp(command, out=json.dumps(good_probe))
                if "-c" in command and str(b.venv_python_path(local, windows=True)) == command[0]:
                    return cp(command, out=python_probe_output((3, 14, 0), command[0]))
                return cp(command, rc=1, err="not installed")
            with mock.patch.object(b, "launch_beginner_proof") as launch:
                rc = b.run_bootstrap(
                    repo=repo,
                    local_root=local,
                    evidence_root=evidence,
                    windows=True,
                    prepare_only=True,
                    run=run,
                    environment={},
                )
            self.assertEqual(rc, 0)
            launch.assert_not_called()
            self.assertTrue(evidence.is_dir())

    def test_no_host_input_focus_or_system_global_mutation_symbols(self):
        source = Path(b.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "SendInput(",
            "SetForegroundWindow(",
            "keybd_event(",
            "mouse_event(",
            "winreg.",
            "pyautogui.",
            "pynput.",
            "AutoHotkey",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
