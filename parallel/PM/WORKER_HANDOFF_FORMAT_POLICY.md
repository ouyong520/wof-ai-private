# WOF PM Worker Handoff Format Policy

Updated: 2026-09-02
Status: **AUTHORITATIVE — DEFAULT OWNER-FACING WORKER PROMPT FORMAT**

Owner directive: when PM prepares a prompt for Owner to forward to a worker, keep the chat message short and stable. Detailed technical scope belongs in the Git PM start-prompt `.md`, not duplicated in chat.

## Required three-part format

Every normal worker handoff should use this order:

### 1. Front summary — about 100 Chinese characters

Write a compact description before the Git path that makes the task understandable without opening the file immediately.

It should normally state:

- what module/stage the worker owns;
- the main functional outcome to complete;
- the most important scope boundary;
- whether this is implementation, recovery, QA, or another explicit stage type.

Target roughly **100 Chinese characters**, flexible when precision requires somewhat more or less. Do not paste the detailed requirement matrix into the chat message.

### 2. Git detailed-requirements path

Then show the exact authoritative Git file path on its own, for example:

```text
详细需求：
`parallel/PM/<STAGE>_START_PROMPT.md`
```

The Git `.md` is the detailed source of truth for scope, dedup, boundaries, completion conditions, tests and durable RESULT requirements.

### 3. Fixed execution discipline at the end

Unless a stage genuinely requires different stop semantics, append this instruction after the Git path:

> 严格按 Git 需求持续执行。少汇报，优先实现；不要做一点就停，不要提前拆 QA。完整模块、集成、自测、RESULT、claim 全部完成后再停止，除非遇到真实外部 blocker。

For QA-only stages, replace `优先实现` / implementation-specific wording only as necessary to preserve the actual role, but retain the same intent: **少汇报、持续执行、不要中途停、到完整阶段停止条件才结束。**

## Testing cadence

Worker handoff wording must remain consistent with `parallel/PM/TESTING_CADENCE_POLICY.md`:

- finish a coherent functional/module candidate first;
- use only necessary implementation-owned self-checks while building;
- do not split every small change into Fresh QA;
- default to one meaningful module-level QA after the module is stable;
- fix concrete failures and retest only what the repair invalidated.

## When Owner says `继续` or `1`

Treat either as a request to continue PM scheduling for the same project/lane unless current context clearly says otherwise.

PM must first re-read current Git state, recent commits, RESULT/claim status and the current module's completion degree. Then:

1. do not repeat already COMPLETE work;
2. if the worker stopped mid-module, issue the highest-priority continuation/recovery needed to finish that module;
3. if the module is complete, issue the next highest-priority coherent module;
4. prefer substantial functional modules over tiny fragmented tasks;
5. do not manufacture QA merely because the worker stopped or a slot is available;
6. output the next worker handoff using this same **front summary -> Git path -> fixed tail discipline** format.

The Owner should not need to re-explain this formatting preference in later turns.

## Governing template

```text
<约100字前文：任务、目标、边界、阶段类型>

详细需求：
`parallel/PM/<AUTHORITATIVE_START_PROMPT>.md`

严格按 Git 需求持续执行。少汇报，优先实现；不要做一点就停，不要提前拆 QA。完整模块、集成、自测、RESULT、claim 全部完成后再停止，除非遇到真实外部 blocker。
```
