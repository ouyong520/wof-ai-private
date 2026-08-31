# EFIELD Field Frontier

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`

This file is the authoritative EFIELD-lane frontier from this point forward. It is discovery-only, read-only, and does not establish Browser/WASM offset equivalence or modify any Browser production rule.

## Operating rule

Each round formally resolves only 1-3 high-value enemy fields. A field must be classified as exactly one of:

- `CONFIRMED`
- `STRONG_CANDIDATE`
- `WEAK_CANDIDATE`
- `REJECTED`
- `UNKNOWN`

`CONFIRMED` requires an explicit offset, width, observed value domain, change behavior, repeated evidence across multiple events/slots/runs, and documented counterexamples/limits. Correlation alone is not sufficient for semantic naming.

Collector failures caused by fresh RAM/discovery ambiguity are acquisition-environment failures, not negative field evidence. Do not repeatedly enqueue an equivalent failed capture.

## Round 001 — three fields formally locked

### 1. `+0x24` — CONFIRMED

**Operational name:** current enemy type-present / lifecycle byte  
**Width:** `U8`  
**Observed domain:** `0x00` plus 30 observed nonzero values (31 total values in the seven-run corpus)

**What is directly established**

- Across 23,400 frames / 468,000 enemy-object samples, `+0x24` produced **74 zero->nonzero** and **74 nonzero->zero** lifecycle boundaries.
- These repeated type-present episodes occur while `+0x00` shows no transition at all, separating current object/type presence from the persistent physical-slot header layer.
- The behavior repeats across occupied enemy slots and across the retained EFIELD runs/sessions.
- Nonzero values form the current per-enemy type domain used throughout the existing type-conditioned analysis.

**Formal interpretation**

`+0x24` is confirmed as the WinKawaks-local **current type-present/lifecycle discriminator**: `0x00` marks absence of a current typed enemy episode in that slot; nonzero marks a current typed enemy episode and carries the current type code.

**Known limits / counterexamples**

- This is **not** promoted as Browser `ACTIVE` and is not an exact hitbox/damage-active field.
- A live target pointer can remain latched while `+0x24 == 0`; therefore target lifetime and type-present lifetime differ.
- Nonzero->nonzero type replacement can occur, so lifecycle cannot be reduced to only zero/nonzero edges when reasoning about object replacement.
- `+0x00` is explicitly rejected as current enemy-presence ACTIVE in the retained corpus: slots 17..19 stay `1`, slots 0..16 stay `0`, with zero transitions despite the 148 `+0x24` zero/nonzero edges.

**Status:** `CONFIRMED`

---

### 2. `+0x6D..+0x6E` — CONFIRMED

**Operational name:** materialized live player-target pointer  
**Width:** `U16 BE`  
**Observed domain:** exactly:

- `0xBE1C` = P1
- `0xBEFC` = P2
- `0xBFDC` = P3

**What is directly established**

- Across the retained seven-run corpus there are **8 pointer transitions** and all 8 are known-player retarget events.
- **6/8** occur while `+0x24` type remains unchanged, directly separating retarget from ordinary lifecycle replacement.
- The remaining two are nonzero-type->nonzero-type replacement events rather than zero/nonzero lifecycle boundaries.
- No observed target transition coincides with an ordinary `+0x24` enter/exit edge.
- On all 8 observed commits, the new `+0x6D..0x6E` value equals the post-frame association pointer at `+0x3D..0x3E`.
- In six same-type retargets, that association had already been stable for roughly 57, 217, 278, 492, 537 and 715 frames before `+0x6D..0x6E` changed, proving this field is the later materialized target layer rather than the upstream selection source.

**Formal interpretation**

`+0x6D..0x6E` is confirmed as the WinKawaks-local **materialized current player-target pointer** among P1/P2/P3.

**Known limits / counterexamples**

- It is not the upstream player-selection field; `+0xC6 / +0x3D..0x3E` can select/associate a player long before the live target commits.
- The pointer can remain latched through `+0x24 == 0`; do not infer current type presence from it.
- This does not imply Browser/WASM target offset equivalence; Browser `enemy+0x7E` remains a separate namespace.
- Only player targets P1/P2/P3 are proven in the retained corpus; no claim is made about any other pointer domain outside observed scenes.

**Status:** `CONFIRMED`

---

### 3. `+0x34` — CONFIRMED

**Operational name:** current script/animation-record dwell countdown  
**Width:** `U8`  
**Observed domain:** at least 43 values in the retained corpus; ordinary record countdowns commonly terminate at `1` or `2`, with special waits and delayed-init records extending the domain.

**What is directly established**

- The neighboring `+0x2F..0x32` U32 BE structure behaves as a flagged logical 10-byte record cursor; after flag masking, **4,323 / 5,539** logical pointer changes are exact `+0x0A` record advances.
- In **6,737** multi-frame logical-record residences, **6,684 / 6,737 = 99.21%** contain no positive `+0x34` step.
- Residence terminal values are concentrated at `1` (**4,410** cases), `2` (**1,191**) and `3` (**446**).
- Before sequential `+0x0A` record advance, `+0x34 <= 2` in about **97.29%** of the original sequential-step pass.
- Record-local reload ceilings are cross-run stable: for 4,323 sequential arrivals, leave-one-run-out coverage is 4,321/4,323 and only **11/4,321 = 0.25%** of holdout reloads exceed the ceiling learned from the other runs.
- Multiple repeatable wait records stall at terminal value `1` for tens of frames before branch/advance, proving that reaching the terminal value does not itself force immediate exit.
- A narrow `0x73=1B` family has **52** repeated residences entering at `+0x34=8`, then loading `9..17` after 1-3 frames before resuming countdown. This is a documented delayed-initialization exception, not a contradiction to the countdown role.

**Formal interpretation**

`+0x34` is confirmed as the WinKawaks-local **record dwell/countdown state** used by the script/animation executor. Ordinary records count it downward toward a small terminal threshold; some records wait at the terminal value and a narrow family initializes dwell after entry.

**Known limits / counterexamples**

- It is not a universal wall-clock timer.
- It does not always load its final dwell value on the exact cursor-arrival frame.
- `+0x34 == 1` does not guarantee immediate record advance because conditional wait records can hold at `1`.
- The exact unit/update cadence can exhibit `-1`, `-2`, repeated values, and scene/execution-order effects; the confirmed semantic is record-local countdown/dwell, not "one unit equals one rendered frame".

**Status:** `CONFIRMED`

## Rejected / bounded alternatives from this round

| Offset | Classification | Reason |
|---|---|---|
| `+0x00` | `REJECTED` as current enemy ACTIVE/presence | zero transitions while `+0x24` has 74 enter + 74 exit boundaries |
| `+0x6D..0x6E` as upstream selector | `REJECTED` | association at `+0x3D..0x3E` precedes six same-type target commits by tens to hundreds of frames |
| `+0x34` as simple universal frame timer | `REJECTED` | terminal waits and delayed initialization are repeatedly observed |

## Next bounded question

Priority remains lifecycle first. The next round should answer exactly:

> **Is there a field that represents active/inactive object execution more directly than `+0x24` type-present, and that changes at lifecycle boundaries without conflating type replacement?**

Do not enqueue another generic 60-second capture for this. First mine the existing seven-run corpus around the 74 enter and 74 exit boundaries and rank fields by deterministic before/after transition behavior. Only request a new EFIELD capture if the existing boundary set cannot distinguish the leading field(s).

## Evidence provenance

Read-only historical sources consumed for this frontier:

- `reports/EFIELD_WIN_KAWAKS_ENEMY_FIELD_ATLAS.md`
- `reports/EFIELD_LATEST_EVIDENCE_20260901.md`
- `reports/EFIELD_TARGET_EXECUTOR_STATE_MACHINE_20260901.md`
- bridge `results/efield/*` analyses referenced by those reports

Acquisition status: valid raw corpus remains seven EFIELD captures. EFIELD-007/008/009 failed before sampling due to fresh RAM discovery ambiguity; those failures are acquisition-environment faults and are not field-research failures.
