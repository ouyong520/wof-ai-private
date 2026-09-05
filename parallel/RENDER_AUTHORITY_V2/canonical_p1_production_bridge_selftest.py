from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = types.ModuleType("wof_launcher")
PKG.__path__ = [str(ROOT / "PYLAUNCH" / "wof_launcher")]
sys.modules["wof_launcher"] = PKG

probe = types.ModuleType("wof_launcher.probe")
probe.WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
sys.modules["wof_launcher.probe"] = probe

anchor_path = ROOT / "PYLAUNCH" / "wof_launcher" / "render_object_anchor.py"
anchor_spec = importlib.util.spec_from_file_location("wof_launcher.render_object_anchor", anchor_path)
anchor_module = importlib.util.module_from_spec(anchor_spec)
assert anchor_spec and anchor_spec.loader
sys.modules[anchor_spec.name] = anchor_module
anchor_spec.loader.exec_module(anchor_module)

production_stub = types.ModuleType("wof_launcher.production_p1_overlay")
production_stub.ProductionP1Overlay = object
sys.modules[production_stub.__name__] = production_stub

bridge_path = ROOT / "PYLAUNCH" / "wof_launcher" / "canonical_p1_production_bridge.py"
bridge_spec = importlib.util.spec_from_file_location("wof_launcher.canonical_p1_production_bridge", bridge_path)
bridge_module = importlib.util.module_from_spec(bridge_spec)
assert bridge_spec and bridge_spec.loader
sys.modules[bridge_spec.name] = bridge_module
bridge_spec.loader.exec_module(bridge_module)

AuthorityBinding = anchor_module.AuthorityBinding
CanonicalP1ProductionBridge = bridge_module.CanonicalP1ProductionBridge


class FakeOverlay:
    def __init__(self) -> None:
        self.calls = []
        self.fixed_draw_state = {"enabled": True, "drawCount": 9}
        self._status = {"visible": False, "drawCount": 0, "drawHooked": True}

    def bind(self, client, page_target_id, authority_key, runtime_epoch):
        self.calls.append(("bind", page_target_id, authority_key, runtime_epoch))
        return self.status()

    def update(self, visual, layout, frame_size, actor_snapshot=None):
        self.calls.append(("update", visual, layout, frame_size))
        visible = visual.get("state") == "HEAD_TRACKING" and int(visual.get("lostFrames") or 0) == 0 and isinstance(layout, dict)
        if visible:
            self._status = {"visible": True, "drawCount": self._status["drawCount"] + 1, "drawHooked": True}
        else:
            self._status = {"visible": False, "drawCount": self._status["drawCount"], "drawHooked": True}
        return self.status()

    def status(self):
        return dict(self._status)

    def dispose(self):
        self.calls.append(("dispose",))
        self._status["visible"] = False


def make_frame(*, renderer="fedcba9876543210", source=True, generation=7):
    return {
        "schema": "wof-render-object-frame-v1",
        "worldSha256": probe.WORLD_SHA256,
        "authorityKey": "authority",
        "runtimeEpoch": "0123456789abcdef",
        "rendererEpoch": renderer,
        "nativeWidth": 384,
        "nativeHeight": 224,
        "rendererSource": {"proven": source, "kind": "exact-cps1-buffered-object"},
        "actors": [
            {
                "actor": "P1",
                "generation": generation,
                "association": {"proven": True, "ambiguous": False, "candidateCount": 1},
                "parts": [
                    {"role": "body-tile", "bounds": {"left": 100, "top": 90, "right": 116, "bottom": 106}},
                    {"role": "body-tile", "bounds": {"left": 100, "top": 106, "right": 116, "bottom": 122}},
                ],
            }
        ],
    }


overlay = FakeOverlay()
binding = AuthorityBinding("authority", "0123456789abcdef", "fedcba9876543210")
bridge = CanonicalP1ProductionBridge(overlay=overlay)
bridge.bind(object(), "page", binding, generation=7)
assert bridge.status()["state"] == "SUPPRESSED"
assert bridge.status()["reason"] == "CANONICAL_WAITING_FOR_READY"

layout = {"width": 768, "height": 448}
ready = bridge.ingest_frame(make_frame(), layout=layout)
assert ready["state"] == "READY"
assert ready["anchor"] == {"x": 108.0, "y": 86.0, "nativeWidth": 384, "nativeHeight": 224}
last_update = [row for row in overlay.calls if row[0] == "update"][-1]
assert last_update[1]["center"] == [108.0, 86.0]
assert last_update[1]["seedSource"] == "wof-render-object-anchor-v1"
assert last_update[2] == layout
assert last_update[3] == (384, 224)

unproven = bridge.ingest_frame(make_frame(source=False), layout=layout)
assert unproven["state"] == "SUPPRESSED"
assert unproven["reason"] == "RENDERER_SOURCE_UNPROVEN"
assert overlay.status()["visible"] is False

bridge.ingest_frame(make_frame(), layout=layout)
stale = bridge.ingest_frame(make_frame(renderer="stale-renderer-00"), layout=layout)
assert stale["state"] == "SUPPRESSED"
assert stale["reason"] == "STALE_AUTHORITY_OR_RENDERER_EPOCH"
assert overlay.status()["visible"] is False

bridge.ingest_frame(make_frame(), layout=layout)
changed = bridge.set_generation(8)
assert changed["state"] == "SUPPRESSED"
assert changed["reason"] == "ACTOR_GENERATION_CHANGED"
assert overlay.status()["visible"] is False

missing_new_generation = bridge.ingest_frame(make_frame(generation=7), layout=layout)
assert missing_new_generation["state"] == "SUPPRESSED"
assert missing_new_generation["reason"] == "ACTOR_ASSOCIATION_MISSING"

bad_layout = bridge.ingest_frame(make_frame(generation=8), layout=None)
assert bad_layout["state"] == "SUPPRESSED"
assert bad_layout["reason"] == "DRAWING_SURFACE_LAYOUT_INVALID"

assert overlay.fixed_draw_state == {"enabled": True, "drawCount": 9}
assert bridge.status()["legacyPositionFallback"] is False
print("canonical P1 production bridge selftest PASS")
