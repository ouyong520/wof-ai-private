# Global GitHub Reuse-First Policy

Updated: 2026-09-03
Status: **AUTHORITATIVE — applies repository-wide to every PM, orchestrator and implementation worker**

## Purpose

Before designing or implementing a non-trivial capability, dependency, infrastructure component, adapter, workflow, algorithmic subsystem, tool, UI/runtime integration, storage/query layer, automation layer, or similar engineering surface, first determine whether maintained GitHub/open-source code can be used directly or adapted safely.

The goal is not maximum reuse for its own sake. The goal is minimum total project cost:

- less duplicate code;
- less implementation time;
- fewer dependencies and services;
- simpler deployment;
- lower long-term maintenance burden;
- less Owner manual work;
- faster path to a usable product.

This policy does not authorize copying code with incompatible licensing, bypassing project safety/source authority, or adding a large framework merely because it exists.

## Mandatory order of operations

For any new non-trivial engineering capability, use this order before committing to a self-built architecture:

```text
READ CURRENT GIT / DURABLE AUTHORITY
-> DEDUP PREFLIGHT
-> GITHUB / OFFICIAL-ECOSYSTEM REUSE PREFLIGHT
-> COMPARE CANDIDATES
-> CHOOSE DIRECT_USE / ADAPT / FORK / REFERENCE_ONLY / SELF_BUILD / DEFER
-> DEFINE THE SMALLEST MVP
-> IMPLEMENT
```

If the same capability already has a recent durable external-reuse decision and the candidate landscape has not materially changed, reuse that decision rather than repeating research for confidence.

A trivial typo, tiny local bug fix, metadata-only closeout, or change that clearly cannot benefit from external code does not require ceremonial broad research. The rule targets actual engineering design/reimplementation decisions.

## Required candidate questions

When a meaningful external candidate exists, PM must answer all of the following before deciding the implementation route.

### 1. Is the project still maintained?

Check evidence such as:

- recent commits;
- recent releases/tags;
- maintainer activity;
- issue/PR activity;
- CI health where visible;
- archived/deprecated status;
- obviously stale dependencies;
- long-unresolved core defects.

Stars/forks alone are not maintenance evidence.

### 2. How difficult is deployment and integration?

Assess at least:

- target-OS compatibility;
- install steps;
- native compilation requirements;
- Docker/container requirements;
- external services such as Redis/PostgreSQL/Kafka/Kubernetes;
- runtime dependency size;
- configuration burden;
- whether it embeds cleanly into the existing process/repository;
- Owner/manual setup burden;
- upgrade and operational maintenance cost.

Prefer the smallest reliable dependency surface that solves the real requirement.

### 3. Which functions can be reused directly?

Evaluate at feature/module level rather than only whole-project level. Examples include:

- transport/protocol clients;
- parsers/serializers;
- browser/runtime discovery;
- schedulers;
- storage/query engines;
- state machines;
- algorithms;
- CLI/UI components;
- file/manifest handling;
- caching;
- monitoring;
- fixtures/test harnesses;
- interoperability contracts.

Record what should be DIRECT_USE, adapted, reference-only, or rejected.

### 4. Which candidate is best for secondary development?

If multiple candidates are plausible, compare:

- maintenance activity;
- license;
- code quality/architecture clarity;
- API stability;
- dependency complexity;
- target-platform fit;
- test coverage;
- ease of trimming/embedding;
- compatibility with the current language/runtime;
- upstream upgrade path;
- fork burden and long-term maintenance risk.

PM must identify a primary recommendation rather than returning an unranked list to the Owner.

### 5. Make an explicit implementation decision

Use one of these durable classifications:

- `DIRECT_USE` — consume the maintained project/package substantially as-is;
- `ADAPT` — reuse maintained code/API with a thin project-owned adapter or glue layer;
- `FORK` — maintain a project fork because upstream cannot satisfy a required bounded change;
- `REFERENCE_ONLY` — learn from the design/algorithm but do not import the project as a maintained dependency;
- `SELF_BUILD` — local implementation has the lowest total lifecycle cost or external candidates fail requirements;
- `DEFER` — useful candidate exists but the current stage does not need it.

Do not leave the technical choice to Owner unless the remaining decision is genuinely strategic/product-level rather than an engineering judgment.

Default preference when requirements are otherwise satisfied:

```text
DIRECT_USE
-> ADAPT
-> REFERENCE_ONLY + small local implementation
-> FORK
-> SELF_BUILD
```

This is a preference, not a mandate. A small self-contained implementation may be cheaper than importing a heavyweight framework and its operational stack.

### 6. Define the simplest MVP

For the selected approach, state the smallest usable path:

- exact external project/package/module reused;
- exact thin glue code that remains project-owned;
- minimum dependencies/services;
- what is intentionally deferred;
- simplest focused validation;
- what capability the MVP proves;
- what may be expanded only after MVP success.

MVP objective:

**minimum code + minimum dependencies + minimum deployment burden + minimum Owner work + fastest safe path to usable product value.**

## License and supply-chain gate

Before importing/forking external code, inspect:

- license and commercial/private-use compatibility;
- modification/distribution/attribution obligations;
- copyleft implications;
- dependency licenses where material;
- known security/supply-chain concerns;
- whether pinning/version verification is needed.

Prefer maintained, narrowly scoped dependencies with permissive licensing when technically equivalent.

External reuse never overrides repository safety, privacy, source/runtime provenance, exact identity, proof, or fail-closed requirements.

## Required PM output for meaningful reuse research

When the Owner asks for open-source research, or when reuse materially changes the implementation plan, PM should provide a concise comparison containing at least:

| Candidate | Maintenance | Deployment complexity | Reusable functions | Adaptation cost | License | Recommendation |
|---|---|---|---|---|---|---|

Then provide exactly one primary engineering decision and the simplest MVP.

Example conclusion shape:

```text
Recommended candidate: <project>
Decision: DIRECT_USE / ADAPT / FORK / REFERENCE_ONLY / SELF_BUILD / DEFER
Why: <short engineering rationale>
MVP: <existing component> -> <thin adapter/glue> -> <current system> -> <focused validation>
```

## Relationship to dedup and current Git authority

GitHub reuse research happens **after** reading the project's current durable Git state and dedup authority.

Do not search for a replacement architecture when the same logical task is already legitimately ACTIVE/claimed unless the active START_PROMPT explicitly requires external-reuse research or a concrete blocker makes the existing approach invalid.

Do not use an external project as an excuse to bypass an existing canonical claim, revive superseded work, rewrite a COMPLETE module, or create a parallel product/control plane.

## Worker responsibility

When a START_PROMPT assigns a non-trivial capability and no current durable reuse decision exists, the implementation worker must perform the bounded reuse preflight before committing to substantial self-built infrastructure.

Workers should not perform broad repetitive research after PM has already recorded a current authoritative dependency/reuse decision. Reuse the decision unless real evidence shows it is stale or unsuitable.

## PM responsibility

PM owns the final judgment of whether to use, adapt, fork, reference, self-build, or defer. Owner should not be asked to choose between technical libraries merely because multiple search results exist.

The success metric is not how much third-party code was imported. The success metric is whether the project reaches a reliable usable product with the lowest reasonable total development, deployment and maintenance cost.
