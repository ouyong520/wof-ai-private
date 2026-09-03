# Alpha V3 W2 — Zero-click P1 Identity / Head Acquisition SUBRESULT

Status: **SUBCOMPLETE — integration-ready module; V3 umbrella authority not claimed**

## Scope / dedup

- W2 dedup key: `alpha.v1.render-authority-v3.w2-zero-click-identity-acquisition`
- W2 stage: `ALPHA_V1_RENDER_AUTHORITY_V3_W2_ZERO_CLICK_IDENTITY_ACQUISITION`
- W2 claim token: `w2-7f7e3bcf63c142eda60ea2b1f051f3e4`
- Start commit: `78335c095af09f20af05e13e959d445d5c0017e5`
- During W2 execution W1 independently landed its screenshot/HUD-to-scene heuristic in `head_visual_tracker.py`. W2 therefore deliberately does **not** duplicate pixel scanning or tracker integration. W2 is the independent fail-closed identity/evidence adjudicator W1 can place in front of `ONE_CLICK_REQUIRED`.

## Durable outputs

1. Production-independent module:
   - `parallel/PYLAUNCH/wof_launcher/zero_click_identity_acquisition.py`
   - implementation commit: `ad0657a137d6996e563a7c11c2d11a2b9037d80e`
2. Deterministic W2 fixture:
   - `parallel/PYLAUNCH/tests/fixtures/alpha_v3_w2_zero_click_identity_acquisition.json`
   - commit: `73548ba7b66eae39eb827a939f8cb4b28f6273df`
3. Module-owned focused regression:
   - `parallel/PYLAUNCH/tests/test_zero_click_identity_acquisition_w2.py`
   - commit: `1deabd06bbf52d6d4a3153be3453eed6ed704029`

## Integration contract

Primary API:

```python
acquire_zero_click_p1_head(
    world_sha256=...,
    p1_lifecycle=...,
    canvas=...,
    hud_identity_candidates=...,
    scene_head_candidates=...,
) -> AcquisitionResult
```

`AcquisitionResult` exposes the required machine-readable handoff:

- `ok: bool`
- `confidence: float`
- `reason: str`
- `character_type: int | None`
- `p1_generation: int | None`
- `head_seed: HeadSeed | None`
- `ambiguity_margin: float | None`
- `evidence_sources: tuple[str, ...]`

`as_dict()` additionally preserves the safety contract: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

### Required evidence chain

A seed is emitted only when all of the following are true:

1. exact World identity is `921031`;
2. P1 lifecycle is active, has a positive runtime character `type`, and has a positive lifecycle `generation`;
3. the captured canvas has bounded dimensions plus a valid SHA-256 screenshot digest (`screenshot_digest()` is provided);
4. one HUD/portrait identity candidate is safely unique and agrees with runtime P1 character type;
5. one scene-P1/head candidate is safely unique, is explicitly actor `P1`, agrees with the same character type and lifecycle generation, and is inside canvas bounds;
6. HUD and scene identity keys cannot conflict;
7. read-only visual evidence includes `canvas` + `hud` and either verified `sprite` / `tile` / `render-object` evidence or an explicit positive bounded coarse-prior consistency signal.

The module never treats world X/Y/Z as screen coordinates and does not infer a projection.

### Fail-closed reasons

Representative stable reasons include:

- `WORLD_MISMATCH`
- `P1_LIFECYCLE_MISSING`
- `P1_NOT_ACTIVE`
- `P1_IDENTITY_UNRESOLVED`
- `P1_GENERATION_UNRESOLVED`
- `CANVAS_EVIDENCE_MISSING` / `CANVAS_EVIDENCE_INVALID`
- `HUD_IDENTITY_MISSING` / `HUD_IDENTITY_LOW_CONFIDENCE` / `HUD_IDENTITY_AMBIGUOUS`
- `HUD_PORTRAIT_REJECTED`
- `SCENE_P1_MISSING` / `NO_SAFE_HEAD_SEED` / `AMBIGUOUS_SCENE_P1_HEAD`
- `REJECTED_WRONG_ACTOR`
- `SCENE_IDENTITY_CONFLICT`
- `STALE_P1_GENERATION`
- `SCENE_COARSE_PRIOR_CONFLICT`
- `HUD_SCENE_IDENTITY_CONFLICT`
- `VISUAL_EVIDENCE_INCOMPLETE`
- `SCENE_AUTHORITY_UNVERIFIED`
- `HEAD_SEED_OUT_OF_BOUNDS`

Every failure returns `head_seed=None`; no candidate is silently selected on ambiguity.

## Focused self-check

Only W2-owned tests were run; no historical PASS suite was rerun.

```text
python -m pytest -q parallel/PYLAUNCH/tests/test_zero_click_identity_acquisition_w2.py
......                                                                   [100%]
6 passed in 0.04s

python -m py_compile parallel/PYLAUNCH/wof_launcher/zero_click_identity_acquisition.py
PASS
```

Covered cases: safe unique acquisition, exact-World mismatch, wrong HUD/portrait identity, ambiguous scene/head candidates, wrong actor, stale lifecycle generation, out-of-bounds head seed, scene-authority rejection, screenshot digest binding, and no input/memory-write primitives.

## W1 handoff

W1 owns integration and should consume W2 before arming fallback click:

1. Reuse the existing exact-World/runtime lifecycle state for `p1_lifecycle` (`type`, `generation`, active state).
2. Reuse the current canvas PNG and call `screenshot_digest(png_bytes)`; pass digest plus backing canvas dimensions.
3. Convert the existing HUD/portrait identity evidence to `hud_identity_candidates`. `characterType` must come from a real HUD/portrait/tile/render identity signal; do **not** manufacture it merely by copying the runtime P1 type, otherwise the wrong-portrait gate becomes circular.
4. Convert W1's existing scene auto-seed evidence to `scene_head_candidates`, including `actor=P1`, `characterType`, `p1Generation`, bounded `center`/`box`, normalized confidence, evidence sources, and the coarse-prior consistency result when available.
5. Call `acquire_zero_click_p1_head(...)`. Only `ok=True` / `reason=SAFE_UNIQUE` may be consumed as an automatic head seed. Any other `reason` remains unbound and may proceed to W1's already-owned one-click fallback policy.
6. Lifecycle/runtime/layout invalidation remains W1 authority; W2 seeds are generation-bound so a changed P1 generation must be reacquired rather than reused.

Important current integration note: W1's concurrent `auto_seed_candidate()` already supplies a scene center plus score/margin/candidate count and runtime P1 type, but its generic HUD palette crop by itself is **not semantic character/portrait identity evidence**. W1 should use an existing proven HUD/tile/render identity signal when available; otherwise W2 correctly fails closed instead of falsely certifying the portrait.

## Write-boundary audit

W2 did not modify:

- `parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py`
- `parallel/RENDER_AUTHORITY_V3/measurement_runner.py`
- `parallel/OPTOOLKIT/owner_zh_cn.py`
- package manifests/generators
- V3 umbrella RESULT or V3 umbrella claims

W2 also does not capture through CDP, inject browser/game input, write RAM, or access ROM/tile data mutably.

**Verdict: W2 SUBCOMPLETE — module + deterministic fixture + focused self-check complete; hand back to W1 for integration/package/umbrella closeout.**
