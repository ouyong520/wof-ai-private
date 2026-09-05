stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P4_FIRST_OWNER_GATE_INTEGRATION_WIRING`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.first-owner-gate.integration-wiring-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P4_FIRST_OWNER_GATE_INTEGRATION_WIRING_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P4_FIRST_OWNER_GATE_INTEGRATION_WIRING_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P4_FIRST_OWNER_GATE_INTEGRATION_WIRING`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_PRODUCT_TAKEOVER_P4_FIRST_OWNER_GATE_INTEGRATION_WIRING_V1.json`

# Alpha V1 Product Takeover P4 — First Owner Gate Integration Wiring

Repository: `ouyong520/wof-ai-private`

Read latest `main`, then read:
- `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_FIRST_OWNER_GATE_PARALLEL_3_WORKER_V2_DISPATCH.md`
- `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P1_RUNTIME_FIXED_TEST_GATE_SUBRESULT.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P2_PERMANENT_LAUNCHER_GATE_MODE_SUBRESULT.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P3_OWNER_FEEDBACK_ACCEPTANCE_HARNESS_SUBRESULT.md`
- accepted W1/W2 durable results referenced by the parent dispatch
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`
- this prompt's immutable manifest.

Scope: Alpha Owner-visible product only. Collector / Unified Collector / Training Farm / 10训 are forbidden. Do not start W3 renderer qualification, P1 geometry, enemy logic, danger logic, semantic acquisition, zero-click work, or broader QA in this stage.

## Ownership

Perform dedup-v2 exactly as declared: latest-main preflight -> create-only canonical claim -> re-read exact claimToken -> create-only stage claim -> re-read exact same claimToken. Any create/verification failure is fail-closed. Do not invent recovery.

## Product goal

P1/P2/P3 are individually implementation-ready, but the first Owner gate is not complete until the permanent Alpha path automatically produces one continuously useful feedback artifact while the fixed TEST runtime is active.

Finish the runtime-side integration so the real product chain is coherent:

`permanent WOF_ALPHA_TEST.cmd -> alpha-live fixed-draw-first-gate -> WOF_ALPHA_FIXED_DRAW_SMOKE=1 -> fixed-draw runtime -> ALPHA_FIXED_DRAW_STATUS.json -> P3 feedback classifier -> LATEST_ALPHA_FEEDBACK.txt`

Owner must not run a separate Python helper, DevTools command, environment-variable command, or hunt internal files.

## Required implementation

Prefer a narrow integration in the fixed-draw runtime domain, for example `parallel/PYLAUNCH/wof_launcher/fixed_draw_runtime_gate.py` plus only a tiny new helper if genuinely needed. Do not redesign P1/P2/P3.

Required behavior:

1. While fixed-draw gate mode is active, every meaningful fixed-smoke status update must also refresh the P3 Owner feedback classifier automatically, or refresh it at a bounded cadence sufficient to keep `LATEST_ALPHA_FEEDBACK.txt` current.
2. Reuse `wof_launcher.owner_feedback_acceptance.write_feedback`; do not duplicate P3 classification logic.
3. The integration must remain independent of P1 identity, semantic evidence, screenshot tracking, enemy data, projection, click fallback, and W3 renderer authority.
4. Missing/malformed P3 feedback helper execution must not crash the fixed TEST runtime or fabricate green state. Preserve the fixed status artifact and surface a precise integration error/fail-closed condition where practical.
5. Preserve P1 machine proof vs Owner visual proof separation. `FIXED_TEST_ACTUALLY_DRAWN` may produce `MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL` but never Owner visual PASS.
6. Preserve read-only safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.
7. Flag OFF / normal Alpha behavior must remain unchanged.
8. Do not move `alpha-live`; PM owns promotion after accepting this integration result.
9. Do not ask Owner to test. PM will ask only after the candidate is promoted.

## Implementation-first cadence

Prioritize wiring the full chain. Only minimum self-checks are expected: Python parse/compile, one bounded fixed-status -> feedback refresh smoke using local/temp artifacts, and one fail-closed helper-error case. Do not create broad regression suites, Fresh QA, second opinion, or additional audit stages.

## Exit

Deliver an integration-ready implementation commit that makes the feedback loop automatic, then write the exact manifest-declared RESULT.json and RESULT.md. Clearly report implementation commits, changed files, minimal self-checks, remaining external/live boundary, and exact PM next action.

Final terminal result commit subject begins:

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P4_FIRST_OWNER_GATE_INTEGRATION_WIRING <STATE>`

Return only COMPLETE / SUBCOMPLETE / precise BLOCKED in chat.
