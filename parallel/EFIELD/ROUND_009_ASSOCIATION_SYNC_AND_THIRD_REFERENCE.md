# EFIELD Round 009 — association synchronization and third player-reference layer

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Questions

1. Is `+0xCC` a repeatable synchronization checkpoint for the confirmed stored player association `+0xC6 / +0x3D..+0x3E`?
2. Do `+0x6F` and `+0x68` jointly encode a distinct third player-reference layer?

No new capture was queued.

## Field 1 — `+0xCC`

**Operational name:** stored-association nearest-X synchronization checkpoint state
**Width:** `U8`
**Observed domain:** exactly `0x00` / `0xFF`
**Classification:** `CONFIRMED`

### Direct evidence

The decisive event is the same-type `00->FF` transition. Across the seven-run corpus:

- same-type `CC 00->FF` entries: `65`;
- before entry, C6 already equals nearest-X in `57/65` cases;
- before entry, C6 is stale relative to nearest-X in `8/65` cases;
- after entry, C6 equals nearest-X in **65/65** cases;
- C6 changes on exactly the eight stale cases and remains unchanged on all 57 already-correct cases.

Thus the checkpoint acts conditionally rather than merely correlating with a C6 write: if the stored association is correct it is preserved; if stale it is replaced by nearest-X on the same frame.

The effect repeats across runs, slots and different player destinations. The eight corrective events include P1/P2/P3 destinations and share a clean execution-state entry signature, most commonly `+0x2D -> 0x06`, without requiring a live-target change.

`+0xCC` is not a one-frame pulse. The full corpus contains 65 `00->FF` and 70 `FF->00` transitions, and `FF` runs commonly persist for tens to more than one hundred frames. This supports a checkpoint/latch-state interpretation rather than an instantaneous event byte.

### Known limits

- `CC=FF` does not mean C6 will remain nearest-X forever; after synchronization C6 is sample-and-hold and geometry can later change while C6 remains latched.
- `CC 00->FF` is not the only way C6 can change: a separate P1 reset/default branch exists while CC remains `00`.
- `+0xCC` is not the live target and is not a retarget pulse.
- The exact engine-level meaning of the FF latch interval is not decoded.

**Status:** `CONFIRMED`

---

## Field pair 2 — `+0x6F` and `+0x68`

**Operational name:** split third player-reference encoding
**Widths:** `U8` high lane at `+0x6F`; `U8` low lane at `+0x68`
**Joint encoding:** `(U8(+0x6F) << 8) | U8(+0x68)`
**Observed joint domain:** exactly `0xBE1C` = P1, `0xBEFC` = P2, `0xBFDC` = P3
**Classification:** `CONFIRMED` as a distinct player-reference layer; downstream semantic role remains unresolved

### Direct evidence

Across all **60,271** type-present samples:

- `+0x68` takes exactly the known player-pointer low bytes `1C`, `FC`, `DC`;
- `+0x6F` takes exactly the corresponding high bytes `BE`, `BF`;
- the split composite `(6F<<8)|68` is a valid known P1/P2/P3 player pointer in **60,271 / 60,271** samples;
- joint domain counts are `BE1C:40874`, `BFDC:12016`, `BEFC:7381`.

It is demonstrably distinct from both previously confirmed player-reference layers:

- split ref equals stored C6 association in only `23,093 / 60,271 = 38.32%`;
- split ref equals materialized live target in only `44,974 / 60,271 = 74.62%`;
- same-type split-reference changes: `20`, versus 11 same-type association changes and 6 same-type live-target changes;
- there are many long identity episodes where association, split ref and live target occupy different player identities.

The event ordering also shows independence rather than aliasing:

- after an association change, the split reference may update immediately, after 11/15/19/52/432 frames, or not at all in the retained window;
- after a split-reference change, the live target may update immediately, after 38/42/51/391 frames, or not at all;
- on the six same-type live-target changes, the split ref already equals the destination at the commit frame, but this relationship does not uniquely identify an imminent commit because the split ref can remain stable long beforehand.

### Width / layout guardrail

This is **not a contiguous U16 field**. The high and low lanes are split across the object (`+0x6F` and `+0x68`), with unrelated bytes between them. Each lane is formally U8; only the tested composite is interpreted as a pointer identity.

### Known limits

- The role of this third reference is unresolved: it is not safely named intended target, previous target, animation target, collision target, or future target.
- It is less nearest-X-aligned than C6 association (~39.05% vs ~87.02%) and more live-target-aligned than association, but those statistics do not establish causal direction.
- No Browser/WASM numeric equivalence is implied.

**Status:** `CONFIRMED`

## Round 009 conclusion

The target/reference subsystem now contains three structurally distinct proven layers:

1. `+0xC6 / +0x3D..+0x3E` — stored player association, refreshed at the confirmed `+0xCC` synchronization checkpoint;
2. split `+0x6F/+0x68` — a separate P1/P2/P3 reference layer with unresolved semantic role;
3. `+0x6D..+0x6E` — materialized live player target.

No existing field is promoted as a universal retarget precursor.

## Next bounded question

Finish the high-value unresolved action/state neighborhood:

> Can `+0x2D`, `+0x2E`, and `+0x37` be narrowed to stable operational structural roles without overclaiming attack semantics?

If existing execution-state evidence cannot discriminate them, leave them candidate-level rather than collecting generically.

## Evidence sources

- bridge `results/efield/C6_CC_SYNC.md`
- bridge `results/efield/CC_PULSE.md`
- bridge `results/efield/PLAYER_REFERENCE_LAYERS.md`
- bridge `results/efield/THIRD_PLAYER_REFERENCE.md`
- bridge `results/efield/PLAYER_REFERENCE_PIPELINE.md`
