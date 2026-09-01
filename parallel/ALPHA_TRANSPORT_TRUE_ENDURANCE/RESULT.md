# Alpha Safe Transport — True 5h+ Endurance

## Verdict

**BLOCKED — ALPHA TRANSPORT TRUE 5H ENDURANCE DID NOT SATISFY SUCCESS STOP**

## Duration

- Intended executor duration: 5.417 h (19500000 ms)
- Actual executor elapsed: 0.417 h (1500048 ms)
- Actual wall-clock span: 0.417 h (1500098 ms)
- Checkpoints: 1/13

## Generated evidence

- Unique generated scenarios: 76962239
- Failure count: 0
- Stress family counts: `{"stale-old-completion-rebind":5497303,"session-change":5497303,"pair-generation-nonce-churn":5497303,"runtime-epoch-reset":5497303,"worker-replacement-reinstall":5497303,"disconnect-reconnect":5497303,"stale-warning-expiry-boundary":5497303,"warning-clear-change-race":5497303,"heartbeat-timing-variation":5497303,"skipped-tick-one-in-flight-no-catch-up":5497303,"unsupported-supported-transition":5497303,"out-of-order-completion":5497302,"legacy-untagged-compatible":5497302,"failure-injection-publish-clear-revoke":5497302}`
- Seed/scenario coverage and rolling evidence hashes: see `final-summary.json`.

## Frozen control

The frozen 67-vector catalog was rerun as a control gate in each completed segment. Per-segment results are recorded in `final-summary.json`.

## Safety

`readOnly=true / ramWrites=0 / inputInjection=false / workerReplacement=false / blobRewrite=false`

## Exact SUT / input blobs

`{"ALPHA_TRANSPORT_IMPL/constants.mjs":"a29cb3ad714598e2e6aeeed64acc9e3eca8b221e","ALPHA_TRANSPORT_IMPL/page_authority.mjs":"5e53bd2ad40823a8768802df0a1c5431adb19ee9","ALPHA_TRANSPORT_IMPL/worker_runtime.mjs":"c353b4500640e31950cde42173a934d541f22531","ALPHA_TRANSPORT_IMPL/acceptance_adapter.mjs":"d79dff0b2708c671ab8a11644fcc4f771ec75003","ALPHA_TRANSPORT_MOCK/fixtures.json":"35bf36b4c741cda5d94be3f9884511a86653c11f","ALPHA_TRANSPORT_MOCK/vectors.json":"5a0cbe2ccfcf7eb6e875552f56748f736722c14d","ALPHA_TRANSPORT_MOCK/expected_results.json":"1231e0946d18068284724d92e732ea185e4e6af8"}`

## Integration reassessment

NO CHANGE AUTHORIZED — investigate blocker before changing integration requirements.

Owner action: **NO**.
