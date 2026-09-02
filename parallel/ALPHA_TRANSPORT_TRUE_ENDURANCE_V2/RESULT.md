# Alpha Safe Transport — True 5h+ Endurance Recovery V2

Stage: `ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_RECOVERY_V2`

## Verdict

**ALPHA TRANSPORT TRUE 5H ENDURANCE V2 PASS — READY AS CURRENT-SNAPSHOT ROBUSTNESS EVIDENCE**

## Durable run identity

- Workflow run ID: `33577350728`
- Workflow run attempt: `1`
- Run head SHA: `de2c86fb3fe528907aad08cd45d8944e3054f680`
- V1 elapsed reused: **NO**

## Duration

- Intended executor duration: 5.417 h (19500000 ms)
- Required minimum: 5.000 h (18000000 ms)
- Actual executor elapsed: 5.417 h (19500882 ms)
- Actual wall-clock span: 5.476 h (19713232 ms)
- Durable checkpoints: 13/13

## Generated evidence

- Unique generated scenarios: 1086849482
- Failure count: 0
- Stress family counts: `{"stale-old-completion-rebind":77632112,"session-change":77632111,"pair-generation-nonce-churn":77632110,"runtime-epoch-reset":77632108,"worker-replacement-reinstall":77632108,"disconnect-reconnect":77632108,"stale-warning-expiry-boundary":77632108,"warning-clear-change-race":77632107,"heartbeat-timing-variation":77632104,"skipped-tick-one-in-flight-no-catch-up":77632103,"unsupported-supported-transition":77632102,"out-of-order-completion":77632101,"legacy-untagged-compatible":77632100,"failure-injection-publish-clear-revoke":77632100}`
- Frozen 67-vector controls passing 67/67: 13/13
- Seed ranges and rolling evidence hashes: see `final-summary.json`.

## Infrastructure recovery proof

- The V2 workflow creates the checkpoint/log directory before `tee`.
- `pipefail` is preserved; the preflight negative smoke proves a failing runner pipeline returns non-zero.
- The positive smoke produces both JSON and log and is explicitly excluded from endurance duration.
- Execution is max-parallel=1 across 13 x 25-minute non-idle stress segments; there is no sleep padding.
- V1 elapsed evidence is not aggregated into V2.

## Safety

`readOnly=true / ramWrites=0 / inputInjection=false / workerReplacement=false / blobRewrite=false`

## Exact SUT / input blobs

`{"ALPHA_TRANSPORT_IMPL/constants.mjs":"a29cb3ad714598e2e6aeeed64acc9e3eca8b221e","ALPHA_TRANSPORT_IMPL/page_authority.mjs":"5e53bd2ad40823a8768802df0a1c5431adb19ee9","ALPHA_TRANSPORT_IMPL/worker_runtime.mjs":"c353b4500640e31950cde42173a934d541f22531","ALPHA_TRANSPORT_IMPL/acceptance_adapter.mjs":"d79dff0b2708c671ab8a11644fcc4f771ec75003","ALPHA_TRANSPORT_MOCK/fixtures.json":"35bf36b4c741cda5d94be3f9884511a86653c11f","ALPHA_TRANSPORT_MOCK/vectors.json":"5a0cbe2ccfcf7eb6e875552f56748f736722c14d","ALPHA_TRANSPORT_MOCK/expected_results.json":"1231e0946d18068284724d92e732ea185e4e6af8"}`

## Current-main drift gate

`{"status":"PASS","exactPinnedBlobsStillCurrent":true}`

## Blocker

None.

## Integration reassessment

NONE — endurance evidence does not require a reference integration contract change.

Owner action: **NO**.
