# Alpha V1 P27 — P21 Staged Runtime Canonical Feed Exposure

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P27_P21_STAGED_RUNTIME_CANONICAL_FEED_EXPOSURE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.p21-staged-runtime-canonical-feed-exposure-v1`
dedupMode: `exclusive`

## Mission

Repair the concrete upstream seam proven by P25: the exact-candidate P21 staged runtime/status publisher must expose the real maintained P10 canonical runtime coordinator feed so downstream P22/P24/P25 acceptance can consume legitimate same-session canonical cycles.

This is a narrow successor repair. It is not a P25 continuation, not a P26 provenance redesign, not W3 reverse engineering, and not a new release/promotion stage.

## Required preflight

Before any mutation:

1. read latest `main` and root `AGENTS.md`;
2. read `parallel/PM/STAGE_DEDUP_GUARD.md`;
3. read `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`;
4. read `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`;
5. read the P25 durable checkpoint:
   `parallel/PM/PROGRESS/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_PROGRESS.json`;
6. read P21 staging/runtime implementation and the exact P19 candidate authority;
7. trace the maintained P10/P12 canonical coordinator producer/contract that carries canonical actor-generation-anchor state;
8. inspect canonical/stage claims for this P27 dedup key and perform normal dedup-v2 acquisition only if unclaimed.

Do not start implementation until canonical + stage claims have been created and re-read with the exact matching claimToken.

Immediately after claim verification, create and maintain:
`parallel/PM/PROGRESS/ALPHA_V1_PRODUCT_TAKEOVER_P27_P21_STAGED_RUNTIME_CANONICAL_FEED_EXPOSURE_PROGRESS.json`.

## Proven blocker being repaired

P25 established this fail-closed state:

`canonicalFeed.state=NOT_EXPOSED_BY_STAGED_RUNTIME_STATUS`

The current exact-candidate staged runtime publisher exposes V3 render-authority measurement status, but that seam does not expose the maintained P10 canonical coordinator feed. There is no authority to synthesize P22/P24 cycles from W3/V3 measurements, screenshots, world projection, row order, nearest-object guesses, or cached coordinates.

P27 must repair that real seam, not reinterpret the evidence.

## Required implementation

Implement the smallest production-shaped wiring that makes the maintained P10 canonical coordinator output available through the exact P21 staged runtime/status publisher used by staged final acceptance.

The exposed canonical feed must preserve and validate the real authority identity, including at minimum:

- `worldSha256`;
- `pageTargetId`;
- `authorityKey`;
- `runtimeEpoch`;
- `rendererEpoch`;
- canonical P10 actor/generation/READY-or-SUPPRESSED records and their canonical anchor payloads where legitimately present.

Requirements:

- consume only the maintained canonical producer/contract already used by the runtime;
- make the feed observable by the staged runtime status/tee path without inventing a second coordinate authority;
- fail closed on missing canonical producer, malformed payload, world/page/authority mismatch, stale runtime/renderer epoch, replay, or cross-candidate state;
- SUPPRESSED records must remain coordinate-free;
- runtime/renderer replacement must not silently reuse an old feed;
- staged cleanup/restoration behavior must remain intact;
- keep exact-candidate identity binding intact.

## Forbidden substitutions

P27 must never:

- treat W3/V3 measurement status as the P10 canonical coordinator feed;
- derive production coordinates from screenshots;
- derive production coordinates from world projection;
- guess actor identity from coordinate proximity, row order, nearest object, old cache, or stale generation;
- hard-code a renderer/object address merely to make tests pass;
- manufacture P22/P24 cycles or P18 acknowledgements;
- claim Owner-visible proof from fixture/unit status.

## Ownership and write boundary

P27 may change only the narrow P21 staged runtime/status seam and directly necessary maintained canonical-feed adapter/helper/tests/documentation required to expose the existing P10 coordinator truthfully.

Do not modify:

- `parallel/OWNER_ACCEPTANCE_COMPOSITE/**` (P25 owned);
- P26 provenance/session-chain implementation or RESULT/PROGRESS;
- P22/P24 analyzers;
- P20 promotion logic;
- P23 post-promotion verifier;
- W3 producer/reverse-engineering ownership;
- permanent W1 updater;
- `alpha-live`.

If the maintained P10 coordinator producer itself has a concrete defect that cannot be repaired without crossing another active ownership boundary, fail closed with a precise BLOCKED result rather than widening scope.

## Safety

Must remain:

- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- `legacySpatialFallback=false`;
- no screenshot production coordinates;
- no world-projection production coordinates;
- no guessed addresses;
- `alphaLiveMoved=false`.

Do not run real WOF for this implementation stage unless a later PM authority explicitly requests it. Do not ask Owner visual YES/NO. Do not execute promotion.

## Focused self-check

Implementation first. Use only narrow deterministic checks needed to prove the seam:

- canonical feed is exposed from the maintained P10 coordinator path;
- exact world/page/authority/runtimeEpoch/rendererEpoch identity survives the publisher seam;
- READY records retain canonical geometry from P10 only;
- SUPPRESSED records remain coordinate-free;
- stale/mismatched/cross-epoch feed is rejected;
- V3/W3-only measurement status cannot masquerade as canonical feed;
- staged cleanup/replacement does not leak old feed state.

Do not open broad QA or run real-WOF acceptance as part of P27.

## Acceptance

P27 may report `COMPLETE` only when:

1. the exact P21 staged runtime/status publisher can expose the real maintained P10 canonical coordinator feed;
2. deterministic focused tests prove exact identity preservation and fail-closed behavior;
3. no P25/P26/P22/P24/W3/P20/P23 ownership was modified;
4. no forbidden coordinate/identity fallback was introduced;
5. RESULT truthfully states real WOF `NOT_RUN`, Owner visual `NOT_RUN`, visible proof `NOT_PROVEN`, and `alphaLiveMoved=false`;
6. canonical + stage claims are closed with the exact P27 claimToken;
7. PROGRESS is updated to `TERMINAL`/100 only after durable RESULT publication and claim closeout.

If the maintained feed cannot be exposed within this boundary, write a precise `BLOCKED` RESULT and terminal checkpoint; do not guess.

## Durable progress and terminal reporting

Progress checkpointing is mandatory under:
`parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`.

Terminal reporting is mandatory under:
`parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

Required terminal paths:

- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P27_P21_STAGED_RUNTIME_CANONICAL_FEED_EXPOSURE_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P27_P21_STAGED_RUNTIME_CANONICAL_FEED_EXPOSURE_RESULT.md`

Final terminal commit prefix:

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P27_P21_STAGED_RUNTIME_CANONICAL_FEED_EXPOSURE <STATE>`

If tool/runtime/context budget becomes low, update PROGRESS before optional further work. A chat-only summary is not sufficient.