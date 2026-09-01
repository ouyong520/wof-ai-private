# WOF052L Recorder Live Topology / Identity — Fresh Independent QA Start Prompt

## PM stage

- stageId: `WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_QA_V1`
- priority: **P0/P1 mainline verification**
- purpose: independently verify the just-delivered Recorder live-topology evidence gate and identity-lifecycle cache fix before long-capture QA is allowed.
- Owner Browser/WOF: **NOT REQUIRED** for this repository-side stage.

## Mandatory dedup / claim guard

Before doing substantive work, inspect `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_QA_V1.json` if it exists.

- If a durable PASS/BLOCKED result for this exact stage already exists, stop with `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`.
- If the exact stage is currently claimed ACTIVE by another thread, stop with `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.
- Otherwise create the claim and continue.

Do not treat implementation-thread READY as QA proof.

## Read first

Re-read current default-branch HEAD and at minimum:

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/PRIORITY_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_FIX/RESULT.md`
- current production files under `parallel/WOF052L_RECORDER/**`
- prior Recorder hardening QA findings/results, especially the live/live shared-Worker ambiguity and reused-target identity-cache blockers.

The SUT must be current HEAD. If Recorder implementation changes while this QA is running, re-read affected blobs and rerun affected vectors before final verdict.

## Write scope

QA may write only:

- `parallel/WOF052L_RECORDER_QA_LIVE_TOPOLOGY_IDENTITY/**`
- `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_QA_V1.json`

Do **not** modify `parallel/WOF052L_RECORDER/**` implementation. A defect requires a fresh fix stage.

## Independent QA requirements

Build fresh adversarial coverage against the real production modules, not only copies of developer tests. At minimum prove:

1. already-live unique page/Worker -> second live page becomes related to same Worker inside the old audit interval: affected room is finalized **before any later evidence poll/admission**;
2. polling between discovery proof epochs cannot collect/admit evidence;
3. discovery/probe exception or missing exact current pair fails closed and cannot defer buffered evidence into a later successful epoch;
4. reused Worker `targetId` on a new runtime/session with wrong World identity must fresh-probe and reject; old cache authority must not carry over;
5. reused `targetId` on a correct recreated runtime must fresh-probe before readmission;
6. same still-live CDP session may reuse only its own proven identity authority;
7. two distinct pages/two distinct Workers remain independently live/admissible;
8. endpoint/port confinement remains fail-closed; no silent cross-port fallover;
9. ambiguity/finalization cannot corrupt room accounting, autosave, or unrelated-room isolation;
10. Chinese owner-facing failure text remains intact;
11. exact World 921031 SHA authority remains required;
12. `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no Worker replacement/wrap, no Blob/ObjectURL rewrite, no gameplay Input capability.

Run current relevant existing regressions plus the fresh QA fixture. Use the current Windows workflow evidence where useful, but do not accept it as a substitute for independent adversarial QA.

## PM meaning

A PASS here closes the Recorder P0/P1 repository gate and allows a **fresh WOF052L long-capture QA retest** to be scheduled. It does **not** authorize a real 1h Owner capture by itself.

## Stop conditions

PASS only if no P0/P1 repository-side blocker remains:

`PASS — WOF052L RECORDER LIVE TOPOLOGY IDENTITY FRESH QA — READY FOR LONG-CAPTURE QA RETEST`

If a precise P0/P1 blocker is found, record reproduction + impact + required fresh-fix ownership and stop:

`BLOCKED — WOF052L RECORDER LIVE TOPOLOGY IDENTITY FRESH QA — <precise blocker>`

Owner action must remain `NO` for this stage.