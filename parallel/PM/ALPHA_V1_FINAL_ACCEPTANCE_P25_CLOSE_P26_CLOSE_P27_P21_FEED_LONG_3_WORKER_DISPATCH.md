# Alpha V1 Final Acceptance — P25 Close + P26 Close + P27 P21 Feed — Long 3 Worker Dispatch

Status: **CURRENT PM DISPATCH AUTHORITY CANDIDATE**

Purpose: use three independent slots without duplicating ownership:

1. P25 reattaches its existing ACTIVE claim and performs terminal `BLOCKED` publication only.
2. P26 reattaches its existing ACTIVE claim and performs terminal `COMPLETE` Git publication only.
3. P27 creates a new dedup-v2 claim for the independently proven upstream P21 staged-runtime canonical-feed exposure defect.

## Slot 1 — P25 terminal BLOCKED closeout

Stage:
`ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION`

Existing claimToken:
`1a8e410f279e1450057986f7e8212959`

Read first:
`parallel/PM/PROGRESS/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_PROGRESS.json`

Do not create a new claim or recovery. Do not change implementation. Preserve the proven blocker `P21_STAGED_RUNTIME_CANONICAL_FEED_NOT_EXPOSED` and `canonicalFeed.state=NOT_EXPOSED_BY_STAGED_RUNTIME_STATUS`. Publish truthful BLOCKED RESULT, close matching canonical/stage claims as BLOCKED, then update PROGRESS to TERMINAL/100.

## Slot 2 — P26 terminal COMPLETE publication

Stage:
`ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN`

Existing claimToken:
`d60b10ee92743c2181969d475ac93164`

Read first:
`parallel/PM/PROGRESS/ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN_PROGRESS.json`

Do not create a new claim or recovery. Do not redesign provenance. Reconcile latest main, verified implementation/test blobs and ownership; perform only non-force terminal Git publication, RESULT `COMPLETE` with `integrationReady=true` if readback is truthful, close matching claims, then update PROGRESS to TERMINAL/100.

## Slot 3 — P27 P21 staged canonical feed exposure

Stage:
`ALPHA_V1_PRODUCT_TAKEOVER_P27_P21_STAGED_RUNTIME_CANONICAL_FEED_EXPOSURE`

START_PROMPT:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P27_P21_STAGED_RUNTIME_CANONICAL_FEED_EXPOSURE_START_PROMPT.md`

This is a new logical repair with dedup key:
`alpha.v1.product-takeover.p21-staged-runtime-canonical-feed-exposure-v1`

It may begin only after normal dedup-v2 claim acquisition and checkpoint creation. Repair only the real P21 staged-runtime/status seam so it exposes the maintained P10 canonical coordinator feed. It must not modify P25/P26-owned files or terminal artifacts.

## Independence / no-overlap rule

- P25 slot owns only P25 terminal artifacts/claims/progress; no implementation changes.
- P26 slot owns P26 implementation publication plus its terminal artifacts/claims/progress; no P25 or P27 changes.
- P27 slot owns only its narrow P21 staged-runtime canonical-feed exposure repair and its own claim/progress/result.
- P27 must not wait for P25 terminal publication merely to begin code inspection; P25's durable checkpoint already establishes the blocker. It must still re-read current Git before writing.
- P25 terminal BLOCKED remains historical truth even if P27 later fixes the upstream seam. Do not rewrite P25 to COMPLETE retroactively.

## Global constraints

All three workers must obey root `AGENTS.md`, dedup-v2, testing cadence, durable PROGRESS checkpointing and terminal RESULT reporting.

No slot may move `alpha-live`, run promotion, invent Owner visual proof, use input injection, write emulator/process RAM, or introduce screenshot/world-projection/guessed production coordinates.

No broad QA. No P28. Real WOF remains a later concentrated acceptance gate after these repository streams reach terminal truth.