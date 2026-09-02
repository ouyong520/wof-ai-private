# WinKawaks Collector Worker Execution Policy

Updated: 2026-09-02
Status: **AUTHORITATIVE — applies to Collector development/recovery tasks unless a later Owner directive explicitly overrides it**

## Purpose

Keep the Collector side lane implementation-heavy, low-chatter, and module-oriented.

The default objective is:

`finish useful Collector functionality -> self-check the completed module -> durable RESULT -> only then consider one meaningful module-level QA`

Do not optimize for task count, QA count, report count, or worker occupancy.

## 1. Worker prompts should stay short

The chat prompt sent to a worker should normally contain only:

- task name;
- repository name(s);
- one authoritative START_PROMPT / requirements MD path;
- instruction to obey canonical dedup v2;
- instruction to continue until the module is actually complete or precisely blocked.

Detailed requirements, boundaries, acceptance criteria, recovery context and file lists belong in GitHub Markdown, not in a long chat prompt.

## 2. Finish the module before stopping

A Collector implementation worker should not voluntarily stop after only:

- reading the repository;
- creating a claim;
- implementing one sub-file;
- wiring only part of the feature;
- adding tests without completing integration;
- documenting unfinished code;
- finding a small defect that can reasonably be fixed inside the assigned scope;
- producing an intermediate status update.

The worker owns the coherent functional/module objective end-to-end:

`code + integration + schema/contract + safety/fail-closed behavior + compatibility + implementation self-checks + docs/manifest where required + durable RESULT + claim/stage closeout`

Continue working until one of these is true:

1. the assigned functional/module objective is complete and self-checked; or
2. a precise blocker exists that cannot be resolved inside the assigned scope/repositories/permissions.

Do not stop merely because the task became long.

## 3. Reporting should be sparse

Keep progress reports brief and infrequent.

Report when useful for Owner steering, especially:

- a material implementation milestone has landed;
- a real blocker is discovered;
- scope facts materially changed;
- the module is complete.

Do not repeatedly narrate routine file reads, small edits, individual unit tests, or every commit.

Implementation work is more valuable than commentary.

## 4. Module-first testing cadence

`parallel/PM/TESTING_CADENCE_POLICY.md` is mandatory.

Default:

`complete coherent module -> implementation self-check -> freeze candidate -> one module-level independent QA if justified`

During implementation use only the tests needed to keep the module healthy:

- syntax/compile;
- directly owned unit tests;
- focused regression;
- deterministic fixture/self-check;
- integrity/hash/schema checks;
- safety/fail-closed assertions.

Do not create Fresh QA, second opinion, cross-check, QA V2/V3/V4, readiness audit or reconciliation after every small change.

If a later QA finds concrete defects, fix the related defect cluster and retest the affected boundary once. Do not replay the historical QA chain.

Testing exists to protect functionality, not consume development time.

## 5. Recovery after a stopped worker

If Owner reports that a worker stopped, PM should re-read current repository state before issuing the next instruction.

PM must determine:

- what code already landed;
- what requirements are already complete;
- what self-checks/results already exist;
- whether the claim is truly active residue or completed;
- the smallest remaining coherent functional objective.

Then issue a short Recovery/Continue prompt that resumes from current HEAD.

Do not ask the replacement worker to restart the module from zero unless repository facts require it.

Do not manufacture QA merely because the previous worker stopped.

A stopped implementation worker normally means:

`resume unfinished implementation -> finish module -> self-check -> RESULT`

not:

`stop -> QA -> audit -> second opinion -> another implementation task`.

## 6. Owner shorthand: “继续” or “1”

When Owner says `继续` or `1` after a Collector worker stops/completes, PM should:

1. re-read current `main` in `wof-ai-private` and `wof-winkawaks-bridge`;
2. inspect recent Collector commits;
3. inspect current claims / RESULT / START_PROMPT;
4. classify what is already complete vs unfinished;
5. select the highest-value remaining Collector development objective;
6. prefer finishing the current module before starting a new module;
7. if the current module is complete, select the next roadmap module;
8. only schedule independent QA at a meaningful completed module boundary;
9. keep the worker prompt short and point it to GitHub MD for details.

PM should not make Owner redesign the roadmap every time a worker stops.

## 7. Priority order

Unless a concrete current defect changes priority:

1. **P0 data correctness / identity integrity**
2. **P1 capture capability and long-session durability**
3. **P1 reusable dataset identity/catalog**
4. **P1 storage / retention / archive / health**
5. **P2 segment-aware analysis tooling**
6. **P2 batch acquisition automation**

Finish the currently active coherent module before moving down the list.

## 8. Side-lane isolation

Always obey `COLLECTOR_ROUTING.md` and `RUNTIME_DATA_SOURCE_BOUNDARIES.md`.

Collector is an independent R&D/data-acquisition side lane.

Collector incomplete/blocked/awaiting QA is not, by itself:

- an Alpha V1 release blocker;
- a reason to stop Browser/WOF acceptance;
- a reason to stop Training Farm;
- a reason to stop the current 10-worker training lane.

Collector remains read-only:

`readOnly=true`

`writesGameMemory=false`

`inputInjection=false`

Browser, WinKawaks and Training Farm provenance remain distinct.

## 9. Stop rule

At the tail of every Collector implementation/recovery START_PROMPT, include an explicit instruction equivalent to:

> Do not stop at an intermediate milestone. Keep implementation reporting sparse. Continue through the complete assigned functional/module scope, implementation-owned self-checks, durable RESULT and required claim/stage closeout. Stop only at COMPLETE or a precise unavoidable BLOCKED condition.

This is an execution rule, not permission to expand scope indefinitely. The worker should complete the assigned coherent module, not wander into unrelated projects.
