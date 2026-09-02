#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import repository_preflight as rp


class AcceptanceSupersedingGatePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.blobs: dict[str, str] = {}
        self._write_green_fixture()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, rel: str, obj: dict) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    def _delete(self, rel: str) -> None:
        path = self.root / rel
        if path.exists():
            path.unlink()

    def _read(self, rel: str) -> dict:
        return json.loads((self.root / rel).read_text(encoding="utf-8"))

    def _mutate(self, rel: str, **updates) -> None:
        obj = self._read(rel)
        obj.update(updates)
        self._write(rel, obj)

    def _blob(self, rel: str) -> str:
        if rel not in self.blobs:
            raise FileNotFoundError(rel)
        return self.blobs[rel]

    def _green(self):
        return rp.release_gate(self.root, self._blob, run_offline=False)

    def _write_green_fixture(self) -> None:
        formal_pins = {p: f"formal-{i:02d}" for i, p in enumerate(rp.FORMAL_FRESH_PATHS, 1)}
        self.blobs.update(formal_pins)
        self.blobs[rp.HEAD_LABEL_PRODUCT] = "labels-current"

        self._write(rp.FORMAL_CLAIM, {
            "state": "COMPLETE",
            "result": rp.FORMAL_PASS,
            "audited_blobs": formal_pins | {rp.HEAD_LABEL_PRODUCT: "labels-old-formal-context-only"},
        })
        self._write(rp.HISTORICAL_FORMAL_BLOCKED, {
            "state": "BLOCKED",
            "result": "BLOCKED — historical adversarial evidence",
        })

        py_pins = {p: f"py-{i:02d}" for i, p in enumerate(rp.PYLAUNCH_FRESH_PATHS, 1)}
        self.blobs.update(py_pins)
        self._write(rp.PYLAUNCH_CLAIM, {"state": "COMPLETE", "result": rp.PYLAUNCH_PASS})
        self._write(rp.PYLAUNCH_RESULT, {
            "status": "PASS",
            "decision": rp.PYLAUNCH_PASS,
            "validatedProductBlobs": py_pins,
        })

        unified_live = "parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py"
        self.blobs[unified_live] = "recorder-current"
        self._write(rp.RECORDER_CLAIM, {"state": "COMPLETE", "stopCondition": rp.RECORDER_PASS})
        self._write(rp.RECORDER_RESULT, {
            "result": "PASS",
            "stopCondition": rp.RECORDER_PASS,
            "production": {"path": unified_live, "blob": "recorder-current"},
        })

        unified_pins = {p: f"unified-{i:02d}" for i, p in enumerate(rp.UNIFIED_PREFLIGHT_FRESH_PATHS, 1)}
        self.blobs.update(unified_pins)
        self._write(rp.UNIFIED_PREFLIGHT_CLAIM, {
            "state": "COMPLETE",
            "result": rp.UNIFIED_PREFLIGHT_PASS,
            "auditedPreflightBlobs": unified_pins,
        })

        self._write(rp.HEAD_LABEL_IMPL_CLAIM, {"state": "COMPLETE"})
        self._write(rp.HEAD_LABEL_STRICT_FIX_CLAIM, {
            "state": "COMPLETE",
            "result": rp.HEAD_LABEL_STRICT_FIX_COMPLETE,
            "productBlobs": {rp.HEAD_LABEL_PRODUCT: "labels-current"},
        })
        self._write(rp.HEAD_LABEL_QA_CLAIM, {
            "state": "COMPLETE",
            "result": rp.HEAD_LABEL_QA_PASS,
            "auditedProductBlobs": {rp.HEAD_LABEL_PRODUCT: "labels-current"},
        })

        self._write(rp.ONECLICK_CLAIM, {"state": "COMPLETE", "result": rp.ONECLICK_PASS})
        self._write(rp.ONECLICK_MANIFEST, {
            "schema": "wof-owner-oneclick-package-v1",
            "files": [
                {"path": "parallel/PYLAUNCH/wof_launcher/browser.py", "gitBlobSha": py_pins["parallel/PYLAUNCH/wof_launcher/browser.py"]},
                {"path": unified_live, "gitBlobSha": "recorder-current"},
            ],
        })

        endurance_pins = {
            "parallel/ALPHA_TRANSPORT_IMPL/constants.mjs": "endurance-constants",
            "parallel/ALPHA_TRANSPORT_IMPL/page_authority.mjs": "endurance-page",
            "parallel/ALPHA_TRANSPORT_IMPL/worker_runtime.mjs": "endurance-worker",
            "parallel/ALPHA_TRANSPORT_IMPL/acceptance_adapter.mjs": "endurance-adapter",
        }
        self.blobs.update(endurance_pins)
        self._write(rp.ENDURANCE_CLAIM, {
            "state": "COMPLETE",
            "result": rp.ENDURANCE_PASS,
            "sourceIntegrity": {
                "observedBlobShas": {p.removeprefix("parallel/"): sha for p, sha in endurance_pins.items()}
            },
        })

    def assertBlocked(self, needle: str) -> None:
        ok, blockers, _ = self._green()
        self.assertFalse(ok)
        self.assertTrue(any(needle in b for b in blockers), blockers)

    def test_historical_formal_blocked_is_superseded_by_current_pass(self):
        ok, blockers, gates = self._green()
        self.assertTrue(ok, blockers)
        formal = next(g for g in gates if g["name"] == "formalCurrentBlob")
        self.assertTrue(formal["pass"])
        self.assertIn("历史", formal["tail"])

    def test_formal_successor_missing_blocked_or_stale_blocks(self):
        original = self._read(rp.FORMAL_CLAIM)
        with self.subTest("missing"):
            self._delete(rp.FORMAL_CLAIM)
            self.assertBlocked("Formal current-blob successor")
        self._write(rp.FORMAL_CLAIM, original)
        with self.subTest("blocked"):
            self._mutate(rp.FORMAL_CLAIM, state="BLOCKED", result="BLOCKED")
            self.assertBlocked("尚未 COMPLETE")
        self._write(rp.FORMAL_CLAIM, original)
        with self.subTest("stale"):
            self.blobs[rp.FORMAL_FRESH_PATHS[0]] = "drifted"
            self.assertBlocked("blob 已漂移")

    def test_pylaunch_missing_blocked_or_blob_drift_blocks(self):
        original_claim = self._read(rp.PYLAUNCH_CLAIM)
        original_result = self._read(rp.PYLAUNCH_RESULT)
        with self.subTest("missing"):
            self._delete(rp.PYLAUNCH_CLAIM)
            self.assertBlocked("PYLAUNCH Startup Attestation")
        self._write(rp.PYLAUNCH_CLAIM, original_claim)
        with self.subTest("blocked"):
            self._mutate(rp.PYLAUNCH_CLAIM, state="BLOCKED", result="BLOCKED")
            self.assertBlocked("PYLAUNCH Startup Attestation 尚未 COMPLETE")
        self._write(rp.PYLAUNCH_CLAIM, original_claim)
        self._write(rp.PYLAUNCH_RESULT, original_result)
        with self.subTest("blob-drift"):
            self.blobs[rp.PYLAUNCH_FRESH_PATHS[1]] = "drifted"
            self.assertBlocked("PYLAUNCH Startup Attestation blob 已漂移")

    def test_recorder_missing_blocked_or_blob_drift_blocks(self):
        original_claim = self._read(rp.RECORDER_CLAIM)
        with self.subTest("missing"):
            self._delete(rp.RECORDER_CLAIM)
            self.assertBlocked("Unified Recorder in-flight atomicity")
        self._write(rp.RECORDER_CLAIM, original_claim)
        with self.subTest("blocked"):
            self._mutate(rp.RECORDER_CLAIM, state="BLOCKED", stopCondition="BLOCKED")
            self.assertBlocked("尚未 COMPLETE")
        self._write(rp.RECORDER_CLAIM, original_claim)
        with self.subTest("blob-drift"):
            self.blobs["parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py"] = "drifted"
            self.assertBlocked("Unified Recorder in-flight atomicity blob 已漂移")

    def test_oneclick_missing_or_stale_manifest_blocks(self):
        original = self._read(rp.ONECLICK_CLAIM)
        with self.subTest("missing"):
            self._delete(rp.ONECLICK_CLAIM)
            self.assertBlocked("Owner OneClick V3")
        self._write(rp.ONECLICK_CLAIM, original)
        with self.subTest("stale"):
            manifest = self._read(rp.ONECLICK_MANIFEST)
            manifest["files"][0]["gitBlobSha"] = "stale"
            self._write(rp.ONECLICK_MANIFEST, manifest)
            self.assertBlocked("package stale")

    def test_true_5h_missing_blocked_or_stale_snapshot_blocks(self):
        original = self._read(rp.ENDURANCE_CLAIM)
        with self.subTest("missing"):
            self._delete(rp.ENDURANCE_CLAIM)
            self.assertBlocked("True 5h Endurance V2")
        self._write(rp.ENDURANCE_CLAIM, original)
        with self.subTest("blocked"):
            self._mutate(rp.ENDURANCE_CLAIM, state="BLOCKED", result="BLOCKED")
            self.assertBlocked("尚未 COMPLETE")
        self._write(rp.ENDURANCE_CLAIM, original)
        with self.subTest("stale"):
            self.blobs["parallel/ALPHA_TRANSPORT_IMPL/constants.mjs"] = "drifted"
            self.assertBlocked("True 5h Endurance V2 blob 已漂移")

    def test_head_labels_impl_or_fresh_qa_missing_blocked_or_stale_blocks(self):
        impl = self._read(rp.HEAD_LABEL_IMPL_CLAIM)
        qa = self._read(rp.HEAD_LABEL_QA_CLAIM)
        with self.subTest("implementation-missing"):
            self._delete(rp.HEAD_LABEL_IMPL_CLAIM)
            self.assertBlocked("Head Labels implementation")
        self._write(rp.HEAD_LABEL_IMPL_CLAIM, impl)
        with self.subTest("qa-missing"):
            self._delete(rp.HEAD_LABEL_QA_CLAIM)
            self.assertBlocked("Head Labels Fresh QA V2")
        self._write(rp.HEAD_LABEL_QA_CLAIM, qa)
        with self.subTest("qa-blocked"):
            self._mutate(rp.HEAD_LABEL_QA_CLAIM, state="BLOCKED", result="BLOCKED")
            self.assertBlocked("Head Labels Fresh QA V2 尚未 COMPLETE")
        self._write(rp.HEAD_LABEL_QA_CLAIM, qa)
        with self.subTest("qa-stale"):
            self.blobs[rp.HEAD_LABEL_PRODUCT] = "drifted"
            self.assertBlocked("Head Labels")

    def test_all_repository_gates_green_is_preflight_only_pass_with_live_visual_pending(self):
        ok, blockers, gates = self._green()
        self.assertTrue(ok, blockers)
        self.assertTrue(all(g["pass"] for g in gates), gates)
        message = rp.preflight_only_success_message()
        self.assertIn("REPO PREFLIGHT-ONLY PASS", message)
        self.assertIn("1P/2P/3P", message)
        self.assertIn("未连接 Browser/WOF", message)
        self.assertIn("bounded real target-label visual acceptance", message)

    def test_complete_without_pass_verdict_never_counts_as_green(self):
        for rel, field in (
            (rp.PYLAUNCH_CLAIM, "result"),
            (rp.RECORDER_CLAIM, "stopCondition"),
            (rp.UNIFIED_PREFLIGHT_CLAIM, "result"),
            (rp.HEAD_LABEL_QA_CLAIM, "result"),
            (rp.ONECLICK_CLAIM, "result"),
            (rp.ENDURANCE_CLAIM, "result"),
        ):
            with self.subTest(rel=rel):
                saved = self._read(rel)
                bad = copy.deepcopy(saved)
                bad[field] = "COMPLETE"
                self._write(rel, bad)
                ok, _, _ = self._green()
                self.assertFalse(ok)
                self._write(rel, saved)


if __name__ == "__main__":
    unittest.main()
