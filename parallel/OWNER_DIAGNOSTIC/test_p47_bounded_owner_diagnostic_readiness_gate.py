from __future__ import annotations

from copy import deepcopy
import unittest

import p47_bounded_owner_diagnostic_readiness_gate as core
import p47_bounded_owner_diagnostic_readiness_gate_final as final


def _claim(spec, token):
    return {
        "state": "COMPLETE",
        "stageId": spec["stage"],
        "dedupKey": spec["dedup"],
        "claimToken": token,
        "testedCommit": spec["tested"],
        "resultPath": spec["result"],
        "resultCommit": spec["resultCommit"],
    }


def happy_snapshot():
    candidate_map = {
        core.P43_CORE_PATH: "coreblob",
        core.P43_CONTINUATION_PATH: "continuationblob",
        core.PINS_PATH: "pinsblob",
    }
    p43_token, p45_token, p46_token = "p43token", "p45token", "p46token"
    p43 = {
        "state": "COMPLETE",
        "stageId": core.STAGES["p43"]["stage"],
        "claimToken": p43_token,
        "testedCommit": core.P43_TESTED,
        "testedTree": core.P43_TREE,
        "testedCandidateMetadata": {"path": core.CANDIDATE_PATH, "gitBlobSha": "candidateblob"},
        "receiptContract": {
            "preservesExactCandidatePackageManifestAttestationProvenancePointer": True,
            "preservesAllPageTargetsAndAuthoritativePageWorkerWasmAssociation": True,
            "preservesP39VisibleHiddenLostStaleAmbiguousReacquire": True,
            "preservesP42CompleteRawBundleBindingSealAndTeardown": True,
            "preservesP46CompleteRawStackFingerprintWasmTruthJsCallerModuleAsmBindingAssociationsAndTeardown": True,
        },
        "p46TruthBoundary": {
            "wasmFunctionIndex": list(core.TRUTH_STATES),
            "wasmFunctionName": list(core.TRUTH_STATES),
            "wasmOffset": list(core.TRUTH_STATES),
        },
        "authorityBoundary": {
            "authorityEligible": False,
            "mappingOnly": True,
            "createsNativeMarkerSourceExport": False,
            "emitsRendererAuthorityProof": False,
            "changesP29Acceptance": False,
            "changesP32Qualification": False,
            "retryEligibilityMinted": False,
            "promotionEligibilityMinted": False,
            "p40BlockerResolved": False,
            "p40Blocker": core.P40_BLOCKER,
        },
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "zeroClick": True,
            "manualSeedRequired": False,
            "promotionPerformed": False,
            "alphaLiveMoved": False,
        },
    }
    p45 = {
        "state": "COMPLETE",
        "stageId": core.STAGES["p45"]["stage"],
        "claimToken": p45_token,
        "testedCandidateCommit": core.P45_TESTED,
        "stagingContract": {
            "zeroClick": True,
            "manualSeedRequired": False,
            "bindingFields": ["runtimeEpoch", "rendererEpoch", "authorityKey"],
            "rawBundleFiltering": False,
        },
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
    }
    p46 = {
        "state": "COMPLETE",
        "stageId": core.STAGES["p46"]["stage"],
        "claimToken": p46_token,
        "testedCommit": core.P46_TESTED,
        "authorityBoundary": {
            "guessedWasmSymbol": False,
            "guessedWasmOffset": False,
        },
    }
    records = {}
    for key, result, token in (("p43", p43, p43_token), ("p45", p45, p45_token), ("p46", p46, p46_token)):
        spec = core.STAGES[key]
        records[key] = {"result": result, "canonical": _claim(spec, token), "claim": _claim(spec, token)}
    return {
        "head": "f" * 40,
        "requestedRunBudget": 1,
        "p43TestedTree": core.P43_TREE,
        "records": records,
        "candidate": {
            "stageId": core.STAGES["p43"]["stage"],
            "claimToken": p43_token,
            "state": "FROZEN_FOR_EXACT_BYTE_TEST",
            "testedBlobMap": candidate_map,
            "safety": {
                "zeroClick": True,
                "manualSeedRequired": False,
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
                "promotionPerformed": False,
                "alphaLiveMoved": False,
            },
        },
        "pins": {
            "p45": {"testedCommit": core.P45_TESTED, "exactFiles": {"p45.py": "p45blob"}},
            "p46": {"testedCommit": core.P46_TESTED, "sourcePath": core.P46_SOURCE_PATH, "sourceGitBlobSha": "p46blob", "truthStates": list(core.TRUTH_STATES)},
        },
        "blobs": {
            core.CANDIDATE_PATH: "candidateblob",
            core.P43_CORE_PATH: "coreblob",
            core.P43_CONTINUATION_PATH: "continuationblob",
            core.PINS_PATH: "pinsblob",
            "p45.py": "p45blob",
            core.P46_SOURCE_PATH: "p46blob",
        },
        "texts": {
            core.P43_CORE_PATH: "MAX_CONSOLE_EVENTS = 512\nMAX_LOG_BYTES = 8 * 1024 * 1024\nmin(args.duration, 60.0)\nP43_BOUNDED_TEARDOWN\n",
            core.P43_CONTINUATION_PATH: "runtimeEpoch rendererEpoch authorityKey P45_STALE_OR_MIXED_AUTHORITY_BINDING P46_STALE_OR_MIXED_AUTHORITY_BINDING P46_TEARDOWN_CONFLICT",
            core.P46_SOURCE_PATH: "maxWallMs:15000 maxEvents:384 BOUNDED_EVENT_LIMIT_REACHED MODULE_OR_ASM_IDENTITY_CHANGED WRAPPER_REPLACED_EXTERNALLY",
        },
        "progress": {"state": "ACTIVE", "testedCommit": "stale-progress-must-not-win"},
    }


class P47ReadinessTests(unittest.TestCase):
    def test_exact_happy_path_ready_with_budget_one(self):
        out = final.evaluate(happy_snapshot())
        self.assertEqual(core.READY, out["decision"])
        self.assertEqual(1, out["runBudget"])
        self.assertEqual([], out["blockerCodes"])

    def test_terminal_result_precedes_stale_progress(self):
        s = happy_snapshot()
        s["progress"] = {"state": "ACTIVE", "claimToken": "wrong", "testedCommit": "wrong"}
        out = final.evaluate(s)
        self.assertEqual(core.READY, out["decision"])
        self.assertEqual("RESULT_AND_CLOSED_CLAIMS_ONLY_PROGRESS_IGNORED", out["terminalAuthority"])

    def test_missing_terminal_result_blocks(self):
        s = happy_snapshot()
        s["records"]["p45"]["result"] = {}
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertEqual(0, out["runBudget"])
        self.assertIn("P45_RESULT_NOT_COMPLETE", out["blockerCodes"])

    def test_claim_mismatch_blocks(self):
        s = happy_snapshot()
        s["records"]["p46"]["claim"]["claimToken"] = "mismatch"
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertIn("P46_CLAIM_CLAIM_TOKEN_MISMATCH", out["blockerCodes"])

    def test_tested_tree_mismatch_blocks(self):
        s = happy_snapshot()
        s["p43TestedTree"] = "0" * 40
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertIn("P43_TESTED_TREE_MISMATCH", out["blockerCodes"])

    def test_required_blob_drift_blocks(self):
        s = happy_snapshot()
        s["blobs"][core.P43_CORE_PATH] = "drifted"
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertIn("P43_REQUIRED_IMPLEMENTATION_BLOB_MISMATCH", out["blockerCodes"])

    def test_dependency_pin_mismatch_blocks(self):
        s = happy_snapshot()
        s["pins"]["p46"]["testedCommit"] = "0" * 40
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertIn("P46_DEPENDENCY_PIN_MISMATCH", out["blockerCodes"])

    def test_alpha_live_or_promotion_blocks(self):
        s = happy_snapshot()
        s["candidate"]["safety"]["alphaLiveMoved"] = True
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertIn("PROMOTION_OR_ALPHA_LIVE_MOVEMENT_PRESENT", out["blockerCodes"])

    def test_requested_budget_above_one_blocks_and_zeroes_budget(self):
        s = happy_snapshot()
        s["requestedRunBudget"] = 2
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertEqual(0, out["runBudget"])
        self.assertIn("RUN_BUDGET_NOT_EXACTLY_ONE", out["blockerCodes"])

    def test_wasm_guessing_blocks(self):
        s = happy_snapshot()
        s["records"]["p46"]["result"]["authorityBoundary"]["guessedWasmOffset"] = True
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertIn("P46_WASM_GUESSING_ENABLED", out["blockerCodes"])

    def test_raw_evidence_contract_missing_blocks(self):
        s = happy_snapshot()
        s["records"]["p43"]["result"]["receiptContract"]["preservesP46CompleteRawStackFingerprintWasmTruthJsCallerModuleAsmBindingAssociationsAndTeardown"] = False
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertIn("P46_RAW_EVIDENCE_PRESERVATION_MISSING", out["blockerCodes"])


if __name__ == "__main__":
    unittest.main()
