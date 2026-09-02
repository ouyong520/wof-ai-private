# Alpha Acceptance — Superseding-Gate Reconciliation V2 Result

Stage: `ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V2`

Status: **PASS — ALPHA ACCEPTANCE SUPERSEDING-GATE RECONCILIATION V2 — REPO PREFLIGHT POLICY CURRENT / RELEASE ADMISSION STILL FAIL-CLOSED ON OPEN GATES**

Owner action: **NO**.

This is a repository-only gate-policy reconciliation result. It does **not** declare the current Alpha release candidate admissible, does not claim Browser/WOF acceptance, and did not launch Browser/WOF.

## Canonical ownership

Canonical dedup v2 ownership remained exact throughout finalization:

- dedup key: `alpha.acceptance.superseding-gate-reconciliation.current-head`
- owner: `chatgpt-alpha-acceptance-superseding-gate-reconciliation-v2`
- claim token: `hEzQI_6fentWaBMu3jCk8xlBZPup1NdfzM_J5U5FsCA`
- claim start commit: `50ed1718092b795f9789264a50b5c781cd7ab49a`
- final audited main before durable result: `e021fc8b0b4256a045bdc404a1a2c9f11a9c0556`

## Reconciled policy

The official Alpha Acceptance path now uses:

`RUN_CURRENT_HEAD_ACCEPTANCE.cmd` -> `acceptance_entrypoint.py` -> `repository_preflight_current.py` -> existing bounded `acceptance_orchestrator.py` runtime.

The bounded Browser/WOF runtime itself was not rewritten by this stage. The historical gate selector is overridden before the runtime can access Browser/WOF.

Current policy/test blobs at final audit:

- `repository_preflight.py` — `c9f45446797189465c3965ec4ae186ad2defa1c4`
- `repository_preflight_current.py` — `45baf4c4045a2aa851a08d9d1131167fcebe6030`
- `acceptance_entrypoint.py` — `fab77495f1d736e0687c103e14262ef1a35ae63d`
- `RUN_CURRENT_HEAD_ACCEPTANCE.cmd` — `12b5f13d75a2961a71c90e656d839f498f34ca0a`
- `test_repository_preflight.py` — `f67cbd93f496da81e12a0f41bc21427e8ebad872`
- `test_repository_preflight_current.py` — `3f2750b80639ccb10604cc1baae8962557a2830a`
- `test_repository_preflight_successor_schema.py` — `a3ec68cd63f84b0664316d50a3bb921f543f6008`

## Superseding behavior — PASS

The repository preflight now preserves historical evidence without mechanically consuming stale verdicts:

1. Historical Formal adversarial `BLOCKED` remains immutable evidence.
2. Formal authority is selected from a `COMPLETE/PASS` current-blob revalidation whose freshness-sensitive worker/HUD/bootstrap/loader/core/real-adapter pins equal current source.
3. A later valid current Formal revalidation can supersede an older current-blob result rather than being permanently blocked by a hardcoded V1 path.
4. PYLAUNCH Startup Attestation requires its exact PASS semantics plus current tested production blobs.
5. Unified Recorder in-flight atomicity requires exact PASS semantics plus the current tested runtime blob.
6. Unified current-head preflight requires exact PASS semantics plus current preflight blobs.
7. Owner OneClick V3 remains mandatory and missing/stale package state fails closed.
8. True 5h V2 remains mandatory and ACTIVE/BLOCKED/missing/stale evidence fails closed.
9. Enemy Target Head Labels select a current-product fresh independent QA successor rather than permanently requiring historical V2. Thus the historical V2 drawing-buffer blocker is preserved while current V3 PASS is consumable.
10. `state=COMPLETE` alone is never accepted as PASS.
11. Missing/malformed evidence and exact blob drift remain blockers.
12. Repository gates must be green before the existing local offline regressions and before Browser access.

## Head Labels current reconciliation

At final audit, `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3` is `COMPLETE` with:

`PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V3 — EPOCH FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED`

It pins the exact current target-label helper:

- `product/alpha/wof_alpha_enemy_target_labels.js` — `e6e1260559f735b85ce6f69e87803369f125b2de`
- projection profile — `8de57739818503a0e14702d2fa0bb4eba58228d2`

The policy therefore correctly consumes V3 and does not falsely remain blocked on historical V2. This repository PASS still does not convert the `UNPROVEN`/bounded projection boundary into Browser proof.

## Player-head mandatory policy reconciliation

During this stage, current product policy changed: player-head danger warning became an **authoritative Alpha V1 P0 mandatory surface** rather than a later/Beta preference.

The current composite preflight detects that authoritative requirement and requires `ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1` to reach its exact integration PASS on current machine-readable product blobs. Old repository snapshots that predate the requirement are not retroactively backfilled with the later gate.

At final audit the integration claim is still `ACTIVE`, so current release admission remains blocked before Browser.

## Deterministic policy QA

Source-exact deterministic fixtures on the exact final policy/test blobs passed **14 / 14**. Final current-main re-read confirmed those policy/test blobs did not change after that execution.

Covered adversarial semantics include:

- historical Formal BLOCKED + current pinned successor PASS -> no false historical block;
- older Formal current-blob result BLOCKED + later current successor PASS -> successor can be consumed;
- Formal successor missing/BLOCKED/stale -> block;
- PYLAUNCH missing/BLOCKED/blob drift -> block;
- Recorder missing/BLOCKED/blob drift -> block;
- OneClick missing/stale -> block;
- 5h missing/BLOCKED/stale -> block;
- Head Labels implementation/current QA missing/BLOCKED/stale -> block;
- Head Labels V2 BLOCKED + exact-current V3 fresh QA PASS -> V3 supersedes release decision while V2 evidence remains immutable;
- actual `evidence.helperBlob/projectionBlob` successor schema compatibility;
- player-head mandatory requirement missing integration -> block;
- player-head product blob drift -> block;
- old snapshot without the later requirement -> no retroactive false block;
- fully green repository fixture -> preflight-only PASS while bounded real visual acceptance remains pending.

## Current gate snapshot

### Current / green

- **Formal current-blob:** `COMPLETE/PASS`; freshness-sensitive worker/HUD/bootstrap/loader/core/real-adapter blobs still match current main.
- **PYLAUNCH Startup Attestation:** `COMPLETE/PASS`; `browser.py`, `monitor.py`, `discovery_v2.py` still match tested blobs.
- **Recorder in-flight generation atomicity:** `COMPLETE/PASS`; current `unified_live_proof.py` remains the tested blob.
- **Unified current-head preflight V2:** `COMPLETE/PASS`; current preflight/entrypoint blobs remain the tested blobs.
- **Enemy Target Head Labels repository QA:** V3 `COMPLETE/PASS` on the exact current helper/projection contract.

### Still open and release-blocking

- **Player-head danger warning production integration:** `ACTIVE`.
- **True 5h Endurance Recovery V2:** `ACTIVE`. Latest observed durable checkpoint is segment 4, PASS with `actualElapsedMs=1500054`, but there is no final genuine >=5h PASS yet.
- **Owner OneClick Current-HEAD Release Refresh V3:** dedicated claim is not present; package gate therefore remains fail-closed.

These open gates do **not** invalidate this reconciliation stage. They are exactly the conditions the reconciled Acceptance preflight must continue to block.

## Real Browser/WOF acceptance remains separate

Even after all repository gates later become green, bounded real acceptance still must prove the release snapshot's visible behavior, including at minimum:

- correct enemy-head `1P / 2P / 3P`;
- correct player-head danger warning;
- horizontal/depth/rapid movement and jump following;
- player/enemy movement with camera/whole-screen scrolling;
- real P1/P2/P3 retarget without stale old label/warning;
- simultaneous supported enemies where applicable;
- resize/fullscreen/drawing-buffer remap;
- stale/uncertain/epoch-mismatched state fails closed rather than visibly drifting.

Repository/synthetic evidence is not substituted for this live proof.

## Safety / scope

Preserved:

- read-only observer;
- `ramWrites=0`;
- input injection false;
- no Worker replacement;
- no Blob rewrite;
- no Browser/WOF launch by this stage.

This stage changed only Acceptance/PM reconciliation artifacts. It did not modify Alpha product implementation, Safe Transport, Formal, PYLAUNCH, Unified/Recorder, Owner OneClick, HUDANCHOR, or game behavior.

## Stop condition

**PASS — ALPHA ACCEPTANCE SUPERSEDING-GATE RECONCILIATION V2 — REPO PREFLIGHT POLICY CURRENT / RELEASE ADMISSION STILL FAIL-CLOSED ON OPEN GATES**
