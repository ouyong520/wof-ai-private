# EFIELD Round 007 — second fine/coarse phase projection

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Question

> Do `+0x70` and `+0x77` form the second repeatable fine-to-coarse executor phase projection, and what can be said safely about `+0x72`?

No new capture was queued.

## Field 1 — `+0x70`

**Operational name:** second fine executor / attack-associated phase code
**Width:** `U8`
**Observed domain:** exactly ten values in the retained type-present corpus: `00,10,28,58,70,78,80,A0,D8,F8`
**Classification:** `CONFIRMED`

### Direct evidence

The byte has a stable repeated state topology across the retained corpus. Representative full-corpus counts include `A0:24997`, `00:27024`, `F8:3358`, `10:1655`, `80:1162`, `D8:1114`, `58:624`, `28:295`, `78:28`, `70:14`.

Its values deterministically project to the coarse byte `+0x77` in the retained corpus:

- `70=00 -> 77=00`
- `70=A0 -> 77=0C`
- `70=F8 -> 77=0A`
- `70=D8 -> 77=14`
- `70=10/28/58/80/70/78 -> 77=0B`

Several different fine codes therefore collapse to the same coarse family while other fine codes uniquely select their own family. The common transition graph repeatedly moves among these states, including `00<->A0`, `00<->F8`, `F8->10`, `80->D8`, `F8->28`, and short `70/78` boundary paths.

Independent controls separate this from movement state:

- movement-vs-attack analysis gives attack support about `0.9385` and movement support about `0.0126`;
- the confirmed record cursor repeatedly predicts the joint phase tuple containing `+0x70` at record arrivals;
- phase episode analysis shows long repeatable `A0` dwell and shorter subordinate states.

Width is U8: adjacent `+0x71` is an independently dynamic three-valued byte and combining it with `+0x70` does not produce a simpler single quantity.

### Known limits

- Fine phase codes are not named startup/hit/recovery/ACTIVE.
- `+0x70` can be zero while the enemy remains type-present and executing.
- Exact gameplay meaning of each fine code remains unresolved.

**Status:** `CONFIRMED`

---

## Field 2 — `+0x77`

**Operational name:** second coarse executor / attack-family phase code
**Width:** `U8`
**Observed domain:** exactly `00,0A,0B,0C,14`
**Classification:** `CONFIRMED`

### Direct evidence

The field is the deterministic coarse projection of `+0x70` listed above. Representative retained-corpus counts are dominated by `0C`, `00`, `0B`, `0A`, and `14`, with repeatable transitions such as `00<->0C`, `00<->0A`, `00<->0B`, `0B->14`, and `14->00`.

The relationship is structurally many-to-one rather than a loose correlation: several fine `+0x70` codes map to `0x0B`, while the other coarse values have stable corresponding fine-state families.

`+0x77` is also part of the same record-driven joint phase tuple predicted at high cross-run accuracy by the confirmed executor cursor.

Width is U8: `+0x76` is constant zero in the width-refinement corpus and extending leftward only adds padding; no adjacent byte participates as a conventional U16 state value.

### Known limits

- `+0x77` is not a universal attack-active boolean.
- Coarse family values are not assigned visual or hitbox semantics.
- It is a second hierarchy distinct from `+0x6C -> +0x73`; neither pair should be collapsed into the other.

**Status:** `CONFIRMED`

---

## Field 3 — `+0x72`

**Operational name:** executor joint-phase payload / companion state
**Width:** `U8`
**Observed domain:** 16 values in the retained corpus, including `D8,00,E8,38,F0,40,48,18,08,30,88,50,20,60,70,78`
**Classification:** `STRONG_CANDIDATE`

### Evidence

`+0x72` is one of the most tightly record/attack-coupled bytes in the object:

- in the movement-vs-attack discriminator it has attack support `1.0` and movement support about `0.0155`;
- it changes 1,026 times in the earlier width-refinement subset and participates in stable recurrent sequences such as `E8<->D8`, `E8<->F0`, `38->40->48`, `18->08`, and `30->08`;
- the full joint state `(6C,70,72,73,77)` is predicted by the confirmed logical record cursor with high steady-state purity and near-perfect sequential-destination holdout accuracy;
- particular `+0x72` values repeatedly occur in stable joint signatures, e.g. `D8` with the dominant `E0,A0,*,0A,0C` core, `E8` with the `40,00,*,1B,00` family, and `88` with the long interior `90,00,*,0B,00` state.

### Why not CONFIRMED semantic naming

Unlike the two proven fine-to-coarse pairs, the current evidence does not isolate one independent semantic dimension for `+0x72`. Its state is highly structured but appears jointly constrained by the other phase bytes and record identity. Calling it action, body, animation frame, damage state, or another specific concept would exceed the evidence.

**Status:** `STRONG_CANDIDATE`

## Round 007 conclusion

The second deterministic hierarchy `+0x70 -> +0x77` is formally locked. `+0x72` remains a strongly established executor-phase companion but is intentionally not given a narrower gameplay semantic name.

## Next bounded question

Proceed to high-value instance metadata:

> Which fields remain constant for an enemy instance/type episode and are reinitialized on replacement strongly enough to be formalized as instance/profile metadata?

Prioritize `+0xB4` and `+0xB6`; evaluate `+0xB0` only if it survives the same controls.

## Evidence sources

- bridge `results/efield/STATE_VALUES.md`
- bridge `results/efield/ATTACK_CYCLE.md`
- bridge `results/efield/PHASE_BOUNDARIES.md`
- bridge `results/efield/WIDTH_REFINEMENT.md`
- bridge `results/efield/MOVE_ATTACK.md`
- bridge `results/efield/POINTER_PHASE_MAPPING.md`
