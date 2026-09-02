# Alpha V1 Live Acceptance — Camera Authority READY Stability Recovery V1 — RESULT

Status: `COMPLETE`

Terminal verdict:

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE CAMERA AUTHORITY READY STABILITY RECOVERY V1 — SUCCESSOR PACKAGE READY — READY FOR ONE FOCUSED OWNER LIVE RETEST`

## Authority / immutable successor

- stageId: `ALPHA_V1_LIVE_ACCEPTANCE_CAMERA_AUTHORITY_READY_STABILITY_RECOVERY_V1`
- dedupKey: `alpha.v1.live-acceptance.camera-authority-ready-stability-recovery-v1`
- implementation repository: `ouyong520/wof-ai-private`
- final immutable sourceCommit: `52c942085c99f6814d4389c43d8e5fe626bdea10`
- successor packageVersion: `2026.09.02.52c942085c99`
- manifestPublicationCommit: `c834497aabe5983801c30dbb7e7843074a9ad05a`
- Camera READY implementation-source workflowRunId: `33660928233`
- successor package validation workflowRunId: `33661111743`
- package manifest: `parallel/OWNER_ONECLICK/package_manifest.json`

The superseded package `2026.09.02.b3f4004f1e32` must not be used for the next Owner retest. It contained the Camera READY authority recovery but still carried the pre-fix Tk dispatcher blob. The final successor pins all selected package runtime files to `52c942085c99f6814d4389c43d8e5fe626bdea10`; the manifest publication commit only publishes that immutable snapshot and is not substituted as the runtime source commit.

## 1. Live Camera READY authority conflict — root cause

The reported live state was a real authority defect, not an Owner-operation error. The game Top UI could observe one instant where the current camera ranking passed quality thresholds and display `READY`, while a later diagnostics poll could observe a different ranking/conditioning state and display `CANDIDATE_AMBIGUOUS`. Top click handling also re-read a current candidate instead of consuming the exact READY observation that had authorized the click. This allowed:

- transient quality success to be promoted directly to Owner-visible READY;
- a later ranking change to make tray/diagnostics contradict the Top UI;
- READY-to-click time-of-check/time-of-use drift between the candidate shown to the Owner and the candidate actually locked;
- polling surfaces to describe different unversioned snapshots without an explicit authority sequence.

The recovery does not loosen ambiguity thresholds and does not guess camera/projection constants.

## 2. Bounded stable READY authority

Camera readiness is now an explicit, versioned authority rather than a synonym for one instantaneous ranking result.

- `READY_STABLE_SAMPLES=20`: a qualifying top candidate must remain qualified for a bounded stable window before READY is created.
- A pre-READY ambiguity/top-candidate change resets the stability streak instead of preserving an unsafe partial streak.
- `AMBIGUOUS_ACTIVE_SAMPLE_LIMIT=1200` remains a bounded fail-closed terminal path; ambiguity is not weakened to make READY easier.
- READY creation records an `authorityId`, `authorityGeneration`, candidate generation/address, proof sample window (`sampleStart`/`sampleEnd`), worker session, and publication sequence.
- Once created, the verified READY authority is latched against ordinary ranking drift. Later transient candidate ordering therefore cannot silently replace the authority already shown to the Owner.
- Runtime/session replacement or explicit stop revokes the old READY authority and publishes a newer revoke sequence; stale authority is not carried into a replacement Worker generation.

Durable authority events include candidate generation, READY creation, lock rejection, successful Camera lock, and READY revocation. Polling the same snapshot does not duplicate the durable timeline.

## 3. Exact READY-to-click consumption / TOCTOU removal

Top-side calibration is now two-phase and authority-bound.

- Top obtains an exact READY snapshot rather than calling a live `cameraTop[0]` accessor at click time.
- The pending click captures the exact authority identity/generation/address and snapshot sequence shown as READY.
- The Worker `lock-camera` message must match the current READY `authorityId`, `authorityGeneration`, and address exactly.
- Wrong address, wrong generation, stale READY snapshot, Worker-session replacement, or READY authority mismatch fails closed.
- Calibration only finalizes after the Worker acknowledges the exact authority lock (`CALIBRATION_LOCK_ACKED`); the click itself is not treated as proof of a successful lock.

This removes the READY -> click candidate TOCTOU path while preserving the existing projection/calibration proof requirements.

## 4. Top / tray / evidence authority consistency

Owner-facing state now carries the same authority identity and sequence into durable launcher state/evidence:

- worker session id;
- snapshot id / sequence;
- camera authority id and generation;
- candidate generation/address;
- stable/required stable sample counts and proof sample window;
- authority timeline events;
- current Chinese guidance / next command.

The tray/evidence layer therefore records the exact authority state that produced READY rather than reconstructing readiness from a separate unversioned ranking poll. A later runtime replacement is represented as a revoke/new-generation event rather than as a contradictory continuation of the old READY state.

## 5. Tk dispatcher shutdown regression found by the recovery gate

The first Camera READY implementation-source workflow (`33656834394`) correctly failed at `test_tk_dispatcher_repeated_callbacks_use_one_ui_thread_and_close_cleanly`: after `TkUiDispatcher.close()`, `status["running"]` could still be `True`.

This was a real production shutdown race, not a harmless slow runner and not merely a test-isolation defect.

The pre-fix sequence was:

1. the Tk owner-thread drain consumed queued UI callbacks and observed the queue empty;
2. another thread entered `close()`, set `_closing=True`, and enqueued `_STOP`;
3. the owner-thread drain reached its tail and skipped scheduling the next `after()` because `_closing` had become true;
4. `_STOP` remained stranded in the queue, so `root.quit()` was never executed;
5. the bounded join returned while the Tk mainloop thread was still alive.

The minimal production fix keeps the Tk owner-thread drain scheduled until `_STOP` is actually consumed. `close()` still performs no Tk calls from the foreign thread: it only marks closing and enqueues the sentinel. The owner thread consumes the sentinel and calls `root.quit()`. This preserves the previous Tk thread-safety recovery rather than regressing to cross-thread Tk access.

The Camera recovery workflow now explicitly includes `parallel/PYLAUNCH/wof_launcher/tray.py` in its trigger paths and restores the exact original shutdown test to its selected regression set. A new deterministic race fixture also forces the precise `empty observed -> close enqueues STOP -> drain tail` interleaving, so this defect cannot be hidden by runner timing or a larger timeout.

## 6. Preserved prior live-acceptance contracts

This recovery preserves, without relaxing:

- exact World 921031 identity / SHA authority;
- lifecycle-aware active/inactive local player identity semantics;
- room leave/re-entry Worker rediscovery and runtime-generation invalidation;
- cached/low-overhead steady-state runtime health behavior;
- retained calibration progress and bounded Owner guidance;
- one Tk owner thread for Tk UI work;
- automatic local evidence and ZIP packaging;
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`.

No Camera/projection constant was guessed and no ambiguity threshold was weakened. No Browser/WOF live PASS is fabricated by this repository closeout.

## 7. Implementation-source verification

Final implementation source: `52c942085c99f6814d4389c43d8e5fe626bdea10`.

Alpha Camera READY Stability Recovery workflow run `33660928233` completed `SUCCESS`. Its module-owned gate passed:

- Camera READY stability / TOCTOU deterministic self-check — PASS;
- stable READY is bounded, latched, and exact-lock-only — PASS;
- pre-READY ambiguity resets the streak and never treats instant quality as READY — PASS;
- Top click is two-phase and authority-bound — PASS;
- StatusStore preserves authority generation/sequence/timeline without duplicate re-poll events — PASS;
- lifecycle-aware identity / retained calibration continuity — PASS;
- original repeated-callback Tk one-thread clean-close regression — PASS;
- deterministic close-vs-drain-tail STOP-consumption race regression — PASS;
- room re-entry/runtime-generation regression — PASS;
- runtime syntax and read-only boundary assertions — PASS.

This is the replacement for failed run `33656834394`; the failure was fixed in production and retested, not excluded or ignored.

## 8. Immutable package freeze and Windows portable validation

Because `tray.py` changed after package `2026.09.02.b3f4004f1e32`, that package was intentionally not accepted as the final successor. The first package run against the changed working source correctly detected manifest/runtime drift at `parallel/PYLAUNCH/wof_launcher/tray.py` and failed integrity rather than silently mixing source generations.

The final package was regenerated from the exact immutable source snapshot:

- packageVersion: `2026.09.02.52c942085c99`
- sourceCommit: `52c942085c99f6814d4389c43d8e5fe626bdea10`
- `tray.py` git blob: `1dd1ee37d841523fe028bb4aebdd64fa8d6b5ac9`
- manifestPublicationCommit: `c834497aabe5983801c30dbb7e7843074a9ad05a`

Owner One-Click Package workflow run `33661111743` completed `SUCCESS` with all required jobs green:

### `field-recovery-self-check` — SUCCESS

- exact identity/generation/Alpha activation — PASS;
- overlay projection and room re-entry — PASS;
- discovery late-readiness/association — PASS;
- live proof Alpha gate — PASS;
- Owner menu/automatic evidence integration — PASS;
- frozen Alpha product regression — PASS;
- runtime syntax checks — PASS.

### `integrity` — SUCCESS

- successor manifest and mutation/last-known-good contracts — PASS;
- deterministic immutable candidate manifest emission — PASS.

### `windows-oneclick` — SUCCESS

- immutable checkout package manifest load — PASS;
- fresh install under Chinese + space portable path — PASS;
- package-selected launcher smoke without Browser fails closed as `WAITING` while preserving safety flags — PASS;
- explicit updater preserves last-known-good and repairs `current` pointer — PASS;
- repeated explicit update is idempotent — PASS.

Thus package validation covers the final Tk-race-safe source, not the superseded package.

## 9. Owner next step

Do not continue testing `2026.09.02.b3f4004f1e32` or any earlier package.

The next action is exactly one focused bounded Owner live retest using:

- packageVersion `2026.09.02.52c942085c99`
- sourceCommit `52c942085c99f6814d4389c43d8e5fe626bdea10`

The live retest should verify the actual game behavior that cannot be proven by repository fixtures: after exact World/local-identity acceptance, Camera READY must only appear after stable authority creation; Top/tray must remain consistent for that authority; one P1-head click must consume the exact READY authority; re-entry/runtime replacement must revoke stale authority and reacquire cleanly; evidence ZIP must preserve the authority sequence. Repository COMPLETE means this implementation/package recovery is ready for that bounded live acceptance retest; it does not pre-claim the visual/live outcome.
