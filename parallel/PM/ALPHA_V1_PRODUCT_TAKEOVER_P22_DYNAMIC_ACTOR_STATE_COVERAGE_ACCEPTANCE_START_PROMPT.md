stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P22_DYNAMIC_ACTOR_STATE_COVERAGE_ACCEPTANCE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.dynamic-actor-state-coverage-acceptance-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P22_DYNAMIC_ACTOR_STATE_COVERAGE_ACCEPTANCE_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P22_DYNAMIC_ACTOR_STATE_COVERAGE_ACCEPTANCE_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P22_DYNAMIC_ACTOR_STATE_COVERAGE_ACCEPTANCE`

# Alpha V1 Product Takeover P22 — Dynamic Actor State Coverage Acceptance

Repository: `ouyong520/wof-ai-private`

This is a long final-acceptance instrumentation task. Do not split it into micro-stages. Its purpose is to close the explicit product question: does canonical actor/head positioning remain correct across meaningful actor lifecycle, animation, movement and visibility changes, rather than only in a static standing fixture?

Read latest `main`, `AGENTS.md`, PM testing cadence, dedup guard, current dispatch, and at minimum:
- P15 COMPLETE result and canonical runtime coordinator;
- P16 COMPLETE canonical Owner status/evidence contract;
- P17 COMPLETE final acceptance orchestrator/result;
- P18 COMPLETE canonical draw acknowledgement/evidence contract;
- P19 COMPLETE final candidate/attestation/latest pointer;
- P20 COMPLETE release-gate result;
- P21 staging prompt/result if available;
- W3 long qualification result/runner;
- `parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`;
- `parallel/PYLAUNCH/wof_launcher/canonical_actor_generation_registry.py`;
- `product/alpha/wof_alpha_field_adapter.js`;
- any existing read-only canonical evidence/status APIs already exposed by the final candidate.

## Ownership

Perform normal dedup-v2 create-only canonical claim -> exact-token re-read -> create-only stage claim -> exact-token re-read. Fail closed on any ownership failure. Do not invent recovery.

Do not modify P21/P20/P19/P17/P18/W3 claims or RESULT files.

## Goal

Implement a bounded, passive, exact-candidate dynamic-state coverage recorder and acceptance analyzer that can later run during the same P21/P17 Owner normal-play acceptance session.

It must answer, with evidence rather than assumptions, which actor/state transitions were actually observed while canonical anchors/draw acknowledgements remained correctly bound to the same actor/generation.

This stage implements the recorder/analyzer/harness only. Do not run real WOF and do not claim that every game state has already been observed.

## Core evidence rule

Do **not** create a second coordinate authority and do not infer actor identity from coordinates.

Allowed inputs are existing exact/canonical evidence already exposed by the accepted stack, such as:
- P16 canonical status/evidence;
- P18 canonical draw ledger/evidence;
- P9/P10/P12 canonical actor/generation/anchor records if exposed through the accepted runtime/status seam;
- semantic-only target/presence/lifecycle state already produced by the final candidate;
- exact authority/runtime/renderer/page/package metadata;
- P21 exact staged-candidate receipt.

Do not add new guessed RAM addresses, screenshot tracking, template tracking, world->screen projection, nearest-object matching, row-order identity, or stale-cache fallbacks.

If a named animation state cannot be deterministically distinguished from already exposed evidence, mark it `UNPROVEN_SIGNAL` or `NOT_OBSERVED`; do not invent a classifier just to fill the matrix.

## Workstream A — bounded dynamic coverage ledger

Create a new isolated area, preferably `parallel/OWNER_ACCEPTANCE_STATE/`.

Implement a deterministic bounded ledger for exact-candidate acceptance observations. Each accepted sample/event must bind at least:
- candidate source commit + package version/hash;
- exact World identity;
- page target identity where available;
- authority key;
- runtime epoch;
- renderer epoch;
- actor;
- generation;
- canonical state READY/SUPPRESSED;
- body bounds / canonical anchor metadata only when already present in canonical evidence;
- draw acknowledgement linkage when present;
- timestamp/sequence;
- semantic/lifecycle state fields only when they come from an already-proven producer.

Ledger must be bounded, generation-aware, renderer-epoch-aware and reset/revoke correctly on authority replacement.

## Workstream B — state/transition coverage matrix

The analyzer must produce explicit coverage states such as `OBSERVED_PROVEN`, `OBSERVED_PARTIAL`, `NOT_OBSERVED`, `UNPROVEN_SIGNAL`, `SUPPRESSED_SAFELY`, never an invented PASS.

Cover the following categories when evidence permits:

1. **Player presence lifecycle**
   - P1 active;
   - P2/P3 active/inactive or join/leave transitions if actually observed;
   - contradictory identity -> fail-closed suppression.

2. **Movement/follow continuity**
   - same actor + same generation anchor changes across multiple accepted samples;
   - no stale old-generation draw acknowledgement after generation/authority change.

3. **Animation/body-geometry change**
   - same actor/generation shows materially changed renderer-qualified body bounds/top/height while anchor remains derived from current body geometry;
   - weapon/effect/projectile-only geometry must not count as actor-body coverage.

4. **Vertical / jump-like movement**
   - only classify as jump/vertical-state if an existing exact semantic signal proves that meaning;
   - otherwise report generic vertical anchor/body movement, not `JUMP`.

5. **Hit/down/recovery-like animation**
   - only name `HIT`, `DOWN`, `RECOVERY`, `DEATH` when an already-exposed exact semantic state proves it;
   - otherwise record generic body-state transition and leave named state `UNPROVEN_SIGNAL`.

6. **Offscreen / clipping / re-entry**
   - canonical suppression when visible body bounds are unavailable/offscreen;
   - later READY re-entry must bind to the current actor/generation, not reuse stale coordinates.

7. **Generation replacement / rebirth**
   - old generation stops producing accepted canonical/draw evidence;
   - new generation may become READY only with its own proven association.

8. **Enemy lifecycle and target semantics**
   - enemy-slot spawn/appearance and disappearance if observed;
   - target mapping `0 -> P1`, `4 -> P2`, `8 -> P3` remains semantic-only;
   - target switches across samples if observed;
   - labels remain tied to the current enemy actor/generation and canonical anchor.

9. **Renderer/runtime replacement**
   - old epoch evidence revoked/suppressed;
   - no acknowledgement from stale renderer/runtime is accepted into the current coverage ledger.

The matrix may include additional evidence-backed categories discovered from the current exact stack, but do not broaden into gameplay prediction or new danger rules.

## Workstream C — continuity/invariant analyzer

Implement fail-closed invariants at least for:
- actor identity never selected by spatial proximity/order;
- generation monotonic/change boundary is respected for each observed actor;
- authority/runtime/renderer mismatch cannot be merged into one continuous track;
- canonical READY records use native 384x224 contract;
- stale READY/draw evidence after revoke is rejected;
- no legacy projection/screenshot coordinate appears as canonical position authority;
- semantic target/presence data never authorizes position by itself;
- P18 draw acknowledgement can prove maintained primitive execution only, never visible pixel correctness;
- missing rare-state observation is reported as coverage gap, not silently treated as PASS.

For a fixed evidence input, analysis output must be deterministic.

## Workstream D — Owner normal-play integration

Provide one later-use Windows-friendly wrapper or callable integration seam that P21/P17 acceptance can invoke without changing the permanent Owner install path.

The Owner instruction later should remain simple: play normally and, if convenient, include movement, attacks, taking a hit/knockdown, scrolling, and multiplayer join/leave. The recorder should observe passively; no DevTools, coordinates, manual JSON, clicks on heads, or state labels are required.

Do not make rare states mandatory for the session to complete. Produce a truthful matrix showing what was and was not observed. Define a small **core acceptance set** that is realistically observable in normal play (for example P1 movement continuity + at least one body-geometry change + enemy target-label continuity when enemies are present), while all rare states remain explicit coverage evidence rather than fabricated prerequisites.

If P21 is not yet COMPLETE, the module must still be implementation-complete and expose a clean integration seam; actual live invocation remains later.

## Workstream E — evidence output

Produce deterministic JSON + concise Markdown under Owner results when later run, with fixtureable output root for tests. Suggested names:
- `ALPHA_DYNAMIC_STATE_COVERAGE.json`
- `ALPHA_DYNAMIC_STATE_COVERAGE.md`

Include:
- exact candidate identity;
- authority/runtime/renderer identities observed;
- per-actor/generation tracks;
- coverage matrix;
- core acceptance summary;
- coverage gaps;
- stale/suppression incidents;
- draw-evidence linkage;
- `visibleProof=NOT_PROVEN` unless a separate P20 real Owner visual receipt says PASS;
- safety fields.

P22 repository implementation must itself record `realWofAcceptance=NOT_RUN` and `ownerVisualAcceptance=NOT_RUN`.

## Write boundaries

Expected new files only under `parallel/OWNER_ACCEPTANCE_STATE/` plus narrow focused tests/docs.

Do not modify:
- P21 `parallel/OWNER_STAGING/` while P21 owns it;
- P20 `parallel/OWNER_RELEASE/`;
- P19 final candidate builder/candidate/attestation;
- P17 orchestrator;
- P18 HUD/draw evidence;
- P15 runtime semantics/coordinator;
- W3 producer/qualification;
- permanent W1 updater;
- `alpha-live`.

If an existing exposed evidence contract is insufficient for a named state, preserve the gap in output. Do not cross ownership to add hidden signals.

## Focused checks only

Implementation first. Run only narrow checks:
- Python/CMD syntax/compile as appropriate;
- deterministic ledger + matrix fixture;
- same actor/generation movement continuity fixture;
- body-geometry change fixture;
- stale generation/runtime/renderer rejection;
- offscreen suppression -> current-generation re-entry fixture;
- enemy target switch mapping fixture;
- missing semantic signal => `UNPROVEN_SIGNAL`, never guessed named state;
- bounded ledger fixture;
- explicit no-legacy-coordinate/no-visible-PASS assertions.

No broad regression and no real WOF run.

## Terminal result

Write exactly:
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P22_DYNAMIC_ACTOR_STATE_COVERAGE_ACCEPTANCE_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P22_DYNAMIC_ACTOR_STATE_COVERAGE_ACCEPTANCE_RESULT.md`

Record implementation commits, changed files, focused checks, integrationReady, exact live evidence boundary, safety, and nextAction.

Successful terminal state proves the coverage recorder/analyzer implementation, not that all actor states were already observed in real WOF.