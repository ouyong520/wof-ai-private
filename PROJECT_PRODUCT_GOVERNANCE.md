# WOF Project Product Governance

Status: ACTIVE / repository-wide

This file is the mandatory first-read for any PM or worker taking over work in this repository.

## 1. Three product lines — strict isolation

The WOF program currently contains three independent product lines:

1. **Alpha mainline product** — the software the Owner actually runs.
2. **Unified Collector** — the user-facing data collection product.
3. **Training Farm / 10训** — the training system and its workers.

These are separate products. Do not use one product line's claims, RESULT files, runtime state, package state, CI status, or progress to declare another product line healthy or complete.

Unless the Owner explicitly authorizes a cross-line task, PMs and workers must not read, modify, run, test, package, or schedule code outside the product line they were assigned.

A permitted interface between products does not merge their product authority. For example, a Collector adapter may read Training Farm data, but Collector does not become Training Farm authority and Training Farm progress does not count as Collector delivery.

## 2. GitHub current main is the state center

Chat threads are not the project state authority.

On takeover or resume:

- re-read the current GitHub `main` HEAD;
- inspect the relevant current production code path;
- inspect the latest applicable authority / RESULT / claim files;
- consume work by exact commit SHA;
- do not wait for another chat thread to reply if its work is already committed;
- do not inherit an old PASS / BLOCKED / ACTIVE status without reconciling it against current main.

If historical documents conflict with current production code, current main plus the latest valid product authority wins.

## 3. PM role — manage product, do not become the production developer

A product manager may:

- read production code and follow the real call chain;
- run necessary safe verification;
- inspect logs, tests, CI, packages and runtime evidence;
- define the current product blocker;
- write requirements, acceptance criteria and PM/dispatch documents;
- dispatch workers;
- verify exact worker commits against current main;
- decide what ships and what is tested by the Owner.

A product manager should **not** become the long-running production implementation worker.

Production implementation is assigned to workers. The PM owns prioritization, task definition, acceptance, integration decisions and delivery cadence.

The PM may perform a bounded takeover audit, but once the first real product blocker is identified, broad analysis must stop and execution must begin.

## 4. Product delivery beats process completion

The following are engineering evidence, not product delivery by themselves:

- CI PASS;
- unit/regression PASS;
- claim COMPLETE;
- RESULT COMPLETE;
- package generated;
- QA complete;
- recovery complete;
- overlay enabled;
- service running;
- synthetic fixture PASS.

A product is only considered delivered when the Owner-facing result works.

Current examples:

- **Alpha:** the real player/enemy head display is visibly correct in the Owner's running software.
- **Unified Collector:** the delivered user EXE binds to the real supported WOF runtime and actually produces valid collected data.
- **Training Farm / 10训:** real workers run the intended training chain with correct isolation and produce real training outputs/checkpoints/results.

Repository-complete and product-delivered are different states and must be reported separately.

## 5. Short Owner feedback loop is mandatory

Do not allow internal work to run for a long time without giving the Owner a testable product change.

Normal cadence:

`real blocker -> PM writes one minimal requirement -> worker implements -> focused verification -> Owner-testable candidate -> Owner real feedback -> next fix`

Rules:

- after a user-visible capability changes and the product is safe to run, prepare an Owner-testable candidate promptly;
- do not wait for unrelated cleanup, extra QA, architecture polish or additional recovery work before allowing Owner testing;
- Owner real-world feedback outranks speculative internal problems;
- do not allow more than two implementation commits in a row with no Owner-testable product change unless a clearly documented safety/data-integrity blocker requires it.

Before approving a new batch, the PM must answer:

> What will the Owner be able to see, do, or obtain after this batch that they cannot see, do, or obtain now?

If the answer is only more tests, more documents, more authority, more recovery, more cleanup, or more internal status, the batch is not approved unless it closes a concrete safety/data-integrity blocker.

## 6. Testing serves product progress

Testing is not a separate product line and must not self-expand.

Use three levels only:

1. **implementation self-check** — smallest affected verification after a change;
2. **focused regression** — once the target capability is integrated;
3. **final acceptance** — once a real candidate is ready for delivery.

Do not create QA-of-QA chains, repeated confidence-only full regressions, fresh QA successors, or recovery layers unless a real new defect or authority break justifies them.

A real Owner-observed failure immediately becomes higher priority than speculative additional testing.

## 7. Version / recovery discipline

Do not create a new version, recovery, workstream or QA stage merely because the previous one ended.

A new version should correspond to a material product behavior change.

Do not create a new version for documentation-only changes, claim cleanup, authority cleanup, confidence reruns, or packaging metadata alone.

Do not open a recovery if the existing active authority can simply continue.

## 8. Worker dispatch rules

Workers receive narrow executable requirements with:

- one product line only;
- current main / exact authority;
- concrete production scope;
- concrete acceptance criteria;
- explicit forbidden scope;
- expected terminal state: integration-ready / COMPLETE / precise BLOCKED.

Workers should commit implementation and evidence to GitHub. Chat replies are secondary.

PM acceptance consumes exact commits from GitHub rather than depending on thread-to-thread conversation handoff.

## 9. Analysis stop condition

A takeover analysis is complete as soon as the PM can state:

1. the current real product execution path;
2. the first real product blocker on that path;
3. what is already proved in repository/synthetic evidence;
4. what still requires real runtime evidence;
5. the single next worker requirement that moves the Owner-facing product forward.

After these five items are known, stop broad historical analysis and dispatch execution.

## 10. Product-line current north-star outcomes

These are product outcomes, not permanent technical designs.

### Alpha mainline

Owner runs the software and sees correct production behavior in the real game. Current head-display work must be judged by actual visible player/enemy head placement and tracking, not by internal overlay state alone.

### Unified Collector

Owner/user runs the delivered Collector executable and real supported WOF sessions become eligible, bind uniquely and produce valid collection output. `eligible=0`, ambiguous runtime binding, or zero produced data is a product blocker even if repository acceptance is green.

### Training Farm / 10训

The intended worker fleet actually trains with strict worker/generation/state/result isolation and produces real usable outputs. Fixture-only success does not substitute for real training operation where real runtime proof is required.

## 11. Takeover reporting format

After bounded takeover, PM reports only:

1. current product execution path;
2. current Owner-visible state;
3. first real blocker;
4. what is repository/synthetic proven versus real-runtime proven;
5. next worker requirement;
6. when the Owner should next receive a testable candidate.

Keep this concise. The purpose of PM analysis is to accelerate product delivery, not to create more project process.
