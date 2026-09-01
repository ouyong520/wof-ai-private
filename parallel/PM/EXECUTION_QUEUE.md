# WOF PM Rolling Execution Queue

Updated: 2026-09-01

## Owner operating rule

Owner does **not** need to read worker summaries, decide PASS/FAIL, compare commits, or remember which prompts were copied.

PM is authoritative for reviewing GitHub results and deciding the next stage.

## Thread lifecycle

Hard rule:

`ONE STAGE = ONE FRESH CHAT`

- A work thread runs only its declared stage.
- When it reaches PASS / READY / BLOCKED / precise stop condition, that thread is finished permanently.
- Do not continue implementation in the old thread.
- Do not send a fix back into the old QA thread.
- Do not reuse a completed dev thread for retest.
- Every fix, retest, QA, integration, recovery, or downstream stage gets a **new stageId and a fresh chat**.

GitHub is the durable state; chats are disposable workers.

## PM review rule

When Owner says `继续`:

1. PM reads current GitHub results/commits/claims.
2. PM decides which finished threads were successful, blocked, stale, or superseded.
3. PM closes those stages conceptually; Owner does not need to inspect their summaries.
4. PM creates fresh downstream/fix/retest prompts as needed.
5. PM fills available concurrency slots from this queue.
6. PM only surfaces prompts whose stage is not already complete and not already claimed.

Owner only needs to open fresh chats and paste the short launcher instruction.

## Mandatory dedup

Every queue item must reference `parallel/PM/STAGE_DEDUP_GUARD.md` and have a unique `stageId`.

A worker must exit immediately with one of:

- `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`
- `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

when appropriate.

Therefore Owner may accidentally paste the same queued prompt twice without duplicating project work.

## Queue states

PM tracks tasks using these meanings:

- `QUEUED`: prompt exists; safe to offer when a slot is free.
- `CLAIMED`: a worker created the stage claim and is executing.
- `COMPLETE`: PM verified stop condition/result; do not reuse thread.
- `BLOCKED`: PM verified blocker; create a new fix/recovery stage instead of reusing thread.
- `SUPERSEDED`: newer stage/result fully replaces it.
- `WAITING_GATE`: valid future stage, but a prerequisite has not passed; do not waste a worker slot yet.

## Current queue principle

Prefer 8-10 useful concurrent execution lanes when write ownership is disjoint.

Do not fill slots with duplicate or premature work. Prefer:
- P0/P1 blocker closure;
- independent component fixes with disjoint write scopes;
- regression/QA that cannot become stale from an in-flight conflicting component change;
- automatic handoffs that reduce future owner operations;
- prebuilt downstream stages only when they do not modify the same core files.

## Owner-visible PM response

PM should not ask Owner to interpret technical summaries.

For each available slot, PM supplies only:

```text
连接 GitHub，读取：
`ouyong520/wof-ai-private/parallel/PM/<PROMPT>.md`

严格持续执行直到停止条件。
```

PM itself remains responsible for the later success/failure judgment.
