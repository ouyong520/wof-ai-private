# Collector External GitHub Reuse Policy

Updated: 2026-09-02
Status: **AUTHORITATIVE — mandatory preflight for new Collector modules unless a later Owner directive explicitly overrides it**

## Owner standing preference

Before starting a genuinely new Collector functional module, PM/worker must first search GitHub and the relevant open-source ecosystem for mature reusable projects, libraries or components.

Owner does not need to repeat this preference in later turns.

Default optimization order:

`use directly -> wrap/adapt -> fork with narrow changes -> reuse proven component/pattern -> custom-build only the project-specific remainder`

Do not build a large custom subsystem merely because implementation from scratch is possible.

## Mandatory preflight

For a new module, evaluate serious external candidates on at least:

1. maintenance/activity and release recency;
2. deployment/installation complexity, especially Windows/local-first use;
3. license compatibility;
4. exact reusable functions and expected code/time savings;
5. security/read-only implications;
6. whether the project preserves Collector provenance, identity and fail-closed boundaries;
7. whether direct dependency, adapter, narrow fork, component reuse or rejection is best.

The PM recommendation must explicitly say one of:

- `DIRECT_USE`
- `ADAPT/WRAP`
- `NARROW_FORK`
- `REUSE_COMPONENT/PATTERN`
- `CUSTOM_IMPLEMENT_REMAINDER`

## Collector-specific boundaries

External code must never become authority merely because it is mature or popular.

Collector-specific authority remains local for:

- source namespace separation;
- taskId/taskBlobSha/captureId/sessionId/runtime identity binding;
- V3 COMPLETE/PARTIAL/FAILED authority;
- V4 immutable dataset identity/lifecycle;
- V5 archive/prune sole-copy safety;
- readOnly=true / writesGameMemory=false / inputInjection=false;
- no Browser/WinKawaks/Training-Farm provenance mixing.

A third-party library that exposes write/injection APIs may be used only behind a Collector-owned read-only adapter that does not expose or call those capabilities.

## Fork policy

Prefer dependency/wrapper over fork. Fork only when the upstream architecture is a strong fit and required Collector behavior cannot be cleanly wrapped.

If forked, record:

- upstream repository;
- exact upstream tag/commit;
- license;
- local divergence;
- update strategy.

Do not fork large frameworks just to change configuration or naming.

## MVP rule

For each new module, PM should provide the smallest reuse-first MVP that proves the integration before expanding scope.

The MVP should normally preserve existing Collector authority and replace only commodity infrastructure with mature open-source components.

## Current preferred candidate classes

As of 2026-09-02, examples worth evaluating before custom work include:

- `srounet/Pymem` — Windows process-memory access; use only through a read-only adapter if selected;
- `giampaolo/psutil` — process enumeration/identity/system/disk telemetry;
- `pola-rs/polars` — streaming/lazy dataframe analysis for large derived datasets;
- `duckdb/duckdb` — embedded SQL/query over derived/catalog/exported data;
- `agronholm/apscheduler` — lightweight local scheduling;
- `PrefectHQ/prefect` — durable workflow state/retry/orchestration if V7 automation outgrows a lightweight scheduler.

This list is not permanent approval. Re-check current maintenance, license and fit before each material adoption.
