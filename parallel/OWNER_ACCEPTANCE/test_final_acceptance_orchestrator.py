from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import final_acceptance_orchestrator as sut


def dump(path: Path, value: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def candidate(package="pkg-1", commit="a" * 40):
    return {
        "schema": "wof-owner-oneclick-package-v1",
        "packageVersion": package,
        "sourceCommit": commit,
        "selectionPolicy": "candidate-pinned",
        "components": {"canonicalProductConvergence": {"stageId": "P15", "initialState": "WAITING", "legacySpatialFallback": False, "alphaLivePromoted": False}},
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False},
    }


def w3(status="PASS", runtime="runtime-1", renderer="renderer-1"):
    ready = status == "PASS"
    return {
        "schema": sut.W3_SCHEMA,
        "status": status,
        "rendererAuthority": status,
        "repoQualificationPolicy": "DETERMINISTIC_FAIL_CLOSED",
        "captureIdentity": {"worldSha256": "w" * 64, "authorityKey": "authority-1", "runtimeEpoch": runtime, "rendererEpoch": renderer},
        "blockingProofEdge": None if ready else "edge",
        "ownerAction": None if ready else "run sample",
        "canonicalProducerReadiness": {"schema": "wof-render-object-frame-v1", "rendererSource": {"proven": ready}, "nativeWidth": 384, "nativeHeight": 224, "ready": ready, "suppressed": not ready},
    }


def p16(runtime="runtime-1", renderer="renderer-1", state="HUD_INGEST_ACCEPTED", package="pkg-1"):
    return {
        "schema": sut.P16_SCHEMA,
        "version": 1,
        "generatedAtUtc": "2026-09-05T00:00:01Z",
        "packageVersion": package,
        "world": {"accepted": True, "sha256": "w" * 64, "pageTargetId": "page-1", "workerTargetId": "worker-1"},
        "runtime": {"epoch": runtime, "authorityKey": "authority-1", "rendererEpoch": renderer, "rendererAuthority": "renderer-authority-1"},
        "canonical": {"state": state, "reason": "READY"},
        "hudCanonicalStatus": {"state": "READY"},
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        "visibleProof": "NOT_PROVEN",
    }


def p18(runtime="runtime-1", renderer="renderer-1", state="CANONICAL_DRAW_ACKNOWLEDGED", package="pkg-1"):
    entries = [] if state != "CANONICAL_DRAW_ACKNOWLEDGED" else [{"sequence": 1, "kind": "enemy-target-label", "nativeX": 100, "nativeY": 50}]
    return {
        "schema": sut.DRAW_SCHEMA,
        "version": 1,
        "collectedAtUtc": "2026-09-05T00:00:02Z",
        "packageVersion": package,
        "evidenceState": state,
        "identity": {"worldSha256": "w" * 64, "pageTargetId": "page-1", "authorityKey": "authority-1", "runtimeEpoch": runtime, "rendererEpoch": renderer, "rendererAuthority": "renderer-authority-1"},
        "entries": entries,
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False},
        "visibleProof": "NOT_PROVEN",
    }


class FinalAcceptanceTests(unittest.TestCase):
    def _inputs(self, td: str, *, w3_value=None, p16_value=None, p18_value=None):
        root = Path(td)
        cpath = dump(root / sut.DEFAULT_CANDIDATE_REL, candidate())
        _ = cpath
        wpath = dump(root / "w3.json", w3_value) if w3_value is not None else None
        p16path = dump(root / "p16.json", p16_value) if p16_value is not None else root / "missing-p16.json"
        p18path = dump(root / "p18.json", p18_value) if p18_value is not None else root / "missing-p18.json"
        return sut.collect_inputs(repo_root=root, candidate_path=None, w3_path=wpath, p16_path=p16path, p18_path=p18path)

    def test_pass_ready_draw_reaches_visual_confirmation_only(self):
        with tempfile.TemporaryDirectory() as td:
            inputs = self._inputs(td, w3_value=w3(), p16_value=p16(), p18_value=p18())
            bundle = sut.build_bundle(inputs, generated_at_utc="2026-09-05T00:00:03Z")
            self.assertEqual(bundle["automaticDecision"], sut.READY_FOR_OWNER_VISUAL_CONFIRMATION)
            self.assertEqual(bundle["visibleProof"], "NOT_PROVEN")
            self.assertTrue(bundle["ownerVisualConfirmationRequired"])

    def test_w3_inconclusive_never_advances(self):
        with tempfile.TemporaryDirectory() as td:
            inputs = self._inputs(td, w3_value=w3("INCONCLUSIVE"), p16_value=p16(), p18_value=p18())
            self.assertEqual(sut.decide(inputs)[0], sut.W3_INCONCLUSIVE)

    def test_mixed_renderer_or_runtime_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            inputs = self._inputs(td, w3_value=w3(), p16_value=p16(renderer="renderer-2"), p18_value=p18())
            state, reasons = sut.decide(inputs)
            self.assertEqual(state, sut.FAILED_EVIDENCE_MISMATCH)
            self.assertTrue(any("rendererEpoch mismatch" in reason for reason in reasons))

    def test_missing_p18_waits_without_downgrading_w3_p16(self):
        with tempfile.TemporaryDirectory() as td:
            inputs = self._inputs(td, w3_value=w3(), p16_value=p16(), p18_value=None)
            self.assertEqual(sut.decide(inputs)[0], sut.WAITING_DRAW_EVIDENCE)

    def test_bundle_write_read_is_deterministic_for_fixed_timestamp(self):
        with tempfile.TemporaryDirectory() as td:
            inputs = self._inputs(td, w3_value=w3(), p16_value=p16(), p18_value=p18())
            bundle = sut.build_bundle(inputs, generated_at_utc="2026-09-05T00:00:03Z")
            out = Path(td) / "out"
            j1, m1 = sut.write_bundle(bundle, out)
            first_json = j1.read_bytes()
            first_md = m1.read_bytes()
            j2, m2 = sut.write_bundle(bundle, out)
            self.assertEqual(first_json, j2.read_bytes())
            self.assertEqual(first_md, m2.read_bytes())

    def test_wrapper_is_one_command_without_devtools_or_json_editing(self):
        wrapper = (Path(__file__).with_name("WOF_ALPHA_FINAL_ACCEPTANCE.cmd")).read_text(encoding="utf-8")
        self.assertIn("final_acceptance_orchestrator.py", wrapper)
        self.assertIn("--invoke-w3", wrapper)
        self.assertNotIn("DevTools", wrapper)
        self.assertNotIn("json edit", wrapper.lower())


if __name__ == "__main__":
    unittest.main()
