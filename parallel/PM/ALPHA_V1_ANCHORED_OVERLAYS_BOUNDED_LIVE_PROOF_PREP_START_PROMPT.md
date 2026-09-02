# Alpha V1 Anchored Overlays — Bounded Dynamic Live Proof Prep

stageId: `ALPHA_V1_ANCHORED_OVERLAYS_BOUNDED_LIVE_PROOF_PREP_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.anchored-overlays.bounded-dynamic-live-proof-prep`
dedupMode: `exclusive`

Priority: **P0/P1 Alpha V1 release-gate preparation**

## Purpose

Alpha V1 now requires both:

1. player-head danger warning;
2. enemy-head current-target label (`1P / 2P / 3P`).

Repository QA for enemy target labels Fresh QA V3 is PASS, but real Browser/WOF projection and visible non-drift remain unproven. Existing HUDANCHOR reverse evidence already narrows the remaining player projection work to one bounded uninterrupted Browser proof session.

This stage prepares/reconciles the **single bounded dynamic live-proof contract** needed after repository-side product integration gates are ready. It must maximize reuse of existing HUDANCHOR proof machinery and avoid asking Owner for broad manual debugging.

This is **repository-only preparation**. Do not launch Browser/WOF.

## Start / canonical dedup v2

Before substantive work, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims, recent Alpha/HUDANCHOR/Acceptance commits, and at minimum:

- `parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md`;
- `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md`;
- `parallel/HUDANCHOR_PROOF/OPERATOR_STEPS.md` and its current proof schema/tooling;
- latest HUDANCHOR bounds/confidence/stress results;
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3/RESULT.md`;
- current `product/alpha/wof_alpha_enemy_head_projection.json`;
- current target-label helper/HUD/worker/loader interfaces as read-only facts;
- `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1.json` and its RESULT if COMPLETE;
- `parallel/PM/STAGE_CLAIMS/ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V2.json` and current acceptance policy.

If equivalent current live-proof preparation already COMPLETE on the same product requirement, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.v1.anchored-overlays.bounded-dynamic-live-proof-prep.json`

with a fresh unpredictable `claimToken`. Re-read current `main` and exact canonical file and verify ownership before creating:

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_ANCHORED_OVERLAYS_BOUNDED_LIVE_PROOF_PREP_V1.json`

Ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Required analysis / preparation

Produce a current-head, fail-closed proof plan that answers all of the following without inventing projection constants:

1. Which facts from the existing HUDANCHOR one-session proof can be reused for player-head and enemy-head projection?
2. Which enemy-head facts remain distinct (enemy world reference, head/clearance offset, type-specific offset if needed)?
3. Can one uninterrupted Browser session prove the common camera/X transform, Y/Z model, WebGL drawing-buffer mapping, resize/fullscreen recovery, and both anchored surfaces?
4. What exact additional observations are minimally required for enemy-head labels beyond the existing player proof?
5. How will the live run prove no obvious drift during:
   - fast left/right movement;
   - depth/lane movement;
   - jump ascent/apex/descent/landing;
   - rapid forward movement with stage/camera scrolling;
   - simultaneous player + camera movement;
   - enemy movement while labels are visible;
   - P1/P2/P3 retarget;
   - multiple supported enemies where practical;
   - resize/fullscreen/drawing-buffer remap?
6. Define objective/fail-closed evidence for stale identity, runtime/projection/drawing-buffer epoch mismatch, non-finite/out-of-bounds projection and confidence loss.
7. Define the exact terminal evidence schema/verdicts. Synthetic/repository evidence must never satisfy the live proof.
8. Bound Owner actions to normal gameplay/proof interactions only; no manual address selection, coordinate transcription, JS copying or arithmetic.
9. If Player-Head Integration is still ACTIVE or its final blobs are not yet stable, prepare the protocol but mark product-blob binding as pending; do not guess or block merely because another implementation stage is legitimately in progress.
10. Identify the exact minimal follow-up stage needed if current proof tooling cannot observe both surfaces in one run. Do not implement that follow-up here unless it is documentation/schema-only within this lane.

## Acceptance semantics

The future live proof must be able to distinguish at least:

- `IMPLEMENTATION_READY` / bounded live projection facts proven;
- `FAILED_COMPONENT:<component>`;
- visible/repeatable overlay drift => P0 fail;
- stale/incorrect target/identity => P0 fail;
- uncertainty correctly hides/falls back => acceptable fail-closed behavior.

Repository prep PASS does **not** mean Browser/WOF live proof has passed.

## Write boundary

Write only:

- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/**`;
- this stage/canonical claim updates.

Do not modify `product/alpha/**`, HUDANCHOR production/reverse implementation, Transport, PYLAUNCH, Recorder, Unified, OneClick or Acceptance implementation.

No Browser/WOF launch.

## Stop

PASS:

`PASS — ALPHA V1 ANCHORED OVERLAYS BOUNDED LIVE PROOF PREP — ONE-SESSION DYNAMIC PROOF CONTRACT READY`

BLOCKED:

`BLOCKED — ALPHA V1 ANCHORED OVERLAYS BOUNDED LIVE PROOF PREP — <precise blocker>`

Owner action during this stage: **NO**.
