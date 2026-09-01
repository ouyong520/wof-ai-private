from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import unified_preflight as p
import unified_preflight_entrypoint as entry

COMMIT = "a" * 40


def now_iso(delta_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=delta_seconds)).isoformat()


class FixtureRepo:
    def __init__(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.base = Path(self.td.name)
        self.root = self.base / f"wof-ai-private-{COMMIT}"
        self.root.mkdir()
        self.status_out = self.base / "UNIFIED_PREFLIGHT_STATUS.json"
        self.manifest = self.base / "snapshot.json"
        self._populate()

    def cleanup(self) -> None:
        self.td.cleanup()

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _populate(self) -> None:
        for paths in p.REQUIRED_FILES.values():
            for rel in paths:
                self.write(rel, "placeholder\n")

        self.write("parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py", "# runtime\n")
        self.write("parallel/LIVE_PROOF_BUNDLE/RUN_WOF_UNIFIED_LIVE_PROOF.cmd", "@echo off\necho 统一 Windows 真人短验证\n")
        self.write("parallel/BROWSER_FLEET/fleet_owner_zh_cn.py", "print('浏览器舰队')\n")
        self.write("parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd", "@echo off\necho 一键验证\n")
        self.write("parallel/WOF052L_RECORDER/owner_zh_cn.py", "print('自动采集器')\n")

        self.write(
            "parallel/BROWSER_FLEET/fleet_discovery_v2.py",
            "Target.setAutoAttach LIGHT_RUNTIME_PROBE moduleOk readOnly ramWrites inputInjection\n",
        )
        self.write(
            "parallel/PYLAUNCH/wof_launcher/discovery_v2.py",
            "Target.setAutoAttach Page.getFrameTree parentFrameId IDENTITY_PROBE WORKER_TYPES\n"
            "def _worker_compatible(t, related=False):\n"
            "    if t.get('type') in WORKER_TYPES:\n"
            "        return True\n"
            "    return related\n",
        )
        self.write(
            "parallel/WOF052L_RECORDER/owner_v2_zh_cn.py",
            "discovery_v2_sync.install(recorder)\nhardening_v2.install(recorder, discovery_v2_sync)\n",
        )
        self.write("parallel/WOF052L_RECORDER/discovery_v2_sync.py", "Target.setAutoAttach\n")
        self.write(
            "parallel/WOF052L_RECORDER/hardening_v2.py",
            "parentFrameId CROSS_PAGE_AMBIGUITY runtime+identity are authority\n",
        )

        self.write(
            "parallel/BROWSER_FLEET/DISCOVERY_CONTRACT.md",
            '{"readOnly": true, "ramWrites": 0, "inputInjection": false, '
            '"windowWorkerReplacement": false, "workerStatusAuthority": "cheap-indicator-only", '
            '"world921031IdentityAuthoritative": false}\n',
        )
        self.write("parallel/BROWSER_FLEET/RESULT.md", "BROWSER FLEET DISCOVERY V2 READY\n")
        self.write(
            "parallel/PYLAUNCH/DISCOVERY_V2_HARDENING_RESULT.md",
            'PYLAUNCH DISCOVERY V2 HARDENING READY\n{"readOnly": true, "ramWrites": 0, '
            '"inputInjection": false, "workerReplacement": false, "urlRewrite": false}\n',
        )
        self.write(
            "parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md",
            "PASS — PYLAUNCH PARENTFRAME AUTHORITY FRESH QA\n",
        )
        self.write(
            "parallel/WOF052L_RECORDER/DISCOVERY_V2_HARDENING_RESULT.md",
            "WOF052L RECORDER DISCOVERY V2 HARDENING READY\n"
            "readOnly=true ramWrites=0 inputInjection=false no `window.Worker` replacement\n",
        )
        self.write(
            "parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md",
            "PASS — UNIFIED LIVE PROOF FRESHNESS FRESH INDEPENDENT QA\n",
        )
        self.write(
            "parallel/LIVE_PROOF_BUNDLE/FRESHNESS_FIX_STATUS.json",
            json.dumps({
                "state": "COMPLETE",
                "fixes": {
                    "readOnly": True, "ramWrites": 0, "inputInjection": False,
                    "windowWorkerReplacement": False, "longCaptureAutoStarted": False,
                },
                "validation": {"combined": {"result": "PASS"}},
            }),
        )
        self.write(
            "parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.json",
            json.dumps({"result": "PASS", "stopCondition": "PASS — UNIFIED LIVE PROOF FRESHNESS FRESH INDEPENDENT QA"}),
        )

        for spec in p.REGRESSIONS:
            self.write(str(Path(spec.cwd) / spec.entrypoint), "def test_fixture():\n    pass\n")

        self.write_manifest()

    def write_manifest(self, *, resolved: str | None = None, components: dict | None = None) -> None:
        value = {
            "schema": "wof-unified-snapshot-manifest-v1",
            "source": "github-main-pinned-codeload",
            "snapshotCommit": COMMIT,
            "resolvedAtUtc": resolved or now_iso(),
            "components": components or {
                "liveProof": COMMIT,
                "browserFleet": COMMIT,
                "pylaunch": COMMIT,
                "recorder": COMMIT,
            },
        }
        self.manifest.write_text(json.dumps(value), encoding="utf-8")


def good_runner(root: Path, spec: p.RegressionSpec) -> dict:
    return {"returncode": 0, "tests": 2, "output": "Ran 2 tests\nOK", "command": spec.entrypoint}


class UnifiedPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = FixtureRepo()
        self.addCleanup(self.fx.cleanup)

    def run_pf(self, runner=good_runner):
        return p.run_preflight(
            self.fx.root,
            snapshot_manifest=self.fx.manifest,
            status_out=self.fx.status_out,
            regression_runner=runner,
        )

    def test_all_repository_checks_pass(self):
        status = self.run_pf()
        self.assertEqual(status["result"], "PASS")
        self.assertTrue(status["gates"]["browserLaunchAllowed"])
        self.assertEqual(status["regression"]["testsObserved"], 18)
        self.assertTrue(self.fx.status_out.is_file())

    def test_component_blocked_fails_closed(self):
        self.fx.write("parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md", "BLOCKED — P1 stale identity cache\n")
        status = self.run_pf()
        self.assertEqual(status["result"], "BLOCKED")
        self.assertFalse(status["gates"]["ownerWofEntryAllowed"])
        self.assertTrue(any("stale identity" in str(x.get("detailZh")) for x in status["blockers"]))

    def test_stale_snapshot_fails_closed(self):
        self.fx.write_manifest(resolved=now_iso(-(p.SNAPSHOT_MAX_AGE_SECONDS + 30)))
        status = self.run_pf()
        self.assertEqual(status["result"], "BLOCKED")
        self.assertTrue(any(x["check"] == "snapshot-freshness" for x in status["blockers"]))

    def test_mixed_component_commits_fail_closed(self):
        components = {"liveProof": COMMIT, "browserFleet": COMMIT, "pylaunch": "b" * 40, "recorder": COMMIT}
        self.fx.write_manifest(components=components)
        status = self.run_pf()
        self.assertEqual(status["result"], "BLOCKED")
        self.assertTrue(any(x["check"] == "single-component-commit" for x in status["blockers"]))

    def test_missing_required_test_fails_closed(self):
        (self.fx.root / "parallel/PYLAUNCH/tests/test_parentframe_authority.py").unlink()
        status = self.run_pf()
        self.assertEqual(status["result"], "BLOCKED")
        self.assertTrue(any("test_parentframe_authority.py" in str(x.get("detailZh")) for x in status["blockers"]))

    def test_old_direct_gstyphoon_style_discovery_rejected(self):
        self.fx.write(
            "parallel/PYLAUNCH/wof_launcher/discovery_v2.py",
            "def choose(t):\n    return t.get('type') == 'worker' and 'gstyphoon' in t.get('url','')\n",
        )
        status = self.run_pf()
        self.assertEqual(status["result"], "BLOCKED")
        self.assertTrue(any(x["check"] == "discovery-v2-capabilities" and x["component"] == "pylaunch" for x in status["blockers"]))

    def test_english_only_owner_entry_rejected(self):
        self.fx.write("parallel/BROWSER_FLEET/fleet_owner_zh_cn.py", "print('browser fleet')\n")
        status = self.run_pf()
        self.assertEqual(status["result"], "BLOCKED")
        self.assertTrue(any(x["check"] == "simplified-chinese-entrypoints" for x in status["blockers"]))

    def test_safety_declaration_mismatch_rejected(self):
        self.fx.write(
            "parallel/BROWSER_FLEET/DISCOVERY_CONTRACT.md",
            '{"readOnly": true, "ramWrites": 1, "inputInjection": false, "windowWorkerReplacement": false}\n',
        )
        status = self.run_pf()
        self.assertEqual(status["result"], "BLOCKED")
        self.assertTrue(any(x["check"] == "safety-declarations" and x["component"] == "browserFleet" for x in status["blockers"]))

    def test_malformed_result_json_rejected(self):
        self.fx.write("parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.json", "{broken")
        status = self.run_pf()
        self.assertEqual(status["result"], "BLOCKED")
        self.assertTrue(any(x["check"] == "fresh-independent-qa-json" for x in status["blockers"]))

    def test_regression_command_failure_rejected(self):
        def bad_runner(root: Path, spec: p.RegressionSpec) -> dict:
            if spec.entrypoint.endswith("test_discovery_v2.py"):
                return {"returncode": 1, "tests": 3, "output": "FAILED", "command": spec.entrypoint}
            return good_runner(root, spec)
        status = self.run_pf(bad_runner)
        self.assertEqual(status["result"], "BLOCKED")
        self.assertTrue(any(x["check"] == "offline-regression" and "failed" in str(x["detailZh"]) for x in status["blockers"]))

    def test_pass_allows_live_stage_to_start(self):
        calls = []
        rc, status = entry.run_guarded_live(
            self.fx.root,
            snapshot_manifest=self.fx.manifest,
            status_out=self.fx.status_out,
            regression_runner=good_runner,
            live_runner=lambda: calls.append("live") or 0,
        )
        self.assertEqual(status["result"], "PASS")
        self.assertEqual(rc, 0)
        self.assertEqual(calls, ["live"])

    def test_fail_never_starts_live_stage(self):
        self.fx.write("parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md", "BLOCKED — P1 recorder authority\n")
        calls = []
        rc, status = entry.run_guarded_live(
            self.fx.root,
            snapshot_manifest=self.fx.manifest,
            status_out=self.fx.status_out,
            regression_runner=good_runner,
            live_runner=lambda: calls.append("live") or 0,
        )
        self.assertEqual(status["result"], "BLOCKED")
        self.assertEqual(rc, entry.PREFLIGHT_BLOCKED_EXIT)
        self.assertEqual(calls, [])

    def test_blocked_output_is_chinese_and_owner_not_required(self):
        self.fx.write("parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md", "BLOCKED — P1 recorder authority\n")
        status = self.run_pf()
        self.assertIn("未启动 Browser", status["ownerSummaryZh"])
        self.assertFalse(status["ownerActionRequired"])
        self.assertFalse(status["gates"]["longCaptureAutoStarted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
