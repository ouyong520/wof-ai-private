# WOF Alpha Safe Transport — Real Adapter Integration Prep Start Prompt

stageId: `ALPHA_TRANSPORT_REAL_ADAPTER_PREP_V1`

## Dedup / claim

Before doing work, follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If this stage is already claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise atomically claim this stage under `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_REAL_ADAPTER_PREP_V1.json` and continue.

## Role

You own **repository-side preparation for wiring the already-complete Alpha Safe Transport reference implementation into the real WOF stack**.

This is a mainline accelerator. Do not modify the live components currently being fixed by other lanes.

## Read first

Re-read current HEAD including:
- `parallel/ALPHA_TRANSPORT_IMPL/**`
- `parallel/ALPHA_TRANSPORT_MOCK/**`
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `product/alpha/**`
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`

Current known reference implementation status:
- reference selftest 8/8 PASS
- existing Safe Transport acceptance catalog 67/67 PASS
- readOnly=true / ramWrites=0 / inputInjection=false
- no Worker replacement / no Blob rewrite

## Goal

Build a durable **real-adapter integration prep layer** so that after current Discovery/PYLAUNCH/Unified-Proof fixes stabilize, formal Alpha integration is mostly controlled adapter wiring rather than architecture work.

## Hard write boundary

Write only under:
- `parallel/ALPHA_TRANSPORT_INTEGRATION_PREP/**`
- mandatory PM stage claim file

Do NOT modify:
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `product/alpha/**`
- `parallel/ALPHA_TRANSPORT_IMPL/**`

## Required deliverables

Create a concrete integration-prep package containing at minimum:

1. **Discovery adapter contract**
   - exact page/Worker pair input shape
   - World 921031 identity authority input
   - session/page/target/generation lifecycle
   - no dependence on unstable internal implementation details

2. **Native Worker runtime adapter contract**
   - read-only probe/install/status/stop interfaces
   - WASM/heap readiness
   - runtime epoch / Worker replacement invalidation
   - no RAM writes / no gameplay input

3. **Alpha detector adapter contract**
   - consume canonical pinned Alpha core rather than duplicate predicates
   - state/warning/diag authority boundaries
   - stale/disable/error invalidation

4. **Page/HUD adapter contract**
   - page-owned generation bind/reset
   - fixed HUD first-release output contract
   - future player-head HUD anchor may plug in later without changing warning semantics

5. **Deterministic adapter fixtures / tests**
   - one valid exact pair
   - wrong World reject
   - stale generation reject
   - Worker replacement reset
   - reconnect/rebind
   - cross-tab/session isolation
   - missing WASM/heap fail closed for warnings
   - gameplay remains fail-open
   - readOnly/no-input invariants

6. **Integration wiring plan**
   - exact files/interfaces that formal integration will touch later
   - identify which current in-flight blockers must be closed first
   - no speculative redesign

7. **Current-HEAD drift check**
   - before finalizing, re-read current HEAD of PYLAUNCH/Recorder/Live Proof and confirm the prep layer is interface-compatible or explicitly record a narrow blocker

## Acceptance

The prep is READY only if:
- no current core component/product file was modified;
- adapters are executable/testable in isolation;
- they reuse the existing 67-vector transport semantics rather than weaken them;
- they reduce formal integration to bounded wiring work;
- no Owner Browser/WOF action is requested.

## Stop conditions

Success:
`ALPHA TRANSPORT REAL ADAPTER PREP READY`

Or stop with one precise repository-side blocker that cannot be resolved within this isolated scope.

Owner action: `NO`.
