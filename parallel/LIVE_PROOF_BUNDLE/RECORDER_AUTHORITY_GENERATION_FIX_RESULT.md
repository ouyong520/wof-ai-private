# Unified Live Proof Recorder Authority Generation Fix — Result

Date: 2026-09-02  
Stage: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_FIX_V1`

## Verdict

**UNIFIED RECORDER AUTHORITY GENERATION FIX READY — READY FOR FRESH QA**

Owner action: **NO**.

This fix closes the repository-side implementation defect reported by fresh QA: stale prior-generation Recorder heartbeat/admission text can no longer refresh or revive the active Recorder authority slot on the real Unified runtime path.

## Implementation

Main implementation commit:

- `443eca7b591fa2331e71d2bd6e91643b90b9765d` — `live-proof: bind Recorder authority to runtime generation`

Changed only under the allowed `parallel/LIVE_PROOF_BUNDLE/**` boundary:

- `unified_live_proof.py`
  - hardened overlay for Recorder authority generation provenance;
  - assigns an immutable token/order to each child process returned by Unified `start_child()`;
  - Recorder `reader()` binds stdout authority events to that exact child generation;
  - older readers cannot roll authority backward;
  - status exposes source/admission generation and rejected-authority diagnostics.
- `unified_live_proof_base.py`
  - source-exact frozen pre-fix implementation blob retained as the orchestration/base surface, so unrelated live-proof behavior is not duplicated or rewritten.
- `test_recorder_authority_generation.py`
  - focused generation/replay regression matrix.
- `_test_unified_live_proof_base.py` + `test_unified_live_proof.py`
  - retain the prior unified regression corpus while making fatal recovery explicit as a **new Recorder runtime generation**, rather than an unproven same-generation text replay.

No changes were made to `parallel/PYLAUNCH/**`, `parallel/WOF052L_RECORDER/**`, `product/alpha/**`, Alpha transport, HUDANCHOR, or Owner OneClick.

## Generation authority semantics

The active Recorder runtime generation is now a first-class authority provenance boundary.

1. A real Recorder child receives one immutable generation token for its process lifetime.
2. A Recorder admission is accepted only from the active source generation and is bound to that generation.
3. A supervisor heartbeat renews authority only when its source generation matches the active admitted generation.
4. Missing or wrong generation on the strict runtime path is fail-closed.
5. A fatal event revokes both the admission and that source generation; the same generation cannot re-admit itself afterward.
6. Starting a newer child generation immediately revokes the prior current authority/freshness before any new admission is accepted.
7. Delayed/out-of-order heartbeat, admission, or fatal events from an older reader are diagnostic only; they cannot change the current authority slot or freshness clock.
8. Generic stdout remains diagnostic only and cannot renew authority.

The narrow unbound compatibility path exists only so the already-committed pre-fix QA fixture can be replayed unchanged: it permits the original single-generation positive cases but fails closed after an unbound rollover and rejects byte-identical old admission replay. The actual Unified runtime uses the strict child-generation path.

## Regression evidence

Locally executable deterministic validation after the landed blob was produced:

- exact committed hardened overlay blob `0ed41e4afb1a6a740315f356672df019ff3a15d3` syntax: **PASS**;
- exact committed generation regression blob `6fb759b51232be08bf7d0af13bfb9fbe1e7b9c1f`: **10/10 PASS**;
- auxiliary generation vectors: **7/7 PASS**;
- blocker-directed vectors copied from the fresh QA Recorder heartbeat/admission adversarial matrix: **8/8 PASS**.

The blocker-directed replay checks now confirm:

- generation-1 heartbeat replay after generation-2 admission does not advance `authorityGeneration` and does not restore `current_healthy`;
- generation-1 admission replay cannot clear a later revocation or replace the current admission;
- current-generation admission/heartbeat still renew normally;
- missing/wrong generation fails closed;
- reconnect/restart rollover revokes old authority immediately;
- delayed/out-of-order old heartbeat/admission/fatal events do not mutate generation 2;
- arbitrary stdout/CR diagnostics remain non-authoritative.

GitHub returned no commit status checks for the implementation commit. The connected execution environment also does not provide a full repository checkout/runner, so this fix stage **does not claim a complete independent fresh-QA PASS**. The already-committed fresh-QA runner should now be executed in a new QA stage against current main, including its existing heartbeat, unified live-proof, unified preflight, and previous freshness suites.

## Safety / Owner gates

Preserved invariants:

- read-only remains required;
- RAM writes remain `0`;
- input injection remains disabled;
- no `window.Worker` replacement is introduced;
- `longCaptureAutoStarted=false` remains unchanged;
- Owner double-generation/freshness gates remain in the frozen base orchestration;
- no Browser/WOF Owner run was requested or used for this repository-side fix.

## Delivery reassessment

Authoritative classification: **ACCEPTED_WAITING_GATE**.

- **P1 implementation blocker:** closed by this fix.
- **Fresh independent QA rerun:** now unblocked and mandatory as the next fresh stage.
- **Alpha critical path:** materially shortened because the Recorder prior-generation replay P1 no longer blocks repository-side live-proof QA. This does **not** yet authorize the real Owner Browser/WOF proof; fresh independent QA/preflight must first pass.
- **Owner action:** **NO**.

## Required next

Open a new fresh independent QA/retest stage against current main. Re-run `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/run_qa.py` (or an equivalent source-exact fresh runner) and only promote Owner live proof if that fresh QA and the Unified preflight gates are green.

## Stop condition

**UNIFIED RECORDER AUTHORITY GENERATION FIX READY — READY FOR FRESH QA**
