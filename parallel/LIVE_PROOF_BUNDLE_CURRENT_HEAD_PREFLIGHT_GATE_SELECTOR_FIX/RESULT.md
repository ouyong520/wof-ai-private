# Unified Live Proof — Current-HEAD Preflight Gate Selector Fix Result

Stage: `UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_GATE_SELECTOR_FIX_V1`

## Verdict

**COMPLETE — UNIFIED CURRENT-HEAD PREFLIGHT GATE SELECTOR FIX — READY FOR FRESH INDEPENDENT QA**

Owner action: **NO**.

This was a narrow repository-preflight implementation fix only. Recorder, PYLAUNCH, Alpha, Browser Fleet, Browser/WOF, Owner OneClick, and Safe Transport implementation were not modified.

## HEAD / claim

- exact stage start HEAD: `b4e1981d36f86d320b396edd9b33997bc84f4827`
- atomic claim commit: `852aba75a495006624a24bed2ccb2aaf4a8f0e72`
- final implementation HEAD before result-only artifacts: `a663dd466a7c029e904f0eb6b347d14c9d93e7bc`
- machine result commit: `c9f0ec9a51c6ae5b1ba621012983f7eaa47cd746`

Concurrent drift between start and implementation closure included an unrelated Alpha target-head-label fresh-QA prompt only. The preflight implementation paths were not overwritten by that concurrent lane.

## Precise selector correction

The historical durable blockers remain untouched as historical evidence:

- `parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.json`

They are no longer treated as current authoritative release gates.

### PYLAUNCH current successor

Current preflight now consumes:

- `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.md`
- `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.json`
- `parallel/PM/STAGE_CLAIMS/PYLAUNCH_STARTUP_ATTESTATION_QA_V1.json`

Required decision:

`PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED`

The selector does not trust `state=COMPLETE` alone. It requires the machine result schema/stage/PASS decision and claim COMPLETE+PASS semantics, then recomputes Git blob SHA-1 for the current production files and requires exact equality with the successor QA pins:

- `parallel/PYLAUNCH/wof_launcher/browser.py` -> `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332`
- `parallel/PYLAUNCH/wof_launcher/monitor.py` -> `8e3c5c527fdd5a845bbfc135f55014de22078cf4`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` -> `ec9d27bfe26557a11187a23853893b898a3366d1`

These pins were re-read from current `main` and still match the Startup Attestation fresh QA evidence.

### Recorder / Unified current successor

Current preflight now consumes:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.json`
- `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1.json`

Required decision:

`PASS — RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA — READY FOR CURRENT-HEAD UNIFIED PREFLIGHT`

The selector requires machine PASS + safety semantics, claim COMPLETE+PASS semantics, and exact current production blob equality:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py` -> `8df637d370d187660592fe8de0f1c73ff3057804`

This is the same current blob accepted by the Recorder in-flight atomicity fresh QA.

## Fail-closed behavior preserved

The correction does not turn successor existence into unconditional admission. Repository preflight still blocks on:

- missing successor result/claim;
- malformed successor machine JSON;
- successor BLOCKED/non-PASS semantics;
- `COMPLETE` claim without the required PASS/READY decision;
- stale/mismatched current production blob versus successor pin;
- stale or future snapshot;
- mixed component commits;
- missing required files/tests;
- failed offline regression command;
- unsupported/old Discovery capability;
- owner UX language failure;
- safety declaration mismatch;
- existing freshness-fix safety/status mismatch.

`parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py` was not changed. Its guarded rule remains exact: a BLOCKED preflight returns before invoking the live Browser/WOF stage.

Preserved output/safety invariants:

- Chinese-first repository blocker summary;
- `ownerActionRequired=false`;
- `longCaptureAutoStarted=false`;
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- `windowWorkerReplacement=false`.

## Changed preflight blobs

- `parallel/LIVE_PROOF_BUNDLE/unified_preflight.py` -> `c756b3da7a8a0c092efe20f2587e131d497f5f72`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_preflight.py` -> `c59edb55e3d99da219bb78d8dffc427cfd2fbb75`
- `parallel/LIVE_PROOF_BUNDLE/UNIFIED_PREFLIGHT_STATUS.json` -> `6dc53eee9bc235d43b466ff83ff0aec2b6bfafe1`
- unchanged `parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py` -> `1a73d02f8171dbbd50cabff52a83c989541de2f7`

`UNIFIED_PREFLIGHT_STATUS.json` is explicitly marked as a repository selector-policy example. Runtime admission still writes a fresh status from a fresh snapshot and fresh regression execution; the static example is not an authority substitute.

## Focused deterministic regression

The connected execution container had no network/private checkout access. Per repository convention, the three current committed preflight files were reconstructed source-exact and their local Git blob hashes were verified equal to the committed GitHub blobs before execution:

- `unified_preflight.py` local reconstructed blob -> `c756b3da7a8a0c092efe20f2587e131d497f5f72`
- `test_unified_preflight.py` local reconstructed blob -> `c59edb55e3d99da219bb78d8dffc427cfd2fbb75`
- `unified_preflight_entrypoint.py` local reconstructed blob -> `1a73d02f8171dbbd50cabff52a83c989541de2f7`

Executed:

```text
python -m unittest -v test_unified_preflight.py
Ran 22 tests
OK
```

Result: **22 PASS / 0 FAIL**.

The suite retains the original 13 adversarial preflight behaviors and adds explicit attacks for:

- historical ParentFrame BLOCKED evidence + current Startup Attestation successor PASS -> no false historical block;
- Startup Attestation successor missing -> BLOCKED;
- Startup Attestation machine result BLOCKED while claim is COMPLETE -> BLOCKED;
- Startup Attestation current production blob drift -> BLOCKED;
- historical Unified freshness BLOCKED evidence + current Recorder successor PASS -> no false historical block;
- Recorder successor missing -> BLOCKED;
- Recorder machine result BLOCKED while claim is COMPLETE -> BLOCKED;
- Recorder current `unified_live_proof.py` blob drift -> BLOCKED;
- malformed successor machine JSON -> BLOCKED;
- claim COMPLETE without required PASS semantics -> BLOCKED;
- PASS may invoke the guarded live runner in test only;
- BLOCKED never invokes it.

This is implementation-side deterministic regression, not fresh independent QA and not Browser/WOF proof.

## Scope / downstream

No Alpha target-label, Owner OneClick, or 5h endurance gate was added to Unified preflight. This fix only replaces the stale selectors identified by the fresh QA.

A fresh independent Current-HEAD preflight QA should now re-run against these settled preflight blobs. Browser/WOF live proof remains guarded behind runtime PASS and was not launched by this stage.

## Stop condition

**COMPLETE — UNIFIED CURRENT-HEAD PREFLIGHT GATE SELECTOR FIX — READY FOR FRESH INDEPENDENT QA**
