# WOF Owner OneClick — Current-HEAD Release Refresh V3

stageId: `OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V3`

Priority: **P1 Alpha release/package gate — gated on fresh runtime QA**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md` before any work.

## PM reconciliation finding

The previous dynamic-refresh implementation/workflow is healthy, but the committed package snapshot is stale against current release-consumed runtime.

At PM reconciliation baseline:

- `parallel/OWNER_ONECLICK/package_manifest.json` sourceCommit is `947c3c5433a1fe5bf88845c6d1f529e40b82510f`;
- it pins `parallel/PYLAUNCH/wof_launcher/browser.py` to `e883030fe8a90333b8ed58aae5699118b2c876fe`, while current verified source is `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332`;
- it pins `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py` to `0d9010007910f58b77c64fde98264697191bb679`, while current generation-hardened source is `0ed41e4afb1a6a740315f356672df019ff3a15d3`.

This is expected fail-closed stale-package behavior after normal upstream runtime changes. Do not weaken integrity and do not manually edit individual hashes.

## Dedup / claim

Re-read latest main and all Owner OneClick dynamic/current-head refresh results.

If the current manifest already exactly represents all selected release-consumed runtime blobs from one immutable current release-candidate commit and the full package workflow is green, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If equivalent refresh stage is ACTIVE, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V3.json`

with exact current main start commit.

## Hard upstream gate

Do **not** refresh early merely to make the manifest look current. Before generating V3, require current evidence that package-consumed release runtime has settled:

1. `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_V1` = COMPLETE/PASS;
2. `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V1` = COMPLETE/PASS;
3. `PYLAUNCH_STARTUP_ATTESTATION_QA_V1` remains COMPLETE/PASS and its tested production blobs still equal current blobs;
4. no active P0/P1 fix owns a package-selected runtime file.

If any gate is not green, stop without modifying package files:

`WAITING_GATE — OWNER ONECLICK V3 REFRESH MUST WAIT FOR FRESH RELEASE QA`

The claim may remain ACTIVE only while actual work is owned; otherwise record a precise BLOCKED/WAITING result according to repository conventions rather than consuming the stage ambiguously.

## Goal

Generate one deterministic, immutable Owner OneClick release snapshot from the final current release-candidate commit, then prove package integrity, Windows one-click behavior, and Chinese/UTF-8 owner UX on that exact snapshot.

## Required implementation

Use the existing deterministic generator, not manual hash editing:

`python parallel/OWNER_ONECLICK/refresh_manifest.py --source <explicit-immutable-current-release-candidate-commit>`

Requirements:

- all selected PYLAUNCH / WOF052L Recorder / Browser Fleet / Unified Live Proof / OPTOOLKIT / Alpha owner assets come from the same explicit immutable commit where the selection policy requires that;
- every selected runtime file is represented and exact blob-pinned;
- added selected runtime files cannot outgrow the manifest;
- removed selected files cannot remain stale in the manifest;
- current worktree/runtime mismatch fails closed;
- stale/mutated payload still fails closed with Chinese-first diagnostic;
- base URL/version/provenance remain immutable and deterministic;
- no integrity weakening.

## Required QA

Run current package-local and workflow-compatible tests, including:

- deterministic manifest `--check` / source provenance;
- current runtime cannot outgrow package;
- all manifest blobs match source commit;
- stale/mutated-blob expected rejection;
- Linux/integrity job equivalents;
- Windows OneClick package flow;
- Chinese install path and path-with-spaces;
- redirected/non-interactive UTF-8 output;
- atomic update/current-pointer/last-known-good behavior;
- current PYLAUNCH and current Unified Live Proof files are exactly the ones delivered by the package.

If the repository workflow is available, run it and record exact Actions run id/result. Do not claim Windows PASS from static inspection alone.

## Read / write boundary

Read current release gate evidence and selected runtime files.

Write only:

- `parallel/OWNER_ONECLICK/**` as required by deterministic refresh/result;
- the dedicated stage claim.

Do not modify upstream PYLAUNCH, Recorder, Live Proof, Alpha transport/product, or HUD implementation to make package tests pass.

If an upstream runtime/package incompatibility is discovered, stop with precise blocker and hand it to the owning lane.

## Downstream consumer

- Alpha current-HEAD acceptance gate reconciliation/preflight;
- Alpha Release Freeze current-HEAD recheck.

## Drift rule

Immediately before finalizing, re-read main and every selected runtime blob. If any selected runtime blob moved after the chosen source snapshot because of a release-relevant fix, refresh again from one new explicit immutable snapshot and rerun package QA. PM-only/result-only commits that do not change selected payloads need not create a content-identical package version; record why.

## Success stop

`PASS — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V3 — PACKAGE GATE CLOSED`

Update claim COMPLETE with source commit, manifest blob, selected runtime provenance, Actions/workflow evidence, Windows/UTF-8 results, and ownerAction=`NO`.

## Failure stop

`BLOCKED — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V3 — <precise blocker>`

Update claim BLOCKED and preserve exact mismatch/test evidence.

Owner action: **NO**.