# Owner One-Click Dynamic Refresh V1 — BLOCKER

Stage: `OWNER_ONECLICK_DYNAMIC_REFRESH_V1`

Status: **BLOCKED — workflow ownership change required**

## Exact blocker

The current Owner One-Click workflow hard-codes the previous immutable package metadata instead of reading the package manifest dynamically:

- package version: `2026.09.01.5`
- PYLAUNCH source commit: `7b10867f14f59ca9ab95c0fa6d30530008409371`
- multiple exact historical PYLAUNCH blob SHAs
- release paths containing `2026.09.01.5`

Current upstream HEAD has already moved beyond those blobs. For example, at inspected HEAD `433f103026a6ad2de1656fe9053ceb9d1b991255`:

- `parallel/PYLAUNCH/wof_launcher/browser.py` = `e883030fe8a90333b8ed58aae5699118b2c876fe`
- `parallel/PYLAUNCH/wof_launcher/cdp.py` = `def308bed2a5609be1da26505a15d621395b66aa`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` = `68ada457ba653bba63ec0308f812f1b6b84f3bd6`
- `parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd` = `fdae80a1af13ab02154330deb3238ed6af1b867a`
- `parallel/WOF052L_RECORDER/owner_zh_cn.py` = `0e0001b1b9e9ea1239450b1c2a14544ced580c1a`
- `parallel/BROWSER_FLEET/fleet_manager.py` = `0a76597bc4788c5aec820510cbf2a909769591b5`
- `parallel/BROWSER_FLEET/fleet_owner_zh_cn.py` = `7ddefc8d3a624e52b07eae11dc1534523662839a`

There are also new runtime dependencies that the old frozen package manifest cannot represent correctly without a package refresh, including `parallel/BROWSER_FLEET/fleet_discovery_v2.py` and Recorder hardening/discovery modules imported by the current owner entry.

## Why this lane must stop

`parallel/PM/OWNER_ONECLICK_DYNAMIC_REFRESH_START_PROMPT.md` explicitly limits writes to `parallel/OWNER_ONECLICK/**` plus the mandatory claim file and says:

> If a workflow change is absolutely required, stop and report the exact required change rather than silently expanding scope.

A refreshed manifest/package cannot be activated safely while `.github/workflows/owner-oneclick-package.yml` still asserts the old version, old source commit, old blob hashes, and old release directory names. Any correct refresh would make that Windows job fail by construction.

## Exact required different-ownership fix

Open a fresh workflow-owned stage that changes `.github/workflows/owner-oneclick-package.yml` so package validation derives its expected values from `parallel/OWNER_ONECLICK/package_manifest.json` (or from a deterministic generated manifest artifact) instead of hard-coded package metadata. At minimum it must:

1. read `packageVersion`, `sourceCommit`, and file `gitBlobSha` values from the manifest;
2. use the manifest package version when constructing release paths and upgrade/re-run assertions;
3. validate installed blobs against manifest entries rather than historical literal SHAs;
4. keep fail-closed integrity behavior — a stale or mismatched manifest/blob must still fail CI;
5. preserve the current Windows Chinese-path/spaces coverage and safety assertions (`readOnly=true`, `ramWrites=0`, `inputInjection=false`);
6. after that workflow lane lands, rerun this dynamic-refresh stage with a new stageId to implement/activate deterministic manifest refresh, stale-cache rejection diagnostics, and UTF-8 redirected-output hardening under `parallel/OWNER_ONECLICK/**`.

No Owner Windows/WOF run is needed for this blocker.

Owner action: `NO`.
