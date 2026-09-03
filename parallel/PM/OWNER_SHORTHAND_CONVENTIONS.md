# Owner Shorthand Conventions

Updated: 2026-09-03
Authority: Owner interaction convention

## `1` means PM checkpoint + continue project

When the Owner sends a message whose trimmed content is exactly:

`1`

interpret it as:

**The current worker may already be finished. Re-read the latest authoritative Git state, inspect what the worker actually changed/completed, judge the real terminal status, then continue advancing the project through the shortest legitimate next step.**

Operational rules:
- Do **not** interpret standalone `1` as “choose option 1” unless the Owner explicitly says they are selecting a numbered option.
- Do **not** ask what `1` means when there is an active project/execution chain in context.
- Treat `1` as a PM checkpoint trigger, not as an automatic instruction to tell the same worker to continue.
- Re-read current `main` / relevant HEAD plus durable RESULT, canonical claim and stage claim as needed.
- Inspect actual committed progress rather than trusting the worker chat summary alone.
- If the current stage is COMPLETE/PASS, review/accept it and immediately identify the next legitimate product step.
- If a fresh implementation/recovery/QA stage is genuinely required, create or surface the proper durable START_PROMPT under canonical dedup and give the Owner the new concise worker requirement.
- If unfinished authorized work only needs closeout/recovery, continue that shortest path without redoing completed implementation.
- If BLOCKED, route only the concrete blocker.
- Preserve dedup, stage, safety, testing-cadence, and no-duplicate-work rules.
- Never merely repeat the previous status after `1`; the project should move forward whenever Git truth permits it.

In short:

`Owner 发 1 -> PM 检查 worker 的 Git 进度 -> 判断完成/阻塞/未收口 -> 生成下一条正确需求 -> 继续推进项目`

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
