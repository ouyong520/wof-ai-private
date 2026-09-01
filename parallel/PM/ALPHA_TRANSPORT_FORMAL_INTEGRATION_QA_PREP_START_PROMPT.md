# WOF Alpha Safe Transport — Formal Integration QA Prep Start Prompt

stageId: `ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP_V1`

Priority: **P1 mainline accelerator**

## Dedup / claim

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable QA-prep artifact exists:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If claimed/executing:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise claim:
`parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP_V1.json`

## Purpose

Prepare an **independent fresh-QA harness** while formal real-adapter integration is being implemented, so that integration delivery can enter fresh QA immediately instead of waiting for a new test design cycle.

This stage does not certify the integration and must not edit its implementation.

## Read first

Re-read current HEAD:

- `parallel/ALPHA_TRANSPORT_QA_STALE_GENERATION/**`
- `parallel/ALPHA_TRANSPORT_IMPL/**`
- `parallel/ALPHA_TRANSPORT_REAL_ADAPTER_PREP/**` if present
- `parallel/PM/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_START_PROMPT.md`
- current `product/alpha/**` only to understand existing public seams; do not modify
- current safe bootstrap / RC5 contracts

## Hard write boundary

Write only:

- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/**`
- mandatory stage claim

Do not modify:

- `product/alpha/**`
- `parallel/ALPHA_TRANSPORT_IMPL/**`
- formal integration implementation directory
- PYLAUNCH / Recorder / Live Proof / Owner One-Click / HUD / Prospective.

## Harness requirements

Build a fresh, independent acceptance harness that can be pointed at the final formal-integration SUT once it exists.

Do not copy implementation assertions blindly. Derive acceptance from frozen product/safety contracts.

Cover at minimum:

1. normal adapter attach -> warning publish -> clear;
2. no adapter/discovery unavailable -> silent fail-closed, game unaffected;
3. old unresolved completion after pair rebind -> rejected;
4. new generation completion remains live after old completion returns;
5. runtime epoch reset revokes prior tick authority;
6. Worker replacement/reinstall revokes prior authority;
7. session/pair-generation/pair-nonce mismatch rejected;
8. disconnect/reconnect clears stale state;
9. heartbeat/staleness and warning clear/change timing preserved;
10. unsupported identity/admission never produces warning;
11. one-in-flight/no-catch-up/queueDepth=0 invariants;
12. Chinese owner-facing failure/status surfaces where the integrated path exposes them;
13. exact safety invariants: read-only, zero RAM writes, no input injection, no Worker replacement, no Blob rewrite;
14. current RC5/bootstrap failure leaves game path unaffected.

Prepare machine-readable expected outcome schema and a runner that refuses to claim PASS if the formal integration SUT is absent or its expected public seam has drifted.

## Current-head drift rule

Before closing, re-read the formal integration claim/result if it appeared while this prep was running.

- If integration is not yet delivered: stop as `HARNESS READY — WAITING SUT`.
- If integration is delivered and the seam matches: record exact SUT blob that a future fresh QA must consume, but do not self-upgrade this prep lane into final QA.
- If the seam drifted incompatibly: document the delta and stop without editing the implementation.

## Stop condition

`ALPHA FORMAL INTEGRATION QA HARNESS READY — WAITING FRESH QA SUT`

This is a prep completion, **not** integration PASS.

Owner action: **NO**.
