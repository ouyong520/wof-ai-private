# Alpha Safe Transport Stale In-Flight Generation Fresh QA Start Prompt

stageId: `ALPHA_TRANSPORT_STALE_INFLIGHT_GENERATION_QA_V1`
priority: `P1`

## Purpose
Independently re-test the reference Safe Transport after `ALPHA_TRANSPORT_STALE_INFLIGHT_GENERATION_FIX_V1`. Do not accept the implementation thread's READY verdict as proof. Verify that an unresolved detector completion from an old runtime/session/pair generation cannot be relabeled or published under a newer pair after rebind/reinstall/runtime epoch reset/Worker replacement.

## Dedup / claim guard
Before any work:
1. Read `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_STALE_INFLIGHT_GENERATION_QA_V1.json` if present.
2. If already COMPLETE/PASS: return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`.
3. If ACTIVE elsewhere: return `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.
4. Otherwise claim that exact stage path.

## Allowed write scope
- `parallel/ALPHA_TRANSPORT_QA_STALE_GENERATION/**`
- `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_STALE_INFLIGHT_GENERATION_QA_V1.json`

Do NOT modify `parallel/ALPHA_TRANSPORT_IMPL/**`, `parallel/ALPHA_TRANSPORT_MOCK/**`, `product/alpha/**`, PYLAUNCH, Recorder, HUDANCHOR, or other implementation lanes.

## Required fresh QA
Independently cover at minimum:
1. generation 1 unresolved tick -> rebind generation 2 -> old completion publishes nothing;
2. old completion cannot clear or steal generation-2 in-flight ownership;
3. generation-2 completion still succeeds normally afterward;
4. runtime epoch reset revokes old tick authority;
5. Worker replacement revokes old tick authority;
6. reinstall/rebind/session change revokes old tick authority;
7. legacy/untagged completion after unresolved revoke fails closed;
8. current valid synchronous/reference compatibility remains intact where no unresolved revoke occurred;
9. one-tick-in-flight, skipped-tick, no-catch-up queue, queueDepth=0 invariants remain intact;
10. stale/fresh boundary, warning clear/change immediacy, heartbeat timing and pair/session isolation remain intact;
11. rerun the frozen Safe Transport V01-V67 catalog unchanged and verify 67/67;
12. verify `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`, `blobRewrite=false`.

Fresh adversarial tests must not reuse only the implementation lane's new fixture; include at least one independently constructed stale-completion ordering.

## Delivery reassessment requirement
Final result must state whether the former P1 is truly closed, whether formal real-adapter integration is now unblocked, and whether any remaining blocker belongs to the reference contract or only downstream integration.

## Stop conditions
PASS:
`PASS — ALPHA TRANSPORT STALE IN-FLIGHT GENERATION FRESH QA — READY FOR FORMAL REAL-ADAPTER INTEGRATION`

BLOCKED:
`BLOCKED — ALPHA TRANSPORT STALE IN-FLIGHT GENERATION FRESH QA — <exact P0/P1 blocker>`

Owner Browser/WOF: NO for this repository-side QA.