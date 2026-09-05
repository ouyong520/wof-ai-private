from copy import deepcopy
import unittest

from native_marker_renderer_submit_source_trace import (
    BLOCKER,
    BUNDLE_SCHEMA,
    EVENT_SCHEMA,
    ProducerBinding,
    SOURCE_SCHEMA,
    produce_native_marker_proof,
)

BINDING = ProducerBinding("runtime-epoch-0001", "renderer-epoch-001", "authority-key")


def source():
    return {
        "schema": SOURCE_SCHEMA,
        "derivationKind": "DIRECT_RENDER_HOOK",
        "guessed": False,
        "displayedFrameCausalLink": True,
        "coordinateAuthority": "NATIVE_RENDERER_OBJECT_384X224",
        "screenshotCoordinatesUsed": False,
        "ocrCoordinatesUsed": False,
        "templateCoordinatesUsed": False,
        "worldProjectionCoordinatesUsed": False,
        "sourceTrace": ["CPS1 object submit", "displayed native renderer frame"],
        "instrumentationId": "p36-test-hook",
        "hookSite": "explicit CPS1 displayed object submit",
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "ownerSelectionRequired": False,
        "manualSeedRequired": False,
    }


def marker(player="P1", generation=7, x=108, y=72):
    cluster = f"marker:{player.lower()}:g{generation}"
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
        "members": [
            {"memberKey": "label", "semanticRole": "PLAYER_LABEL", "clusterKey": cluster, "guessed": False},
            {
                "memberKey": "arrow",
                "semanticRole": "DOWN_ARROW",
                "clusterKey": cluster,
                "guessed": False,
                "anchorPoint": {"x": x, "y": y},
            },
        ],
    }


def event(i, player="P1", generation=7, x=108, y=72):
    return {
        "schema": EVENT_SCHEMA,
        "runtimeEpoch": BINDING.runtime_epoch,
        "rendererEpoch": BINDING.renderer_epoch,
        "authorityKey": BINDING.authority_key,
        "frameGeneration": 100 + i,
        "displayedFrameId": f"displayed-{i}",
        "submissionId": f"submit-{player}-{generation}-{i}",
        "displayedFrameCausalLink": True,
        "coordinateAuthority": "NATIVE_RENDERER_OBJECT_384X224",
        "guessed": False,
        "actorAssociation": {
            "player": player,
            "generation": generation,
            "explicit": True,
            "generationBound": True,
            "ambiguous": False,
            "candidateCount": 1,
            "guessed": False,
        },
        "marker": marker(player, generation, x, y),
    }


def bundle(events=None, direct_source=None):
    return {
        "schema": BUNDLE_SCHEMA,
        "source": source() if direct_source is None else direct_source,
        "events": list(events or []),
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "ownerSelectionRequired": False,
        "manualSeedRequired": False,
    }


class ProducerTests(unittest.TestCase):
    def test_direct_source_all_player_slots_feed_existing_p32(self):
        for player in ("P1", "P2", "P3"):
            events = [event(i, player=player) for i in (3, 1, 2)]
            out = produce_native_marker_proof(bundle(events), player=player, generation=7, binding=BINDING)
            self.assertEqual("READY_FOR_BOUNDED_LIVE_VERIFICATION", out["state"], player)
            self.assertIsNone(out["blocker"])
            self.assertEqual(player, out["qualification"]["anchor"]["player"])
            self.assertEqual([101, 102, 103], [s["frameGeneration"] for s in out["evidence"]["samples"]])
            self.assertFalse(out["ownerSelectionRequired"])
            self.assertFalse(out["manualSeedRequired"])

    def test_arrival_order_is_not_marker_identity_authority(self):
        events = [event(i) for i in (3, 1, 2)]
        a = produce_native_marker_proof(bundle(events), player="P1", generation=7, binding=BINDING)
        b = produce_native_marker_proof(bundle(list(reversed(events))), player="P1", generation=7, binding=BINDING)
        self.assertEqual("READY_FOR_BOUNDED_LIVE_VERIFICATION", a["state"])
        self.assertEqual(a["qualification"]["anchor"], b["qualification"]["anchor"])
        self.assertEqual(a["evidence"], b["evidence"])

    def test_structural_only_cannot_mint_authority(self):
        structural = {"structuralHeapCandidate": {"offset": 1234}}
        out = produce_native_marker_proof(bundle([event(i) for i in (1, 2, 3)], direct_source=structural),
                                          player="P1", generation=7, binding=BINDING)
        self.assertEqual("BLOCKED", out["state"])
        self.assertEqual(BLOCKER, out["blocker"])
        self.assertIsNone(out["qualification"])

    def test_visual_coordinate_sources_are_forbidden(self):
        for field in ("screenshotCoordinatesUsed", "ocrCoordinatesUsed", "templateCoordinatesUsed", "worldProjectionCoordinatesUsed"):
            bad = source()
            bad[field] = True
            out = produce_native_marker_proof(bundle([event(i) for i in (1, 2, 3)], bad),
                                              player="P1", generation=7, binding=BINDING)
            self.assertEqual("BLOCKED", out["state"], field)
            self.assertEqual(BLOCKER, out["blocker"])

    def test_stale_binding_is_rejected_not_ignored(self):
        events = [event(i) for i in (1, 2, 3)]
        events[1]["runtimeEpoch"] = "stale"
        out = produce_native_marker_proof(bundle(events), player="P1", generation=7, binding=BINDING)
        self.assertEqual("REJECTED", out["state"])
        self.assertEqual(BLOCKER, out["blocker"])
        self.assertTrue(any("RUNTIME_EPOCH_MISMATCH" in item for item in out["details"]))

    def test_ambiguous_actor_association_is_rejected(self):
        events = [event(i) for i in (1, 2, 3)]
        events[1]["actorAssociation"]["ambiguous"] = True
        events[1]["actorAssociation"]["candidateCount"] = 2
        out = produce_native_marker_proof(bundle(events), player="P1", generation=7, binding=BINDING)
        self.assertEqual("REJECTED", out["state"])
        self.assertTrue(any("ACTOR_ASSOCIATION_AMBIGUOUS" in item for item in out["details"]))

    def test_out_of_native_bounds_remains_p32_rejection(self):
        events = [event(i) for i in (1, 2, 3)]
        events[-1]["marker"]["members"][1]["anchorPoint"] = {"x": 385, "y": 72}
        out = produce_native_marker_proof(bundle(events), player="P1", generation=7, binding=BINDING)
        self.assertEqual("REJECTED", out["state"])
        self.assertEqual("EXISTING_P32_QUALIFIER_REJECTED_PRODUCER_EVIDENCE", out["reason"])

    def test_zero_click_contract_is_mandatory(self):
        value = bundle([event(i) for i in (1, 2, 3)])
        value["manualSeedRequired"] = True
        out = produce_native_marker_proof(value, player="P1", generation=7, binding=BINDING)
        self.assertEqual("REJECTED", out["state"])
        self.assertEqual("ZERO_CLICK_CONTRACT_VIOLATED", out["reason"])


if __name__ == "__main__":
    unittest.main()
