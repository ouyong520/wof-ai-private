from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.alpha_runtime import AlphaRuntimeError, AlphaRuntimeManager, PACKAGE_MANIFEST_ENV
from wof_launcher.production_p1_overlay import HUD_SOURCES, ProductionP1Overlay, ProductionP1OverlayError

P9 = "product/alpha/wof_alpha_canonical_anchor_envelope.js"
P8 = "product/alpha/wof_alpha_canonical_overlay_plan.js"
HUD = "product/alpha/wof_alpha_hud.js"


class FakeSession:
    def __init__(self) -> None:
        self.closed = False

    def request(self, _method: str):
        return {}

    def evaluate(self, expression: str, **_kwargs):
        if expression.startswith("!!(window.WOFALPHAHUD"):
            return False
        if "const c=window.__WOF_ALPHA_CONFIG" in expression:
            return "DIRECT_CONFIG"
        if "window.WOFHEADVISUALV3" in expression:
            return True
        if "productionOverlayEnabled:true" in expression:
            return {
                "schema": "wof-alpha-production-p1-overlay-adapter-v1",
                "authorityKey": "authority-1",
                "runtimeEpoch": "runtime-1",
                "productionOverlayEnabled": True,
                "visible": False,
                "drawCount": 0,
                "drawHooked": True,
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
            }
        return True

    def close(self):
        self.closed = True


class FakeClient:
    def __init__(self) -> None:
        self.session = FakeSession()

    def attach(self, _target_id: str):
        return self.session


class AlphaP30P9P1BindingTests(unittest.TestCase):
    def test_p1_fallback_injects_p9_and_p8_before_maintained_hud(self):
        self.assertLess(HUD_SOURCES.index(P9), HUD_SOURCES.index(P8))
        self.assertLess(HUD_SOURCES.index(P8), HUD_SOURCES.index(HUD))
        requested: list[str] = []

        def verified(rel: str) -> str:
            requested.append(rel)
            return "true"

        status = ProductionP1Overlay(verified).bind(FakeClient(), "page-1", "authority-1", "runtime-1")
        self.assertEqual(status["installMode"], "DIRECT_CONFIG")
        self.assertLess(requested.index(P9), requested.index(P8))
        self.assertLess(requested.index(P8), requested.index(HUD))

    def test_p1_binding_fails_closed_with_exact_p9_diagnostic_when_pin_is_missing(self):
        def verified(rel: str) -> str:
            if rel == P9:
                raise RuntimeError(f"package manifest did not pin {rel}")
            return "true"

        with self.assertRaisesRegex(ProductionP1OverlayError, "wof_alpha_canonical_anchor_envelope\\.js"):
            ProductionP1Overlay(verified).bind(FakeClient(), "page-1", "authority-1", "runtime-1")

    def test_alpha_runtime_reads_only_explicit_staged_manifest_when_bound(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            checkout = root / "checkout"; checkout.mkdir()
            staged = root / "run" / "PACKAGE_MANIFEST.json"; staged.parent.mkdir()
            staged.write_text(json.dumps({
                "schema": "wof-owner-oneclick-package-v1",
                "sourceCommit": "a" * 40,
                "packageVersion": "pkg",
                "files": [
                    {"path": P9, "gitBlobSha": "1" * 40},
                    {"path": P8, "gitBlobSha": "2" * 40},
                ],
            }), encoding="utf-8")
            env = {
                PACKAGE_MANIFEST_ENV: str(staged),
                "WOF_ALPHA_ACCEPTANCE_COMMIT": "a" * 40,
                "WOF_ALPHA_ACCEPTANCE_PACKAGE_VERSION": "pkg",
            }
            with patch.dict(os.environ, env, clear=False):
                manager = AlphaRuntimeManager(checkout)
                manifest = manager._load_manifest()
                self.assertEqual(manifest["packageVersion"], "pkg")
                self.assertEqual(manager._blob_map[P9], "1" * 40)
                self.assertEqual(manager._blob_map[P8], "2" * 40)

    def test_explicit_staged_manifest_identity_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); checkout = root / "checkout"; checkout.mkdir()
            staged = root / "manifest.json"
            staged.write_text(json.dumps({
                "schema": "wof-owner-oneclick-package-v1",
                "sourceCommit": "b" * 40,
                "packageVersion": "wrong",
                "files": [],
            }), encoding="utf-8")
            env = {
                PACKAGE_MANIFEST_ENV: str(staged),
                "WOF_ALPHA_ACCEPTANCE_COMMIT": "a" * 40,
                "WOF_ALPHA_ACCEPTANCE_PACKAGE_VERSION": "pkg",
            }
            with patch.dict(os.environ, env, clear=False):
                with self.assertRaisesRegex(AlphaRuntimeError, "packageVersion"):
                    AlphaRuntimeManager(checkout)._load_manifest()


if __name__ == "__main__":
    unittest.main()
