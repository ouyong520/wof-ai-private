# Alpha First Owner Gate — Feedback / Acceptance Contract

P3 owns **aggregation, fail-closed acceptance, and failure routing only**. It does not implement or modify the HUD, runtime fixed-draw probe, permanent updater/launcher, renderer/object authority, or `alpha-live` ref.

## Owner-facing artifact

The single obvious artifact is:

`%USERPROFILE%\Documents\WOF_RESULTS\LATEST_ALPHA_FEEDBACK.txt`

The Owner is not required to open DevTools, inspect JSON, choose an internal file, set environment variables, or diagnose the failure layer. For the first gate, PM can work from this file alone (plus an optional screenshot/one-line Owner observation when human visual confirmation is needed).

## Automatic inputs

The helper reads only stable Alpha result surfaces under the same `WOF_RESULTS` directory:

1. Launcher/update status: parse the existing P2 `LATEST_ALPHA_FEEDBACK.txt` key/value surface for release SHA/live mode and prove readiness from read-only managed-repo Git metadata. Managed readiness requires managed HEAD == the reported release SHA. Update readiness requires the expected SSH origin plus a recent `FETCH_HEAD` containing `alpha-live` (<= 30 seconds; the P2 controller fetches every 6 seconds). A stale `RUNNING` line is never enough by itself.
2. Runtime fixed-smoke status: `ALPHA_FIXED_DRAW_STATUS.json`. It must be readable and fresh (mtime <= 60 seconds) before any runtime/draw readiness can be green.

The helper has no required Owner arguments. Integration invokes:

`python -m wof_launcher.owner_feedback_acceptance`

It atomically replaces `LATEST_ALPHA_FEEDBACK.txt` so the file is never intentionally left half-written.

## Required feedback fields

The artifact contains the current release SHA, `alpha-live`, live mode, managed repo/update readiness, runtime readiness, fixed-smoke status path/state, HUD/canvas evidence when available, `drawHooked`, `callbackCount`, `drawCount`, drawing buffer, native `384x224`, center `192,112`, label `TEST`, last error, machine-draw proof flag, and exactly one routing classification/reason.

`ownerVisualConfirmation=NOT_RECORDED` is deliberate. Machine evidence never manufactures a human visual PASS.

## Fail-closed routing order

Routing is deterministic and stops at the first failing layer:

1. `BOOTSTRAP_NOT_READY`
2. `UPDATE_CHANNEL_NOT_READY`
3. `LIVE_MODE_NOT_FIXED_DRAW`
4. `RUNTIME_NOT_STARTED`
5. explicit probe state: `HUD_INJECTION_MISSING`, `GAME_CANVAS_CONTEXT_MISSING`, `DRAW_HOOK_NOT_FIRING`, `DRAWING_BUFFER_INVALID`, or `DRAW_FAILED`
6. malformed/unknown potentially-green evidence: `FEEDBACK_INPUT_MALFORMED`
7. coherent armed candidate: `READY_FOR_OWNER_FIXED_TEST`
8. `FIXED_TEST_ACTUALLY_DRAWN` plus positive hook/callback/draw counts, positive drawing buffer, exact `384x224 @ 192,112 / TEST`, and read-only safety proof: `MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL`

A stale/missing fixed status routes to `RUNTIME_NOT_STARTED`; it cannot reuse a previous green draw. A malformed/unknown potentially-green payload routes to `FEEDBACK_INPUT_MALFORMED`.

## Human visual boundary

`FIXED_TEST_ACTUALLY_DRAWN` is **machine draw proof only**. The P3 helper intentionally ignores any untrusted `ownerVisualPass`-style input and never emits `OWNER VISUAL PASS`. Only a real Owner observation can establish whether `TEST` was visibly seen in the real WOF window.

## P1 + P2 coherent-candidate handoff

P3 is integration-ready when P1 writes the stable fixed-smoke JSON and P2 exposes the release SHA/live mode while its managed Git checkout supplies the read-only update heartbeat proof. No P3 production change is required to those owners: their coherent candidate can be fed directly into this helper and receives one classification with all evidence co-located in `LATEST_ALPHA_FEEDBACK.txt`.
