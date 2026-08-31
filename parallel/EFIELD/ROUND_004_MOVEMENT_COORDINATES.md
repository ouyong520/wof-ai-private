# EFIELD Round 004 — movement / coordinate fields

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Question

> Which enemy fields carry coordinate motion, and which fields are specifically tied to horizontal locomotion rather than attack/executor state?

No new capture was queued. Existing seven-run raw and movement-conditioned analyses were used.

## Field block 1 — `+0x07..+0x0A` / `+0x0B..+0x0E`

**Operational interpretation:** two signed fixed-point coordinate-bearing blocks used successfully as orthogonal movement deltas
**Width candidate:** `S32 BE` at `+0x07` and `+0x0B`, with active payload concentrated in interior bytes
**Classification:** `STRONG_CANDIDATE`, not `CONFIRMED`

### Evidence

The retained movement analysis computes same-type per-frame deltas as signed 32-bit BE values at `+0x07` and `+0x0B`, and obtains a coherent two-axis partition:

- no motion: 15,497 transitions
- first-axis only: 927 right + 901 left
- second-axis only: 1,157 up + 1,048 down
- diagonal combinations: 837 / 506 / 366 / 342 transitions

Independent control fields validate that the partition is meaningful rather than arbitrary byte noise:

- `+0xB9` changes only `7/15497 = 0.045%` in no-motion samples, `1/1157` in pure second-axis-up, and `0/1048` in pure second-axis-down;
- the same byte changes about 45% during pure first-axis left/right and 77–99% during diagonal motion;
- `+0xBB` has zero changes in all 15,497 no-motion and all 2,205 pure second-axis samples, but changes repeatedly during first-axis motion.

Byte-level change localization is also consistent with fixed-point coordinate payloads rather than independent state bytes:

- within the first block, `+0x07` and `+0x0A` are constant in the movement-selectivity pass while `+0x08/+0x09` carry the dynamic payload;
- within the second block, `+0x0E` is constant, `+0x0C/+0x0D` carry most dynamic payload, and `+0x0B` changes sparsely as an upper/page component;
- typical deltas are strongly quantized (e.g. 65,536 / 131,072 / 196,608 units in the current S32 representation), consistent with fixed-point packing.

### Why not CONFIRMED yet

The existing EFIELD corpus provides self-consistent motion axes but no independent enemy-world-coordinate ground truth that fixes:

- which block should receive the final semantic labels X vs floor-depth/Y in game-space;
- whether the minimum authoritative representation should be the entire S32 block or a narrower packed fixed-point subfield;
- exact scale / fractional-bit interpretation.

Therefore the coordinate-bearing role and two-axis independence are strong, but the final X/Y naming and width remain unresolved.

**Status:** `STRONG_CANDIDATE`

---

## Field 2 — `+0xB9`

**Operational name:** horizontal-locomotion cyclic phase counter
**Width:** `U8`
**Observed domain:** at least `0x00..0x08` in the retained movement corpus
**Classification:** `CONFIRMED`

### Direct evidence

Across repeated same-type motion transitions:

- no-motion change rate: `7/15497 = 0.000452`;
- pure second-axis movement: `1/1157` up and `0/1048` down;
- pure first-axis movement: `417/927 = 44.98%` right and `406/901 = 45.06%` left;
- diagonal movement: `76.70%` to `99.12%` depending direction.

The transitions are not merely binary movement flags; they form repeated cyclic phase chains on both horizontal signs, including:

- `04->03`
- `03->02`
- `02->01`
- `01->04`

and extended `08->07->06->05->04` sequences.

A separate movement-vs-attack discriminator gives `+0xB9`:

- movement support `0.514537`;
- attack-transition support only `0.003764`;
- movement selectivity ratio `136.659`;
- 6,423 total active changes in the analyzed six-run pass.

This repeated axis control and cyclic transition topology establishes an operational horizontal locomotion phase/counter role without relying on a single correlation.

### Known limits

- The byte is not a direct movement-active boolean: nonzero phase values can remain latched while position is momentarily stationary.
- The phase does not encode left versus right directly; both signs use similar descending/cyclic chains.
- Exact animation-frame meaning and visual sprite mapping are not claimed.

**Status:** `CONFIRMED`

---

## Field 3 — `+0xBB`

**Operational name:** horizontal-locomotion decrementing step/countdown state
**Width:** `U8`
**Observed domain:** broad small-count domain, including `0x00`, `0x01..0x14` and larger recurrent values such as `0x2E`, `0x32`, `0x3E`
**Classification:** `CONFIRMED`

### Direct evidence

Axis controls are exceptionally clean:

- no-motion: `0/15497` changes;
- pure second-axis-up: `0/1157` changes;
- pure second-axis-down: `0/1048` changes;
- pure first-axis-right: `71/927` changes;
- pure first-axis-left: `80/901` changes;
- all diagonal classes also contain repeated changes.

When the field changes during first-axis motion, its transition shape is overwhelmingly decrementing:

- right-only: `67/71 = 94.37%` exact -1, `94.37%` decreasing;
- left-only: `74/80 = 92.50%` exact -1, `95.00%` decreasing;
- diagonal classes: roughly `86.5–94.0%` exact -1 and `90.6–95.0%` decreasing.

Movement-vs-attack control gives:

- movement support `0.117822`;
- attack support `0.001673`;
- movement selectivity ratio `70.386`.

The combination of zero vertical/control changes, repeated horizontal occurrence, and deterministic decrement shape supports the operational countdown/step-state interpretation.

### Known limits

- It is not a universal movement timer and does not decrement on every moving frame.
- It can hold a nonzero value while coordinates are stationary.
- Its exact consumer and reload trigger are not decoded; `step/countdown state` is intentionally narrower than a claim about animation or physics timing.

**Status:** `CONFIRMED`

## Round 004 conclusion

The horizontal locomotion subsystem is now materially separated from the attack/executor subsystem:

- `+0xB9` = confirmed horizontal locomotion cyclic phase counter;
- `+0xBB` = confirmed horizontal locomotion decrementing step/countdown state;
- the two coordinate-bearing blocks are strong but remain unpromoted until final axis label / minimum-width / scale are independently discriminated.

A generic capture would not resolve that remaining coordinate ambiguity. Do not queue one.

## Next bounded question

Proceed to timer / executor priority:

> Is `+0x2F..+0x32` sufficiently established as the executor record cursor, and what is `+0x35` relative to the already-confirmed `+0x34` dwell countdown?

Use existing record-residence, pointer-mask, holdout and timer-mode evidence first.

## Evidence sources

- bridge `results/efield/VELOCITY_PHASE.md`
- bridge `results/efield/MOVEMENT_CYCLE.md`
- bridge `results/efield/MOVE_ATTACK.md`
- bridge `results/efield/LAG_MIRRORS.md`
- GEO `parallel/GEO/P1_XY_FRONTIER.md` read-only only as a caution that player and enemy layouts must not be numerically conflated
