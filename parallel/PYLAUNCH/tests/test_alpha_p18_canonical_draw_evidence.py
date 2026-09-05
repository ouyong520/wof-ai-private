from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

PYLAUNCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.canonical_draw_evidence import (  # noqa: E402
    HUD_EVIDENCE_SCHEMA,
    HUD_EVIDENCE_VERSION,
    collect_canonical_draw_evidence,
)


AUTHORITY = {
    "authorityKey": "authority-p18",
    "runtimeEpoch": "runtime-epoch-p18-0001",
    "rendererEpoch": "renderer-epoch-p18-0001",
    "worldSha256": "a" * 64,
}
PAGE_ID = "page-accepted-p18"
PAGE_URL = "https://example.invalid/wof"


def valid_remote(authority=None):
    binding = dict(authority or AUTHORITY)
    row = {
        "sequence": 4,
        "acknowledgedAt": 123456,
        "evidenceGeneration": 2,
        "kind": "enemy-target-label",
        "primitive": "maintained-labelTex-nativeDraw",
        "completed": True,
        "actor": "enemy-slot-0",
        "generation": 7,
        "sourceId": "enemy-slot-0",
        "label": "1P",
        "warningIdentity": None,
        "nativeX": 25,
        "nativeY": 30,
        "nativeWidth": 384,
        "nativeHeight": 224,
        "drawRectDb": {"x": 50, "y": 50, "width": 30, "height": 18},
        "mappingKey": "m",
        "authority": binding,
        "sampleIdentity": {"transportSequence": 11, "sampleAt": 123450, "envelopeReceivedAt": 123451},
        "coordinateAuthority": "canonical-render-object-only",
        "screenshotAuthority": False,
        "worldProjectionAuthority": False,
        "visibleProof": "NOT_PROVEN",
    }
    return {
        "schema": HUD_EVIDENCE_SCHEMA,
        "version": HUD_EVIDENCE_VERSION,
        "evidenceState": "CANONICAL_DRAW_ACKNOWLEDGED",
        "reason": None,
        "bound": True,
        "authority": binding,
        "evidenceGeneration": 2,
        "maxEntries": 128,
        "entryCount": 1,
        "entries": [row],
        "latestAcknowledgement": row,
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "legacySpatialFallback": False,
            "screenshotAuthority": False,
            "worldProjectionAuthority": False,
            "positionAuthority": False,
        },
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "visibleProof": "NOT_PROVEN",
    }


class FakeSession:
    def __init__(self, remote):
        self.remote = remote
        self.closed = False
        self.enabled = False
        self.expressions = []

    def request(self, method, params=None):
        if method != "Runtime.enable":
            raise AssertionError(method)
        self.enabled = True
        return {}

    def evaluate(self, expression, *, timeout=5.0):
        self.expressions.append(expression)
        return copy.deepcopy(self.remote)

    def close(self):
        self.closed = True


class FakeClient:
    def __init__(self, remote, *, target_id=PAGE_ID, target_url=PAGE_URL, target_type="page"):
        self.remote = remote
        self.target = {"targetId": target_id, "url": target_url, "type": target_type}
        self.attached = []
        self.session = None

    def request(self, method, params=None):
        if method != "Target.getTargets":
            raise AssertionError(method)
        return {"targetInfos": [dict(self.target)]}

    def attach(self, target_id):
        self.attached.append(target_id)
        self.session = FakeSession(self.remote)
        return self.session


class CanonicalDrawEvidenceCollectorTests(unittest.TestCase):
    def collect(self, client, directory, **kwargs):
        output = Path(directory) / "ALPHA_CANONICAL_DRAW_EVIDENCE.json"
        result = collect_canonical_draw_evidence(
            client,
            page_target_id=kwargs.pop("page_target_id", PAGE_ID),
            expected_page_url=kwargs.pop("expected_page_url", PAGE_URL),
            expected_authority=kwargs.pop("expected_authority", AUTHORITY),
            output_path=output,
        )
        self.assertFalse(kwargs)
        self.assertTrue(output.exists())
        with output.open("r", encoding="utf-8") as handle:
            persisted = json.load(handle)
        self.assertEqual(persisted, result)
        self.assertEqual(list(output.parent.glob(f".{output.name}.*.tmp")), [])
        return result

    def test_exact_identity_is_accepted_and_atomically_written(self):
        with tempfile.TemporaryDirectory() as td:
            client = FakeClient(valid_remote())
            result = self.collect(client, td)
        self.assertEqual(result["evidenceState"], "CANONICAL_DRAW_ACKNOWLEDGED")
        self.assertEqual(result["acknowledgementCount"], 1)
        self.assertEqual(result["authority"], AUTHORITY)
        self.assertEqual(result["visibleProof"], "NOT_PROVEN")
        self.assertEqual(result["safety"]["positionAuthority"], False)
        self.assertEqual(client.attached, [PAGE_ID])
        self.assertTrue(client.session.closed)
        self.assertIn("canonicalDrawEvidence", client.session.expressions[0])

    def test_runtime_and_renderer_mismatch_are_rejected(self):
        for key, bad in (("runtimeEpoch", "runtime-epoch-stale-9999"), ("rendererEpoch", "renderer-epoch-stale-9999")):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as td:
                wrong = dict(AUTHORITY)
                wrong[key] = bad
                client = FakeClient(valid_remote(wrong))
                result = self.collect(client, td)
                self.assertEqual(result["evidenceState"], "STALE_OR_MISMATCH")
                self.assertEqual(result["reason"], "AUTHORITY_RUNTIME_RENDERER_MISMATCH")
                self.assertEqual(result["acknowledgementCount"], 0)
                self.assertIsNone(result["authority"])
                self.assertEqual(result["visibleProof"], "NOT_PROVEN")

    def test_page_target_url_mismatch_is_rejected_before_attach(self):
        with tempfile.TemporaryDirectory() as td:
            client = FakeClient(valid_remote(), target_url="https://example.invalid/stale-page")
            result = self.collect(client, td)
        self.assertEqual(result["evidenceState"], "STALE_OR_MISMATCH")
        self.assertEqual(result["reason"], "PAGE_TARGET_URL_MISMATCH")
        self.assertEqual(client.attached, [])

    def test_missing_hud_api_is_explicit_and_not_visible_proof(self):
        with tempfile.TemporaryDirectory() as td:
            client = FakeClient({"__wofP18": "HUD_API_MISSING"})
            result = self.collect(client, td)
        self.assertEqual(result["evidenceState"], "HUD_API_MISSING")
        self.assertEqual(result["acknowledgementCount"], 0)
        self.assertEqual(result["visibleProof"], "NOT_PROVEN")

    def test_empty_exact_snapshot_is_no_draw_not_pass(self):
        remote = valid_remote()
        remote["evidenceState"] = "NO_CANONICAL_DRAW"
        remote["reason"] = "HUD_INGEST_ACCEPTED_WAITING_FOR_DRAW"
        remote["entryCount"] = 0
        remote["entries"] = []
        remote["latestAcknowledgement"] = None
        with tempfile.TemporaryDirectory() as td:
            result = self.collect(FakeClient(remote), td)
        self.assertEqual(result["evidenceState"], "NO_CANONICAL_DRAW")
        self.assertEqual(result["visibleProof"], "NOT_PROVEN")
        self.assertEqual(result["reason"], "HUD_INGEST_ACCEPTED_WAITING_FOR_DRAW")


if __name__ == "__main__":
    unittest.main()