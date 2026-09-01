# Owner One-Click Dynamic Refresh V2 Start Prompt

stageId: `OWNER_ONECLICK_DYNAMIC_REFRESH_V2`
priority: `P1`

## Why V2 exists
`OWNER_ONECLICK_DYNAMIC_REFRESH_V1` stopped correctly because the package workflow still hard-coded stale package/source/blob metadata and V1 had no workflow write authority. That prerequisite has now been closed by `OWNER_ONECLICK_WORKFLOW_DYNAMIC_MANIFEST_FIX_V1`, whose validation recorded Windows One-Click PASS, dynamic-manifest regression PASS, and stale-manifest fail-closed behavior. Re-run the package-owned work now against current HEAD; do not inherit the old BLOCKED state as if the blocker still exists.

## Dedup / claim guard
1. Check `parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_DYNAMIC_REFRESH_V2.json`.
2. If durable current result already satisfies the stop condition, return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`.
3. If another thread holds ACTIVE, return `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.
4. Otherwise claim the V2 stage and continue.

## Allowed write scope
- `parallel/OWNER_ONECLICK/**`
- `parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_DYNAMIC_REFRESH_V2.json`

Do NOT modify workflows, PYLAUNCH, Recorder, Live Proof, Alpha Transport, HUDANCHOR or product code. The required workflow capability is already present; if a new workflow defect is genuinely discovered, stop with an exact blocker instead of expanding ownership.

## Current problem to close
Current PYLAUNCH generation hardening changed production blobs after the previously frozen package manifest. Recent integrity checks have therefore correctly failed `test_current_pylaunch_runtime_cannot_outgrow_package`. This V2 must convert that fail-closed signal into a deterministic refreshed package snapshot, not weaken the integrity rule.

## Required work
1. Re-read current HEAD PYLAUNCH, WOF052L Recorder and Unified Live Proof package-consumed files.
2. Select one explicit immutable package-build source commit and regenerate all package manifest entries from that snapshot.
3. Ensure current PYLAUNCH `browser.py`, `cdp.py`, `discovery_v2.py`, `monitor.py`, `probe.py` and every other consumed runtime blob are represented by their actual selected-snapshot hashes.
4. Include current Recorder/Live Proof consumed blobs so the package cannot be a mixed-generation snapshot.
5. Preserve fail-closed verification: one mutated/stale blob must still reject the package with a Chinese-first diagnostic naming the stale path/hash.
6. Preserve/verify UTF-8 Chinese output in Windows-style redirected/non-interactive paths.
7. Verify Chinese path-with-spaces handling.
8. Record immutable package provenance: source commit, generated-at metadata as appropriate, exact resolved blob hashes, and package version derived deterministically rather than hand-maintained stale constants.
9. Re-read HEAD immediately before finalization. If package-consumed upstream files changed during the stage, either refresh to a new explicit final snapshot or stop with a clear moving-head blocker; never knowingly certify a mixed snapshot.
10. Run package-local/current workflow-compatible regression without modifying the workflow itself.

## Delivery reassessment requirement
Final result must state whether Owner One-Click stale-pin risk is actually removed for the current Alpha path, what remaining upstream blockers still prevent Owner testing, and whether another manual manifest refresh should be expected after normal upstream changes.

## Stop conditions
Success:
`OWNER ONECLICK DYNAMIC REFRESH V2 READY — CURRENT SNAPSHOT + UTF-8 PACKAGE VERIFIED`

Blocker:
`BLOCKED — OWNER ONECLICK DYNAMIC REFRESH V2 — <exact ownership/integrity blocker>`

Owner action: NO. Do not request Browser/WOF testing.