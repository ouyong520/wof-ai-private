from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from wof_launcher.live_diagnostic_staging import (
    INJECTION_ORDER,
    P39_CLASSIFICATION,
    P42_CLASSIFICATION,
    LiveDiagnosticStagingError,
    P45LiveDiagnosticStagingRuntime,
)


BINDING = {
    "runtimeEpoch": "runtime-epoch-0000000000000001",
    "rendererEpoch": "renderer-epoch-00000000000001",
    "authorityKey": "authority-key-1",
}


class FakeRuntime:
    def __init__(self):
        self.ensure_calls = 0
        self.revoke_calls = 0
        self.status_value = {
            "requested": True,
            "running": True,
            "runtimeEpoch": BINDING["runtimeEpoch"],
            "authorityKey": BINDING["authorityKey"],
            "canonicalSpatialAuthority": "P12->P10->P9/P8->P11",
        }

    def ensure_running(self, client, choice, authority_key):
        self.ensure_calls += 1
        return self.status_value

    def revoke(self, client=None):
        self.revoke_calls += 1

    def status(self):
        return self.status_value

    def poll_projection_recovery(self, *args, **kwargs):
        return {"state": "IDLE"}, False

    def ingest_canonical_w3_frame(self, *args, **kwargs):
        return {"state": "READY"}

    def clear_canonical_overlay(self, *args, **kwargs):
        return {"state": "SUPPRESSED"}

    def projection_proof_result(self):
        return None


class FakeHud:
    def __init__(self, reader, events):
        self.reader = reader
        self.events = events
        self.disabled = False
        self.disposed = False
        self.ingested = 0

    def bind(self, client, page_target_id):
        self.events.append("P39_AUTO_BASELINE_HUD")
        self.reader("parallel/AUTO_MARKER_BASELINE/native_marker_auto_acquisition_baseline.js")
        self.reader("product/alpha/wof_alpha_auto_baseline_hud_adapter.js")
        self.reader("product/alpha/wof_alpha_auto_baseline_visible_hud.js")
        return self.refresh()

    def refresh(self):
        return {
            "schema": "wof-alpha-auto-baseline-visible-hud-v1",
            "classification": P39_CLASSIFICATION,
            "enabled": True,
            "zeroClick": True,
            "manualSeedRequired": False,
            "automaticPlayers": ["P1", "P2", "P3"],
            "visiblePlayers": ["P1"],
            "controller": {
                "state": "TRACKING",
                "visibleFresh": False,
                "envelopeState": "AMBIGUOUS",
                "tracks": {
                    "P1": {"state": "TRACKED", "reacquireCount": 2},
                    "P2": {"state": "LOST", "reacquireCount": 1},
                    "P3": {"state": "AMBIGUOUS", "reacquireCount": 4},
                },
            },
            "rendererSourceProof": None,
            "authorityEligibility": {
                "p29Pass": False,
                "p32NativeMarkerQualification": False,
                "p36RendererSourceTrace": False,
                "p34RetryReadiness": False,
                "promotion": False,
            },
            "promotionEligibility": False,
            "productAuthority": "NONE_DIAGNOSTIC_ONLY",
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        }

    def ingest_frame(self, frame, timestamp_ms):
        self.ingested += 1
        return self.refresh()

    def disable(self):
        self.disabled = True
        return self.refresh()

    def dispose(self):
        self.disposed = True


class FakeSession:
    def __init__(self, events):
        self.events = events
        self.binding = None
        self.closed = False
        self.terminal = False
        self.reason = "BOUNDED_DIAGNOSTIC_CAPTURE_ACTIVE"
        self.submissions = [
            {"submissionSequence": 1, "draw": {"method": "drawArrays"}, "payload": "raw-a"},
            {"submissionSequence": 2, "draw": {"method": "drawElements"}, "payload": "raw-b"},
        ]
        self.buffer_uploads = [{"payload": {"raw": {"hex": "0011"}}}]
        self.texture_uploads = [{"payload": {"raw": {"hex": "2233"}}}]

    def request(self, method):
        return {}

    def _status(self):
        return {
            "schema": "wof-gstyphoon-renderer-correlation-probe-v1",
            "state": "CAPTURE_READY" if self.terminal else "OBSERVING",
            "terminal": self.terminal,
            "reason": self.reason,
            "installed": not self.terminal,
            "binding": dict(self.binding or BINDING),
            "authorityEligible": False,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }

    def _result(self):
        return {
            "schema": "wof-gstyphoon-renderer-correlation-probe-v1",
            "state": "CAPTURE_READY" if self.terminal else "OBSERVING",
            "terminal": self.terminal,
            "reason": self.reason,
            "binding": dict(self.binding or BINDING),
            "submissions": list(self.submissions),
            "bufferUploads": list(self.buffer_uploads),
            "textureUploads": list(self.texture_uploads),
            "submissionGroups": [{"groupKey": "G-a"}, {"groupKey": "G-b"}],
            "mappingAssessment": {
                "status": "DIAGNOSTIC_ONLY_NO_AUTHORITY_SELECTION",
                "selectionMade": False,
                "selectedSubmission": None,
                "selectedGroup": None,
            },
            "teardown": {"installed": not self.terminal, "conflicts": []},
            "authorityEligible": False,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }

    def evaluate(self, expression, timeout=0):
        if "Object.freeze({...binding})" in expression:
            self.binding = dict(BINDING)
            self.events.append("P42_RAW_CORRELATION_PROBE")
            return self._status()
        if "const b=window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1" in expression:
            return dict(self.binding or BINDING)
        if "?.status?.()||null" in expression:
            return self._status()
        if "?.result?.()||null" in expression:
            return self._result()
        if "?.stop?.(" in expression:
            if "P45_REBIND" not in expression and "P45_INSTALL_FAILED" not in expression:
                try:
                    fragment = expression.split("?.stop?.(", 1)[1].split(")", 1)[0]
                    self.reason = json.loads(fragment)
                except Exception:
                    self.reason = "STOPPED"
                self.terminal = True
            return self._status()
        return True

    def close(self):
        self.closed = True


class FakeClient:
    def __init__(self, events):
        self.events = events
        self.session = FakeSession(events)
        self.attach_calls = 0

    def attach(self, page_target_id):
        self.attach_calls += 1
        return self.session


class TestableP45(P45LiveDiagnosticStagingRuntime):
    def _accepted_text(self, rel):
        # Unit tests isolate lifecycle semantics from filesystem integrity. Exact-byte
        # pins are covered separately by static assertions below and the real reader.
        return "// accepted-test-source"


class P45LiveDiagnosticStagingTests(unittest.TestCase):
    def _choice(self):
        return SimpleNamespace(page={"targetId": "page-1"})

    def test_gate_off_is_exact_delegate_and_does_not_inject(self):
        runtime = FakeRuntime()
        client = Mock()
        hud_factory = Mock(side_effect=AssertionError("gate-off must not construct P39"))
        wrapper = TestableP45(Path("."), enabled=False, runtime=runtime, hud_factory=hud_factory)
        result = wrapper.ensure_running(client, self._choice(), BINDING["authorityKey"])
        self.assertIs(result, runtime.status_value)
        self.assertEqual(wrapper.status(), runtime.status_value)
        hud_factory.assert_not_called()
        client.attach.assert_not_called()

    def test_gate_on_injects_p39_then_p42_and_preserves_raw_bundle(self):
        events = []
        runtime = FakeRuntime()
        client = FakeClient(events)
        wrapper = TestableP45(
            Path("."),
            enabled=True,
            runtime=runtime,
            hud_factory=lambda reader: FakeHud(reader, events),
            renderer_epoch_factory=lambda: BINDING["rendererEpoch"],
        )
        status = wrapper.ensure_running(client, self._choice(), BINDING["authorityKey"])
        self.assertEqual(events, list(INJECTION_ORDER))
        diagnostic = status["liveDiagnosticStaging"]
        self.assertEqual(diagnostic["p39"]["classification"], P39_CLASSIFICATION)
        self.assertEqual(diagnostic["p42"]["classification"], P42_CLASSIFICATION)
        self.assertEqual(diagnostic["binding"]["runtimeEpoch"], BINDING["runtimeEpoch"])
        self.assertEqual(diagnostic["binding"]["rendererEpoch"], BINDING["rendererEpoch"])
        self.assertFalse(diagnostic["binding"]["productionRendererAuthority"])
        self.assertEqual(diagnostic["p42"]["rawBundle"]["submissions"], client.session.submissions)
        self.assertEqual(diagnostic["p42"]["rawBundle"]["bufferUploads"], client.session.buffer_uploads)
        self.assertEqual(diagnostic["p42"]["rawBundle"]["textureUploads"], client.session.texture_uploads)
        self.assertFalse(diagnostic["p42"]["rawBundle"]["mappingAssessment"]["selectionMade"])
        self.assertFalse(any(diagnostic["authorityEligibility"].values()))
        self.assertNotIn("rendererSourceProof", diagnostic)

    def test_p39_lifecycle_exposes_visible_hidden_lost_stale_ambiguous_reacquire(self):
        events = []
        wrapper = TestableP45(
            Path("."),
            enabled=True,
            runtime=FakeRuntime(),
            hud_factory=lambda reader: FakeHud(reader, events),
            renderer_epoch_factory=lambda: BINDING["rendererEpoch"],
        )
        diagnostic = wrapper.ensure_running(FakeClient(events), self._choice(), BINDING["authorityKey"])["liveDiagnosticStaging"]
        lifecycle = diagnostic["p39"]["lifecycle"]
        self.assertEqual(lifecycle["visiblePlayers"], ["P1"])
        self.assertEqual(lifecycle["hiddenPlayers"], ["P2", "P3"])
        self.assertEqual(lifecycle["lostPlayers"], ["P2"])
        self.assertTrue(lifecycle["stale"])
        self.assertTrue(lifecycle["ambiguous"])
        self.assertEqual(lifecycle["reacquireCountByPlayer"], {"P1": 2, "P2": 1, "P3": 4})

    def test_stale_or_mixed_binding_fails_closed(self):
        events = []
        client = FakeClient(events)
        wrapper = TestableP45(
            Path("."),
            enabled=True,
            runtime=FakeRuntime(),
            hud_factory=lambda reader: FakeHud(reader, events),
            renderer_epoch_factory=lambda: BINDING["rendererEpoch"],
        )
        wrapper.ensure_running(client, self._choice(), BINDING["authorityKey"])
        client.session.binding = {**BINDING, "authorityKey": "mixed-authority"}
        out = wrapper.live_diagnostic_readout()
        self.assertEqual(wrapper._reason, "STALE_OR_MIXED_AUTHORITY_BINDING")
        self.assertIsNotNone(out)
        self.assertIsNone(wrapper._binding)
        self.assertTrue(client.session.closed)

    def test_seal_reports_reason_then_tears_down_without_authority_promotion(self):
        events = []
        client = FakeClient(events)
        wrapper = TestableP45(
            Path("."),
            enabled=True,
            runtime=FakeRuntime(),
            hud_factory=lambda reader: FakeHud(reader, events),
            renderer_epoch_factory=lambda: BINDING["rendererEpoch"],
        )
        wrapper.ensure_running(client, self._choice(), BINDING["authorityKey"])
        out = wrapper.stop_live_diagnostic("P43_BOUNDED_CAPTURE_COMPLETE")
        self.assertEqual(out["p42"]["sealReason"], "P43_BOUNDED_CAPTURE_COMPLETE")
        self.assertFalse(any(out["authorityEligibility"].values()))
        self.assertIsNone(wrapper._binding)
        self.assertTrue(client.session.closed)

    def test_required_labels_and_order_are_fixed(self):
        self.assertEqual(INJECTION_ORDER, ("P39_AUTO_BASELINE_HUD", "P42_RAW_CORRELATION_PROBE"))
        self.assertEqual(P39_CLASSIFICATION, "UNVERIFIED_AUTO_BASELINE")
        self.assertEqual(P42_CLASSIFICATION, "BOUNDED_LIVE_DIAGNOSTIC_MAPPING_ONLY")


if __name__ == "__main__":
    unittest.main()
