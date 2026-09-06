# Alpha V1 P43 — Post-P45/P46 Continuation Prompt

This is a continuation of the existing P43 claim, not a new stage, not recovery, and not a new dedup generation.

Existing stageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P43_BOUNDED_ZERO_CLICK_LIVE_DIAGNOSTIC_HARNESS`

Existing dedupKey:
`alpha.v1.product-takeover.bounded-zero-click-live-diagnostic-harness-v2`

Existing exact claimToken:
`9b45b04fc8f5e86849c08c07dcf0dc07`

Fresh PM authority at continuation dispatch:
- current main observed at dispatch: `4e2bc3a253236e2b4f489b3695c99183d2d61164`;
- P45 terminal COMPLETE, tested candidate `3dac7a9e2cbe4a23c3de44eb15cf45f19b136149`, result commit `034911b98001318e0be7d0e42ffe60df13c95d78`;
- P45 provides the default-off maintained staging wrapper that injects exact P39 then exact P42 and returns the full bound P39/P42 diagnostic readout;
- P46 terminal COMPLETE, exact tested commit `210efdda5bbf3715989c751eb90442f26f42d0a9`, result commit `90a8abe2368f2c8b172aee13b7531a389985017b`;
- P46 provides bounded raw JS stack + normalized call-site fingerprint + browser-exposed WASM index/name/offset truth states + JS wrapper identity + Module/Module.asm identity + exact buffer/setup-to-draw association;
- P40 remains terminal BLOCKED: `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`;
- no Owner live run is authorized by this continuation.

Before further substantive work:
1. re-read latest main;
2. re-read the existing canonical/stage P43 claim and verify the exact token above is still ACTIVE;
3. re-read current P43 PROGRESS and reconcile all P43 commits newer than its stale checkpoint, including the already-published harness/P42 integration commits;
4. update the existing P43 PROGRESS before further implementation so durable progress reflects Git reality.

Required continuation work:
- keep P43 as the single owner of the bounded live diagnostic harness; do not create any new claim;
- consume P45 rather than duplicating its P39/P42 staging integration;
- add exact P46 call-site evidence to the same bounded diagnostic orchestration so one later authorized run can preserve, in one session:
  - P39 P1/P2/P3 visible/hidden/lost/stale/ambiguous/reacquire state;
  - complete P42 raw renderer-correlation bundle, seal reason and teardown;
  - complete P46 raw call-site bundle, including raw stack, normalized fingerprint, exact observed WASM fields or explicit `NOT_AVAILABLE` / `UNRESOLVED`, JS wrapper frame identity, Module/Module.asm identity, event/draw sequence and exact object/state associations;
  - exact `runtimeEpoch` / `rendererEpoch` / `authorityKey` binding across all diagnostic evidence;
  - exact sourceCommit / packageVersion / candidate / manifest / attestation and Page / Worker / WASM association already owned by P43;
  - raw runtime / console / staging logs and first failing gate chronology;
- preserve wrapper composition safely: P46 must observe the real WebGL boundary before/around P42 without timing/order guessing; if both directly wrap the same GL methods, use deterministic wrapper-stack/LIFO semantics consistent with P46's documented contract and record teardown conflicts rather than overwriting an external wrapper;
- stale/mixed binding or Module/asm identity drift must fail closed and preserve raw rejection reason;
- if the browser does not expose wasm function identity/name/offset, persist explicit truth states instead of guessing;
- the final receipt/archive must keep the P42 and P46 raw bundles unfiltered enough for later source-mapping analysis.

Authority boundary remains unchanged:
- P39/P42/P46 evidence is diagnostic only;
- do not create `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__` or `WOFNativeMarkerRendererSubmitSourceV1`;
- do not mint `rendererSourceProof`, P29 PASS, P32 qualification, retry eligibility or promotion eligibility;
- timing-only/order-only/nearest/screenshot/OCR/template/guessed WASM symbol/guessed offset can never become authority;
- do not modify P45/P46 terminal evidence or reopen their claims.

Scope:
- P43-owned harness/entrypoint/docs/tests and the minimum glue required to consume exact P45/P46 are in scope;
- do not open a new stage/claim;
- no real WOF run, Owner YES/NO, promotion, RAM write, input injection, or alpha-live movement.

Before terminal-significant self-check create/freeze one durable exact integrated P43 candidate containing the final harness bytes and exact dependency pins, fresh-read its tree/blob identities, then run the focused deterministic regression once against those bytes. Any implementation-byte change afterward requires a new candidate and affected rerun.

Progress checkpointing must follow `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`; update the existing P43 PROGRESS at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

Terminal COMPLETE means: the existing P43 harness is exact-byte-tested and ready to capture P45 + P46 together in one later PM-authorized bounded live diagnostic. It does not mean the live diagnostic ran and does not resolve P40.
