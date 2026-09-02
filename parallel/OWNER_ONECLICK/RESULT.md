# Owner OneClick Current-HEAD Release Refresh V4 — Result

Date: 2026-09-02  
Stage: `OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V4`

## Verdict

**PASS — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V4 — IMMUTABLE PLAYER-TEST CANDIDATE READY FOR BOUNDED REAL WOF ACCEPTANCE**

Owner action: **NO packaging action required**. The package candidate is ready for the separately bounded real-WOF acceptance flow; this stage did not launch Browser/WOF.

## Canonical ownership

- dedup protocol: `v2`
- dedup key: `owner.oneclick.current-head.release-refresh-v4`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/owner.oneclick.current-head.release-refresh-v4.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V4.json`
- claim token: `f0f42b4d-6b8c-4e0a-a9ec-0ff6e1bf7d5c`
- claim acquisition start commit: `c00e458e4cc96c75e6985aa793ac423c7cbac756`

The canonical claim was create-only and then re-read with the same token/key/mode/stage/state before V4 execution. The stage claim was also create-only and re-read with the same token.

## Immutable candidate

The V4 player-test candidate is frozen to one immutable Git snapshot:

- source commit: `770d240d286aa69c95e002a1ea88bcc3edb36407`
- source commit time: `2026-09-02T06:38:17Z`
- package version: `2026.09.02.770d240d286a`
- selection policy: `owner-oneclick-runtime-v2`
- selected files: **50**
- manifest: `parallel/OWNER_ONECLICK/package_manifest.json`
- manifest publish commit: `fa8f48712d3da580ca2b9aec437c1665ed6a8de8`

Every selected entry carries its exact Git blob SHA and all component provenance points to the same `770d240d...` source commit.

The repository CI independently executed the deterministic generator contract:

`manifest == refresh_manifest.generate_manifest(ROOT, manifest.sourceCommit)`

and passed. Therefore the committed manifest is a deterministic derivation of the immutable source snapshot rather than a manually assembled set of current-looking hashes.

## Hard gates re-read on the candidate

### 1. Formal Real-Adapter current-generation QA — **GREEN**

Successor result:

`parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3_RECOVERY_V4/RESULT.md`

Verdict:

`PASS — ALPHA FORMAL REAL-ADAPTER INTEGRATION CURRENT-HEAD FRESH QA V3 RECOVERY V4 — CURRENT RELEASE RUNTIME VERIFIED / V3 INTERRUPTION SUPERSEDED`

Recovered current-source execution is **85/85 PASS** and its final revalidation is **14/14 exact source pins current**, with no runtime/SUT drift.

The candidate exact production pins match that gate, including:

- `product/alpha/wof_alpha_real_worker.js` = `b7f4506fc90b681ede059df5ad3316e665c6f15e`
- `product/alpha/wof_alpha_hud.js` = `50d944c451ac94b114e4f86441aeae8ad6b25c78`
- `product/alpha/wof_alpha_player_head_warning.js` = `af7f2359514dc6f86f74fac0c47858e8a6acf107`
- `product/alpha/wof_alpha_bootstrap.user.js` = `5aed15ff14aa39d95eade187cefb63dbd00848e6`
- `product/alpha/wof_alpha_loader.js` = `66aee09fc2dd009c2f295d2092f3129548605efb`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` = `ec9d27bfe26557a11187a23853893b898a3366d1`
- `parallel/PYLAUNCH/wof_launcher/probe.py` = `789a6849b826b35542b22d56a4d2ca3628d285a1`

### 2. Recorder successor QA — **GREEN**

Successor result:

`parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.md`

Verdict:

`PASS — RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA — READY FOR CURRENT-HEAD UNIFIED PREFLIGHT`

Execution result is **42/42 PASS**. The candidate packages the same tested production blob:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py` = `8df637d370d187660592fe8de0f1c73ff3057804`

The successor closes the old in-flight Recorder-generation mutation race while keeping stale/wrong-generation authority fail-closed.

### 3. PYLAUNCH startup attestation — **GREEN / CURRENT**

Result:

`parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.md`

Verdict:

`PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED`

Execution result is **35/35 PASS**. Candidate pins exactly match the current tested authority blobs:

- `parallel/PYLAUNCH/wof_launcher/browser.py` = `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332`
- `parallel/PYLAUNCH/wof_launcher/monitor.py` = `8e3c5c527fdd5a845bbfc135f55014de22078cf4`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` = `ec9d27bfe26557a11187a23853893b898a3366d1`

### 4. Package-selected ACTIVE P0/P1 implementation owner — **NONE**

At candidate freeze, the concurrent proof-authority hardening activity was in the proof-only lane. The candidate commit itself only added the corresponding PM stage claim and did not alter selected runtime.

A final drift scan from candidate `770d240d...` to latest observed `main` after the V4 CI found only:

- `parallel/OWNER_ONECLICK/package_manifest.json`
- `parallel/OWNER_ONECLICK/refresh_manifest.py`
- PM start prompts / canonical claims / stage claims for bounded live acceptance and danger-coverage authority audit

There were **no post-freeze changes** to package-selected Alpha, Transport/PYLAUNCH, Recorder, Browser Fleet, or Unified Live Proof runtime files.

The newly active bounded-live-acceptance / authority-audit claims are acceptance/audit work, not P0/P1 implementation ownership of selected runtime, so they do not trigger V4 `WAITING_GATE`.

## Current V1 production closure selected correctly

V4 found and corrected one package-policy omission without modifying production implementation.

The existing Alpha bootstrap loads `wof_alpha_loader.js`, and the loader in turn requires current dual-overlay production assets. The previous OneClick selector did not include the complete current production closure. V4 therefore changed only:

`parallel/OWNER_ONECLICK/refresh_manifest.py`

so the fixed package selection now includes:

- `product/alpha/wof_alpha_loader.js`
- `product/alpha/wof_alpha_real_worker.js`
- `product/alpha/wof_alpha_enemy_target_labels.js`
- `product/alpha/wof_alpha_player_head_warning.js`

alongside the already selected bootstrap/core/HUD/HUD-model assets.

No Alpha, Transport, PYLAUNCH, Recorder, Browser Fleet, Unified Live Proof, danger-rule, target-semantic, input/AI, or RAM implementation was changed to make the package pass.

## Proof-only tooling remains outside the player package

Proof-only dual-overlay/live-proof tooling under lanes such as:

`parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**`

is **not selected** into the 50-file player package and did not block V4 solely because a proof-only owner was active.

Likewise, the current projection-profile JSON artifacts remain fail-closed/unproved and are not silently activated or added merely to make the package look more complete. V4 packages the production execution closure actually selected by the current runtime, not proof-only capability or unproved calibration profiles.

## Exact package safety

Manifest safety is exactly:

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false
}
```

The Windows installed proof smoke independently returned the same safety state while disconnected from any Browser/WOF instance:

- read-only: `true`
- RAM writes: `0`
- input injection: `false`

The installed-package CI also rejects a forbidden `window.Worker = ...` replacement pattern.

## Owner OneClick CI — **PASS**

Workflow: `Owner One-Click Package`  
Run ID: `33600926628`  
Workflow head: `fa8f48712d3da580ca2b9aec437c1665ed6a8de8`

Jobs:

- `integrity` — **PASS**
- `windows-oneclick` — **PASS**

### Integrity regression: 13/13 PASS

The repository-native package tests passed all 13 checks, including:

- deterministic immutable manifest generation from one source commit;
- one-snapshot component provenance;
- every manifest blob equals the pinned Git commit;
- current selected runtime cannot outgrow or drift from package;
- stale/mutated selected payload rejection with Chinese-first integrity diagnostics;
- atomic staging / release switch / current-pointer ordering;
- failed staging cannot replace last-known-good;
- update from previous package preserves last-known-good;
- Chinese + spaces path atomic switch;
- redirected/non-interactive Windows UTF-8 contract;
- Python missing automatic `winget` path;
- Chinese owner surface;
- PYLAUNCH Discovery V2 and Chinese proof path truly pinned.

The stale/mutated fixture specifically alters a selected `browser.py` after staging and verifies fail-closed rejection with expected/actual Git-blob diagnostics. The current-runtime drift check separately rejects a manifest whose selected runtime is stale relative to the checkout.

### Windows OneClick regression: PASS

Windows Server 2025 executed the real Chinese OneClick entry under a path containing both Chinese characters and spaces.

The workflow proved:

1. manifest contract / safety validated before install;
2. real `WOF_一键工具.cmd --update-only` fresh install succeeded;
3. all **50/50** selected files downloaded from the immutable source commit and passed Git-blob integrity checks;
4. installed manifest exactly matched checkout manifest, source commit, file set and safety;
5. no staging directory remained after successful switch;
6. installed Chinese Windows proof path smoke-started with `--once --attach-only` and did **not** launch Browser/WOF;
7. disconnected proof remained fail-closed and reported `{readOnly:true, ramWrites:0, inputInjection:false}`;
8. update from a synthetic previous version switched to the new candidate while retaining the previous `installed.ok` last-known-good;
9. all updated package files were re-hashed against the manifest;
10. a second updater run kept the immutable current release and preserved the previous LKG.

## Update failure / LKG guarantee

The package updater contract stages a new release first, verifies blob integrity, moves the completed stage into the release directory, and only then atomically replaces `current.txt`.

Repository regression proves a failed/partial stage is removed without changing the existing `current.txt`, and the current known-good release remains present. Therefore a failed update cannot replace or destroy the currently usable version.

## Scope / non-live boundary

- Alpha implementation modified: **NO**
- Transport implementation modified: **NO**
- PYLAUNCH implementation modified: **NO**
- Recorder implementation modified: **NO**
- Browser/WOF launched: **NO**
- proof-only tooling added to player package: **NO**
- unproved projection profile activated: **NO**
- player candidate immutable source: **YES**
- selected blobs exact-pinned: **YES**
- Windows OneClick current candidate regression: **PASS**

This PASS does **not** claim real Browser/WOF visual/non-drift acceptance. That is intentionally the next bounded acceptance step.

## Stop condition

**PASS — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V4 — IMMUTABLE PLAYER-TEST CANDIDATE READY FOR BOUNDED REAL WOF ACCEPTANCE**
