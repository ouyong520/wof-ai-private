# WOF Unified Windows Live Proof — Fail-Closed Fix Result

Date: 2026-09-01
Stage: `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_V1`

## Verdict

**UNIFIED WINDOWS LIVE PROOF FAIL-CLOSED FIX READY — READY FOR FRESH INDEPENDENT QA**

Fresh independent QA may now retest the previously reported P1. No Owner Windows/Browser run was requested or used for this fix.

## Scope

Product/runtime code changed only inside `parallel/LIVE_PROOF_BUNDLE/**`:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_live_proof.py`
- this result/status evidence

The mandatory PM stage claim is the only write outside that product/runtime scope.

Not modified:

- `parallel/PYLAUNCH/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `product/alpha/**`

## Fix implemented

### 1. Final PASS is fail-closed

`build_status()` now makes PASS depend on all of the following being true at the same time:

- blocker list is empty;
- Recorder has no current fatal state;
- Fleet current Browser/page/Worker indicator checks are healthy;
- PYLAUNCH current authoritative proof is PASS and World 921031 is current PASS;
- safety invariants are current PASS;
- required PYLAUNCH/Recorder child-process health is known and the required children are still live;
- Owner playability is `CONFIRMED`.

Blockers have priority over PASS. A retained blocker can no longer coexist with `overallResult=PASS` or `tenRoomLongCaptureReady=true`.

### 2. Recorder fatal revokes admission authority

`RecorderEvidence` now separates **current authority** from **historical evidence**.

A fatal marker, including `WOF-052L 采集器没有正常完成` or `已安全拒绝采集`, now:

- advances the Recorder evidence generation;
- sets current health to `FATAL`;
- clears current `admitted` authority and its admission generation;
- preserves the prior admission in historical fields for diagnostics.

A later recovery requires a new admission marker in a newer generation. Historical admission alone never restores readiness.

### 3. Child exit after prior success fails closed

Live status now carries explicit required-process/current-health semantics:

- `healthKnown`
- `launcherRequired` / `recorderRequired`
- `launcherLive` / `recorderLive`
- child exit codes
- aggregate process `healthy`

An unexpected PYLAUNCH exit after a previous PASS and a Recorder exit after previous admission are both synthesized into blockers and make automatic readiness false immediately. Stale positive JSON/admission remains visible as history but has no readiness authority.

### 4. Owner Y/N prompt is gated by current health

The Owner playability question is reachable only through `ownerPromptEligible=true`, which requires the complete current automatic gate and no blocker.

The live loop re-checks state immediately before asking. After the Owner answers, it performs a final current-state re-check so a child or automatic lane that regresses while the Owner is answering cannot produce PASS.

### 5. Sticky blocker semantics

Once the live run has recorded a blocker, that run cannot PASS even if a component later emits a positive state. Recovery evidence is retained, but a fresh current positive state does not erase the already-recorded run blocker.

### 6. Evidence preservation

A blocked final JSON still retains unaffected Fleet/PYLAUNCH positive evidence plus Recorder historical admission/fatal evidence and exact blocker details.

### 7. Safety / UX invariants preserved

Still enforced:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `windowWorkerReplacement=false`
- no Worker replacement/wrap
- long capture is never auto-started
- normal/error owner-facing strings in the modified live-proof path default to Simplified Chinese

## Offline regression

Executed from the modified bundle source:

```text
python -m unittest -v test_unified_live_proof.py
```

Result:

```text
Ran 21 tests
OK
```

`python -m py_compile unified_live_proof.py test_unified_live_proof.py` also passed.

Git blob verification after GitHub writes:

- `unified_live_proof.py`: `b3098a586dae8a1d3070e6667c536ea011911e6b`
- `test_unified_live_proof.py`: `05b739158d4147ac5d87a16520f75be5497c6028`

These exactly match the GitHub content blob SHAs returned after the updates.

## Regression vectors covered

Fresh QA should re-run/inspect at least these exact vectors:

1. fatal-after-admission => `BLOCKED` and current Recorder admission revoked;
2. blocker + simulated Owner `Y` => still `BLOCKED`;
3. PYLAUNCH exit-after-PASS => `BLOCKED` with child-exit blocker;
4. Recorder exit-after-admission => `BLOCKED` with child-exit blocker;
5. any blocker => playability prompt unreachable;
6. fatal recovery requires a newer current positive generation;
7. recovery inside a run with a retained blocker => still `BLOCKED`;
8. unaffected Fleet/PYLAUNCH/Recorder historical positive evidence remains in blocked JSON;
9. clean current Fleet + PYLAUNCH + Recorder + live children + Owner `CONFIRMED` => `PASS`;
10. missing process-health knowledge cannot satisfy live readiness;
11. repository/CI `PASS` never substitutes live `PASS`;
12. RAM-write safety violation => not ready;
13. Worker replacement safety violation => not ready;
14. long capture remains `longCaptureAutoStarted=false` even on clean PASS.

## Commits containing the implementation

- fail-closed aggregation/current-health implementation: `e6984d1f05d9bc8a5cb86efc237c01e7151c7f39`
- expanded fail-closed regression suite: `926104f519acc05df7b1cc1e4e43c8771e9ad85e`

## Owner intervention

`你现在需要操作：NO`

This stage used only source inspection plus mock/fixture/offline tests. Fresh independent QA is the next gate; this fix stage does not claim a real Windows/Browser live PASS.

## Stop condition

**UNIFIED WINDOWS LIVE PROOF FAIL-CLOSED FIX READY — READY FOR FRESH INDEPENDENT QA**
