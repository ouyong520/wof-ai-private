from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.fixed_draw_runtime_gate import (
    FIXED_DRAW_STATUS_FILE,
    FixedDrawRuntimeGate,
    _GAME_CANVAS_CONTEXT_EXPR,
    fixed_draw_gate_enabled,
)
from wof_launcher.production_p1_overlay import FIXED_SMOKE_STATES


def _probe_state(
    state: str,
    *,
    draws: int = 0,
    callbacks: int = 0,
    hooked: bool = False,
    buffer: dict | None = None,
) -> dict:
    drawn = state == "FIXED_TEST_ACTUALLY_DRAWN"
    return {
        "state": state,
        "enabled": state != "DISABLED",
        "hudInjected": drawn or state in {"DRAW_HOOK_NOT_FIRING", "DRAWING_BUFFER_INVALID", "DRAW_FAILED"},
        "gameCanvasContextPresent": state not in {"DISABLED", "HUD_INJECTION_MISSING", "GAME_CANVAS_CONTEXT_MISSING"},
        "drawHooked": hooked,
        "drawCount": draws,
        "callbackCount": callbacks,
        "drawingBuffer": buffer,
        "nativeWidth": 384,
        "nativeHeight": 224,
        "nativeX": 192,
        "nativeY": 112,
        "label": "TEST",
        "lastError": None,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


class _ScanSession:
    def __init__(self) -> None:
        self.requests: list[str] = []
        self.scripts: list[str] = []
        self.closed = False

    def request(self, method: str, *args, **kwargs):
        self.requests.append(method)
        return {}

    def evaluate(self, script: str, timeout: float = 0.0):
        self.scripts.append(script)
        return {
            "canvas": True,
            "context": True,
            "href": "https://example.invalid/wof",
            "title": "WOF",
        }

    def close(self) -> None:
        self.closed = True


class _Client:
    def __init__(self, session: _ScanSession) -> None:
        self.session = session

    def request(self, method: str, *args, **kwargs):
        if method != "Target.getTargets":
            raise AssertionError(method)
        return {
            "targetInfos": [
                {
                    "targetId": "page-1",
                    "type": "page",
                    "url": "https://example.invalid/wof",
                    "title": "WOF",
                }
            ]
        }

    def attach(self, target_id: str):
        if target_id != "page-1":
            raise AssertionError(target_id)
        return self.session


class _Probe:
    def __init__(self) -> None:
        self.enable_calls: list[tuple[object, str, str]] = []
        self.poll_calls = 0
        self.disposed = False

    def enable(self, client, target_id: str, runtime_epoch: str):
        self.enable_calls.append((client, target_id, runtime_epoch))
        return _probe_state(
            "DRAW_HOOK_NOT_FIRING",
            draws=0,
            callbacks=1,
            hooked=True,
            buffer={"width": 768, "height": 448},
        )

    def poll(self):
        self.poll_calls += 1
        return _probe_state(
            "FIXED_TEST_ACTUALLY_DRAWN",
            draws=1,
            callbacks=2,
            hooked=True,
            buffer={"width": 768, "height": 448},
        )

    def dispose(self) -> None:
        self.disposed = True


class AlphaP1RuntimeFixedTestGateTests(unittest.TestCase):
    def test_gate_flag_is_exact_opt_in_and_off_path_stays_off(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(fixed_draw_gate_enabled())
        with patch.dict(os.environ, {"WOF_ALPHA_FIXED_DRAW_SMOKE": "0"}, clear=True):
            self.assertFalse(fixed_draw_gate_enabled())
        with patch.dict(os.environ, {"WOF_ALPHA_FIXED_DRAW_SMOKE": "1"}, clear=True):
            self.assertTrue(fixed_draw_gate_enabled())

        source = (PYLAUNCH / "render_authority_measurement_entry.py").read_text(encoding="utf-8")
        gate_branch = source.index("if fixed_draw_gate_enabled():")
        gate_call = source.index("run_fixed_draw_runtime_gate(", gate_branch)
        normal_runner = source.index("runner = _load_runner(root)", gate_branch)
        self.assertLess(gate_branch, gate_call)
        self.assertLess(gate_call, normal_runner)

    def test_game_canvas_scan_has_no_p1_semantic_click_or_projection_dependency(self):
        lower = _GAME_CANVAS_CONTEXT_EXPR.lower()
        for forbidden in ("p1", "semantic", "click", "screenshot", "enemy", "projection", "camera"):
            self.assertNotIn(forbidden, lower)

        session = _ScanSession()
        target, first_page = FixedDrawRuntimeGate.find_game_canvas_target(_Client(session))
        self.assertEqual("page-1", target["targetId"])
        self.assertEqual("page-1", first_page["targetId"])
        self.assertEqual(["Runtime.enable"], session.requests)
        self.assertTrue(session.closed)

    def test_gate_reaches_existing_fixed_smoke_probe_without_p1_prerequisites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            out = Path(tmp) / "Documents" / "WOF_RESULTS"
            root.mkdir(parents=True)
            probe = _Probe()
            gate = FixedDrawRuntimeGate(
                root,
                out,
                acceptance_sha="a" * 40,
                smoke_factory=lambda _verified: probe,
            )
            stop = threading.Event()
            callbacks: list[tuple[str, dict]] = []

            def status_callback(state: str, payload: dict) -> None:
                callbacks.append((state, payload))
                if state == "RUNNING":
                    stop.set()

            session = _ScanSession()
            code = gate.run_connected(
                _Client(session),
                stop,
                status_callback=status_callback,
                poll_interval=0.001,
            )
            self.assertEqual(0, code)
            self.assertEqual(1, len(probe.enable_calls))
            self.assertEqual("page-1", probe.enable_calls[0][1])
            self.assertEqual(gate.runtime_epoch, probe.enable_calls[0][2])
            self.assertTrue(any(state == "RUNNING" for state, _ in callbacks))
            self.assertTrue((out / FIXED_DRAW_STATUS_FILE).is_file())

    def test_status_artifact_preserves_all_fail_closed_states_and_never_false_greens(self):
        required = {
            "HUD_INJECTION_MISSING",
            "GAME_CANVAS_CONTEXT_MISSING",
            "DRAW_HOOK_NOT_FIRING",
            "DRAWING_BUFFER_INVALID",
            "DRAW_FAILED",
            "FIXED_TEST_ACTUALLY_DRAWN",
            "DISABLED",
        }
        self.assertTrue(required.issubset(FIXED_SMOKE_STATES))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            out = Path(tmp) / "Documents" / "WOF_RESULTS"
            root.mkdir(parents=True)
            gate = FixedDrawRuntimeGate(
                root,
                out,
                acceptance_sha="b" * 40,
                smoke_factory=lambda _verified: _Probe(),
            )

            for state in sorted(required - {"FIXED_TEST_ACTUALLY_DRAWN"}):
                payload = gate.record_probe_status(_probe_state(state))
                self.assertEqual(state, payload["fixedSmokeState"])
                self.assertFalse(payload["drawSuccess"])

            false_green = gate.record_probe_status(
                _probe_state(
                    "FIXED_TEST_ACTUALLY_DRAWN",
                    draws=0,
                    callbacks=1,
                    hooked=True,
                    buffer={"width": 768, "height": 448},
                )
            )
            self.assertFalse(false_green["drawSuccess"])

            invalid_buffer = gate.record_probe_status(
                _probe_state(
                    "FIXED_TEST_ACTUALLY_DRAWN",
                    draws=1,
                    callbacks=1,
                    hooked=True,
                    buffer={"width": 0, "height": 448},
                )
            )
            self.assertFalse(invalid_buffer["drawSuccess"])

            success = gate.record_probe_status(
                _probe_state(
                    "FIXED_TEST_ACTUALLY_DRAWN",
                    draws=2,
                    callbacks=3,
                    hooked=True,
                    buffer={"width": 768, "height": 448},
                ),
                {"targetId": "page-1", "url": "https://example.invalid/wof", "title": "WOF"},
            )
            self.assertTrue(success["drawSuccess"])
            self.assertEqual("b" * 40, success["releaseSha"])
            self.assertEqual(gate.runtime_epoch, success["runtimeEpoch"])
            self.assertEqual(2, success["drawCount"])
            self.assertEqual(3, success["callbackCount"])
            self.assertEqual({"width": 768, "height": 448}, success["drawingBuffer"])
            self.assertEqual(384, success["nativeWidth"])
            self.assertEqual(224, success["nativeHeight"])
            self.assertEqual(192, success["nativeX"])
            self.assertEqual(112, success["nativeY"])
            self.assertEqual("TEST", success["label"])
            self.assertTrue(success["readOnly"])
            self.assertEqual(0, success["ramWrites"])
            self.assertFalse(success["inputInjection"])

            persisted = json.loads((out / FIXED_DRAW_STATUS_FILE).read_text(encoding="utf-8"))
            self.assertEqual(success, persisted)


if __name__ == "__main__":
    unittest.main()
