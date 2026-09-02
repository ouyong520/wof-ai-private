# Unified Live Proof — Current-HEAD Preflight Gate Selector Fix

stageId: `UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_GATE_SELECTOR_FIX_V1`

Priority: **P1 Alpha release gate fix**

Purpose: fix the current Unified repository preflight so it consumes the authoritative successor QA/results that supersede historical BLOCKED evidence, while preserving fail-closed behavior. This is a narrow preflight-policy fix, not a Recorder/PYLAUNCH implementation change and not a Browser/WOF task.

## Start / dedup

Before work, re-read latest `main`, recent relevant commits, `parallel/PM/STAGE_DEDUP_GUARD.md`, all relevant `parallel/PM/STAGE_CLAIMS/**`, and especially:

- `parallel/LIVE_PROOF_BUNDLE_QA_CURRENT_HEAD_PREFLIGHT/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight.py`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_preflight.py`
- `parallel/LIVE_PROOF_BUNDLE/UNIFIED_PREFLIGHT_STATUS.json`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.md`
- current Recorder in-flight atomicity QA claim/result JSON
- `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.md`
- current PYLAUNCH startup-attestation claim/result and identity-cache generation fix evidence
- current Browser Fleet / Discovery result used by the preflight
- current Formal Real-Adapter fresh-QA result.

If an equivalent current-head fix already exists and is COMPLETE/PASS, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If equivalent work is CLAIMED/EXECUTING, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_GATE_SELECTOR_FIX_V1.json`

using the exact current start HEAD.

## Precise blocker to fix

Fresh independent QA found that current `unified_preflight.py` still treats historical, intentionally durable BLOCKED files as authoritative required gates:

1. `parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md`
2. `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md`
3. `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.json` through `_statuses()`

Those files must remain historical evidence and must not be rewritten to fake completion.

Current authoritative successor evidence is instead represented by the later fix + fresh-QA chains, including:

- PYLAUNCH identity-cache/runtime-generation hardening culminating in current Startup Attestation fresh QA PASS on the current production blobs;
- Recorder heartbeat/generation/in-flight atomicity hardening culminating in `RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA` PASS on current `unified_live_proof.py`.

The current preflight is safely fail-closed but false-blocks a valid current successor chain because its selector names are stale.

## Required fix

Update only the Unified repository preflight policy/status/test surface needed to select current authoritative gates.

Requirements:

1. preserve historical BLOCKED results unchanged;
2. replace stale authoritative selectors with the current successor evidence, validating both durable result/verdict and freshness/current production blobs where the successor contract provides those pins;
3. do not weaken the current fail-closed model: missing result, malformed result, BLOCKED successor, stale blob, mixed snapshot, failed regression, safety mismatch, missing required test, unsupported Discovery capability, or other current gate failure must still block;
4. do not accept a claim merely because `state=COMPLETE`; require the PASS/READY semantics needed by that gate;
5. keep Chinese-first blocker output, `ownerActionRequired=false` on repository blockers, and `longCaptureAutoStarted=false`;
6. preserve the guarded rule that a BLOCKED preflight never invokes the live Browser/WOF stage;
7. update `UNIFIED_PREFLIGHT_STATUS.json` only as a current status/example generated from the corrected policy; do not erase historical evidence elsewhere;
8. do not add Alpha target-head-label/OneClick/5h gates to this Unified preflight unless they are already explicitly part of its authoritative contract. Keep this fix scoped to the stale selectors found by QA.

## Required regressions

Add/update deterministic tests covering at least:

- historical PYLAUNCH parentFrame result remains BLOCKED + current Startup Attestation successor PASS/current blobs => no false block from historical result;
- current Startup Attestation missing/BLOCKED/stale production blob => block;
- historical Unified freshness result remains BLOCKED + current Recorder in-flight atomicity successor PASS/current Unified blob => no false block from historical result;
- current Recorder successor missing/BLOCKED/stale production blob => block;
- malformed successor machine result => block;
- all existing 13 adversarial preflight behaviors remain green;
- PASS allows guarded live-stage call in test only; BLOCKED never calls it;
- Chinese-first / ownerAction / safety / long-capture invariants remain unchanged.

Run the repository-side preflight/regression commands available to the worker. If the environment cannot execute the private checkout natively, use source-exact reconstruction only where repository conventions allow it and state that precisely; do not fabricate execution evidence.

## Write boundary

Allowed writes:

- `parallel/LIVE_PROOF_BUNDLE/unified_preflight.py`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py` only if genuinely required by the selector fix
- `parallel/LIVE_PROOF_BUNDLE/test_unified_preflight.py`
- `parallel/LIVE_PROOF_BUNDLE/UNIFIED_PREFLIGHT_STATUS.json`
- `parallel/LIVE_PROOF_BUNDLE_CURRENT_HEAD_PREFLIGHT_GATE_SELECTOR_FIX/**`
- this dedicated stage claim.

Do not modify:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- Recorder authority/generation implementation
- PYLAUNCH implementation
- Browser Fleet implementation
- Alpha product/HUD
- Owner OneClick
- Safe Transport
- historical QA result/claim files.

If the successor evidence itself is insufficient/stale, stop with the exact owning-lane blocker rather than broadening this fix.

## Stop conditions

Success:

`COMPLETE — UNIFIED CURRENT-HEAD PREFLIGHT GATE SELECTOR FIX — READY FOR FRESH INDEPENDENT QA`

Failure:

`BLOCKED — UNIFIED CURRENT-HEAD PREFLIGHT GATE SELECTOR FIX — <precise blocker>`

Duplicate:

`ALREADY COMPLETE — SAFE TO CLOSE`

or

`ALREADY CLAIMED — SAFE TO CLOSE`

Owner action: **NO**.