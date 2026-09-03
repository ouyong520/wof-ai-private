# Project-wide Agent / PM Bootstrap

This file applies repository-wide, including fresh chats and newly assigned PMs/workers.

## Mandatory PM bootstrap

Any agent acting as Product Manager, orchestrator, reviewer, or task issuer MUST first read and follow:

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/GLOBAL_PM_WORKER_HANDOFF_RULES.md`
- `parallel/PM/GLOBAL_GITHUB_REUSE_FIRST_POLICY.md`
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
- Before committing to a new non-trivial implementation architecture, PM must apply `parallel/PM/GLOBAL_GITHUB_REUSE_FIRST_POLICY.md`: check maintained GitHub/official-ecosystem candidates, compare maintenance/deployment/reusable functions/licensing, make an explicit DIRECT_USE/ADAPT/FORK/REFERENCE_ONLY/SELF_BUILD/DEFER decision, and define the simplest MVP. Reuse an existing recent durable decision rather than repeating research for confidence.
- Do not create parallel workers just to fill capacity. Parallelize only genuinely independent work that safely shortens the mainline.
- Do not proliferate recovery, QA or cross-check stages. Prefer one coherent implementation module through integration, self-check, durable RESULT and claim closeout, then the minimum justified downstream gate.
- Owner is not the debugger. Exhaust code inspection, CI, historical evidence, fixtures, mocks, automation and safe diagnosis before asking for manual/live action.
- Request Owner live testing only when the remaining fact is intrinsically real-environment dependent, and keep that run bounded, simple and product-like.
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

Every worker handoff must preserve duplicate preflight behavior: **先检查该逻辑任务是否已经 ACTIVE / COMPLETE / superseded；如果已在做或已完成，不重复执行，直接告诉 Owner 已认领/已完成并 NO EXECUTION。**

For implementation/setup/recovery work, handoffs should end with the equivalent of:

> 如果遇到问题，不要停在一句报错。继续自动诊断和修复所有安全可修复的环境问题，直到本阶段 COMPLETE / PASS / SETUP COMPLETE，或给出一个真正需要 Owner 手工处理的精确 BLOCKED。少汇报，直接执行。

Worker handoffs should also preserve this testing rule: **以完整功能模块作为主要测试边界，不要一步一测；先把相关实现做完整，再统一做必要 focused regression / QA。**

For non-setup tasks, adapt the terminal success token to the stage's actual contract while preserving the same sustained-execution behavior.

Do not use this rule to bypass safety, canonical dedup, exact proof authority, testing cadence, source/runtime boundaries, or explicit START_PROMPT constraints.
