from __future__ import annotations

import hashlib
import json
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

EXPECTED_PACKAGE_VERSION = "2026.09.01.5"
EXPECTED_PYLAUNCH_SOURCE = "7b10867f14f59ca9ab95c0fa6d30530008409371"
EXPECTED_WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
EXPECTED_PYLAUNCH_BLOBS = {
    "parallel/PYLAUNCH/RUN_WINDOWS_PROOF.cmd": "a6c52c436d1d7f1fa1cffcd8c24849ec14dd806d",
    "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd": "f840103ea5a0a827c69d20f27c11f4bb4cef3490",
    "parallel/PYLAUNCH/launcher.py": "f19489896591a1ee5db416ca86c88ff9161b3237",
    "parallel/PYLAUNCH/wof_launcher/cdp.py": "06480f3aa7ab9261d7f91ab09074e96b4a6befc9",
    "parallel/PYLAUNCH/wof_launcher/discovery_v2.py": "cee0bdef0fe461ab0cb003e6ae198db8c19a5ec2",
    "parallel/PYLAUNCH/wof_launcher/monitor.py": "5ee0ce9a84988d7841799d907ebdfe2a3e68ea56",
    "parallel/PYLAUNCH/wof_launcher/proof.py": "7cddae420b08bba627b05f2164083289569e5f5a",
    "parallel/PYLAUNCH/wof_launcher/state.py": "7f00e9a2e948f86c30a99cab04809d726b60c95d",
    "parallel/PYLAUNCH/wof_launcher/tray.py": "c3529a60da46fc7507e6899991fa9e4f8bd816e7",
}


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


def current_pylaunch_payload_paths() -> list[str]:
    base = ROOT / "parallel" / "PYLAUNCH"
    files = [
        base / "RUN_WINDOWS_PROOF.cmd",
        base / "RUN_WOF_LAUNCHER.bat",
        base / "WOF_ONECLICK_PROOF_CN.cmd",
        base / "launcher.py",
        base / "requirements.txt",
    ]
    files.extend(sorted((base / "wof_launcher").glob("*.py")))
    return [p.relative_to(ROOT).as_posix() for p in files]


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        cls.bootstrap = BOOTSTRAP.read_text(encoding="utf-8-sig")
        cls.entry = ENTRY.read_text(encoding="utf-8-sig")
        cls.blobs = {row["path"]: row["gitBlobSha"] for row in cls.manifest["files"]}

    def test_manifest_is_immutable_and_safe(self) -> None:
        m = self.manifest
        self.assertEqual(m["schema"], "wof-owner-oneclick-package-v1")
        self.assertEqual(m["packageVersion"], EXPECTED_PACKAGE_VERSION)
        self.assertRegex(m["packageVersion"], r"^[A-Za-z0-9._-]+$")
        commit = m["sourceCommit"]
        self.assertEqual(commit, EXPECTED_PYLAUNCH_SOURCE)
        self.assertRegex(commit, r"^[0-9a-f]{40}$")
        self.assertEqual(m["baseUrl"], f"https://raw.githubusercontent.com/ouyong520/wof-ai-private/{commit}/")
        self.assertEqual(m["safety"], {"readOnly": True, "ramWrites": 0, "inputInjection": False})
        paths = [row["path"] for row in m["files"]]
        self.assertEqual(len(paths), len(set(paths)))
        required = {
            "WOF_一键工具.cmd",
            "WOF_TOOLKIT.cmd",
            "parallel/OPTOOLKIT/toolkit.py",
            "parallel/OPTOOLKIT/owner_zh_cn.py",
            "parallel/PYLAUNCH/RUN_WINDOWS_PROOF.cmd",
            "parallel/PYLAUNCH/RUN_WOF_LAUNCHER.bat",
            "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd",
            "parallel/PYLAUNCH/launcher.py",
            "parallel/PYLAUNCH/wof_launcher/discovery_v2.py",
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

    def test_pylaunch_component_metadata_is_exact(self) -> None:
        c = self.manifest["components"]["pylaunch"]
        self.assertEqual(c["revision"], "worker-discovery-v2")
        self.assertEqual(c["sourceCommit"], EXPECTED_PYLAUNCH_SOURCE)
        self.assertEqual(c["windowsProofEntry"], "parallel/PYLAUNCH/RUN_WINDOWS_PROOF.cmd")
        self.assertEqual(c["directProofEntry"], "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd")
        self.assertEqual(c["world921031Sha256"], EXPECTED_WORLD_SHA256)
        for path, sha in EXPECTED_PYLAUNCH_BLOBS.items():
            self.assertEqual(self.blobs.get(path), sha)

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_every_manifest_blob_matches_pinned_commit(self) -> None:
        commit = self.manifest["sourceCommit"]
        for row in self.manifest["files"]:
            with self.subTest(path=row["path"]):
                data = git_show(commit, row["path"])
                self.assertEqual(git_blob_sha(data), row["gitBlobSha"])

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_current_pylaunch_runtime_cannot_outgrow_package(self) -> None:
        commit = self.manifest["sourceCommit"]
        for path in current_pylaunch_payload_paths():
            with self.subTest(path=path):
                self.assertIn(path, self.blobs, f"PYLAUNCH runtime file missing from package manifest: {path}")
                current = (ROOT / path).read_bytes()
                self.assertEqual(git_blob_sha(current), self.blobs[path], f"manifest is stale for current PYLAUNCH file: {path}")
                self.assertEqual(git_show(commit, path), current, f"current PYLAUNCH file is newer than pinned immutable package: {path}")

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_discovery_v2_and_chinese_proof_are_really_pinned(self) -> None:
        commit = self.manifest["sourceCommit"]
        discovery = git_show(commit, "parallel/PYLAUNCH/wof_launcher/discovery_v2.py").decode("utf-8")
        monitor = git_show(commit, "parallel/PYLAUNCH/wof_launcher/monitor.py").decode("utf-8")
        proof = git_show(commit, "parallel/PYLAUNCH/wof_launcher/proof.py").decode("utf-8")
        oneclick = git_show(commit, "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd").decode("utf-8")
        self.assertIn("Target.setAutoAttach", discovery)
        self.assertIn('WORKER_TYPES = {"worker", "shared_worker", "service_worker"}', discovery)
        self.assertIn('path="page-autoattach"', discovery)
        self.assertIn("from .discovery_v2 import discover", monitor)
        self.assertIn('"ownerSummaryZh"', proof)
        self.assertIn('"checksZh"', proof)
        self.assertIn("WOF Launcher 一键下载与真人验证", oneclick)
        self.assertIn("不需要 DevTools", oneclick)

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
        self.assertIn("raw\\.githubusercontent\\.com/ouyong520/wof-ai-private/[0-9a-f]{40}/", s)
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
        for text in ["WOF 一键工具", "正在启动 WOF 工具安装/更新程序", "旧版本不会被删除", "日志文件发回来"]:
            self.assertIn(text, self.entry)
        for text in ["正在检查 WOF 工具更新", "正在准备 Python 环境", "旧版本工具仍然保留", "正在打开中文 WOF 工具箱"]:
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

    def test_update_from_previous_package_keeps_last_known_good(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            releases = root / "releases"
            old = releases / "2026.09.01.4"
            old.mkdir(parents=True)
            (old / "installed.ok").write_text("ok", encoding="ascii")
            current = root / "current.txt"
            current.write_text("2026.09.01.4", encoding="ascii")

            stage = releases / "2026.09.01.5.staging-x"
            stage.mkdir()
            (stage / "installed.ok").write_text("ok", encoding="ascii")
            new = releases / "2026.09.01.5"
            stage.rename(new)
            pointer_tmp = root / "current.txt.tmp"
            pointer_tmp.write_text("2026.09.01.5", encoding="ascii")
            pointer_tmp.replace(current)

            self.assertEqual(current.read_text(encoding="ascii"), "2026.09.01.5")
            self.assertTrue((old / "installed.ok").is_file())
            self.assertTrue((new / "installed.ok").is_file())

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
