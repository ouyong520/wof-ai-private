from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCER_PATH = ROOT / "wof_launcher" / "semantic_evidence_producer.py"
W2_PATH = ROOT / "wof_launcher" / "zero_click_identity_acquisition.py"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "alpha_v3_w6_semantic_evidence_producer.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = _load(PRODUCER_PATH, "semantic_evidence_producer_w6")
w2 = _load(W2_PATH, "zero_click_identity_acquisition_for_w6")


def _fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _args():
    base = copy.deepcopy(_fixture()["base"])
    return {
        "world_sha256": base["worldSha256"],
        "runtime_epoch": base["runtimeEpoch"],
        "layout_key": base["layoutKey"],
        "p1_lifecycle": base["p1Lifecycle"],
        "canvas": base["canvas"],
        "semantic_identity_observations": base["semanticIdentity"],
        "scene_head_observations": base["sceneHead"],
    }


def _mutation(name: str):
    args = _args()
    mutation = _fixture()["mutations"][name]
    if "semanticIdentity" in mutation:
        args["semantic_identity_observations"][0].update(copy.deepcopy(mutation["semanticIdentity"]))
    if "sceneHead" in mutation:
        args["scene_head_observations"][0].update(copy.deepcopy(mutation["sceneHead"]))
    return args


def test_safe_unique_produces_w2_consumable_envelope():
    args = _args()
    result = producer.produce_p1_zero_click_evidence(**args)
    assert result.ok is True
    assert result.reason == "SAFE_UNIQUE"
    assert result.envelope is not None
    envelope = result.envelope
    assert envelope["schema"] == "alpha-v3-runtime-p1-zero-click-evidence-v1"
    assert envelope["producerSchema"] == producer.PRODUCER_SCHEMA
    assert envelope["worldSha256"] == "921031"
    assert envelope["runtimeEpoch"] == args["runtime_epoch"]
    assert envelope["layoutKey"] == args["layout_key"]
    assert envelope["p1Generation"] == 9
    assert envelope["readOnly"] is True and envelope["ramWrites"] == 0 and envelope["inputInjection"] is False

    acquisition = w2.acquire_zero_click_p1_head(
        world_sha256=args["world_sha256"],
        p1_lifecycle=args["p1_lifecycle"],
        canvas=args["canvas"],
        hud_identity_candidates=envelope["hudIdentityCandidates"],
        scene_head_candidates=envelope["sceneHeadCandidates"],
    )
    assert acquisition.ok is True
    assert acquisition.reason == "SAFE_UNIQUE"
    assert acquisition.head_seed is not None
    assert acquisition.head_seed.p1_generation == 9
    assert set(acquisition.evidence_sources) == {"canvas", "hud", "sprite"}


def test_runtime_type_copy_cannot_masquerade_as_semantic_identity():
    result = producer.produce_p1_zero_click_evidence(**_mutation("runtimeTypeCopy"))
    assert (result.ok, result.reason, result.envelope) == (False, "CIRCULAR_RUNTIME_TYPE_REJECTED", None)


def test_generic_palette_cannot_masquerade_as_identity_authority():
    result = producer.produce_p1_zero_click_evidence(**_mutation("genericPalette"))
    assert (result.ok, result.reason, result.envelope) == (False, "GENERIC_PALETTE_REJECTED", None)


def test_semantic_or_scene_ambiguity_emits_no_envelope():
    semantic = producer.produce_p1_zero_click_evidence(**_mutation("semanticAmbiguous"))
    scene = producer.produce_p1_zero_click_evidence(**_mutation("sceneAmbiguous"))
    assert (semantic.ok, semantic.reason, semantic.envelope) == (False, "SEMANTIC_IDENTITY_AMBIGUOUS", None)
    assert (scene.ok, scene.reason, scene.envelope) == (False, "SCENE_HEAD_AMBIGUOUS", None)


def test_runtime_lifecycle_layout_and_canvas_staleness_revoke_evidence():
    expected = {
        "staleGeneration": "SCENE_HEAD_STALE",
        "staleRuntime": "SEMANTIC_IDENTITY_STALE",
        "staleLayout": "SCENE_HEAD_STALE",
        "staleCanvas": "SCENE_CANVAS_STALE",
    }
    for name, reason in expected.items():
        result = producer.produce_p1_zero_click_evidence(**_mutation(name))
        assert result.ok is False, name
        assert result.reason == reason, name
        assert result.envelope is None, name


def test_identity_and_runtime_type_conflicts_emit_no_envelope():
    identity = producer.produce_p1_zero_click_evidence(**_mutation("identityConflict"))
    runtime_type = producer.produce_p1_zero_click_evidence(**_mutation("semanticTypeConflict"))
    assert (identity.ok, identity.reason, identity.envelope) == (False, "SEMANTIC_SCENE_IDENTITY_CONFLICT", None)
    assert (runtime_type.ok, runtime_type.reason, runtime_type.envelope) == (False, "SEMANTIC_RUNTIME_TYPE_CONFLICT", None)


def test_multiple_input_rows_are_ambiguous_and_never_ranked_or_guessed():
    args = _args()
    args["semantic_identity_observations"].append(copy.deepcopy(args["semantic_identity_observations"][0]))
    semantic = producer.produce_p1_zero_click_evidence(**args)
    assert (semantic.ok, semantic.reason, semantic.envelope) == (False, "SEMANTIC_IDENTITY_AMBIGUOUS", None)

    args = _args()
    args["scene_head_observations"].append(copy.deepcopy(args["scene_head_observations"][0]))
    scene = producer.produce_p1_zero_click_evidence(**args)
    assert (scene.ok, scene.reason, scene.envelope) == (False, "SCENE_HEAD_AMBIGUOUS", None)


def test_producer_has_no_capture_ui_input_or_memory_write_primitives():
    source = PRODUCER_PATH.read_text(encoding="utf-8")
    forbidden = (
        "CdpClient",
        "Page.captureScreenshot",
        "Runtime.evaluate",
        "Input.dispatch",
        "dispatchMouseEvent",
        "armClick",
        "HEAPU8",
        "write_memory",
        "subprocess",
        "tkinter",
        "PIL",
    )
    assert all(token not in source for token in forbidden)
    assert producer.SAFETY == {"readOnly": True, "ramWrites": 0, "inputInjection": False}
