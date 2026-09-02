# Alpha V1 双头顶 One-Session Live-Proof Tooling Proof-Authority Fix V1

stageId: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_PROOF_AUTHORITY_FIX_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.anchored-overlays.one-session-live-proof-tooling-proof-authority-fix-v1`
dedupMode: `exclusive`

Priority: **P0 release-proof tooling fix**

Repository: `ouyong520/wof-ai-private`

## Trigger

Independent second-opinion cross-check V1 is durably BLOCKED:

`parallel/PM/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_CROSSCHECK_V1_RESULT.md`

The blocker is in proof authority/scoring, not in danger rules or target semantics. Browser/WOF must not be used to waive these repository-level false-pass paths.

## Before work

Strictly follow `parallel/PM/STAGE_DEDUP_GUARD.md` canonical dedup v2.

Re-read current `main`, the cross-check BLOCKED result, Recovery V2 RESULT, current `RUN_MANIFEST.json`, current proof tooling blobs, current stage/canonical claims, and recent related commits.

If an equivalent fix is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

If an equivalent fix is already ACTIVE, stop `ALREADY CLAIMED — SAFE TO CLOSE`.

Otherwise atomically create the canonical claim for the exact dedupKey, reread and verify your claimToken, then create the stage claim before modifying implementation.

## Narrow goal

Fix only the proof-authority / proof-scoring defects that can create false `IMPLEMENTATION_READY` or false-close required live gates.

Do **not** start Browser/WOF.
Do **not** modify danger rules, raw target semantics, Transport authority, gameplay input/AI, RAM-write policy, or speculative projection constants.
Do **not** activate either production projection profile from repository/synthetic evidence.

## Required fixes

### 1. Live provenance must not be self-declared

Current public/declarative fields such as `evidenceClass`, `source`, `synthetic`, or `browserWofActuallyRun` must not be sufficient to create live authority.

Implement a session-rooted live capability/witness that is obtained only through the actual one-session Top/Worker live runtime path and is not forgeable by constructing a JSON/object with matching strings/booleans.

At minimum:

- repository/synthetic/replay construction with all public fields forged must still be unable to reach `IMPLEMENTATION_READY`;
- candidate profile binders must require the real rooted live capability, not only declarative provenance fields;
- the capability must not be accepted from serialized evidence or a caller-provided token string;
- repository tests may exercise the negative boundary but may never mint/pretend the real live capability.

### 2. Cross-surface epoch correlation

Any phase that claims both player and enemy surfaces PASS must require the contributing observations to belong to one compatible authority tuple.

Correlate, as applicable:

- runtime epoch;
- projection epoch;
- drawing-buffer epoch / projectionEpoch;
- mapping generation/key;
- proof session identity.

A player event from epoch A plus an enemy event from epoch B must never jointly close a phase merely because their timestamps fall in the same window.

### 3. Lifecycle-safe proof identity

Add proof-local lifecycle/generation identity sufficient to distinguish an actor replacement from a retarget/motion continuation.

Enemy requirements:

- same numeric slot reused by a different physical enemy must create a new occupant generation/identity;
- `liveRetarget` may close only when target changes within the same proved enemy occupant generation;
- disappearance/reappearance, replacement evidence, type/identity discontinuity, or ambiguous continuity must invalidate old retarget/head-offset authority;
- enemy head-offset observations must bind to the same lifecycle-safe occupant/type identity; ambiguous overlap/replacement fails closed.

Player requirements:

- P1/P2/P3 proof samples must carry proof-local lifecycle/generation identity;
- head/reference click and body/reference click used to derive player head facts must be proven to belong to the same player lifecycle;
- death/respawn/object replacement inside the same runtime/projection epoch must invalidate old click/calibration authority rather than silently inherit it.

Do not invent a product gameplay identity field that is not actually observable. If continuity cannot be proven, fail closed / require recapture rather than assume sameness.

### 4. Stale-authority exercise must be transaction-rooted

The bounded stop/reinstall stale-authority exercise must have its own actual transaction identity/capability rooted in the real stop/reinstall operation.

Reason text, event type, timestamps, or caller-populated fields alone must not be enough to close the stale-authority gate.

A synthetic/replayed `STALE_*` event must not satisfy the gate without the real bounded transaction witness.

### 5. Preserve existing strict safety behavior

Must remain unchanged or stronger:

- primitive finite `warningSampleAt` only;
- strict raw target `0/4/8` only;
- marker/player/projection/drawing-buffer freshness;
- runtime/projection/drawing-buffer cross-epoch fail-closed;
- invalid confidence/non-finite/bounds fail-closed;
- player fixed-HUD fallback and enemy no-draw/suppression;
- resize/fullscreen/DPR remap authority;
- readOnly=true;
- ramWrites=0;
- inputInjection=false;
- no Worker replacement / Blob rewrite;
- no synthetic production-profile activation.

### 6. RUN_MANIFEST / result pinning

After implementation is stable, update the proof `RUN_MANIFEST.json` only through exact current blob pinning required by the tooling contract. Do not weaken drift detection.

Record a durable RESULT and correctly close canonical/stage claims.

## Independent regression requirements

Add deterministic regression attacks that are independent of the old Recovery 19/19 happy/supportive fixture and prove at least:

1. forged public live fields cannot produce `IMPLEMENTATION_READY`;
2. forged public live fields cannot activate/bind production-ready candidates;
3. player epoch A + enemy epoch B cannot jointly close a phase;
4. same-slot enemy A(P1) -> replacement enemy B(P2) is not counted as a retarget;
5. true same-enemy P1 -> P2/P3 retarget still closes correctly;
6. player respawn between head/body calibration invalidates old calibration authority;
7. ambiguous enemy head capture/replacement does not create a stable type offset;
8. synthetic stale reason/event cannot close the stale-authority exercise;
9. real-path-shaped valid fixtures preserve strict warningSampleAt, target, epoch, bounds and safety behavior;
10. repository regression cannot produce real `IMPLEMENTATION_READY` because the real live capability is unavailable by design.

Recovery V2's existing 19/19 regression may be rerun only as supportive regression after these independent attacks pass.

## Write boundary

Allowed implementation/result scope:

- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**`;
- this stage's RESULT/STATUS evidence;
- this stage's canonical/stage claims.

Do not modify `product/alpha/**` unless the current repository facts prove the blocker cannot be solved proof-locally. If that happens, stop BLOCKED with the exact required upstream product identity field instead of widening scope silently.

## Success stop

`COMPLETE — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING PROOF-AUTHORITY FIX V1 — FALSE-PROOF PATHS CLOSED / READY FOR FRESH QA`

## Failure stop

`BLOCKED — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING PROOF-AUTHORITY FIX V1 — <precise blocker>`
