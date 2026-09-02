# Unified Live Proof — Current-HEAD Repository Preflight Fresh QA Result

Date: 2026-09-02  
Stage: `UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V1`

## Verdict

**BLOCKED — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT — P1 stale superseded gate selectors block current successor PASS evidence**

Owner action: **NO**.

This was repository-only fresh independent QA. No production implementation was modified, no Browser/WOF was launched, and no WOF-052/WOF-052L long capture was started.

## Audited HEAD / drift

- stage start HEAD: `fbbd2e0535edce2dd5173d63be2db9eb12e86eed`
- stage claim commit / immediate pre-result HEAD: `25f0632d6eb6e0c054c8c66dc6b1b86e07435417`
- drift classification before result write: **QA claim metadata only**

The only main movement between start and the pre-result final re-read was this stage's claim commit. No release-consumed preflight, Recorder, PYLAUNCH, or Browser Fleet production blob changed during the audit.

## Current production/preflight blobs audited

- `parallel/LIVE_PROOF_BUNDLE/unified_preflight.py` — `c7dc2113609ff6b3cfda4344ea7b27f43d77afa0`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py` — `1a73d02f8171dbbd50cabff52a83c989541de2f7`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_preflight.py` — `ec087a44e4e35afee5369e480ee90b5d848e182f`
- `parallel/LIVE_PROOF_BUNDLE/UNIFIED_PREFLIGHT_STATUS.json` — `b846a03c942ee6ebcd4271eebf8d00ae5ae22b56`
- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py` — `8df637d370d187660592fe8de0f1c73ff3057804`
- `parallel/PYLAUNCH/wof_launcher/browser.py` — `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332`
- `parallel/PYLAUNCH/wof_launcher/monitor.py` — `8e3c5c527fdd5a845bbfc135f55014de22078cf4`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` — `ec9d27bfe26557a11187a23853893b898a3366d1`

## Current authoritative successor evidence

### Recorder / Unified

Latest fresh QA is:

`parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.md` / `RESULT.json`

Verdict:

**PASS — RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA — READY FOR CURRENT-HEAD UNIFIED PREFLIGHT**

That QA accepted production blob:

`parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py` -> `8df637d370d187660592fe8de0f1c73ff3057804`

The current production blob is still exactly the same. Its fresh independent source-exact execution reported **42 PASS / 0 FAIL**, including Recorder generation, heartbeat/freshness, Unified recovery/sticky blocker, and current preflight adversarial semantics.

Therefore the old generic-stdout freshness blocker is historical and superseded by the later heartbeat -> generation -> in-flight atomicity fix/QA chain.

### PYLAUNCH

Current startup-attestation fresh QA:

`parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.md`

Verdict:

**PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED**

The current PYLAUNCH production blobs still match the blobs accepted by that QA:

- browser `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332`
- monitor `8e3c5c527fdd5a845bbfc135f55014de22078cf4`
- discovery `ec9d27bfe26557a11187a23853893b898a3366d1`

The earlier parentFrame fresh QA blocker was specifically targetId-only identity-cache authority. `parallel/PYLAUNCH/IDENTITY_CACHE_GENERATION_FIX_RESULT.md` closed that implementation defect, and the later startup-attestation fresh QA re-ran the current identity-generation regression and confirmed stale authority invalidation remains green.

### Browser Fleet / Discovery

`parallel/BROWSER_FLEET/RESULT.md` remains:

**BROWSER FLEET DISCOVERY V2 READY**

The preflight-consumed Discovery V2 capability contract remains compatible and fail-closed.

### Formal Real-Adapter

`parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_RECOVERY_V2/RESULT.md` remains:

**PASS — ALPHA FORMAL REAL-ADAPTER FRESH QA RECOVERY V2 — READY FOR NEXT RELEASE GATES**

This is not the blocker found here.

## Precise P1 blocker — stale superseded preflight gate selectors

Current `unified_preflight.py` still defines required status gates against historical files:

1. `parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md`
   - required marker: `PASS — PYLAUNCH PARENTFRAME AUTHORITY FRESH QA`
   - actual historical file remains `BLOCKED — PYLAUNCH PARENTFRAME AUTHORITY FRESH QA — P1-STALE-TARGETID-IDENTITY-CACHE-AUTHORITY`.

2. `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md`
   - required marker: `PASS — UNIFIED LIVE PROOF FRESHNESS FRESH INDEPENDENT QA`
   - actual historical file remains `BLOCKED — UNIFIED LIVE PROOF FRESHNESS QA — P1 arbitrary Recorder stdout can refresh stale admission authority`.

3. `_statuses()` also directly parses `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.json`, whose durable `result` remains `BLOCKED` against old `unified_live_proof.py` blob `ce2e9f970f1a9e70493eb0d06b04431ea4870aa1`.

The current `UNIFIED_PREFLIGHT_STATUS.json` is likewise still a historical example that lists these two old blockers.

These historical files are valid evidence of what was once broken and must not be rewritten. The defect is that **current preflight policy still treats them as the authoritative required gates after newer fixes and fresh QA have superseded those exact blockers**.

Result: current preflight is safely fail-closed, but it cannot recognize the now-valid successor PASS chain. It deterministically false-blocks repository admission on stale gate names.

This matches the start prompt's explicit blocker condition: if preflight still references a historical superseded claim/result name in a way that blocks a valid successor PASS, record the exact policy mismatch and stop. This QA does not rewrite that policy.

## Fresh preflight regression

The current exact blobs were reconstructed in an isolated source-exact harness:

- `unified_preflight.py` `c7dc2113609ff6b3cfda4344ea7b27f43d77afa0`
- `unified_preflight_entrypoint.py` `1a73d02f8171dbbd50cabff52a83c989541de2f7`
- `test_unified_preflight.py` `ec087a44e4e35afee5369e480ee90b5d848e182f`

Executed:

```text
python -m unittest -v test_unified_preflight.py
Ran 13 tests
OK
```

Result: **13 PASS / 0 FAIL**.

The suite freshly reconfirmed:

- malformed result JSON fails closed;
- stale snapshot fails closed;
- mixed component commits fail closed;
- missing required tests fail closed;
- old direct-gstyphoon discovery fails closed;
- English-only owner entry is rejected;
- safety declaration mismatch is rejected;
- regression command failure blocks;
- BLOCKED preflight never starts the live stage;
- blocker output remains Chinese-first;
- `ownerActionRequired=false`;
- `longCaptureAutoStarted=false`.

The connected execution container has no private checkout and cannot resolve GitHub directly, so after the decisive current preflight policy defect was established, this QA did not claim a native execution of all nine repository regression entrypoints. Per the write-boundary instruction, once a production/preflight defect is found, this stage records the precise blocker and stops instead of modifying implementation or broadening scope. The blocker does not depend on native checkout behavior: it is directly encoded in current `STATUS_GATES` / `_statuses()` and the referenced durable files are currently BLOCKED.

## Safety invariants

Confirmed preserved:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- Worker replacement disabled / `windowWorkerReplacement=false`
- `longCaptureAutoStarted=false`
- Browser/WOF launch: **NOT RUN**
- production implementation writes: **0**
- Owner action: **NO**

## Required next ownership

A separate fresh implementation/fix stage should update Unified preflight's required gate mapping to consume the current authoritative PYLAUNCH and Recorder/Unified successor QA chain while preserving all existing fail-closed behavior. This QA stage must not perform that fix.

## Stop condition

**BLOCKED — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT — P1 stale superseded gate selectors block current successor PASS evidence**
