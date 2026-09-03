# Project-wide Agent / PM Bootstrap

This file applies repository-wide, including fresh chats and newly assigned PMs/workers.

## Mandatory PM bootstrap

Any agent acting as Product Manager, orchestrator, reviewer, or task issuer MUST first read and follow:

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/GLOBAL_PM_WORKER_HANDOFF_RULES.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`

These rules survive chat/thread changes. A fresh PM chat must not rely on old chat memory; GitHub durable state is authoritative.

## Owner interaction contract

- Standalone `1` means **continue project progression**. The current worker may already be finished. PM must inspect latest Git HEAD, durable RESULT, canonical/stage claims and actual changes, independently judge the worker result, then choose the shortest legitimate next step.
- Owner is the relay and strategic/product-direction leader. Owner is NOT responsible for reviewing worker quality, implementation details, tests, commits, claims, or routine next-step selection. PM owns those decisions end-to-end.
- PM must keep Owner communication concise. Worker handoffs should normally begin with about 100 Chinese characters of task intent, put the authoritative Git/START_PROMPT path in the middle, and avoid repeating repository history already captured in Git.
- PM should give Owner only the next prompt that needs relaying or a genuinely strategic decision that needs Owner leadership.

## Worker handoff execution behavior

For implementation/setup/recovery work, handoffs should end with the equivalent of:

> 如果遇到问题，不要停在一句报错。继续自动诊断和修复所有安全可修复的环境问题，直到：SETUP COMPLETE，或给出一个真正需要 Owner 手工处理的精确 BLOCKED。少汇报，直接执行。

For non-setup tasks, adapt `SETUP COMPLETE` to the stage's real terminal success state while preserving the same sustained-execution behavior.

Do not use this rule to bypass safety, canonical dedup, exact proof authority, testing cadence, source/runtime boundaries, or explicit START_PROMPT constraints.
