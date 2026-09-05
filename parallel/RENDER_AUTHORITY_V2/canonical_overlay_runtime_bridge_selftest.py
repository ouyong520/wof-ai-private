from __future__ import annotations

import importlib.util
import json
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
production_stub.HUD_SOURCES = (
    "product/alpha/wof_alpha_hud_model.js",
    "product/alpha/wof_alpha_enemy_target_labels.js",
    "product/alpha/wof_alpha_player_head_warning.js",
    "product/alpha/wof_alpha_relative_head_anchor.js",
    "product/alpha/wof_alpha_hud.js",
    "product/alpha/wof_alpha_relative_enemy_overlay.js",
)
sys.modules[production_stub.__name__] = production_stub

bridge_path = ROOT / "PYLAUNCH" / "wof_launcher" / "canonical_overlay_runtime_bridge.py"
bridge_spec = importlib.util.spec_from_file_location("wof_launcher.canonical_overlay_runtime_bridge", bridge_path)
bridge_module = importlib.util.module_from_spec(bridge_spec)
assert bridge_spec and bridge_spec.loader
sys.modules[bridge_spec.name] = bridge_module
bridge_spec.loader.exec_module(bridge_module)

AuthorityBinding = anchor_module.AuthorityBinding
CanonicalOverlayRuntimeBridge = bridge_module.CanonicalOverlayRuntimeBridge

required = [
    "product/alpha/wof_alpha_enemy_target_labels.js",
    "product/alpha/wof_alpha_player_head_warning.js",
    "product/alpha/wof_alpha_canonical_anchor_envelope.js",
    "product/alpha/wof_alpha_canonical_overlay_plan.js",
    "product/alpha/wof_alpha_hud.js",
]
positions = [bridge_module.CANONICAL_HUD_SOURCES.index(rel) for rel in required]
assert positions == sorted(positions), bridge_module.CANONICAL_HUD_SOURCES


def make_frame(*, renderer="fedcba9876543210", source=True):
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
                "generation": 7,
                "association": {"proven": True, "ambiguous": False, "candidateCount": 1},
                "parts": [
                    {"role": "body-tile", "bounds": {"left": 100, "top": 90, "right": 116, "bottom": 106}},
                    {"role": "body-tile", "bounds": {"left": 100, "top": 106, "right": 116, "bottom": 122}},
                ],
            },
            {
                "actor": "enemy-slot-4",
                "generation": 3,
                "association": {"proven": True, "ambiguous": False, "candidateCount": 1},
                "parts": [
                    {"role": "actor-body", "bounds": {"left": 180, "top": 80, "right": 204, "bottom": 112}},
                ],
            },
        ],
    }


class FakeSession:
    def __init__(self, binding):
        self.binding = {
            "authorityKey": binding.authority_key,
            "runtimeEpoch": binding.runtime_epoch,
            "rendererEpoch": binding.renderer_epoch,
            "worldSha256": binding.world_sha256,
        }
        self.calls = []
        self.capable = False
        self.bound = False
        self.closed = False

    def request(self, method, params=None, timeout=None):
        self.calls.append(("request", method, params))
        assert method == "Runtime.enable"
        return {}

    def _status(self, state="SUPPRESSED", reason=None):
        return {
            "schema": "wof-alpha-maintained-hud-canonical-overlay-status-v1",
            "bound": self.bound,
            "state": state,
            "reason": reason,
            "authority": dict(self.binding) if self.bound else None,
            "fallback": "NONE",
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }

    def evaluate(self, expression, *, await_promise=False, timeout=8.0):
        self.calls.append(("evaluate", expression))
        if expression.startswith("(()=>!!("):
            return self.capable
        if "return 'DIRECT_CONFIG'" in expression:
            return "DIRECT_CONFIG"
        if expression.startswith("(0,eval)("):
            if "SOURCE:product/alpha/wof_alpha_hud.js" in expression:
                self.capable = True
            return True
        if "/*WOF_P10_BIND*/" in expression:
            self.bound = True
            return self._status("SUPPRESSED", "BOUND_WAITING_FOR_ENVELOPE")
        if "/*WOF_P10_INGEST*/" in expression:
            assert self.bound
            state = "READY" if '\"state\":\"READY\"' in expression else "SUPPRESSED"
            return self._status(state, None if state == "READY" else "CANONICAL_SUPPRESSED")
        if "/*WOF_P10_CLEAR*/" in expression:
            self.bound = False
            return self._status("SUPPRESSED", "CLEARED")
        raise AssertionError("unexpected expression: " + expression[:120])

    def close(self):
        self.closed = True


class FakeClient:
    def __init__(self, binding):
        self.session = FakeSession(binding)
        self.target_ids = []

    def attach(self, target_id):
        self.target_ids.append(target_id)
        return self.session


def verified_text(rel):
    return "SOURCE:" + rel


binding = AuthorityBinding("authority", "0123456789abcdef", "fedcba9876543210")
client = FakeClient(binding)
bridge = CanonicalOverlayRuntimeBridge(verified_text)
bound = bridge.bind(client, "page-1", binding)
assert bound["bound"] is True
assert bound["legacyPositionFallback"] is False
assert client.target_ids == ["page-1"]

ready = bridge.ingest_frame(
    make_frame(),
    [
        {"kind": "player", "actor": "P1", "generation": 7},
        {"kind": "enemy", "actor": "enemy-slot-4", "generation": 3},
    ],
    sample_at=1000,
)
assert ready["recordCount"] == 2
assert ready["readyRecordCount"] == 2
records = ready["lastPayload"]["records"]
assert records[0]["canonicalAnchor"]["anchor"] == {"x": 108.0, "y": 86.0}
assert records[1]["canonicalAnchor"]["anchor"] == {"x": 192.0, "y": 76.0}
assert all(row["sampleAt"] == 1000.0 for row in records)
assert all(row["authorityKey"] == "authority" for row in records)
assert all(row["rendererEpoch"] == "fedcba9876543210" for row in records)
ready_expr = [row[1] for row in client.session.calls if row[0] == "evaluate" and "/*WOF_P10_INGEST*/" in row[1]][-1]
assert '"schema":"wof-alpha-canonical-anchor-runtime-envelope-input-v1"' in ready_expr
assert '"actor":"P1"' in ready_expr and '"generation":7' in ready_expr
assert '"x":108.0' in ready_expr and '"y":86.0' in ready_expr

suppressed = bridge.ingest_frame(
    make_frame(renderer="stale-renderer-00"),
    [{"kind": "player", "actor": "P1", "generation": 7}],
    sample_at=1001,
)
assert suppressed["recordCount"] == 1
assert suppressed["readyRecordCount"] == 0
assert suppressed["suppressedRecordCount"] == 1
suppressed_anchor = suppressed["lastPayload"]["records"][0]["canonicalAnchor"]
assert suppressed_anchor["state"] == "SUPPRESSED"
assert suppressed_anchor["reason"] == "STALE_AUTHORITY_OR_RENDERER_EPOCH"
assert "anchor" not in suppressed_anchor
suppressed_expr = [row[1] for row in client.session.calls if row[0] == "evaluate" and "/*WOF_P10_INGEST*/" in row[1]][-1]
payload_json = suppressed_expr.split("ingestCanonicalAnchorEnvelope(", 1)[1].split(");})()", 1)[0]
payload = json.loads(payload_json)
assert payload["records"][0]["canonicalAnchor"]["state"] == "SUPPRESSED"
assert "anchor" not in payload["records"][0]["canonicalAnchor"]

revoked = bridge.revoke("RENDERER_EPOCH_CHANGED")
assert revoked["bound"] is False
assert revoked["recordCount"] == 0
assert client.session.closed is True
clear_calls = [row for row in client.session.calls if row[0] == "evaluate" and "/*WOF_P10_CLEAR*/" in row[1]]
assert clear_calls, client.session.calls

print("canonical overlay runtime bridge selftest PASS")
