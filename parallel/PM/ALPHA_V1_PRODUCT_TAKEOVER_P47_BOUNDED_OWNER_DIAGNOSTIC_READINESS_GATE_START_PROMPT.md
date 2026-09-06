# Alpha V1 P47 — Bounded Owner Diagnostic Readiness Gate

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P47_BOUNDED_OWNER_DIAGNOSTIC_READINESS_GATE`

DedupKey:
`alpha.v1.product-takeover.bounded-owner-diagnostic-readiness-gate-v1`

Fresh PM authority at dispatch:
- main: `92957360b535694cdc310a061b11e0634bbe5d68`;
- P43 terminal COMPLETE, tested commit `0c23e22b0387d0b3042c5601ab0a9e897ce1c476`, result commit `2c916da0bdaa10777e75d356e8a9975698e99835`;
- P45 terminal COMPLETE, tested commit `3dac7a9e2cbe4a23c3de44eb15cf45f19b136149`, result commit `034911b98001318e0be7d0e42ffe60df13c95d78`;
- P46 terminal COMPLETE, tested commit `210efdda5bbf3715989c751eb90442f26f42d0a9`, result commit `90a8abe2368f2c8b172aee13b7531a389985017b`;
- P40 remains terminal BLOCKED: `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`;
- no real WOF run is authorized by this task;
- no promotion or alpha-live movement is authorized.

Purpose:
Decide deterministically whether the exact P43 diagnostic candidate is ready for exactly one later PM-authorized bounded Owner live diagnostic. This is a diagnostic-run readiness gate, not the P34 final retry/promotion gate.

Required work:
1. Run fresh main + dedup-v2 preflight and acquire one new exclusive P47 claim.
2. Fresh-read terminal RESULT + closed claim provenance for P43/P45/P46.
3. Fresh-read exact P43 candidate metadata:
   - tested commit/tree;
   - `P43_POST_P45_P46_INTEGRATED_CANDIDATE.json`;
   - `P43_POST_P45_P46_DEPENDENCY_PINS.json`;
   - exact candidate/source/package/manifest/attestation provenance pointer preserved by the P43 receipt contract;
   - exact P45/P46 blob pins.
4. Verify no implementation bytes required by the diagnostic candidate changed after the exact tested candidate. Any mismatch => BLOCKED.
5. Verify P43/P45/P46 terminal state is COMPLETE, claims are closed with matching tested/result provenance, and no stale ACTIVE/PROGRESS state is treated as terminal authority.
6. Verify the later run would remain:
   - zero click / zero manual seed;
   - read-only;
   - no RAM writes;
   - no input injection;
   - bounded wall time/event/log limits;
   - deterministic teardown;
   - exact runtimeEpoch / rendererEpoch / authorityKey binding;
   - exact Page / Worker / WASM association;
   - raw P39/P42/P46 evidence preserved;
   - fail-closed on stale/mixed binding, Module/asm drift, wrapper conflict, candidate mismatch, or missing dependency.
7. Verify P46 WASM truth states remain explicit `AVAILABLE` / `NOT_AVAILABLE` / `UNRESOLVED`; guessing symbols/offsets is forbidden.
8. Verify P40/P32/P29 authority semantics are unchanged. Diagnostic correlation cannot mint renderer authority, P29 PASS, P32 qualification, retry eligibility, promotion eligibility, or source export.
9. Verify the bounded diagnostic run budget is exactly 1 if READY, else 0.
10. Output a deterministic machine-readable readiness artifact answering exactly:
    - `READY_FOR_ONE_BOUNDED_OWNER_DIAGNOSTIC`
    - or `BLOCKED`
   together with all blocker codes and exact provenance readback.

Important distinction:
- P34/P38 are historical final-retry/promotion mechanisms and must not be used to rewrite P32/P40 into ready state.
- This task may still declare the diagnostic harness READY even while P40 remains BLOCKED, because the single bounded diagnostic exists specifically to collect the missing runtime evidence.
- READY here authorizes nothing by itself. PM must separately authorize the real run after reading the terminal P47 RESULT.

Testing:
- deterministic focused tests only;
- include terminal RESULT precedence over PROGRESS;
- stale/missing P43/P45/P46 result or claim mismatch => BLOCKED;
- candidate/tree/blob/dependency-pin mismatch => BLOCKED;
- alpha-live movement or promotion flag => BLOCKED;
- run budget >1 => BLOCKED;
- exact happy-path fixture => READY_FOR_ONE_BOUNDED_OWNER_DIAGNOSTIC;
- no real game.

Progress checkpointing:
Follow `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`.

Terminal reporting:
Follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

Terminal COMPLETE means the gate implementation itself is exact-byte-tested and the current repo is truthfully classified READY or BLOCKED. It does not mean the real diagnostic ran and does not resolve P40.
