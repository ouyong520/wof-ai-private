# Alpha V1 Final Acceptance — Zero-Click Renderer — Long 3 Worker Dispatch

DispatchId: `ALPHA_V1_FINAL_ACCEPTANCE_ZERO_CLICK_RENDERER_LONG_3_WORKER_V1`

Fresh PM state:
- P29/P30/P31 terminal COMPLETE and PM-accepted at repo-side authority boundaries.
- P32 terminal BLOCKED with `NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN`.
- P33 terminal COMPLETE: deterministic post-repair rebuild mechanism.
- P34 terminal COMPLETE: fail-closed final retry readiness gate.
- P35 terminal COMPLETE: exact accepted-repair integration source `82b0b09ecd902f502ae5509bcb3ee5a713f43fee` containing exact P29/P30/P31 tested commits as true ancestors.
- Product requirement is zero-click automatic player acquisition; manual avatar/portrait click or seed is not an acceptable final product path.

Use exactly three project Worker slots:

1. P36 `ALPHA_V1_PRODUCT_TAKEOVER_P36_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_TRACE`
   - critical blocker attack;
   - source-trace displayed CPS1 renderer/object submission to exact native `1P/2P/3P + down-arrow` object/cluster and actor generation;
   - preserve P29/P32 proof standards.

2. P37 `ALPHA_V1_PRODUCT_TAKEOVER_P37_ZERO_CLICK_NATIVE_MARKER_AUTO_ACQUISITION_BASELINE`
   - recover historical automatic native-label/arrow tracking as an isolated **zero-click** diagnostic baseline;
   - explicitly test/fix Y-axis orientation;
   - always label output non-authoritative and never satisfy rendererSourceProof/P34 readiness;
   - provide correlation evidence to P36 without editing P36 ownership surfaces.

3. P38 `ALPHA_V1_PRODUCT_TAKEOVER_P38_ACCEPTED_REPAIR_INTEGRATED_CANDIDATE_MATERIALIZATION`
   - consume exact P35 source through terminal P33 rebuild mechanism;
   - materialize/read back one fresh accepted-repair integrated candidate/provenance;
   - explicitly keep it `NOT_RETRY_ELIGIBLE_PENDING_P36`;
   - no promotion or Owner run.

No Worker may duplicate another stage's ownership. P36 and P37 must remain strictly separated: P37 proves functional zero-click acquisition behavior only; P36 alone owns authoritative direct renderer source proof. P38 owns only package/candidate materialization.

All three stages must follow dedup-v2, mandatory PROGRESS checkpointing, durable exact tested-candidate semantics, focused self-check, terminal RESULT, and exact-token claim close. No real WOF run, no Owner YES/NO, no alpha-live movement, no RAM writes/input injection, and no global environment changes under this dispatch.

Codex remains local Windows deployment/runner only and is not assigned repository implementation work.
