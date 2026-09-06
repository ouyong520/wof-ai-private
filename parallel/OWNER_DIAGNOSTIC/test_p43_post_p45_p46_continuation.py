from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest

import p43_post_p45_p46_continuation as h


class P43PostP45P46ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.binding = {
            "runtimeEpoch": "runtime-epoch-1234567890",
            "rendererEpoch": "renderer-epoch-1234567890",
            "authorityKey": "authority-key-exact",
        }

    def p45_fixture(self):
        p42_bundle = {
            "schema": h.P42_SCHEMA,
            "binding": dict(self.binding),
            "authorityEligible": False,
        }
        return {
            "schema": h.P45_SCHEMA,
            "enabled": True,
            "binding": {**self.binding, "rendererEpochSource": "P45_DIAGNOSTIC_SESSION_ONLY", "productionRendererAuthority": False},
            "p39": {
                "classification": h.P39_CLASSIFICATION,
                "testedCommit": h.P45_P39_TESTED_COMMIT,
                "status": {"classification": h.P39_CLASSIFICATION},
                "lifecycle": {
                    "visiblePlayers": ["P1"],
                    "hiddenPlayers": ["P2", "P3"],
                    "lostPlayers": ["P2"],
                    "stale": False,
                    "ambiguous": False,
                    "reacquireCountByPlayer": {"P1": 2, "P2": 1, "P3": 0},
                },
            },
            "p42": {
                "classification": h.P42_CLASSIFICATION,
                "testedCommit": h.P45_P42_TESTED_COMMIT,
                "rawBundle": p42_bundle,
                "sealReason": "P43_FINAL_LIFO_TEARDOWN",
                "teardown": {"installed": False, "conflicts": []},
            },
            "authorityEligibility": {
                "p29Pass": False,
                "p32NativeMarkerQualification": False,
                "p36RendererSourceTrace": False,
                "retry": False,
                "promotion": False,
            },
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        }

    def p46_fixture(self):
        return {
            "schema": h.P46_SCHEMA,
            "state": "CAPTURE_READY",
            "reason": "P43_FINAL_LIFO_TEARDOWN",
            "terminal": True,
            "binding": dict(self.binding),
            "moduleSurfaceAtStart": {
                "Module": {"status": "AVAILABLE", "objectId": "M1"},
                "ModuleAsm": {"status": "AVAILABLE", "objectId": "A2"},
                "relationship": "DISTINCT_OBJECTS",
            },
            "events": [
                {
                    "eventSequence": 1,
                    "kind": "DRAW",
                    "method": "drawElements",
                    "binding": dict(self.binding),
                    "callsite": {
                        "rawStack": "Error: P46_CALLSITE\n at wasm-function[42]:0x2a\n at dynCall_vi (runtime.js:1:2)",
                        "rawStackStatus": "AVAILABLE",
                        "normalizedCallsiteFingerprint": {"status": "AVAILABLE", "algorithm": "FNV1A64", "value": "0123456789abcdef"},
                        "wasm": {
                            "status": "AVAILABLE",
                            "functionIndexStatus": "AVAILABLE",
                            "functionIndices": [42],
                            "functionNameStatus": "UNRESOLVED",
                            "functionNames": ["UNRESOLVED"],
                            "offsetStatus": "AVAILABLE",
                            "offsets": ["0x2a"],
                        },
                        "jsWrapperOrImport": {
                            "status": "AVAILABLE",
                            "immediateJsCaller": {"functionName": "dynCall_vi"},
                            "observedFunctionNames": ["dynCall_vi"],
                            "semanticRole": "UNRESOLVED",
                        },
                        "moduleSurface": {
                            "Module": {"status": "AVAILABLE", "objectId": "M1"},
                            "ModuleAsm": {"status": "AVAILABLE", "objectId": "A2"},
                            "relationship": "DISTINCT_OBJECTS",
                        },
                    },
                    "exactAssociations": {
                        "associationRule": "EXACT_OBJECT_OR_ATTRIB_STATE_IDENTITY_ONLY",
                        "semanticSelectionMade": False,
                    },
                },
                {
                    "eventSequence": 2,
                    "kind": "BUFFER",
                    "method": "bufferData",
                    "binding": dict(self.binding),
                    "callsite": {
                        "rawStack": "",
                        "rawStackStatus": "NOT_AVAILABLE",
                        "normalizedCallsiteFingerprint": {"status": "NOT_AVAILABLE", "algorithm": "FNV1A64", "value": None},
                        "wasm": {
                            "status": "NOT_AVAILABLE",
                            "functionIndexStatus": "NOT_AVAILABLE",
                            "functionIndices": ["NOT_AVAILABLE"],
                            "functionNameStatus": "NOT_AVAILABLE",
                            "functionNames": ["NOT_AVAILABLE"],
                            "offsetStatus": "NOT_AVAILABLE",
                            "offsets": ["NOT_AVAILABLE"],
                        },
                        "jsWrapperOrImport": {
                            "status": "NOT_AVAILABLE",
                            "immediateJsCaller": "NOT_AVAILABLE",
                            "observedFunctionNames": ["NOT_AVAILABLE"],
                            "semanticRole": "UNRESOLVED",
                        },
                        "moduleSurface": {
                            "Module": {"status": "NOT_AVAILABLE", "objectId": "NOT_AVAILABLE"},
                            "ModuleAsm": {"status": "NOT_AVAILABLE", "objectId": "NOT_AVAILABLE"},
                            "relationship": "NOT_AVAILABLE",
                        },
                    },
                },
            ],
            "mappingAssessment": {
                "status": "CALLSITE_CORRELATION_EVIDENCE_ONLY",
                "selectionMade": False,
                "orderOnlySelection": False,
                "timingOnlySelection": False,
                "nearestSelection": False,
                "guessedWasmSymbol": False,
                "guessedWasmOffset": False,
                "authorityEligible": False,
            },
            "teardown": {"complete": True, "conflicts": []},
            "authorityEligible": False,
            "mappingOnly": True,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        }

    def test_exact_dependency_pins_match_terminal_authorities(self):
        pins = h.dependency_pins()
        self.assertEqual("3dac7a9e2cbe4a23c3de44eb15cf45f19b136149", pins["p45"]["testedCommit"])
        self.assertEqual("752a172911d76eb3573684b200d597926c819716", pins["p45"]["sourceGitBlobSha"])
        self.assertEqual("210efdda5bbf3715989c751eb90442f26f42d0a9", pins["p46"]["testedCommit"])
        self.assertEqual("efd71e25e28f171e080774eb5aa1309a0d7bbe2b", pins["p46"]["sourceGitBlobSha"])
        self.assertEqual(["P45_P39", "P45_P42", "P46"], pins["composition"]["installOrder"])
        self.assertEqual(["P46", "P45_P42_AND_P39"], pins["composition"]["teardownOrder"])

    def test_dependency_pin_json_matches_code(self):
        raw = json.loads((Path(__file__).with_name("P43_POST_P45_P46_DEPENDENCY_PINS.json")).read_text())
        pins = h.dependency_pins()
        self.assertEqual(pins["p45"]["testedCommit"], raw["p45"]["testedCommit"])
        self.assertEqual(pins["p45"]["sourceGitBlobSha"], raw["p45"]["sourceGitBlobSha"])
        self.assertEqual(pins["p46"]["testedCommit"], raw["p46"]["testedCommit"])
        self.assertEqual(pins["p46"]["sourceGitBlobSha"], raw["p46"]["sourceGitBlobSha"])
        self.assertEqual(pins["composition"], raw["composition"])

    def test_exact_dependency_git_blobs_exist(self):
        repo = Path(__file__).resolve().parents[2]
        for rel, wanted in h.P45_EXACT_FILES.items():
            cp = subprocess.run(
                ["git", "rev-parse", f"{h.P45_TESTED_COMMIT}:{rel}"],
                cwd=repo,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, cp.returncode, cp.stderr)
            self.assertEqual(wanted, cp.stdout.strip())
        cp = subprocess.run(
            ["git", "rev-parse", f"{h.P46_TESTED_COMMIT}:{h.P46_SOURCE_REL}"],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, cp.returncode, cp.stderr)
        self.assertEqual(h.P46_SOURCE_BLOB, cp.stdout.strip())

    def test_p45_readout_is_consumed_unfiltered_and_binding_exact(self):
        raw = self.p45_fixture()
        self.assertEqual((True, "P45_P39_P42_BOUND_EXACT"), h.validate_p45_readout(raw, self.binding))
        p42 = h._p42_from_p45({"readout": raw})
        self.assertEqual("P42_CORRELATION_PROBE_PRESENT", p42["state"])
        self.assertIs(raw["p42"]["rawBundle"], p42["bundle"])
        self.assertEqual(["P1"], raw["p39"]["lifecycle"]["visiblePlayers"])
        self.assertEqual(["P2", "P3"], raw["p39"]["lifecycle"]["hiddenPlayers"])

    def test_p45_stale_binding_fails_closed(self):
        raw = self.p45_fixture()
        raw["binding"]["rendererEpoch"] = "stale-renderer"
        ok, reason = h.validate_p45_readout(raw, self.binding)
        self.assertFalse(ok)
        self.assertEqual("P45_STALE_OR_MIXED_AUTHORITY_BINDING", reason)

    def test_p46_preserves_raw_stack_fingerprint_and_wasm_truth_states(self):
        raw = self.p46_fixture()
        self.assertEqual((True, "P46_RAW_CALLSITE_BUNDLE_BOUND_EXACT"), h.validate_p46_bundle(raw, self.binding))
        first = raw["events"][0]["callsite"]
        self.assertIn("wasm-function[42]", first["rawStack"])
        self.assertEqual("AVAILABLE", first["normalizedCallsiteFingerprint"]["status"])
        self.assertEqual("AVAILABLE", first["wasm"]["functionIndexStatus"])
        self.assertEqual("UNRESOLVED", first["wasm"]["functionNameStatus"])
        second = raw["events"][1]["callsite"]
        self.assertEqual("NOT_AVAILABLE", second["wasm"]["status"])
        self.assertEqual("NOT_AVAILABLE", second["wasm"]["offsetStatus"])

    def test_p46_guessed_truth_state_or_binding_is_rejected(self):
        raw = self.p46_fixture()
        raw["events"][0]["callsite"]["wasm"]["functionNameStatus"] = "GUESSED"
        ok, reason = h.validate_p46_bundle(raw, self.binding)
        self.assertFalse(ok)
        self.assertIn("functionNameStatus_INVALID", reason)
        raw = self.p46_fixture()
        raw["binding"]["authorityKey"] = "mixed"
        self.assertEqual((False, "P46_STALE_OR_MIXED_AUTHORITY_BINDING"), h.validate_p46_bundle(raw, self.binding))

    def test_p46_wrapper_composition_uses_exact_p45_binding_and_lifo_teardown(self):
        start = h._p46_start_expression(self.binding)
        stop = h._p46_stop_expression(self.binding, "P43_FINAL_LIFO_TEARDOWN")
        self.assertIn("__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1", start)
        self.assertIn("strictModuleIdentity:true", start)
        self.assertIn("__WOF_P43_P46_CALLSITE_PROBE_V1__", start)
        self.assertIn("STALE_OR_MIXED_AUTHORITY_BINDING", stop)
        self.assertIn("MODULE_OR_ASM_IDENTITY_CHANGED", stop)
        self.assertIn("p.stop", stop)
        self.assertIn("delete window.__WOF_P43_P46_CALLSITE_PROBE_V1__", stop)

    def test_gate_merge_reports_first_failure_after_successful_pre_gates(self):
        pre = [
            {"seq": 1, "atUtc": "a", "gate": "CANDIDATE_BINDING", "state": "PASS", "reason": "ok"},
            {"seq": 2, "atUtc": "b", "gate": "P45_STAGING_GATE", "state": "PASS", "reason": "ok"},
            {"seq": 3, "atUtc": "c", "gate": "P46_CALLSITE_GATE", "state": "PASS", "reason": "ok"},
        ]
        core_rows = [
            {"seq": 1, "atUtc": "d", "gate": "CANDIDATE_BINDING", "state": "PASS", "reason": "ok"},
            {"seq": 2, "atUtc": "e", "gate": "DEDICATED_RUNTIME_ENVIRONMENT", "state": "PASS", "reason": "ok"},
            {"seq": 3, "atUtc": "f", "gate": "BROWSER_ENDPOINT", "state": "PASS", "reason": "ok"},
            {"seq": 4, "atUtc": "g", "gate": "PAGE_WORKER_WASM_ASSOCIATION", "state": "PASS", "reason": "ok"},
            {"seq": 5, "atUtc": "h", "gate": "P16_GATE", "state": "PASS", "reason": "ok"},
            {"seq": 6, "atUtc": "i", "gate": "P9_GATE", "state": "PASS", "reason": "ok"},
            {"seq": 7, "atUtc": "j", "gate": "P36_SOURCE_GATE", "state": "BLOCKED", "reason": "DIRECT_SOURCE_MISSING"},
        ]
        rows = h.merge_gate_timelines(pre, core_rows, [])
        first = h._first_failure(rows)
        self.assertEqual("P36_SOURCE_GATE", first["gate"])
        passed = h._passed_before(rows, first)
        self.assertIn("P45_STAGING_GATE", passed)
        self.assertIn("P46_CALLSITE_GATE", passed)
        self.assertIn("P9_GATE", passed)

    def test_final_entrypoint_consumes_continuation_not_legacy_standalone_p42(self):
        source = Path(__file__).with_name("p43_bounded_zero_click_live_diagnostic_final.py").read_text()
        self.assertIn("p43_post_p45_p46_continuation", source)
        self.assertNotIn("_start_p42", source)
        continuation_source = Path(h.__file__).read_text()
        self.assertNotIn("__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__", continuation_source)
        self.assertNotIn("WOFNativeMarkerRendererSubmitSourceV1", continuation_source)


if __name__ == "__main__":
    unittest.main()
