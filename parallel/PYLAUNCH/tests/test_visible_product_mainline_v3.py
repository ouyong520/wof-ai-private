from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from wof_launcher.production_p1_overlay import ProductionP1Overlay, SCHEMA as OVERLAY_SCHEMA


AUTHORITY = "authority"
EPOCH = "a" * 32
SURFACE = {"width": 320, "height": 200, "layoutKey": "L"}


class FakeHudSession:
    def __init__(self) -> None:
        self.visible = False
        self.draw_count = 0
        self.calls: list[str] = []

    def evaluate(self, expression: str, timeout: float = 0):
        self.calls.append(expression)
        if "setP1HeadTracker" in expression:
            self.visible = True
            self.draw_count += 1
        elif "clearP1HeadTracker" in expression:
            self.visible = False
        return {
            "schema": OVERLAY_SCHEMA,
            "authorityKey": AUTHORITY,
            "runtimeEpoch": EPOCH,
            "productionOverlayEnabled": True,
            "visible": self.visible,
            "drawCount": self.draw_count,
            "drawHooked": True,
            "hudVersion": "wof-alpha-hud-rc5",
            "hudSource": "product/alpha/wof_alpha_hud.js",
            "tracker": {"visible": self.visible, "drawCount": self.draw_count},
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }


class VisibleProductMainlineV3Tests(unittest.TestCase):
    @staticmethod
    def repo_root() -> Path:
        return Path(__file__).resolve().parents[3]

    def adapter(self) -> tuple[ProductionP1Overlay, FakeHudSession]:
        overlay = ProductionP1Overlay(lambda _rel: "")
        session = FakeHudSession()
        overlay._session = session
        overlay._authority_key = AUTHORITY
        overlay._runtime_epoch = EPOCH
        overlay._install_mode = "TEST_MAINTAINED_HUD"
        return overlay, session

    def test_zero_click_and_one_click_seed_sources_reach_same_production_sink(self):
        for seed_source in ("W2_SEMANTIC_IDENTITY_SAFE_UNIQUE", "OWNER_FALLBACK_CLICK"):
            overlay, session = self.adapter()
            shown = overlay.update(
                {"state": "HEAD_TRACKING", "lostFrames": 0, "center": [160.0, 100.0], "seedSource": seed_source},
                dict(SURFACE),
                (320, 200),
            )
            self.assertTrue(shown["visible"])
            self.assertTrue(overlay.visible_and_drawn())
            self.assertTrue(any("setP1HeadTracker" in call for call in session.calls))

    def test_loss_hides_and_recovery_reappears_without_second_product_path(self):
        overlay, session = self.adapter()
        tracked = {"state": "HEAD_TRACKING", "lostFrames": 0, "center": [150.0, 92.0], "seedSource": "OWNER_FALLBACK_CLICK"}
        self.assertTrue(overlay.update(tracked, dict(SURFACE), (320, 200))["visible"])
        lost = overlay.update({**tracked, "state": "HEAD_ACQUIRING", "lostFrames": 1}, dict(SURFACE), (320, 200))
        self.assertFalse(lost["visible"])
        recovered = overlay.update({**tracked, "center": [155.0, 94.0]}, dict(SURFACE), (320, 200))
        self.assertTrue(recovered["visible"])
        self.assertGreaterEqual(recovered["drawCount"], 2)
        self.assertTrue(any("clearP1HeadTracker" in call for call in session.calls))

    def test_selected_runtime_reuses_maintained_alpha_hud_not_forked_hud(self):
        root = self.repo_root()
        runner = (root / "parallel/RENDER_AUTHORITY_V3/measurement_runner.py").read_text(encoding="utf-8")
        adapter = (root / "parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py").read_text(encoding="utf-8")
        hud = (root / "product/alpha/wof_alpha_hud.js").read_text(encoding="utf-8")
        self.assertIn('PRODUCTION_OVERLAY_SOURCE="product/alpha/wof_alpha_hud.js"', runner)
        self.assertIn('"productionOverlayEnabled":True', runner)
        self.assertIn('"productionOverlaySuppressed":False', runner)
        self.assertIn("ProductionP1Overlay", runner)
        self.assertIn('SOURCE = "product/alpha/wof_alpha_hud.js"', adapter)
        self.assertIn("bindP1HeadTrackerAuthority", hud)
        self.assertIn("setP1HeadTracker", hud)
        self.assertIn("clearP1HeadTracker", hud)
        self.assertIn("drawP1Tracker", hud)
        self.assertIn("label:'1P'", hud)
        self.assertFalse((root / "product/alpha/wof_alpha_p1_tracker_overlay.js").exists())

    def test_white_acquisition_marker_is_suppressed_when_product_label_is_driven(self):
        hud = (self.repo_root() / "product/alpha/wof_alpha_hud.js").read_text(encoding="utf-8")
        self.assertIn("WOFHEADVISUALV3?.showMarker?.(0,0,false)", hud)
        self.assertIn("P1_TRACKER_STALE_MS", hud)
        self.assertIn("p1TrackerStatus", hud)

    def test_no_manual_projection_or_input_authority_reintroduced(self):
        root = self.repo_root()
        runner = (root / "parallel/RENDER_AUTHORITY_V3/measurement_runner.py").read_text(encoding="utf-8")
        adapter = (root / "parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py").read_text(encoding="utf-8")
        self.assertIn('"manualCalibration":False', runner)
        self.assertIn('"legacyProjectionSelected":False', runner)
        self.assertIn('"readOnly":True', runner)
        self.assertIn('"ramWrites":0', runner)
        self.assertIn('"inputInjection":False', runner)
        self.assertNotIn("WOFOWNERPROJECTION", adapter)
        self.assertNotIn("Input.dispatch", adapter)


if __name__ == "__main__":
    unittest.main()
