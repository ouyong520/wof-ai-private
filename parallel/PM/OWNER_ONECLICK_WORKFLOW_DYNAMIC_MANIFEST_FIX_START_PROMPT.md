# WOF Owner One-Click — Workflow Dynamic Manifest Fix Start Prompt

stageId: `OWNER_ONECLICK_WORKFLOW_DYNAMIC_MANIFEST_FIX_V1`

## Dedup / claim

Before doing work, follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If this stage is already claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise atomically claim this stage under `parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_WORKFLOW_DYNAMIC_MANIFEST_FIX_V1.json` and continue.

## Role

You own the **GitHub workflow side** of Owner One-Click package dynamic manifest hardening.

This stage exists because `OWNER_ONECLICK_DYNAMIC_REFRESH_V1` correctly stopped on a different-ownership blocker: `.github/workflows/owner-oneclick-package.yml` hard-codes historical package version/source commit/blob SHAs and therefore rejects any correct current-head manifest refresh.

Read first:
- `parallel/OWNER_ONECLICK/DYNAMIC_REFRESH_BLOCKER.md`
- `parallel/OWNER_ONECLICK/**`
- `.github/workflows/owner-oneclick-package.yml`
- current `parallel/PYLAUNCH/**`
- current `parallel/WOF052L_RECORDER/**`
- current `parallel/BROWSER_FLEET/**`
- current `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`

## Hard write boundary

You may modify only:
- `.github/workflows/owner-oneclick-package.yml`
- workflow-specific tests/helpers only if they live under `parallel/OWNER_ONECLICK/**`
- mandatory PM stage claim

Do NOT modify:
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `product/alpha/**`

## Required fix

Make the workflow derive package expectations from `parallel/OWNER_ONECLICK/package_manifest.json` (or a deterministic generated manifest artifact) instead of literal historical metadata.

At minimum:
1. read `packageVersion`, `sourceCommit`, and each file `gitBlobSha` from the manifest;
2. use manifest package version when constructing release paths and upgrade/re-run assertions;
3. validate installed blobs against manifest entries rather than historical literal SHAs;
4. keep fail-closed integrity behavior — stale/mismatched manifest or blob must fail CI;
5. preserve Windows Chinese path/spaces coverage;
6. preserve safety assertions: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no Worker replacement;
7. workflow must not silently regenerate a manifest from a different commit than the selected package-build commit;
8. add regression proving a newer valid manifest does not require manual workflow edits;
9. add regression proving tampered/stale manifest or blob still fails.

## Final rescan

Before finishing, re-read current HEAD and ensure the workflow contains no hard-coded historical package version/source commit/blob SHA that would force future manual pin edits.

## Stop condition

Success:
`OWNER ONECLICK WORKFLOW DYNAMIC MANIFEST READY`

Or one precise blocker requiring another ownership lane.

No Owner Windows/WOF run.
Owner action: `NO`.
