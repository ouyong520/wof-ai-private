# WOF-052L Recorder Long-Capture QA Retest — Start Prompt

stageId: `WOF052L_RECORDER_LONG_CAPTURE_QA_RETEST_V1`

Priority: **P1 — evidence infrastructure / owner-time reducer**

## Dedup / claim

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`.
If equivalent result exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`
If claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`
Otherwise claim `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_LONG_CAPTURE_QA_RETEST_V1.json`.

## Why now

Fresh Recorder live-topology/identity QA is PASS and explicitly says `READY FOR LONG-CAPTURE QA RETEST`.
The previous Recorder hardening blockers (live/live shared Worker topology transition and recreated Worker stale identity authority) have been fixed and independently rechecked.

## Goal

Retest the Recorder as a long-capture evidence producer using repository-side simulation/replay/failure injection before any Owner real WOF capture is requested.

## Read first

- current `parallel/WOF052L_RECORDER/**`
- `parallel/WOF052L_RECORDER_QA_LIVE_TOPOLOGY_IDENTITY/RESULT.md`
- previous `parallel/WOF052L_RECORDER_QA_HARDENING/RESULT.md`
- existing endurance/fleet/simulation assets
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/TRUE_LONGRUN_EXECUTION_POLICY.md`

## Required QA

At minimum exercise:
1. repeated discovery epochs across multiple simulated rooms;
2. live/live shared Worker emergence mid-capture -> affected room evidence stops before untrusted poll;
3. Worker/runtime recreation with reused targetId -> fresh exact-World proof required;
4. disconnect/reconnect and endpoint drift fail closed;
5. probe exceptions/fresh topology proof failure finalize affected room safely;
6. distinct workers/pages remain isolated;
7. polling between proof epochs cannot collect evidence without matching proof token;
8. room lifecycle/accounting remains consistent;
9. Chinese owner diagnostics remain usable;
10. no RAM writes / input injection / cross-port silent fallover.

Use current committed production modules, not copies that can drift silently.

## True long-run rule

If this stage starts a 5h+ executor, it must comply with `TRUE_LONGRUN_EXECUTION_POLICY.md`: durable checkpoints/heartbeats, exact SUT snapshot, no sleep-padding. Otherwise describe the run honestly as bounded long-capture QA, not 5h+.

Do not ask Owner to open WOF in this stage.

## Write boundary

Write only:
- `parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/**`
- mandatory PM claim

Do not modify Recorder implementation, PYLAUNCH, Live Proof, Transport, HUD, or Alpha.

## Delivery reassessment

State whether repository-side long-capture confidence is sufficient to proceed to one bounded real capture later, or whether another precise code/QA blocker remains.

## Stop

Success:
`PASS — WOF052L RECORDER LONG-CAPTURE QA RETEST — REPOSITORY GATES READY`

Or precise blocker.

Owner action: **NO**.
