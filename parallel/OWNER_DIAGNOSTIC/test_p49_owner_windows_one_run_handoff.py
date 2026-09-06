from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p49", HERE / "p49_owner_windows_one_run_handoff.py")
p49 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(p49)


class DummyConn:
    def close(self):
        pass


class P49Tests(unittest.TestCase):
    def test_exact_bundle_byte_binding_and_permit_identity(self):
        permit = json.loads((HERE / "P49_OWNER_WINDOWS_ONE_RUN_PERMIT.json").read_text(encoding="utf-8"))
        self.assertEqual(p49.permit_id(permit), permit["permitIdentity"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in permit["identityBinding"]["bundleFileSha256"]:
                src = HERE / Path(rel).name
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
            p49.verify_bundle(root, permit)

    def test_p48_budget_consumed_blocks(self):
        good = {"runStarted": False, "runBudgetConsumed": False, "remainingRunBudget": 1, "retryAttempted": False}
        bad = dict(good, runBudgetConsumed=True, remainingRunBudget=0)
        with self.assertRaisesRegex(p49.HandoffBlocked, "BUDGET_CONSUMED"):
            p49.budget(bad, good, good)

    def test_p48_run_started_blocks(self):
        good = {"runStarted": False, "runBudgetConsumed": False, "remainingRunBudget": 1, "retryAttempted": False}
        bad = dict(good, runStarted=True)
        with self.assertRaisesRegex(p49.HandoffBlocked, "RUN_STARTED"):
            p49.budget(bad, good, good)

    def test_missing_or_stale_p47_p48_p43_p45_p46_authority_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for label in ("P47", "P48", "P43", "P45", "P46"):
                rel = f"{label}.authority"
                with self.assertRaisesRegex(p49.HandoffBlocked, "AUTHORITY_FILE_MISSING"):
                    p49.pin(root, rel, "0" * 40)
                f = root / rel
                f.write_text(label, encoding="utf-8")
                with self.assertRaisesRegex(p49.HandoffBlocked, "AUTHORITY_FILE_STALE"):
                    p49.pin(root, rel, "0" * 40)
                f.unlink()

    def test_source_head_mismatch_and_dirty_block(self):
        def mismatch(_repo, op):
            return (0, "0" * 40) if op == "head" else (0, "")
        with self.assertRaisesRegex(p49.HandoffBlocked, "SOURCE_HEAD_MISMATCH"):
            p49.source_ok(Path("."), call=mismatch)

        def dirty(_repo, op):
            return (0, p49.SRC) if op == "head" else (0, " M changed.py")
        with self.assertRaisesRegex(p49.HandoffBlocked, "SOURCE_CHECKOUT_DIRTY"):
            p49.source_ok(Path("."), call=dirty)

    def test_missing_managed_interpreter_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(p49.HandoffBlocked, "MANAGED_INTERPRETER_MISSING"):
                p49.managed(env={"LOCALAPPDATA": td}, match=False)

    def test_missing_or_unreachable_debugger_blocks(self):
        with self.assertRaisesRegex(p49.HandoffBlocked, "MISSING_EXPLICIT_INPUT"):
            p49.debugger("")
        def fail(_addr, _timeout):
            raise OSError("no listener")
        with self.assertRaisesRegex(p49.HandoffBlocked, "BROWSER_WEBSOCKET_UNREACHABLE"):
            p49.debugger("ws://127.0.0.1:9222/devtools/browser/x", connect=fail)

    def test_atomic_start_is_one_way(self):
        with tempfile.TemporaryDirectory() as td:
            marker = Path(td) / "RUN_STARTED.json"
            record = {"runStarted": True}
            p49.mark(marker, record)
            with self.assertRaisesRegex(p49.HandoffBlocked, "PERMIT_ALREADY_CONSUMED"):
                p49.mark(marker, record)

    def test_preflight_failure_before_started_consumes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            marker = Path(td) / "RUN_STARTED.json"
            def blocked(*args, **kwargs):
                raise p49.HandoffBlocked("fixture")
            with self.assertRaises(p49.HandoffBlocked):
                p49.run_once(Path(td), Path(td), "ws://x:1/z", Path(td) / "out", {}, pre=blocked, env={"LOCALAPPDATA": td})
            self.assertFalse(marker.exists())

    def test_simulated_failure_invoked_once_no_retry_and_budget_consumed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            meta = root / "meta"; src = root / "src"; out = root / "out"
            meta.mkdir(); src.mkdir(); out.mkdir()
            cmd = meta / p49.P43
            cmd.parent.mkdir(parents=True)
            cmd.write_text("@echo off\n", encoding="utf-8")
            permit = {"identityBinding": {"x": 1}}
            permit_id = "a" * 64
            marker = root / "state" / "RUN_STARTED.json"
            def fake_preflight(*args, **kwargs):
                return permit_id, marker
            calls = []
            class C: returncode = 9
            def fake_invoker(*args, **kwargs):
                calls.append(args)
                return C()
            rc = p49.run_once(meta, src, "ws://127.0.0.1:9222/x", out, permit, pre=fake_preflight, invoke=fake_invoker, env={"LOCALAPPDATA": str(root)})
            self.assertEqual(rc, 9)
            self.assertEqual(len(calls), 1)
            self.assertTrue(marker.exists())
            imported = json.loads((out / p49.IMPORT).read_text(encoding="utf-8"))
            self.assertTrue(imported["runBudgetConsumed"])
            self.assertEqual(imported["remainingRunBudget"], 0)
            self.assertFalse(imported["automaticRetry"])

    def test_happy_path_fixture_permit_without_real_wof(self):
        permit = json.loads((HERE / "P49_OWNER_WINDOWS_ONE_RUN_PERMIT.json").read_text(encoding="utf-8"))
        self.assertEqual(permit["identityBinding"]["remainingRunBudget"], 1)
        self.assertFalse(permit["identityBinding"]["p48RunStarted"])
        self.assertFalse(permit["identityBinding"]["p48RunBudgetConsumed"])
        self.assertFalse(permit["automaticRetry"])
        self.assertEqual(permit["p43Entrypoint"], p49.P43)


if __name__ == "__main__":
    unittest.main()
