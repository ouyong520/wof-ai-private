# WOF Unified Live Proof — Recorder Authority Generation Fresh QA

stageId: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_FRESH_QA_V1`

Priority: **P0/P1 Alpha release gate**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md` before any work.

## PM reason / current upstream

This is the mandatory independent retest after `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_FIX_V1`.

At PM reconciliation baseline `a31f8940e4a7be7b18e8ad13b0754e2c00676c38`:

- fix claim is `COMPLETE` with classification `ACCEPTED_WAITING_GATE`;
- implementation commit is `443eca7b591fa2331e71d2bd6e91643b90b9765d`;
- current `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py` blob is expected to be `0ed41e4afb1a6a740315f356672df019ff3a15d3`;
- fix result explicitly says `READY FOR FRESH QA` and does not self-certify release PASS;
- historical `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_QA_V1` remains BLOCKED on prior-generation heartbeat/admission replay reviving authority. Keep that historical result unchanged.

## Dedup / claim

Re-read latest main plus all equivalent Unified Recorder generation/heartbeat QA results.

If a newer independent current-blob QA already closes the exact blocker surface, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If equivalent fresh QA is ACTIVE, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_FRESH_QA_V1.json`

with `state=ACTIVE` and exact current main start commit.

## Upstream gate

Proceed only if the generation fix claim is COMPLETE and the current Unified production blob is identifiable. If relevant production changed after the fix result, pin and test current source; do not reuse fix-stage selftests as fresh certification.

## Goal

Independently prove the real Unified runtime is generation-bound so stale Recorder text from an earlier child/runtime generation cannot refresh, revive, replace, or clear current authority.

Required attacks / positives:

1. generation-1 heartbeat after generation-2 admission does not advance current `authorityGeneration`, freshness, or health;
2. generation-1 admission replay cannot clear a newer revocation or replace current admission;
3. delayed/out-of-order old heartbeat/admission/fatal is diagnostic only against generation 2;
4. starting a newer child generation immediately revokes prior admission/freshness before new admission;
5. fatal revokes the current source generation and the same generation cannot re-admit itself;
6. missing/wrong generation fails closed on the strict runtime path;
7. generic stdout never renews authority;
8. current-generation admission + trusted supervisor heartbeat renew normally;
9. reconnect/restart generation rollover remains fail closed;
10. legacy compatibility path cannot become a bypass for the strict real runtime;
11. existing Unified preflight/freshness/heartbeat and prior live-proof regressions remain green;
12. safety remains read-only, `ramWrites=0`, no input injection, no Worker replacement, and `longCaptureAutoStarted=false`.

## Required execution

Use current source-exact independent runners. At minimum execute current equivalents of:

- `python parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/run_qa.py`;
- focused `parallel/LIVE_PROOF_BUNDLE/test_recorder_authority_generation.py`;
- current Unified Live Proof regression suite;
- current Unified preflight/freshness gates that consume Recorder authority.

The old BLOCKED QA vectors are mandatory regression inputs. A PASS must demonstrate that those exact attacks now fail closed on the real current implementation, not merely on a copied model.

Retain raw machine-readable output and exact production/test blobs.

## Read / write boundary

Read/test current repository code.

Write only:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_FRESH/**`;
- the dedicated stage claim above.

Do **not** modify:

- `parallel/LIVE_PROOF_BUNDLE/**` production implementation;
- PYLAUNCH / WOF052L Recorder / Owner OneClick / Alpha transport / HUDANCHOR;
- historical heartbeat QA claim/result.

If an implementation defect is found, stop BLOCKED and preserve exact repro. Do not repair in this QA lane.

## Downstream consumer

A PASS is consumed by:

- Owner OneClick current-head package refresh;
- Unified preflight / Alpha acceptance release gates;
- Release Freeze current-HEAD recheck.

## Drift rule

Immediately before finalizing, re-read main and exact Unified production blobs. If tested production changed, rerun or stop stale; PM-only/result-only drift may be recorded as non-invalidating only if production blobs remain exact.

## Success stop

`PASS — UNIFIED RECORDER AUTHORITY GENERATION FRESH QA — RELEASE GATE CLOSED`

Update claim COMPLETE with result path/commit, tested HEAD, current production blob(s), pass counts, old-blocker replay disposition, preflight status, and ownerAction=`NO`.

## Failure stop

`BLOCKED — UNIFIED RECORDER AUTHORITY GENERATION FRESH QA — <precise blocker>`

Update claim BLOCKED with first deterministic repro/evidence.

Owner action: **NO**.