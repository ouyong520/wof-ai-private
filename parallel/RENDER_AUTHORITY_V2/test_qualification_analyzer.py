from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from qualification_analyzer import INCONCLUSIVE, PASS, REJECTED, analyze_capture


def candidate_capture() -> dict:
    base = {
        "schema": "wof-render-authority-capture-v2",
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "overlayEnabled": False,
        "worldSha256": "world",
        "authorityKey": "authority",
        "runtimeEpoch": "runtime-epoch",
        "rendererEpoch": "renderer-epoch",
        "rendererSourceQualification": "UNVERIFIED_CANDIDATE_ONLY",
        "canonicalNativeContract": {"width": 384, "height": 224, "accepted": False},
        "candidateTimeline": [],
    }
    for i in range(4):
        base["candidateTimeline"].append(
            {
                "at": 1000 + i * 250,
                "sequence": i + 1,
                "runtimeEpoch": "runtime-epoch",
                "rendererEpoch": "renderer-epoch",
                "authorityKey": "authority",
                "p1Lifecycle": {"active": True, "generation": 1},
                "regions": [
                    {
                        "heapOffset": 0x910000,
                        "byteOrder": "BE16",
                        "entries": [{"xWord": 10 + i, "yWord": 20, "tileWord": 30, "attrWord": 40}],
                    }
                ],
            }
        )
    return base


def proof_for(capture: dict) -> dict:
    return {
        "schema": "wof-renderer-source-proof-v1",
        "proofClass": "DIRECT_DISPLAYED_FRAME_RENDER_OBJECT",
        "displayedFrameCausalLink": True,
        "coordinateAuthority": "NATIVE_RENDERER_OBJECT_384X224",
        "addressDerivation": {"kind": "DIRECT_RENDER_HOOK", "guessed": False},
        "screenshotCoordinatesUsed": False,
        "worldProjectionCoordinatesUsed": False,
        "actorAssociation": {"explicit": True, "generationBound": True, "ambiguous": False},
        "runtimeEpoch": capture["runtimeEpoch"],
        "rendererEpoch": capture["rendererEpoch"],
        "authorityKey": capture["authorityKey"],
        "sourceTrace": ["CPS1 renderer submission", "direct object hook", "native object rows"],
        "directFrameSamples": 4,
        "frameGenerationMonotonic": True,
    }


class QualificationAnalyzerTests(unittest.TestCase):
    def test_structural_candidate_never_self_qualifies(self) -> None:
        report = analyze_capture(candidate_capture())
        self.assertEqual(report["status"], INCONCLUSIVE)
        self.assertFalse(report["canonicalProducerReadiness"]["rendererSource"]["proven"])
        self.assertIsNotNone(report["ownerAction"])
        self.assertIn("displayed CPS1 frame", report["blockingProofEdge"])

    def test_direct_causal_proof_can_pass(self) -> None:
        capture = candidate_capture()
        capture["rendererSourceProof"] = proof_for(capture)
        capture["rendererSourceQualification"] = "DIRECT_DISPLAYED_FRAME_RENDER_OBJECT"
        report = analyze_capture(capture)
        self.assertEqual(report["status"], PASS)
        self.assertTrue(report["canonicalProducerReadiness"]["rendererSource"]["proven"])
        self.assertIsNone(report["ownerAction"])

    def test_screenshot_production_coordinates_rejected(self) -> None:
        capture = candidate_capture()
        capture["productionCoordinateSource"] = "screenshot_projection"
        report = analyze_capture(capture)
        self.assertEqual(report["status"], REJECTED)

    def test_world_projection_proof_rejected(self) -> None:
        capture = candidate_capture()
        proof = proof_for(capture)
        proof["worldProjectionCoordinatesUsed"] = True
        capture["rendererSourceProof"] = proof
        self.assertEqual(analyze_capture(capture)["status"], REJECTED)

    def test_guessed_address_rejected(self) -> None:
        capture = candidate_capture()
        proof = proof_for(capture)
        proof["addressDerivation"] = {"kind": "DIRECT_RENDER_HOOK", "guessed": True}
        capture["rendererSourceProof"] = proof
        self.assertEqual(analyze_capture(capture)["status"], REJECTED)

    def test_stale_renderer_epoch_rejected(self) -> None:
        capture = candidate_capture()
        capture["candidateTimeline"][2]["rendererEpoch"] = "stale"
        report = analyze_capture(capture)
        self.assertEqual(report["status"], REJECTED)
        self.assertTrue(any("rendererEpoch mismatch" in reason for reason in report["rejections"]))

    def test_ambiguous_stable_candidates_stay_inconclusive(self) -> None:
        capture = candidate_capture()
        for frame in capture["candidateTimeline"]:
            frame["regions"].append(
                {"heapOffset": 0x910008, "byteOrder": "BE16", "entries": [{"xWord": 1, "yWord": 2, "tileWord": 3, "attrWord": 4}]}
            )
        report = analyze_capture(capture)
        self.assertEqual(report["status"], INCONCLUSIVE)
        self.assertEqual(len(report["timelineDiagnostics"]["stableCandidates"]), 2)

    def test_deterministic_output(self) -> None:
        capture = candidate_capture()
        first = json.dumps(analyze_capture(copy.deepcopy(capture)), sort_keys=True)
        second = json.dumps(analyze_capture(copy.deepcopy(capture)), sort_keys=True)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
