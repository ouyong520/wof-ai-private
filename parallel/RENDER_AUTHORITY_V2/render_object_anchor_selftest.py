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

path = ROOT / "PYLAUNCH" / "wof_launcher" / "render_object_anchor.py"
spec = importlib.util.spec_from_file_location("wof_launcher.render_object_anchor", path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

AuthorityBinding = module.AuthorityBinding
DeterministicRenderObjectAnchor = module.DeterministicRenderObjectAnchor
NATIVE_WIDTH = module.NATIVE_WIDTH
NATIVE_HEIGHT = module.NATIVE_HEIGHT

binding = AuthorityBinding("authority", "0123456789abcdef", "fedcba9876543210")
resolver = DeterministicRenderObjectAnchor()
resolver.bind(binding)

def frame(*, runtime="0123456789abcdef", renderer="fedcba9876543210", source=True, actors=None):
    return {
        "schema": "wof-render-object-frame-v1",
        "worldSha256": probe.WORLD_SHA256,
        "authorityKey": "authority",
        "runtimeEpoch": runtime,
        "rendererEpoch": renderer,
        "nativeWidth": NATIVE_WIDTH,
        "nativeHeight": NATIVE_HEIGHT,
        "rendererSource": {"proven": source, "kind": "exact-cps1-buffered-object"},
        "actors": actors or [],
    }

actor = {
    "actor": "P1",
    "generation": 7,
    "association": {"proven": True, "ambiguous": False, "candidateCount": 1},
    "parts": [
        {"role": "body-tile", "bounds": {"left": 100, "top": 90, "right": 116, "bottom": 106}},
        {"role": "body-tile", "bounds": {"left": 100, "top": 106, "right": 116, "bottom": 122}},
        {"role": "weapon", "bounds": {"left": 60, "top": 80, "right": 150, "bottom": 130}},
        {"role": "projectile", "bounds": {"left": 200, "top": 20, "right": 216, "bottom": 36}},
    ],
}
good = resolver.resolve(frame(actors=[actor]), generation=7)
assert good["state"] == "READY"
assert good["anchor"] == {"x": 108.0, "y": 86.0}
assert good["bodyBounds"] == {"left": 100.0, "top": 90.0, "right": 116.0, "bottom": 122.0}
assert resolver.resolve(frame(actors=[actor]), generation=7) == good

assert resolver.resolve(frame(runtime="stale-runtime-0000", actors=[actor]), generation=7)["reason"] == "STALE_AUTHORITY_OR_RENDERER_EPOCH"
assert resolver.resolve(frame(renderer="stale-renderer-000", actors=[actor]), generation=7)["reason"] == "STALE_AUTHORITY_OR_RENDERER_EPOCH"
assert resolver.resolve(frame(source=False, actors=[actor]), generation=7)["reason"] == "RENDERER_SOURCE_UNPROVEN"
assert resolver.resolve(frame(actors=[actor, dict(actor)]), generation=7)["reason"] == "AMBIGUOUS_ACTOR_ASSOCIATION"

ambiguous = dict(actor)
ambiguous["association"] = {"proven": True, "ambiguous": True, "candidateCount": 2}
assert resolver.resolve(frame(actors=[ambiguous]), generation=7)["reason"] == "ACTOR_ASSOCIATION_UNPROVEN"

clipped = dict(actor)
clipped["parts"] = [{"role": "body", "bounds": {"left": -10, "top": -5, "right": 10, "bottom": 10}}]
clipped_out = resolver.resolve(frame(actors=[clipped]), generation=7)
assert clipped_out["state"] == "READY"
assert clipped_out["bodyBounds"] == {"left": 0.0, "top": 0.0, "right": 10.0, "bottom": 10.0}
assert clipped_out["anchor"] == {"x": 5.0, "y": 0.0}

resolver.revoke()
assert resolver.resolve(frame(actors=[actor]), generation=7)["reason"] == "NO_AUTHORITY_BINDING"
print("render-object-anchor selftest PASS")
