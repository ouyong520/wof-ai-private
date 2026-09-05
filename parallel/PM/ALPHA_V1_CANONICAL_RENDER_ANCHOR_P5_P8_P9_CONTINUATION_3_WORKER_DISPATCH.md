# Alpha V1 — Canonical Render Anchor P5/P8/P9 Continuation 3-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

This dispatch uses exactly three concurrent product workstreams without duplicating ownership:

1. **P5 — existing ACTIVE workstream**: continue its already-owned P1 canonical render-anchor -> maintained production HUD wiring. This dispatch does not create, replace, recover, or mutate P5 ownership.
2. **P8 — new workstream**: compose the already-COMPLETE P6 enemy target-label canonical planner and P7 player-danger canonical planner into one fail-closed canonical overlay product plan.
3. **P9 — new workstream**: define and implement a strict canonical anchor runtime envelope for transporting already-resolved canonical READY/SUPPRESSED actor anchors plus generation/authority epochs into product-side consumers without legacy position fallback.

## Current authority facts

- P5 stage `ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING` is ACTIVE under dedup key `alpha.v1.product-takeover.p1-canonical-render-anchor-wiring-v1` and must continue under the same claim token.
- P6 `ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS` is COMPLETE / integration-ready.
- P7 `ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR` is COMPLETE / integration-ready.
- W3 `alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2` remains ACTIVE and is the only authority allowed to qualify the exact displayed-frame renderer/object source. P8/P9 must not edit W3 capture/producer/claim files or claim that source is proven.

## Shared fail-closed product rule

Canonical product mode may consume only explicit canonical `wof-render-object-anchor-v1` READY/SUPPRESSED outputs bound to exact World/runtime/renderer authority and current actor generation. Any missing, stale, unsafe, ambiguous, unproven, generation-mismatched, authority-mismatched, runtime-epoch-mismatched, renderer-epoch-mismatched, or invalid drawing-buffer input must suppress the affected draw intent.

Forbidden fallback in P8/P9:
- screenshot/template tracking as steady-state position authority;
- world/camera projection;
- Y / Y-Z / Y+Z fitting;
- click calibration;
- nearest-sprite selection;
- relative geometry guesses;
- guessed constants.

Safety remains `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

## File ownership boundaries

### P5
P5 keeps the exact ownership/boundaries in its original start prompt. P8/P9 must not modify P5-owned launcher/HUD bridge files while P5 is ACTIVE.

### P8
Preferred new files only:
- `product/alpha/wof_alpha_canonical_overlay_plan.js`
- optional `product/alpha/canonical_overlay_plan_selfcheck.mjs`

P8 may read but should not rewrite P6/P7 implementation modules unless a minimal compatibility fix is unavoidable and proven not to overlap P5.

### P9
Preferred new files only:
- `product/alpha/wof_alpha_canonical_anchor_envelope.js`
- optional `product/alpha/canonical_anchor_envelope_selfcheck.mjs`

P9 is transport/contract normalization only. It must not draw, compose warnings/labels, or modify maintained HUD/launcher runtime files while P5 is ACTIVE.

## Cadence

Implementation first. Each new worker performs only parse/load plus the smallest fixture self-check needed to prevent obvious bad commits. No broad regression, Fresh QA, second-opinion audit, Owner test, real-WOF run, or alpha-live promotion in this dispatch.

## Reporting

P5 continues to its original RESULT paths. P8/P9 report to the exact RESULT.json/RESULT.md declared in their start prompts and immutable manifest. Terminal reporting follows `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.
