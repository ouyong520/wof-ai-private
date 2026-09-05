from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from wof_launcher.canonical_runtime_coordinator import CanonicalRuntimeCoordinator
from wof_launcher.probe import WORLD_SHA256


AUTHORITY = "authority:p15-fixture"
RUNTIME_EPOCH = "1" * 32
RENDERER_A = "2" * 32
RENDERER_B = "3" * 32


class FakeSession:
    def __init__(self) -> None:
        self.bound = None
        self.last_payload = None
        self.closed = False
        self.clear_reasons = []

    def request(self, _method: str):
        return {}

    @staticmethod
    def _call_json(expression: str, name: str):
        marker = name + "("
        start = expression.index(marker) + len(marker)
        end = expression.index(");})()", start)
        return json.loads(expression[start:end])

    @staticmethod
    def _hud_status(binding, *, state="READY", reason=None):
        return {
            "state": state,
            "reason": reason,
            "bound": True,
            "authority": dict(binding),
            "fallback": "NONE",
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }

    def evaluate(self, expression: str, **_kwargs):
        if "WOF_P10_CLEAR" in expression:
            self.bound = None
            self.clear_reasons.append(expression)
            return {
                "state": "SUPPRESSED",
                "reason": "CLEARED",
                "bound": False,
                "authority": None,
                "fallback": "NONE",
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
            }
        if "WOF_P10_BIND" in expression:
            self.bound = self._call_json(expression, "bindCanonicalOverlayAuthority")
            return self._hud_status(
                self.bound,
                state="SUPPRESSED",
                reason="BOUND_WAITING_FOR_ENVELOPE",
            )
        if "WOF_P10_INGEST" in expression:
            self.last_payload = self._call_json(expression, "ingestCanonicalAnchorEnvelope")
            rows = self.last_payload.get("records") or []
            suppressed = [
                row
                for row in rows
                if row.get("canonicalAnchor", {}).get("state") == "SUPPRESSED"
            ]
            state = "SUPPRESSED" if suppressed else "READY"
            reason = suppressed[0]["canonicalAnchor"].get("reason") if suppressed else None
            return self._hud_status(self.bound, state=state, reason=reason)
        if "WOFAlphaCanonicalAnchorEnvelope" in expression:
            return True
        if "PRESERVED_CONFIG" in expression:
            return "PRESERVED_CONFIG"
        raise AssertionError(f"unexpected fake CDP expression: {expression[:120]}")

    def close(self) -> None:
        self.closed = True


class FakeClient:
    def __init__(self) -> None:
        self.sessions = []

    def attach(self, _target_id: str):
        session = FakeSession()
        self.sessions.append(session)
        return session


def actor(actor: str, generation: int, left: int, top: int):
    kind = "player" if actor.startswith("P") else "enemy"
    return {
        "kind": kind,
        "actor": actor,
        "generation": generation,
        "association": {
            "proven": True,
            "ambiguous": False,
            "candidateCount": 1,
        },
        "parts": [
            {
                "role": "body",
                "bounds": {
                    "left": left,
                    "top": top,
                    "right": left + 16,
                    "bottom": top + 32,
                },
            }
        ],
    }


def frame(renderer_epoch: str, *, source_proven=True, actors=None):
    return {
        "schema": "wof-render-object-frame-v1",
        "worldSha256": WORLD_SHA256,
        "authorityKey": AUTHORITY,
        "runtimeEpoch": RUNTIME_EPOCH,
        "rendererEpoch": renderer_epoch,
        "nativeWidth": 384,
        "nativeHeight": 224,
        "rendererSource": {
            "proven": source_proven,
            "kind": "renderer-side-equivalent",
        },
        "actors": list(actors or []),
    }


class P15CanonicalProductConvergenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeClient()
        self.runtime = CanonicalRuntimeCoordinator(
            lambda _rel: (_ for _ in ()).throw(
                AssertionError("normal AlphaRuntime must not require bridge reinjection")
            )
        )
        status = self.runtime.activate(
            self.client,
            "page-1",
            authority_key=AUTHORITY,
            runtime_epoch=RUNTIME_EPOCH,
            world_sha256=WORLD_SHA256,
            capability_present=True,
        )
        self.assertEqual(status["state"], "WAITING")
        self.assertFalse(status["bound"])
        self.assertFalse(status["legacySpatialFallback"])

    def test_bind_p12_p10_ingest_then_revoke(self):
        status = self.runtime.ingest_frame(
            frame(
                RENDERER_A,
                actors=[
                    actor("P1", 7, 100, 80),
                    actor("enemy-slot-4", 12, 200, 90),
                ],
            ),
            sample_at=1000,
        )
        self.assertEqual(status["state"], "READY")
        self.assertEqual(status["frameResolution"]["state"], "READY")
        self.assertEqual(status["frameResolution"]["descriptorCount"], 2)
        self.assertEqual(status["latestIngest"]["readyRecordCount"], 2)
        self.assertTrue(status["bound"])
        payload = status["bridge"]["lastPayload"]
        self.assertEqual(len(payload["records"]), 2)
        for row in payload["records"]:
            self.assertEqual(
                set(k for k in row if k in {"kind", "actor", "generation"}),
                {"kind", "actor", "generation"},
            )
            self.assertEqual(row["canonicalAnchor"]["state"], "READY")
            self.assertNotIn("legacyAnchor", row)
            self.assertNotIn("position", row)

        revoked = self.runtime.revoke("FIXTURE_DONE")
        self.assertFalse(revoked["bound"])
        self.assertEqual(revoked["state"], "SUPPRESSED")

    def test_unproven_renderer_suppresses_without_fallback_coordinates(self):
        status = self.runtime.ingest_frame(
            frame(
                RENDERER_A,
                source_proven=False,
                actors=[actor("enemy-slot-3", 9, 140, 70)],
            ),
            sample_at=1000,
        )
        self.assertEqual(status["frameResolution"]["state"], "READY")
        self.assertEqual(status["state"], "SUPPRESSED")
        self.assertEqual(status["reason"], "RENDERER_SOURCE_UNPROVEN")
        record = status["bridge"]["lastPayload"]["records"][0]
        anchor = record["canonicalAnchor"]
        self.assertEqual(anchor["state"], "SUPPRESSED")
        for forbidden in (
            "anchor",
            "renderAnchor",
            "position",
            "fallbackAnchor",
            "legacyAnchor",
        ):
            self.assertNotIn(forbidden, anchor)

    def test_renderer_epoch_change_clears_old_state_before_invalid_registry(self):
        ready = self.runtime.ingest_frame(
            frame(RENDERER_A, actors=[actor("P1", 1, 120, 80)]),
            sample_at=1000,
        )
        self.assertTrue(ready["bound"])

        bad = actor("P1", 2, 130, 80)
        bad["association"]["proven"] = False
        status = self.runtime.ingest_frame(
            frame(RENDERER_B, actors=[bad]),
            sample_at=1010,
        )
        self.assertEqual(status["frameResolution"]["state"], "SUPPRESSED")
        self.assertEqual(status["state"], "SUPPRESSED")
        self.assertFalse(status["bound"])
        self.assertEqual(status["rendererEpoch"], RENDERER_B)

    def test_existing_p11_direct_and_fixed_test_surfaces_remain_present(self):
        root = Path(__file__).resolve().parents[3]
        hud = (root / "product" / "alpha" / "wof_alpha_hud.js").read_text(encoding="utf-8")
        for token in (
            "bindP1HeadTrackerAuthority",
            "setP1HeadTracker",
            "clearP1HeadTrackerAuthority",
            "FIXED_TEST_ACTUALLY_DRAWN",
            "setFixedDrawSmokeEnabled",
            "ingestCanonicalAnchorEnvelope",
        ):
            self.assertIn(token, hud)
        self.assertNotRegex(
            hud,
            re.compile(r"canonicalOverlay.*legacyProjectionSelected", re.S),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
