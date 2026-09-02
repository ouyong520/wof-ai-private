# WOF Alpha — Current-HEAD Acceptance Prep

Stage origin: `ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP_V1`  
Current repository gate policy: `ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V2`  
Owner action now: **NO while any repository gate is open**.

This directory prepares one bounded later Windows/Browser/WOF acceptance. Repository preflight PASS is only admission to that bounded acceptance; it is never itself Browser/WOF evidence and never declares Alpha released.

## Current entrypoints

- `repository_preflight.py` — stable successor-gate layer for Formal/PYLAUNCH/Unified/OneClick/5h/Head Labels.
- `repository_preflight_current.py` — **authoritative current-HEAD composite policy**. It layers any newer mandatory Alpha policy that appeared after the V2 start snapshot; currently this includes the P0 player-head danger-warning production integration requirement.
- `acceptance_entrypoint.py` — official entrypoint; injects `repository_preflight_current.release_gate` into the existing bounded acceptance runtime without changing Browser/WOF logic.
- `acceptance_orchestrator.py` — bounded Browser/WOF runtime implementation retained from the prep stage. Its historical internal `CLAIMS` selector is no longer the official policy entrypoint.
- `RUN_CURRENT_HEAD_ACCEPTANCE.cmd` — Windows wrapper; calls `acceptance_entrypoint.py`.
- `test_repository_preflight.py` — deterministic successor-gate adversarial regression.
- `test_repository_preflight_successor_schema.py` — current Head Labels V2 evidence-schema compatibility regression.
- `test_repository_preflight_current.py` — current mandatory-policy extension regression.
- `current_head_acceptance.schema.json` — compact final Browser/WOF result schema.
- `failure_classification.json` — fail-closed English codes + Chinese owner messages.

## Authoritative repository gates

Before Browser access, the current composite requires all applicable gates below to be current and green. A claim being merely `COMPLETE` is insufficient; the expected PASS/decision/stop condition and release-consumed blob pins are checked.

1. **Formal current-blob successor** — `ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION_V1` must be `COMPLETE/PASS`; freshness-sensitive worker/HUD/bootstrap/loader/core/real-adapter blobs must still match. Historical Formal adversarial `BLOCKED` evidence remains preserved but does not override the newer authoritative successor PASS.
2. **PYLAUNCH Startup Attestation** — `PYLAUNCH_STARTUP_ATTESTATION_QA_V1` and its machine result must PASS; current `browser.py`, `monitor.py`, and `discovery_v2.py` must equal the tested production blobs.
3. **Unified Recorder in-flight generation atomicity** — `UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1` and its machine result must PASS; the tested `unified_live_proof.py` blob must still be current.
4. **Unified current-HEAD preflight Fresh QA V2** — `UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V2` must PASS and its release-consumed preflight blobs must still be current.
5. **Owner OneClick V3** — `OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V3` must reach its exact package-gate PASS and every manifest file blob must equal the current selected runtime blob. Missing claim or stale package fails closed.
6. **True 5h Endurance V2** — `ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_RECOVERY_V2` must reach the exact genuine-5h PASS and expose machine-readable Safe Transport snapshot pins that still match current source. Partial checkpoints, ACTIVE/BLOCKED claims, missing pins, or drift fail closed.
7. **Enemy Target Head Labels** — original mandatory implementation must be COMPLETE; strict raw-target-type fix must be COMPLETE on the current label helper; `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2` must reach the exact fresh independent PASS on the same current helper blob. Historical V1 QA BLOCKED is preserved, not rewritten.
8. **Player-head danger warning** — because current `parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md` now marks this as a P0 Alpha V1 requirement, `ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1` must reach its exact COMPLETE verdict with machine-readable current product blob pins. If an older snapshot does not contain that authoritative requirement, the future gate is not backfilled into that old snapshot.
9. Only after all evidence gates are green, the existing local deterministic Safe Transport/Formal/PYLAUNCH offline regressions are rerun before Browser admission.

All blockers are reported Chinese-first and the gate stops before Browser access. Missing/malformed claims, wrong verdicts, missing machine evidence, or blob drift are treated as blockers rather than guessed green.

## Live acceptance boundary

Even when repository preflight is fully green, the following remain **bounded real Browser/WOF acceptance requirements** unless exact live evidence for the release snapshot already exists.

Enemy-head target tracker:
- supported enemies show the correct `1P / 2P / 3P` label;
- labels follow enemy movement and camera movement;
- real retargeting switches promptly and leaves no stale old label;
- multiple enemies remain independent;
- unsupported/stale/uncertain/projection-invalid states suppress the label rather than showing a wrong target.

Player-head danger warning:
- warning follows the correct targeted live player through left/right movement, depth/lane movement, jump, rapid movement and stage scrolling;
- player + camera movement must not create repeatable/visible drift;
- real retarget invalidates the old player-head warning before the new one appears;
- resize/fullscreen/DPR/drawing-buffer remap and player replacement must not reuse stale coordinates;
- uncertain/stale projection falls back/hides rather than fabricating continuity.

Repository synthetic QA, source inspection, and an `UNPROVEN` projection profile are not accepted as live projection/non-drift proof. `--preflight-only` therefore reports repository PASS separately and explicitly says bounded live visual acceptance remains pending.

## Single bounded owner procedure — later only

Only after PM/release says the repository gates are green:

1. On the exact release-candidate checkout, start the normal supported Windows Browser/WOF flow and enter one ordinary playable room. Do not open DevTools or Worker Console.
2. Double-click `parallel\ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP\RUN_CURRENT_HEAD_ACCEPTANCE.cmd`.
3. The tool reruns the current composite repository preflight first. Any non-green gate exits before Browser access; do not bypass it.
4. If green, the existing bounded runtime performs strict local Browser/CDP attestation, Discovery V2 unique page/native-Worker/WASM/World Gate A, installs the support-only acceptance collector, and asks the single normal-play confirmation.
5. Continue normal play. No gameplay input is injected to manufacture evidence.
6. Preserve the first valid result JSON. Do not retry a real FAIL until its explicit cause has been fixed.

There is no fallback involving pasted JavaScript, Worker selection, RAM inspection, ad-hoc Console diagnosis, gameplay input injection, game Worker replacement, or Blob rewrite.

## Safety / separation

Repository reconciliation and preflight remain:

```text
readOnly=true
ramWrites=0
inputInjection=false
windowWorkerReplacement=false
blobRewrite=false
Browser/WOF launched by reconciliation=false
```

The V2 reconciliation changes only Acceptance/PM policy artifacts. It does not modify Alpha, Safe Transport, Formal, PYLAUNCH, Unified, OneClick, Recorder, HUDANCHOR, or Browser/WOF product implementation.

## Historical evidence rule

Historical BLOCKED/FAIL results remain immutable evidence of what was true at their tested snapshot. They are neither deleted nor rewritten. A newer authoritative successor gate can supersede their *release decision* only when its own exact PASS semantics and current blob pins validate successfully.

Current release admission stays fail-closed until every mandatory current gate above is green.
