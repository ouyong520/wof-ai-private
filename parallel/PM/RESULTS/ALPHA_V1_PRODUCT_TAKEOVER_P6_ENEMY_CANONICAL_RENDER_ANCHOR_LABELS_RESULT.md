# Alpha V1 P6 — Enemy Canonical Render-Anchor Target Labels RESULT

State: **COMPLETE**

## Verdict

P6 now has an explicit canonical render-anchor planning path in `product/alpha/wof_alpha_enemy_target_labels.js`.

- `target7E == 0` -> `P1` -> `1P`
- `target7E == 4` -> `P2` -> `2P`
- `target7E == 8` -> `P3` -> `3P`
- canonical label position comes directly from a READY `wof-render-object-anchor-v1` native `384x224` enemy head anchor and is mapped into the maintained WebGL drawing-buffer content rect
- canonical mode validates actor, generation, authority key, runtime epoch, renderer epoch, native size, safety fields, anchor bounds, drawing-buffer freshness/epoch and optional anchor freshness
- missing, SUPPRESSED, stale, unsafe, ambiguous, explicitly unproven, actor/generation mismatched, epoch mismatched, invalid native-size or invalid drawing-buffer state suppresses the label
- canonical mode is separate from legacy `world/camera/Y/Z` projection and has no silent fallback into `projectMarkerNative` / legacy projection APIs

Legacy projection APIs remain unchanged for compatibility; they are not used by `buildCanonicalPlan`.

## Implementation commits

- `7b888503777e694fb851e31b8673ba523693966e` — canonical enemy anchor planner and fail-closed validation
- `5ac1e950e2a06587c82d3bb508368b5c1a690d9d` — focused canonical-anchor self-check fixture

## Changed files

- `product/alpha/wof_alpha_enemy_target_labels.js`
- `product/alpha/enemy_canonical_anchor_labels_selfcheck.mjs`

## Minimum self-check

PASS:

- `node --check product/alpha/wof_alpha_enemy_target_labels.js`
- `node product/alpha/enemy_canonical_anchor_labels_selfcheck.mjs`
  - READY canonical anchors produce `1P/2P/3P` and expected drawing-buffer coordinates
  - stale / SUPPRESSED / generation-mismatched / explicitly unproven anchors produce no labels
  - canonical mode does not access legacy projection fallback

No broad regression, Fresh QA, Owner acceptance, W3 source qualification, or live-WOF test was run, per dispatch.

## Product proof boundary

Classification: **IMPLEMENTATION_PROOF only**.

W3 renderer/object source qualification is still intentionally unproven in real WOF. This result does **not** claim machine-draw proof, Owner-visible proof, real-WOF PASS, or permission to move `alpha-live`.

Until W3 supplies a proven current anchor, canonical input remains SUPPRESSED/missing and the enemy label remains hidden.

## Integration readiness

`integrationReady: true`.

Later runtime glue can call `buildCanonicalPlan` with current per-slot actor/generation, canonical anchors, current `authorityKey/runtimeEpoch/rendererEpoch`, and maintained drawing-buffer state. No enemy geometry redesign is required; unproven or mismatched inputs fail closed.

Blocker: **none for P6 implementation scope**.

Next action: PM integrates this planner with the W3-qualified enemy anchor feed after renderer source qualification, preserving the no-fallback invariant.
