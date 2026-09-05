# Alpha V1 P22 — Dynamic Actor State Coverage Acceptance

P22 is a **passive, fail-closed evidence recorder/analyzer** for the final Alpha acceptance session. It adds no game-memory reader, renderer discovery, coordinate model, screenshot tracker, projection fallback, identity heuristic, or input injection.

## Authority consumed

P22 accepts only evidence that already passed the maintained canonical path:

- exact P19/P21 candidate identity (`sourceCommit`, `packageVersion`, candidate SHA-256);
- `AlphaRuntimeManager.status()` or `CanonicalRuntimeCoordinator.status()`;
- P12 actor + generation records carried by the P10/P9 runtime bridge;
- P10 `wof-render-object-anchor-v1` READY/SUPPRESSED results on native `384x224`;
- optional P18 `wof-alpha-canonical-draw-evidence-v1` acknowledgement snapshots;
- optional existing field-adapter `wof-alpha-v2` semantic envelopes for only:
  - `player-head-spatial`: `P1/P2/P3.present` lifecycle semantics;
  - `enemy-target-markers`: projection-independent `target7E` `0/4/8 -> P1/P2/P3` semantics.

Field-adapter `x/y/z`, projection objects, screenshot pixels, row order, proximity, stale generations, and any guessed address are deliberately ignored and never enter the P22 spatial or identity ledger.

## Callable same-session seam

The main API is `DynamicActorStateCoverageRecorder.record_cycle(...)`. A P21/P17 same-session caller can pass the current canonical runtime status plus the already-available semantic envelopes and P18 snapshot on each bounded cycle. P22 requires no permanent install change and no Owner calibration.

For process-level orchestration, `dynamic_actor_state_coverage.py` consumes a `wof-alpha-p22-cycle-bundle-v1` file whose cycles **nest the original accepted evidence objects**. The bundle is a transport container, not a new authority. The Windows wrapper accepts the bundle path as argument 1 or environment variable `WOF_ALPHA_P22_INPUT`; output defaults to `%USERPROFILE%\Documents\WOF_RESULTS`.

```text
parallel\OWNER_ACCEPTANCE_STATE\WOF_ALPHA_DYNAMIC_STATE_COVERAGE.cmd <same-session-bundle.json> [output-dir]
```

The Owner should not hand-author this bundle. P21/P17 orchestration supplies it while the Owner only plays normally during the later real acceptance run.

## Coverage semantics

Every matrix row is one of:

- `OBSERVED_PROVEN`
- `OBSERVED_PARTIAL`
- `NOT_OBSERVED`
- `UNPROVEN_SIGNAL`
- `SUPPRESSED_SAFELY`

The analyzer covers same-generation movement, renderer-qualified body geometry changes, generic vertical movement, explicit visibility suppression/reentry, player generation rebuilds, P2/P3 presence transitions, enemy generation rebuilds, projection-independent enemy target switches, current-generation target-label draw linkage, and runtime/renderer replacement.

`HIT`, `DOWN`, `RECOVERY`, `JUMP`, and `DEATH` are **never inferred from geometry, velocity, animation-looking rectangles, warnings, RAM fields, or screenshots**. The maintained runtime currently exposes no exact named-state classifier that P22 is authorized to consume, so these remain `UNPROVEN_SIGNAL`. Generic vertical/body changes may still be recorded without renaming them.

Enemy first sighting is not promoted to an exact spawn edge, and later absence is not promoted to disappearance without an explicit lifecycle signal. Those remain partial/not-observed rather than guessed.

## Stale/replacement rules

- An authority/runtime/renderer identity is a hard track namespace.
- Once replaced, the old identity is retired; re-entry is rejected as stale.
- Once an actor generation is replaced, a later READY row from the retired generation is rejected.
- SUPPRESSED old-generation evidence may be retained only as suppression evidence and carries no P10 position.
- P18 evidence with a mismatched page/authority/runtime/renderer identity is not linked.
- P18 acknowledgement proves maintained primitive execution only; it never proves visible pixels or correct on-screen following.

## Core acceptance set

The small automatic core is intentionally bounded:

1. P1 same-generation canonical anchor movement;
2. P1 renderer-qualified body geometry change;
3. when an enemy semantic target is observed, current-generation enemy label acknowledgement continuity with `0/4/8 -> 1P/2P/3P`.

Rare named states are useful gaps, not mandatory blockers. `CORE_COVERAGE_READY` is still only **automatic dynamic-evidence coverage**, never Owner visual PASS.

## Outputs

P22 writes atomically:

- `ALPHA_DYNAMIC_STATE_COVERAGE.json`
- `ALPHA_DYNAMIC_STATE_COVERAGE.md`

The output includes exact candidate identity, bounded cycles/tracks, coverage matrix, core summary, gaps, stale-evidence rejection, suppression evidence, draw linkage, invariants, and safety. `visibleProof` is always `NOT_PROVEN` in P22; `realWofAcceptance` and `ownerVisualAcceptance` remain `NOT_RUN` for this repository implementation stage.
