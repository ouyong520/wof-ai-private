# WOF Future Danger AI — PM Core Operating Charter

Updated: 2026-09-02
Status: **AUTHORITATIVE — ALL PM PRIORITIZATION AND NEW START PROMPTS MUST FOLLOW THIS**

This file records the Owner's operating directives so the project does not drift away from the real product goal.

## 1. Product north star — do not confuse tools with the product

The project exists to make **WOF Future Danger AI actually useful in real WOF gameplay**.

The long-term north star is to progress, step by step, toward:

**reliable danger understanding -> correct warning -> safe movement guidance -> safe path -> increasingly low-damage play -> eventually target stable 0-damage clear capability.**

Do not declare success because launchers, recorders, dashboards, QA harnesses, or packaging tools are finished. Those are supporting infrastructure only.

### WOF-052 / WOF-052L role

The WOF-052 family is a major current evidence/research mainline because it supplies long-duration real Browser evidence needed for attack prediction, ordered-context disambiguation, coverage and prospective validation.

`WOF-052L` is the multi-room long-capture/analysis pipeline. It is **core R&D infrastructure**, but it is not by itself the final user product.

The final user-facing core remains the evolving **WOF Future Danger Alpha -> Beta -> v1 -> Safe Path / Assist** system.

All WOF-052/052L work must be judged by whether it improves the real product's predictive coverage, correctness, safety, or path toward low/zero-damage play.

## 2. Step-by-step product progression

Do not jump directly from partial research to “0 damage”. The required progression is:

### Stage A — real-user Alpha
A normal user can start the system simply and obtain a small number of highly trustworthy real-time warnings in real WOF.

Required themes:
- automatic runtime attachment;
- exact supported-game identity;
- validated production rules only;
- warning/HUD/target/side/lead-time behavior;
- fail-open gameplay and fail-closed warnings;
- read-only / no gameplay input injection;
- Chinese one-click UX.

### Stage B — Beta coverage
Increase coverage of common dangerous attacks and ambiguous branches through long capture, ordered-sequence discovery and fresh prospective validation.

### Stage C — Safe Path
Fuse attack prediction with geometry, player/enemy positions, threat regions, reachable space, multi-enemy threat fusion and real-time replanning to recommend where/when to move.

### Stage D — 0-damage objective
Use the mature predictor + geometry + planner + execution model to progressively prove low-damage and eventually stable 0-damage clear capability.

Optional command/assist execution remains separated from the read-only warning mode and comes only after the read-only product is trustworthy.

## 3. PM must proactively manage work, not wait for Owner to invent tasks

PM is responsible for:
- reading latest GitHub state;
- judging distance to real user value;
- finding the highest-value next blockers/work;
- issuing fresh stages proactively;
- maintaining a rolling task queue;
- closing or parking work that is no longer valuable;
- keeping useful parallelism when legitimate independent work exists.

The Owner should not need to ask “还有没有别的可以做”.

However, concurrency is a ceiling, not a KPI. Do not manufacture low-value work merely to fill empty chats.

## 4. Every completed worker submission must be independently PM-reviewed

A worker saying `PASS`, `READY`, or “done” means only **submitted for PM review**.

PM must independently inspect the durable GitHub result, relevant code/tests, and any newer QA/audit evidence before deciding whether the stage is actually accepted.

For every completed stage PM must classify it as one of:
- `ACCEPTED_COMPLETE` — result is good enough; close and do not optimize further now;
- `ACCEPTED_WAITING_GATE` — stage is good but downstream prerequisite is not ready;
- `NEEDS_FRESH_FIX` — result/QA exposes P0/P1 or material mainline defect;
- `SUPERSEDED` — newer work makes it obsolete;
- `NO_DURABLE_RESULT` — thread stopped but did not leave sufficient GitHub evidence; treat as not completed.

Then PM decides, by priority, whether to:
1. open a fresh fix/QA/retest stage;
2. leave the result closed and work on a more important blocker;
3. park it until a prerequisite changes.

The Owner does **not** review worker summaries or decide success/failure.

## 5. One stage = one fresh chat

Hard rule:

`ONE STAGE = ONE FRESH CHAT`

When a thread reaches its stop condition, it is finished permanently.

- Do not continue a completed dev thread.
- Do not ask an old QA thread to fix its own blocker.
- Do not reuse a fix thread for QA retest.
- Every fix, independent QA, retest, integration, recovery and next research stage uses a new `stageId` and a fresh chat.

GitHub is the durable state. Chats are disposable workers.

## 6. Automatic duplicate protection

All new PM start prompts must follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

For prompts created after canonical-dedup v2 hardening, `stageId` alone is not the ownership gate. New prompts must declare `dedupProtocol: v2`, a stable semantic `dedupKey`, and `dedupMode`. Equivalent logical tasks must contend on the same create-only canonical resource under `parallel/PM/DEDUP_CLAIMS/**`, and a worker must re-read that claim and verify its exact `claimToken` before doing task work.

Before doing work, a worker must check:
- is an equivalent result already complete?
- is the canonical logical work item already claimed/executing, even under another `stageId`?

If yes, it must stop immediately and return that the thread is idle/safe to close.

Intentional second-opinion/cross-check QA remains allowed only when a PM/start prompt explicitly declares the independent-validation mode/group/key defined by the guard. A worker may not invent a new validation slot to bypass an occupied claim.

The Owner may accidentally paste the same or an equivalent prompt twice; duplicate project work should still not occur.

## 7. PM rolling queue — Owner does not need to remember which prompt was copied

PM maintains `parallel/PM/EXECUTION_QUEUE.md`.

When Owner says `继续`, PM must:
1. inspect latest results, commits and stage claims;
2. review finished work;
3. identify missed/unclaimed queued prompts;
4. re-surface only tasks that are still truly needed;
5. never re-surface equivalent work already claimed/completed;
6. create fresh downstream/fix stages when appropriate.

The Owner does not need to remember which prompt was copied before leaving the computer.

## 8. Priority must follow product progress, not task count

Authoritative order:

### P0 — current product/mainline blocker
Examples:
- evidence could be attributed to the wrong room/page/Worker;
- exact runtime identity is unreliable;
- a validator/acceptance path can falsely PASS;
- a defect blocks Alpha transport or real warning behavior.

### P1 — direct mainline risk / prevents wasted real test
Examples:
- component contract drift;
- missing fail-closed gate;
- regression gap covering the current P0 fixes;
- packaging/preflight defect that could cause a wasted Owner run.

### P2 — near-term accelerator
Start only when active P0/P1 work will not immediately invalidate it.

### P3 — useful but non-blocking
Park while P0/P1 exists.

An empty worker slot may remain empty. Do not drift away from the mainline merely to keep every worker busy.

## 9. Minimize Owner workload — Owner is not the debugger

Authoritative gate: `parallel/PM/OWNER_INTERVENTION_GATE.md`.

Before requesting Owner action, exhaust everything possible through:
- code inspection;
- reverse engineering;
- historical evidence reuse;
- static analysis;
- mock/fixture/synthetic CDP topology;
- recorded corpus replay;
- component regression;
- independent QA;
- cross-component audit;
- global regression;
- one-click/preflight/package checks.

Forbidden normal pattern:

`让 Owner 试一下 -> 失败 -> 修一点 -> 再让 Owner 试 -> 再失败`

Owner should join only when the remaining fact is intrinsically impossible to prove without a real Windows/Browser/WOF run or genuine long-duration capture.

When Owner action is unavoidable, combine as many gates as possible into **one bounded run** and require only one final JSON or screenshot.

## 10. Long capture must not waste Owner time

Do not request a 1h/2h/overnight WOF-052L run until short-run code/runtime gates are already clean.

Before long capture, repository-side checks must cover:
- Worker/page/session association;
- exact identity admission;
- multi-room isolation;
- failure/reload behavior;
- Chinese owner UX;
- automatic analysis;
- automatic evidence handoff;
- result recovery/finalization;
- relevant fresh QA/regression.

Only then is long capture an unavoidable evidence-generation activity rather than exploratory debugging.

## 11. Current mainline test

Before PM creates any new stage, answer:

> If this stage succeeds, does it materially shorten the path to a trustworthy real-user Alpha, improve WOF-052 evidence needed for predictive coverage, or unlock the later Safe Path / 0-damage objective?

If not, do not prioritize it now.

## 12. Owner-visible PM reporting

Keep Owner updates concise. PM should normally state:
- current product status in one sentence;
- top priorities only;
- whether Owner action is required: `YES` or `NO`;
- exact fresh prompt(s) only when a worker slot should actually be used.

Do not make Owner interpret implementation summaries or choose technical solutions.

## 13. Product version and release cadence are user-value driven

Authoritative roadmap: `parallel/PM/PRODUCT_VERSION_ROADMAP.md`.

All PM work must distinguish **engineering stages** from **user-facing product versions**.

Hard rules:

1. a product version must deliver a gameplay improvement the user can actually perceive;
2. backend/refactor/QA/tooling completion alone does not earn a new product version number;
3. target roughly one safe user-visible patch every 2–3 days and one materially stronger minor release roughly every 7 days once a usable baseline exists;
4. do not ship on cadence if a release safety gate remains open;
5. V1.0.0 is the first hard foundation; later V1.x patches should reuse it to deliver faster visible improvements;
6. multi-instance Training Farm work may run early as an isolated R&D accelerator when it directly improves automated enemy/action-state collection, future V1.x warning coverage, or later safe-route learning, but it must not displace legitimate V1 P0/P1 release work or be counted as product-version progress by itself;
7. before opening a new stage, PM should be able to state which user-visible release it supports, or explicitly classify it as an isolated R&D accelerator.
