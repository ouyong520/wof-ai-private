# Unified Live Proof Recorder Authority Generation — Fresh Independent QA Result

Date: 2026-09-02  
Stage: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V1`

## Verdict

**BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY GENERATION FRESH QA — P1 generation rollover is not revoked at child-start boundary; stale prior-generation heartbeat can still renew authority before the new reader binds generation**

Owner action: **NO**.

No Owner Browser/WOF run was requested or required.

## Current-head / production pin

Fresh QA was claimed from main start HEAD:

- `922fe72ad518a6e2ac1d850f56359a468e02725a`

The repository advanced only through PM/QA claim/result changes while this check ran. The production target remained unchanged at the tested QA head `b2bb9a234163f50337bd731e389d703e1e92747c`:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`: blob `0ed41e4afb1a6a740315f356672df019ff3a15d3`
- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof_base.py`: blob `0d9010007910f58b77c64fde98264697191bb679`

The implementation commit under review remains:

- `443eca7b591fa2331e71d2bd6e91643b90b9765d` — `live-proof: bind Recorder authority to runtime generation`

## Independent fresh QA artifacts

Created under the allowed QA-only boundary:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/test_recorder_authority_generation_adversarial.py`
  - commit `67129863755c16a06c60960ee8798da85de5fb98`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/run_qa.py`
  - commit `b2bb9a234163f50337bd731e389d703e1e92747c`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/RESULT.json`
  - machine-readable blocker evidence

The fixture imports the real repository `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`; it does not copy the implementation author's generation regression tests.

## Deterministic blocker

The required semantics say that when generation 2 starts, generation-1 authority/freshness must become invalid **immediately**, before generation-2 admission and before any delayed generation-1 reader output can renew authority.

Current implementation does not make generation activation/revocation occur at the child-start boundary:

1. `start_child()` calls the base child starter, increments `_child_generation_counter`, attaches `_wof_authority_generation` / `_wof_authority_generation_order` to the returned process, and returns it.
2. `start_child()` has no `RecorderEvidence` argument and does not revoke or advance `evidence.source_generation`.
3. The generation switch is deferred until the new Recorder `reader()` begins and calls `evidence.begin_source_generation(token, order=order)`.
4. The real `run_live()` ordering is likewise `recproc = start_child(...)` first and only afterward `threading.Thread(target=reader, ...).start()`.

Therefore there is a real authority window after the new child generation has started but before the new reader has entered its generation-binding code. During that window, generation 1 is still the exact active `source_generation` and its heartbeat is still accepted by the strict path.

### Fresh adversarial sequence

The independent fixture models the exact boundary:

1. allocate/bind generation 1;
2. accept generation-1 admission + trusted heartbeat;
3. confirm `current_healthy=true`;
4. call current `start_child()` to start/allocate generation 2 with a strictly newer order;
5. do **not** enter generation-2 `reader()` yet;
6. replay a delayed generation-1 trusted heartbeat.

Source-exact isolated execution of the current logic produced:

```text
after generation-2 start:
  sourceGeneration = generation-1
  admitted = true
  currentHealthy = true
  authorityGeneration = 1

after delayed generation-1 heartbeat:
  sourceGeneration = generation-1
  admitted = true
  currentHealthy = true
  authorityGeneration = 2
```

That is a direct violation of required cases 2 and 3: generation 1 did not lose authority at generation-2 start, and its delayed heartbeat renewed the authority freshness/generation after the newer child already existed.

A control vector in the fresh fixture confirms that once the generation-2 reader finally enters, `begin_source_generation()` does revoke generation 1. The blocker is precisely that this happens **too late**: reader entry is being used as the authority rollover boundary instead of child-generation start.

## Why implementation-authored tests missed it

The existing implementation regression `test_restart_rollover_revokes_old_generation_immediately` directly calls:

`recorder.begin_source_generation("generation-2")`

before testing the stale generation-1 heartbeat. That proves behavior only **after** the new generation is already bound in `RecorderEvidence`; it does not test the real orchestration interval between `start_child()` returning generation 2 and the generation-2 reader entering `begin_source_generation()`.

The fresh QA fixture specifically attacks that missing boundary.

## Regression disposition

Per the QA prompt, a real implementation blocker requires recording it and stopping without repairing implementation in this thread.

Therefore the runner is prepared to execute, after the fresh generation boundary is green:

- existing Recorder heartbeat independent QA;
- implementation generation regression;
- Unified live-proof regression;
- current Unified preflight regression;
- previous freshness QA;
- previous fail-closed QA.

Those suites are marked `NOT_RUN_STOP_ON_BLOCKER` in the machine result because the first required safety property already fails. This is not a claim that those suites regress; they were not reached after the deterministic P1 stop condition.

## Safety / Owner invariants

This QA thread did not modify implementation, PYLAUNCH, WOF052L Recorder, Alpha Transport, HUD, Browser production rules, or Owner OneClick.

No game RAM write or input injection was performed by this repository-side QA, and no Browser/WOF Owner run was needed. The production implementation still exposes the previously documented read-only / RAM-writes-0 / input-injection-disabled / `longCaptureAutoStarted=false` surfaces, but the full regression suite was intentionally not promoted to PASS because the generation safety blocker stops the stage first.

## Delivery reassessment

- **Current-head Unified preflight:** **NOT unblocked** by this QA.
- **Alpha Formal Integration fresh QA:** **NOT unblocked** by this Recorder generation gate.
- **Owner action:** **NO**.

The implementation needs a fresh fix stage that makes the newer Recorder child generation revoke/bind authority at an atomic generation-start boundary, not only when the new reader later begins consuming stdout. After that, this fresh QA must be rerun from a new stage.

## Stop condition

**BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY GENERATION FRESH QA — P1 generation rollover is not revoked at child-start boundary; stale prior-generation heartbeat can still renew authority before the new reader binds generation**
