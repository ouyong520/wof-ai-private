# WOF Alpha Safe Transport — Formal Real-Adapter Integration Start Prompt

stageId: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_V1`

Priority: **P0/P1 — Alpha mainline integration**

## Dedup / claim

Before work, follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise claim under:
`parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_V1.json`

## Why this stage is now allowed

Fresh independent QA has closed the former stale in-flight generation P1 and explicitly reports:

`PASS — ALPHA TRANSPORT STALE IN-FLIGHT GENERATION FRESH QA — READY FOR FORMAL REAL-ADAPTER INTEGRATION`

Re-read current HEAD before doing anything. Do not rely on this prompt's snapshot alone.

## Read first

- `parallel/ALPHA_TRANSPORT_IMPL/**`
- `parallel/ALPHA_TRANSPORT_QA_STALE_GENERATION/**`
- `parallel/ALPHA_TRANSPORT_REAL_ADAPTER_PREP/**` if present
- `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_STALE_INFLIGHT_GENERATION_QA_V1.json`
- current `product/alpha/**`
- current RC5/bootstrap safety invariants
- current PYLAUNCH/Discovery interface contracts as **read-only external dependencies**
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- `parallel/PM/PM_DELIVERY_REASSESSMENT_GATE.md` or `parallel/PM/DELIVERY_REASSESSMENT_GATE.md` if present

## Goal

Perform the first **formal production-facing real-adapter integration** of the accepted Safe Transport reference contract into the Alpha path.

The integration must consume the stable real-adapter preparation/contracts already built, preserve the immutable per-tick authority fix, and keep RC5 startup safety/fail-closed semantics.

This stage is repository-side integration. **Do not request Owner Browser/WOF testing.**

## Required product semantics

Preserve all of the following:

- no `window.Worker` replacement/wrap;
- no Blob/ObjectURL Worker rewrite;
- no gameplay input injection;
- no RAM writes;
- exact World 921031 identity remains external admission authority, not guessed here;
- stale/rebound/replaced runtime completions cannot publish into a newer pair/session/generation;
- one detector tick in flight; no catch-up burst; `queueDepth=0` behavior preserved;
- invalid/stale authority clears or suppresses warnings fail-closed;
- unsupported state stays silent;
- game remains playable if adapter/discovery/transport is unavailable.

## Integration boundary

The formal integration must not copy old PYLAUNCH/Recorder discovery logic into Alpha. Consume the current external discovery/identity surface through a narrow adapter boundary.

If PYLAUNCH fresh QA is still running, integration may proceed against its current documented interface, but must:

1. keep the dependency isolated;
2. not self-certify PYLAUNCH correctness;
3. re-read current HEAD before finalization;
4. stop on any incompatible authority/interface change rather than patching PYLAUNCH from this lane.

## Hard write boundary

Allowed:

- `product/alpha/**`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/**`
- mandatory stage claim file

Do not modify:

- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/OWNER_ONECLICK/**`
- HUDANCHOR implementation/proof lanes
- Prospective Validator

## Required work

1. Pin/re-read the accepted Safe Transport source + frozen contract provenance.
2. Wire the real adapter boundary into the Alpha runtime without weakening RC5 bootstrap safety.
3. Carry immutable `tickAuthority` through the real asynchronous detector completion path.
4. Prove rebind/session/runtime-epoch/Worker replacement revokes prior completion authority end-to-end through the integrated path.
5. Preserve current warning clear/change heartbeat and pair/session isolation semantics.
6. Add deterministic integration tests for:
   - normal attach/produce/clear;
   - no transport / no supported runtime;
   - stale generation completion after rebind;
   - runtime epoch replacement;
   - Worker replacement;
   - session/pair nonce mismatch;
   - disconnect/reconnect;
   - unsupported identity/discovery result fail-closed;
   - game path remains unaffected on integration failure.
7. Re-run frozen 67-vector Safe Transport catalog or equivalent byte-pinned consumer gate.
8. Re-run current Alpha/RC4/RC5 safe-bootstrap regressions relevant to changed files.
9. Produce machine-readable result and Chinese summary.
10. Before final result, re-read current external interface blobs; if they drifted incompatibly, stop with one precise blocker instead of claiming integration-ready.

## Delivery reassessment

Before closing, explicitly state:

- whether this actually moves Alpha from reference-only transport to integrated real-adapter path;
- what fresh independent integration QA is newly unblocked;
- whether Owner One-Click package refresh must be rerun after this integration;
- whether a true 5h+ integration endurance is now valid;
- remaining repository-side blockers;
- Owner action required: expected `NO`.

## Stop conditions

Success:
`ALPHA FORMAL REAL-ADAPTER INTEGRATION READY — READY FOR FRESH INTEGRATION QA`

Or one precise P0/P1 blocker requiring a fresh ownership lane.

Owner action: **NO**.
