# Unified Live Proof — Current-HEAD Repository Preflight Fresh QA

stageId: `UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V1`

Priority: **P1 Alpha release gate / repository-only QA**

You are the independent QA owner for the current-head Unified Live Proof repository preflight. This stage validates whether the now-fixed Recorder/PYLAUNCH/Unified stack is currently repository-admissible. It must not launch Browser/WOF and must not modify production implementation.

## Start / dedup

Before any work, re-read the latest `main` HEAD and current repository facts. Read at minimum:

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/STAGE_CLAIMS/**`
- `parallel/LIVE_PROOF_BUNDLE/PREFLIGHT_HARDENING_RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight.py`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_preflight.py`
- `parallel/LIVE_PROOF_BUNDLE/UNIFIED_PREFLIGHT_STATUS.json`
- current Unified / Recorder / PYLAUNCH / Browser Fleet result files referenced by the preflight
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.md`
- current authoritative PYLAUNCH startup/runtime-generation fresh-QA results
- current Formal Real-Adapter fresh-QA result
- recent relevant commits.

If an equivalent current-head repository preflight QA already has a durable PASS/BLOCKED result, stop. If this stage is already CLAIMED/EXECUTING/COMPLETE, stop per duplicate guard.

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V1.json`

with the exact current start HEAD.

## Goal

Re-run the hardened fail-closed repository preflight against **current `main`**, after the latest Recorder in-flight generation atomicity fresh QA PASS, and determine whether the Unified live-proof stack is repository-ready for later bounded live proof.

This is not a release-freeze audit and not Owner acceptance. Alpha V1 now also has the mandatory enemy target-head-label gate and 5h endurance/package/acceptance gates; therefore even a PASS here does not authorize release or Owner action by itself.

## Required verification

At minimum:

1. verify every preflight-consumed required result/claim is current and has the required PASS/READY semantics rather than only `state=COMPLETE`;
2. verify the current Recorder production blob still matches the blob accepted by `UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1`;
3. verify old historical Recorder heartbeat/generation/freshness blockers are superseded by current fixes + fresh QA, not mechanically reused;
4. verify current PYLAUNCH startup/runtime-generation authority gates and production blobs remain current;
5. verify Browser Fleet / Discovery capability surfaces consumed by preflight remain compatible;
6. run `test_unified_preflight.py` and all safe offline regression commands currently required by the preflight mechanism;
7. run the repository-only current preflight using its current supported entrypoint/command without allowing any Browser/WOF launch;
8. confirm malformed/stale/mixed/missing evidence still fails closed and Chinese-first blocker output remains intact;
9. confirm `readOnly=true`, `ramWrites=0`, `inputInjection=false`, Worker replacement disabled, and `longCaptureAutoStarted=false` remain enforced;
10. re-read `main` immediately before finalizing and distinguish metadata-only drift from release-consumed production drift.

If the current preflight policy still references a historical superseded claim name in a way that blocks a now-valid successor PASS, record the exact policy mismatch as a blocker. Do not rewrite unrelated acceptance/package policy in this QA stage.

## Write boundary

Write only:

- `parallel/LIVE_PROOF_BUNDLE_QA_CURRENT_HEAD_PREFLIGHT/**`
- this stage claim.

Do not modify:

- `parallel/LIVE_PROOF_BUNDLE/**` production/preflight implementation;
- PYLAUNCH;
- Alpha Transport;
- `product/alpha/**`;
- Owner OneClick;
- HUD/HUDANCHOR;
- WOF-052/WOF-052L paths.

If a production/preflight defect is found, record a precise blocker and stop; a separate fresh fix stage will own implementation.

## Result requirements

Durable result must record:

- audited start/final HEAD;
- exact production/preflight blobs tested;
- exact authoritative claims/results consumed;
- offline regression counts/results;
- repository preflight verdict and blocker details if any;
- whether any later main drift invalidates the verdict;
- safety invariants;
- `Owner action: NO`.

## Stop conditions

- `PASS — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT — REPOSITORY GATE CLOSED`
- `BLOCKED — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT — <precise blocker>`
- `ALREADY COMPLETE — SAFE TO CLOSE`
- `ALREADY CLAIMED — SAFE TO CLOSE`

Do not launch Browser/WOF. Strictly continue until one stop condition is durably recorded.
