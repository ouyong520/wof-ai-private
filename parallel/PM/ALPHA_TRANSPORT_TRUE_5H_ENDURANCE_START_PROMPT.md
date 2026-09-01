# WOF Alpha Safe Transport — True 5h+ Endurance Start Prompt

stageId: `ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_V1`

Priority: **P1 accelerator — directly protects Alpha formal integration**

This stage is governed by:
`parallel/PM/TRUE_LONGRUN_EXECUTION_POLICY.md`

## Dedup / claim

Follow `parallel/PM/STAGE_DEDUP_GUARD.md` first.

If equivalent durable long-run result already exists:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If claimed/executing:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise claim:
`parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_V1.json`

## Admission gate

Do not launch unless current HEAD still proves:

- `ALPHA_TRANSPORT_STALE_INFLIGHT_GENERATION_QA_V1` = COMPLETE/PASS;
- the accepted Safe Transport reference SUT blobs are identifiable and byte-pinnable;
- no newer P0/P1 transport blocker has appeared.

If any gate fails, stop before consuming long-run compute.

## Goal

Launch a **real durable executor intended to run at least 5 hours wall-clock** when no P0/P1 stop condition occurs.

This is not a large matrix that finishes in minutes and is not a sleep timer. Every execution segment must generate new decision-changing transport stress evidence.

Downstream consumer:

- formal real-adapter integration;
- fresh integration QA;
- eventual bounded Windows/WOF proof.

## SUT / write boundary

Read/test only current accepted Safe Transport reference implementation and frozen contract inputs.

Write only:

- `parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE/**`
- one dedicated workflow if needed: `.github/workflows/alpha-transport-true-5h-endurance.yml`
- mandatory stage claim

Do not modify:

- `parallel/ALPHA_TRANSPORT_IMPL/**`
- `product/alpha/**`
- PYLAUNCH / Recorder / Live Proof / Owner One-Click / HUD / Prospective implementation lanes.

If a real implementation defect is found, stop with a precise blocker; do not fix it in this endurance lane.

## True-longrun requirements

The executor must satisfy `TRUE_LONGRUN_EXECUTION_POLICY.md`, including:

1. intended runtime >= 5 hours;
2. no padding with idle sleeps to reach duration;
3. continuously varying deterministic seeds/scenario families;
4. exact SUT blob/input snapshot recorded;
5. durable checkpoint/heartbeat at least every 30 minutes;
6. checkpoints include elapsed runtime, completed scenario count, seed range, failure count, latest invariant status;
7. if using CI, structure checkpoints so partial progress survives a later runner failure (for example sequential segments with uploaded checkpoint artifacts/log evidence);
8. one final machine-readable summary with actual elapsed executor time.

If CI/runtime limits or repository permissions make a genuine 5h durable executor impossible, stop and report that exact infrastructure blocker. Do not call a shorter run `5h+`.

## Stress families

Continuously generate non-identical scenarios spanning at minimum:

- unresolved old tick -> rebind -> new tick -> old completion first;
- session changes;
- pair generation + nonce churn;
- runtime epoch resets;
- Worker replacement/reinstall;
- disconnect/reconnect cycles;
- stale warning expiry boundary;
- warning clear/change races;
- heartbeat timing variation;
- skipped tick / one-in-flight / no-catch-up pressure;
- repeated unsupported/supported transitions;
- out-of-order completion sequences;
- legacy untagged completion only where current compatibility contract permits;
- deterministic failure injection around publish/clear/revoke boundaries.

Every generated case must keep safety assertions active:

`readOnly=true / ramWrites=0 / inputInjection=false / workerReplacement=false / blobRewrite=false`

Run the frozen 67-vector catalog periodically as a control gate, but do not count repeated identical catalog reruns as the substantive long-run workload.

## Early stop

Stop before 5h only for:

- precise P0/P1 defect;
- SUT/input snapshot invalidation that makes continuing misleading;
- infrastructure failure preventing durable execution;
- mathematically/empirically demonstrated convergence where further execution cannot change the decision.

If early-stopped, report intended duration and actual elapsed duration explicitly. Never call it a completed 5h soak.

## Success stop condition

Only after actual durable executor elapsed time >= 5 hours with no blocker:

`ALPHA TRANSPORT TRUE 5H ENDURANCE PASS — READY AS INTEGRATION ROBUSTNESS EVIDENCE`

Result must include:

- intended duration;
- actual elapsed duration;
- checkpoint count;
- unique generated scenario count;
- seed/scenario coverage;
- frozen catalog control results;
- safety invariants;
- exact SUT/input blobs;
- whether any integration requirement should change.

Owner action: **NO**.
