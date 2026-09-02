from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from training.farm import beginner_real_wof_launcher as beginner


class BeginnerRealWofLauncherTests(unittest.TestCase):
    @staticmethod
    def _write_reference(repo: Path, rom: Path, *, sha256: str | None = None, size: int | None = None) -> None:
        farm = repo / "training" / "farm"
        farm.mkdir(parents=True, exist_ok=True)
        digest = sha256 or hashlib.sha256(rom.read_bytes()).hexdigest()
        length = rom.stat().st_size if size is None else size
        (farm / "OWNER_LOCAL_ROM_REFERENCE.md").write_text(
            "# Training Farm Owner Local ROM Reference\n\n"
            "- uploaded/local filename observed by PM: `wof(2).zip`\n"
            f"- size: `{length}` bytes\n"
            f"- SHA-256: `{digest}`\n",
            encoding="utf-8",
        )

    @staticmethod
    def _ready_dependency(_path: Path) -> dict[str, object]:
        return {
            "platform_supported": True,
            "stable_retro_present": True,
            "stable_retro_version": "0.9.8",
            "fbneo_declared": True,
            "fbneo_zip_mapping": True,
            "runtime_ready": True,
            "detail": "READY",
        }

    def test_reference_parser_reads_filename_size_and_sha(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            rom = root / "wof(2).zip"
            rom.write_bytes(b"owner-rom-metadata-test")
            self._write_reference(repo, rom)
            ref = beginner.load_owner_rom_reference(repo)
            self.assertIsNotNone(ref)
            assert ref is not None
            self.assertEqual(ref.display_filename, "wof(2).zip")
            self.assertEqual(ref.size_bytes, rom.stat().st_size)
            self.assertEqual(ref.sha256, hashlib.sha256(rom.read_bytes()).hexdigest())

    def test_spaces_chinese_and_parentheses_path_matches_without_copy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            (repo / "training" / "farm").mkdir(parents=True)
            rom_dir = root / "本地 ROM 空格目录"
            rom_dir.mkdir()
            rom = rom_dir / "wof(2).zip"
            rom.write_bytes(b"external-only-rom-test-bytes")
            ref = beginner.RomReference(
                display_filename=rom.name,
                size_bytes=rom.stat().st_size,
                sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
            )
            selection = beginner.validate_selected_rom(
                rom,
                repo_root=repo,
                reference=ref,
                source="test",
                allow_unrecorded_rom=False,
            )
            self.assertTrue(selection.reference_matched)
            self.assertEqual(selection.path, rom.resolve())
            self.assertEqual(list(repo.rglob("*.zip")), [])

    def test_wrong_recorded_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            rom = root / "wof.zip"
            rom.write_bytes(b"wrong-rom")
            ref = beginner.RomReference(rom.name, rom.stat().st_size, "0" * 64)
            with self.assertRaisesRegex(beginner.BeginnerLauncherError, "Owner ROM 记录不一致"):
                beginner.validate_selected_rom(
                    rom,
                    repo_root=repo,
                    reference=ref,
                    source="test",
                    allow_unrecorded_rom=False,
                )

    def test_expert_override_is_explicit_and_does_not_claim_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            rom = root / "different.zip"
            rom.write_bytes(b"different-legal-local-rom")
            ref = beginner.RomReference("wof(2).zip", 1, "0" * 64)
            selection = beginner.validate_selected_rom(
                rom,
                repo_root=repo,
                reference=ref,
                source="CLI",
                allow_unrecorded_rom=True,
            )
            self.assertFalse(selection.reference_matched)
            self.assertTrue(selection.expert_override)

    def test_repository_local_rom_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            rom = repo / "training" / "farm" / "roms" / "wof.zip"
            rom.parent.mkdir(parents=True)
            rom.write_bytes(b"must-not-live-in-repo")
            with self.assertRaisesRegex(beginner.BeginnerLauncherError, "仓库目录之外"):
                beginner.validate_selected_rom(
                    rom,
                    repo_root=repo,
                    reference=None,
                    source="test",
                    allow_unrecorded_rom=True,
                )

    def test_picker_cancel_is_clean_waiting_without_subprocess(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            called = False

            def child(*_args):
                nonlocal called
                called = True
                raise AssertionError("strict runner must not launch after picker cancel")

            outcome = beginner.run_beginner_flow(
                chooser=lambda: None,
                process_runner=child,
                repo_root=repo,
                environment={},
            )
            self.assertEqual(outcome.exit_code, 2)
            self.assertTrue(outcome.verdict.startswith("WAITING_PREREQUISITE —"))
            self.assertIn("未选择 WOF ZIP", outcome.verdict)
            self.assertFalse(called)

    def test_existing_wof_rom_path_bypasses_picker_and_reaches_child_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            rom_dir = root / "中文 路径"
            rom_dir.mkdir()
            rom = rom_dir / "wof(2).zip"
            rom.write_bytes(b"existing-env-rom")
            self._write_reference(repo, rom)
            captured: dict[str, object] = {}
            picker_called = False
            evidence = root / "proof evidence" / "run"

            def chooser() -> Path | None:
                nonlocal picker_called
                picker_called = True
                return None

            def child(cmd, cwd, env):
                captured["cmd"] = list(cmd)
                captured["cwd"] = cwd
                captured["rom"] = env.get("WOF_ROM_PATH")
                evidence.mkdir(parents=True)
                (evidence / "summary.json").write_text(
                    json.dumps({"state": "WAITING_PREREQUISITE", "detail": "stub dependency after handoff"}),
                    encoding="utf-8",
                )
                (evidence / "summary.txt").write_text("stub\n", encoding="utf-8")
                return subprocess.CompletedProcess(
                    cmd,
                    2,
                    f"WAITING_PREREQUISITE — stub dependency after handoff\nEvidence: {evidence}\n",
                    "",
                )

            original_env = {"WOF_ROM_PATH": str(rom.resolve()), "KEEP": "unchanged"}
            outcome = beginner.run_beginner_flow(
                chooser=chooser,
                process_runner=child,
                dependency_checker=self._ready_dependency,
                repo_root=repo,
                environment=original_env,
            )
            self.assertFalse(picker_called)
            self.assertEqual(captured["rom"], str(rom.resolve()))
            self.assertEqual(original_env["WOF_ROM_PATH"], str(rom.resolve()))
            self.assertEqual(captured["cmd"][:3], [beginner.sys.executable, "-m", beginner.STRICT_RUNNER_MODULE])
            self.assertTrue(outcome.verdict.startswith("WAITING_PREREQUISITE —"))
            self.assertEqual(outcome.files["summary.txt"], evidence / "summary.txt")

    def test_selected_path_is_session_local_child_environment_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            rom = root / "a b" / "wof(2).zip"
            rom.parent.mkdir()
            rom.write_bytes(b"session-local")
            ref = beginner.RomReference(
                rom.name,
                rom.stat().st_size,
                hashlib.sha256(rom.read_bytes()).hexdigest(),
            )
            selection = beginner.validate_selected_rom(
                rom,
                repo_root=repo,
                reference=ref,
                source="picker",
                allow_unrecorded_rom=False,
            )
            base = {"KEEP": "yes"}
            captured: dict[str, str] = {}

            def child(cmd, cwd, env):
                captured.update(env)
                return subprocess.CompletedProcess(cmd, 2, "WAITING_PREREQUISITE — stub\n", "")

            beginner.launch_strict_owner_runner(
                selection,
                repo_root=repo,
                evidence_root=None,
                process_runner=child,
                base_environment=base,
            )
            self.assertNotIn("WOF_ROM_PATH", base)
            self.assertEqual(captured["WOF_ROM_PATH"], str(rom.resolve()))
            self.assertEqual(captured["KEEP"], "yes")

    def test_dependency_messages_are_beginner_readable(self) -> None:
        missing = self._ready_dependency(Path("x"))
        missing["stable_retro_present"] = False
        missing["runtime_ready"] = False
        self.assertIn("stable-retro==0.9.8", beginner.dependency_wait_reason(missing) or "")
        wrong = self._ready_dependency(Path("x"))
        wrong["stable_retro_version"] = "0.9.7"
        wrong["runtime_ready"] = False
        self.assertIn("严格要求 0.9.8", beginner.dependency_wait_reason(wrong) or "")
        fbneo = self._ready_dependency(Path("x"))
        fbneo["fbneo_declared"] = False
        fbneo["runtime_ready"] = False
        self.assertIn("FBNeo capability probe 未通过", beginner.dependency_wait_reason(fbneo) or "")

    def test_pass_waiting_and_blocked_verdicts_remain_unambiguous(self) -> None:
        self.assertEqual(
            beginner._summary_verdict({"state": "PASS", "detail": "ignored"}),
            "PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE",
        )
        self.assertTrue(
            beginner._summary_verdict({"state": "WAITING_PREREQUISITE", "detail": "missing"}).startswith(
                "WAITING_PREREQUISITE —"
            )
        )
        self.assertTrue(
            beginner._summary_verdict({"state": "BLOCKED_R0_2_REAL_DETERMINISM", "detail": "x"}).startswith(
                "BLOCKED — R0.2 REAL DETERMINISM —"
            )
        )
        self.assertTrue(
            beginner._summary_verdict({"state": "BLOCKED_R0_4_REAL_FORK_SMOKE", "detail": "x"}).startswith(
                "BLOCKED — R0.4 REAL FORK SMOKE —"
            )
        )

    def test_missing_reference_fails_closed_without_expert_override(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            rom = root / "wof.zip"
            rom.write_bytes(b"local")
            with self.assertRaisesRegex(beginner.BeginnerLauncherError, "不会绕过身份核对"):
                beginner.validate_selected_rom(
                    rom,
                    repo_root=repo,
                    reference=None,
                    source="picker",
                    allow_unrecorded_rom=False,
                )


if __name__ == "__main__":
    unittest.main()
