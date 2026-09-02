# Alpha V1 Enemy Target Head Labels — Fresh Independent QA V2 Result

Stage: `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2`

Status: **BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V2 — drawing-buffer runtime epoch is not cross-checked against the current projection epoch, so an internally-consistent stale drawing-buffer generation can still render a confident target label**

Owner action during this repository QA: **NO**.

## Canonical dedup v2 / ownership

- `dedupKey`: `alpha.enemy-target-head-labels.post-strict-type-fix-fresh-qa`
- claim-start HEAD: `7e27899a5c44d84e96ae27d89581fb89eee474ca`
- canonical create-only claim commit: `5cd73fc8c516b80dfc97cfc326b6e08486f71f02`
- canonical claim path: `parallel/PM/DEDUP_CLAIMS/alpha.enemy-target-head-labels.post-strict-type-fix-fresh-qa.json`
- stage create-only claim commit: `03ca03ca165eb76386779c9a1b8e8ca838adc0c2`
- canonical claim was re-read after creation and again immediately before this result; schema / key / stage / prompt metadata / `ACTIVE` state and the exact private `claimToken` all matched this worker.
- no equivalent PASS/COMPLETE existed on the strict-fix product blobs before claim acquisition.

The canonical claim was acquired and verified before any QA task execution, as required by dedup v2.

## Exact audited product blobs

Pinned at QA execution and re-read immediately before finalization:

| Path | Blob |
|---|---|
| `product/alpha/wof_alpha_enemy_target_labels.js` | `50dfd831b21ea79ed06e34a1a7fb559aee011b6c` |
| `product/alpha/enemy_target_labels_regression.mjs` | `449dd7cbe3281dc3cdf6a52e3324e19a4707de70` |
| `product/alpha/wof_alpha_enemy_head_projection.json` | `8de57739818503a0e14702d2fa0bb4eba58228d2` |
| `product/alpha/wof_alpha_real_worker.js` | `924d02eb575d1031b168b3bb7450c34107447c85` |
| `product/alpha/wof_alpha_hud.js` | `b6f9cbf23ec1c00fe969aa2a2b59ad5e0d5433f4` |
| `product/alpha/wof_alpha_loader.js` | `b1d2bd5cc3f5e4e7a3bed084d6d35ea71489717b` |

Final pre-result HEAD before this RESULT write: `844de5783a58e0be56655e8d40dae40884956559`. No audited product blob drifted during this QA.

## Strict raw target-type fix — independently verified

The original V1 blocker is fixed on the current helper blob.

Fresh independent attacks confirm:

- primitive numeric `0 / 4 / 8` map exactly to `P1 / P2 / P3` and render `1P / 2P / 3P` under a synthetic valid projection;
- strings `"0" / "4" / "8"` fail closed;
- boxed numbers, ordinary/coercible objects, booleans, arrays, `null`, `undefined`, `NaN`, `Infinity`, `-Infinity`, fractional values, bigint, symbol and negative zero fail closed;
- unsupported numeric raw targets fail closed;
- raw-target / normalized-target disagreement fails closed.

Therefore this V2 result does **not** reopen the numeric-string coercion defect that blocked V1.

## Independent fixture / execution

Added:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2/independent_enemy_target_labels_qa_v2.mjs`
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2/independent_qa_result.json`

Evidence commits:

- fixture: `6cc7edd70fa36a3acb233f9e3cf6f8f3cf5a94f7`
- durable execution output: `844de5783a58e0be56655e8d40dae40884956559`

The execution environment had Node but no usable native private checkout: `git ls-remote https://github.com/ouyong520/wof-ai-private.git HEAD` failed with `Could not resolve host: github.com`. The helper and projection profile were therefore reconstructed from the claimed GitHub contents and verified byte-for-byte by Git blob hash before execution:

- helper -> `50dfd831b21ea79ed06e34a1a7fb559aee011b6c`
- projection profile -> `8de57739818503a0e14702d2fa0bb4eba58228d2`

`node --check` passed for the exact helper and independent fixture.

Independent matrix result:

- schema: `wof-alpha-enemy-target-head-labels-independent-repository-qa-v2`
- evidence class: `SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_PROJECTION_PROOF`
- tests: **19**
- PASS: **18**
- FAIL: **1**

The implementation-owned current regression source was re-read and still contains the strict malformed-target regression on blob `449dd7cb...`. Its implementation-stage exact-blob evidence is 13/13 PASS, but it was not falsely presented as freshly re-executed here because the full private checkout/dependency set was unavailable. It is supporting evidence only, not the acceptance basis for this result.

## Blocking independent finding — cross-generation drawing-buffer epoch gap

The current helper validates a drawing-buffer state by checking that `drawingBufferState.epoch` and `drawingBufferState.projectionEpoch` agree **with each other**. It does not require either value to equal the current `projection.epoch` used by the same `buildPlan()` call.

The independent fixture supplies:

- marker `epoch = runtime-a`, `projectionEpoch = runtime-a`;
- projection `epoch = runtime-a`;
- drawing-buffer `epoch = runtime-old`, `projectionEpoch = runtime-old`.

The stale drawing-buffer generation is internally self-consistent, so current `validateDrawingBuffer()` accepts it. `projectMarkerNative()` separately accepts the marker against `projection.epoch`. The plan then emits one confident label instead of suppressing the cross-generation mixture.

Observed assertion:

`stale drawing-buffer runtime epoch must not render against current projection` — expected `0` labels, observed `1`.

This violates the V2 start prompt's explicit fail-closed requirement for runtime/drawing-buffer epoch mismatch. An old drawing-buffer mapping must not be combinable with a current projection simply because its two local epoch fields match each other.

### Current HUD construction does not erase the helper defect

Current HUD source normally calls `drawingBufferState(now, projection?.epoch)` and stamps both drawing-buffer epoch fields from that projection epoch. That means the ordinary current HUD path is constructed to avoid this mismatch.

However, the V2 QA requirement is explicitly fail-closed on epoch mismatch. The helper is the final projection/plan validation layer and currently accepts an independently supplied stale generation when its local fields are mutually consistent. Repository QA therefore cannot PASS this mandated adversarial condition merely because today's HUD producer usually constructs matching fields.

A narrow follow-up should require the drawing-buffer generation used by `buildPlan()` to match the accepted current projection/runtime epoch, and add a regression for an internally-consistent old drawing-buffer epoch paired with a new projection epoch.

## Remaining independent matrix — PASS

The other 18 independent checks are green:

- exact `1P / 2P / 3P` mapping;
- strict malformed raw-target rejection;
- unsupported raw targets and normalized-target inconsistency;
- same-enemy `P1 -> P2 -> P3` immediate retarget with no stale hold;
- simultaneous enemies remain independent;
- disappearance and same-slot replacement do not inherit old labels;
- marker/projection `300 ms` boundary accepted and `301 ms` suppressed;
- stale/malformed drawing-buffer state suppressed;
- marker/projection epoch mismatch suppressed;
- drawing-buffer **internal** epoch mismatch suppressed;
- invalid confidence and non-finite XYZ/projection/camera suppressed;
- unsupported enemy type and invalid slot suppressed;
- near-edge valid anchor clamps only the compact label rect;
- out-of-bounds anchor is suppressed before clamp;
- resize/fullscreen remap changes mapping key and recomputes coordinates;
- repository `UNPROVEN` projection profile remains silent;
- malformed proof/profile facts fail closed.

## Warning channel / HUD / GL / safety compatibility

Fresh current-source inspection confirms the surrounding invariants remain intact:

- HUD accepts messages only after schema/session/transport match;
- `kind === 'state'` alone refreshes danger-warning `lastMsg / lastRx`;
- `enemy-target-markers` updates only marker state and cannot authorize or refresh danger-warning freshness;
- `diag` clears both warning and marker state;
- startup and disabled diagnostics remain present;
- warning freshness remains `1500 ms`, marker freshness remains separate at `300 ms`;
- current label path remains `holdMs: 0`, `smoothing: false`;
- WebGL label/HUD drawing retains save/draw/`finally` restore behavior through `snapGL()` / `restoreGL()`;
- worker safety declaration remains exact: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`, `blobRewrite=false`, `gamePostMessageControl=false`, `heapWrites=false`, `assistMode=false`;
- marker publication remains on the existing authority envelope and same gated detector tick; normal warning heartbeat remains `>=250 ms`, marker follow heartbeat remains `>=50 ms`.

No Browser/WOF process was launched by this QA.

## Projection live-proof boundary

Current repository profile remains:

- `verdict: UNPROVEN`
- `status: FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`

So current production live target-head labels remain silent until bounded real projection/enemy-head proof exists. Synthetic repository evidence here is **not** Browser/WOF projection proof.

The required bounded live proof remains a separate downstream gate even after this repository blocker is fixed.

## Formal current-blob classification

The current Formal Real-Adapter result remains:

`PASS — ALPHA FORMAL REAL-ADAPTER CURRENT-BLOB REVALIDATION — FRESHNESS GATE CURRENT`.

Fresh exact-blob comparison shows all Formal authority/freshness-sensitive pins named by that result remain unchanged:

- worker `924d02eb...`
- HUD `b6f9cbf2...`
- bootstrap `5aed15ff...`
- loader `b1d2bd5c...`
- core `267a4419...`
- real adapter `1a5c6a25...`

The strict target-type implementation changed only the decorative target-label helper and its implementation regression. It did not change those Formal warning-authority/lifecycle blobs. Therefore the strict helper-only fix does **not** mechanically invalidate the existing Formal current-blob PASS.

This V2 BLOCKED verdict is a Head Labels fail-closed release blocker, not a reclassification of Formal warning authority.

## Scope compliance

This fresh QA modified no `product/alpha/**` file and no Formal/HUDANCHOR/Unified/PYLAUNCH/Safe Transport/OneClick/Acceptance implementation. Writes are limited to this V2 QA evidence/result and its own stage/canonical claim records.

No Browser/WOF was launched.

## Stop condition

**BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V2 — current helper accepts an internally-consistent stale drawing-buffer runtime epoch against a newer current projection epoch and can render a confident label instead of failing closed.**
