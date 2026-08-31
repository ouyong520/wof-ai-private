# EFIELD Round 006 — coarse/fine attack-associated executor phase

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Question

> Do `+0x6C` and `+0x73` form a repeatable fine-to-coarse executor phase hierarchy, independent of any claim about visual hit/onset semantics?

No new capture was queued.

## Field 1 — `+0x6C`

**Operational name:** fine executor / attack-associated phase code
**Width:** `U8`
**Observed domain:** exactly nine values in the seven-run type-present corpus: `00,40,48,50,58,70,78,90,E0`
**Classification:** `CONFIRMED`

### Direct evidence

Across the full 60,271 type-present sample corpus the value distribution and transition topology repeat across many enemies, slots, records and runs. Representative counts include `E0:27486`, `00:15366`, `40:11432`, `50:2358`, `48:1517`, `58:1344`, `90:726`, `78:28`, `70:14`.

The field is not merely attack-correlated. It has a deterministic structural projection to the neighboring coarse family byte `+0x73` in the retained corpus:

- `6C=00 -> 73=00`
- `6C=40/48/50/58 -> 73=1B`
- `6C=E0 -> 73=0A`
- `6C=90 -> 73=0B`
- `6C=70/78 -> 73=1E`

The repeated transition graph is correspondingly hierarchical: common fine transitions such as `00->40`, `40->E0`, `E0->40`, `40->48`, `00->50`, `00->58` either move between coarse families or refine paths inside a family.

Independent executor evidence ties the phase code to script-record execution rather than to a generic motion byte:

- the confirmed `+0x2F..+0x32` record cursor predicts the full phase tuple `(6C,70,72,73,77)` with ~96.31% steady-state modal purity and ~99.98% leave-one-run-out accuracy at sequential destination arrivals;
- `+0x6C` has zero support on the clean movement-event partition and support `1.0` on the attack-field-transition partition used by the existing movement-vs-attack discriminator;
- repeated phase episodes and dwell runs show stable, recurrent state sequences, including long `E0` cores and short `70/78` boundary states.

Width is specifically U8: adjacent `+0x6D` begins the independently confirmed live-target U16 pointer, so interpreting `+0x6C..+0x6D` as one wider semantic field mixes two separately demonstrated structures.

### Known limits

- `attack-associated phase` is a structural name, not a claim that any particular value equals hitbox-active, damage onset, startup, recovery, or a visual animation frame.
- Some phase families can occur in long interior runs and some at boundaries; the exact gameplay label of each fine code is intentionally unresolved.
- WinKawaks-local semantics are not Browser/WASM offset semantics.

**Status:** `CONFIRMED`

---

## Field 2 — `+0x73`

**Operational name:** coarse executor / attack-family phase code
**Width:** `U8`
**Observed domain:** exactly `00,0A,0B,1B,1E`
**Classification:** `CONFIRMED`

### Direct evidence

Across 60,271 type-present samples the five-value domain is stable and highly populated: `0A:27486`, `1B:16651`, `00:15366`, `0B:726`, `1E:42`.

The byte is the deterministic coarse projection of `+0x6C` listed above. This is stronger than same-frame correlation: every observed fine-code family collapses to one and only one `+0x73` value, while several distinct fine codes share the same coarse value.

The coarse family also organizes repeatable multi-frame episodes:

- existing episode analysis contains hundreds of `+0x73 != 0` runs;
- common transitions include `1B<->00`, `0A<->1B`, `00<->0A`, and `0A<->0B`;
- `0B` runs are long and strongly interior-dominant in the joint-state analysis;
- `1E` occurs only in rare short states whose full joint signatures are boundary-enriched and have no interior samples in the retained boundary corpus;
- `0A` contains the dominant long-lived core state family.

The confirmed record cursor provides an independent structural anchor: logical record destinations predict `+0x73` with near-perfect cross-run destination purity, and `+0x73` participates consistently in the same repeated record/phase state machine as `+0x34` dwell countdown.

Width is U8: `+0x74` is constant zero in the retained type-present corpus, so a U16 interpretation adds padding rather than explanatory state.

### Known limits

- `+0x73 != 0` was used as an episode anchor for analysis, not proven as a universal 'attacking now' boolean.
- `00` does not mean 'inactive enemy'; enemies remain type-present and execute other states while `+0x73==0`.
- No value is promoted to visual strike/hit/recovery semantics without an independent event discriminator.

**Status:** `CONFIRMED`

## Round 006 conclusion

`+0x6C -> +0x73` is now formally locked as a fine-to-coarse executor phase hierarchy. The conclusion is intentionally structural: it resolves the state relationship while avoiding unsupported labels such as hit, ACTIVE, startup or recovery.

## Next bounded question

> Do `+0x70` and `+0x77` form the second deterministic fine-to-coarse phase projection, and where does `+0x72` sit relative to that pair?

Use the existing joint phase corpus first.

## Evidence sources

- bridge `results/efield/STATE_VALUES.md`
- bridge `results/efield/ATTACK_CYCLE.md`
- bridge `results/efield/PHASE_BOUNDARIES.md`
- bridge `results/efield/POINTER_PHASE_MAPPING.md`
- bridge `results/efield/POINTER_PHASE_HOLDOUT.md`
- bridge `results/efield/WIDTH_REFINEMENT.md`
- bridge `results/efield/MOVE_ATTACK.md`
