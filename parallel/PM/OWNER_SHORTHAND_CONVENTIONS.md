# Owner Shorthand Conventions

Updated: 2026-09-03
Authority: Owner interaction convention

## `1` means continue

When the Owner sends a message whose trimmed content is exactly:

`1`

interpret it as:

**Continue the current task / execution chain from the latest authoritative state.**

Operational rules:
- Do **not** interpret standalone `1` as “choose option 1” unless the Owner explicitly says they are selecting a numbered option.
- Do **not** ask what `1` means when there is an active task or execution chain in context.
- Re-read the latest authoritative repository state when required by that task, then continue rather than restarting completed work.
- Preserve the current task's dedup, stage, safety, testing-cadence, and no-duplicate-work rules.
- `1` does not by itself authorize inventing a new stage, recovery, QA chain, or scope expansion; it means continue the already-authorized work.

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
