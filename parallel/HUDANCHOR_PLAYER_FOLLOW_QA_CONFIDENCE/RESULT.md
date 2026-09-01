# HUDANCHOR Player-Follow Confidence Fail-Closed Fresh QA Result

Stage: `HUDANCHOR_PLAYER_FOLLOW_CONFIDENCE_FAILCLOSED_QA_V1`

Status: **PASS — HUDANCHOR CONFIDENCE FAIL-CLOSED FRESH QA — READY FOR LONG-STRESS V2**

## Scope / authority

This was an independent repository-side QA of the completed confidence fail-closed fix. No HUD implementation file was modified by this stage.

Allowed writes were limited to:

- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA_CONFIDENCE/**`
- this stage's claim under `parallel/PM/STAGE_CLAIMS/**`

This is synthetic/repository QA only. It is **not** real Browser/WOF projection proof and does not claim any guessed Browser projection constants.

## Current SUT verified before completion

Current `parallel/HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference.js` blob after the QA artifacts were written:

- `e36e80fdad7bcf7f73485f9093aa9014428c86b1`

Fresh QA executable:

- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA_CONFIDENCE/qa_confidence_matrix.js`
- blob `3958316d4a47189de63158bbb180c6b9109cb0b8`
- commit `a1a414f6e17ac4eea221d730b749a5fd64274631`

Attack matrix artifact:

- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA_CONFIDENCE/matrix.json`
- commit `d05f69873c1a291c96866b9240da2d689eb21e3c`

Execution environment: Node `v22.16.0`.

The current SUT, synthetic fixture, and unchanged regression files were reconstructed from their committed Git blobs and the local Git blob hashes were checked before execution.

## Fresh adversarial QA

Fresh matrix result:

```json
{"status":"PASS","stageId":"HUDANCHOR_PLAYER_FOLLOW_CONFIDENCE_FAILCLOSED_QA_V1","passed":12,"total":12,"invalidValuesPerSurface":8,"sutBlob":"e36e80fdad7bcf7f73485f9093aa9014428c86b1","fixtureBlob":"79e42e675d371ec91715116227fecf0ed3c27d97","fixture":"FRESH_SYNTHETIC_CONFIDENCE_QA_NOT_BROWSER_PROOF"}
```

The fresh matrix independently attacked all confidence surfaces participating in anchor authority:

- player confidence;
- projection confidence;
- drawing-buffer/mapping confidence;
- projected-result confidence.

For each authority surface, the matrix injected:

- `NaN`;
- `+Infinity`;
- `-Infinity`;
- explicit `undefined`;
- `null`;
- string;
- object;
- array.

All invalid values failed closed. No invalid/non-finite confidence authorized anchored rendering.

## Required behavioral attacks

### Threshold / domain boundaries

Valid finite confidence values at `0`, `Number.EPSILON`, `0.5`, `1 - Number.EPSILON`, and `1` remained anchored under the existing contract.

Values immediately outside the admissible domain (`-Number.EPSILON`, `1 + Number.EPSILON`) failed closed on all four confidence surfaces.

No new confidence threshold was invented by QA.

### Stale high-confidence after invalid transition

A valid high-confidence anchored frame (`0.99`) was followed by invalid projection confidence and then a valid low-confidence frame (`0.05`).

Observed:

- invalid frame immediately used fixed HUD;
- player-follow state was cleared;
- recovery reset smoothing;
- recovered anchor confidence was the new `0.05`, not stale `0.99`;
- the old follow coordinate was not reused.

### Retarget P1 -> P2 during invalid confidence

With hold enabled, P1 was first validly anchored. The target then changed to P2 while projection confidence was an invalid string.

Observed:

- P1 was immediately invalidated with `RETARGET`;
- no P1 cue remained;
- P2 used fixed HUD with `INVALID_PROJECTION_CONFIDENCE`;
- neither P1 nor P2 retained stale follow state.

### Body coordinates valid while confidence invalid

The matrix supplied finite, in-bounds body/head coordinates while projection or projected confidence was invalid.

Observed:

- invalid projection confidence failed before projection authority could be used;
- invalid projected confidence failed with `INVALID_PROJECTED_CONFIDENCE`;
- finite body coordinates never overrode confidence invalidity.

### Invalid -> valid recovery / valid -> invalid immediate fallback

Both directions were exercised.

Observed:

- valid -> invalid switched immediately to fixed HUD and cleared follow state;
- invalid -> valid recovered anchored rendering with smoothing reset and current coordinates only.

## Bounds / edge-clamp interaction

The already-closed bounds bug remained closed.

Fresh QA proved all three required distinctions:

1. a valid near-edge anchor remains a real anchor and only the final warning rectangle clamps inside the drawing buffer;
2. the same near-edge geometry with invalid confidence does **not** produce an anchored/clamped cue and instead uses fixed HUD;
3. finite out-of-bounds anchor coordinates fail with `PROJECTION_OUT_OF_BOUNDS` and are never converted into an apparent attachment by rectangle clamping.

Therefore there is no edge-clamp masquerading as player attachment.

## Existing regressions re-run unchanged

### Confidence fail-closed regression

Blob:

- `1efcac65e9cc5598358c86e968a6b148d9e970a2`

Result:

```json
{"status":"PASS","passed":18,"total":18,"fixture":"SYNTHETIC_CONFIDENCE_FAILCLOSED_ONLY_NOT_BROWSER_PROOF"}
```

### Bounds regression

Blob:

- `d5798e3470625d440092aa00a05142157f99799b`

Result:

```json
{"status":"PASS","passed":8,"total":8,"fixture":"SYNTHETIC_BOUNDS_ONLY_NOT_BROWSER_PROOF"}
```

### Full player-follow synthetic regression

Blob:

- `b7d56a74ef520bccb47055bc59558da6dfcb6139`

Result:

```json
{"status":"PASS","passed":15,"total":15,"fixture":"SYNTHETIC_ONLY_NOT_BROWSER_PROOF"}
```

All three unchanged regressions executed with exit code `0` against SUT blob `e36e80fdad7bcf7f73485f9093aa9014428c86b1`.

## QA conclusion

Required invariants are satisfied on the current repository SUT:

- **no stale player-follow cue:** PASS;
- **no edge clamp masquerading as attachment:** PASS;
- **fixed HUD fail-closed whenever confidence is not finite/admissible:** PASS;
- **retarget invalidates the old player immediately:** PASS;
- **invalid -> valid recovery does not reuse stale smoothing state:** PASS;
- **existing bounds and 15-case synthetic behavior remains intact:** PASS.

No P1 blocker was found by this fresh QA.

## Downstream

Fresh player-follow long-stress V2 is unblocked and may start from current SUT blob `e36e80fdad7bcf7f73485f9093aa9014428c86b1` while retaining the same fail-closed invariants.

Real Browser/WOF projection and live native-to-drawing-buffer facts are still external proof requirements for eventual production anchoring, but they are not required to accept this confidence fail-closed repository QA.

Owner action: **NO**.

## Stop condition

**PASS — HUDANCHOR CONFIDENCE FAIL-CLOSED FRESH QA — READY FOR LONG-STRESS V2**
