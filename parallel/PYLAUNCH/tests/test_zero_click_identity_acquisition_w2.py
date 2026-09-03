from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "wof_launcher" / "zero_click_identity_acquisition.py"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "alpha_v3_w2_zero_click_identity_acquisition.json"
spec = importlib.util.spec_from_file_location("zero_click_identity_acquisition_w2", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def _fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _args():
    fixture = _fixture()
    base = copy.deepcopy(fixture["base"])
    return {
        "world_sha256": fixture["worldSha256"],
        "p1_lifecycle": base["p1Lifecycle"],
        "canvas": base["canvas"],
        "hud_identity_candidates": base["hud"],
        "scene_head_candidates": base["scene"],
    }


def _mutation(name: str):
    fixture = _fixture()
    args = _args()
    mutation = fixture["mutations"][name]
    if "worldSha256" in mutation:
        args["world_sha256"] = mutation["worldSha256"]
    if "hud" in mutation:
        args["hud_identity_candidates"] = copy.deepcopy(mutation["hud"])
    if "sceneAppend" in mutation:
        args["scene_head_candidates"].append(copy.deepcopy(mutation["sceneAppend"]))
    if "scenePatch" in mutation:
        args["scene_head_candidates"][0].update(copy.deepcopy(mutation["scenePatch"]))
    return args


def test_safe_unique_zero_click_seed_is_identity_and_generation_bound():
    result = module.acquire_zero_click_p1_head(**_args())
    assert result.ok is True
    assert result.reason == "SAFE_UNIQUE"
    assert result.confidence == 0.93
    assert result.character_type == 2
    assert result.p1_generation == 7
    assert result.head_seed is not None
    assert result.head_seed.center_x == 145.0
    assert result.head_seed.canvas_digest == "sha256:09f8b6b4c0c010720c6f5e61eec33bbb3fd03632ddcb4ede98282368a8a590a5"
    assert set(result.evidence_sources) == {"canvas", "hud", "sprite"}
    assert result.as_dict()["inputInjection"] is False
    assert module.screenshot_digest(b"w2-fixture-canvas") == result.head_seed.canvas_digest


def test_wrong_world_and_wrong_hud_portrait_fail_closed():
    world = module.acquire_zero_click_p1_head(**_mutation("wrongWorld"))
    portrait = module.acquire_zero_click_p1_head(**_mutation("wrongHudPortrait"))
    assert (world.ok, world.reason, world.head_seed) == (False, "WORLD_MISMATCH", None)
    assert (portrait.ok, portrait.reason, portrait.head_seed) == (False, "HUD_PORTRAIT_REJECTED", None)


def test_ambiguous_scene_never_picks_first_candidate():
    result = module.acquire_zero_click_p1_head(**_mutation("ambiguousScene"))
    assert result.ok is False
    assert result.reason == "AMBIGUOUS_SCENE_P1_HEAD"
    assert result.head_seed is None
    assert result.ambiguity_margin is not None and result.ambiguity_margin < module.DEFAULT_AMBIGUITY_MARGIN


def test_wrong_actor_stale_generation_and_bad_geometry_fail_closed():
    cases = {
        "wrongActor": "REJECTED_WRONG_ACTOR",
        "staleGeneration": "STALE_P1_GENERATION",
        "outOfBounds": "HEAD_SEED_OUT_OF_BOUNDS",
    }
    for name, reason in cases.items():
        result = module.acquire_zero_click_p1_head(**_mutation(name))
        assert result.ok is False, name
        assert result.reason == reason, name
        assert result.head_seed is None, name


def test_scene_requires_verified_read_only_visual_authority():
    result = module.acquire_zero_click_p1_head(**_mutation("noSceneAuthority"))
    assert result.ok is False
    assert result.reason == "SCENE_COARSE_PRIOR_CONFLICT"
    assert result.head_seed is None
    assert module.SAFETY == {"readOnly": True, "ramWrites": 0, "inputInjection": False}


def test_no_input_or_memory_write_primitives_are_present():
    source = MODULE_PATH.read_text(encoding="utf-8")
    forbidden = ("Input.dispatch", "dispatchMouseEvent", "armClick", "HEAPU8", "write_memory", "Runtime.evaluate")
    assert all(token not in source for token in forbidden)
