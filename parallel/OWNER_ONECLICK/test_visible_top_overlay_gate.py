from __future__ import annotations

import copy
import unittest

import refresh_manifest as refresh


class VisibleTopOverlayPackageGateTests(unittest.TestCase):
    def good_manifest(self) -> dict:
        return {
            "sourceCommit": "1" * 40,
            "components": {
                "renderAuthorityV3": {
                    "sliceARuntimeCommit": "2" * 40,
                    "selectedNormalPath": "production-top-overlay",
                    "productionOverlayEnabled": True,
                    "productionOverlaySuppressed": False,
                    "diagnosticOnly": False,
                    "whiteAcquisitionMarkerIsProduct": False,
                    "automaticSeedRequiredBeforeFallback": True,
                    "ownerClickFallbackMaximumPerAuthorityGeneration": 1,
                },
                "projectionProof": {"selected": False},
            },
            "safety": {
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
                "manualCalibration": False,
                "legacyProjectionSelected": False,
                "productionOverlayEnabled": True,
                "productionOverlaySuppressed": False,
            },
        }

    def test_runtime_source_gate_rejects_overlay_suppression(self) -> None:
        bad = 'SAFETY={"manualCalibration":False,"legacyProjectionSelected":False,"productionOverlayEnabled":False}\nsummary={"productionOverlaySuppressed":True}'
        with self.assertRaises(refresh.ManifestError):
            refresh.validate_visible_overlay_text(bad)

    def test_runtime_source_gate_requires_explicit_enabled_and_unsuppressed(self) -> None:
        good = 'SAFETY={"manualCalibration":False,"legacyProjectionSelected":False,"productionOverlayEnabled":True}\nsummary={"productionOverlaySuppressed":False}'
        refresh.validate_visible_overlay_text(good)
        for mutation in [
            good.replace('"productionOverlayEnabled":True', '"productionOverlayEnabled":False'),
            good.replace('"productionOverlaySuppressed":False', '"productionOverlaySuppressed":True'),
            good.replace('"manualCalibration":False', '"manualCalibration":True'),
            good.replace('"legacyProjectionSelected":False', '"legacyProjectionSelected":True'),
        ]:
            with self.subTest(mutation=mutation):
                with self.assertRaises(refresh.ManifestError):
                    refresh.validate_visible_overlay_text(mutation)

    def test_publishable_manifest_accepts_only_real_product_selection(self) -> None:
        refresh.verify_publishable_manifest(self.good_manifest())
        bad_cases = {
            "overlay_disabled": ("components", "renderAuthorityV3", "productionOverlayEnabled", False),
            "overlay_suppressed": ("components", "renderAuthorityV3", "productionOverlaySuppressed", True),
            "diagnostic_only": ("components", "renderAuthorityV3", "diagnosticOnly", True),
            "white_marker_product": ("components", "renderAuthorityV3", "whiteAcquisitionMarkerIsProduct", True),
            "no_slice_a_pin": ("components", "renderAuthorityV3", "sliceARuntimeCommit", ""),
            "legacy_projection_selected": ("components", "projectionProof", "selected", True),
            "manual_calibration": ("safety", "manualCalibration", None, True),
        }
        for name, (a, b, c, value) in bad_cases.items():
            m = copy.deepcopy(self.good_manifest())
            if c is None:
                m[a][b] = value
            else:
                m[a][b][c] = value
            with self.subTest(name=name):
                with self.assertRaises(refresh.ManifestError):
                    refresh.verify_publishable_manifest(m)

    def test_generator_refuses_to_publish_without_exact_slice_a_commit(self) -> None:
        with self.assertRaises(refresh.ManifestError) as ctx:
            refresh.generate_manifest(refresh.ROOT, "HEAD")
        self.assertIn("Slice A exact commit", str(ctx.exception))

    def test_selection_policy_names_visible_product_path(self) -> None:
        self.assertIn("visible-production-top-overlay", refresh.SELECTION_POLICY)
        self.assertIn("slice-a-pinned", refresh.SELECTION_POLICY)


if __name__ == "__main__":
    unittest.main(verbosity=2)
