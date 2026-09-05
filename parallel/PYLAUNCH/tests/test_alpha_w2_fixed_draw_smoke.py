from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.production_p1_overlay import (
    FIXED_SMOKE_SCHEMA,
    FIXED_SMOKE_STATES,
    ProductionHudFixedDrawSmoke,
)


class _Session:
    def __init__(self, replies):
        self.replies = list(replies)
        self.scripts: list[str] = []
        self.requests: list[str] = []
        self.closed = False

    def request(self, method: str, *args, **kwargs):
        self.requests.append(method)
        return {}

    def evaluate(self, script: str, timeout: float = 0.0):
        self.scripts.append(script)
        if self.replies:
            reply = self.replies.pop(0)
            if isinstance(reply, BaseException):
                raise reply
            return reply
        return None

    def close(self):
        self.closed = True


class _Client:
    def __init__(self, session: _Session):
        self.session = session
        self.targets: list[str] = []

    def attach(self, page_target_id: str):
        self.targets.append(page_target_id)
        return self.session


def _remote(state: str, *, draws: int = 0, callbacks: int = 0, hooked: bool = True):
    return {
        "schema": "wof-alpha-fixed-draw-smoke-v1",
        "enabled": True,
        "state": state,
        "hudInjected": True,
        "gameCanvasContextPresent": True,
        "drawHooked": hooked,
        "drawCount": draws,
        "callbackCount": callbacks,
        "nativeWidth": 384,
        "nativeHeight": 224,
        "nativeX": 192,
        "nativeY": 112,
        "drawingBuffer": {"width": 768, "height": 448},
        "lastError": None,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


class AlphaW2FixedDrawSmokeTests(unittest.TestCase):
    def test_machine_states_are_explicit_and_hud_absence_cannot_false_green(self):
        required = {
            "HUD_INJECTION_MISSING",
            "GAME_CANVAS_CONTEXT_MISSING",
            "DRAW_HOOK_NOT_FIRING",
            "DRAWING_BUFFER_INVALID",
            "FIXED_TEST_ACTUALLY_DRAWN",
        }
        self.assertTrue(required.issubset(FIXED_SMOKE_STATES))
        missing = ProductionHudFixedDrawSmoke._normalize(None)
        self.assertEqual(FIXED_SMOKE_SCHEMA, missing["schema"])
        self.assertEqual("HUD_INJECTION_MISSING", missing["state"])
        self.assertFalse(ProductionHudFixedDrawSmoke(lambda _rel: "").fixed_test_actually_drawn())

    def test_game_canvas_context_missing_is_reported_before_hud_injection(self):
        session = _Session([{"canvas": False, "context": False}])
        smoke = ProductionHudFixedDrawSmoke(lambda _rel: self.fail("HUD source must not load without game WebGL"))
        out = smoke.enable(_Client(session), "page", "runtime-epoch-123456789")
        self.assertEqual("GAME_CANVAS_CONTEXT_MISSING", out["state"])
        self.assertTrue(out["enabled"])
        self.assertFalse(out["hudInjected"])
        self.assertFalse(out["drawHooked"])
        self.assertEqual(["Runtime.enable"], session.requests)

    def test_draw_hook_requires_a_real_renderer_draw_before_success(self):
        session = _Session(
            [
                {"canvas": True, "context": True},
                True,
                _remote("DRAW_HOOK_NOT_FIRING", draws=0, callbacks=0, hooked=True),
                _remote("FIXED_TEST_ACTUALLY_DRAWN", draws=1, callbacks=1, hooked=True),
            ]
        )
        smoke = ProductionHudFixedDrawSmoke(lambda _rel: self.fail("existing maintained HUD should be reused"))
        first = smoke.enable(_Client(session), "page", "runtime-epoch-123456789")
        self.assertEqual("DRAW_HOOK_NOT_FIRING", first["state"])
        self.assertFalse(smoke.fixed_test_actually_drawn())
        drawn = smoke.poll()
        self.assertEqual("FIXED_TEST_ACTUALLY_DRAWN", drawn["state"])
        self.assertEqual(1, drawn["drawCount"])
        self.assertEqual(1, drawn["callbackCount"])
        self.assertTrue(smoke.fixed_test_actually_drawn())

    def test_hud_source_is_opt_in_fixed_native_and_uses_maintained_native_draw(self):
        root = HERE.parents[3]
        source = (root / "product" / "alpha" / "wof_alpha_hud.js").read_text(encoding="utf-8")
        self.assertIn("enabled:false,state:'DISABLED'", source)
        self.assertIn("FIXED_NATIVE_W=384,FIXED_NATIVE_H=224,FIXED_NATIVE_X=192,FIXED_NATIVE_Y=112", source)
        self.assertIn("function mapFixedNativeRectToDrawingBuffer(W,H)", source)
        self.assertIn("const sx=W/FIXED_NATIVE_W,sy=H/FIXED_NATIVE_H;", source)
        self.assertIn("bridge.nativeDraw.call(gl,gl.TRIANGLES,0,6);drawCount++;return true;", source)
        self.assertIn("if(fixedSmoke.enabled)drawFixedSmoke();\n  if(!visible)return;", source)
        self.assertIn("fixedSmoke.drawCount++;", source)
        self.assertNotIn("appendChild(fixedSmokeHud)", source)

        start = source.index("function drawFixedSmoke(){")
        end = source.index("function paintLabelAtlas(){", start)
        body = source[start:end]
        for forbidden in ("p1Tracker", "lastMarkerMsg", "lastPlayerMsg", "projection", "screenshot", "semantic"):
            self.assertNotIn(forbidden, body)
        native_draw = body.index("drawTexture(")
        proof_increment = body.index("fixedSmoke.drawCount++")
        self.assertLess(native_draw, proof_increment)

    def test_disabled_smoke_does_not_change_normal_visibility_gate(self):
        root = HERE.parents[3]
        source = (root / "product" / "alpha" / "wof_alpha_hud.js").read_text(encoding="utf-8")
        self.assertIn("function setFixedDrawSmokeEnabled(enabled)", source)
        self.assertIn("if(!fixedSmoke.enabled)return fixedSmokeSet('DISABLED'", source)
        self.assertIn("callbackCount++;\n  if(disposed)return;\n  if(fixedSmoke.enabled)drawFixedSmoke();\n  if(!visible)return;", source)


if __name__ == "__main__":
    unittest.main()
