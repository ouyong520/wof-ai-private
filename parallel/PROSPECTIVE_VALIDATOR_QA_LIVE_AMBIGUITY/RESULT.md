# WOF Prospective Validator Live Ambiguity P0 — Fresh Independent QA Result

stageId: `PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_QA_V1`

## Verdict

**PASS — PROSPECTIVE VALIDATOR LIVE AMBIGUITY P0 FRESH QA**

Fresh QA independently re-read the current implementation and prior blocker; the fix thread's READY verdict was not accepted as proof. No P0/P1 blocker remains in the repository-side surface required by this stage.

Owner Browser run: **NO**.
Owner action: **NO**.

## Prior P0 re-test

The prior blocker was a positive live-topology audit gap: after a room had been proved unique, ownership could become shared/cross-page ambiguous while the old room continued `drain()/ingest()` until the next full audit.

Current control flow closes that admission gap:

- `AUDIT_LIVE_TOPOLOGY_INTERVAL = 0.0` remains explicit;
- if `now - endpoint.last_discovery < DISCOVERY_INTERVAL`, `discover_and_poll()` returns before any prospective drain, so the scheduling interval is not an evidence-admission interval;
- every cycle that can admit prospective evidence performs `discover_candidates(..., skip_page_ids=set())` first;
- ambiguity is resolved before the drain loop and affected rooms are finalized with `worker-association-ambiguous`;
- surviving rooms must have their exact current `(pageTargetId, workerTargetId)` present in the fresh scan's `proven_pairs`; absence finalizes the room as `worker-association-unverified` before drain;
- topology-scan exceptions finalize all live rooms as unverified and return, so buffered evidence cannot be deferred to a later successful scan;
- there is one real `globalThis.__WOF_PROSPECTIVE_VALIDATOR.drain()` call in the live V2 admission control flow, after those guards.

Therefore there is no positive-duration interval in which post-ambiguity evidence can be admitted: between admission cycles there is no drain; at the next admission cycle, the full topology and exact pair are freshly re-proved before drain.

## Independent adversarial fixtures

Fresh QA added two fixtures under this lane only:

1. `fixtures/topology_transition_adversarial.json`
   - `t=200.0`: live shared-worker room and unrelated control room are uniquely proved;
   - `t=200.125`: a second page appears for the shared Worker;
   - `t=200.5`: intermediate poll admits nothing (`drain=0`, `ingest=0`);
   - `t=201.01`: next admission cycle performs a full scan with empty skip set; the affected shared-worker room is finalized before any drain and admits zero evidence, while the unrelated exact-pair room remains independently admissible.

2. `fixtures/cleanup_finalization_adversarial.json`
   - remote `stop()` returns deliberately forbidden result/pending markers;
   - the Live V2 finalizer calls `stop()` for cleanup but discards its return value;
   - forbidden stop payload markers do not enter prospective traces/counters;
   - only pending state that had already been admitted after a prior fresh topology proof may be finalized as censored.

The repository-equivalent timing/cleanup harness for these fixtures passed. The reproducible private-repo import suite is committed as `test_live_ambiguity_fresh_qa.py`.

Execution note: this connector session provides private GitHub read/write access but not a checked-out private-repository process runner, so the committed repo-import unittest file was not directly executed from the connector session. PASS is based on fresh source/control-flow audit plus independently executed repository-equivalent adversarial models, matching the repository-side QA mode used for this fix family; the limitation is recorded in `QA_RESULT.json` rather than hidden.

## Required matrix

1. **PASS** — unique live room -> shared/cross-page ambiguity finalizes/censors affected room before later prospective admission.
2. **PASS** — no positive-duration audit gap can admit post-ambiguity evidence.
3. **PASS** — current exact `(pageTargetId, workerTargetId)` pair is freshly re-proved before every prospective admission cycle.
4. **PASS** — topology scan failure / unverified exact pair fails closed and cannot defer buffered evidence for later ingest.
5. **PASS** — remote cleanup/stop payload cannot bypass fresh topology authority.
6. **PASS** — two pages / two distinct Workers remain independently admissible when each exact pair is freshly proved.
7. **PASS** — shared Worker cross-page ambiguity rejects all affected relations; unrelated room remains isolated/admissible.
8. **PASS** — discovery diagnostics remain `discovery-only` and validator counters/gates separate them from prospective evidence.
9. **PASS** — all conservative gates remain enforced: `minProspectiveSignals`, `minProspectiveRooms`, `requireZeroHardMiss`, `minDistinctTargets`, `minObservedTypes`, `requireLifecycleReset`; unknown gate fails closed during manifest validation.
10. **PASS** — a passing validator verdict remains `PROSPECTIVE_PASS_RESEARCH_ONLY`; `productionPromotionAllowed=false`.
11. **PASS** — exact World 921031 SHA identity, loopback/exact-port endpoint confinement, parent/parentFrame association authority, and cross-page relation safety remain intact.
12. **PASS** — `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `windowWorkerReplacement=false`; discovery CDP allowlist has no gameplay `Input.*`, no `Runtime.callFunctionOn`, no page preload injection, and the prospective probe contains no Worker/ObjectURL rewrite path.

## Audited SUT snapshot

Freshly re-read after concurrent repository activity:

- `live_validator_v2.py` blob `512c6635d2a8c1bf99cd7f4a5e3f9e45b9b2b3d0`
- `discovery_v2_hardening.py` blob `959cf2d4dbfecc2031b1e3feee141a3dd06f9b01`
- `validator.py` blob `2e1d574574205b176725a50edd7ec062ab100d40`
- `discovery_v2.py` blob `37b0bd95cf2882b46ef6291a53fd46b6d268c898`
- `live_validator_v2_hardened.py` blob `393b6f34b3bf9f0b13e3d644414a0ea3a392299a`

These are the same audited implementation blobs; no SUT file was modified by this QA stage.

## Write scope

This stage wrote only:

- `parallel/PROSPECTIVE_VALIDATOR_QA_LIVE_AMBIGUITY/**`
- `parallel/PM/STAGE_CLAIMS/PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_QA_V1.json`

It did **not** modify `parallel/PROSPECTIVE_VALIDATOR/**`.

## Stop condition

**PASS — PROSPECTIVE VALIDATOR LIVE AMBIGUITY P0 FRESH QA**
