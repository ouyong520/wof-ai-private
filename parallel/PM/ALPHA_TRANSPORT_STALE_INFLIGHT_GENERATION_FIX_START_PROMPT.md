# Alpha Safe Transport — Stale In-Flight Generation Fix — Fresh Stage

stageId: `ALPHA_TRANSPORT_STALE_INFLIGHT_GENERATION_FIX_V1`
priority: `P1`

## Dedup / claim
Read `parallel/PM/STAGE_DEDUP_GUARD.md` and `parallel/PM/DELIVERY_REASSESSMENT_GATE.md` first.
If equivalent work is already complete or claimed, use the standard dedup stop message. Otherwise claim under `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_STALE_INFLIGHT_GENERATION_FIX_V1.json` before writing implementation files.

## Why now
Fresh independent QA found a real warning-authority race in `parallel/ALPHA_TRANSPORT_IMPL/**`: unresolved detector work from pair generation 1 can complete after a rebind, consume the generation-2 in-flight slot, and be stamped with the current mutable generation-2 pair/nonce. This can make stale evidence authoritative after rebind.

Authoritative QA result:
- `parallel/ALPHA_TRANSPORT_IMPL_QA/RESULT.md`
- blocker: `STALE_INFLIGHT_COMPLETION_RELABELED_AFTER_REBIND`

This must close before formal real-adapter integration.

## Write scope
Write only under:
- `parallel/ALPHA_TRANSPORT_IMPL/**`
- mandatory stage claim

Do not modify real-adapter prep, PYLAUNCH, Recorder, HUD, Prospective, Owner package, or production Alpha files.

## Required fix properties
1. Every started detector tick captures immutable authority identity containing at least runtime epoch + session + pair generation + pair nonce, or an equivalent unique tick token.
2. Completion may publish only if that captured identity is still the current authoritative runtime/pair.
3. Stale completion from an old runtime/pair is ignored/revoked and must never be relabeled with current mutable pair state.
4. Old completion must never consume, clear, or corrupt the new generation's in-flight slot.
5. Rebind/reinstall/Worker replacement invalidates all old tick authority immediately.
6. Preserve one detector tick in flight and no catch-up queue/backpressure buildup.
7. Preserve warning-change/clear immediacy and bounded heartbeat behavior.
8. Preserve exact World 921031 identity gate and all fail-closed warning authority semantics.
9. Preserve `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no Worker replacement/wrap, no Blob/ObjectURL rewrite.

## Required regression
At minimum add deterministic coverage for:
- generation 1 tick unresolved;
- rebind/install generation 2;
- generation 2 starts a valid tick;
- generation 1 completes first;
- old result publishes nothing and does not touch generation-2 in-flight ownership;
- generation 2 then completes normally and is authoritative;
- repeat across Worker/runtime epoch replacement and reconnect/rebind;
- rerun frozen 67-vector contract catalog after targeted regression.

## Stop condition
Success:
`ALPHA TRANSPORT STALE IN-FLIGHT GENERATION FIX READY — READY FOR FRESH QA`

Or one precise blocker requiring different ownership.

Repository-side only. Owner Browser/WOF action: `NO`.
