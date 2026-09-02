# Alpha V1 Anchored Overlays — One-Session Dynamic Live Proof Contract

Stage: `ALPHA_V1_ANCHORED_OVERLAYS_BOUNDED_LIVE_PROOF_PREP_V1`

Evidence class: **PREPARATION ONLY — NOT BROWSER/WOF LIVE PROOF**

Prepared against current `main` observed at `ca12c344d6d67c079356deaa52d475d0880d3413`. All executable proof work must re-pin current product blobs before launch.

## 1. Goal and hard boundary

Prepare one tightly bounded Browser/WOF session that can close the remaining real projection/non-drift gate for both Alpha V1 anchored surfaces:

- player-head danger warning;
- enemy-head current-target label `1P / 2P / 3P`.

This document does not execute Browser/WOF, does not activate either unproved production profile, does not invent projection constants, and does not allow repository/synthetic QA to satisfy live proof.

Owner actions are limited to normal gameplay/proof interactions. No address selection, coordinate transcription, JS value copying, manual arithmetic, screenshot measurement, or broad debugging is permitted.

## 2. Current product binding

### Player-head danger warning

Current integration result is COMPLETE and pins the production path. The live proof must bind to these exact current blobs (or fail preflight if they drift):

- `product/alpha/wof_alpha_player_head_warning.js` — `43b54e361f9bffcc4be278549692d0fb229aae7e`;
- `product/alpha/wof_alpha_player_head_projection.json` — `bbed0618b348961580ca805bb93e4d17525f0142`;
- `product/alpha/player_head_warning_regression.mjs` — `80b927d8d8791e2e4a4b0e929899b11877a449f9`;
- `product/alpha/wof_alpha_real_worker.js` — integration result pin `b7f4506fc90b681ede059df5ad3316e665c6f15e`;
- `product/alpha/wof_alpha_hud.js` — integration result pin `50d944c451ac94b114e4f86441aeae8ad6b25c78`;
- `product/alpha/wof_alpha_loader.js` — integration result pin `66aee09fc2dd009c2f295d2092f3129548605efb`.

Current behavior to preserve in live proof:

- active-warning player spatial publication is bounded to 20 ms / 50 Hz;
- player and projection freshness are 80 ms in the helper;
- drawing-buffer freshness is 250 ms;
- `holdMs=0`, `smoothing=false`;
- invalid/stale/non-finite/out-of-bounds/cross-epoch/pre-retarget state must use fixed HUD, never an old player-head coordinate.

Current player production profile remains `status: UNPROVED` and `activation: DISABLED_UNTIL_BOUNDED_BROWSER_WOF_PROOF`.

### Enemy-head target labels

Fresh Independent QA V3 is PASS/COMPLETE. Bind to the current helper/profile blobs:

- `product/alpha/wof_alpha_enemy_target_labels.js` — `e6e1260559f735b85ce6f69e87803369f125b2de`;
- `product/alpha/wof_alpha_enemy_head_projection.json` — `8de57739818503a0e14702d2fa0bb4eba58228d2`.

Current behavior to preserve in live proof:

- strict primitive numeric `target7E` only: `0/4/8 -> P1/P2/P3 -> 1P/2P/3P`;
- marker max age 300 ms, projection max age 300 ms, drawing-buffer max age 1000 ms;
- marker/projection/drawing-buffer epochs must agree, including drawing-buffer `epoch === projectionEpoch === projection.epoch`;
- `holdMs=0`, `smoothing=false` in the product path;
- invalid target/type/slot/confidence/geometry/bounds/epoch suppresses the label rather than retaining an old label position.

Current enemy production profile remains `verdict: UNPROVEN` / `FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF` and has no `enemyHeadOffsetsByType` entries.

## 3. Reusable proof facts vs surface-specific facts

### Reuse from existing HUDANCHOR one-session proof

The existing `parallel/HUDANCHOR_PROOF/**` / `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md` contract already provides one-session evidence for facts shared by player and enemy anchoring:

1. native viewport `384 x 224`;
2. bounded camera scan identity in `0xFF0000 .. 0xFFBDFF`, step 2, `u16be`;
3. camera quality gate before calibration;
4. common horizontal formula `nativeX = worldX - camera + xBias`;
5. selection among exactly `Y-Z`, `Y+Z`, `Y`;
6. live direct-WebGL drawing-buffer/viewport mapping;
7. resize/fullscreen/DPR/layout change and stable recovery;
8. objective movement coverage: world-X, camera scroll, floor/depth and Z jump excursion;
9. optional P2/P3 reuse when those players are live;
10. terminal `IMPLEMENTATION_READY` or `FAILED_COMPONENT:<component>`.

These common facts must be proven once and reused by both surface binders in the same runtime/projection epoch.

### Player-specific facts still required

The existing proof JSON freezes an above-character calibration point, but the production player profile requires an exact complete profile accepted by `validateProofProfile`, including:

- `proofId` and `projectionVersion`;
- `cameraAddress`, `cameraSign`, `cameraScale`;
- `worldXScale`, `xBias`;
- `floorYScale`, `zScale`, `yBias`;
- `headClearanceNative`;
- finite `validationBounds`.

The final binder must derive these fields from live proof evidence without guessing. In particular, the existing HUDANCHOR output's single selected Y bias / logical above-character offset must not be silently double-counted or arbitrarily split between production `yBias` and `headClearanceNative`.

### Enemy-specific facts still required

Enemy projection reuses the common camera/X/Y-model facts but additionally requires:

- current supported enemy world reference (`enemyX/enemyY/enemyZ`) to be demonstrably the moving enemy that owns the label;
- one proved finite `enemyHeadOffsetsByType[type]` for every enemy type claimed supported by the activated profile;
- type-specific clearance calibration when a common offset is not visibly stable;
- proof that a moving enemy retains the label while the camera and/or player also move;
- proof that current target changes update the text immediately and never leave the prior target label behind.

A type not proved in this session must remain absent from `enemyHeadOffsetsByType` and therefore fail closed as `UNSUPPORTED_ENEMY_TYPE`.

## 4. Exact existing loader command

The current HUDANCHOR proof loader is reused unchanged as the common-transform collector. Run the following exact line first in the game Worker Console and then in the Top page Console:

```js
fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/HUDANCHOR_PROOF/wof_hudanchor_proof.js?'+Date.now()).then(r=>r.text()).then(t=>(0,eval)(t))
```

Expected readiness messages are the existing:

- `✅ HUDANCHOR proof Worker ready`
- `✅ HUDANCHOR proof Top ready`

The current proof result remains retrievable as:

```js
WOFHUDANCHOR.result()
```

No additional console command is authorized by this prep because no current committed command yet exists for dual Alpha-surface observation. Inventing one here would violate the proof boundary.

## 5. Required single-session choreography

The future executable tooling extension must keep one Browser/WOF runtime alive from common calibration through both overlay observations. It may automate evidence collection, but Owner interaction remains ordinary gameplay.

### Phase 0 — preflight / blob and runtime pin

Before any visual verdict is possible, automatically retain:

- repository HEAD and exact product blob SHAs;
- proof-tool blob SHAs;
- ROM SHA (`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62` for enemy helper authority);
- Browser/WOF build identity if available;
- one proof session ID;
- runtime epoch / projection epoch;
- initial canvas CSS rect, DPR, fullscreen state, drawing-buffer dimensions and live GL viewport.

Any product/helper/profile blob mismatch against the run manifest is `FAILED_COMPONENT:product_blob_binding`.

### Phase 1 — common camera/X calibration

Use the existing bounded scanner and gates. Owner moves P1 horizontally until the background genuinely scrolls. Do not permit calibration until the existing camera gate passes.

Then Owner performs the existing one calibration click at the desired player warning anchor center above P1.

Post-calibration require at minimum:

- world-X excursion >= 24;
- camera excursion >= 6;
- locked camera identity unchanged.

### Phase 2 — depth and complete jump

Without reload:

- make a visible depth/lane excursion, floor-Y range >= 8;
- perform one complete jump with Z range >= 8;
- retain evidence spanning ascent, apex, descent and landing, not just two endpoints.

The selected Y model must remain visually attached through the whole jump and depth motion.

### Phase 3 — fast horizontal + rapid stage/camera advance

Perform a deliberately fast left/right burst, then advance rapidly enough to produce obvious stage/camera scrolling.

Required observation:

- player warning candidate and enemy label candidate do not visibly lag or detach from their owner;
- common camera transform remains locked;
- no previous drawing-buffer coordinate is reused after a current sample becomes invalid.

### Phase 4 — player + camera simultaneous motion

Move the player while the background is simultaneously scrolling. Require current-frame compensation, not a later catch-up.

Any repeatable visible separation between overlay and owner is a P0 `FAILED_COMPONENT:visible_overlay_drift`.

### Phase 5 — live player danger warning

Using only real current Alpha warning authority, enter a normal gameplay situation that makes a supported danger warning active.

Require:

- warning appears above the current warned P1/P2/P3 only after a valid live anchor exists;
- current 50 Hz spatial path visibly follows fast movement;
- warning does not remain attached to an old player after retarget/lifecycle change;
- if anchor authority becomes invalid, the head warning disappears from the old coordinate and the existing fixed HUD fallback remains available.

No synthetic warning injection satisfies this phase.

### Phase 6 — moving enemy target label

With a supported enemy and a current valid target:

- observe `1P`, `2P` or `3P` above that moving enemy;
- let the enemy move in both screen X and lane/depth where practical;
- include camera motion while the enemy moves;
- require the label to stay attached to the same enemy identity.

### Phase 7 — live retarget

Cause a real supported enemy to change current target through normal gameplay.

Require an observable sequence such as `1P -> 2P -> 3P` where available. The exact target sequence need not be forced if the game situation exposes fewer players, but every observed retarget must satisfy:

- new text corresponds to current raw target authority;
- old text clears immediately;
- old screen coordinate is not held;
- target label remains on the same enemy identity unless the enemy itself is replaced.

### Phase 8 — multiple enemies

Where practical, keep two or more supported enemies visible simultaneously.

Require per-enemy isolation:

- labels bind to distinct current enemy identities;
- one enemy's retarget/disappearance does not rewrite or preserve another enemy's label;
- crossing/overlapping sprites must not cause identity swap. Visual overlap is allowed; ownership swap is not.

If the live encounter cannot practically expose multiple supported enemies, record `NOT_OBSERVED` and do not fabricate PASS for this subcase. The terminal release policy may decide whether a separate bounded encounter is required.

### Phase 9 — resize/fullscreen/drawing-buffer remap

Perform at least one actual window resize or fullscreen transition and then reach a stable recovered layout.

Reuse existing objective gates:

- WebGL hook count >= 30;
- marker draw count >= 30;
- valid live viewport;
- layout change count > 0;
- stable recovery after the change.

For both Alpha surfaces require:

- mapping uses the new drawing buffer/content rect;
- no old mapping key / old coordinate persists visibly;
- any cross-epoch remap window suppresses/falls back until authority is current.

### Phase 10 — fail-closed authority windows

The dual-surface observer must correlate actual draw decisions with live authority state. A pass requires that any observed invalid window never displays an anchored cue from stale/invalid authority.

Classify and record these authority failures independently:

- stale player / marker / projection / drawing buffer;
- player/enemy identity replacement or absence;
- runtime/projection/drawing-buffer epoch mismatch;
- invalid/non-finite confidence;
- non-finite projected coordinates;
- native or drawing-buffer out-of-bounds anchor;
- player spatial/projection sample older than the warning sample after retarget.

If a category is not naturally observed, mark it `NOT_OBSERVED`, never infer a live PASS from repository regression. A later executable tooling stage may add a bounded **live fault-boundary exercise** using real Browser/WOF state, but it must not substitute fabricated coordinates or synthetic target/warning semantics.

## 6. Objective visual acceptance

### Pass-level behavior

A surface is visually acceptable only when all of the following hold for every observed dynamic phase:

- attachment remains on the correct actor during motion;
- no obvious repeated lag/trailing is visible at the required rapid movement cadence;
- no snap to an old actor/old enemy after retarget or lifecycle replacement;
- no stale coordinate survives resize/fullscreen/remap;
- uncertainty hides/suppresses or uses fixed HUD as designed.

### P0 failures

Any of these is immediate failure:

- repeatable visible overlay drift/detachment;
- wrong player/enemy identity;
- wrong current target text;
- stale old target or old coordinate after retarget/replacement;
- anchored rendering during known invalid confidence/epoch/stale authority;
- cross-epoch drawing-buffer mapping accepted;
- synthetic/repository evidence represented as live proof.

## 7. One-session feasibility conclusion

### Common projection: YES

One uninterrupted session can and should prove the common camera/X transform, Y/Z model selection, live WebGL drawing-buffer mapping, resize/fullscreen recovery and motion coverage.

### Actual Alpha dual-surface end-to-end observation with current tooling: NO

Current `HUDANCHOR_PROOF` draws only its three projection candidates and produces the common projection JSON. It does not observe/score the production player danger warning and enemy target label surfaces, does not bind the two current `UNPROVED` production profiles in-session, and does not collect enemy-type head offsets.

Therefore the final release live proof should remain one session, but **one minimal tooling extension must be completed first**. This is a tooling/observation gap, not a request for more synthetic QA and not a request for broad manual Owner work.

## 8. Exact minimal follow-up stage

Recommended stage:

- stageId: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_V1`
- dedupKey: `alpha.v1.anchored-overlays.one-session-live-proof-tooling`
- scope: `parallel/HUDANCHOR_PROOF/**` and a dedicated proof-output lane only; no danger rules, target semantics, Transport authority or gameplay input changes.

Minimum deliverables:

1. extend the existing Top/Worker proof harness so the common frozen projection is handed to two live **proof observers** in the same runtime without Owner copying values;
2. add a deterministic production-profile binder that converts only proved fields into the player and enemy profile schemas and refuses ambiguous decomposition;
3. add enemy-type clearance capture against real moving enemy identities, with unproved types omitted/fail-closed;
4. observe actual Alpha draw decisions for player-head warning and enemy-head labels, including fixed-HUD/suppressed reasons;
5. record actor identity, target, sample age, confidence, epochs, mapping key and draw/no-draw for each evidence frame/event;
6. add automatic phase markers for rapid horizontal, depth, complete jump, scroll, simultaneous player+camera, moving enemy, retarget, multi-enemy, remap and fail-closed windows;
7. emit exactly one terminal evidence JSON conforming to this prep's `LIVE_PROOF_EVIDENCE_SCHEMA.json`;
8. retain the existing exact loader UX or provide one equally bounded single loader per Worker/Top half; Owner must not paste projection constants or select addresses.

The extension must not claim success merely because common HUDANCHOR candidates are stable. It must observe the Alpha surface decisions tied to the same live identities/epochs.

## 9. Terminal verdict policy for the future live run

Allowed terminal verdicts:

- `IMPLEMENTATION_READY` — all required observable live gates close, both activated surface bindings are proved, and no P0 failure occurs;
- `FAILED_COMPONENT:<component>` — any objective or visual gate fails;
- `INCOMPLETE_OBSERVATION:<component>` — live session never exposes a required release observation and policy does not permit omission.

`IMPLEMENTATION_READY` must never be emitted from repository/synthetic QA alone.

Suggested component names:

- `product_blob_binding`
- `worker_bridge`
- `calibration`
- `camera`
- `camera_scroll_coverage`
- `depth_coverage`
- `jump_coverage`
- `x_camera_transform`
- `depth_y`
- `jump_z`
- `drawing_buffer`
- `resize_fullscreen`
- `player_profile_binding`
- `enemy_profile_binding`
- `enemy_type_clearance`
- `player_warning_follow`
- `enemy_label_follow`
- `live_retarget`
- `multi_enemy_identity`
- `stale_fail_closed`
- `identity_fail_closed`
- `epoch_fail_closed`
- `confidence_fail_closed`
- `bounds_fail_closed`
- `visible_overlay_drift`
- `visual_confirmation`

## 10. Owner action bound

Owner performs only:

1. load the committed proof tool in Worker and Top using the documented loader line(s);
2. normal P1 horizontal movement until background scrolls;
3. one calibration click;
4. visible depth movement;
5. one complete jump;
6. fast movement / normal stage advance;
7. normal gameplay sufficient to expose a real danger warning, moving targeted enemy, retarget, and multiple enemies when practical;
8. one resize/fullscreen transition and recovery;
9. one final visual classification if the automated observer cannot objectively decide attachment;
10. return the single generated JSON.

No other Owner debugging action is part of this contract.
