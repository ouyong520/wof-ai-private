# Alpha V3 W6 — Independent Semantic Evidence Producer SUBRESULT

Status: **SUBCOMPLETE — standalone producer + deterministic fixture/tests complete; source discovery and umbrella integration intentionally not claimed**

## Scope / authority

- Dispatch: `parallel/PM/ALPHA_V1_RENDER_AUTHORITY_V3_FINAL_ZERO_CLICK_PRODUCER_PARALLEL_ACCELERATION_DISPATCH.md`
- W6 dedup key: `alpha.v1.render-authority-v3.w6-semantic-evidence-producer`
- W6 stage: `ALPHA_V1_RENDER_AUTHORITY_V3_W6_SEMANTIC_EVIDENCE_PRODUCER`
- W6 claim token: `b80a5241753db7ea56a2afca4fbcf159`
- Start commit: `d902a5e0ce082b2267cd44f2163f830f7cb130d2`
- W6 does not discover semantic authority. W4 owns source discovery. W6 accepts only already-proven observations and translates them into the explicit V3/W2 envelope.

## Durable outputs

1. Standalone producer module:
   - `parallel/PYLAUNCH/wof_launcher/semantic_evidence_producer.py`
   - final implementation commit: `89d91d7cde439726e8a0c6b9499ccc885599d2fa`
   - final blob: `505ff1122e9c45e3d12d0fc187f00a92a8067288`
2. Deterministic fixture:
   - `parallel/PYLAUNCH/tests/fixtures/alpha_v3_w6_semantic_evidence_producer.json`
   - final fixture commit: `91ad89bc47904c862ff0f8908e59abc5ca04bd85`
   - final blob: `5d7e104949202c954d6b4c1bcb1de1c1b9656969`
3. Focused producer regression:
   - `parallel/PYLAUNCH/tests/test_semantic_evidence_producer_w6.py`
   - final test commit: `ba6df097307180e31f2b87bfe33c19d0f104a117`
   - final blob: `bfdb25b9389c266d0b0c332a5fddc0dbc7589982`

## Integration-ready API

```python
produce_p1_zero_click_evidence(
    world_sha256=...,
    authority_key=...,
    runtime_epoch=...,
    layout_key=...,
    p1_lifecycle=...,
    canvas=...,
    semantic_identity_observations=...,
    scene_head_observations=...,
) -> ProducerResult
```

On `ok=True`, `ProducerResult.envelope` is the value the umbrella integration may place at runtime key `p1ZeroClickEvidence`.

The envelope schema is exactly:

`alpha-v3-runtime-p1-zero-click-evidence-v1`

and contains the existing W2 consumer inputs:

- `hudIdentityCandidates`
- `sceneHeadCandidates`
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`

It additionally carries producer/readiness binding metadata: exact World, `authorityKey`, `runtimeEpoch`, `layoutKey`, `p1Generation`, `p1Type`, canvas digest, producer schema/verdict, and an explicit root `identityAuthority` description.

## Non-circular semantic identity contract

A HUD/portrait/tile/render semantic observation is accepted only when all of the following are explicit:

1. it is marked already proven;
2. its authority kind is one of the semantic allow-list (`hud-semantic`, `portrait-semantic`, `tile-semantic`, `render-semantic`);
3. its identity derivation is semantic and matches that authority kind;
4. `independentOfRuntimeType=true`;
5. it independently provides `characterType` and `identityKey` plus a concrete authority/provenance id;
6. it is bound to the current exact World, authority key, runtime epoch, layout key, and P1 lifecycle generation;
7. confidence and ambiguity margin pass the strict producer gate;
8. the independently derived semantic character type agrees with current runtime P1 type.

The runtime P1 type is therefore used only as a cross-check. It is never copied to manufacture HUD identity.

Generic palette/color authority is absent from the semantic allow-list and is explicitly rejected. A `runtime-p1-type`, lifecycle-type, palette, or color derivation cannot create an envelope.

The root envelope records the anti-circular readiness facts:

- `identityAuthority.kind = semantic`
- `independentOfRuntimeP1Type = true`
- `derivedFromRuntimeP1Type = false`
- `genericHudPalette = false`

## Scene P1/head contract

The scene observation must already be proven and must:

- be `actor=P1`;
- independently agree with the semantic `characterType` and `identityKey`;
- be bound to the same exact World / authority key / runtime epoch / layout / P1 generation;
- be bound to the current canvas digest;
- provide bounded `center` and `box` geometry;
- carry confidence and ambiguity margin;
- be backed by verified `sprite`, `tile`, or `render-object` head authority, or by an explicitly proven positive coarse-prior consistency signal.

W6 does not scan the canvas, infer projection, inspect generic HUD colors, discover sprite/tile authority, or select among competing observations. Multiple semantic rows or multiple scene rows are treated as ambiguity and fail closed.

## Fail-closed behavior

Any mismatch, ambiguity, staleness, circular derivation, or incomplete provenance returns:

`ProducerResult(ok=False, ..., envelope=None)`

Representative reasons covered by the producer/tests include:

- `WORLD_MISMATCH`
- `AUTHORITY_KEY_MISSING`
- `CIRCULAR_RUNTIME_TYPE_REJECTED`
- `CIRCULAR_OR_NONSEMANTIC_DERIVATION_REJECTED`
- `GENERIC_PALETTE_REJECTED`
- `SEMANTIC_IDENTITY_AMBIGUOUS`
- `SEMANTIC_IDENTITY_STALE`
- `SEMANTIC_RUNTIME_TYPE_CONFLICT`
- `SCENE_HEAD_AMBIGUOUS`
- `SCENE_HEAD_STALE`
- `SEMANTIC_SCENE_IDENTITY_CONFLICT`
- `SCENE_CANVAS_STALE`
- `SCENE_HEAD_GEOMETRY_INVALID`
- `SCENE_AUTHORITY_UNVERIFIED`

Thus runtime/lifecycle/layout/authority/canvas changes revoke old evidence instead of permitting reuse.

## W2 compatibility proof

The safe-unique deterministic fixture produces a W6 envelope and immediately feeds its `hudIdentityCandidates` / `sceneHeadCandidates` into the current W2 adjudicator:

`parallel/PYLAUNCH/wof_launcher/zero_click_identity_acquisition.py`

W2 source blob used for the focused check: `0c1cead751a7f6ee949c84eb61ab342062df9a57`.

The current W2 adjudicator returns `ok=True`, `reason=SAFE_UNIQUE`, a generation-bound head seed, and evidence sources `{canvas,hud,sprite}`. This proves the W6 output shape is consumable by the existing W2 contract without modifying W2.

## Focused self-check

Only W6-owned focused tests and syntax compilation were run; historical regression suites were not rerun.

```text
python -m pytest -q parallel/PYLAUNCH/tests/test_semantic_evidence_producer_w6.py
........                                                                 [100%]
8 passed in 0.07s

python -m py_compile parallel/PYLAUNCH/wof_launcher/semantic_evidence_producer.py
PASS
```

Covered behavior includes:

- safe unique producer -> current W2 `SAFE_UNIQUE`;
- runtime P1 type copying rejected;
- generic HUD palette rejected;
- semantic and scene ambiguity rejected;
- authority/runtime/lifecycle/layout/canvas staleness revoked;
- semantic/scene identity and runtime-type conflicts rejected;
- multiple candidates never ranked or guessed;
- no capture, UI, input injection, RAM-write, or ROM/game-content primitive in the producer.

## Main-worker handoff

After W4 identifies the actual reusable semantic authority, the V3 umbrella/main worker should perform only the narrow adapter step:

1. normalize W4's already-proven identity observation into one supported semantic authority kind without inventing identity fields;
2. normalize the already-proven scene P1/head observation with the same authority/runtime/layout/lifecycle/canvas bindings;
3. call `produce_p1_zero_click_evidence(...)`;
4. only when `result.ok is True`, publish `result.envelope` as `p1ZeroClickEvidence` for the existing W2 consumer;
5. when W6 returns any failure, publish no semantic evidence envelope and preserve W2's fail-closed/fallback behavior;
6. integration selection, package pins, final W5 readiness, final regression, immutable package, V3 RESULT and umbrella claim closeout remain the main worker's authority.

## Write-boundary audit

W6 did **not** modify:

- `parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py`
- `parallel/RENDER_AUTHORITY_V3/measurement_runner.py`
- Owner UI / `parallel/OPTOOLKIT/owner_zh_cn.py`
- package manifests or package generators
- V3 umbrella RESULT or umbrella canonical/stage claims
- W4 source discovery work
- W5 readiness tests/fixtures/docs

No ROM/game content was committed.

**Verdict: W6 SUBCOMPLETE — standalone producer, deterministic fixture, W2-compatible focused proof, and durable handoff are complete.**
