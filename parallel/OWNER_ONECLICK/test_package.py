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
        cls.blobs = {row["path"]: row["gitBlobSha"] for row in cls.manifest["files"]}

    def test_manifest_is_deterministic_immutable_and_safe(self) -> None:
        m = self.manifest
        self.assertEqual(m["schema"], refresh.SCHEMA)
        self.assertEqual(m["generator"], refresh.GENERATOR)
        self.assertEqual(m["selectionPolicy"], refresh.SELECTION_POLICY)
        self.assertRegex(m["packageVersion"], r"^[A-Za-z0-9._-]+$")
        self.assertRegex(m["sourceCommit"], r"^[0-9a-f]{40}$")
        self.assertRegex(m["generatedAtUtc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(
            m["baseUrl"],
            f"https://raw.githubusercontent.com/ouyong520/wof-ai-private/{m['sourceCommit']}/",
        )
        self.assertEqual(m["safety"], {"readOnly": True, "ramWrites": 0, "inputInjection": False})
        self.assertEqual(
            m,
            refresh.generate_manifest(ROOT, m["sourceCommit"]),
            "manifest must be a byte-stable derivation of its immutable source commit",
        )

        paths = [row["path"] for row in m["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        for row in m["files"]:
            self.assertNotIn("..", row["path"])
            self.assertRegex(row["gitBlobSha"], r"^[0-9a-f]{40}$")

    def test_component_provenance_is_one_snapshot(self) -> None:
        m = self.manifest
        source = m["sourceCommit"]
        for name in ("pylaunch", "recorder", "browserFleet", "liveProof"):
            with self.subTest(component=name):
                self.assertEqual(m["components"][name]["sourceCommit"], source)

        required = {
            "parallel/PYLAUNCH/wof_launcher/browser.py",
            "parallel/PYLAUNCH/wof_launcher/cdp.py",
            "parallel/PYLAUNCH/wof_launcher/discovery_v2.py",
            "parallel/PYLAUNCH/wof_launcher/monitor.py",
            "parallel/PYLAUNCH/wof_launcher/probe.py",
            "parallel/WOF052L_RECORDER/owner_zh_cn.py",
            "parallel/WOF052L_RECORDER/recorder.py",
            "parallel/WOF052L_RECORDER/fleet_recorder.py",
            "parallel/WOF052L_RECORDER/discovery_v2_sync.py",
            "parallel/WOF052L_RECORDER/hardening_v2.py",
            "parallel/WOF052L_RECORDER/identity_probe.js",
            "parallel/BROWSER_FLEET/fleet_owner_zh_cn.py",
            "parallel/BROWSER_FLEET/fleet_manager.py",
            "parallel/BROWSER_FLEET/fleet_discovery_v2.py",
            "parallel/LIVE_PROOF_BUNDLE/RUN_WOF_UNIFIED_LIVE_PROOF.cmd",
            "parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py",
            "parallel/LIVE_PROOF_BUNDLE/unified_preflight.py",
            "parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py",
        }
        self.assertTrue(required.issubset(self.blobs), required - self.blobs.keys())

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_every_manifest_blob_matches_pinned_commit(self) -> None:
        commit = self.manifest["sourceCommit"]
        for row in self.manifest["files"]:
            with self.subTest(path=row["path"]):
                data = git_show(commit, row["path"])
                self.assertEqual(refresh.git_blob_sha(data), row["gitBlobSha"])

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_current_runtime_cannot_outgrow_or_drift_from_package(self) -> None:
        refresh.verify_worktree_payload(ROOT, self.manifest)
        commit = self.manifest["sourceCommit"]
        current = set(refresh.selected_worktree_paths(ROOT))
        packaged = {p for p in self.blobs if refresh.is_runtime_path(p)}
        self.assertEqual(current, packaged)
        for path in sorted(current):
            with self.subTest(path=path):
                data = (ROOT / path).read_bytes()
                self.assertEqual(refresh.git_blob_sha(data), self.blobs[path])
                self.assertEqual(git_show(commit, path), data)

    def test_mutated_blob_is_rejected_with_chinese_first_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="WOF 中文 stale ") as td:
            root = Path(td)
            for path in self.blobs:
                src = ROOT / path
                dst = root / path
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())

            refresh.verify_worktree_payload(root, self.manifest)
            victim = "parallel/PYLAUNCH/wof_launcher/browser.py"
            with (root / victim).open("ab") as f:
                f.write(b"\n# stale-fixture\n")

            with self.assertRaises(refresh.ManifestError) as ctx:
                refresh.verify_worktree_payload(root, self.manifest)
            msg = str(ctx.exception)
            self.assertTrue(msg.startswith("文件完整性校验失败："))
            self.assertIn(victim, msg)
            self.assertIn("expected=", msg)
            self.assertIn("actual=", msg)

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_discovery_v2_and_chinese_proof_are_really_pinned(self) -> None:
        commit = self.manifest["sourceCommit"]
        discovery = git_show(commit, "parallel/PYLAUNCH/wof_launcher/discovery_v2.py").decode("utf-8")
        monitor = git_show(commit, "parallel/PYLAUNCH/wof_launcher/monitor.py").decode("utf-8")
        proof = git_show(commit, "parallel/PYLAUNCH/wof_launcher/proof.py").decode("utf-8")
        oneclick = git_show(commit, "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd").decode("utf-8")
        self.assertIn("Target.setAutoAttach", discovery)
        self.assertIn('WORKER_TYPES = {"worker", "shared_worker", "service_worker"}', discovery)
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

    def test_bootstrap_forces_utf8_for_redirected_noninteractive_windows_output(self) -> None:
        s = self.bootstrap
        for token in [
            "[Console]::OutputEncoding = $Utf8NoBom",
            "$OutputEncoding = $Utf8NoBom",
            "$env:PYTHONUTF8 = '1'",
            "$env:PYTHONIOENCODING = 'utf-8'",
        ]:
            self.assertIn(token, s)
        self.assertIn("if ($detail -match '^文件完整性校验失败：') { Fail $detail $null 21 }", s)

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
            old = releases / "previous"
            old.mkdir(parents=True)
            (old / "installed.ok").write_text("ok", encoding="ascii")
            current = root / "current.txt"
            current.write_text("previous", encoding="ascii")

            version = self.manifest["packageVersion"]
            stage = releases / f"{version}.staging-x"
            stage.mkdir()
            (stage / "installed.ok").write_text("ok", encoding="ascii")
            new = releases / version
            stage.rename(new)
            pointer_tmp = root / "current.txt.tmp"
            pointer_tmp.write_text(version, encoding="ascii")
            pointer_tmp.replace(current)

            self.assertEqual(current.read_text(encoding="ascii"), version)
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
