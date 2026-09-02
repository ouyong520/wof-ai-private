# Alpha V1 Anchored Overlays One-Session Live-Proof Tooling Recovery V2 — RESULT

Status: **COMPLETE — READY FOR FRESH QA / BOUNDED LIVE RUN**

Stage: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_RECOVERY_V2`

Canonical recovery key: `alpha.v1.anchored-overlays.one-session-live-proof-tooling-recovery-v2`

Claim token: `9dc2b3ca-39f2-484d-9b5e-6d696f2192b7-d5595989907522d76a58b75a5c3eea2e`

## What was implemented

A proof-only lane now exists under `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**` for a future single uninterrupted Browser/WOF session.

It reuses the existing `parallel/HUDANCHOR_PROOF/**` common camera/X/Y/WebGL/remap proof and adds:

- read-only Worker snapshots for P1/P2/P3 and current live enemy slot/type/raw `target7E`/world X/Y/Z;
- Top-side wrapping of the existing Alpha player-warning and enemy-label helper objects, delegating the original `buildPlan` unchanged and recording the actual returned anchored/fixed/suppressed decisions that the HUD consumes;
- recording of `warningSampleAt`, sample age/confidence, runtime/projection/drawing-buffer epochs, mapping keys, actor/slot/type/target identity and projected draw anchors;
- automatic required-phase gates for fast horizontal movement, depth movement, complete jump, rapid camera/stage scroll, simultaneous player+camera motion, moving enemy, live retarget, resize/fullscreen remap, and optional multi-enemy observation;
- a bounded real stale-authority exercise that stops the official Alpha observer for 450ms, requires both player fixed-HUD fallback and enemy no-draw/suppression, then reinstalls the same live candidates through the official transport install API;
- terminal JSON generation using the existing bounded-live-proof evidence root/event structure, with `IMPLEMENTATION_READY`, `FAILED_COMPONENT:*`, or `INCOMPLETE_OBSERVATION:*` only.

## Live-only head facts — no guessed constants

The current production player and enemy projection profiles remain unproved/disabled. This stage did not activate or edit them.

The common HUDANCHOR head click alone cannot mathematically separate the player's body `yBias` from `headClearanceNative`. The recovery tooling therefore adds one same-session P1 body/reference click. It combines that live native click with the frozen common head click and the current P1 world Y/Z sample. No numeric coordinate is manually copied or typed.

Enemy `enemyHeadOffsetsByType` is also live-observation-only. A type becomes available to the runtime candidate only after an operator clicks the head of a current, non-overlapping live enemy. The tool binds the click to the nearest current live enemy X/slot/type, derives its offset from the selected common Y model, rejects ambiguous overlaps, rejects repeated captures with spread greater than 4 native pixels, and omits all unobserved types. Omitted types remain fail-closed.

Both generated candidates are tagged `PROOF_ONLY_RUNTIME_BINDING`, `REAL_BROWSER_WOF_BOUNDED_DYNAMIC_LIVE_PROOF_CANDIDATE_RUNTIME_ONLY`, and `guessedConstants:false`.

## Runtime binding boundary

The Worker validates the two runtime candidates using the current Alpha helper validators. It then calls the existing `WOFAlphaTransportAuthority.install(globalThis, binding)` with the current official session binding while temporarily intercepting only the two projection-profile fetch URLs. The fetch function is restored in `finally`.

No transport semantics, danger rules, target semantics, detector behavior, input path, AI path, HUD rendering semantics, or product profile file is changed by this stage.

## Drift pinning

`RUN_MANIFEST.json` pins the exact current product, HUDANCHOR, evidence-schema, and recovery tooling Git blob SHAs. A future live session recomputes each Git blob SHA before evidence collection; a mismatch makes the proof preflight fail closed.

Pinned product blobs at completion:

- player warning helper `af7f2359514dc6f86f74fac0c47858e8a6acf107`
- player projection profile `bbed0618b348961580ca805bb93e4d17525f0142`
- enemy target-label helper `e6e1260559f735b85ce6f69e87803369f125b2de`
- enemy projection profile `8de57739818503a0e14702d2fa0bb4eba58228d2`
- real worker `b7f4506fc90b681ede059df5ad3316e665c6f15e`
- Alpha HUD `50d944c451ac94b114e4f86441aeae8ad6b25c78`
- Alpha loader `66aee09fc2dd009c2f295d2092f3129548605efb`

Pinned recovery runtime blobs:

- proof core `fbfa665daa624b7a81b6b75d488af504194bd378`
- Top observer `3f2ffdfc2947387518e593445306f8803132345c`
- Worker observer `5cc30f3a3b32ee0ef3dfe1b9ac2937dbabc774f3`
- one-session loader `30c965bb8b16466810781e2741f2d2eb86a0533d`

## Deterministic repository test

Command:

`node parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/tooling_regression.mjs`

Result: **PASS — 19 / 19** on Node `v22.16.0`, plus syntax checks for the core, Top observer, Worker observer, loader, and regression file.

The regression covers real-live-only profile binding, player Y split fail-closed, enemy unproved-type omission, `warningSampleAt`/epoch/mapping correlation, raw enemy target/identity/label correlation, fixed/suppress invalid-authority behavior, anchored-during-invalid-authority failure, required phase and retarget gating, both-surface stale authority gating, final visual confirmation, terminal structure, original helper delegation, read-only Worker behavior, official transport install usage, fetch restoration, and HUDANCHOR-first loader ordering.

`REPOSITORY_TEST_RESULT.json` is explicitly `SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_LIVE_PROOF`. It cannot activate a production profile or satisfy the live-proof gate.

## Browser/WOF status

**NOT RUN by this stage.** No Browser/WOF session was started. No live projection constant was guessed. No production profile was activated from synthetic evidence.

The next stage is fresh independent repository QA and then the bounded single-session Browser/WOF live run using the committed loader.

## Dedup recovery status

The historical ACTIVE canonical/stage claim for `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_V1` was preserved and was not overwritten, deleted, or reused. Recovery V2 used its own PM-authorized canonical key and claim token.

Terminal stage text:

`COMPLETE — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING RECOVERY V2 — READY FOR FRESH QA / BOUNDED LIVE RUN`
