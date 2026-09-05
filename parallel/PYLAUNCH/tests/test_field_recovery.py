from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

import wof_launcher.discovery_v2 as discovery_module
from wof_launcher.alpha_runtime import AlphaRuntimeError, AlphaRuntimeManager, git_blob_sha
from wof_launcher.discovery_v2 import TargetChoice
from wof_launcher.probe import LIGHT_WORKER_PROBE, PAGE_PROBE, WORLD_SHA256
from wof_launcher.probe_v2 import IDENTITY_PROBE, select_unique_exact_candidate
from wof_launcher.runtime_authority import RuntimeAuthorityGuard

GOOD_LIGHT = {"moduleOk": True, "heapOk": True, "moduleKey": "m", "heapBytes": 0x400000, "ramBase": 0x20000, "ramWithinHeap": True, "readOnly": True, "ramWrites": 0, "inputInjection": False}
GOOD_ID = {"ok": True, "sha256": WORLD_SHA256, "locator": {"heapBase": 0x1000, "swap16": False}}
CHOICE = TargetChoice({"targetId": "page", "url": "https://game/wof"}, {"targetId": "worker", "url": "blob:x"}, GOOD_LIGHT, GOOD_ID)


class FakeSession:
    def __init__(self, client, target_id): self.client = client; self.target_id = target_id
    def request(self, method, params=None, timeout=None):
        self.client.methods.append((self.target_id, method))
        if method == "Runtime.getIsolateId": return {"id": self.client.isolates[self.target_id]}
        if method == "Runtime.enable": return {}
        raise AssertionError(method)
    def evaluate(self, expression, *, await_promise=False, timeout=8.0):
        self.client.expressions.append((self.target_id, expression))
        if expression == PAGE_PROBE: return {"gameSurface": True}
        if expression == LIGHT_WORKER_PROBE: return dict(self.client.light)
        raise AssertionError("health guard must never run identity/full-ROM probe")
    def close(self): pass


class FakeClient:
    def __init__(self):
        self.isolates = {"page": "page-a", "worker": "worker-a"}; self.light = dict(GOOD_LIGHT); self.methods = []; self.expressions = []
    def request(self, method, params=None, **kwargs):
        self.methods.append(("browser", method))
        if method == "Target.getTargets": return {"targetInfos": [{"targetId": "page", "type": "page"}, {"targetId": "worker", "type": "worker"}]}
        raise AssertionError(method)
    def attach(self, target_id): return FakeSession(self, target_id)


class FakeAlphaRuntime(AlphaRuntimeManager):
    def __init__(self, root: Path):
        super().__init__(root); self.calls = []
        # This legacy unit fixture tests the Alpha release start path, not Browser
        # projection calibration. Mark projection as already live-proved in-fixture so
        # the new proof installer is not asked for package files the fixture omits.
        self._projection._profiles = {"player": {}, "enemy": {}}
        self._projection._state = "PROVED_LIVE_PROCESS_AUTHORITY"
    def _load_manifest(self): return {"packageVersion": "field-self-check"}
    def _page_install(self, client, page_id, pair_nonce):
        self.calls.append(("page", page_id)); return {
            "session": "1" * 32,
            "channel": "WOF_ALPHA_" + "1" * 32,
            "pairGeneration": 1,
            "pairNonce": pair_nonce,
            "canonicalOverlayCapable": True,
            "canonicalOverlayStatus": {"bound": False},
        }
    def _worker_install(self, client, worker_id, pair, identity, runtime_epoch):
        self.calls.append(("worker", worker_id)); return {"running": True, "identity": dict(identity), "readOnly": True, "ramWrites": 0, "inputInjection": False}
    def _evaluate(self, client, target_id, expression, *, await_promise=False, timeout=12.0):
        self.calls.append(("status", target_id)); return {"attachState": "PAIRED", "hudLoaded": True, "hudStatus": {"mode": "field-self-check"}}
    def revoke(self, client=None):
        self._authority_key = None; self._page_target_id = None; self._worker_target_id = None
        self._status = {"requested": True, "running": False, "readOnly": True, "ramWrites": 0, "inputInjection": False}


class FieldRecoveryTests(unittest.TestCase):
    def test_discovery_directly_uses_strict_field_identity_probe(self): self.assertEqual(IDENTITY_PROBE, discovery_module.IDENTITY_PROBE)
    def test_identity_probe_hashes_every_structural_candidate_and_is_strict(self):
        self.assertIn("for(const c of found)", IDENTITY_PROBE); self.assertIn("candidateDiagnostics.filter(x=>x.exactMatch)", IDENTITY_PROBE); self.assertIn("if(exact.length===0)", IDENTITY_PROBE); self.assertIn("if(exact.length>1)", IDENTITY_PROBE); self.assertIn("exactMatchCount:1", IDENTITY_PROBE); self.assertNotIn("if(found.length!==1)", IDENTITY_PROBE)
    def test_exact_candidate_decision_zero_candidates_rejects(self):
        with self.assertRaisesRegex(ValueError, "no ROM locator"): select_unique_exact_candidate([])
    def test_exact_candidate_decision_one_exact_accepts(self):
        row = {"heapBase": 1, "sha256": WORLD_SHA256}; self.assertEqual(row, select_unique_exact_candidate([row]))
    def test_two_candidates_unique_exact_match_accepts_only_exact(self):
        wrong = {"heapBase": 1, "sha256": "0" * 64}; exact = {"heapBase": 2, "sha256": WORLD_SHA256}; self.assertEqual(exact, select_unique_exact_candidate([wrong, exact]))
    def test_two_candidates_with_no_exact_match_reject(self):
        with self.assertRaisesRegex(ValueError, "no ROM locator"): select_unique_exact_candidate([{"heapBase": 1, "sha256": "0" * 64}, {"heapBase": 2, "sha256": "1" * 64}])
    def test_multiple_exact_matches_remain_ambiguous(self):
        with self.assertRaisesRegex(ValueError, "ambiguous exact"): select_unique_exact_candidate([{"heapBase": 1, "sha256": WORLD_SHA256}, {"heapBase": 2, "sha256": WORLD_SHA256}])
    def test_stable_runtime_uses_only_cheap_health_not_identity_probe(self):
        client = FakeClient(); guard = RuntimeAuthorityGuard(); guard.accept(client, CHOICE); client.expressions.clear(); ok, reason, diag = guard.healthy(client, CHOICE)
        self.assertTrue(ok, reason); self.assertEqual("cached-runtime-health", diag["path"]); self.assertFalse(diag["fullIdentityScan"]); self.assertEqual([PAGE_PROBE, LIGHT_WORKER_PROBE], [expr for _, expr in client.expressions]); self.assertFalse(any("crypto.subtle.digest" in expr for _, expr in client.expressions)); self.assertEqual(1, guard.diagnostics()["fullAttestations"]); self.assertEqual(1, guard.diagnostics()["cheapHealthChecks"])
    def test_same_target_worker_replacement_revokes_cached_authority(self):
        client = FakeClient(); guard = RuntimeAuthorityGuard(); guard.accept(client, CHOICE); client.isolates["worker"] = "worker-b"; ok, reason, _ = guard.healthy(client, CHOICE); self.assertFalse(ok); self.assertIn("generation changed", reason); self.assertFalse(guard.diagnostics()["accepted"])
    def test_same_target_page_replacement_revokes_cached_authority(self):
        client = FakeClient(); guard = RuntimeAuthorityGuard(); guard.accept(client, CHOICE); client.isolates["page"] = "page-b"; ok, reason, _ = guard.healthy(client, CHOICE); self.assertFalse(ok); self.assertIn("generation changed", reason)
    def test_heap_generation_change_revokes_cached_authority(self):
        client = FakeClient(); guard = RuntimeAuthorityGuard(); guard.accept(client, CHOICE); client.light["heapBytes"] += 65536; ok, reason, _ = guard.healthy(client, CHOICE); self.assertFalse(ok); self.assertIn("generation changed", reason)
    def test_package_selected_blob_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="WOF 中文 package ") as td:
            root = Path(td); rel = "product/alpha/wof_alpha_field_adapter.js"; p = root / rel; p.parent.mkdir(parents=True); p.write_text("safe", encoding="utf-8")
            manifest = {"packageVersion": "field-v1", "files": [{"path": rel, "gitBlobSha": git_blob_sha(p.read_bytes())}]}; (root / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            manager = AlphaRuntimeManager(root); self.assertEqual(b"safe", manager._verified_bytes(rel)); p.write_text("mutated", encoding="utf-8")
            with self.assertRaises(AlphaRuntimeError): manager._verified_bytes(rel)
    def test_accepted_authority_reaches_alpha_release_start(self):
        with tempfile.TemporaryDirectory() as td:
            manager = FakeAlphaRuntime(Path(td)); status = manager.ensure_running(object(), CHOICE, "authority-generation-a"); self.assertTrue(status["running"]); self.assertTrue(status["readOnly"]); self.assertEqual(0, status["ramWrites"]); self.assertFalse(status["inputInjection"]); self.assertEqual([("page", "page"), ("worker", "worker"), ("status", "page")], manager.calls)
    def test_invalid_authority_never_starts_alpha_or_false_overlay_path(self):
        with tempfile.TemporaryDirectory() as td:
            manager = FakeAlphaRuntime(Path(td)); invalid = TargetChoice({"targetId": "page"}, {"targetId": "worker"}, GOOD_LIGHT, {"ok": False})
            with self.assertRaisesRegex(AlphaRuntimeError, "没有可激活"): manager.ensure_running(object(), invalid, "invalid")
            self.assertEqual([], manager.calls); self.assertFalse(manager.status()["running"])


if __name__ == "__main__": unittest.main()
