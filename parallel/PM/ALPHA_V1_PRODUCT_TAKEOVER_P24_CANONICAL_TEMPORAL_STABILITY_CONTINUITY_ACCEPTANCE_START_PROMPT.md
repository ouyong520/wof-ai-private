stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P24_CANONICAL_TEMPORAL_STABILITY_CONTINUITY_ACCEPTANCE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.canonical-temporal-stability-continuity-acceptance-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P24_CANONICAL_TEMPORAL_STABILITY_CONTINUITY_ACCEPTANCE_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P24_CANONICAL_TEMPORAL_STABILITY_CONTINUITY_ACCEPTANCE_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P24_CANONICAL_TEMPORAL_STABILITY_CONTINUITY_ACCEPTANCE`

# Alpha V1 Product Takeover P24 — Canonical Temporal Stability / Continuity Acceptance

Repository: `ouyong520/wof-ai-private`

This is a long final product-stability module. Implement the complete temporal continuity evidence/analyzer layer in one bounded task. Do not split into micro-patches and do not run real WOF in this implementation stage.

Read latest `main`, `AGENTS.md`, PM testing cadence, dedup guard, current dispatch, and at minimum:
- P12 actor/generation registry implementation/result;
- P10 transport bridge implementation/result;
- P15 canonical runtime convergence implementation/result;
- P16 Owner canonical status/evidence implementation/result;
- P18 maintained HUD draw acknowledgement implementation/result;
- P21 exact-candidate staging harness implementation/result;
- P22 prompt/claim and result if it becomes available during execution;
- P23 prompt/claim;
- W3 long qualification result/runner contract;
- maintained `product/alpha/wof_alpha_hud.js` canonical ledger/evidence API;
- canonical runtime coordinator, render-object anchor and envelope contracts.

## Why P24 exists

Per-frame correctness is not sufficient for an Owner-visible overlay. A product can use the right actor and right anchor on individual frames yet still be unusable because of temporal defects such as flicker, one-frame stale reuse, rapid READY/SUPPRESSED oscillation, generation handoff ghosts, renderer/runtime epoch crossover, draw acknowledgements arriving after authority revocation, or an actor label jumping between unrelated body instances.

P24 must make these temporal failure modes explicitly measurable and fail-closed without inventing coordinates or gameplay states.

## Ownership

Normal dedup-v2 create-only canonical claim -> exact token re-read -> create-only stage claim -> exact-token re-read. Fail closed on any ownership failure. Do not invent recovery.

Do not modify P22/P23/P21/P20/P19/P18/W3 claims or RESULT files. Do not steal their owned files.

## Product goal

Implement a passive canonical temporal continuity analyzer and evidence contract that consumes an ordered sequence of already-authoritative canonical runtime / envelope / draw-evidence observations and classifies continuity without becoming a new position or identity authority.

The analyzer must answer whether the product remained temporally coherent across normal continuous play and lifecycle boundaries while preserving all existing fail-closed semantics.

## Workstream A — ordered observation contract

Create an isolated area such as `parallel/TEMPORAL_ACCEPTANCE/`.

Define a deterministic observation schema sufficient to bind each sample to:
- exact World SHA;
- authorityKey;
- runtimeEpoch;
- rendererEpoch;
- actor + generation;
- canonical state READY/SUPPRESSED and suppression reason when present;
- anchor/bodyBounds only when already supplied by canonical authority;
- P18 maintained draw acknowledgement identity/counter/timestamp when present;
- monotonic local sample sequence/time metadata;
- read-only safety fields.

The module must never derive identity from coordinates, nearest-object heuristics, row order, screenshots, projection or old cache.

## Workstream B — temporal stability classifier

Implement deterministic sequence analysis for at least:
1. **same actor/generation continuity** — repeated READY samples for the same exact generation remain associated with that generation and cannot silently switch body identity;
2. **movement continuity evidence** — canonical anchors may move freely with the renderer, but impossible/stale cross-epoch reuse must be rejected. Do not impose arbitrary gameplay-speed limits that could reject legitimate animation/teleport behavior;
3. **READY/SUPPRESSED transition integrity** — suppression must not retain stale draw authority; later READY requires current exact authority/generation;
4. **generation rollover** — old generation must cease authorizing immediately when a new generation becomes current; no ghost draw acknowledgement from old generation may be accepted afterward;
5. **runtime/renderer replacement** — epoch change invalidates previous samples/ledger rows; no cross-epoch continuity claim;
6. **actor disappearance/reappearance** — disappearance may suppress; reappearance is acceptable only with current exact actor/generation authority;
7. **draw acknowledgement causality** — P18 acknowledgements must correspond to current canonical identity and may not arrive as accepted evidence after revoke/epoch rollover;
8. **bounded oscillation/flicker evidence** — report READY<->SUPPRESSED churn rate/durations and repeated one-sample pulses as evidence, but do not declare a hard product failure from arbitrary thresholds unless threshold is explicitly configured by acceptance authority;
9. **stale-frame/duplicate sequence detection** — duplicate/out-of-order samples cannot increase confidence or coverage;
10. **multi-actor independence** — P1/P2/P3/enemy-slot-N streams are analyzed independently and never allowed to repair each other by proximity or shared coordinates.

Classifications should include deterministic states such as `PROVEN_CONTINUOUS`, `OBSERVED_WITH_CHURN`, `SUPPRESSED_SAFELY`, `STALE_OR_MISMATCH`, `INSUFFICIENT_EVIDENCE`, and `UNPROVEN` where appropriate.

## Workstream C — no-flicker / ghost-risk evidence matrix

Produce a bounded report with per actor/generation and aggregate fields covering at least:
- sample count and accepted sequence span;
- READY sample count;
- SUPPRESSED sample count by exact reason;
- transition count;
- one-sample READY pulses;
- one-sample SUPPRESSED pulses;
- longest observed READY run;
- generation rollover count;
- renderer/runtime epoch replacement count;
- stale/duplicate/out-of-order rejection count;
- accepted maintained draw acknowledgements;
- stale draw acknowledgement rejection count;
- observed actor disappearance/reappearance transitions;
- final classification and exact reasons.

Do not claim that low churn proves visible correctness. This is temporal runtime/draw evidence only.

## Workstream D — P21/P17/P23-compatible passive collector seam

Provide a read-only collector/CLI that can later consume evidence from a P21 staged acceptance run without modifying the staged runtime or P21 itself.

Prefer reading bounded JSON/JSONL snapshots/evidence already emitted by canonical/P16/P18/P21 paths, or accepting an explicit fixture input path. If a live CDP read seam is necessary, it must be passive/read-only and exact-identity bound; do not add a new coordinate producer.

Emit deterministic JSON + concise Markdown under an overridable output root suitable for `Documents\\WOF_RESULTS` later.

Expose a stable evidence path/schema that P23 can consume later, but do not modify P23-owned files while its claim is ACTIVE. If P23 needs a future integration update, document the exact seam in P24 RESULT/nextAction rather than crossing ownership.

## Workstream E — truthfulness rules

P24 must explicitly preserve these boundaries:
- no real WOF run in this worker stage;
- no Owner visual PASS;
- no W3 renderer-source promotion;
- no `alpha-live` movement;
- no screenshot/world-projection production coordinates;
- no guessed HIT/DOWN/JUMP/DEATH states;
- no inferred actor identity from spatial continuity;
- no smoothing/interpolation inserted into the production HUD by this task.

Temporal analysis is evidence/acceptance only. It is not permission to hide a real canonical defect with interpolation or sticky stale coordinates.

## Write boundaries

Expected new files only under `parallel/TEMPORAL_ACCEPTANCE/` plus narrow focused tests/docs.

Do not modify:
- `product/alpha/wof_alpha_hud.js`;
- P22 dynamic-state analyzer files while P22 is ACTIVE;
- P23 close-harness files while P23 is ACTIVE;
- P21 staging files;
- P20 release gate;
- P19 candidate builder/attestation;
- W3 producer/qualification;
- permanent W1 updater;
- `alpha-live` ref.

If a genuine integration defect is discovered in an owned file, fail closed and record exact evidence instead of editing across ownership.

## Focused checks only

Implementation first. Run only narrow tests:
- Python parse/compile;
- deterministic ordered-sequence fixture;
- same-generation READY continuity fixture;
- generation rollover with stale old-generation draw rejection;
- runtime/renderer epoch rollover invalidation;
- READY/SUPPRESSED one-sample churn accounting;
- duplicate/out-of-order rejection;
- actor disappearance/reappearance fixture;
- multi-actor independence fixture;
- explicit assertion that no coordinate inference/smoothing/alpha-live mutation occurs.

No broad QA and no real WOF.

## Terminal result

Write exactly:
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P24_CANONICAL_TEMPORAL_STABILITY_CONTINUITY_ACCEPTANCE_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P24_CANONICAL_TEMPORAL_STABILITY_CONTINUITY_ACCEPTANCE_RESULT.md`

Record implementation commits, changed files, focused tests, evidence schema/path, integrationReady, P21/P22/P23/W3 boundaries, safety, and exact nextAction.

A successful COMPLETE proves only that temporal stability acceptance tooling is implemented and fixture-verified. It must keep `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, and `alphaLiveMoved=false` until later live evidence exists.
