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

    @classmethod
    def render(cls) -> dict:
        components = cls.manifest.get("components")
        value = components.get("renderAuthorityV3") if isinstance(components, dict) else None
        return value if isinstance(value, dict) else {}

    @classmethod
    def is_publishable_generation(cls) -> bool:
        r = cls.render()
        return bool(
            r.get("selectedNormalPath") == "production-top-overlay"
            and r.get("productionOverlayEnabled") is True
            and r.get("productionOverlaySuppressed") is False
            and isinstance(r.get("sliceARuntimeCommit"), str)
            and len(r.get("sliceARuntimeCommit")) == 40
        )

    def test_manifest_snapshot_integrity_and_release_state(self) -> None:
        m = self.manifest
        self.assertEqual(m["schema"], refresh.SCHEMA)
        self.assertRegex(m["packageVersion"], r"^[A-Za-z0-9._-]+$")
        self.assertRegex(m["sourceCommit"], r"^[0-9a-f]{40}$")
        self.assertEqual(m["baseUrl"], f"https://raw.githubusercontent.com/ouyong520/wof-ai-private/{m['sourceCommit']}/")
        safety = m.get("safety") or {}
        self.assertIs(safety.get("readOnly"), True)
        self.assertEqual(safety.get("ramWrites"), 0)
        self.assertIs(safety.get("inputInjection"), False)
        paths = [row["path"] for row in m["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        if not self.is_publishable_generation():
            with self.assertRaises(refresh.ManifestError):
                refresh.verify_publishable_manifest(m)
            self.assertIsNot(self.render().get("productionOverlayEnabled"), True)
            return
        refresh.verify_publishable_manifest(m)
        self.assertEqual(m["generator"], refresh.GENERATOR)
        self.assertEqual(m["selectionPolicy"], refresh.SELECTION_POLICY)
        self.assertEqual(
            m,
            refresh.generate_manifest(ROOT, m["sourceCommit"], self.render()["sliceARuntimeCommit"]),
        )

    def test_runtime_selection_is_one_snapshot_or_legacy_is_rejected(self) -> None:
        source = self.manifest["sourceCommit"]
        for name in ("ownerOneclick", "alpha", "pylaunch", "operatorToolkit", "projectionProof", "recorder", "browserFleet", "liveProof"):
            self.assertEqual(self.manifest["components"][name]["sourceCommit"], source, name)
        if not self.is_publishable_generation():
            with self.assertRaises(refresh.ManifestError):
                refresh.verify_publishable_manifest(self.manifest)
            return
        required = {
            "WOF_一键工具.cmd",
            "parallel/OWNER_ONECLICK/bootstrap_v2.ps1",
            "parallel/OPTOOLKIT/owner_zh_cn.py",
            "parallel/PYLAUNCH/render_authority_measurement_entry.py",
            "parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py",
            "parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py",
            "parallel/PYLAUNCH/wof_launcher/semantic_evidence_producer.py",
            "parallel/PYLAUNCH/wof_launcher/zero_click_identity_acquisition.py",
            "parallel/RENDER_AUTHORITY_V3/measurement_runner.py",
            "product/alpha/wof_alpha_hud_model.js",
            "product/alpha/wof_alpha_enemy_target_labels.js",
            "product/alpha/wof_alpha_player_head_warning.js",
            "product/alpha/wof_alpha_hud.js",
        }
        self.assertTrue(required.issubset(self.blobs), required - self.blobs.keys())
        r = self.render()
        self.assertEqual(self.manifest["components"]["pylaunch"]["revision"], "visible-production-top-overlay-slice-a-pinned")
        self.assertEqual(r["selectedNormalPath"], "production-top-overlay")
        self.assertIs(r["productionOverlayEnabled"], True)
        self.assertIs(r["productionOverlaySuppressed"], False)
        self.assertIs(r["diagnosticOnly"], False)
        self.assertIs(r["whiteAcquisitionMarkerIsProduct"], False)
        self.assertEqual(self.manifest["components"]["projectionProof"]["selected"], False)

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_every_manifest_blob_matches_pinned_commit(self) -> None:
        commit = self.manifest["sourceCommit"]
        for row in self.manifest["files"]:
            with self.subTest(path=row["path"]):
                self.assertEqual(refresh.git_blob_sha(git_show(commit, row["path"])), row["gitBlobSha"])

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_current_runtime_exactness_only_for_publishable_generation(self) -> None:
        if not self.is_publishable_generation():
            with self.assertRaises(refresh.ManifestError):
                refresh.verify_worktree_payload(ROOT, self.manifest)
            return
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

    def test_mutated_pinned_snapshot_is_rejected(self) -> None:
        commit = self.manifest["sourceCommit"]
        with tempfile.TemporaryDirectory(prefix="WOF 中文 stale ") as td:
            root = Path(td)
            for path in self.blobs:
                dst = root / path
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(git_show(commit, path))
            refresh.verify_worktree_payload(root, self.manifest)
            victim = "parallel/PYLAUNCH/wof_launcher/alpha_runtime.py"
            with (root / victim).open("ab") as f:
                f.write(b"\n# stale-fixture\n")
            with self.assertRaises(refresh.ManifestError) as ctx:
                refresh.verify_worktree_payload(root, self.manifest)
            self.assertIn("文件完整性校验失败：", str(ctx.exception))
            self.assertIn(victim, str(ctx.exception))

    def test_bootstrap_is_portable_atomic_and_rejects_non_product_manifest(self) -> None:
        s = self.bootstrap
        for token in [
            "$InstallRoot", "WOF_Portable", "releases", ".staging-", "installed.ok", "current.txt",
            "Get-GitBlobSha1", "gitBlobSha", "Test-ReleaseIntegrity", "Move-Item -LiteralPath $stage -Destination $releaseDir",
            "Move-Item -LiteralPath $pointerTmp -Destination $CurrentFile -Force", "Python.Python.3.12", "winget.exe",
            "Assert-VisibleOverlayManifest", "sliceARuntimeCommit", "production-top-overlay", "productionOverlayEnabled",
            "productionOverlaySuppressed", "diagnostic-only", "白色 acquisition marker",
        ]:
            self.assertIn(token, s)
        self.assertIn("raw\\.githubusercontent\\.com/ouyong520/wof-ai-private/[0-9a-f]{40}/", s)
        self.assertNotIn("WOF Future Danger/OwnerTools", s)
        self.assertNotIn("git clone", s.lower())

    def test_manifest_refresh_is_cache_safe_and_exact_pin_capable(self) -> None:
        s = self.bootstrap
        self.assertIn("$env:WOF_MANIFEST_URL", s)
        self.assertIn("package_manifest\\.json(?:\\?.*)?$", s)
        self.assertIn("main/parallel/OWNER_ONECLICK/package_manifest.json?cb=", s)
        self.assertIn("[Guid]::NewGuid().ToString('N')", s)
        self.assertNotIn("$ManifestUrl = 'https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/OWNER_ONECLICK/package_manifest.json'\n", s)

    def test_second_launch_is_direct_and_network_free_until_update(self) -> None:
        s = self.entry
        self.assertIn('if /I "%~1"=="--update-only" goto :bootstrap', s)
        self.assertIn('set "PORTABLE_ROOT=%LAUNCH_DIR%\\WOF_Portable"', s)
        direct_label = s.index("\n:direct\n")
        bootstrap_label = s.index("\n:bootstrap\n")
        self.assertLess(direct_label, bootstrap_label)
        direct = s[direct_label:bootstrap_label]
        self.assertNotIn("Invoke-WebRequest", direct)
        self.assertNotIn("pip install", direct)
        self.assertNotIn("raw.githubusercontent.com", direct)
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
            root = Path(td) / "Launcher Folder" / "WOF_Portable"
            releases = root / "releases"
            stage = releases / "field.staging-abc"
            stage.mkdir(parents=True)
            (stage / "installed.ok").write_text("ok", encoding="utf-8")
            release = releases / "field"
            stage.rename(release)
            tmp = root / "current.txt.tmp"
            tmp.write_text("field", encoding="ascii")
            tmp.replace(root / "current.txt")
            self.assertTrue((release / "installed.ok").is_file())
            self.assertEqual((root / "current.txt").read_text(encoding="ascii"), "field")

    def test_last_known_good_survives_failed_stage(self) -> None:
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
