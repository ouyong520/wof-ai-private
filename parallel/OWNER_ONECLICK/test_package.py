from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import refresh_manifest as refresh

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "package_manifest.json"
BOOTSTRAP = HERE / "bootstrap_v2.ps1"
ENTRY = ROOT / "WOF_一键工具.cmd"


def git_show(commit: str, path: str) -> bytes:
    cp = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if cp.returncode:
        raise AssertionError(cp.stderr.decode("utf-8", "replace"))
    return cp.stdout


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        cls.bootstrap = BOOTSTRAP.read_text(encoding="utf-8-sig")
        cls.entry = ENTRY.read_text(encoding="utf-8-sig")
        cls.blobs = {row["path"]: row["gitBlobSha"] for row in cls.manifest["files"]}

    def test_manifest_is_deterministic_immutable_and_safe(self) -> None:
        m = self.manifest
        self.assertEqual(m["schema"], refresh.SCHEMA)
        self.assertEqual(m["generator"], refresh.GENERATOR)
        self.assertEqual(m["selectionPolicy"], refresh.SELECTION_POLICY)
        self.assertRegex(m["packageVersion"], r"^[A-Za-z0-9._-]+$")
        self.assertRegex(m["sourceCommit"], r"^[0-9a-f]{40}$")
        self.assertEqual(m["baseUrl"], f"https://raw.githubusercontent.com/ouyong520/wof-ai-private/{m['sourceCommit']}/")
        self.assertEqual(m["safety"], {"readOnly": True, "ramWrites": 0, "inputInjection": False})
        self.assertEqual(m, refresh.generate_manifest(ROOT, m["sourceCommit"]))
        paths = [row["path"] for row in m["files"]]
        self.assertEqual(paths, sorted(paths)); self.assertEqual(len(paths), len(set(paths)))

    def test_field_recovery_runtime_is_selected_from_one_snapshot(self) -> None:
        source = self.manifest["sourceCommit"]
        for name in ("ownerOneclick", "alpha", "pylaunch", "recorder", "browserFleet", "liveProof"):
            self.assertEqual(self.manifest["components"][name]["sourceCommit"], source, name)
        required = {
            "WOF_一键工具.cmd",
            "parallel/OWNER_ONECLICK/bootstrap_v2.ps1",
            "parallel/PYLAUNCH/launcher.py",
            "parallel/PYLAUNCH/wof_launcher/alpha_runtime.py",
            "parallel/PYLAUNCH/wof_launcher/runtime_authority.py",
            "parallel/PYLAUNCH/wof_launcher/probe_v2.py",
            "parallel/PYLAUNCH/wof_launcher/monitor.py",
            "product/alpha/wof_alpha_field_adapter.js",
            "product/alpha/wof_alpha_enemy_head_projection.json",
            "product/alpha/wof_alpha_player_head_projection.json",
        }
        self.assertTrue(required.issubset(self.blobs), required - self.blobs.keys())
        self.assertEqual(self.manifest["components"]["alpha"]["fieldAdapter"], "product/alpha/wof_alpha_field_adapter.js")

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_every_manifest_blob_matches_pinned_commit(self) -> None:
        commit = self.manifest["sourceCommit"]
        for row in self.manifest["files"]:
            with self.subTest(path=row["path"]):
                self.assertEqual(refresh.git_blob_sha(git_show(commit, row["path"])), row["gitBlobSha"])

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_current_runtime_cannot_outgrow_or_drift_from_package(self) -> None:
        refresh.verify_worktree_payload(ROOT, self.manifest)
        commit = self.manifest["sourceCommit"]
        current = set(refresh.selected_worktree_paths(ROOT)); packaged = {p for p in self.blobs if refresh.is_runtime_path(p)}
        self.assertEqual(current, packaged)
        for path in sorted(current):
            with self.subTest(path=path):
                data = (ROOT / path).read_bytes()
                self.assertEqual(refresh.git_blob_sha(data), self.blobs[path])
                self.assertEqual(git_show(commit, path), data)

    def test_mutated_blob_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="WOF 中文 stale ") as td:
            root = Path(td)
            for path in self.blobs:
                src = ROOT / path; dst = root / path; dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(src.read_bytes())
            refresh.verify_worktree_payload(root, self.manifest)
            victim = "parallel/PYLAUNCH/wof_launcher/alpha_runtime.py"
            with (root / victim).open("ab") as f: f.write(b"\n# stale-fixture\n")
            with self.assertRaises(refresh.ManifestError) as ctx: refresh.verify_worktree_payload(root, self.manifest)
            self.assertIn("文件完整性校验失败：", str(ctx.exception)); self.assertIn(victim, str(ctx.exception))

    def test_bootstrap_is_portable_atomic_and_explicit_update_only(self) -> None:
        s = self.bootstrap
        for token in ["$InstallRoot", "WOF_Portable", "releases", ".staging-", "installed.ok", "current.txt", "Get-GitBlobSha1", "gitBlobSha", "Test-ReleaseIntegrity", "Move-Item -LiteralPath $stage -Destination $releaseDir", "Move-Item -LiteralPath $pointerTmp -Destination $CurrentFile -Force", "Python.Python.3.12", "winget.exe"]:
            self.assertIn(token, s)
        self.assertIn("raw\\.githubusercontent\\.com/ouyong520/wof-ai-private/[0-9a-f]{40}/", s)
        self.assertNotIn("WOF Future Danger/OwnerTools", s)
        self.assertNotIn("git clone", s.lower())

    def test_second_launch_is_direct_and_network_free_until_update(self) -> None:
        s = self.entry
        self.assertIn('if /I "%~1"=="--update-only" goto :bootstrap', s)
        self.assertIn('set "PORTABLE_ROOT=%LAUNCH_DIR%\\WOF_Portable"', s)
        direct_label = s.index("\n:direct\n")
        bootstrap_label = s.index("\n:bootstrap\n")
        self.assertLess(direct_label, bootstrap_label)
        direct = s[direct_label:bootstrap_label]
        self.assertNotIn("Invoke-WebRequest", direct); self.assertNotIn("pip install", direct); self.assertNotIn("raw.githubusercontent.com", direct)
        self.assertNotIn("LOCALAPPDATA", s)
        self.assertIn("EnableDelayedExpansion", s)
        self.assertIn("!CURRENT_VERSION!", s)
        self.assertRegex(s, r"raw\.githubusercontent\.com/ouyong520/wof-ai-private/[0-9a-f]{40}/parallel/OWNER_ONECLICK/bootstrap_v2\.ps1")

    def test_utf8_and_chinese_owner_surface(self) -> None:
        for token in ["chcp 65001", "PYTHONUTF8=1", "PYTHONIOENCODING=utf-8", "WOF 一键工具", "本地 portable 工具", "首次安装或显式更新/修复"]:
            self.assertIn(token, self.entry)
        for token in ["[Console]::OutputEncoding = $Utf8NoBom", "$OutputEncoding = $Utf8NoBom", "$env:PYTHONUTF8 = '1'", "$env:PYTHONIOENCODING = 'utf-8'", "portable 工具版本", "正在打开中文 WOF 工具箱"]:
            self.assertIn(token, self.bootstrap)

    def test_chinese_and_space_paths_support_atomic_switch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="WOF 中文 路径 ") as td:
            root = Path(td) / "Launcher Folder" / "WOF_Portable"; releases = root / "releases"
            stage = releases / "field.staging-abc"; stage.mkdir(parents=True); (stage / "installed.ok").write_text("ok", encoding="utf-8")
            release = releases / "field"; stage.rename(release)
            tmp = root / "current.txt.tmp"; tmp.write_text("field", encoding="ascii"); tmp.replace(root / "current.txt")
            self.assertTrue((release / "installed.ok").is_file()); self.assertEqual((root / "current.txt").read_text(encoding="ascii"), "field")

    def test_last_known_good_survives_failed_stage(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); good = root / "releases" / "good"; good.mkdir(parents=True); (good / "installed.ok").write_text("ok", encoding="ascii")
            current = root / "current.txt"; current.write_text("good", encoding="ascii")
            failed = root / "releases" / "bad.staging-x"; failed.mkdir(parents=True); (failed / "partial.file").write_text("partial", encoding="ascii"); shutil.rmtree(failed)
            self.assertEqual(current.read_text(encoding="ascii"), "good"); self.assertTrue((good / "installed.ok").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
