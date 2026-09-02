# Alpha V1 Live Acceptance Overlay + Re-entry Recovery V1 — Execution Recovery V2 RESULT

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1_EXECUTION_RECOVERY_V2`
dedupKey: `alpha.v1.live-acceptance.overlay-reentry-recovery-v1.execution-recovery-v2`
claimToken: `c1f5a776-c916-4d89-9729-02325f2dedd7`

## Verdict

COMPLETE.

This PM-authorized continuation reused the already-landed V1 projection/re-entry/automatic-evidence implementation and completed the missing implementation-source workflow diagnosis, immutable successor manifest publication, Windows portable validation, durable result, and successor ownership closeout. No Fresh QA / second opinion / cross-check was opened. No Browser/WOF was started. The rejected historical package was not sent back to the Owner.

## Historical V1 ownership

The historical V1 canonical/stage claims remain unchanged and ACTIVE as stopped-worker historical ownership evidence:

- `parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.overlay-reentry-recovery-v1.json`
- `parallel/PM/STAGE_CLAIMS/ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1.json`

This V2 successor authority supersedes them; their old claim token was not reused, modified, or closed.

## Exact immutable successor package

Frozen implementation/package source:

- repository: `ouyong520/wof-ai-private`
- sourceCommit: `3aad0e9d316701e30cda65dc4a45ab00f0e3d1c3`
- packageVersion: `2026.09.02.3aad0e9d3167`
- generatedAtUtc: `2026-09-02T14:13:33Z`
- selectionPolicy: `owner-oneclick-runtime-v4-overlay-reentry-recovery`
- selected blobs: 63 exact Git blob pins
- manifest path: `parallel/OWNER_ONECLICK/package_manifest.json`
- manifest publication commit: `940a4d2778b7224679f1b620dd86ae716f901f07`

The package selects all recovery-critical runtime from the same frozen source: Owner OneClick, Alpha, PYLAUNCH, operator toolkit/automatic live session, HUDANCHOR bounded projection proof, recorder, browser fleet, and live-proof bundle. PYLAUNCH revision is `overlay-reentry-runtime-generation-v1`; projection proof mode is `package-selected-bounded-live`.

The old live-retest-rejected package `2026.09.02.91be86ade8d4` is not reused.

## Why the source workflow initially failed

Implementation-source Owner One-Click Package run `33640669500` at source `3aad0e9d316701e30cda65dc4a45ab00f0e3d1c3` established that the implementation self-check job was already SUCCESS. Its integrity/Windows failures were stale packaging state: the checked-in manifest still selected the older `91be86ade8d4dcc7ee100458a1cedd87f5873bf7` field-recovery snapshot and lacked the newly required `operatorToolkit` / `projectionProof` component layout and recovery runtime blobs. The Windows job therefore failed closed at manifest load and did not validate or bless the old package.

That run deterministically emitted the exact 63-blob `2026.09.02.3aad0e9d3167` candidate. Execution Recovery V2 published that frozen candidate rather than changing the already-complete implementation.

## Final workflow terminal result

Final Owner One-Click Package run: `33645002099` on manifest publication commit `940a4d2778b7224679f1b620dd86ae716f901f07`.

Terminal jobs:

- `field-recovery-self-check`: SUCCESS
- `integrity`: SUCCESS
- `windows-oneclick`: SUCCESS

The integrity job passed all 11 package tests, including deterministic immutable manifest/source pinning, exact blob matching, runtime-not-outgrowing-manifest, mutation rejection, overlay/re-entry runtime selection, Chinese/space path atomic switch, last-known-good behavior, UTF-8 owner surface, and second-launch direct/network-free-until-explicit-update contract.

Runtime/module checks passed 63 Python tests: 14 field recovery + 6 overlay/re-entry + 16 discovery + 5 Windows proof + 22 operator-toolkit/automatic-evidence tests. Together with 11 package integrity tests, 74 Python self-check/integrity tests PASS. Alpha RC5 product regression PASS. Python and HUDANCHOR JavaScript syntax checks PASS.

## Windows portable validation

The final Windows job ran on Windows Server 2025 and validated the exact published package:

- `WOF_PACKAGE_VERSION=2026.09.02.3aad0e9d3167`
- `WOF_SOURCE_COMMIT=3aad0e9d316701e30cda65dc4a45ab00f0e3d1c3`
- portable path included Chinese characters and spaces: `WOF 中文 Portable Launcher`
- first-run install downloaded and verified all 63/63 exact files
- selected recovery files were present, including `live_session.py`, `projection_recovery.py`, `reentry_discovery.py`, all three HUDANCHOR projection proof scripts, and player/enemy projection configuration
- no stale staging directory remained
- no-Browser package-selected launcher smoke correctly failed closed as `WAITING`, with Chinese proof surface and unchanged safety; that expected no-Browser WAITING was accepted by the workflow and is not a task blocker
- last-known-good `ci.previous` survived explicit update while current pointer was repaired to the immutable successor
- a second explicit updater run was idempotent and retained last-known-good
- the package integrity contract separately passed `test_second_launch_is_direct_and_network_free_until_update`, preserving direct local/offline second-launch behavior until an explicit update is requested

## No-overlay root cause and projection authority

The prior package could load Alpha after exact World 921031 acceptance but anchored overlays remained intentionally invisible because player/enemy projection authority was still UNPROVED / fail-closed. This was not evidence that target7E `0/4/8 -> 1P/2P/3P` semantics had disappeared, and danger-rule coverage was not changed.

V1 implementation now package-selects the bounded Owner-friendly HUDANCHOR proof and a projection recovery consumer. It does not guess camera address, scale, bias, head clearance, or enemy offsets; unsafe/unproved/synthetic proof is rejected. Serialized proof is not silently restored as authority in a future launcher process. A valid bounded live proof creates current-launcher-process projection authority; under that authority the enemy `1P/2P/3P` anchored path is reachable for observed authoritative enemy types, and the player `[危险]` anchored path is reachable when the existing production-enabled danger rules actually fire. Danger semantics/rules remain unchanged.

Repository checks cannot fabricate the required real visual calibration, and this recovery deliberately did not start Browser/WOF. Therefore exactly one bounded Owner calibration/live retest is still required. The successor is `READY FOR ONE MINIMAL OWNER CALIBRATION/LIVE RETEST`, not falsely marked live-proven.

## Re-entry Worker rediscovery and Alpha reactivation

The landed recovery revokes stale page/Worker/runtime generation authority on room leave/replacement, including same-targetId replacements. While the page is `page-only`, monitoring remains lightweight and invokes bounded deeper auto-attach traversal to find a late related Worker/WASM/heap. Exact World 921031 authority must be rebuilt before Alpha can reactivate. Stable accepted runtime returns to cheap cached-runtime-health checks.

Deterministic checks cover page-only recovery, bounded traversal, Worker replacement/new isolate, authority revocation, live projection authority preservation within the same launcher process across room re-entry, ambiguity/wrong identity/wrong World fail-closed behavior, and Alpha reactivation path.

## Periodic hitch regression boundary

The recovery does not restore periodic full-heap/ROM scanning. Field recovery tests explicitly verify that a stable runtime uses cheap health checks rather than repeating the identity probe. Deep re-entry discovery is only used when normal authority has been revoked/page-only recovery is needed. This preserves the previous periodic-hitch improvement boundary.

## Automatic evidence and ZIP

Menu 6 / focused live acceptance owns the normal evidence lifecycle. `parallel/OPTOOLKIT/live_session.py` automatically creates the session evidence directory, captures launcher stdout/stderr and compact proof/status, extracts a projection result when present, writes `SESSION_SUMMARY.json`, retains partial/error evidence, and atomically creates `results/packages/WOF_LIVE_ACCEPTANCE_<session>.zip`. The ZIP includes only the session tree, preventing recursive package nesting, and `FINAL_ZIP.txt` records the final ZIP location. Menu 7/8 remain manual fallback/repair paths rather than required normal steps.

Automatic-evidence tests also cover UTF-8/Chinese paths, valid partial JSON, read-only safety, projection extraction, non-recursive ZIP packaging, and menu 6 package-selected Alpha activation without DevTools.

## Git upload authority / secret safety

Current package has no repository-defined secure uploader at `parallel/OWNER_ONECLICK/upload_live_evidence.py`. The automatic session supervisor intentionally treats generic `gh` presence/authentication as insufficient authority to choose a remote destination/retention policy. Current result is therefore:

`LOCAL_ONLY_NO_REPOSITORY_DEFINED_SECURE_UPLOADER`

The local ZIP remains available. No PAT/token is requested from the Owner, inspected, embedded in the package/repository, or written into evidence. If a future package supplies the fixed approved uploader, it may reuse already-existing non-interactive machine authorization; upload failure still retains the local ZIP.

## Safety boundary

Unchanged and validated throughout package manifest, module checks, and Windows smoke:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`

## Precise next step

Use only successor package `2026.09.02.3aad0e9d3167`. Start the focused/menu-6 live acceptance flow and follow the existing minimal Chinese bounded projection-calibration prompts once. No DevTools, pasted JavaScript, address transcription, or manual arithmetic is required. In that same launcher session, perform the focused live retest including room leave/re-entry; evidence is collected and ZIPped automatically. Repository validation must not be substituted for that real bounded calibration.

COMPLETE — ALPHA V1 LIVE ACCEPTANCE OVERLAY + REENTRY RECOVERY V1 EXECUTION RECOVERY V2 — SUCCESSOR PACKAGE/RESULT DURABLE — READY FOR ONE MINIMAL OWNER CALIBRATION/LIVE RETEST
