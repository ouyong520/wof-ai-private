# WOF Future Danger AI — Global PM / Worker Handoff Rules

Updated: 2026-09-03
Status: **AUTHORITATIVE — ALL PRODUCT MANAGERS AND ALL NEW WORKER HANDOFFS MUST FOLLOW THIS**

This file is project-wide PM operating policy. It applies to Alpha/V1, Collector, Training Farm, QA, recovery, audit, setup, acceptance, packaging and future workstreams unless the Owner explicitly overrides a rule for a specific task.

It supplements, and must be read consistently with:

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/OWNER_SHORTHAND_CONVENTIONS.md`

## 1. Owner shorthand: standalone `1` means PM checkpoint + continue project

When the Owner sends a message whose trimmed content is exactly `1`, interpret it as:

**The current worker may already be finished. PM must inspect the latest authoritative Git state, judge the worker's real progress/result, then continue advancing the project through the shortest legitimate next step.**

Standalone `1` is therefore a **PM checkpoint / project-continuation trigger**, not an instruction to blindly tell the same worker to continue.

Do not treat standalone `1` as “choose option 1” unless the Owner explicitly says they are selecting a numbered option.

On every standalone `1`, PM must:

1. re-read current `main` / relevant repository HEAD and the latest durable RESULT, canonical claim and stage claim;
2. inspect what the worker actually changed or completed instead of trusting chat wording alone;
3. classify the current stage from Git truth: COMPLETE/PASS, precise BLOCKED, still legitimately in progress, duplicate/no execution, or stopped without durable closeout;
4. if complete, accept/review it and immediately identify the legitimate next product step;
5. if a new implementation/recovery/QA stage is genuinely required, create or surface the correct fresh durable START_PROMPT under canonical dedup rules, then give the Owner the new concise worker requirement;
6. if only closeout/recovery of unfinished authorized work is needed, continue that shortest path without redoing completed implementation;
7. if blocked, route only the concrete blocker and avoid broad speculative recovery chains;
8. never merely repeat the previous status and never automatically instruct the old worker to continue without checking Git first.

The objective of `1` is: **Owner presses one key -> PM checks worker progress -> PM decides and issues the next correct requirement -> project keeps moving.**

## 2. All PM-to-worker handoffs must stay short

Default Owner-facing handoff format:

1. Start with roughly **100 Chinese characters** of plain-language task description. State the concrete responsibility, outcome and most important boundary. Do not paste a long history when Git already contains the durable specification.
2. Put the authoritative Git repository path / START_PROMPT reference in the **middle** of the handoff.
3. Keep the rest compact. The Git START_PROMPT is the detailed authority; the chat handoff is only a concise execution entry point.
4. Prefer one coherent worker instruction instead of many verbose sections.
5. PM should not make the Owner interpret implementation summaries or choose routine technical solutions.

Typical middle form:

```text
仓库：ouyong520/wof-ai-private
读取：parallel/PM/<START_PROMPT>.md
```

## 3. Default terminal execution instruction for implementation/setup/recovery workers

Unless the Owner explicitly overrides it, PM must end implementation/setup/recovery handoffs with an instruction equivalent to:

```text
如果遇到问题，不要停在一句报错。继续自动诊断和修复所有安全可修复的环境问题，直到：SETUP COMPLETE，或给出一个真正需要 Owner 手工处理的精确 BLOCKED。少汇报，直接执行。
```

For tasks whose terminal success state is `COMPLETE` rather than `SETUP COMPLETE`, PM may adapt the success token while preserving the same behavior: keep diagnosing and safely fixing recoverable problems until the authorized stage reaches its real terminal state or a genuinely Owner-required precise blocker remains.

This rule means:

- do not stop after the first dependency, path, shell, package, CI, permission, cache, launcher or other recoverable environment error;
- continue automatic diagnosis and safe remediation inside the authorized scope;
- do not ask Owner for routine confirmations between recoverable steps;
- do not stop merely because one intermediate patch/test/setup step finished;
- implementation workers finish the coherent module, integration, self-check, durable RESULT and required claim closeout before terminal reporting when the START_PROMPT requires them;
- report sparingly and spend the turn executing rather than narrating routine progress.

It does **not** authorize destructive changes, unsafe actions, secret disclosure, bypassing dedup/safety gates, weakening proof authority, inventing scope, or fabricating PASS/COMPLETE evidence.

## 4. Terminal reporting

Normal worker behavior is:

**clear handoff -> sustained execution -> terminal report**.

Workers should stop/report primarily at one of the authorized terminal states for the stage, such as:

- `SETUP COMPLETE` / `COMPLETE` / `PASS`;
- precise `BLOCKED` that truly requires Owner/manual/external action or cannot safely be repaired inside scope;
- canonical duplicate `NO EXECUTION` / duplicate stop.

A one-line error is not a terminal result when safe automatic diagnosis/remediation remains possible.

## 5. Mandatory PM application

All product managers creating or resurfacing worker prompts must apply this file by default. New PM START_PROMPTs and recovery prompts should be written so their Owner-facing handoff can follow these rules without restating large amounts of background context.

If another older PM document conflicts only in handoff verbosity or routine stop/report behavior, this global policy governs the newer Owner interaction convention. Safety, canonical dedup, exact proof authority, testing cadence, source/runtime boundaries and explicit task-specific START_PROMPT constraints remain fully authoritative.

## 6. Owner is relay + strategic leader; PM owns worker review and execution routing

The Owner is not expected to inspect whether a worker implemented the task correctly, read detailed worker summaries, compare commits, validate test coverage, or decide the routine next engineering step.

Default role split:

- **Owner**: relay concise worker handoffs between chats, provide product direction, challenge or lead PM thinking at important strategic points, and perform only genuinely unavoidable manual/live actions.
- **PM**: own project-state inspection, worker-result review, quality judgment, acceptance/rejection, blocker diagnosis, task decomposition, prioritization, recovery/QA necessity, next-stage creation, dedup correctness, and shortest-path project progression.

Therefore:

1. PM must independently review Git durable evidence; do not ask the Owner whether a worker “did it right”.
2. PM must decide whether a worker result is accepted, incomplete, defective, superseded, blocked, or needs a focused successor stage.
3. PM must give the Owner only the concise next handoff that actually needs relaying, plus any genuinely important strategic decision that needs Owner leadership.
4. Routine implementation details, test logs, worker self-assessments and recovery mechanics should remain PM responsibility unless they materially affect product strategy or require Owner action.
5. `1` remains the Owner's minimal “continue” signal: PM checks current Git truth and keeps the project moving without making the Owner review worker quality.

The operating model is:

**Owner leads product direction and relays concise prompts; PM owns execution governance and worker quality control.**
