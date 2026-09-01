# WOF PM Mainline-First Priority Policy

Updated: 2026-09-01

Status: **MANDATORY**

## Core rule

Concurrency capacity is a ceiling, not a target.

Do **not** create work merely to keep every chat busy. A task only gets a slot if it materially advances the shortest path to a trustworthy user product, removes a blocker/risk on that path, or creates a reusable accelerator that materially reduces future research/engineering/Owner time.

## Priority classes

### P0 — Mainline blocker

Use immediately. Examples:
- blocks authoritative Browser/Worker/WASM/World identity proof;
- can corrupt evidence ownership/admission;
- can make research/QA verdict falsely PASS;
- blocks Alpha transport/acceptance/release;
- risks wrong room/session/Worker association.

P0 tasks outrank all other work.

### P1 — Mainline risk / owner-time reducer

Use when it directly supports a P0/P0-closed path or prevents wasted real testing. Examples:
- cross-component conformance needed to prove P0 fixes align;
- Discovery V2 endpoint/session isolation drift;
- global regression coverage for current mainline components;
- preflight that prevents Owner from running a known-broken package;
- Chinese/runtime packaging defect that blocks owner-ready acceptance.

### P2 — Near-term downstream accelerator

P2 is not automatically idle merely because P0/P1 exists.

A P2 task may use spare concurrency while P0/P1 runs when all of the following are true:
- write scope does not conflict with active P0/P1;
- its result is unlikely to be invalidated by the current P0/P1 implementation changes;
- it creates durable leverage for the Alpha/Beta/Safe Path/0-damage path;
- it reduces later engineering time, evidence collection time, or Owner intervention.

Examples:
- one-click packaging after component interfaces stabilize;
- acceptance automation after transport contract/runtime proof stabilizes;
- Beta validator queue tooling after Validator semantics stabilize;
- synthetic runtime/endurance simulation;
- reusable corpus replay;
- reverse-engineering tools that expose stable game state/geometry/attack semantics;
- emulator adapters, deterministic fixtures, trace replay, and automated differential analysis.

### P3 — Useful but non-blocking

Normally do not consume a slot while stronger P0/P1/P2 work exists. Examples:
- polish not required for current release gate;
- low-priority research expansion with no near-term leverage;
- extra reports/dashboards already covered by current tooling.

### WAITING_GATE

A legitimate future task whose prerequisite is still changing. Do not start it early merely to fill capacity.

## Strategic accelerator lane — reverse engineering / emulator / simulation

The project must not confuse “not the current product UI” with “low value”.

Reverse engineering, emulator work and simulation can be among the highest-leverage project accelerators because they can replace repeated manual experiments with deterministic, reusable evidence.

Examples worth active attention when scopes are independent:
- WinKawaks/emulator state adapters and safe read-only bridges;
- game-logic reverse engineering that identifies stable state fields, lifecycle, geometry, camera/projection, attack dispatch or timing semantics;
- Browser-vs-emulator differential tooling;
- deterministic mock/synthetic CDP topology;
- trace/corpus record-and-replay;
- long-duration 10-room endurance simulation;
- automatic candidate mining/ordered-sequence analysis;
- synthetic failure injection for reload/disconnect/Worker replacement/session isolation;
- tooling that turns one real capture into many offline regression/prospective test cases.

These accelerator lanes deserve spare concurrency even when they are not the direct release blocker, provided they satisfy the durability/non-conflict rule above.

### Accelerator value test

Before assigning an accelerator task, PM asks:

1. **Leverage:** will one unit of work save many future manual/research/QA hours?
2. **Reuse:** will multiple later stages consume the result?
3. **Owner reduction:** can it replace or shorten real Browser/WinKawaks testing?
4. **Evidence quality:** does it improve determinism, reproducibility or attribution?
5. **Durability:** will active mainline changes leave the result largely valid?
6. **Non-conflict:** can it execute without competing for the same implementation files as higher-priority blockers?

If most answers are YES, it is a legitimate P2 accelerator and should not be ignored merely because it is not the current product surface.

## Mainline definition — current

Current shortest product path:

`Discovery V2 component correctness -> repository cross-component alignment -> global regression/preflight -> Alpha Safe Transport implementation -> ONE unified real Windows/WOF proof when intrinsically required -> fresh integrated QA -> Browser Acceptance -> Alpha release decision`

Parallel evidence path:

`10-room capture readiness -> exhaustive offline/endurance simulation -> real long capture only after short proof -> automatic analysis -> automatic discovery->prospective handoff -> research-only prospective validation`

Strategic accelerator path runs alongside both when non-conflicting:

`reverse engineering / emulator adapters / deterministic simulation / corpus replay / differential tooling -> reusable evidence + faster future product work`

Tasks that do not shorten, de-risk, or multiply the effectiveness of one of these paths should normally wait.

## Anti-busywork rule

Before PM creates or offers a fresh stage, answer:

1. Which current P0/P1/immediate gate does it close, **or what durable accelerator leverage does it create**?
2. Which downstream stage becomes unblocked or materially faster if it succeeds?
3. Could an in-flight upstream change make its result stale?
4. Does it duplicate an existing lane/tool/result?
5. Does it reduce Owner work or repeated real testing?
6. If it is an accelerator, is the expected future time saved clearly larger than the cost of building it?

If answers are weak, leave the slot idle.

## Fresh-thread and dedup

All priority levels still obey:
- `ONE STAGE = ONE FRESH CHAT`;
- `parallel/PM/STAGE_DEDUP_GUARD.md`;
- atomic stage claims;
- Owner never evaluates worker summaries; PM does.

## Owner intervention

`parallel/PM/OWNER_INTERVENTION_GATE.md` remains authoritative: repository-side uncertainty must be exhausted before real Owner testing.
