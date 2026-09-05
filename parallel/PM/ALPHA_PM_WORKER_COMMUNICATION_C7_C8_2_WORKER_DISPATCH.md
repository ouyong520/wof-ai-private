# Alpha PM Worker Communication — C7/C8 2-Worker Dispatch

Scope: PM/Worker coordination mechanism only. No Alpha product runtime/HUD/renderer/updater changes. Collector / Unified Collector / Training Farm / 10训 are out of scope.

Current accepted inputs:
- C1 result envelope/validator COMPLETE.
- C2 immutable dispatch manifest + fast reader COMPLETE.
- C3 dispatch contract enforcement COMPLETE.
- C4 dispatch package builder COMPLETE.
- C5 current dispatch resolver COMPLETE.
- C6 terminal result publisher is an independent ACTIVE implementation and must not be modified by C7/C8.

Owner directive: implementation-first. Build the requested coordination capability end-to-end, use only minimal self-checks needed to avoid obvious breakage, and defer broad QA/regression until the communication mechanism reaches a coherent candidate.

## C7 — PM Current Dispatch Activator

Start prompt:
`parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C7_CURRENT_DISPATCH_ACTIVATOR_START_PROMPT.md`

Goal: implement the PM-only missing write side of the C5 pointer contract. Given one already-built immutable manifest, produce/validate the exact next `parallel/PM/CURRENT_DISPATCH.json` content with monotonic revision, previous-dispatch identity, exact authority commit, and exact manifest SHA-256; support create/update planning and post-write verification without letting ordinary workers mutate the pointer.

## C8 — Result Evidence Verifier

Start prompt:
`parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C8_RESULT_EVIDENCE_VERIFIER_START_PROMPT.md`

Goal: implement a fast structural evidence verifier for terminal RESULT.json. It must check that declared implementation commits exist in the local Git history, materially touch the declared changed files, and do not rely only on claim/result/docs commits; emit concise discrepancies/acceptability for PM integration intake. This is structural verification, not product QA.

## File separation

C7 owns only new PM activation tool/protocol/supporting coordination files and its own RESULT artifacts. It may consume but must not rewrite C1-C6 implementation files.

C8 owns only new result-evidence tool/protocol/supporting coordination files and its own RESULT artifacts. It may consume but must not rewrite C1-C7 implementation files.

Neither worker may write `parallel/PM/CURRENT_DISPATCH.json`; that file remains PM/coordinator-owned. Neither worker may modify product code or move `alpha-live`.

## Terminal reporting

Both workers must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md` and write the exact RESULT paths declared by the immutable manifest for this dispatch.
