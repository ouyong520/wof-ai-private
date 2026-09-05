# Alpha Worker Result Fast Feedback Protocol V1

Scope: Alpha Owner-visible product only.

Purpose: make every worker completion instantly auditable by PM without re-reading the whole thread or manually reconstructing what changed.

## 1. Mandatory worker terminal output

Every worker that reaches SUBCOMPLETE, COMPLETE, or BLOCKED must create exactly two durable result artifacts under `parallel/PM/RESULTS/`:

1. Human-readable Markdown:
   `parallel/PM/RESULTS/<stageId>_RESULT.md`
2. Machine-readable JSON:
   `parallel/PM/RESULTS/<stageId>_RESULT.json`

The JSON is the PM fast-path. The Markdown is the detailed evidence path.

Do not create a shared mutable global index from worker threads; parallel workers must not race on one status file.

## 2. Mandatory final commit message

The commit that adds the terminal result artifacts must use this exact searchable prefix:

`WORKER_RESULT <stageId> <STATE>`

Where `<STATE>` is exactly one of:

- `SUBCOMPLETE`
- `COMPLETE`
- `BLOCKED`

Examples:

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P1_RUNTIME_FIXED_TEST_GATE COMPLETE`

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P3_OWNER_FEEDBACK_ACCEPTANCE_HARNESS BLOCKED`

PM can therefore inspect the latest repository commits and find terminal worker results immediately.

## 3. Required machine-readable JSON schema

Every `<stageId>_RESULT.json` must contain at least:

```json
{
  "schema": "wof-alpha-worker-result-v1",
  "stageId": "...",
  "dedupKey": "...",
  "claimToken": "...",
  "state": "SUBCOMPLETE|COMPLETE|BLOCKED",
  "verdict": "one short factual sentence",
  "startCommit": "<sha>",
  "implementationCommits": ["<sha>"],
  "integrationReady": true,
  "changedFiles": ["path"],
  "tests": [
    {
      "name": "focused test name",
      "result": "PASS|FAIL|NOT_RUN",
      "detail": "short detail"
    }
  ],
  "productProof": {
    "status": "PROVEN|NOT_PROVEN|NOT_APPLICABLE",
    "detail": "what is actually proven"
  },
  "ownerGate": {
    "required": false,
    "question": null,
    "reason": null
  },
  "blocker": null,
  "nextAction": "single next action for PM",
  "evidencePaths": ["path"],
  "safety": {
    "readOnly": true,
    "ramWrites": 0,
    "inputInjection": false
  }
}
```

Additional fields are allowed, but these keys must not be omitted.

## 4. Verdict rules

`verdict` must answer only one question: **what did this worker actually achieve?**

Good:

`Runtime now enables and polls maintained fixed TEST smoke before P1 acquisition when gate mode is active.`

Bad:

`Work completed successfully.`

Do not claim product-visible success unless that exact product behavior was actually proven.

## 5. implementationCommits

`implementationCommits` must contain only commits that changed the implementation owned by this worker.

Do not include:

- claim-only commits;
- PM prompt commits;
- unrelated concurrent commits;
- documentation-only commits unless the worker is documentation-only.

This lets PM inspect the exact code delta immediately.

## 6. changedFiles

List only materially changed files owned by the worker. Paths must be repository-relative and exact.

This allows PM to detect file-boundary violations without diffing the entire repository.

## 7. Test reporting

Every test entry must state PASS / FAIL / NOT_RUN.

Do not write vague statements such as `tests look good`.

If a real-WOF or Owner-visible test was not run, explicitly use `NOT_RUN` and explain why.

## 8. Product proof separation

Workers must distinguish implementation proof from Owner-visible proof.

Examples:

- fixed smoke unit/focused tests pass -> implementation proof only;
- machine state says `FIXED_TEST_ACTUALLY_DRAWN` -> maintained renderer machine proof;
- Owner says TEST is visible in real WOF -> Owner visual proof.

One must never be substituted for another.

## 9. Owner gate

If the worker has reached the exact point where Owner evidence is unavoidable:

```json
"ownerGate": {
  "required": true,
  "question": "固定 TEST 是否持续显示在真实 WOF 游戏画面？",
  "reason": "machine draw proof exists; only visual persistence remains unproven"
}
```

Workers may identify the gate but must not ask the Owner directly unless their authority explicitly permits it. PM owns Owner interaction.

## 10. BLOCKED reporting

When state is BLOCKED, `blocker` must be an object:

```json
{
  "code": "PRECISE_MACHINE_CODE",
  "detail": "one precise sentence",
  "ownerRequired": false,
  "pmRequired": true,
  "recoveryAllowedByWorker": false
}
```

No vague `blocked by environment` wording.

If blocked by dedup/claim handling, the worker must fail closed and set `nextAction` to the exact PM action needed.

## 11. Claim closeout

A worker may report COMPLETE only after its own canonical/stage claim state is correctly closed according to its authority.

If implementation is ready but the logical stream intentionally remains ACTIVE for later evidence, use SUBCOMPLETE and explain the remaining dependency.

## 12. PM fast-read procedure

When the Owner sends `1`, `1 2`, or `1 3`, PM should use this fast path:

1. read latest main commits;
2. search the recent commit list for `WORKER_RESULT`;
3. open each new `<stageId>_RESULT.json` first;
4. from JSON immediately determine:
   - worker state;
   - exact implementation commits;
   - changed files;
   - tests;
   - integration readiness;
   - blocker;
   - Owner gate;
   - next action;
5. open `<stageId>_RESULT.md` only when deeper evidence is needed;
6. inspect implementation commits only for acceptance/integration review.

The default PM status recap should therefore be obtainable from a few small JSON files instead of reconstructing the full worker history.

## 13. Worker chat terminal reply

The worker's chat reply to the Owner should be short and match the durable result.

Format:

`<STATE> — <one-line verdict>`

Then at most:

- `result: parallel/PM/RESULTS/<stageId>_RESULT.json`
- `implementation: <sha>`
- `next: <single next action>`

No long narrative is required in chat because the detailed evidence belongs in Git.

## 14. No central worker-owned dashboard

Workers must not update one common dashboard/index file because simultaneous writes create unnecessary GitHub 409/race failures.

PM may generate a coordinator-owned summary after workers return, but worker terminal reporting remains per-stage and append/create-only where possible.

## 15. Acceptance rule for future Alpha prompts

Every new Alpha worker start prompt should include:

`Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.`

This requirement is additive to dedup-v2 and does not weaken any existing fail-closed, product-proof, scope-isolation, or Owner-intervention rules.
