# Owner Shorthand Conventions

Updated: 2026-09-03
Authority: Owner interaction convention

## `1` means PM checkpoint + continue project + one worker has finished/become idle

When the Owner sends a message whose trimmed content is exactly:

`1`

interpret it as:

**Equivalent to `1 1`: continue the project from latest authoritative Git state, and understand that one worker has just finished its previous work / become idle and now needs PM review and reassignment if appropriate.**

This is stronger than a generic capacity hint. In an active parallel/multi-worker project, standalone `1` means:

1. **continue the current project;**
2. **one of the currently assigned workers has finished or become idle;**
3. PM must inspect current Git/RESULT/claims/commits to determine which workstream actually finished and whether its result is acceptable;
4. after that review, decide whether the freed worker should rejoin the mainline/integration path, receive the next independent acceleration task, or remain idle.

The Owner does not need to identify which worker finished. PM determines that from durable Git state.

Parallel / merge context semantics:

- If the project is already running in parallel/multi-worker mode, standalone `1` means **at least one previously occupied worker slot has become free because that worker finished/stopped its assigned work**, while other workers may still be ACTIVE. PM must inspect all current workstreams and find the newly completed/idle one before assigning anything.
- If the finished worker produced a sub-result that must now be consumed by an umbrella/integration owner, treat that as a merge/integration event first. Do not automatically invent a new parallel task for the freed slot.
- If the current critical path needs a continuation/recovery and the freed worker is the appropriate executor, give that worker the next mainline task.
- If another ACTIVE mainline worker owns integration and a genuinely independent accelerator exists, the freed worker may take that task.
- If no useful non-conflicting task exists, leave the worker idle.
- If the project is not running in parallel and there is only one worker, standalone `1` means **the sole/current worker has finished or become idle**. Check its durable Git result first; if project work remains, immediately give that same worker the shortest legitimate next task.
- In all modes, `1` does not prove the worker succeeded. Git RESULT/claims/commits remain authoritative.

Operational rules:
- Do **not** interpret standalone `1` as “choose option 1” unless the Owner explicitly says they are selecting a numbered option.
- Do **not** ask what `1` means when there is an active project/execution chain in context.
- Treat `1` as a PM checkpoint trigger plus a **worker-finished / worker-now-idle signal**, not as an automatic instruction to repeat the same task.
- Re-read current `main` / relevant HEAD plus durable RESULT, canonical claim and stage claim as needed.
- Inspect actual committed progress rather than trusting the worker chat summary alone.
- If the finished stage is COMPLETE/PASS, review/accept it and immediately identify the legitimate next product step.
- If a fresh implementation/recovery/QA stage is genuinely required, create or surface the proper durable START_PROMPT under canonical dedup and give the Owner the new concise worker requirement.
- If unfinished authorized work only needs closeout/recovery, continue that shortest path without redoing completed implementation.
- If BLOCKED, route only the concrete blocker.
- Preserve dedup, stage, safety, testing-cadence, and no-duplicate-work rules.
- Never merely repeat the previous status after `1`; the project should move forward whenever Git truth permits it.
- The newly freed worker is available capacity after PM review, not a requirement to invent work.

In short:

`Owner 发 1 == 1 1 -> 有一个 worker 刚做完/空闲 -> PM 查最新 Git 找出是谁和做得怎样 -> 继续主线/并线 -> 再决定这个空闲 worker 的下一任务`

## `1 N` means continue project + N workers have finished/become idle

When the Owner sends a shorthand message matching:

`1 <N>`

where `N` is a non-negative integer, interpret it as two simultaneous facts/instructions:

1. **`1` = continue the current project from authoritative Git state** using the same checkpoint/review behavior defined above.
2. **`N` = N previously occupied/current worker slots have finished their assigned work or are now idle and available for PM review/reassignment.**

Examples:

- `1` = exactly the same as `1 1`: continue + one worker has finished/become idle;
- `1 1` = continue + one worker has finished/become idle;
- `1 2` = continue + two workers have finished/become idle;
- `1 3` = continue + three workers have finished/become idle.

Mandatory PM execution order for `1 N`:

`READ LATEST GIT -> IDENTIFY WHICH N WORKERS/WORKSTREAMS FINISHED OR BECAME IDLE -> REVIEW THEIR DURABLE RESULTS -> CONTINUE / MERGE THE REAL CRITICAL PATH -> IDENTIFY SAFE INDEPENDENT PARALLEL WORK -> REASSIGN UP TO N FREED WORKERS`

Rules:

- Always inspect latest authoritative Git first. `1 N` does not authorize guessing which workers finished from chat memory.
- The Owner does not need to name the finished workers; PM derives them from current claims/results/commits.
- First continue, merge, close, or repair the real mainline. Reassignment comes after current-state review.
- Treat `N` as **newly available worker capacity after completion/idle**, not a requirement to fill every slot.
- Do not double-count the same freed worker as both a mainline continuation worker and an additional parallel worker.
- Assign only work that is genuinely independent, non-duplicative, authority-safe, file/runtime non-conflicting, and likely to shorten the product critical path.
- If only one useful independent task exists while `N=3`, assign one worker and leave two idle.
- Never manufacture QA, recovery, audit, cross-check, speculative refactor, documentation-only work, or low-value side work merely to consume freed workers.
- Every reassigned worker still performs canonical dedup/current-state preflight before substantive work.
- If equivalent work is already ACTIVE/CLAIMED, do not duplicate it; report `ALREADY ACTIVE / CLAIMED — NO EXECUTION` for that slot and redirect only if another legitimate independent task exists.
- If equivalent work is already COMPLETE, do not repeat it; report `ALREADY COMPLETE — NO EXECUTION` and use capacity only for the next legitimate task.
- Respect umbrella/subworkstream ownership. Freed workers do not get permission to steal an existing canonical claim.
- PM must define explicit file/runtime/authority boundaries before parallel implementation when multiple workers touch the same project.
- Owner does not need to decide which worker gets which technical subtask; PM owns that allocation.
- Do not interpret `1 N` as numbered-option selection unless the Owner explicitly says they are choosing options.

In short:

`Owner 发 1 N -> N 个 worker 已做完/空闲 -> PM 查最新 Git 审核它们 -> 继续/并线真正主线 -> 最多把这 N 个释放出来的 worker 重新分给最能加速且互不冲突的任务`

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
