from copy import deepcopy
import unittest

from native_player_marker_anchor_qualification import (
    EVIDENCE_SCHEMA,
    ExpectedBinding,
    QUALIFIED,
    REJECTED,
    qualify_native_player_marker,
)

BINDING = ExpectedBinding("runtime-epoch-0001", "renderer-epoch-001", "authority-key")


def marker(player="P1", generation=7, members=None, cluster="cluster:p1:g7"):
    return {
        "player": player,
        "generation": generation,
        "labelSemantic": {"P1": "1P", "P2": "2P", "P3": "3P"}[player],
        "clusterKey": cluster,
        "clusterJoin": {"explicit": True, "guessed": False, "key": cluster},
        "actorAssociation": {
            "player": player,
            "generation": generation,
            "explicit": True,
            "generationBound": True,
            "ambiguous": False,
            "candidateCount": 1,
            "guessed": False,
        },
        "members": members or [
            {"memberKey": "label", "semanticRole": "PLAYER_LABEL", "clusterKey": cluster, "guessed": False},
            {"memberKey": "arrow", "semanticRole": "DOWN_ARROW", "clusterKey": cluster, "guessed": False, "anchorPoint": {"x": 108, "y": 72}},
        ],
    }


def evidence():
    samples = []
    for i, frame_generation in enumerate((101, 102, 103), 1):
        samples.append({
            "runtimeEpoch": BINDING.runtime_epoch,
            "rendererEpoch": BINDING.renderer_epoch,
            "authorityKey": BINDING.authority_key,
            "frameGeneration": frame_generation,
            "displayedFrameId": f"display-{i}",
            "submissionId": f"submit-{i}",
            "actorAssociation": {"player": "P1", "generation": 7},
            "markers": [marker()],
        })
    return {
        "schema": EVIDENCE_SCHEMA,
        "runtimeEpoch": BINDING.runtime_epoch,
        "rendererEpoch": BINDING.renderer_epoch,
        "authorityKey": BINDING.authority_key,
        "nativeWidth": 384,
        "nativeHeight": 224,
        "directSource": {
            "derivationKind": "DIRECT_RENDER_HOOK",
            "guessed": False,
            "displayedFrameCausalLink": True,
            "coordinateAuthority": "NATIVE_RENDERER_OBJECT_384X224",
            "screenshotCoordinatesUsed": False,
            "ocrCoordinatesUsed": False,
            "templateCoordinatesUsed": False,
            "worldProjectionCoordinatesUsed": False,
            "sourceTrace": ["renderer submit hook", "displayed CPS1 frame"],
            "instrumentationId": "p32-contract-test",
            "hookSite": "explicit renderer object submit",
        },
        "samples": samples,
    }


class QualificationTests(unittest.TestCase):
    def test_direct_marker_contract_qualifies_exact_generation(self):
        out = qualify_native_player_marker(evidence(), player="P1", generation=7, binding=BINDING)
        self.assertEqual(QUALIFIED, out["state"])
        self.assertEqual({"x": 108.0, "y": 72.0}, {"x": out["anchor"]["x"], "y": out["anchor"]["y"]})
        self.assertEqual("wof-renderer-source-proof-v1", out["rendererSourceProof"]["schema"])
        self.assertEqual(3, out["rendererSourceProof"]["directFrameSamples"])

    def test_multi_object_row_order_is_not_authority(self):
        a = evidence()
        b = evidence()
        for sample in b["samples"]:
            sample["markers"][0]["members"].reverse()
        out_a = qualify_native_player_marker(a, player="P1", generation=7, binding=BINDING)
        out_b = qualify_native_player_marker(b, player="P1", generation=7, binding=BINDING)
        self.assertEqual(QUALIFIED, out_a["state"])
        self.assertEqual(out_a["anchor"], out_b["anchor"])
        self.assertEqual(out_a["rendererSourceProof"]["nativePlayerMarker"], out_b["rendererSourceProof"]["nativePlayerMarker"])

    def test_duplicate_same_player_marker_fails_closed(self):
        value = evidence()
        value["samples"][1]["markers"].append(deepcopy(value["samples"][1]["markers"][0]))
        out = qualify_native_player_marker(value, player="P1", generation=7, binding=BINDING)
        self.assertEqual(REJECTED, out["state"])
        self.assertIsNone(out["rendererSourceProof"])
        self.assertIn("SAMPLE_1_DUPLICATE_OR_MISSING_PLAYER_MARKER", out["details"])

    def test_stale_epoch_or_generation_mismatch_rejected(self):
        for field, value in (("runtimeEpoch", "stale-runtime"), ("rendererEpoch", "stale-renderer"), ("authorityKey", "stale-authority")):
            sample = evidence()
            sample["samples"][0][field] = value
            out = qualify_native_player_marker(sample, player="P1", generation=7, binding=BINDING)
            self.assertEqual(REJECTED, out["state"])
            self.assertIsNone(out["rendererSourceProof"])
        generation = evidence()
        generation["samples"][0]["actorAssociation"]["generation"] = 8
        out = qualify_native_player_marker(generation, player="P1", generation=7, binding=BINDING)
        self.assertEqual(REJECTED, out["state"])
        self.assertIsNone(out["rendererSourceProof"])

    def test_visual_or_structural_only_evidence_cannot_qualify(self):
        for mutation in ("screenshot", "structural"):
            value = evidence()
            if mutation == "screenshot":
                value["directSource"]["screenshotCoordinatesUsed"] = True
            else:
                value.pop("directSource")
                value["structuralHeapCandidate"] = {"heapOffset": 1234, "authority": "UNVERIFIED_CANDIDATE_ONLY"}
            out = qualify_native_player_marker(value, player="P1", generation=7, binding=BINDING)
            self.assertEqual(REJECTED, out["state"])
            self.assertIsNone(out["rendererSourceProof"])

    def test_no_proof_when_displayed_frame_causal_link_absent(self):
        value = evidence()
        value["directSource"]["displayedFrameCausalLink"] = False
        out = qualify_native_player_marker(value, player="P1", generation=7, binding=BINDING)
        self.assertEqual(REJECTED, out["state"])
        self.assertIsNone(out["rendererSourceProof"])


if __name__ == "__main__":
    unittest.main()
