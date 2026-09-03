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

This convention is durable PM/operator guidance and should be applied across future WOF project chats/workers unless the Owner explicitly overrides it.
