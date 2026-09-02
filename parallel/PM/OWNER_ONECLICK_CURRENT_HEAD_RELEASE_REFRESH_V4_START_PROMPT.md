# Owner OneClick Current-HEAD Release Refresh V4

stageId: `OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V4`
dedupProtocol: `v2`
dedupKey: `owner.oneclick.current-head.release-refresh-v4`
dedupMode: `exclusive`

Priority: **P0/P1 release packaging gate**

Repository: `ouyong520/wof-ai-private`

## PM reason

Owner OneClick V3 correctly stopped `WAITING_GATE` because no current formal real-adapter fresh QA certified the then-current `real_worker` / HUD generation.

That blocker is now superseded by durable successor:

`parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3_RECOVERY_V4/RESULT.md`

with verdict:

`PASS — ALPHA FORMAL REAL-ADAPTER INTEGRATION CURRENT-HEAD FRESH QA V3 RECOVERY V4 — CURRENT RELEASE RUNTIME VERIFIED / V3 INTERRUPTION SUPERSEDED`

The recovery verified 85/85 fresh current-source cases and 14/14 tested source pins current with no runtime/SUT drift.

This V4 is a new successor packaging stage. Do not reopen, overwrite or reuse the historical V3 canonical claim/result.

## Goal

Generate the current deterministic player-test candidate package from one immutable current release snapshot, now that the formal real-adapter gate is green.

## Before work

Re-read current `main`, recent commits, STAGE_DEDUP_GUARD, relevant canonical/stage claims and at least:

- Formal Real-Adapter Current-HEAD Fresh QA V3 Recovery V4 PASS;
- Recorder in-flight generation atomicity Fresh QA successor PASS;
- PYLAUNCH startup attestation/current checked blobs;
- current `parallel/OWNER_ONECLICK/RESULT.md` historical V3 WAITING_GATE;
- current package selector / refresh code / manifest;
- current selected Alpha runtime files and current dual-overlay/player/enemy production assets;
- any current P0/P1 implementation owner that modifies package-selected runtime.

If a package-selected runtime implementation fix is ACTIVE, stop `WAITING_GATE` rather than packaging around it.

Proof-only tooling under `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**` is not package-selected runtime under the current selector. Its repository proof-integrity fix may proceed in parallel and must not be silently added to the player payload in this stage.

## Required work

1. Select exactly one immutable current candidate snapshot after all package-selected hard gates are green.
2. Deterministically regenerate `parallel/OWNER_ONECLICK/package_manifest.json` from the selector; do not hand-edit hashes.
3. Pin every selected payload blob exactly to the chosen source commit.
4. Ensure current player-head warning and enemy `1P/2P/3P` production assets required by V1 are selected through the existing package policy where applicable.
5. Run package integrity checks for stale/mutated payload rejection.
6. Run Windows OneClick validation for:
   - Chinese path;
   - spaces in path;
   - UTF-8 output;
   - Python/py launch behavior;
   - atomic staging/current pointer switch;
   - last-known-good preservation;
   - partial/failed update rollback/fail-closed behavior.
7. Preserve exact safety expectations: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.
8. Do not modify Alpha/Transport/PYLAUNCH/Recorder implementation merely to make packaging pass.
9. Do not start Browser/WOF.

## Drift rule

Immediately before final PASS, re-read current `main` and compare package-selected source blobs to the immutable candidate. PM/result/claim/proof-only commits that do not alter selected payload do not invalidate the candidate. Any selected runtime drift requires a fresh deterministic candidate or `WAITING_GATE/BLOCKED`.

## Output

Update the OneClick result/manifest/package evidence only within the allowed packaging lane and claims.

## Success

`PASS — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V4 — IMMUTABLE PLAYER-TEST CANDIDATE READY FOR BOUNDED REAL WOF ACCEPTANCE`

Owner action after PASS: **RUN ONE BOUNDED REAL WOF PLAYER-TEST ACCEPTANCE SESSION**.

## Failure

`WAITING_GATE — OWNER ONECLICK V4 — <precise unmet hard gate>`

or

`BLOCKED — OWNER ONECLICK V4 — <precise packaging/integrity defect>`

## Dedup

Strict canonical dedup v2. If equivalent current V4/successor packaging already PASS, stop complete-safe; if already claimed, stop duplicate-safe.
