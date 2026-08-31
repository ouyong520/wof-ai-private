# EFIELD Round 003 — player association layer and retarget precursor boundary

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Questions

1. Is `+0xC6` a stable three-player association index distinct from the confirmed live target `+0x6D..+0x6E`?
2. Is `+0x3D..+0x3E` the redundant full pointer encoding of that association?
3. Is there a selective field that reliably precedes the confirmed live-target commit?

No new capture was queued. This round uses the retained seven-capture / 60,271 type-present-sample corpus and all 8 known live-target changes.

## Field 1 — `+0xC6`

**Operational name:** stored player-association index / nearest-X synchronization state
**Width:** `U8`
**Observed domain:** exactly `0x00`, `0x01`, `0x02`
**Classification:** `CONFIRMED`

### Direct evidence

- Across 60,271 type-present samples the three values map deterministically to the association pointer:
  - `0x00 -> 0xBE1C` = P1
  - `0x01 -> 0xBEFC` = P2
  - `0x02 -> 0xBFDC` = P3
- The mapping repeats across all seven captures, two WinKawaks sessions and all represented enemy types.
- Global association geometry is strongly but not perfectly spatial: C6 equals nearest-X on `52,445 / 60,271 = 87.0153%` of type-present samples.
- The decisive synchronization experiment is `+0xCC 00->FF`:
  - 65 same-type entries observed;
  - 57/65 were already nearest-X and C6 stayed unchanged;
  - 8/65 were stale before entry and C6 changed on that exact frame;
  - after entry C6 equals nearest-X in `65/65` cases.
- Same-type C6 changes are rare (`11` total in the seven-run corpus), showing a stored/sample-and-hold association rather than a per-frame geometry calculation.

### Known limits / counterexamples

- C6 is **not** the live target: C6/association equals `+0x6D..+0x6E` on only `18,753 / 60,271 = 31.11%` of type-present samples.
- Three of 11 same-type C6 changes are a separate P3->P1 reset/default path and move away from instantaneous nearest-X; therefore C6 is not simply `argmin(absDx)` every frame.
- Six same-type live-target retargets occur after the destination C6 association has already been stable for about 57, 217, 278, 492, 537 and 715 frames. C6 is an upstream association state, not a selective imminent-retarget signal.

**Status:** `CONFIRMED`

---

## Field 2 — `+0x3D..+0x3E`

**Operational name:** stored player-association pointer
**Width:** `U16 BE`
**Observed domain:** exactly:

- `0xBE1C` = P1
- `0xBEFC` = P2
- `0xBFDC` = P3

**Classification:** `CONFIRMED`

### Direct evidence

- Across all 60,271 type-present samples the observed pointer domain is exactly the three known player object addresses.
- It is a deterministic redundant representation of C6:
  - C6 `0x00` -> `0xBE1C` in 18,091 samples;
  - C6 `0x01` -> `0xBEFC` in 17,494 samples;
  - C6 `0x02` -> `0xBFDC` in 24,686 samples.
- The low byte `+0x3E` obeys the C6 encoding formula in `60,271 / 60,271` samples with no mismatches; the full observed U16 values provide the corresponding player addresses.
- On all 8 known live-target changes, the **new** confirmed live target equals the post-frame association pointer. In six same-type retargets the association was already stable tens to hundreds of frames earlier.

### Known limits / counterexamples

- This pointer is not the materialized live target; equality with `+0x6D..+0x6E` is only 31.11% globally.
- It is not a direct imminent-retarget precursor because it often remains at the eventual destination for long periods without a live-target commit.
- The association can be changed by both nearest-X synchronization and the separate P1 reset/default branch.

**Status:** `CONFIRMED`

---

## Field 3 — `+0x99`

**Width:** `U8`
**Observed domain:** `0x00` / `0xFF`
**Classification:** `REJECTED` for the hypothesis **universal or pre-commit retarget signal**

### Evidence

- Only 17 changes occur across the seven-capture corpus.
- It changes on the exact live-target commit frame in only `5/8` known retarget events.
- Those 5 changes are all lag `0`; there is no repeated negative-lag lead transition in the event analysis.
- Multiple `+0x99` transitions occur hundreds of frames away from any live-target change while the target stays unchanged.
- Therefore its rarity raises same-frame enrichment but does not supply universal recall and does not lead the commit.

### Scope of rejection

This rejects only the meanings:

- `retarget precursor`
- `universal retarget pulse`
- `target identity`

It remains an internal sparse mode/flag candidate for later state-specific interpretation.

**Status:** `REJECTED`

## Retarget precursor conclusion

The retained corpus contains no field currently justified as a **selective universal pre-commit retarget signal**.

- C6 / `+0x3D..+0x3E` is upstream association but is too long-lived: six same-type commits lag association by 57..715 frames.
- `+0x28` is a strong same-frame companion for same-type target copies (6/6 same-type commits) but has many non-retarget changes and is absent on the two replacement-associated target changes.
- `+0x65` changes exactly on 6/8 commits and within ±3 frames on 7/8, but has 401 total changes and no stable negative-lag lead pattern.
- `+0x2D/+0x2E` are highly recurrent execution/action states and have very low event precision.
- `+0x99` is sparse but only 5/8 and same-frame, not pre-frame.

Therefore no additional generic capture is warranted merely to search for a precursor. A future capture is justified only by a deliberately staged repeated retarget scene capable of distinguishing long-lived association from the immediate copy trigger.

## Next bounded question

Proceed to priority 3, movement/geometry:

> Which enemy fields are the actual X and Y/depth coordinates, and what is their minimum reasonable width and update behavior?

Use existing movement-conditioned raw evidence first; do not enqueue a generic burst.

## Evidence sources

- bridge `results/efield/TARGET_LAYERS.md`
- bridge `results/efield/C6_3E_ENCODING.md`
- bridge `results/efield/PLAYER_ASSOC_GEOMETRY.md`
- bridge `results/efield/C6_CC_SYNC.md`
- bridge `results/efield/RETARGET_LEAD.md`
- bridge `results/efield/RETARGET_LAG_SPARSE.md`
- bridge `results/efield/TARGET_COPY_ALL.md`
- bridge `results/efield/TARGET_MATERIALIZATION.md`
