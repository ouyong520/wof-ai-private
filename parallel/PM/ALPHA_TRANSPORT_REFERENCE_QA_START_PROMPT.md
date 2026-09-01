# Alpha Safe Transport Reference Implementation — Fresh Independent QA Start Prompt

stageId: `ALPHA_TRANSPORT_REFERENCE_QA_V1`
priority: `P1`

## Dedup / claim
Follow `parallel/PM/STAGE_DEDUP_GUARD.md`. If equivalent complete/claimed work exists, use the standard exact dedup stop message. Otherwise claim under `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_REFERENCE_QA_V1.json`.

## Why now
`parallel/ALPHA_TRANSPORT_IMPL/**` reports the frozen Safe Transport reference implementation ready and compatible with the existing 67-vector contract. A separate real-adapter prep lane is active. Independently validate the reference semantics now so formal integration does not inherit an unreviewed reference bug.

## Read first
- `parallel/ALPHA_TRANSPORT_IMPL/RESULT.md`
- current `parallel/ALPHA_TRANSPORT_IMPL/**`
- `parallel/ALPHA_TRANSPORT_MOCK/**`
- frozen Safe Transport contract documents
- RC5 safety/bootstrap contract as read-only context

## Independent QA focus
Do not merely rerun the same 67 vectors. Add adversarial coverage around boundaries most likely to fail during real adapter wiring:
1. session/tab/page exact isolation;
2. pairGeneration + pairNonce + seq stale/replay rejection;
3. Worker replacement/reload resets old authority immediately;
4. reconnect/rebind cannot revive an old generation;
5. exact World 921031 handshake and detector-local identity disagreement fail closed for warnings;
6. stale state/warning/diag authority thresholds and boundary values;
7. warning clear/change publication vs bounded heartbeat;
8. one detector tick in-flight; missed intervals skipped, no catch-up queue/backpressure buildup;
9. multi-tab/session cross-talk impossible;
10. target retarget/stale warning cannot survive onto another player/session;
11. transport failure keeps gameplay fail-open while warning authority fails closed;
12. adapter exceptions cannot cause game RAM writes/input injection;
13. `readOnly=true / ramWrites=0 / inputInjection=false` mandatory and immutable;
14. no Worker replacement/wrap / Blob/Data/ObjectURL rewrite;
15. no automatic production promotion from mock/reference success.

Re-run the frozen 67-vector catalog as regression after adversarial tests, but treat it as baseline rather than sole QA evidence.

## Write scope
Write only under:
- `parallel/ALPHA_TRANSPORT_IMPL_QA/**`
- mandatory claim file
Do not modify `parallel/ALPHA_TRANSPORT_IMPL/**`, active real-adapter prep, PYLAUNCH, Recorder, Alpha product, or HUD.

## Stop condition
Success:
`PASS — ALPHA TRANSPORT REFERENCE IMPLEMENTATION FRESH INDEPENDENT QA`
Or one precise blocker with required fresh-fix ownership.

Repository-side only. No Owner Browser/WOF run.
Owner action: `NO`.
