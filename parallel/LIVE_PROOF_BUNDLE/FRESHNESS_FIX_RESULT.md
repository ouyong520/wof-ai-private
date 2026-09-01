# WOF Unified Live Proof Freshness / Child Health Fix — Result

Date: 2026-09-01
Stage: `UNIFIED_LIVE_PROOF_FRESHNESS_FIX_V1`

## Verdict

**UNIFIED LIVE PROOF FRESHNESS FIX READY — READY FOR FRESH INDEPENDENT QA**

`你现在需要操作：NO`

Fresh independent QA may now retest the stale/unknown child-success P1. This fix stage did not request or use a real Owner Windows/Browser run.

## Scope

Runtime/test changes are limited to `parallel/LIVE_PROOF_BUNDLE/**`:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_live_proof.py`
- `parallel/LIVE_PROOF_BUNDLE/FRESHNESS_FIX_STATUS.json`
- this result file

The mandatory stage claim is the only write outside that tree.

Not modified by this stage:

- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/BROWSER_FLEET/**`
- Prospective lanes
- `product/alpha/**`

## P1 fixes implemented

### 1. Process health is structurally complete and fail closed

A process-health mapping is current/healthy only when all required facts are explicitly present and well formed:

- current observation timestamp and positive observation generation;
- PYLAUNCH required/live facts plus exit code;
- Recorder required/live facts plus exit code;
- both children explicitly required and live for unified readiness.

Empty, partial, null, wrong-type, inconsistent, malformed, or stale mappings cannot authorize readiness. Existing exit blockers remain preserved.

### 2. PYLAUNCH PASS now has current authority semantics

The bundle consumes PYLAUNCH `lastUpdateUtc` without changing PYLAUNCH.

- raw `automatedResult=PASS` is retained as diagnostic/history;
- only a fresh, parseable, timezone-aware `lastUpdateUtc` can set `currentAutomatedPass=true`;
- stale, missing, malformed, or implausibly future timestamps cannot authorize PASS;
- stale positive evidence is preserved in the final JSON for diagnosis rather than discarded.

### 3. Recorder success now has bundle-local heartbeat freshness

Recorder current admission is paired with an output heartbeat/generation. The bundle reader now recognizes both newline and carriage-return output, so the existing Recorder supervisor's periodic `\r` status line advances the heartbeat without any Recorder modification.

An old admission with no current child output becomes `STALE` and cannot authorize readiness. A newer output generation restores current freshness when the child is healthy.

### 4. Owner prompt and final answer require new generations

A simple age threshold alone is not enough to catch a child that hangs immediately after writing a recent PASS. Therefore the live path now requires all current authority sources to advance before the Owner prompt:

- PYLAUNCH proof generation (`lastUpdateUtc`);
- Recorder output generation;
- bundle process-observation generation.

After the Owner answers `Y`, the same all-source generation-advance gate runs again before final PASS. Failure to advance within the bounded freshness gate becomes a sticky blocker. Thus a live-but-hung child plus stale success cannot produce `overallResult=PASS` or `tenRoomLongCaptureReady=true`, even when its process has not exited.

### 5. Existing invariants preserved

The fix keeps:

- sticky blockers;
- Recorder fatal/current-generation revocation semantics;
- unaffected positive evidence/history in blocked output;
- `longCaptureAutoStarted=false`;
- Simplified Chinese Owner UX;
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- no `window.Worker` replacement.

## Regression / adversarial validation

The modified bundle regression suite passed:

```text
Ran 34 tests
OK
```

The previous independent fail-closed adversarial fixture logic was replayed unchanged against the modified bundle source, without modifying the QA lane:

```text
Ran 9 tests
OK
```

Combined result:

```text
43 tests
PASS
```

`py_compile` also passed for the modified implementation and regression suite.

New/expanded vectors include:

1. empty process-health mapping => BLOCKED;
2. partial mapping => BLOCKED;
3. null/wrong-type fields => BLOCKED;
4. inconsistent live/exit facts => BLOCKED;
5. stale process observation => BLOCKED;
6. both PYLAUNCH and Recorder must be explicitly required;
7. stale PYLAUNCH PASS => diagnostic only, no current authority;
8. missing/malformed PYLAUNCH `lastUpdateUtc` => no authority;
9. new current PYLAUNCH generation can recover in a fresh valid state;
10. stale Recorder admission => diagnostic only, no authority;
11. new Recorder output generation restores freshness;
12. all three authority generations must advance at the Owner gates;
13. carriage-return Recorder heartbeat is observed;
14. original fatal/exit/sticky/safety/evidence/long-capture vectors remain passing.

## GitHub byte verification

The exact bytes tested locally match the GitHub blobs after write:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
  - commit: `ef7b1123279c8affec07799bb49b62dac882fc50`
  - blob: `ce2e9f970f1a9e70493eb0d06b04431ea4870aa1`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_live_proof.py`
  - commit: `a42cf32b05fdb8ddbcc34e83ea1b918ab280f201`
  - blob: `e24cf4be27927e8595aff5bce1913f28496ca13a`
- machine-readable fix status commit: `c09c5b041f1913078ecc16c0fd90430f6c54ee97`

## Next gate

A **fresh independent QA stage** should now rerun the adversarial matrix from repository HEAD. This fix stage deliberately does not self-certify that independent QA.

No Owner Browser action is required for the repository-side fix or next independent QA.

## Stop condition

**UNIFIED LIVE PROOF FRESHNESS FIX READY — READY FOR FRESH INDEPENDENT QA**

`你现在需要操作：NO`
