# WOF PM Testing Cadence Policy

Updated: 2026-09-02
Status: **AUTHORITATIVE — MANDATORY FOR PM SCHEDULING AND ALL NEW IMPLEMENTATION / QA START PROMPTS**

Owner directive:

> 不需要做完一点代码就测试。应该按功能 / 模块完成后再统一测试；存在具体问题才回去修复；不要过多测试。

This policy exists to keep engineering time focused on product implementation and prevent QA / closeout / recovery / cross-check chains from becoming larger than the feature work itself.

## 1. Default cadence: implement the whole functional module first

A functional/module implementation stage should normally continue until the intended module candidate is coherent and complete, including all work in the same implementation domain that is required to make it runnable:

- code implementation;
- integration / wiring;
- schema or contract updates;
- loader/bootstrap changes required by that module;
- lifecycle / authority propagation required by that module;
- manifest/blob repinning required by that module;
- implementation-owned regression updates;
- durable implementation RESULT / handoff.

Do **not** split these into separate independent QA stages merely because one sub-file or sub-step was completed.

Examples of the forbidden default pattern:

`core change -> Fresh QA -> Top change -> Fresh QA -> Worker change -> Fresh QA -> manifest closeout -> another QA`

Preferred pattern:

`complete coherent module candidate -> implementation self-check -> freeze candidate -> one module-level independent QA`

## 2. Development self-checks are not independent QA stages

During implementation, developers may and should run the minimum checks needed to avoid knowingly committing broken code, for example:

- syntax / parse checks;
- unit tests directly owned by the implementation;
- narrow regression tests for changed logic;
- deterministic fixture smoke tests;
- manifest/hash consistency checks;
- static invariants and safety assertions.

These are **implementation self-checks**. They do not require a new QA stage, fresh worker, second opinion, cross-check, recovery generation, or PM reconciliation stage.

The purpose is to keep one implementation worker responsible for finishing the module rather than exiting after every small change.

## 3. Independent QA is scheduled at a meaningful module boundary

Default rule:

**One coherent functional/module candidate -> one independent QA gate.**

PM should schedule independent Fresh QA only when all of the following are true:

1. the functional/module implementation is materially complete;
2. required integration in that module is wired;
3. implementation-owned regressions/self-checks pass or have an explicit understood limitation;
4. required manifest/blob pins for that candidate are current;
5. the candidate is stable enough that QA results will not immediately be invalidated by planned edits in the same module.

Do not launch Fresh QA against an obviously partial candidate just to discover integration work that the implementation stage already knows remains unfinished.

## 4. Batch related fixes before retesting

When QA finds one or more concrete defects in the same functional/module domain:

1. record the exact defects;
2. return to implementation;
3. fix the known related defects together where practical;
4. finish the module candidate again;
5. run one focused retest / successor QA for the repaired candidate.

Do not create a new QA generation after every individual bug fix within the same failure cluster.

The repair loop should look like:

`module QA -> concrete failures -> focused module fix -> one retest`

not:

`QA -> fix A -> QA -> fix B -> QA -> closeout -> cross-check -> second opinion`.

## 5. Extra QA requires a concrete reason

Second-opinion, cross-check, additional independent validation, broad audit, or another Fresh QA generation is **not** the default.

PM may schedule extra validation only when there is a specific reason such as:

- the previous QA itself is shown to be invalid or stale;
- the SUT materially changed after the QA in a way that affects the verified contract;
- a concrete high-risk defect escaped the previous gate;
- an explicit independent authority requirement cannot be satisfied by the existing QA;
- Owner explicitly asks for an additional independent opinion.

"A worker slot is free", "more confidence would be nice", or "another version number is available" are not valid reasons.

## 6. Closeout / manifest / documentation are normally part of implementation

If a module still needs its final manifest repin, integration result, exact blob list, or claim/result closeout, the implementation stage is not complete yet.

Do not normally create a separate QA or closeout stage just to discover that those implementation deliverables were never finished.

A stopped worker may require PM-authorized recovery for ownership reasons, but recovery should resume the **same unfinished implementation objective** and finish it end-to-end. Recovery is not a reason to add another QA layer.

## 7. Test levels

Use three distinct levels and do not confuse them:

### A. Implementation self-check
Runs while code is being written. Cheap, local, narrow, owned by the implementation stage.

### B. Module-level independent QA
Runs once the functional/module candidate is coherent. Default: one independent QA per stable candidate.

### C. Product / real-game acceptance
Runs only when repository/module gates are green and the remaining facts are intrinsically live. Combine checks into one bounded Owner run where possible.

Do not turn every implementation self-check into B, and do not use C as exploratory debugging.

## 8. PM scheduling rules

Before opening any new QA/retest/cross-check task, PM must answer:

1. **Which functional/module boundary has just completed?**
2. **What stable candidate is being verified?**
3. **Why would the existing implementation self-checks be insufficient for this boundary?**
4. **Has equivalent current-candidate QA already passed?**
5. **Will planned same-module implementation immediately invalidate this QA?**

If there is no completed module boundary, or the candidate is still being actively changed, normally keep implementing instead of opening QA.

PM should prefer leaving worker slots idle over manufacturing validation work.

## 9. Current release-path principle

For a release candidate, the preferred flow is:

`finish functional/module implementation -> freeze candidate -> one final module/release QA -> bounded real-game acceptance -> release/freeze decision`

If the QA passes, proceed. Do not add second-opinion/cross-check/reconciliation loops without a new concrete defect or changed SUT.

If the QA fails, fix the concrete defect(s), then retest the repaired gate. Do not restart the entire historical QA chain.

## 10. Success metric

Testing exists to protect user value, not to maximize test count.

PM should actively avoid a project state where QA/audit/closeout stage count grows faster than meaningful implementation work without concrete evidence justifying that validation load.

The governing principle is:

**Build a coherent feature/module first. Test it once at the meaningful boundary. Fix real failures. Retest only what the repair invalidated. Then move forward.**
