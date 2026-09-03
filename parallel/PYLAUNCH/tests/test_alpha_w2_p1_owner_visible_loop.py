from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.production_p1_overlay import ProductionP1Overlay, SCHEMA, SOURCE
from wof_launcher.render_measurement_ui import MeasurementTrayApp


def _remote(*, visible: bool, draw_count: int) -> dict:
    return {
        "schema": SCHEMA,
        "authorityKey": "authority",
        "runtimeEpoch": "epoch",
        "productionOverlayEnabled": True,
        "visible": visible,
        "drawCount": draw_count,
        "drawHooked": True,
        "hudVersion": "fixture",
        "hudSource": SOURCE,
        "tracker": {},
        "relativeEnemy": None,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


class _Session:
    def __init__(self, replies: list[dict]) -> None:
        self.replies = list(replies)
        self.scripts: list[str] = []

    def evaluate(self, script: str, timeout: float = 0.0):
        self.scripts.append(script)
        if self.replies:
            return self.replies.pop(0)
        return None


def _snap(state: str, *, visual: dict | None = None, overlay: dict | None = None):
    measurement = {
        "measurementState": state,
        "visual": visual or {},
        "productionOverlay": overlay or {},
    }
    return SimpleNamespace(state=state, alpha_status={"renderAuthorityV3": measurement})


class AlphaW2P1OwnerVisibleLoopTests(unittest.TestCase):
    def test_current_visibility_generation_requires_a_new_maintained_hud_draw(self):
        overlay = ProductionP1Overlay(lambda _rel: "")
        overlay._session = _Session(
            [
                _remote(visible=True, draw_count=7),
                _remote(visible=True, draw_count=8),
                _remote(visible=False, draw_count=8),
                _remote(visible=True, draw_count=8),
                _remote(visible=True, draw_count=9),
            ]
        )
        overlay._authority_key = "authority"
        overlay._runtime_epoch = "epoch"
        overlay._last = _remote(visible=False, draw_count=7)
        overlay._draw_baseline = 7
        overlay._diagnostic_marker_suppressed = True

        visual = {"center": [100, 50], "state": "HEAD_TRACKING", "lostFrames": 0, "seedSource": "semantic"}
        layout = {"width": 384, "height": 224}

        self.assertFalse(overlay.update(visual, layout, (384, 224))["drawnCurrentTracker"])
        self.assertFalse(overlay.visible_and_drawn())

        self.assertTrue(overlay.update(visual, layout, (384, 224))["drawnCurrentTracker"])
        self.assertTrue(overlay.visible_and_drawn())

        lost = {**visual, "lostFrames": 1}
        self.assertFalse(overlay.update(lost, layout, (384, 224))["visible"])
        self.assertFalse(overlay.visible_and_drawn())

        self.assertFalse(overlay.update(visual, layout, (384, 224))["drawnCurrentTracker"])
        self.assertFalse(overlay.visible_and_drawn())

        self.assertTrue(overlay.update(visual, layout, (384, 224))["drawnCurrentTracker"])
        self.assertTrue(overlay.visible_and_drawn())

    def test_diagnostic_marker_is_forced_hidden_and_is_part_of_success_gate(self):
        overlay = ProductionP1Overlay(lambda _rel: "")
        session = _Session([True])
        overlay._session = session
        self.assertTrue(overlay._suppress_diagnostic_marker())
        self.assertIn("showMarker=function", session.scripts[0])
        self.assertIn("original(x,y,false)", session.scripts[0])

        proof = {
            "visible": True,
            "drawCount": 2,
            "drawHooked": True,
            "drawnCurrentTracker": True,
            "diagnosticMarkerSuppressed": False,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }
        overlay._last = proof
        self.assertFalse(overlay.visible_and_drawn())

    def test_owner_statuses_are_exact_and_stale_draw_cannot_claim_visible(self):
        proof = {
            "visible": True,
            "drawCount": 4,
            "drawHooked": True,
            "drawnCurrentTracker": True,
            "diagnosticMarkerSuppressed": True,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }
        stale = {**proof, "drawnCurrentTracker": False}

        self.assertEqual("等待 WOF", MeasurementTrayApp._owner_product_state(_snap("WAITING_FOR_WOF")))
        self.assertEqual("正在自动找 P1", MeasurementTrayApp._owner_product_state(_snap("HEAD_ACQUIRING")))
        self.assertEqual("需要一次点击 P1 真实头部", MeasurementTrayApp._owner_product_state(_snap("ONE_CLICK_REQUIRED")))
        self.assertEqual("正在自动找 P1", MeasurementTrayApp._owner_product_state(_snap("MEASURING", overlay=stale)))
        self.assertEqual("头顶已显示", MeasurementTrayApp._owner_product_state(_snap("MEASURING", overlay=proof)))
        self.assertEqual(
            "暂时丢失，恢复中",
            MeasurementTrayApp._owner_product_state(_snap("MEASURING", visual={"lostFrames": 1}, overlay=proof)),
        )
        self.assertEqual("BLOCKED", MeasurementTrayApp._owner_product_state(_snap("BLOCKED")))


if __name__ == "__main__":
    unittest.main()
