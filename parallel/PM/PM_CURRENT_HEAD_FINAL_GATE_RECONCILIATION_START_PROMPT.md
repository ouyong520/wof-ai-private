# PM Current-HEAD Final-Gate Reconciliation — Start Prompt

stageId: `PM_CURRENT_HEAD_FINAL_GATE_RECONCILIATION_V1`

Priority: **P0/P1 — Alpha final-gate coordination**

## Dedup / claim

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If this stage is already claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise create the atomic claim:
`parallel/PM/STAGE_CLAIMS/PM_CURRENT_HEAD_FINAL_GATE_RECONCILIATION_V1.json`.

## Role

You are a fresh PM reconciliation worker. This is **not** an implementation stage and not an invitation to revive old blocked verdicts mechanically.

Reconstruct the Alpha final-gate state from **main current HEAD** and durable repository facts only.

## Read first

At minimum re-read:

- current `main` HEAD and recent relevant commits;
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`;
- `parallel/PM/STAGE_DEDUP_GUARD.md`;
- `parallel/PM/OWNER_INTERVENTION_GATE.md`;
- `parallel/PM/STAGE_CLAIMS/**` relevant to Alpha / Transport / Unified Live Proof / Acceptance;
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/RESULT.md`;
- current Alpha formal real-adapter recovery claim/result;
- current Alpha acceptance current-head prep claim/result;
- `parallel/LIVE_PROOF_BUNDLE/RECORDER_AUTHORITY_GENERATION_FIX_RESULT.md`;
- latest relevant fresh QA / regression results.

Treat `ACTIVE_PRIORITIES.md` and `EXECUTION_QUEUE.md` as potentially stale historical coordination inputs until reconciled against current HEAD.

## Required reconciliation

1. Record the exact current `main` HEAD.
2. Build a current-head gate graph showing every still-material Alpha release gate as one of:
   - `ACCEPTED_COMPLETE`;
   - `ACCEPTED_WAITING_GATE`;
   - `NEEDS_FRESH_FIX`;
   - `NEEDS_FRESH_QA`;
   - `SUPERSEDED`;
   - `NO_DURABLE_RESULT`.
3. Explicitly verify the current status of:
   - Alpha Formal Real-Adapter Integration Recovery V2;
   - detector-local identity / same-targetId replacement regression hardening;
   - Unified Recorder Authority Generation Fix;
   - Alpha Acceptance Current-HEAD Prep;
   - older Formal Integration adversarial BLOCKED verdict;
   - older Alpha Release Freeze BLOCKED verdict.
4. Do not mechanically inherit an old BLOCKED verdict if a later fix/recovery supersedes it. State the superseding evidence precisely.
5. Identify the **minimum** remaining gate sequence to reach one bounded real Owner Windows/WOF proof and then Alpha release decision.
6. Decide whether each of the following is genuinely still required on current HEAD and in what order:
   - fresh Alpha formal integration QA;
   - fresh Recorder authority generation QA;
   - current-head Unified preflight/global regression;
   - bounded Owner proof;
   - bounded Browser acceptance.
7. Identify at most 2–3 fresh non-conflicting next stages that are truly unclaimed and valuable. Do not manufacture work to fill concurrency.
8. Do **not** advance WOF-052/WOF-052L long capture merely to fill a slot. Long capture remains gated by the short-runtime/release evidence path.
9. Owner action remains `NO` unless the remaining fact is intrinsically impossible to establish repository-side.

## Write boundary

Write only:

- `parallel/PM/CURRENT_HEAD_FINAL_GATE_RECONCILIATION/**`;
- mandatory stage claim file.

Do **not** edit shared `ACTIVE_PRIORITIES.md`, `EXECUTION_QUEUE.md`, implementation directories, Browser production rules, WinKawaks research lanes, or Alpha product code in this worker. If coordination docs need refreshing, record the proposed changes in your reconciliation result for the controlling PM to consume.

## Required result

Produce a durable result containing:

- exact audited HEAD;
- reconciled gate table;
- superseded old verdicts with evidence;
- exact remaining release gate sequence;
- exact fresh stage recommendations, if any;
- Owner action `YES/NO` and why.

## Stop

Success:
`PASS — CURRENT-HEAD FINAL-GATE RECONCILIATION COMPLETE — <exact next gates>`

Failure:
`BLOCKED — CURRENT-HEAD FINAL-GATE RECONCILIATION — <precise blocker>`

Owner action: **NO by default**.
