from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.auto_baseline_hud import (
    ADAPTER_SOURCE,
    CLASSIFICATION,
    P37_SOURCE,
    P37_TESTED_COMMIT,
    VISIBLE_SOURCE,
    AutoBaselineHud,
    AutoBaselineHudError,
)
from wof_launcher.production_p1_overlay import HUD_SOURCES


def valid_status(enabled: bool = True, **overrides):
    out = {
        "schema": "wof-alpha-auto-baseline-visible-hud-v1",
        "classification": CLASSIFICATION,
        "p37TestedCommit": P37_TESTED_COMMIT,
        "enabled": enabled,
        "state": "READY" if enabled else "DISABLED",
        "zeroClick": True,
        "manualAvatarClickRequired": False,
        "manualPortraitSeedRequired": False,
        "manualSeedRequired": False,
        "manualPlayerSelectionRequired": False,
        "automaticPlayers": ["P1", "P2", "P3"],
        "automaticReacquire": True,
        "nativeWidth": 384,
        "nativeHeight": 224,
        "nativeYAxis": "TOP_LEFT_POSITIVE_DOWN",
        "viewportYInversion": False,
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
        "visiblePlayers": ["P1", "P2", "P3"] if enabled else [],
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
    }
    out.update(overrides)
    return out


class FakeSession:
    def __init__(self, install_status=None):
        self.closed = False
        self.requests = []
        self.expressions = []
        self.install_status = install_status or valid_status(True)

    def request(self, method: str):
        self.requests.append(method)
        return {}

    def evaluate(self, expression: str, **_kwargs):
        self.expressions.append(expression)
        if expression.startswith("!!(window.WOFALPHAHUD"):
            return True
        if "WOFAutoBaselineVisibleHUDP39" in expression and ".install()" in expression:
            return dict(self.install_status)
        if "h.disable('STAGING_GATE_CLOSED')" in expression:
            return valid_status(False)
        if "h.ingestFrame(" in expression:
            return valid_status(True, visiblePlayers=["P1", "P2", "P3"])
        if "const h=window.WOFALPHAAUTOBASELINEHUD" in expression:
            return valid_status(True)
        return True

    def close(self):
        self.closed = True


class FakeClient:
    def __init__(self, session: FakeSession):
        self.session = session
        self.target = None

    def attach(self, target: str):
        self.target = target
        return self.session


class AlphaP39AutoBaselineHudTests(unittest.TestCase):
    def test_explicit_staging_bind_injects_only_p37_p39_sources(self):
        requested = []
        session = FakeSession()
        bridge = AutoBaselineHud(lambda rel: requested.append(rel) or f"/* {rel} */")
        status = bridge.bind(FakeClient(session), "page-1")
        self.assertEqual(requested, [P37_SOURCE, ADAPTER_SOURCE, VISIBLE_SOURCE])
        self.assertEqual(session.requests, ["Runtime.enable"])
        self.assertEqual(status["classification"], CLASSIFICATION)
        self.assertTrue(status["zeroClick"])
        self.assertEqual(status["automaticPlayers"], ["P1", "P2", "P3"])
        self.assertIsNone(status["rendererSourceProof"])
        self.assertFalse(status["promotionEligibility"])
        self.assertEqual(status["productAuthority"], "NONE_DIAGNOSTIC_ONLY")
        for source in (P37_SOURCE, ADAPTER_SOURCE, VISIBLE_SOURCE):
            self.assertNotIn(source, HUD_SOURCES, "production HUD injection list must remain independent of diagnostic staging")
        bridge.dispose()
        self.assertTrue(session.closed)

    def test_ingest_and_disable_require_no_manual_seed_or_click(self):
        session = FakeSession()
        bridge = AutoBaselineHud(lambda rel: f"/* {rel} */")
        bridge.bind(FakeClient(session), "page-1")
        status = bridge.ingest_frame({"width": 384, "height": 224, "data": [0, 0, 0, 0]}, 10.0)
        self.assertEqual(status["visiblePlayers"], ["P1", "P2", "P3"])
        status = bridge.disable()
        self.assertFalse(status["enabled"])
        joined = "\n".join(session.expressions).lower()
        self.assertNotIn(".click(", joined)
        self.assertNotIn("showmarker", joined)
        self.assertNotIn("manual seed", joined)
        bridge.dispose()

    def test_authority_impersonation_fails_closed(self):
        bad = valid_status(True, rendererSourceProof={"forged": True})
        session = FakeSession(bad)
        bridge = AutoBaselineHud(lambda rel: f"/* {rel} */")
        with self.assertRaisesRegex(AutoBaselineHudError, "authority boundary"):
            bridge.bind(FakeClient(session), "page-1")
        self.assertTrue(session.closed)

    def test_safety_or_coordinate_mismatch_fails_closed(self):
        for bad in (
            valid_status(True, viewportYInversion=True),
            valid_status(True, safety={"readOnly": True, "ramWrites": 1, "inputInjection": False}),
        ):
            with self.subTest(bad=bad):
                session = FakeSession(bad)
                bridge = AutoBaselineHud(lambda rel: f"/* {rel} */")
                with self.assertRaises(AutoBaselineHudError):
                    bridge.bind(FakeClient(session), "page-1")
                self.assertTrue(session.closed)


if __name__ == "__main__":
    unittest.main()
