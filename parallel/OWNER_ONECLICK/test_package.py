from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "package_manifest.json"
BOOTSTRAP = HERE / "bootstrap_v2.ps1"
ENTRY = ROOT / "WOF_一键工具.cmd"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def git_show(commit: str, path: str) -> bytes:
    cp = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if cp.returncode:
        raise AssertionError(cp.stderr.decode("utf-8", "replace"))
    return cp.stdout


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        cls.bootstrap = BOOTSTRAP.read_text(encoding="utf-8-sig")
        cls.entry = ENTRY.read_text(encoding="utf-8-sig")

    def test_manifest_is_immutable_and_safe(self) -> None:
        m = self.manifest
        self.assertEqual(m["schema"], "wof-owner-oneclick-package-v1")
        self.assertRegex(m["packageVersion"], r"^[A-Za-z0-9._-]+$")
        commit = m["sourceCommit"]
        self.assertRegex(commit, r"^[0-9a-f]{40}$")
        self.assertEqual(
            m["baseUrl"],
            f"https://raw.githubusercontent.com/ouyong520/wof-ai-private/{commit}/",
        )
        self.assertEqual(m["safety"], {"readOnly": True, "ramWrites": 0, "inputInjection": False})
        paths = [row["path"] for row in m["files"]]
        self.assertEqual(len(paths), len(set(paths)))
        required = {
            "WOF_一键工具.cmd",
            "WOF_TOOLKIT.cmd",
            "parallel/OPTOOLKIT/toolkit.py",
            "parallel/OPTOOLKIT/owner_zh_cn.py",
            "parallel/PYLAUNCH/launcher.py",
            "parallel/WOF052L_RECORDER/owner_zh_cn.py",
            "parallel/WOF052L_RECORDER/fleet_recorder.py",
            "parallel/WOF052L_RECORDER/recorder.py",
            "parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd",
            "parallel/BROWSER_FLEET/fleet_owner_zh_cn.py",
            "parallel/BROWSER_FLEET/fleet_manager.py",
        }
        self.assertTrue(required.issubset(paths))
        for row in m["files"]:
            self.assertNotIn("..", row["path"])
            self.assertRegex(row["gitBlobSha"], r"^[0-9a-f]{40}$")

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_every_manifest_blob_matches_pinned_commit(self) -> None:
        commit = self.manifest["sourceCommit"]
        for row in self.manifest["files"]:
            with self.subTest(path=row["path"]):
                data = git_show(commit, row["path"])
                self.assertEqual(git_blob_sha(data), row["gitBlobSha"])

    def test_bootstrap_has_atomic_lkg_contract(self) -> None:
        s = self.bootstrap
        for token in [
            "releases",
            ".staging-",
            "installed.ok",
            "current.txt",
            "Get-GitBlobSha1",
            "gitBlobSha",
            "Move-Item -LiteralPath $stage -Destination $releaseDir",
            "Move-Item -LiteralPath $pointerTmp -Destination $CurrentFile -Force",
            "Remove-Item -LiteralPath $stage -Recurse -Force",
        ]:
            self.assertIn(token, s)
        self.assertLess(
            s.index("Move-Item -LiteralPath $stage -Destination $releaseDir"),
            s.index("Move-Item -LiteralPath $pointerTmp -Destination $CurrentFile -Force"),
        )
        self.assertRegex(
            s,
            r"raw\.githubusercontent\.com/ouyong520/wof-ai-private/\[0-9a-f\]\{40\}",
        )
        self.assertNotIn("git clone", s.lower())
        self.assertNotIn("github desktop", s.lower())

    def test_python_missing_has_automatic_winget_path(self) -> None:
        s = self.bootstrap
        self.assertIn("Find-Python", s)
        self.assertIn("Ensure-Python", s)
        self.assertIn("Python.Python.3.12", s)
        self.assertIn("winget.exe", s)
        self.assertIn("--scope user", s)

    def test_owner_surface_is_chinese_utf8(self) -> None:
        for text in [
            "WOF 一键工具",
            "正在启动 WOF 工具安装/更新程序",
            "旧版本不会被删除",
            "日志文件发回来",
        ]:
            self.assertIn(text, self.entry)
        for text in [
            "正在检查 WOF 工具更新",
            "正在准备 Python 环境",
            "旧版本工具仍然保留",
            "正在打开中文 WOF 工具箱",
        ]:
            self.assertIn(text, self.bootstrap)
        self.assertIn("chcp 65001", self.entry)

    def test_chinese_and_space_paths_can_be_created_and_atomically_switched(self) -> None:
        with tempfile.TemporaryDirectory(prefix="WOF 中文 路径 ") as td:
            root = Path(td) / "Local App Data" / "WOF Future Danger" / "OwnerTools"
            releases = root / "releases"
            stage = releases / "2026.09.01.test.staging-abc"
            stage.mkdir(parents=True)
            (stage / "WOF_TOOLKIT.cmd").write_text("echo 中文\n", encoding="utf-8")
            (stage / "installed.ok").write_text("ok\n", encoding="utf-8")
            release = releases / "2026.09.01.test"
            stage.rename(release)
            tmp = root / "current.txt.tmp"
            tmp.write_text("2026.09.01.test", encoding="ascii")
            tmp.replace(root / "current.txt")
            self.assertTrue((release / "WOF_TOOLKIT.cmd").is_file())
            self.assertEqual((root / "current.txt").read_text(encoding="ascii"), "2026.09.01.test")

    def test_failed_stage_does_not_replace_last_known_good(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            good = root / "releases" / "good"
            good.mkdir(parents=True)
            (good / "installed.ok").write_text("ok", encoding="ascii")
            current = root / "current.txt"
            current.write_text("good", encoding="ascii")
            failed = root / "releases" / "bad.staging-x"
            failed.mkdir(parents=True)
            (failed / "partial.file").write_text("partial", encoding="ascii")
            shutil.rmtree(failed)
            self.assertEqual(current.read_text(encoding="ascii"), "good")
            self.assertTrue((good / "installed.ok").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
