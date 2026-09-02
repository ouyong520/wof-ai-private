# WOF Alpha Safe Transport — True 5h+ Endurance Recovery V2

stageId: `ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_RECOVERY_V2`

Priority: **P1/P2 release robustness gate — do not outrank fresh P0/P1 QA**

Governed by:

- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/TRUE_LONGRUN_EXECUTION_POLICY.md`

## PM reconciliation finding

V1 is **not** a transport-defect failure and is **not** a valid 5h PASS.

Authoritative V1 evidence:

- workflow run: `33528136552`;
- run head: `8e23ead5e9bc632a0f39747af843ef0c3b53f20f`;
- segment-0 job: `99924615364`;
- segment-0 checkpoint status: `PASS`;
- segment-0 actual elapsed: `1500048 ms` (~25 min);
- segment-0 failureCount: `0`;
- frozen control: `67/67 PASS`;
- V1 aggregate: only `1/13` checkpoints, actual executor `0.417 h`, therefore correctly `BLOCKED` against the >=5h success stop.

The concrete CI infrastructure defect is deterministic:

1. At run-head `8e23ead...`, `parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE/checkpoints/` did not exist.
2. The workflow ran `node ... 2>&1 | tee parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE/checkpoints/segment-${segment}.log` with `set -o pipefail` before creating that directory.
3. `tee` therefore could not open its log target, while Node continued running the 25-minute workload.
4. The Node runner itself later created the checkpoint directory while writing JSON and completed segment 0 with PASS/zero failures.
5. The pipeline still returned failure because `tee` had failed; `fail-fast: true` then cancelled the other 12 matrix jobs.
6. The uploaded segment-0 artifact contains the PASS JSON checkpoint but no `.log`, corroborating the failed tee path.

Do not reinterpret V1 as PASS and do not modify Safe Transport implementation to fix this CI bug.

## Dedup / claim

Before work, re-read latest main, V1 claim/result, Actions runs, and any newer equivalent endurance claim/result.

If a newer genuine >=5h current-SUT endurance already satisfies the success stop, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If an equivalent recovery/long-run claim is ACTIVE, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_RECOVERY_V2.json`

with `state=ACTIVE` and exact start commit.

## Upstream gate

Before consuming multi-hour compute, verify:

- no current P0/P1 Safe Transport implementation blocker is open;
- the exact reference SUT/input blobs are still identifiable;
- the V1 pinned blobs remain current, or V2 explicitly repins a newer accepted snapshot;
- any concurrent Formal Integration fresh QA has not discovered a core transport defect that makes the soak misleading.

V1 pinned snapshot was:

- `ALPHA_TRANSPORT_IMPL/constants.mjs` -> `a29cb3ad714598e2e6aeeed64acc9e3eca8b221e`
- `ALPHA_TRANSPORT_IMPL/page_authority.mjs` -> `5e53bd2ad40823a8768802df0a1c5431adb19ee9`
- `ALPHA_TRANSPORT_IMPL/worker_runtime.mjs` -> `c353b4500640e31950cde42173a934d541f22531`
- `ALPHA_TRANSPORT_IMPL/acceptance_adapter.mjs` -> `d79dff0b2708c671ab8a11644fcc4f771ec75003`
- frozen mock blobs exactly as recorded in V1 final-summary.

If the relevant SUT changed, do not mix V1 and V2 elapsed time; run V2 from zero on one exact snapshot.

## Goal

Repair only the durable-executor infrastructure defect, then obtain a genuine >=5h non-idle deterministic endurance result on one exact Safe Transport snapshot.

## Required recovery

At minimum:

1. ensure the log/checkpoint directory exists **before** starting `tee` (for example `mkdir -p .../checkpoints`);
2. keep `pipefail` so a real Node invariant failure still fails the segment;
3. preserve non-zero failure on actual BLOCKED checkpoint / invariant violation;
4. preserve durable checkpoint upload/mirroring;
5. ensure a normal PASS segment returns success to Actions;
6. retain sequential/non-overlapping execution so actual wall-clock span and executor duration are honest;
7. retain or improve final aggregation so PASS requires all intended checkpoints and >=5h actual elapsed;
8. do not pad duration with sleep.

Before launching the full run, use a short infrastructure-only smoke (not counted toward 5h evidence) proving a PASS segment produces both JSON and log and exits 0, while a deliberate negative control exits non-zero.

## True-longrun requirements

The final V2 executor must satisfy `TRUE_LONGRUN_EXECUTION_POLICY.md`:

- intended wall-clock >=5h;
- continuously varying deterministic workload;
- exact SUT/input blobs pinned;
- durable checkpoint at least every 30 minutes;
- no idle padding;
- frozen 67-vector control throughout;
- exact safety assertions throughout;
- final machine-readable aggregate with actual executor and wall-clock duration.

Required stress families remain at least the V1 set: stale completion/rebind, session changes, pair generation/nonce churn, runtime epoch reset, Worker replacement/reinstall, disconnect/reconnect, stale-boundary, warning clear/change race, heartbeat timing, one-in-flight/no-catch-up, unsupported/supported transitions, out-of-order completion, allowed legacy compatibility, failure-injection around publish/clear/revoke.

## Read / write boundary

Read/test the accepted Safe Transport implementation and frozen inputs.

Write only:

- `parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE_V2/**`;
- a dedicated V2 workflow such as `.github/workflows/alpha-transport-true-5h-endurance-v2.yml`;
- the V2 stage claim.

Do **not** modify:

- `parallel/ALPHA_TRANSPORT_IMPL/**`;
- `product/alpha/**`;
- Formal Integration implementation;
- PYLAUNCH / Recorder / Live Proof / Owner OneClick / HUDANCHOR.

If a real implementation defect is discovered, stop with precise blocker; do not fix it here.

## Downstream consumer

- Alpha Release Freeze current-HEAD recheck;
- robustness evidence supporting final current-head acceptance.

This lane is not allowed to self-promote Formal Integration fresh QA or Recorder fresh QA.

## Drift rule

Each checkpoint and final summary must pin the exact SUT/input blobs. If any relevant SUT/input changes during the run, stop and classify evidence stale; do not combine elapsed time across different snapshots.

## Success stop

Only after actual durable executor elapsed >=5h, actual wall-clock span >=5h, all intended checkpoints PASS, zero invariant failures, frozen controls green, and exact snapshot unchanged:

`ALPHA TRANSPORT TRUE 5H ENDURANCE V2 PASS — READY AS CURRENT-SNAPSHOT ROBUSTNESS EVIDENCE`

Update claim COMPLETE with run id, run head, exact blobs, actual durations, checkpoint count, unique scenarios, control results, safety, and result paths.

## Failure stop

On precise P0/P1 defect, snapshot invalidation, unrecoverable CI infrastructure failure, or true-longrun success criteria not met:

`BLOCKED — ALPHA TRANSPORT TRUE 5H ENDURANCE V2 — <precise blocker>`

Update claim BLOCKED with durable evidence.

Owner action: **NO**.