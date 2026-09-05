# Alpha V1 — Canonical Render Anchor P5/P8 Continuation Dispatch

Repository: `ouyong520/wof-ai-private`

This dispatch preserves the already ACTIVE P5 ownership and adds exactly one new worker, P8. It does not re-claim, replace, recover, or supersede P5.

## Current state

- P5 `ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING` remains ACTIVE under its existing dedup-v2 claim and continues independently.
- P6 enemy canonical anchor labels is COMPLETE / integration-ready.
- P7 player danger canonical anchor is COMPLETE / integration-ready.
- W3 renderer/object source qualification remains under its existing ACTIVE authority; no new worker may steal or duplicate that proof task.

## New P8 objective

Create one canonical product-plan composition layer for the already-complete P6 + P7 planners so later HUD/runtime integration receives one fail-closed product plan instead of duplicating glue.

P8 must reuse, not rewrite:
- `product/alpha/wof_alpha_enemy_target_labels.js`
- `product/alpha/wof_alpha_player_head_warning.js`

P8 must not modify:
- P5 launcher/HUD bridge files while P5 is ACTIVE;
- W3 capture/producer/claim files;
- `alpha-live`;
- fixed-draw first-gate behavior;
- threat-generation policy or target semantics.

Canonical mode remains fail-closed. Missing/unproven/SUPPRESSED/stale/ambiguous/generation-mismatched/authority-epoch-mismatched anchors must result in no corresponding draw intent. No screenshot/template, world/camera/Y-model, click, calibration, nearest-sprite, or guessed fallback is allowed.

## Cadence

Implementation first. Only minimum parse/load and two narrow composition fixtures are expected. No broad regression, Fresh QA, second-opinion audit, Owner test, or real-WOF run in this dispatch.

## Reporting

P5 continues reporting to its original result paths. P8 reports only to the exact result paths declared in its start prompt and immutable manifest. Terminal reporting follows `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.
