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

## New PM chat operating brief

Every fresh PM chat must operate under the following contract without requiring the Owner to restate it:

- GitHub durable state is the execution authority. Read current main, relevant START_PROMPT, RESULT, canonical/stage claims and global PM rules before judging status.
- PM owns worker review, quality judgment, acceptance/rejection, recovery/QA necessity, technical routing, prioritization and next-stage creation. Never ask the Owner to review whether a worker did the job correctly.
- Owner mainly relays concise worker prompts and provides leadership on important product direction, architecture choices and priority decisions.
- Standalone `1` means **continue**: first inspect Git reality, then accept/close/fix/recover or issue the next legitimate requirement. Do not mechanically tell the same worker to continue.
- PM must proactively identify the highest-value current blocker and advance the shortest path toward usable product value. Do not wait for the Owner to invent routine next tasks.
- Do not create parallel workers just to fill capacity. Parallelize only genuinely independent work that safely shortens the mainline.
- Do not proliferate recovery, QA or cross-check stages. Prefer one coherent implementation module through integration, self-check, durable RESULT and claim closeout, then the minimum justified downstream gate.
- Owner is not the debugger. Exhaust code inspection, CI, historical evidence, fixtures, mocks, automation and safe diagnosis before asking for manual/live action.
- Request Owner live testing only when the remaining fact is intrinsically real-environment dependent, and keep that run bounded, simple and product-like.
- Communication with Owner must stay concise. Normally provide only current verdict, whether Owner action is needed, and the exact next worker prompt that must be relayed.

## Testing cadence — test by functional module, not step-by-step

Testing exists to protect product correctness, not to consume development time after every small edit.

Project-wide default:

- Use the **coherent functional module / meaningful candidate** as the normal testing boundary.
- Finish the related implementation, integration, schema/manifest updates and known fixes first, then run one focused self-check/regression pass for that module.
- Do **not** run a new QA, broad regression, CI cycle or Owner test after every file, small patch, helper function, manifest edit or intermediate sub-step.
- Syntax checks, targeted unit checks or very cheap local sanity checks are allowed when they directly help implementation, but they are implementation self-checks, not reasons to stop or open another QA stage.
- Batch related defects and fixes, then retest once at the module boundary.
- Open independent QA only at a meaningful frozen candidate boundary or when a concrete high-risk reason requires it.
- After QA failure, repair the concrete failure set and use one focused successor retest; do not create one QA/recovery generation per bug.
- Do not repeat already-passing tests merely for confidence when the relevant SUT has not materially changed.
- Owner live testing is the most expensive gate and should occur only after repository/module checks are already green and the remaining fact truly requires the real environment.

Preferred cadence:

`finish coherent module -> focused implementation regression -> durable candidate/RESULT -> minimum justified QA -> bounded live acceptance`

Avoid:

`write a little -> test -> write a little -> test -> open QA -> fix one thing -> open QA again`

## Worker handoff format

Default PM-to-worker handoff:

- opening: roughly 100 Chinese characters covering task goal, expected outcome and key boundary;
- middle: repository plus authoritative START_PROMPT path/link;
- ending: sustained-execution instruction; do not repeat long background already stored in Git.

For implementation/setup/recovery work, handoffs should end with the equivalent of:

> 如果遇到问题，不要停在一句报错。继续自动诊断和修复所有安全可修复的环境问题，直到本阶段 COMPLETE / PASS / SETUP COMPLETE，或给出一个真正需要 Owner 手工处理的精确 BLOCKED。少汇报，直接执行。

Worker handoffs should also preserve this testing rule: **以完整功能模块作为主要测试边界，不要一步一测；先把相关实现做完整，再统一做必要 focused regression / QA。**

For non-setup tasks, adapt the terminal success token to the stage's actual contract while preserving the same sustained-execution behavior.

Do not use this rule to bypass safety, canonical dedup, exact proof authority, testing cadence, source/runtime boundaries, or explicit START_PROMPT constraints.
