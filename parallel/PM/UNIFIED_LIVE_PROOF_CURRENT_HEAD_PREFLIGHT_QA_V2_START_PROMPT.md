# Unified Live Proof — Current-HEAD Repository Preflight Fresh QA V2

stageId: `UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V2`

Priority: **P1 Alpha release gate / repository-only independent QA**

Purpose: independently verify the completed current-head preflight gate-selector fix. Confirm the Unified repository preflight now consumes the authoritative current PYLAUNCH Startup Attestation and Recorder in-flight atomicity successor evidence, no longer false-blocks on historical superseded BLOCKED files, and still preserves all fail-closed behavior.

## Start / dedup

Before work, re-read latest `main`, recent relevant commits, `parallel/PM/STAGE_DEDUP_GUARD.md`, current `parallel/PM/STAGE_CLAIMS/**`, and at minimum:

- `parallel/LIVE_PROOF_BUNDLE_CURRENT_HEAD_PREFLIGHT_GATE_SELECTOR_FIX/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight.py`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_preflight.py`
- `parallel/LIVE_PROOF_BUNDLE/UNIFIED_PREFLIGHT_STATUS.json`
- `parallel/LIVE_PROOF_BUNDLE_QA_CURRENT_HEAD_PREFLIGHT/RESULT.md` historical V1 blocker
- current PYLAUNCH Startup Attestation fresh QA RESULT / RESULT.json / claim
- current Recorder in-flight atomicity fresh QA RESULT / RESULT.json / claim
- current Browser Fleet / Discovery evidence consumed by preflight.

If an equivalent V2/current-head independent QA is already COMPLETE/PASS on the same preflight blobs, stop `ALREADY COMPLETE — SAFE TO CLOSE`.
If equivalent work is CLAIMED/EXECUTING, stop `ALREADY CLAIMED — SAFE TO CLOSE`.
Otherwise atomically create `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V2.json` with exact current HEAD and audited preflight blobs.

## Scope

Independent QA only. Do not modify production/preflight implementation. Allowed writes only under `parallel/LIVE_PROOF_BUNDLE_QA_CURRENT_HEAD_PREFLIGHT_V2/**` plus this claim.
Do not launch Browser/WOF and do not start WOF-052/WOF-052L capture.

## Required checks

Independently verify at minimum:

1. historical PYLAUNCH ParentFrame BLOCKED evidence remains historical and does not false-block when current Startup Attestation successor is PASS/current;
2. missing/BLOCKED/malformed Startup Attestation successor blocks;
3. current PYLAUNCH production blob drift against successor pins blocks;
4. historical Unified freshness BLOCKED evidence remains historical and does not false-block when current Recorder in-flight atomicity successor is PASS/current;
5. missing/BLOCKED/malformed Recorder successor blocks;
6. current `unified_live_proof.py` blob drift against successor pin blocks;
7. claim COMPLETE without required PASS semantics blocks;
8. stale snapshot, mixed component commit, missing files/tests, unsupported Discovery capability, failed regression and safety mismatch all continue to block;
9. Chinese-first blocker output, `ownerActionRequired=false`, `longCaptureAutoStarted=false`, read-only/RAM-writes-0/input-disabled invariants remain exact;
10. BLOCKED preflight never invokes live runner; PASS may invoke only the guarded test seam;
11. current exact implementation-side 22-case suite remains green, but do not treat that suite alone as independent acceptance.

If private checkout is unavailable, source-exact reconstruction is allowed where repository convention permits; state execution limits precisely and never fabricate native execution.

## Success / failure

Success:
`PASS — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT FRESH QA V2 — REPOSITORY PREFLIGHT GREEN`

Failure:
`BLOCKED — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT FRESH QA V2 — <precise blocker>`

Owner action: **NO**.
