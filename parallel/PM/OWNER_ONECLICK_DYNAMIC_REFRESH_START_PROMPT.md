# WOF Owner One-Click — Dynamic Refresh / UTF-8 Hardening Start Prompt

stageId: `OWNER_ONECLICK_DYNAMIC_REFRESH_V1`

## Dedup / claim

Before doing work, follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If this stage is already claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise atomically claim this stage under `parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_DYNAMIC_REFRESH_V1.json` and continue.

## Role

You own the **Owner One-Click package refresh/hardening lane**.

This is a mainline owner-time reducer. The package must stop becoming stale every time upstream PYLAUNCH/Recorder/Proof files change.

## Read first

Re-read current HEAD including:
- `parallel/OWNER_ONECLICK/**`
- current `parallel/PYLAUNCH/**`
- current `parallel/WOF052L_RECORDER/**`
- current `parallel/LIVE_PROOF_BUNDLE/**`
- relevant workflows/tests that exercise Owner One-Click
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`

Known recent observations:
- Owner One-Click manifest can retain old PYLAUNCH blob SHAs after upstream hardening changes;
- Windows/direct Python output can encounter CP1252/Chinese Unicode problems outside the CMD codepage-protected path;
- do not solve this by editing active PYLAUNCH implementation while its own fix lane is running.

## Goal

Make Owner One-Click robust against moving upstream blobs and Windows Chinese output so the final Owner proof package can be refreshed once without repeated manual pin repair.

## Hard write boundary

Write only under:
- `parallel/OWNER_ONECLICK/**`
- package-specific tests/helpers in that directory
- mandatory PM stage claim file

Do NOT modify:
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `product/alpha/**`

If a workflow change is absolutely required, stop and report the exact required change rather than silently expanding scope.

## Required work

1. **Eliminate fragile stale-pin behavior**
   - design/implement a deterministic refresh mechanism for package manifest entries sourced from current repository HEAD or an explicitly frozen package-build commit;
   - never silently accept mismatched blobs;
   - package build must either regenerate/verify pins correctly or fail closed with a clear Chinese explanation;
   - do not weaken integrity checks just to make tests green.

2. **UTF-8 / Simplified Chinese robustness**
   - package/bootstrap path must force or safely establish UTF-8 for owner-facing JSON/status/error output;
   - cover redirected/non-interactive Windows output where possible without editing PYLAUNCH itself;
   - preserve Chinese-first UX, technical details second.

3. **Immutable package provenance**
   - final package should record source commit + resolved blob hashes;
   - stale cache/package reuse must fail closed;
   - diagnostics must explain which file/hash is stale.

4. **Regression**
   - current-head manifest refresh succeeds;
   - mutate one expected source blob => stale package rejected;
   - upstream hash changes can be refreshed deterministically rather than hand-edited;
   - Chinese path with spaces;
   - Windows-style UTF-8 output/redirected stdout simulation;
   - no change to readOnly / ramWrites=0 / inputInjection=false / no Worker replacement safety contracts.

5. **Current-HEAD final rescan**
   - before final result, re-read upstream source blobs again;
   - prove the generated/frozen package metadata matches the selected package-build commit;
   - if an upstream component changes while this stage runs, refresh against the final selected commit rather than leaving knowingly stale metadata.

## Stop conditions

Success:
`OWNER ONECLICK DYNAMIC REFRESH READY — STALE PIN + UTF-8 PACKAGE PATH HARDENED`

Or one precise blocker requiring a fresh different ownership lane.

Do not request Owner Windows/WOF testing in this stage.

Owner action: `NO`.
