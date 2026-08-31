# EFIELD Round 005 — executor cursor and timer-control mode

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Questions

1. Is `+0x2F..+0x32` sufficiently established as a flagged executor record cursor rather than unrelated bytes?
2. Is `+0x35` part of the `+0x34` countdown width, or a separate control/mode state?

No new capture was queued.

## Field 1 — `+0x2F..+0x32`

**Operational name:** flagged logical script/animation executor record cursor
**Width:** `U32 BE`
**Observed domain:** 178 raw U32 values in the seven-run type-present corpus; dominant family `0x0200xxxx` plus embedded flag variants
**Classification:** `CONFIRMED`

### Direct evidence

The byte-lane structure itself requires the 32-bit interpretation:

- `+0x2F` alone is constant `0x02` over all 60,271 type-present samples;
- `+0x30` carries a small flag-like domain (`00,04,08,10,14,18`);
- `+0x31/+0x32` provide the varying address/record payload;
- the U32 BE view yields 178 distinct values and 5,540 changes.

A mask of embedded bits `0x001C0000` exposes a strongly quantized logical cursor:

- logical changes: `5,539`;
- exact logical `+0x0A`: `4,323 / 5,539 = 78.05%`;
- logical `-0x32` occurs 352 times, exactly five 10-byte records backward;
- repeated larger branches preserve 10-byte-aligned record topology.

The cursor is not inferred from arithmetic alone. Destination records predict the executor phase tuple `(0x6C,0x70,0x72,0x73,0x77)` with cross-run replication:

- leave-one-run-out sequential `+0x0A` destination events: `4,820`;
- logical-destination model coverage `4,819/4,820 = 99.979%`;
- accuracy on covered `4,818/4,819 = 99.979%`;
- most individual run holdouts are 100%; the only observed covered error is a one-frame exceptional phase initialization.

The neighboring confirmed dwell byte independently validates record progression:

- before logical `+0x0A`, `+0x34 <= 2` in `4,206/4,323 = 97.29%`;
- after the step `+0x34` generally reloads into a record-specific dwell value;
- while logical cursor is stable, `+0x34` overwhelmingly decrements.

Embedded flag bits are meaningful execution modifiers rather than noise: retaining them raises steady-state phase-tuple modal purity from `96.31%` for logical cursor alone to `97.30%` for raw/logical+flag conditioning, and specific flag values have repeatable phase distributions.

### Known limits

- `cursor` is an operational structural name; the exact ROM table ownership / source routine is not proven by RAM observation alone.
- Not every transition is sequential `+0x0A`; loops, branches and bank/flag changes are normal and repeatedly observed.
- One destination can show a one-frame exceptional post-arrival phase before settling, so the cursor does not imply all phase bytes update atomically at capture time.

**Status:** `CONFIRMED`

---

## Field 2 — `+0x35`

**Operational name:** executor dwell/control-mode byte adjacent to `+0x34`
**Width:** `U8`
**Observed domain:** exactly `0x00`, `0xFF`, `0x01`, `0x02`, `0x04`
**Classification:** `CONFIRMED` as a separate control/mode field; exact mode meanings remain unresolved

### Direct evidence

Across the seven-run type-present corpus:

- samples: 60,271;
- transitions: 1,024;
- dominant values: `00` 49,787; `FF` 7,471; `01` 2,598; `04` 240; `02` 175;
- dominant transitions include `00->FF` 353, `FF->00` 237, `02->00` 128, `FF->02` 74, `00->01` 67 and `00->02` 52.

It is not the low byte or high byte of a 16-bit countdown with `+0x34`:

- among 53,128 same-type, cursor-stable transitions, `+0x35` is unchanged in 52,994;
- meanwhile `+0x34` performs 19,928 `-1`, 6,372 `-2`, 338 `-3`, plus smaller decrement classes;
- the common joint changes are `(34 N,35=0) -> (34 N-1,35=0)`, repeated thousands of times;
- there is no carry/borrow pattern required by a conventional U16 timer.

Its changes instead align with executor-mode boundaries:

- `00->FF` occurs 251 times on logical cursor `+0x0A` steps;
- `FF->00`, `01->FF`, `04->00` also repeatedly coincide with cursor advances;
- `FF->02`, `00->01`, `00->02` are enriched at coarse `+0x73` family transitions;
- the same five-value state machine repeats across runs and many records.

This establishes an independent U8 control/mode role in the dwell/executor neighborhood even though the behavioral meaning of each code is not decoded.

### Known limits

- Do not call `+0x35` a second timer or timer high/low byte.
- `00/FF/01/02/04` meanings are not assigned to attack stages, waits, loops, or animation behavior without a direct discriminator.
- The field can change while `+0x34` holds or changes; no single deterministic mapping `35 -> dwell` exists.

**Status:** `CONFIRMED`

## Rejected interpretation

`U16(+0x34..+0x35)` as a simple countdown is **REJECTED**. The decrement behavior resides in `+0x34`; `+0x35` is a sparse independent five-state control/mode field.

## Next bounded question

Proceed to attack/action/state priority:

> Which fields form the repeatable coarse/fine executor phase hierarchy, without claiming visual hit/onset semantics?

Start with `+0x6C -> +0x73` and `+0x70 -> +0x77`, then test `+0x72` as the remaining strongly attack-coupled companion.

## Evidence sources

- bridge `results/efield/POINTER_RECORD_MASK.md`
- bridge `results/efield/POINTER_PHASE_HOLDOUT.md`
- bridge `results/efield/POINTER_FLAG_SEMANTICS.md`
- bridge `results/efield/TIMER_SEMANTICS.md`
- bridge `results/efield/TIMER_WIDTH_3435.md`
- bridge `results/efield/TIMER_MODE_35.md`
