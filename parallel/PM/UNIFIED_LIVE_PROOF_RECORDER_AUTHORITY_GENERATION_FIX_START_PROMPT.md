# WOF Unified Live Proof — Recorder Authority Generation Replay Fix Start Prompt

stageId: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_FIX_V1`

Priority: **P1 — Alpha release gate**

## Dedup / claim

Before doing work, follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If this stage is already claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise claim under:
`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_FIX_V1.json`

## Why this stage exists

Fresh independent QA of the Recorder authority heartbeat fix found a remaining P1:

**stale prior-generation Recorder heartbeat/admission replay is not generation-bound and can revive authority.**

Authoritative evidence:
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/RESULT.json`
- claim `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_QA_V1` closed BLOCKED

## Goal

Bind every Recorder heartbeat/admission authority update to the exact current runtime/admission generation so that evidence from an older generation can never refresh or revive the newer generation's authority.

## Read first

Re-read current HEAD before work, especially:
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/**`
- `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_QA_V1.json`
- current Fleet/Recorder supervisor heartbeat/admission schema and lifecycle
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/DELIVERY_REASSESSMENT_GATE.md` if present

## Required semantics

1. Heartbeat/admission freshness must carry an immutable generation/session/authority token or equivalent current-generation proof.
2. A stale prior-generation heartbeat/admission replay must be ignored and must not refresh freshness.
3. Rebind/restart/reconnect/generation rollover must revoke prior authority immediately.
4. Generic stdout must remain non-authoritative.
5. A stale message must never consume, clear, or mutate the current generation's authority slot.
6. Same-generation valid heartbeat/admission remains accepted.
7. Fail closed if generation metadata is missing where authority requires it.
8. Preserve existing preflight/freshness/read-only behavior.

## Hard write boundary

Allowed:
- `parallel/LIVE_PROOF_BUNDLE/**`
- mandatory stage claim file

Do not modify:
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `product/alpha/**`
- Alpha Transport implementation
- HUDANCHOR
- Owner OneClick

## Required regression

Add deterministic regression covering at least:
- generation 1 valid heartbeat -> generation 2 starts -> replay generation 1 heartbeat -> generation 2 authority remains unchanged;
- generation 1 admission replay after generation 2 -> ignored;
- current generation heartbeat/admission still refreshes normally;
- missing/wrong generation fails closed;
- reconnect/restart invalidates old generation;
- delayed/out-of-order events;
- generic stdout cannot refresh authority;
- current Unified preflight and freshness regressions remain green.

Re-run the fresh QA blocker-directed fixture against the real SUT.

## Delivery reassessment

Before closing, state explicitly:
- whether the fresh QA P1 is actually closed;
- whether a fresh independent QA rerun is now unblocked;
- whether this changes the Alpha release critical path;
- whether Owner action is needed (expected NO).

## Stop condition

Success:
`UNIFIED RECORDER AUTHORITY GENERATION FIX READY — READY FOR FRESH QA`

Or one precise blocker requiring a different ownership lane.

Owner action: **NO**.
