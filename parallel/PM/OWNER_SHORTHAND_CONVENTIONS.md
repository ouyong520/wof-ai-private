# Owner Shorthand Conventions

Updated: 2026-09-03
Authority: Owner interaction convention

## `1` means PM checkpoint + continue project + one idle worker

When the Owner sends a message whose trimmed content is exactly:

`1`

interpret it as:

**Equivalent to `1 1`: re-read the latest authoritative Git state, inspect what the worker actually changed/completed, continue advancing the project through the shortest legitimate next step, and treat exactly one worker slot as currently idle/available for the next useful assignment.**

Idle-worker context semantics:

- If the project is already running in parallel/multi-worker mode, standalone `1` means **one worker slot is idle now** while other workers may still be ACTIVE. Check the whole current Git/claim state, continue the critical path, then assign that one idle slot only if a useful independent task exists.
- If the project is not running in parallel and there is only one worker, standalone `1` means **the sole/current worker has become idle or finished its previous instruction**. Check that worker's durable Git result first; if project work remains, immediately give that same sole worker the shortest legitimate next task.
- In either mode, `1` does not itself prove the previous worker succeeded. Git RESULT/claims/commits remain authoritative.

Operational rules:
- Do **not** interpret standalone `1` as “choose option 1” unless the Owner explicitly says they are selecting a numbered option.
- Do **not** ask what `1` means when there is an active project/execution chain in context.
- Treat `1` as a PM checkpoint trigger plus one-idle-worker capacity signal, not as an automatic instruction to repeat the same task.
- Re-read current `main` / relevant HEAD plus durable RESULT, canonical claim and stage claim as needed.
- Inspect actual committed progress rather than trusting the worker chat summary alone.
- If the current stage is COMPLETE/PASS, review/accept it and immediately identify the next legitimate product step.
- If a fresh implementation/recovery/QA stage is genuinely required, create or surface the proper durable START_PROMPT under canonical dedup and give the Owner the new concise worker requirement.
- If unfinished authorized work only needs closeout/recovery, continue that shortest path without redoing completed implementation.
- If BLOCKED, route only the concrete blocker.
- Preserve dedup, stage, safety, testing-cadence, and no-duplicate-work rules.
- Never merely repeat the previous status after `1`; the project should move forward whenever Git truth permits it.
- The one idle slot is capacity, not a requirement to invent work. If no useful independent/next task exists, leave it idle.

In short:

`Owner 发 1 == 1 1 -> PM 检查最新 Git -> 判断当前 worker 完成/阻塞/未收口 -> 继续真正下一步 -> 把 1 个空闲 worker 用在最有效且不冲突的任务上`

## `1 N` means continue project + N currently idle workers available

When the Owner sends a shorthand message matching:

`1 <N>`

where `N` is a non-negative integer, interpret it as two simultaneous facts/instructions:

1. **`1` = continue the current project from authoritative Git state** using the same checkpoint/review behavior defined above.
2. **`N` = there are currently N idle worker slots available for immediate assignment** if useful independent work exists.

Examples:

- `1 1` = continue project progression and there is 1 idle worker available. This is semantically the same as standalone `1`.
- `1 2` = continue project progression and there are 2 idle workers available.
- `1 3` = continue project progression and there are 3 idle workers available.

Mandatory PM execution order for `1 N`:

`READ LATEST GIT -> REVIEW CURRENT MAINLINE/WORKERS -> CONTINUE THE REAL CRITICAL PATH -> IDENTIFY SAFE INDEPENDENT PARALLEL WORK -> ASSIGN UP TO N IDLE WORKERS`

Rules:

- Always inspect latest authoritative Git first. `1 N` does not authorize guessing worker state from chat memory.
- First continue or repair the real mainline. Worker-capacity allocation comes after current-state review, not before it.
- Treat `N` as **available capacity, not a requirement to fill every slot**.
- Assign only work that is genuinely independent, non-duplicative, authority-safe, file/runtime non-conflicting, and likely to shorten the product critical path.
- If only one useful independent task exists while `N=3`, assign one worker and leave two idle.
- Never manufacture QA, recovery, audit, cross-check, speculative refactor, documentation-only work, or low-value side work merely to consume idle capacity.
- Every dispatched worker still performs canonical dedup/current-state preflight before substantive work.
- If equivalent work is already ACTIVE/CLAIMED, do not duplicate it; report `ALREADY ACTIVE / CLAIMED — NO EXECUTION` for that worker slot and redirect only if another legitimate independent task exists.
- If equivalent work is already COMPLETE, do not repeat it; report `ALREADY COMPLETE — NO EXECUTION` and use capacity only for the next legitimate task.
- Respect umbrella/subworkstream ownership. Idle workers do not get permission to steal an existing canonical claim.
- PM must define explicit file/runtime/authority boundaries before parallel implementation when multiple workers touch the same project.
- Owner does not need to decide which worker gets which technical subtask; PM owns that allocation.
- Do not interpret `1 N` as numbered-option selection unless the Owner explicitly says they are choosing options.

In short:

`Owner 发 1 N -> PM 查最新 Git -> 审核当前主线 -> 继续真正下一步 -> 最多把 N 个空闲 worker 分给最能加速且互不冲突的独立任务`

## PM / worker handoff formatting

Default handoff style should be compact and execution-oriented.

- Keep the opening request concise, generally around 100 Chinese characters unless the task genuinely needs more context.
- Put the authoritative Git path/link or START_PROMPT reference in the middle of the handoff instead of burying it at the end.
- Avoid long background restatements when the repository already contains the durable specification.
- Prefer one coherent worker instruction over multiple verbose sections.
- Report sparingly and execute directly.

Unless the Owner explicitly overrides it, append the following execution rule near the end of implementation/setup handoffs:

> 如果遇到问题，不要停在一句报错。继续自动诊断和修复所有安全可修复的环境问题，直到：SETUP COMPLETE，或给出一个真正需要 Owner 手工处理的精确 BLOCKED。少汇报，直接执行。

This rule does not authorize unsafe changes, secret handling, destructive operations, bypassing repository authority, weakening dedup/safety gates, or inventing work outside the authorized scope. It means the worker should keep diagnosing and safely fixing recoverable environment/setup problems instead of stopping at the first error.

This convention is durable PM/operator guidance and should be applied across future WOF project chats/workers unless the Owner explicitly overrides it.
