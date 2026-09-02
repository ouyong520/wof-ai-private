# WOF Alpha V1 — Anchored Overlays One-Session Live Proof Tooling

stageId: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.anchored-overlays.one-session-live-proof-tooling`
dedupMode: `exclusive`

Priority: **P0 Alpha V1 live-proof enablement implementation**

## Purpose

The bounded live-proof preparation stage is COMPLETE/PASS and established that one uninterrupted Browser/WOF session can reuse the common HUDANCHOR camera/X/YZ/WebGL/remap proof for both mandatory Alpha V1 anchored surfaces, but the current committed proof harness cannot yet observe/score the actual Alpha player-head warning and enemy-head target-label draws or bind the two production projection profiles from that same runtime.

This stage implements the exact minimal repository tooling follow-up. It does not execute the real live proof and must not invent projection constants.

## Start / canonical dedup v2

Before substantive implementation, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current claims/recent commits, and at minimum:

- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/RESULT.md`;
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/ONE_SESSION_DYNAMIC_PROOF_CONTRACT.md`;
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/LIVE_PROOF_EVIDENCE_SCHEMA.json`;
- current `parallel/HUDANCHOR_PROOF/**` and `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md`;
- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION/RESULT.md`;
- latest enemy-head label QA V3 result;
- current player/enemy projection profiles and player/enemy anchored helpers/HUD/worker/loader only as needed to bind observable contracts.

If equivalent tooling is already COMPLETE and satisfies the current evidence schema/one-session contract, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.v1.anchored-overlays.one-session-live-proof-tooling.json`

with a fresh unpredictable `claimToken`. Re-read current `main` and exact canonical file and verify ownership, then create:

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_V1.json`

Any ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Implementation requirements

Extend the existing bounded HUDANCHOR proof harness rather than creating a separate manual calibration workflow. The resulting tooling must be capable, in one uninterrupted future runtime, of:

1. retaining the existing common native 384x224 / camera / X-transform / Y-model / WebGL viewport-drawing-buffer / resize-fullscreen-remap objective proof and thresholds;
2. exposing the frozen common live projection facts to both Alpha anchored-surface observers without a second calibration session;
3. observing and recording actual Alpha player-head warning draw/no-draw decisions, with authoritative player identity, warning target, warning sample barrier, runtime/projection/drawing-buffer epochs, confidence, freshness, bounds and mapping inputs;
4. observing and recording actual Alpha enemy-head `1P / 2P / 3P` label draw/no-draw decisions, including current enemy identity/type/target, retarget clearing, epochs, freshness, confidence, bounds and mapping inputs;
5. collecting the minimal live enemy-type head-clearance/offset facts needed for supported enemy types instead of guessing `enemyHeadOffsetsByType`;
6. resolving the player production Y-bias/head-clearance split from observable live facts, or fail closed with a precise incomplete-observation component;
7. producing candidate/frozen player and enemy projection profile payloads only from real successful live observations; tooling/synthetic tests alone must never activate the production profiles;
8. correlating fast left/right, depth/lane, full jump, rapid forward+camera scroll, simultaneous player+camera movement, moving enemy label follow, retarget, multiple supported enemies where practical, and resize/fullscreen/remap evidence in the same evidence session;
9. explicitly record stale/identity/epoch/confidence/non-finite/out-of-bounds invalid windows and prove the product does not retain an anchored draw under known-invalid authority;
10. emit one terminal JSON conforming to the committed `LIVE_PROOF_EVIDENCE_SCHEMA.json` with terminal semantics limited to `IMPLEMENTATION_READY`, `FAILED_COMPONENT:<component>`, or `INCOMPLETE_OBSERVATION:<component>` as defined by the prep contract;
11. keep Owner interaction bounded to the existing normal-gameplay/proof controls: normal movement, one calibration click, one resize/fullscreen transition, gameplay needed to expose warning/retarget/moving enemies, and final visual classification only when required;
12. add repository-only deterministic/synthetic tests for schema generation, observer correlation, profile-binding fail-closed rules, no-draw invalid authority, and compatibility with the existing common proof harness.

## Hard boundaries

- Do **not** launch Browser/WOF in this tooling implementation stage.
- Do **not** modify danger-rule thresholds/selection, target semantics, Safe Transport authority, game input/AI or game RAM.
- Do **not** claim candidate/synthetic markers as actual Alpha surface live proof.
- Do **not** write guessed camera/Y/head-offset constants into production profiles.
- Prefer proof/tooling paths such as `parallel/HUDANCHOR_PROOF/**` plus a dedicated `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**` result/test lane.
- Avoid `product/alpha/**` changes unless absolutely necessary to expose read-only diagnostics already permitted by the contract; if such a change becomes materially necessary, document the smallest exact reason and preserve all product semantics/fail-closed activation boundaries.

## Stop

COMPLETE only when the repository tooling and deterministic tests show the future single Browser/WOF session can produce the committed dual-surface terminal evidence contract without manual address/constant transcription:

`COMPLETE — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING IMPLEMENTED — READY FOR FRESH QA / BOUNDED LIVE RUN`

BLOCKED:

`BLOCKED — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING — <precise blocker>`

Owner action: **NO** during this stage.
