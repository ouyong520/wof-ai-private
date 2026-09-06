from __future__ import annotations
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

import p43_bounded_zero_click_live_diagnostic_entry as e


class EntryTests(unittest.TestCase):
    def test_p42_exact_identity_is_pinned(self):
        self.assertEqual("7b523187a955179b04155b758847c82aaf569a0d", e.P42_TESTED_COMMIT)
        self.assertEqual("32b9c50e8a72de1a097b8ce5dc91b69bdcef0219", e.P42_TESTED_BLOB)
        self.assertEqual("parallel/RENDER_AUTHORITY_V2/gstyphoon_renderer_submit_correlation_probe.js", e.P42_REL)

    def test_p16_binding_requires_all_exact_fields(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "p16.json"
            path.write_text(json.dumps({"runtime":{"epoch":"r","rendererEpoch":"re","authorityKey":"a"},"world":{"pageTargetId":"p"}}), encoding="utf-8")
            args = types.SimpleNamespace(p16_evidence=path)
            binding, err = e._p16_binding(args)
            self.assertIsNone(err)
            self.assertEqual({"runtimeEpoch":"r","rendererEpoch":"re","authorityKey":"a","pageTargetId":"p"}, binding)
            path.write_text(json.dumps({"runtime":{"epoch":"r"},"world":{"pageTargetId":"p"}}), encoding="utf-8")
            binding, err = e._p16_binding(args)
            self.assertIsNone(binding)
            self.assertEqual("P16_EXACT_P42_BINDING_INCOMPLETE", err)

    def test_absent_p16_records_explicit_p42_absence(self):
        args = types.SimpleNamespace(p16_evidence=None)
        out = e._start_p42(args)
        self.assertEqual("P42_CORRELATION_PROBE_NOT_PRESENT", out["state"])
        self.assertFalse(out["present"])
        self.assertEqual(e.P42_TESTED_COMMIT, out["testedCommit"])

    def test_stable_receipt_removes_self_hash_and_archives_p42(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = types.SimpleNamespace(output_root=root)
            receipt = {
                "schema": e.core.RECEIPT_SCHEMA,
                "candidateBinding": {"sourceCommit":"b"*40,"packageVersion":"v"},
                "firstFailingGate": {"gate":"P36_SOURCE_GATE","state":"BLOCKED","reason":"x"},
                "passedBeforeFirstFailure": ["CANDIDATE_BINDING"],
                "p36": {"teardownReason":"done"},
                "safety": {"alphaLiveMoved":False},
                "gateTimeline": [],
                "artifacts": {"receipt":{"path":"stale","sha256":"stale"},"humanReceipt":{"path":"stale2","sha256":"stale2"}},
            }
            p42 = {"state":"P42_CORRELATION_PROBE_PRESENT","present":True,"bundle":{"schema":e.core.P42_SCHEMA},"authorityEligible":False}
            stable = e._stable_receipts(args, receipt, {"present":True}, p42, {})
            persisted = json.loads((root / "P43_DIAGNOSTIC_RECEIPT.json").read_text(encoding="utf-8"))
            self.assertNotIn("receipt", persisted["artifacts"])
            self.assertNotIn("humanReceipt", persisted["artifacts"])
            self.assertEqual("P42_CORRELATION_PROBE_PRESENT", persisted["p42"]["state"])
            self.assertTrue((root / "raw" / "P42_CORRELATION_BUNDLE.json").is_file())
            self.assertEqual(e.core.sha256_bytes((root / "P43_DIAGNOSTIC_RECEIPT.json").read_bytes()), stable["receiptSha256"])

    def test_raw_candidate_binding_archive_rechecks_sha_and_blob(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payloads = {n: (f'{{"name":"{n}"}}\n').encode() for n in ("pointer","provenance","candidate","attestation","manifest")}
            binding = {"state":"PASS","metadataCommit":"a"*40}
            for n, data in payloads.items():
                binding[n] = {"path":f"x/{n}.json","sha256":e.core.sha256_bytes(data),"gitBlobSha":e.core.git_blob_sha(data)}
            class FG:
                def __init__(self, _): pass
                def read_blob(self, commit, rel):
                    name=Path(rel).stem
                    return payloads[name]
            args=types.SimpleNamespace(repo_root=root, output_root=root)
            with mock.patch.object(e.core, "GitReader", FG):
                out=e._raw_binding_artifacts(args,binding)
            self.assertEqual(set(payloads), set(out))
            self.assertEqual(payloads["manifest"], (root/"raw"/"candidate_binding"/"MANIFEST.json").read_bytes())
            self.assertEqual("a"*40, out["candidate"]["metadataCommit"])

    def test_cmd_contract_targets_integrated_wrapper_by_name(self):
        self.assertEqual("WOFP43P42CORRELATIONPROBE", e.P42_INSTANCE_GLOBAL)


if __name__ == "__main__":
    unittest.main()
