# EFIELD Round 008 — instance/profile metadata

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Question

> Which fields are truly stable for an enemy type episode and are reinitialized/reselected across replacement strongly enough to be formalized as instance/profile metadata?

No new capture was queued.

## Field 1 — `+0xB4`

**Operational name:** episode-stable coarse profile/variant metadata bit
**Width:** `U8`
**Observed domain:** exactly `0x00` / `0xFF`
**Classification:** `CONFIRMED`

### Direct evidence

Across the full seven-run corpus there are 1,604 contiguous same-nonzero-type episodes. `+0xB4` is constant in **1,604 / 1,604** episodes with **zero within-episode changes**.

The byte is not merely a type code alias:

- both values occur within the retained type-conditioned corpus (`00` dominates, `FF` is also repeatedly populated);
- same-type replacement boundaries can change the byte (`3/11` observed same-type replacement boundaries), proving that it can distinguish instances/profiles even when the enemy type remains the same;
- most replacement boundaries retain the same value, as expected for a coarse binary profile dimension rather than a unique instance ID.

Full-corpus boundary analysis records 16 value changes across 1,583 consecutive episode boundaries, including both zero-gap and direct replacement cases. Its stability therefore belongs to the episode/initialization layer rather than to per-frame executor state.

Width is U8: `+0xB5` is constant zero in the width-refinement corpus, so a U16 interpretation adds padding and no additional state.

### Known limits

- `+0xB4` is not a unique instance identifier; many episodes and replacements share the same bit.
- The exact gameplay meaning of `00` versus `FF` is not known; no claim such as palette, elite, direction, spawn side, or difficulty is made.
- It is not the enemy type field; `+0x24` separately carries type-present/type code.

**Status:** `CONFIRMED`

---

## Field 2 — `+0xB6`

**Operational name:** episode-stable instance/profile initialization code
**Width:** `U8`
**Observed domain:** 34 values in the full seven-run corpus
**Classification:** `CONFIRMED`

### Direct evidence

`+0xB6` is also constant in **1,604 / 1,604** type episodes with **zero within-episode changes**, but carries a much richer 34-value domain. Common values include `46`, `2C`, `26`, `29`, `36`, `44`, `43`, `0E` and many additional codes.

The strongest replacement control is same-type replacement:

- 11 same-type replacement boundaries are available;
- `+0xB6` changes on **9/11** of them;
- because `+0x24` type is unchanged at these boundaries, these changes cannot be explained as simple type identity.

Across all 1,583 episode boundaries, `+0xB6` changes 43 times. Many different-type replacements reuse the same code, demonstrating that it is neither a type code nor a unique object ID. Instead it behaves as an initialized profile/variant dimension selected for an episode and then held invariant.

Episode-level tuple analysis further shows `+0xB6` participating in high-coverage instance-varying profile tuples with `+0xB0`, `+0xD0`, `+0xD6`, `+0xB4` and others. The tuple diversity is substantial within the same enemy type, reinforcing an instance/profile layer rather than type identity.

Width is U8: the adjacent-byte U16 view creates mixed composite values with the next independently varying byte rather than a simpler scalar code.

### Known limits

- It is not a unique instance ID; different episodes can reuse a code.
- The exact meaning of individual values is unknown.
- A same-type replacement can retain the same `+0xB6` value (2/11 observed), so replacement is not equivalent to value change.

**Status:** `CONFIRMED`

---

## Field 3 — `+0xB0`

**Width:** `U8`
**Observed domain:** `0x70`, `0x80`, `0x90` in the retained full-corpus type-present samples
**Classification:** `REJECTED` for the hypothesis **immutable per-instance initialization field**

### Evidence

`+0xB0` is highly episode-stable but not invariant:

- full-corpus constant episodes: `1,580 / 1,604 = 98.50%`;
- within-episode changes: `29`;
- earlier focused pass likewise contained clear long episodes where `+0xB0` changed one or more times without a type replacement;
- same-type replacement changes occur on `5/11`, so it also participates in profile variation.

This is enough to retain `+0xB0` as a strong slowly-changing profile/runtime-state candidate, but it fails the stricter claim that its value is fixed at instance creation and held for the whole episode.

**Status:** `REJECTED` only as immutable instance-initialization field

## Round 008 conclusion

`+0xB4` and `+0xB6` are now formally locked as episode-stable profile/variant metadata at different granularities. `+0xB0` is explicitly excluded from that strict immutable category because real within-episode changes exist.

## Next bounded question

Return to the target subsystem for unresolved high-value structure:

> Is `+0xCC` sufficiently specific to be confirmed as the synchronization checkpoint that refreshes the stored `+0xC6 / +0x3D..+0x3E` player association, and does `+0x6F/+0x68` constitute a distinct third player-reference layer?

Use existing seven-run target/reference analyses first.

## Evidence sources

- bridge `results/efield/EPISODE_STABILITY_ATLAS.md`
- bridge `results/efield/INSTANCE_BUNDLE.md`
- bridge `results/efield/INSTANCE_PROPERTIES.md`
- bridge `results/efield/PROFILE_TUPLES.md`
- bridge `results/efield/WIDTH_REFINEMENT.md`
