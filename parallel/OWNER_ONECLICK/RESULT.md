# Owner One-Click Dynamic Refresh V2 — Result

Date: 2026-09-01  
Stage: `OWNER_ONECLICK_DYNAMIC_REFRESH_V2`

## Verdict

**OWNER ONECLICK DYNAMIC REFRESH V2 READY — CURRENT SNAPSHOT + UTF-8 PACKAGE VERIFIED**

Owner action: `NO`

The Owner One-Click package has been refreshed from one explicit immutable repository snapshot, its complete consumed runtime set is hash-pinned from that same snapshot, stale/mutated payloads fail closed with Chinese-first diagnostics, and the existing manifest-driven Linux + Windows package workflow passed without any workflow edit.

## Immutable package snapshot

- package version: `2026.09.01.947c3c5433a1`
- source commit: `947c3c5433a1fe5bf88845c6d1f529e40b82510f`
- deterministic generated-at: `2026-09-01T15:26:37Z` (derived from source commit time)
- selection policy: `owner-oneclick-runtime-v2`
- generator: `parallel/OWNER_ONECLICK/refresh_manifest.py`
- manifest payload count: `46`
- immutable raw base URL is pinned to the same 40-character source commit
- PYLAUNCH, WOF052L Recorder, Browser Fleet, Unified Live Proof, OPTOOLKIT, fixed Alpha assets, and owner entry files are all represented by exact Git blob SHA-1 values from that snapshot
- component provenance uses the same `sourceCommit` for PYLAUNCH, Recorder, Browser Fleet, and Unified Live Proof; no mixed-generation component pin remains

The refreshed PYLAUNCH set includes the current snapshot blobs for:

- `browser.py` -> `e883030fe8a90333b8ed58aae5699118b2c876fe`
- `cdp.py` -> `def308bed2a5609be1da26505a15d621395b66aa`
- `discovery_v2.py` -> `ec9d27bfe26557a11187a23853893b898a3366d1`
- `monitor.py` -> `4430f7e927265cd3366fd70ce560c375aa878993`
- `probe.py` -> `789a6849b826b35542b22d56a4d2ca3628d285a1`

The V2 selector also closes the V1 omission class by packaging all selected non-test runtime files under Recorder and Browser Fleet, including Recorder discovery/hardening/identity/worker modules and `parallel/BROWSER_FLEET/fleet_discovery_v2.py`. Unified Live Proof is pinned in the same snapshot, including current `unified_live_proof.py` blob `0d9010007910f58b77c64fde98264697191bb679`.

## Deterministic refresh / anti-stale behavior

Added `parallel/OWNER_ONECLICK/refresh_manifest.py`.

It:

1. resolves an explicit git ref to a full immutable commit;
2. enumerates the package runtime selection from that commit instead of copying prior manifest hashes;
3. preserves UTF-8 git paths with `git -c core.quotepath=false ls-tree ...`;
4. derives package version and generated-at metadata from the immutable source commit;
5. records exact Git blob SHA-1 for every selected file;
6. detects a newly added selected runtime file that the manifest does not express;
7. detects removed selected runtime files still present in the manifest;
8. rejects worktree payload drift against the pinned hashes;
9. provides `--check` for deterministic manifest/provenance validation.

A stale or deliberately mutated blob is rejected with a Chinese-first diagnostic of the form:

`文件完整性校验失败：<path> expected=<pinned-hash> actual=<actual-hash>`

The bootstrap propagates this as the first owner-visible failure and uses a dedicated non-zero integrity exit path instead of replacing the known-good release.

## Windows UTF-8 / owner-path hardening

`parallel/OWNER_ONECLICK/bootstrap_v2.ps1` now explicitly establishes UTF-8 for redirected/non-interactive Windows execution:

- `[Console]::OutputEncoding`
- `[Console]::InputEncoding`
- `$OutputEncoding`
- `PYTHONUTF8=1`
- `PYTHONIOENCODING=utf-8`

The existing atomic release staging/current-pointer/last-known-good contract remains intact. Chinese install paths and paths containing spaces remain supported.

## Regression evidence

The existing `.github/workflows/owner-oneclick-package.yml` was not modified by this stage.

Push workflow run `33526502448` (`Owner One-Click Package`, run 71) completed successfully:

### `integrity` — PASS

- deterministic manifest / immutable source validation
- complete current runtime set cannot outgrow the package
- every manifest blob matches the pinned source commit
- current runtime bytes match the package snapshot
- mutated stale blob fails closed with Chinese path/hash diagnostic
- Discovery V2 / Chinese proof content checks
- atomic update / rollback / LKG contracts
- explicit redirected UTF-8 contract
- workflow metadata remains manifest-driven

### `windows-oneclick` — PASS

- real Chinese CMD install path
- manifest-selected package verification
- Chinese + space path handling
- installed Chinese Windows proof execution-path smoke
- update from a synthetic previous package while retaining last-known-good
- repeated updater run without changing the immutable current release

An earlier run correctly exposed a generator defect where default git path quoting escaped `WOF_一键工具.cmd`; V2 was not declared ready. The generator was corrected to disable git quote-path escaping, and the full workflow then passed.

## Final HEAD freshness reassessment

Immediately before result finalization, default branch was re-read at:

`d59b438edee3142cf373709db1ea4f1e8aa437c7`

Although default branch had advanced beyond the package source through parallel QA/PM work, the package-consumed runtime blobs were re-read and still matched the `947c3c...` manifest snapshot across:

- PYLAUNCH selected runtime files;
- WOF052L Recorder selected runtime files;
- Browser Fleet selected runtime files;
- Unified Live Proof selected runtime files;
- root Owner CMD entries;
- OPTOOLKIT owner/toolkit entries;
- fixed Alpha regression/runtime assets;
- ALPHAQA bootstrap retest asset.

Therefore no package-consumed upstream drift existed at this gate, and refreshing merely to a metadata-only HEAD would create a new version without changing package payload. The immutable `947c3c...` package remains the correct current payload snapshot.

## Delivery reassessment

### Stale-pin risk

The prior hand-maintained stale-pin failure mode is closed for this package generation: the manifest is a deterministic derivation of an explicit immutable snapshot and the regression fails closed when current selected runtime content outgrows or differs from the package.

Normal future upstream changes to a package-consumed runtime file are expected to make the package regression fail until a new manifest is generated. The current workflow validates but does not commit a refreshed manifest automatically. Therefore a refresh action is still expected after normal consumed upstream changes, but it is now:

`python parallel/OWNER_ONECLICK/refresh_manifest.py --source <explicit-immutable-commit>`

followed by committing the generated manifest — **not** manual hash editing.

### Remaining upstream gates before Owner testing

This package stage does **not** unlock a real Browser/WOF run by itself.

1. Fresh `PYLAUNCH_IDENTITY_CACHE_GENERATION_QA_V1` is currently `BLOCKED`: startup `/json/version` metadata attestation is not fully fail-closed; QA reproduced acceptance of missing Browser metadata / non-browser websocket endpoint shape. That is an upstream `parallel/PYLAUNCH/**` ownership issue and is outside this stage's allowed writes.
2. Unified Live Proof Recorder authority-heartbeat implementation is READY and its fixed `unified_live_proof.py` blob is already the one pinned by this package, but its implementation result explicitly requires a fresh independent Unified Live Proof freshness QA before preflight may permit a bounded real Browser/WOF run.

Accordingly Owner action remains `NO`.

## Safety / ownership

No workflow file, upstream runtime file, Browser/WOF state, gameplay input path, Worker replacement path, or RAM write path was modified by this stage. Stage writes were limited to `parallel/OWNER_ONECLICK/**` plus the mandatory PM claim file.

Safety remains:

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false
}
```

## Stop condition

> **OWNER ONECLICK DYNAMIC REFRESH V2 READY — CURRENT SNAPSHOT + UTF-8 PACKAGE VERIFIED**

`你现在需要操作：NO`
