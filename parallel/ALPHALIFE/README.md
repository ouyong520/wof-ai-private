# WOF Alpha enemy lifecycle / slot reuse audit

Updated: 2026-09-01  
Lane: `ALPHALIFE`  
Scope: read-only audit of `product/alpha/**`; no Alpha product code changed.

## Status

**Stop condition B reached.**

The retained Browser implementation/evidence does **not** expose a Browser-proven unique enemy episode / instance identity, nor does it prove that a same-type slot replacement must present an observable `null` or type-change sample to the current 10 ms reader.

Therefore `slot + type` cannot be treated as episode identity.

The current RC1 engine can arm a watch for enemy episode A and then keep that watch when a different same-type enemy episode B occupies the same slot without an observed gap/type change. `warningRows()` then reads B's live target/coordinates while retaining A's watch provenance and age. This is the ALPHAQA-002 failure mode.

## Safety conclusion

No retained Browser evidence supports importing a hidden instance/profile field into Alpha. WinKawaks EFIELD proves that same-type replacement is real and that some profile fields change at many replacement boundaries, but those fields are not unique instance IDs and their WinKawaks offsets are not Browser release evidence.

The implementation-safe RC2 policy is therefore:

1. **Never infer episode continuity from `slot + type`.**
2. **History/edge-triggered rules require positive continuity evidence.** With the current Browser snapshot contract, continuity is unknown, so those rules must fail closed rather than evaluate an edge across two samples that may belong to different episodes.
3. **Current-level rules may remain available only as current-sample evidence.** They must not keep a warning alive after the current sample stops satisfying the exact frozen predicate; a later same-type occupant may independently satisfy the predicate, but it must be treated as fresh evidence rather than inheriting an old watch.
4. `slotGone` and `typeChanged` remain valid invalidation signals, but they are insufficient as the sole lifetime guard.
5. Target/side must continue to be read live; live retargeting is not an enemy-lifecycle identity signal.

This policy intentionally prefers silence over a potentially inherited false warning.

## Frozen-rule impact

| Frozen Alpha rule | Trigger shape | Safe with no Browser episode identity? | RC2 recommendation |
|---|---|---:|---|
| `T16_B4_DANGER_40` | entry/history | No | quarantine unless positive continuity is available |
| `T20_5136_B0_TO_B255_1250` | explicit B0 -> B255 transition | No | quarantine unless positive continuity is available |
| `D867BA_3232_TM6_220` | entry/history | No | quarantine unless positive continuity is available |
| `D8811E_3232_TM6_135` | entry/history | No | quarantine unless positive continuity is available |
| `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` | current level | Yes, with stateless/hold-only publication | publish only while exact predicate is currently true; no post-predicate carry |
| `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` | current level | Yes, with stateless/hold-only publication | publish only while exact predicate is currently true; no post-predicate carry |

“Quarantine” here means safety suppression of user-facing warning output for a rule whose correctness depends on unproven cross-sample episode continuity. It does not delete the frozen rule definition or claim the research evidence is invalid.

## Required RC2 implementation artifacts

See:

- `LIFECYCLE_AUDIT.md` — evidence and impossibility boundary
- `RECOMMENDED_INVALIDATION_POLICY.md` — implementation-ready behavior
- `RC2_REGRESSION_CASES.md` — adversarial fixtures

No new real-Browser capture is required to close ALPHAQA-002 if RC2 accepts the conservative fail-closed policy above. A Browser probe is only required if product wants to restore the four history-dependent rules without this safety quarantine.
