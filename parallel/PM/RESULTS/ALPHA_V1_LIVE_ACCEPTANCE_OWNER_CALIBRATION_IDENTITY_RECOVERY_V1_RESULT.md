# Alpha V1 Live Acceptance — Owner Calibration + Local Identity Recovery V1 — RESULT

Status: `COMPLETE`

Terminal verdict:

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE OWNER CALIBRATION + LOCAL IDENTITY RECOVERY V1 — SUCCESSOR PACKAGE READY — READY FOR ONE FOCUSED OWNER LIVE RETEST`

## Authority / immutable successor

- stageId: `ALPHA_V1_LIVE_ACCEPTANCE_OWNER_CALIBRATION_IDENTITY_RECOVERY_V1`
- dedupKey: `alpha.v1.live-acceptance.owner-calibration-identity-recovery-v1`
- implementation repository: `ouyong520/wof-ai-private`
- successor packageVersion: `2026.09.02.ffa2cb162df0`
- successor sourceCommit: `ffa2cb162df0cda65e6fa09b6b0e4fa8f6025399`
- manifestPublicationCommit: `58971200c57ea28398ba695a872885ea812da3ed`
- final implementation/package workflowRunId: `33650273815`
- package manifest: `parallel/OWNER_ONECLICK/package_manifest.json`

The repository `main` has subsequently advanced for unrelated stages. That does not change this successor: the package manifest is immutable and pins all selected runtime blobs to `ffa2cb162df0cda65e6fa09b6b0e4fa8f6025399`.

## 1. Live local-identity defect — root cause and strict recovery

The Owner field failure was real and reproducible at the authority boundary: Page/Worker/WASM/heap and exact World 921031 were accepted, but the package-selected field adapter then rejected Alpha activation with `P1/P2/P3 local identity mismatch`.

Root cause: the detector-local gate treated the three fixed player records as if P1/P2/P3 were simultaneously active and therefore required `+0x7C` to be `[0,4,8]` unconditionally. Existing recorder/HUD player topology authority already distinguishes an active player record from an unused/inactive fixed record by the record presence/lifecycle state. In a one-player topology, inactive/not-joined P2/P3 records can be zeroized and are not authoritative active-player identities, so the old unconditional three-slot equality check falsely converted a valid exact World into an Alpha activation failure.

Authoritative `+0x7C` semantics used by the recovery:

- active P1 must have its exact local self identity `0`;
- active P2 must have its exact local self identity `4`;
- active P3 must have its exact local self identity `8`;
- an inactive/not-joined fixed player record is not promoted to an active identity merely because the record address exists; its local identity may be zeroized by lifecycle teardown;
- for an inactive record, only the lifecycle-safe empty/zero form or that slot's own exact retained self identity is accepted;
- an active slot with a malformed/mismatched self identity still fails closed;
- an inactive slot containing a contradictory foreign/non-empty identity still fails closed;
- target semantics remain exactly `0 -> 1P`, `4 -> 2P`, `8 -> 3P`.

This is lifecycle-aware strict validation, not removal of the self-index gate.

The World identity hard gates were not relaxed. Detector-local exact World 921031 SHA-256 remains mandatory:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

Browser/WASM/heap authority, unique ROM locator sanity, runtime generation binding, stale/replacement invalidation, and read-only constraints remain fail-closed. Room leave/re-entry and runtime generation replacement continue to revoke stale authority before rediscovery/reactivation.

## 2. Calibration `NEED_MORE_SAMPLES` / prompt continuity — root cause and recovery

The live calibration had reached `samples 29 / NEED_MORE_SAMPLES`, but the old path did not provide sufficiently continuous Owner-facing state across temporary player lifecycle gaps. Sampling/projection readiness was coupled too closely to a currently active P1 frame; a temporary inactive/missing P1 could stop useful frame publication while the already collected camera samples had no explicit retained/pause/resume contract. At the same time the top-side UI exposed the internal quality reason without a durable, explicit Chinese action/next-command contract for the Owner. This allowed a valid in-progress calibration to appear stalled or silent instead of clearly remaining in `NEED_MORE_SAMPLES` and explaining what to do next.

The recovery now:

- retains valid camera samples across a temporary P1 inactive interval instead of discarding/resetting them;
- records a bounded paused state and reason while P1 is unavailable;
- resumes from the retained count when the authoritative P1 lifecycle becomes active again;
- continuously publishes calibration progress and explicit Chinese `actionZh` / `nextCommandZh` guidance while Camera is not yet ready;
- reports samples, target/remaining samples, quality reason/conditioning, pause state, restart/reset and checklist progression;
- keeps bounded watchdog/progress behavior rather than silently waiting forever;
- invalidates old calibration authority on page/Worker/runtime-generation replacement and restarts the visible state machine under the new authority;
- does not synthesize or promote a projection result and does not guess camera address, scale, bias, head offsets, or other projection constants.

The later proof requirements remain unchanged: Camera authority must become real; then the Owner still performs the bounded P1-head click, horizontal/scroll evidence, depth movement, jump, resize/fullscreen recovery, visible-enemy evidence, and unique stable projection-model selection. Repository self-check does not claim that this live proof has already passed.

## 3. Windows Owner UI thread safety

The live evidence addendum captured a concrete Python 3.13/Tkinter failure: a Tk `messagebox` could be created from a background thread and terminate that notification thread with `RuntimeError: main thread is not in main loop`.

The Owner tray notification path now dispatches Tk work through one UI/mainloop-owned dispatcher. Repeated notifications and clean shutdown are serialized on that UI thread; the old fire-and-forget background Tk calls are removed from the notification path. This prevents silent owner-notification thread death while keeping the game/runtime read-only.

## 4. Durable automatic evidence / ZIP continuity

The old live-session packaging retained only the final disconnected proof snapshot, so a later CDP disconnect could overwrite the useful earlier accepted authority and the real Alpha/calibration failure.

The successor retains bounded durable live state independently of the terminal snapshot:

- last accepted Browser/Page/Worker/WASM/heap/World authority tuple;
- last Alpha activation failure;
- last calibration progress/state/reason/action/next-command;
- bounded significant-event timeline (maximum 96 events);
- terminal disconnect/end state as a separate event rather than destructive replacement.

`WINDOWS_PROOF_STATUS.json` and the automatic session summary/ZIP therefore preserve diagnostically useful live state even if the final launcher snapshot is disconnected. Evidence remains local-safe; no repository upload is attempted without a repository-defined secure uploader.

## 5. Re-entry / runtime health / safety preserved

Existing Overlay + Re-entry Recovery behavior remains in force:

- page-only recovery can rediscover the room Worker/WASM after leave/re-entry;
- stale Alpha runtime authority is revoked before a new generation is activated;
- same-process valid live projection authority is not silently serialized into future-process authority;
- steady-state accepted runtime uses cheap cached runtime-health checks rather than periodic full heap/ROM rescans;
- automatic evidence collection and ZIP packaging remain enabled.

Safety boundaries are unchanged and package-validated:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`

No Browser/WOF session was started for repository closure and no live PASS was fabricated.

## 6. Module-owned self-check / integration result

Implementation-source self-check passed before successor publication. Recovery-specific deterministic coverage includes:

- lifecycle-aware local-identity matrix, including active exact identities, inactive zeroized/retained-own identity, and contradictory/malformed fail-closed cases;
- exact World identity gate remains mandatory;
- `29 samples -> temporary P1 inactive -> retain 29 -> resume sampling` continuity;
- significant accepted authority / Alpha failure / calibration progress survives terminal disconnect;
- significant-event history remains bounded to 96 entries;
- repeated Tk UI callbacks use one UI thread and close cleanly.

The maintained integration lane also passed existing exact-identity/generation/Alpha activation checks, overlay projection and room re-entry recovery, discovery late-readiness/association, Windows proof Alpha gate, Owner menu/evidence integration, frozen Alpha regression, and syntax checks.

## 7. Final successor workflow / Windows portable validation

Final workflow run `33650273815` completed with all required jobs `SUCCESS`:

### `field-recovery-self-check` — SUCCESS

- Exact identity, generation cache and Alpha activation self-check — PASS
- Overlay projection and room re-entry recovery self-check — PASS
- Discovery late-readiness and association self-check — PASS
- Live proof Alpha gate self-check — PASS
- Owner menu and automatic evidence integration self-check — PASS
- Frozen Alpha product regression — PASS
- Recovery runtime syntax checks — PASS

### `integrity` — SUCCESS

- successor manifest and mutation/last-known-good contracts — PASS
- deterministic immutable candidate manifest emission — PASS

### `windows-oneclick` — SUCCESS

- immutable checkout manifest load — PASS
- fresh portable install under Chinese + space path — PASS
- package-selected live-acceptance launcher no-Browser fail-closed smoke — PASS
- explicit update preserves last-known-good and repairs current pointer — PASS
- second explicit updater run is idempotent — PASS

This validates the published successor package itself, not the superseded `2026.09.02.3aad0e9d3167` package.

## 8. Owner next step

Do **not** retest the old package and do not use an unpinned current-main working tree as the acceptance candidate.

The next action is exactly one focused Owner live retest using successor package:

- packageVersion `2026.09.02.ffa2cb162df0`
- sourceCommit `ffa2cb162df0cda65e6fa09b6b0e4fa8f6025399`

For that single bounded retest, verify that exact World 921031 is accepted, Alpha no longer false-rejects a normal one-player topology on inactive P2/P3 local identity, calibration continues visibly beyond `NEED_MORE_SAMPLES` with explicit Chinese guidance, the required live head/projection checklist can proceed, re-entry automatically reacquires the new Worker/runtime generation, and the automatic evidence ZIP retains the useful accepted/failure/calibration timeline.

A repository COMPLETE result means the implementation/package recovery is ready for that live acceptance retest; it does not pre-claim the live visual acceptance outcome.
