# Alpha Worker Progress Checkpoint Protocol V1

Status: **AUTHORITATIVE — MANDATORY FOR ALL PM-DISPATCHED ALPHA WORKERS**

Purpose: make unfinished work durably inspectable. A worker chat may stop, time out, lose tool budget, or finish implementation before terminal Git publication. PM must never have to infer progress from an `ACTIVE` claim alone.

This protocol is additive to:

- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`

## 1. Mandatory per-stage progress file

After the canonical claim **and** stage claim are both created and re-read with the exact matching `claimToken`, and before meaningful implementation work begins, every Alpha worker must create:

`parallel/PM/PROGRESS/<stageId>_PROGRESS.json`

This file belongs only to that stage/claim token. Workers must never update another stage's progress file and must not create a shared mutable worker dashboard.

The progress file is a durable checkpoint, **not a heartbeat**. It records the last known completed work even if the chat later stops.

## 2. Required schema

Every progress file must conform to `parallel/PM/PROGRESS/worker-progress.schema.json` and contain at least:

```json
{
  "schema": "wof-alpha-worker-progress-v1",
  "stageId": "...",
  "dedupKey": "...",
  "claimToken": "...",
  "claimStateAtCheckpoint": "ACTIVE",
  "workState": "IMPLEMENTING",
  "overallPercent": 45,
  "implementationState": "IN_PROGRESS",
  "selfCheckState": "NOT_RUN",
  "resultPublicationState": "NOT_STARTED",
  "claimCloseState": "PENDING",
  "startCommit": "<sha>",
  "lastKnownGoodCommit": "<sha-or-null>",
  "implementationCommits": [],
  "completed": [],
  "remaining": [],
  "tests": [],
  "blocker": null,
  "nextAction": "one concrete next action",
  "terminalResultPath": null,
  "writerRole": "WORKER",
  "updatedAtUtc": "..."
}
```

`completed` and `remaining` are more authoritative than the percentage. `overallPercent` is a bounded progress estimate for Owner/PM triage, not acceptance proof.

## 3. Work-state vocabulary

`workState` must be exactly one of:

- `CLAIMED` — ownership acquired; implementation not started.
- `IMPLEMENTING` — implementation is actively incomplete at this checkpoint.
- `SELF_CHECK` — implementation is substantially present and focused self-check is in progress.
- `READY_TO_PUBLISH` — implementation/self-check are done; terminal Git publication remains.
- `BLOCKED_PENDING_RESULT` — a real blocker is known; terminal BLOCKED result still needs publication/claim close.
- `PUBLISHING` — RESULT/claim closeout is currently being written.
- `INTERRUPTED` — worker intentionally records that it is stopping before terminal result.
- `TERMINAL` — RESULT is durable and canonical/stage claim closeout is complete.

`ACTIVE` in a claim never means the chat is currently running. It means only that the logical claim has not reached terminal closeout.

## 4. Percentage rules

- `0..99` is allowed while `workState != TERMINAL`.
- `100` is allowed only when `workState == TERMINAL`, `resultPublicationState == DONE`, and `claimCloseState == DONE`.
- `READY_TO_PUBLISH` should normally be about `90..99`.
- `BLOCKED_PENDING_RESULT` may also be high if implementation is complete; the blocker and `remaining` fields must explain what prevents terminal success.
- A worker must never use `100` merely because code or tests are done.

## 5. Mandatory checkpoint moments

The worker must update the progress file at all of these boundaries:

1. immediately after canonical + stage claim verification;
2. after the first durable implementation commit or equivalent durable implementation milestone;
3. after every coherent implementation milestone that materially changes `completed` / `remaining`;
4. immediately after focused self-check completes or fails;
5. immediately when a real blocker is discovered;
6. immediately before terminal RESULT publication / claim closeout;
7. before voluntarily ending the chat while the claim is non-terminal;
8. **before continuing additional work when tool/runtime/context budget is visibly low** — checkpoint publication takes priority over optional extra implementation or tests.

Workers do not need to update every few minutes. The requirement is milestone durability, not noisy heartbeat commits.

## 5A. Final tested-candidate durability — tests must bind to durable bytes

Any test result that will be cited by terminal RESULT as proof for an implementation candidate must be bound to durable Git identity before it can become final test provenance.

Rules:

1. before the final focused/self-check pass, create a durable implementation candidate commit (or another explicitly authorized immutable Git tree/ref) containing the exact bytes to be tested;
2. record that exact candidate commit/tree SHA in PROGRESS before or immediately with the final test checkpoint;
3. when practical, record the exact changed-file set and file/blob identity needed to re-read the tested candidate later;
4. run the terminal-significant focused tests against that exact durable candidate, not only workspace/unpublished bytes;
5. if any implementation byte changes after the test, create a new durable candidate and rerun every affected terminal-significant focused check; old test results must not be rebound to the new bytes;
6. RESULT/testedCommit must identify the final durable tested candidate actually covered by the reported tests;
7. workspace-only tests may still be used during implementation as cheap self-checks, but they must be labeled nonterminal and cannot by themselves justify `COMPLETE`, `integrationReady=true`, or a terminal tested-byte claim;
8. if tool/context budget becomes low after testing but before publication, PROGRESS must durably record the tested candidate SHA, test result, exact remaining publication work, and any required blob/file map before stopping.

A worker must never report historical tests as applying to regenerated, reconstructed, or otherwise different bytes merely because the logical implementation is similar. If the exact tested bytes cannot be identified durably, fail closed and either run fresh tests on a new durable candidate under valid authority or publish a precise blocker.

This rule is mandatory specifically to prevent the failure mode: **tests PASS, but the tested bytes have no durable Git identity and therefore cannot be safely published or verified later.**

## 6. Update safety

Before every worker-authored progress update:

1. re-read the canonical claim;
2. verify the exact `claimToken` still matches;
3. verify the claim is still compatible with the intended checkpoint (`ACTIVE` for non-terminal work; matching terminal state for final checkpoint);
4. update only the stage's own progress path using the current blob SHA / non-force semantics.

If token verification fails, do not overwrite the progress file or any claim. Fail closed.

## 7. Blockers and interrupted work

If a blocker is found before RESULT publication:

- write `workState=BLOCKED_PENDING_RESULT` immediately;
- record a precise blocker object/string;
- list exactly what implementation/tests are already complete;
- list only the remaining terminalization or upstream dependency work;
- do not leave the only blocker description in chat.

If the worker must stop for time/tool/context reasons without a product blocker, use `workState=INTERRUPTED` and state the exact resume action. The claim normally remains `ACTIVE`; a continuation reattaches the same claim/token unless PM explicitly authorizes recovery.

## 8. Terminal checkpoint

The final progress update must agree with the durable RESULT and claims:

- `workState=TERMINAL`;
- `overallPercent=100`;
- `resultPublicationState=DONE`;
- `claimCloseState=DONE`;
- `terminalResultPath` points to the exact RESULT JSON;
- `claimStateAtCheckpoint` is the real terminal claim state (`COMPLETE`, `BLOCKED`, or the authority-approved terminal equivalent).

The RESULT remains the terminal acceptance authority. PROGRESS never replaces RESULT.

## 9. PM reconstruction for already-interrupted legacy/current work

If an existing claimed stage predates this protocol or its worker stopped before creating/updating PROGRESS, PM may create or repair **only the progress file** from Git evidence plus the worker's explicit status report.

Such a checkpoint must use:

`"writerRole": "PM_RECONSTRUCTION"`

and must not fabricate unpublished commits, tests, product proof, or claim closure. PM reconstruction does **not** mutate worker ownership and does not convert an `ACTIVE` claim to terminal.

A reattached worker must read this checkpoint first, verify the exact claim token, reconcile any newer Git work, then continue from the listed `remaining` work.

## 10. PM status-read algorithm

When the Owner asks for progress, PM must read in this order:

1. terminal RESULT (if present);
2. canonical + stage claim;
3. per-stage PROGRESS;
4. recent implementation commits newer than the checkpoint.

Interpretation:

- RESULT + correctly closed matching claim => terminal truth.
- `ACTIVE` claim + PROGRESS => report the **last durable checkpoint**, not "currently running".
- Owner says the worker stopped + matching `ACTIVE` claim => treat as interrupted logical work and reattach the same token unless a terminal RESULT already exists.
- `ACTIVE` claim with no PROGRESS => report `LEGACY_PROGRESS_UNKNOWN`, inspect Git, and reconstruct a checkpoint before dispatching continuation.
- commits newer than `lastKnownGoodCommit`/checkpoint => progress file may be stale; continuation must reconcile before new implementation.

PM must never infer live execution merely from `state=ACTIVE`.

## 11. Future prompt requirement

Every new Alpha worker prompt and every non-terminal continuation should contain:

`Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.`

This requirement does not authorize extra scope, extra tests, claim recovery, or ownership changes.
