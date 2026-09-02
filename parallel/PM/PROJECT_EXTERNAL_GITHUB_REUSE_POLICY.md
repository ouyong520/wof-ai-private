# Project-wide External GitHub Reuse Policy

Updated: 2026-09-02
Status: **AUTHORITATIVE — default preflight for genuinely new functional modules across project lanes unless a later Owner directive explicitly overrides it**

## Owner standing preference

Before starting a genuinely new functional module, PM/worker must first search GitHub and the relevant open-source ecosystem for mature reusable projects, libraries, frameworks, tools, components or proven implementation patterns.

Owner does not need to repeat this preference in later turns.

Default optimization order:

`DIRECT_USE -> ADAPT/WRAP -> NARROW_FORK -> REUSE_COMPONENT/PATTERN -> CUSTOM_IMPLEMENT_REMAINDER`

Do not custom-build commodity infrastructure merely because writing it from scratch is possible.

## Mandatory external-reuse preflight

For every serious candidate, evaluate at minimum:

1. current maintenance/activity and release recency;
2. deployment/install complexity, with Windows/local-first constraints where relevant;
3. license compatibility;
4. exact functions that can be reused and expected development-time savings;
5. security/sandbox/write/injection implications;
6. compatibility with current repository authority, provenance, identity and fail-closed contracts;
7. dependency/update risk and upstream stability;
8. whether direct dependency, adapter, narrow fork, component reuse or rejection is best.

The resulting design decision must explicitly classify each accepted candidate as one of:

- `DIRECT_USE`
- `ADAPT/WRAP`
- `NARROW_FORK`
- `REUSE_COMPONENT/PATTERN`
- `CUSTOM_IMPLEMENT_REMAINDER`

## Reuse-first rule

Prefer mature open-source implementations for commodity capabilities such as:

- scheduling/orchestration;
- process/system telemetry;
- local databases/query engines;
- dataframe/analytics engines;
- serialization/compression;
- CLI/config/schema infrastructure;
- retry/state-machine plumbing;
- dashboards/observability;
- storage/filesystem helpers;
- generic test/fixture tooling.

Keep custom code focused on project-specific contracts, domain authority, provenance, safety boundaries and integration glue.

## Do not blindly import authority

Popularity or maturity does not make third-party output authoritative for this project.

External components must not silently weaken existing contracts such as:

- canonical dedup v2 ownership;
- exact task/result/source/runtime/candidate identity binding;
- source/provenance namespace separation;
- immutable evidence/hash authority;
- fail-closed semantics;
- read-only or no-input/no-write safety boundaries;
- release/proof/test authority;
- Training Farm deterministic/action/state contracts;
- Collector V3/V4/V5/V6 authority;
- Alpha production/release authority.

Project-specific authority remains owned by this repository even when commodity infrastructure is delegated to an external dependency.

## Fork policy

Prefer dependency/wrapper over fork.

Fork only when:

- upstream architecture is a strong fit;
- required behavior cannot be expressed cleanly through public extension/adaptation points;
- maintaining the divergence is materially cheaper than custom implementation.

For any fork, record:

- upstream repository;
- exact upstream tag/commit;
- license;
- local changes/divergence;
- upstream update strategy;
- security/authority implications.

Do not fork large frameworks just to change configuration, naming or one narrow policy surface.

## Security / capability restriction

If an external project exposes capabilities broader than this project's allowed boundary (for example memory writes, code injection, gameplay input injection, destructive deletion or network mutation), use it only behind a project-owned adapter that exposes the permitted subset.

Do not make dangerous/irrelevant APIs available to the normal application path merely because the dependency provides them.

## MVP rule

For each new module, PM should prefer the smallest reuse-first MVP that proves integration before expanding scope.

A good MVP normally:

1. keeps current project authority unchanged;
2. replaces one commodity subsystem with a mature external component;
3. proves Windows/local deployment where relevant;
4. exercises one end-to-end happy path plus fail-closed boundary;
5. records exact dependency/version/license;
6. leaves a clean escape path if the external component later proves unsuitable.

## Current project examples

Examples currently worth evaluating before custom work include:

- `giampaolo/psutil` — process/system/disk telemetry;
- `pola-rs/polars` — streaming/lazy analytics;
- `duckdb/duckdb` — embedded SQL/query over local datasets;
- `agronholm/apscheduler` — lightweight local scheduling;
- `PrefectHQ/prefect` — durable workflow orchestration/retry/state/history;
- `srounet/Pymem` — Windows process-memory access only behind a strict read-only adapter if ever used.

This list is not permanent approval. Re-check maintenance, license and fit before each material adoption.

## Lane-specific policies still apply

This project-wide policy does not replace stricter lane rules.

For Collector, also obey:

`parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`

and all Collector routing/source-boundary/read-only rules.

Alpha, Training Farm and other lanes must preserve their own canonical authority, safety and non-regression contracts.

## Stop / dedup interaction

External-reuse preflight does not authorize duplicate implementation.

Workers must still run the current canonical dedup/current-state checks first. If the same/equivalent task is already ACTIVE, COMPLETE or superseded, stop with duplicate/already-complete/superseded disposition instead of starting a new external integration task.
