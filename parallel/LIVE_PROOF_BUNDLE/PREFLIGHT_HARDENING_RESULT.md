# Unified Live Proof Preflight Hardening — Result

Date: 2026-09-01  
Stage: `UNIFIED_LIVE_PROOF_PREFLIGHT_HARDENING_V1`

## Verdict

**UNIFIED LIVE PROOF PREFLIGHT HARDENING READY — OWNER NOT NEEDED FOR REPOSITORY CHECKS**

The preflight mechanism is repository-ready. This verdict does **not** claim that the current repository is eligible for a real Browser/WOF run. Current fresh independent QA still contains repository-side P1 blockers, and the new preflight intentionally blocks before Browser launch until those gates are closed.

## What changed

Only `parallel/LIVE_PROOF_BUNDLE/**` was changed for runtime/product scope, plus the mandatory PM claim file.

Added:

- `unified_preflight.py` — repository-side fail-closed gate and Chinese JSON output;
- `unified_preflight_entrypoint.py` — only calls `unified_live_proof.py` after preflight PASS;
- `test_unified_preflight.py` — 13 adversarial/mock hardening cases;
- `UNIFIED_PREFLIGHT_STATUS.json` — repository example/current-admission status.

Hardened:

- `RUN_WOF_UNIFIED_LIVE_PROOF.cmd` now resolves a 40-char `main` SHA, downloads the exact SHA, records a single-snapshot manifest, rechecks that `main` did not move during download, and routes through the guarded preflight entrypoint;
- preflight exit code 20 returns without `pause`, Y/N, click confirmation, or Browser launch;
- README documents repository gate vs real live proof separately.

## Fail-closed repository gates

Preflight blocks on:

1. missing required implementation / owner / RESULT / test files;
2. malformed or non-40-char snapshot commit;
3. stale/future snapshot resolution time;
4. mixed component commits;
5. explicit current `BLOCKED` / `SUPERSEDED` required result;
6. missing required PASS/READY marker;
7. malformed/unsafe freshness JSON status;
8. current fresh independent QA JSON not PASS;
9. old/incomplete Discovery V2 capability surfaces, including direct-gstyphoon-only PYLAUNCH logic;
10. missing Simplified-Chinese owner entrypoint content;
11. safety declaration mismatch;
12. any safe offline regression failure or 0-test result.

`UNIFIED_PREFLIGHT_STATUS.json` contains exact component, check, path, command where applicable, snapshot commit and Chinese blocker detail.

## Offline regression executed for this hardening

The exact remote-equivalent preflight source/test bytes were reconstructed locally from the committed blobs and executed:

```text
python -m unittest -v test_unified_preflight.py
Ran 13 tests
OK
```

Vectors:

1. all repository checks PASS;
2. component current result BLOCKED;
3. stale snapshot;
4. mixed component commits;
5. missing required test;
6. old direct-gstyphoon-style discovery;
7. English-only owner entry;
8. safety declaration mismatch;
9. malformed result JSON;
10. regression command failure;
11. PASS allows live-stage call;
12. FAIL never calls live-stage runner;
13. blocked output remains Chinese and `ownerActionRequired=false`.

Python compile check for the exact preflight modules/tests: **PASS**.

Committed blob verification:

- `unified_preflight.py`: `c7dc2113609ff6b3cfda4344ea7b27f43d77afa0`
- `unified_preflight_entrypoint.py`: `1a73d02f8171dbbd50cabff52a83c989541de2f7`
- `test_unified_preflight.py`: `ec087a44e4e35afee5369e480ee90b5d848e182f`
- `RUN_WOF_UNIFIED_LIVE_PROOF.cmd`: `0ede2bcc71b5c55295868b4a6eda2bef3cf0f209`
- `README.md`: `d768f4453487da7017c790a8850e366e727f2625`
- `UNIFIED_PREFLIGHT_STATUS.json`: `b846a03c942ee6ebcd4271eebf8d00ae5ae22b56`

At runtime the preflight invokes 9 safe unittest entrypoints spanning Live Proof, preflight hardening, Browser Fleet, PYLAUNCH and Recorder. A historical artifact alone cannot substitute for those current commands. Because the current repository already has required P1 blockers, no Owner Browser/WOF execution is requested to validate the blocker path.

## Current repository admission re-evaluation

Latest default-branch state was re-read after concurrent mainline changes. Current required fresh QA is not all green:

### PYLAUNCH P1

`parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md` currently reports:

`BLOCKED — PYLAUNCH PARENTFRAME AUTHORITY FRESH QA — P1-STALE-TARGETID-IDENTITY-CACHE-AUTHORITY`

This can reuse old exact World identity authority when a browser/runtime generation reuses the same target id. Repository fix + new fresh QA are required before live admission.

### Unified Proof P1

`parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md` / `RESULT.json` currently report:

`BLOCKED — UNIFIED LIVE PROOF FRESHNESS QA — P1 arbitrary Recorder stdout can refresh stale admission authority`

Generic Recorder stdout can currently renew old admission freshness. Repository fix + new fresh QA are required before live admission.

Therefore current preflight result is expected to be **BLOCKED**, Browser launch disallowed, Owner action `NO`.

## Safety

Preflight only reads files/status and runs offline tests. It does not attach to WOF or launch Browser.

Live bundle invariants remain:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `windowWorkerReplacement=false`
- no Worker replacement/wrap
- no gameplay input injection
- `longCaptureAutoStarted=false`
- no `product/alpha/**` modification

## Facts that still intrinsically require real Windows/WOF

Only after all repository P0/P1 and fresh QA gates pass can one bounded live run prove:

- installed Chrome/Edge exposes the expected real loopback CDP endpoint;
- current live WOF exposes the real page/iframe/Worker/WASM topology and exact World 921031 identity;
- read-only attachment/probing preserves actual gameplay/playability.

The repository preflight itself requires no Owner action.

## Owner action

`你现在需要操作：NO`

## Stop condition

> **UNIFIED LIVE PROOF PREFLIGHT HARDENING READY — OWNER NOT NEEDED FOR REPOSITORY CHECKS**
