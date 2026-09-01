import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("scanner", HERE.parent / "scan_project_status.py")
scanner = importlib.util.module_from_spec(SPEC)
import sys
sys.modules["scanner"] = scanner
SPEC.loader.exec_module(scanner)

class ScannerTests(unittest.TestCase):
    def test_choose_waiting_human_over_ready(self):
        text = """# Result
Verdict: REPOSITORY-SIDE READY — one bounded real Windows proof remains.
## Stop condition
Wait for bounded Windows proof.
"""
        status, conflicts = scanner.choose_status([text], True)
        self.assertEqual(status, "WAITING_HUMAN")
        self.assertEqual(conflicts, [])

    def test_conflicting_fail_and_pass_needs_review(self):
        text1 = "Verdict: PASS"
        text2 = "Verdict: FAIL"
        status, conflicts = scanner.choose_status([text1, text2], False)
        self.assertEqual(status, "NEEDS_PM_REVIEW")
        self.assertTrue(conflicts)

    def test_owner_human_action_separates_stage_dispatch(self):
        text = """## Current owner action required: YES — open fresh work stages only
Do not reopen the game or rerun the old proof now.
Fresh stage A:
- `parallel/PM/PYLAUNCH_WORKER_DISCOVERY_FIX_START_PROMPT.md`
"""
        required, reason = scanner.human_owner_action(text)
        dispatch, prompts = scanner.stage_dispatch_action(text)
        self.assertEqual(required, "NO")
        self.assertEqual(dispatch, "YES")
        self.assertIn("PYLAUNCH_WORKER_DISCOVERY_FIX_START_PROMPT.md", prompts[0])

    def test_priority_parser(self):
        text = """## P0 — Worker Fix
## P1 acceleration — Bootstrap
## 非阻塞 — Docs
"""
        parsed = scanner.parse_priorities(text)
        self.assertEqual(parsed["p0"], ["Worker Fix"])
        self.assertEqual(parsed["p1"], ["acceleration — Bootstrap"])
        self.assertEqual(parsed["non_blocking"], ["Docs"])

    def test_duplicate_worker_discovery_risk(self):
        texts = {
            "PYLAUNCH_WORKER_DISCOVERY_FIX_START_PROMPT.md": "fix gstyphoon Worker discovery",
            "WORKER_SURFACE_AUDIT_START_PROMPT.md": "audit worker surface and worker discovery",
        }
        risks = scanner.duplicate_prompt_risks(texts, set(texts))
        self.assertEqual(len(risks), 1)
        self.assertIn("worker-discovery", risks[0]["shared_topics"])

    def test_selects_most_recent_result_for_lane(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            lane = repo / "parallel" / "LANE"
            lane.mkdir(parents=True)
            old = lane / "RESULT_OLD.md"
            new = lane / "RESULT.md"
            old.write_text("Verdict: FAIL", encoding="utf-8")
            new.write_text("Verdict: PASS", encoding="utf-8")
            commits = [
                scanner.CommitInfo("newsha", "2026-09-01T00:00:00Z", "new", ["parallel/LANE/RESULT.md"]),
                scanner.CommitInfo("oldsha", "2026-08-31T00:00:00Z", "old", ["parallel/LANE/RESULT_OLD.md"]),
            ]
            selected = scanner.select_current_results([old, new], repo, commits)
            self.assertEqual(selected, [new])

    def test_build_status_and_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "parallel" / "PM").mkdir(parents=True)
            (repo / "parallel" / "LANE1").mkdir(parents=True)
            (repo / "parallel" / "PM" / "ACTIVE_PRIORITIES.md").write_text(
                "## P0 — LANE1\nFresh stage:\n`parallel/PM/LANE1_START_PROMPT.md`\n", encoding="utf-8")
            (repo / "parallel" / "PM" / "OWNER_ACTIONS.md").write_text(
                "Do not reopen the game now.\nFresh stage:\n`parallel/PM/LANE1_START_PROMPT.md`\n", encoding="utf-8")
            (repo / "parallel" / "PM" / "RELEASE_READINESS.md").write_text(
                "## Required sequence\n1. fix lane1\n2. proof\n", encoding="utf-8")
            (repo / "parallel" / "PM" / "CHINESE_UI_UX_REQUIREMENT.md").write_text(
                "简体中文", encoding="utf-8")
            (repo / "parallel" / "PM" / "LANE1_START_PROMPT.md").write_text(
                "目标：lane1", encoding="utf-8")
            (repo / "parallel" / "LANE1" / "RESULT.md").write_text(
                "Verdict: **REPOSITORY-SIDE READY — waiting real Windows proof.**\n"
                "## Stop condition\nOnly live proof remains.\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "test ready lane"], cwd=repo, check=True, capture_output=True)
            data = scanner.build_status(repo)
            lane = next(x for x in data["lanes"] if x["lane"] == "LANE1")
            self.assertEqual(lane["status"], "WAITING_HUMAN")
            self.assertEqual(data["owner_action"]["required"], "NO")
            self.assertEqual(data["owner_action"]["pm_stage_dispatch_required"], "YES")
            out = repo / "out"
            j, t = scanner.write_outputs(data, out)
            self.assertTrue(j.exists())
            self.assertTrue(t.exists())
            parsed = json.loads(j.read_text(encoding="utf-8"))
            self.assertEqual(parsed["schema"], scanner.SCHEMA)
            self.assertIn("WOF 项目状态", t.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
