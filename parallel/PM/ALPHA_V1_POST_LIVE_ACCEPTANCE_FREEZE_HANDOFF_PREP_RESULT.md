# Alpha V1 Post-Live Acceptance / Freeze Handoff Prep — RESULT

## Verdict

**COMPLETE — ALPHA V1 POST-LIVE ACCEPTANCE / FREEZE HANDOFF PREP — LIVE PASS CAN FLOW DIRECTLY TO FINAL ACCEPTANCE/FREEZE WITHOUT REDUNDANT QA**

Release state at this preparation stop: **NOT RELEASED**.

Browser/WOF launched by this stage: **NO**.

This result prepares the repository closeout path only. It does not claim that Proof-Authority Hardening V2 has completed, that its one Final Fresh QA has PASSed, that bounded real Browser/WOF acceptance has run, or that V1.0.0 has been released.

## Audited authority snapshot

Final pre-result current `main` observed by this stage:

`ceb230d5efd42e059a374ed75ed2769a6a6b39f4`

Owner OneClick V4 immutable acceptance candidate:

- source commit: `770d240d286aa69c95e002a1ea88bcc3edb36407`;
- package version: `2026.09.02.770d240d286a`;
- selection policy: `owner-oneclick-runtime-v2`;
- selected files: 50;
- manifest: `parallel/OWNER_ONECLICK/package_manifest.json`;
- current V4 result: `parallel/OWNER_ONECLICK/RESULT.md`;
- V4 verdict: `PASS — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V4 — IMMUTABLE PLAYER-TEST CANDIDATE READY FOR BOUNDED REAL WOF ACCEPTANCE`.

A static compare from V4 source `770d240d...` to observed current main found no post-freeze change to a V4 package-selected Alpha/PYLAUNCH/Recorder/Unified Live Proof/Browser Fleet payload file. Later changes are packaging metadata/selector/result plus PM/acceptance/proof-prep artifacts. This is not a QA rerun; it is the narrow selected-runtime drift fact required by this handoff.

## Authority precedence used by this handoff

This handoff consumes the newest applicable successor authority rather than mechanically reusing stale historical gate names.

1. `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/README.md` identifies the official current acceptance entrypoint and successor-aware repository policy.
2. `parallel/PM/ALPHA_V1_CURRENT_HEAD_LIVE_ACCEPTANCE_READINESS_RECONCILIATION_RESULT.md` is the current gate ledger for the V4 era and explicitly closes already-PASS Formal/Recorder/PYLAUNCH/player-head/enemy-label gates absent audited blob drift.
3. `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/FINAL_PRELIVE_DRIFT_GATE.md` is the newest one-shot pre-live authorization seam after Hardening V2 + exactly one Final Fresh QA.
4. `parallel/PM/ALPHA_V1_BOUNDED_LIVE_ACCEPTANCE_OWNER_FLOW_V2.md` is the current Owner-facing live observation procedure and PASS/FAIL/NOT EXERCISED classification authority.
5. `parallel/PM/ALPHA_RELEASE_FREEZE_CURRENT_HEAD_RECHECK_V2_START_PROMPT.md` is the current freeze-reconciliation authority; historical Freeze Audit V1 remains immutable history and must not be mechanically reused.
6. `parallel/ALPHA_V1_0_0_USER_TEST_RELEASE_PREP/RESULT.md` is the current prepared V1.0.0 player-facing delivery surface and remains explicitly `NOT RELEASED` until final gates close.
7. `parallel/PM/ALPHA_V1_0_0_CURRENT_HEAD_RELEASE_GATE_PREFLIGHT_RECOVERY_V2/RESULT.md` supplies the current V1.0.0 fail-closed release-state rule and shortest-path discipline. Its older V3/package/tooling status is superseded where newer V4/current-head evidence exists.

Historical `parallel/PM/ALPHA_RELEASE_START_PROMPT.md` still defines the existence of an explicit terminal release-recording decision, but its older RC4-era product-scope statements conflict with later mandatory player-head/enemy-head V1 scope and therefore cannot be used to reopen or downgrade current V1 requirements. The final decision must consume current successor acceptance/freeze authority, not mechanically replay the old RC4 gate list.

## 1. Exact existing acceptance entrypoint for real live evidence

The official acceptance path is already present and must be reused:

- Windows Owner entry: `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/RUN_CURRENT_HEAD_ACCEPTANCE.cmd`;
- official Python entrypoint: `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/acceptance_entrypoint.py`;
- bounded runtime implementation: `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/acceptance_orchestrator.py`;
- result schema: `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/current_head_acceptance.schema.json`;
- default durable session output: `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/acceptance_result.json` unless `--output` selects another preservation path.

`acceptance_entrypoint.py` is authoritative because it injects `repository_preflight_current.release_gate` into the bounded runtime. Do not invoke the orchestrator's historical internal claim selector as a separate release policy.

During the real session, also apply the already-COMPLETE Owner Flow V2 observation checklist. The Owner Flow result is not a second acceptance engine: its per-surface observations are attached to the same final acceptance record as live visual evidence.

Preserve the **first valid result JSON**. A real FAIL must not be erased by immediate retry; retry is allowed only after the explicit failure cause is fixed.

## 2. Exact result/evidence field contract

### 2.1 Machine acceptance JSON — always required

Per `wof-alpha-current-head-acceptance-v1`, every top-level result requires:

- `schema` = `wof-alpha-current-head-acceptance-v1`;
- `result`;
- `snapshotCommit` = exact 40-hex checkout used for the session;
- `safety`;
- `failures`;
- `ownerStatusZh`.

Safety remains exact:

- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- `windowWorkerReplacement=false`.

### 2.2 Machine PASS fields

A machine result may be `PASS — CURRENT-HEAD REAL BROWSER ACCEPTANCE` only when it additionally contains:

- `world921031` exact SHA/signature authority;
- `repositoryGates`;
- `browserAttestation`;
- `runtimeIdentity`;
- `transport` with session, initial/rebound generations/nonces, `generationIncreased=true`, `nonceChanged=true`;
- `warning`;
- `clearStale`;
- `reconnectRebind`;
- `negativePairRejection`;
- `gameplay`;
- `failures=[]`.

The existing machine schema already permits `warning.firstValidWarning=NOT_EXERCISED`. Therefore a machine transport/identity PASS is **not by itself sufficient** for V1.0.0 release if a current release-mandatory live visual case remains unexercised.

### 2.3 Machine FAIL / INCOMPLETE / BLOCKED fields

For `FAIL`, `INCOMPLETE`, or `BLOCKED`, preserve the top-level required fields above and at least the emitted failure record(s):

- `code`;
- `class` = `BLOCKED | INCOMPLETE | FAIL`;
- `detail`;
- `messageZh`.

Do not collapse an `INCOMPLETE`/missing evidence window into PASS. Do not reclassify Browser/repository-gate BLOCKED as a gameplay FAIL.

### 2.4 Owner Flow V2 live-observation rows

For every visual/behavioral case actually used in the release decision, record at minimum:

- `verdict`: `PASS | FAIL | NOT EXERCISED`;
- `surface`: danger detection / player `[危险]` projection / enemy target label / retarget / mapping-remap / lifecycle / stale-authority fallback as applicable;
- `scene`: the exercised motion/event, e.g. left-right, depth, jump, rear-jump, rapid advance, stage scroll, retarget, resize, fullscreen, DPR, respawn, stale/rebind;
- `symptom`: one sentence describing the observed correct behavior, failure, or why no valid evidence window occurred;
- `mandatory`: whether the current release contract requires this subcase before release;
- `candidateSourceCommit`: `770d240d286aa69c95e002a1ea88bcc3edb36407` while V4 remains current;
- `packageVersion`: `2026.09.02.770d240d286a` while V4 remains current;
- `acceptanceSnapshotCommit`: the `snapshotCommit` from the machine acceptance JSON;
- `evidenceClass`: `REAL_BROWSER_WOF`.

Optional on PASS; strongly preferred on FAIL:

- short screenshot/video reference;
- enemy/move authority identifier when classifying danger detection;
- brief room/session note sufficient to distinguish a supplemental bounded session from the first session.

The Owner's minimal one-line report remains valid input:

`PASS/FAIL/NOT EXERCISED | surface=... | scene=... | symptom=...`

Repository closeout adds the candidate/snapshot/mandatory metadata so separate rooms cannot be accidentally combined across different release authority.

### 2.5 PASS / FAIL / NOT EXERCISED semantics

`PASS` means the required real event/window actually occurred and the expected behavior was positively observed.

`FAIL` means the required event/window occurred with enough authority to judge it and the behavior violated the contract. For danger warnings, distinguish `DETECTION FAIL` from `PROJECTION FAIL`; an unsupported/quarantined/unmapped attack without warning is neither.

`NOT EXERCISED` is a **per-case evidence state, not a top-level release PASS**. It means the room/session did not supply a valid positive observation window. It is not a bug verdict and must never be converted to PASS by repository/synthetic fixture evidence.

## 3. CLOSED repository gates — do not rerun after live PASS

The current V4-era readiness reconciliation marks these release gates CLOSED and they remain reusable while their audited release-consumed blobs do not drift:

| Gate | Current disposition | Post-live rule |
|---|---|---|
| Owner OneClick V4 immutable candidate | **CLOSED** | Do not rebuild/re-QA unless the deterministic selector finds selected path/set/blob drift. |
| Formal Real-Adapter Recovery V4 | **CLOSED** | Do not rerun 85/85 or 14/14 pin QA absent tested selected-runtime drift. |
| Recorder in-flight generation successor QA | **CLOSED** | Do not rerun 42/42 absent selected Unified runtime drift. |
| PYLAUNCH Startup Attestation | **CLOSED** | Do not rerun 35/35 absent tested PYLAUNCH blob drift. |
| Player-head warning latest Fresh QA V2 | **CLOSED** | Do not rerun repository QA; real visual projection is the live acceptance item. |
| Enemy target-head labels latest Fresh QA V3 | **CLOSED** | Do not rerun repository QA; real visual projection/retarget is the live acceptance item. |
| Danger coverage authority audit | **CLOSED** | Missing name↔type↔attack mapping is an observability/coverage limitation, not a reason to rerun the audit. |
| Bounded Live Acceptance Owner Flow V2 | **CLOSED** | Reuse the same procedure. |
| V1.0.0 player-test release preparation | **CLOSED** | Reuse prepared docs; do not recreate release notes/bug template after live PASS. |

Historical ACTIVE residues that have already been superseded by successor authority must not reopen these gates.

Hardening V2 and its one Final Fresh QA are not listed as already CLOSED here because this preparation does not pre-judge their future terminal state. They are pre-live prerequisites handled by the one-shot Final Pre-Live Narrow Drift Gate.

## 4. Proof-only Hardening V2 / Final Fresh QA cannot force V4 repackaging by themselves

This rule is now explicit and mechanical.

Before live acceptance, run only the prepared one-shot checker after Hardening V2 is terminal and exactly one Final Fresh QA PASS exists:

`python parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/final_prelive_drift_gate.py`

That checker verifies the exact hardened authority pins and Final Fresh QA while separately asking the current `owner-oneclick-runtime-v2` selector whether the V4 selected path set/blob SHAs still equal the frozen manifest.

Therefore:

- proof-only Hardening V2 files outside the OneClick selector: **NO V4 rebuild**;
- proof-only Final Fresh QA/result/fixture files outside the selector: **NO V4 rebuild**;
- PM/claim/audit/acceptance documentation drift outside the selector: **NO V4 rebuild**;
- actual selected-runtime path-set/blob drift: **V4 is no longer current; deterministic package refresh/revalidation is required before live/freeze**.

Do not use `main != 770d240d...` as a reason to repackage. Candidate currentness is selected-runtime equality, not branch-head equality.

## 5. Exact Release Freeze condition after live evidence

The current freeze entrypoint is the **Release Freeze Current-HEAD Recheck V2** authority. Historical Freeze Audit V1's old HOLD/BLOCKED verdict is superseded for current decision-making and remains history only.

After a successful live session, the freeze step is a **reconciliation/recording step, not another QA campaign**.

Freeze may close only when all of the following are true for one coherent release authority:

1. Final Pre-Live Narrow Drift Gate had authorized `START BOUNDED REAL WOF ACCEPTANCE` after Hardening V2 COMPLETE + exactly one exact-blob Final Fresh QA PASS.
2. The official acceptance result for the bounded session is machine-valid and has top-level `PASS — CURRENT-HEAD REAL BROWSER ACCEPTANCE`.
3. Every current release-mandatory Owner Flow V2 live visual case is `PASS`; there is no mandatory `FAIL` and no mandatory `NOT EXERCISED`.
4. The V4 package candidate is still the same immutable selected-runtime candidate: source `770d240d...`, package `2026.09.02.770d240d286a`, with no selected-runtime path/set/blob drift.
5. All already-CLOSED Formal/Recorder/PYLAUNCH/player-head/enemy-label/5h/preflight/package successor gates are still current by their exact pin/claim authority; they are consumed, not rerun.
6. No new unresolved package-selected/runtime P0/P1 implementation owner or new mandatory proof-authority blocker appeared after the pre-live authorization/live evidence.
7. Safety remains `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no Worker replacement; unsupported/uncertain evidence remains fail-closed.
8. The live acceptance evidence and candidate identity refer to the same release snapshot/authority; evidence from a different package/runtime authority is not merged into a freeze PASS.

If those conditions hold, the existing Freeze V2 success branch may be used directly:

`PASS — ALPHA CURRENT-HEAD ACCEPTANCE + RELEASE FREEZE GATES CLOSED`

There is no repository-authorized reason to insert another Formal, Recorder, PYLAUNCH, player-head, enemy-label, OneClick, or generic cross-check loop between live PASS and this freeze record.

If only repository-side freeze readiness is being recorded before live evidence exists, the weaker branch remains:

`PASS — ALPHA RELEASE FREEZE CURRENT-HEAD RECHECK V2 — REPOSITORY FREEZE-READY`

That weaker branch alone is **not** V1.0.0 release authority.

## 6. Exact `V1.0.0 PLAYER TEST RELEASE` condition

The release state may change from `NOT RELEASED` to `V1.0.0 PLAYER TEST RELEASE` only after all of these are simultaneously true:

1. exact current candidate has passed the one bounded real Browser/WOF acceptance through the official acceptance entrypoint;
2. all release-mandatory Owner Flow V2 live cases are PASS;
3. Release Freeze V2 is closed on that same accepted candidate, preferably via `PASS — ALPHA CURRENT-HEAD ACCEPTANCE + RELEASE FREEZE GATES CLOSED`;
4. no release-consumed selected-runtime drift occurred between live acceptance and freeze/release decision;
5. no new unresolved release-blocking P0/P1 authority exists;
6. V1.0.0 user-test release prep remains CLOSED/PASS and its prepared Chinese first-test guide, bug template, release notes and known limitations are included in the delivery surface;
7. a final **explicit release decision/record** is written by the current release authority. Live PASS or freeze PASS alone must not silently mutate the state to RELEASED.

Until the explicit final release decision exists, the state remains:

**NOT RELEASED**

No new product QA is implied by the release-decision step unless that step itself modifies a freshness-sensitive release-consumed product/runtime blob. Pure release metadata/docs recording does not justify re-running unrelated component QA.

## 7. Handling `NOT EXERCISED` without a full-game retest

### Non-mandatory subcase

If a subcase is explicitly non-mandatory under the current release contract and is `NOT EXERCISED`, preserve that state in the acceptance record. It does not by itself block freeze/release.

Current Owner Flow V2 explicitly treats naturally unavailable cases such as DPR remap when the environment cannot safely/naturally expose it, and death/respawn when it never occurs, as `NOT EXERCISED` rather than FAIL. Do not manufacture them with DevTools/scripts. A later authority may promote a subcase to mandatory; if so, follow that later authority rather than this example.

### Mandatory subcase

If any mandatory live case is `NOT EXERCISED`:

- overall release remains **NOT RELEASED**;
- do **not** rerun already-PASS repository QA;
- do **not** rebuild V4 while selected runtime is unchanged;
- do **not** require a full game, a clear, or repetition of already-PASS live cases;
- start exactly one additional **bounded active-room session** aimed only at the missing mandatory evidence window(s);
- preserve earlier PASS rows and the first session's original artifact;
- merge the supplemental live row(s) only if the same immutable candidate/selected-runtime authority remains current and there is no intervening authority drift/blocker.

Examples:

- missing real retarget -> enter an active room and stop once one authority-valid retarget has been observed and classified;
- no real supported danger-warning window -> use another bounded active-room session until a positively authority-recognized supported danger event exposes the warning/projection window, then stop;
- stale/invalid live window remains mandatory but was absent -> use only the bounded supported acceptance/proof exercise if the final candidate exposes one; never synthesize it in DevTools.

The supplemental session is evidence completion, **not a replay of the entire acceptance matrix**. A real earlier FAIL is different: it is not eligible for evidence-only supplementation until its cause is fixed.

## 8. Post-live outcome state machine

### A. Live PASS / all mandatory cases PASS

Shortest authorized closeout:

`live PASS -> preserve/record official acceptance JSON + Owner Flow rows -> Release Freeze V2 reconciliation on same candidate -> explicit V1.0.0 release decision`

No redundant QA or repackaging step is inserted unless an exact freshness-sensitive blob drift/new blocker is detected.

### B. Live machine PASS but mandatory `NOT EXERCISED`

`machine PASS + mandatory NOT EXERCISED -> NOT RELEASED -> one bounded supplemental active-room session for only missing case(s) -> update acceptance evidence -> freeze -> release decision`

### C. Any mandatory live FAIL

`live FAIL -> preserve first failure artifact -> NOT RELEASED -> owning fix lane -> only affected successor QA/repackage if its guarded blobs changed -> bounded re-acceptance`

Do not overwrite the failure with retries and do not rerun unrelated CLOSED gates.

### D. Selected-runtime drift after live evidence

If a package-selected path/set/blob changes after the accepted V4 run, that accepted evidence cannot silently authorize a different payload. Stop release, deterministically refresh/revalidate the package as required, and obtain acceptance against the new release authority only to the extent required by the changed surface. Do not pretend metadata drift is runtime drift, and do not pretend runtime drift is harmless metadata.

## 9. Frozen minimal handoff path

The intended default post-live closeout is now fixed as:

`LIVE PASS`

`-> acceptance_result.json + Owner Flow V2 live rows recorded for exact candidate`

`-> Release Freeze Current-HEAD Recheck V2 consumes existing CLOSED gates + exact pins; no component QA rerun`

`-> PASS — ALPHA CURRENT-HEAD ACCEPTANCE + RELEASE FREEZE GATES CLOSED`

`-> explicit V1.0.0 PLAYER TEST RELEASE decision`

This is deliberately the shortest path. Additional stages are justified only by one of four facts:

- mandatory `NOT EXERCISED` -> one bounded supplemental session;
- real FAIL -> fix only the owning defect and affected evidence;
- package-selected runtime drift -> refresh/revalidate affected package authority;
- new unresolved P0/P1/proof-authority blocker -> close that blocker before freeze/release.

Anything else is redundant gate churn and is not required by the current authority reviewed here.

## Scope compliance

This stage:

- launched Browser/WOF: **NO**;
- modified `product/alpha/**`: **NO**;
- modified danger rules: **NO**;
- modified target semantics: **NO**;
- modified Transport/PYLAUNCH/Recorder: **NO**;
- modified OneClick runtime/package selector/manifest: **NO**;
- modified proof tooling: **NO**;
- reran Formal/Recorder/PYLAUNCH/player-head/enemy-label/OneClick QA: **NO**;
- declared V1.0.0 released: **NO**.

## Stop condition

**COMPLETE — ALPHA V1 POST-LIVE ACCEPTANCE / FREEZE HANDOFF PREP — LIVE PASS CAN FLOW DIRECTLY TO FINAL ACCEPTANCE/FREEZE WITHOUT REDUNDANT QA**

Current release state remains **NOT RELEASED** until the real live evidence and explicit final release decision exist.
