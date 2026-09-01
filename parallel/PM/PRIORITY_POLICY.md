# WOF PM Mainline-First Priority Policy

Updated: 2026-09-01

Status: **MANDATORY**

## Core rule

Concurrency capacity is a ceiling, not a target.

Do **not** create work merely to keep every chat busy. A task only gets a slot if it materially advances the shortest path to a trustworthy user product or removes a blocker/risk on that path.

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

Only start when it will not be invalidated by active P0/P1 changes. Examples:
- one-click packaging after component interfaces stabilize;
- acceptance automation after transport contract/runtime proof stabilizes;
- Beta validator queue tooling after Validator semantics stabilize.

### P3 — Useful but non-blocking

Do not consume a slot while P0/P1 exists. Examples:
- polish not required for current release gate;
- low-priority research expansion;
- extra reports/dashboards already covered by current tooling.

### WAITING_GATE

A legitimate future task whose prerequisite is still changing. Do not start it early just to fill capacity.

## Mainline definition — current

Current shortest product path:

`Discovery V2 component correctness -> repository cross-component alignment -> global regression/preflight -> ONE unified real Windows/WOF proof -> Alpha Safe Transport implementation -> fresh independent QA -> Browser Acceptance -> Alpha release decision`

Parallel research path:

`10-room capture readiness -> real long capture only after short proof -> automatic analysis -> automatic discovery->prospective handoff -> research-only prospective validation`

Tasks that do not shorten or de-risk one of these paths should normally wait.

## Anti-busywork rule

Before PM creates or offers a fresh stage, answer:

1. Which current P0/P1 or immediate gate does it close?
2. Which downstream stage becomes unblocked if it succeeds?
3. Could an in-flight upstream change make its result stale?
4. Does it duplicate an existing lane/tool/result?
5. Does it reduce Owner work or repeated real testing?

If answers are weak, leave the slot idle.

## Fresh-thread and dedup

All priority levels still obey:
- `ONE STAGE = ONE FRESH CHAT`;
- `parallel/PM/STAGE_DEDUP_GUARD.md`;
- atomic stage claims;
- Owner never evaluates worker summaries; PM does.

## Owner intervention

`parallel/PM/OWNER_INTERVENTION_GATE.md` remains authoritative: repository-side uncertainty must be exhausted before real Owner testing.
