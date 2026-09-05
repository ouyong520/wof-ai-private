# Project-wide Agent / PM Bootstrap

This file applies repository-wide, including fresh chats and newly assigned PMs/workers.

## Mandatory product governance — read first

Any PM or worker taking over any WOF product MUST first read and obey:

- `PROJECT_PRODUCT_GOVERNANCE.md`

The WOF program contains three independent product lines:

- Alpha mainline product;
- Unified Collector;
- Training Farm / 10训.

Unless the Owner explicitly authorizes a cross-line task, work only inside the assigned product line. Do not read, run, modify, test, package, schedule, or use another product line's claims/RESULT/runtime/package/CI/progress as evidence for the assigned product.

PMs manage product progression rather than becoming long-running production developers. A PM may read code, follow the real call chain, run bounded verification, define requirements, dispatch workers and accept exact commits. Production implementation should be assigned to workers. Once the first real Owner-facing blocker is known, broad takeover analysis must stop and execution must begin.

Repository/CI/claim/RESULT/package completion is not the same as product delivery. Owner-facing reality wins. Keep the feedback loop short: real blocker -> requirement -> worker implementation -> batched functional verification -> Owner-testable candidate -> Owner feedback -> next fix.

Each product normally uses **1 PM + 1-3 implementation workers**. Do not create workers merely to fill capacity.

Owner shorthand:

- `1` = continue project progression; PM verifies GitHub, accepts finished work and chooses the next requirement.
- `1 2` = continue, and two implementation workers have finished / two worker slots are available after PM GitHub acceptance. PM may assign up to two new independent tasks if genuinely useful.

Do not allow endless internal development without Owner testing. Once a coherent feature is safe and materially changed, converge to an Owner-testable candidate.

Full/broad testing is normally batched at a **major version / coherent feature-batch / final candidate** boundary. Do not run broad regression, QA, CI or Owner testing after every small commit. Cheap implementation self-checks are allowed while coding.

## Mandatory PM bootstrap

Any agent acting as Product Manager, orchestrator, reviewer, or task issuer MUST first read and follow:

- `PROJECT_PRODUCT_GOVERNANCE.md`
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/GLOBAL_PM_WORKER_HANDOFF_RULES.md`
- `parallel/PM/GLOBAL_GITHUB_REUSE_FIRST_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`

These rules survive chat/thread changes. A fresh PM chat must not rely on old chat memory; GitHub durable state is authoritative.

## Owner interaction contract

- Standalone `1` means **continue project progression**. The current worker may already be finished. PM must inspect latest Git HEAD, durable RESULT, canonical/stage claims and actual changes, independently judge the worker result, then choose the shortest legitimate next step.
- `1 2` means **continue progression and two implementation workers have finished / two worker slots are free after Git acceptance**. Verify both finished workers first, then dispatch at most two new independent worker tasks if useful.
- Owner is the relay and strategic/product-direction leader. Owner is NOT responsible for reviewing worker quality, implementation details, tests, commits, claims, or routine next-step selection. PM owns those decisions end-to-end.
- PM must keep Owner communication concise. Worker handoffs should normally begin with about 100 Chinese characters of task intent, put the authoritative Git/START_PROMPT path in the middle, and avoid repeating repository history already captured in Git.
- PM should give Owner only the next prompt that needs relaying or a genuinely strategic decision that needs Owner leadership.

## New PM chat operating brief

Every fresh PM chat must operate under the following contract without requiring the Owner to restate it:

- GitHub durable state is the execution authority. Read current main, relevant START_PROMPT, RESULT, canonical/stage claims and global PM rules before judging status.
- PM owns worker review, quality judgment, acceptance/rejection, recovery/QA necessity, technical routing, prioritization and next-stage creation. Never ask the Owner to review whether a worker did the job correctly.
- Owner mainly relays concise worker prompts and provides leadership on important product direction, architecture choices and priority decisions.
- Standalone `1` means **continue**: first inspect Git reality, then accept/close/fix/recover or issue the next legitimate requirement. Do not mechanically tell the same worker to continue.
- `1 2` means two worker slots have become available after completion; verify the work in Git, then use up to two slots only for independent highest-value work.
- One product normally has one PM and one to three implementation workers. The PM is not an implementation slot.
- PM must proactively identify the highest-value current blocker and advance the shortest path toward usable product value. Do not wait for the Owner to invent routine next tasks.
- Before committing to a new non-trivial implementation architecture, PM must apply `parallel/PM/GLOBAL_GITHUB_REUSE_FIRST_POLICY.md`: check maintained GitHub/official-ecosystem candidates, compare maintenance/deployment/reusable functions/licensing, make an explicit DIRECT_USE/ADAPT/FORK/REFERENCE_ONLY/SELF_BUILD/DEFER decision, and define the simplest MVP. Reuse an existing recent durable decision rather than repeating research for confidence.
- Do not create parallel workers just to fill capacity. Parallelize only genuinely independent work that safely shortens the mainline.
- Do not proliferate recovery, QA or cross-check stages. Prefer coherent implementation through integration, one batched regression at the feature/release boundary, durable RESULT and minimal justified downstream gate.
- Owner is not the debugger. Exhaust code inspection, CI, historical evidence, fixtures, mocks, automation and safe diagnosis before asking for manual/live action.
- Request Owner live testing when a safe coherent candidate exists and real-environment feedback is valuable; do not postpone it indefinitely for internal polish.
- Communication with Owner must stay concise. Normally provide only current verdict, whether Owner action is needed, and the exact next worker prompt that must be relayed.

## Mandatory GitHub reuse-first preflight

For any new non-trivial capability, dependency, infrastructure component, adapter, workflow, algorithmic subsystem, UI/runtime integration, storage/query layer, automation layer or similar engineering surface, PM must check whether maintained GitHub/open-source code can be used directly or adapted before choosing a self-built architecture.

The required sequence is:

`READ CURRENT GIT -> DEDUP -> GITHUB/OFFICIAL-ECOSYSTEM REUSE PREFLIGHT -> DIRECT_USE/ADAPT/FORK/REFERENCE_ONLY/SELF_BUILD/DEFER -> SIMPLEST MVP -> IMPLEMENT`

A meaningful candidate review must answer:

1. whether the project is still maintained;
2. how difficult deployment/integration is;
3. which exact functions/modules can be reused;
4. which candidate is best for secondary development;
5. whether the correct decision is direct use, adaptation, fork, reference-only, self-build or defer;
6. the simplest MVP that minimizes new code, dependencies, deployment burden, maintenance cost and Owner manual work.

License, attribution/copyleft implications and material supply-chain/security risk must be checked before import/fork. Stars alone are not maintenance evidence. Do not force a heavyweight framework into the project when a small local implementation has lower total lifecycle cost.

The full authoritative rule is `parallel/PM/GLOBAL_GITHUB_REUSE_FIRST_POLICY.md`.

## Mandatory duplicate-task preflight — Owner may paste the wrong or repeated task

The Owner may accidentally paste a task that is already ACTIVE, already COMPLETE, superseded, or logically equivalent to another task under a different stage name. Every PM and worker must protect the project from duplicate execution.

Before any meaningful task work or implementation mutation:

- Re-read current `main`, relevant durable RESULTs, canonical dedup claims, stage claims, recent equivalent commits and the authoritative START_PROMPT.
- Apply `parallel/PM/STAGE_DEDUP_GUARD.md` and canonical dedup v2. Compare the logical work item, not only the pasted stage name.
- If an equivalent task is already ACTIVE/claimed by another worker, do **not** execute it again and do not create a parallel replacement merely because the Owner pasted it again. Return a concise duplicate/claimed verdict to the Owner.
- If an equivalent task is already COMPLETE/PASS with durable authority and no material drift requiring a new stage, do **not** execute it again. Tell the Owner that it is already completed and let PM continue to the next legitimate project step.
- If the pasted task has been superseded by newer authority, do not revive the old work. Follow the current successor authority instead.
- If only a genuinely unfinished closeout or concrete successor repair remains, route only that remaining work; do not redo completed implementation.
- A duplicate paste is never permission to bypass canonical claims, invent a new dedup key, open an unnecessary recovery, or rerun already-passing QA.

Preferred duplicate terminal behavior:

`ALREADY ACTIVE / CLAIMED — NO EXECUTION`

or

`ALREADY COMPLETE — NO EXECUTION`

followed by a concise note to the Owner stating that the pasted task is already in progress or already finished. PM then decides the actual next step from Git truth.

## Mandatory durable worker progress / summary — unfinished work must never disappear into chat

For every PM-dispatched Alpha worker, durable progress reporting is mandatory and is part of the execution contract, not optional documentation.

Authoritative protocol:

- `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`
- terminal reporting remains governed by `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`

Rules:

- After canonical dedup claim **and** stage claim are both created and re-read with the exact matching `claimToken`, the worker must create `parallel/PM/PROGRESS/<stageId>_PROGRESS.json` **before meaningful implementation begins**.
- The progress file must be updated after the first durable implementation milestone, after each coherent material milestone, after focused self-check, immediately when a real blocker is discovered, immediately before terminal RESULT publication, and before any voluntary non-terminal stop.
- If tool/runtime/context budget is visibly low, **writing the PROGRESS checkpoint takes priority over optional additional implementation or tests**.
- A worker that must stop before terminal publication must durably record its state as `INTERRUPTED`, `READY_TO_PUBLISH`, or `BLOCKED_PENDING_RESULT` as appropriate, with exact completed work, remaining work, tests, blocker and next action. A chat-only summary is insufficient.
- `ACTIVE` in a canonical/stage claim means only that the logical claim is not terminally closed. It must **never** be interpreted as proof that the worker chat is still running.
- `overallPercent=100` is allowed only after durable terminal RESULT publication **and** matching canonical/stage claim closeout are complete. Code-complete or tests-pass alone is not 100%.
- Terminal worker truth requires `RESULT.json` + `RESULT.md`, matching terminal claim closeout, final `WORKER_RESULT <stageId> <STATE>` commit, and a terminal PROGRESS checkpoint consistent with those artifacts.
- A continuation of interrupted work must read the current PROGRESS checkpoint first, verify the exact existing claim token, reconcile newer Git commits, and continue the same logical claim. Do not create a new claim or recovery merely because the chat/window changed.
- When the Owner asks for status, PM must read in this order: **terminal RESULT -> canonical/stage claim -> per-stage PROGRESS -> recent commits newer than the checkpoint**. PM must report the last durable checkpoint and must not guess live execution from `ACTIVE` alone.
- If an older/current worker stopped before this protocol and no PROGRESS exists, PM may reconstruct only the progress file from Git evidence plus the worker's explicit report using `writerRole=PM_RECONSTRUCTION`; this does not close claims or fabricate unpublished work.

Required lifecycle vocabulary:

`CLAIMED -> IMPLEMENTING -> SELF_CHECK -> READY_TO_PUBLISH -> PUBLISHING -> TERMINAL`

Exceptional non-terminal states:

`BLOCKED_PENDING_RESULT` / `INTERRUPTED`

The purpose is simple: **whether a worker finishes, blocks, times out, or loses its execution window, Git must still show exactly how far it got and what remains.**

## Testing cadence — batch by major version / coherent feature set

Testing exists to protect product correctness, not to consume development time after every small edit.

Project-wide default:

- Use the **major version candidate / coherent completed feature batch / meaningful release candidate** as the normal full testing boundary.
- Finish related implementation and integration first, then run one focused/batched regression for that capability.
- Do **not** run a new broad QA, full regression, CI cycle or Owner test after every file, helper, small patch, manifest edit or intermediate sub-step.
- Syntax checks, targeted unit checks or very cheap local sanity checks are allowed when they directly help implementation; they are implementation self-checks, not separate QA stages.
- Batch related defects and fixes, then retest once at the functional boundary.
- Open independent QA only at a meaningful frozen candidate boundary or when a concrete high-risk reason requires it.
- After QA failure, repair the concrete failure set and use one focused successor retest; do not create one QA/recovery generation per bug.
- Do not repeat already-passing tests merely for confidence when the relevant SUT has not materially changed.
- Once a coherent safe candidate exists, do not keep developing indefinitely just to avoid Owner testing.

Preferred cadence:

`1-3 workers implement coherent feature -> integrate -> one batched regression -> Owner-testable candidate -> Owner feedback`

Avoid:

`write a little -> full test -> write a little -> full test -> QA -> recovery -> more development -> no Owner test`

## Worker handoff format

Default PM-to-worker handoff:

- opening: roughly 100 Chinese characters covering task goal, expected outcome and key boundary;
- middle: repository plus authoritative START_PROMPT path/link;
- ending: sustained-execution instruction; do not repeat long background already stored in Git.

Every worker handoff must preserve duplicate preflight behavior: **先检查该逻辑任务是否已经 ACTIVE / COMPLETE / superseded；如果已在做或已完成，不重复执行，直接告诉 Owner 已认领/已完成并 NO EXECUTION。**

Every Alpha worker handoff and non-terminal continuation must also preserve durable progress reporting: **claim/stage claim 验真后先建立或读取 `parallel/PM/PROGRESS/<stageId>_PROGRESS.json`；每个关键里程碑、测试、blocker、终态发布前和任何非终态停止前都必须更新；窗口不足时优先写 PROGRESS，禁止只在聊天里留总结。**

For implementation/setup/recovery work, handoffs should end with the equivalent of:

> 如果遇到问题，不要停在一句报错。继续自动诊断和修复所有安全可修复的环境问题，直到本阶段 COMPLETE / PASS / SETUP COMPLETE，或给出一个真正需要 Owner 手工处理的精确 BLOCKED。少汇报，直接执行。

Worker handoffs should also preserve this testing rule: **以完整功能模块/大版本候选作为主要测试边界，不要一步一测；先把相关实现做完整，再统一做必要 regression / QA。**

For non-setup tasks, adapt the terminal success token to the stage's actual contract while preserving the same sustained-execution behavior.

Do not use this rule to bypass safety, canonical dedup, exact proof authority, testing cadence, source/runtime boundaries, or explicit START_PROMPT constraints.
