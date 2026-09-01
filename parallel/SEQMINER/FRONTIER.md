# SEQMINER Frontier

Updated: 2026-09-01

## Current verdict

The ordered-sequence hypothesis is **required**, not optional:

- Browser T18 has prospective proof that one exact zero-attack state can lead to both A4704 and A4712.
- Browser T23 has eight attack-labelled same-cycle traces across A4792/A4920/A5888 and already contains a concrete state that appears in more than one eventual-attack branch.
- Retained WinKawaks EFIELD evidence shows a highly structured ordered executor: logical record cursor -> timer/mode -> full phase tuple. This gives SEQMINER a strong local sequence backbone, but not yet an exact attack label.

## Exhausted information from currently visible retained corpus

### Cursor/order

- `+0x2F..0x32` is the strongest ordered backbone.
- logical cursor advances are predominantly `+0x0A` records.
- destination phase tuple prediction is near-deterministic and survives leave-one-run-out.
- pair/triple mining should be record-aware rather than only byte-state-aware.

### Timer

- `+0x34` is a record dwell/countdown.
- literal timer equality is too brittle for family matching.
- record-relative ceiling normalization preserves the dominant sampling variation (`ceiling`, `ceiling-1`, `ceiling-2`).

### Branch mode

- `+0x35` has an independent transition machine and can distinguish branches sharing the same broad phase.
- `+0x37` remains useful as a gate/substate feature.

### Phase path

- the `(6C,70,72,73,77)` tuple provides useful compressed ordered paths and boundary families.
- `+0x73` must remain a structural proxy, not an attack semantic.

### Context

- live target `+0x6D..0x6E` and association/reference `+0x3D..0x3E/+0xC6` are distinct layers and must not be collapsed.
- `+0xB0/+0xB4/+0xB6` should be retained when measuring cross-instance stability.

## Highest-value Browser return candidates

1. **T18 post-BODY4728 sequence split** — highest priority because the shared anchor has already failed attack specificity prospectively.
2. **T23 A5888 BODY4936 tail3** — direct same-cycle ordered evidence; constituent single state is ambiguous.
3. **T23 branch-set tail2/tail3 model** — A4792 and A4920 are visibly multi-branch, so branch-set validation is more defensible than a universal fingerprint.
4. **Cross-target invariance** for any surviving ordered candidate.

## Current hard blocker for full-game WinKawaks attack atlas

On connector-visible GitHub `main` during this pass:

- `parallel/SWEEPATLAS/` is absent;
- no retained all-game `SWEEP*` raw is visible in bridge `captures/`;
- the retained EFIELD corpus has rich attack-associated phase structure but no separately proven exact local `activeAttack` value that can safely be used to label A4704/A4712/etc.

Therefore it would be scientifically invalid to fabricate all-game `eventual activeAttack` pair/triple tables from the current GitHub-visible data.

This blocker does **not** justify asking the operator to hand-move files. `seqminer.py` automatically scans retained raw from a checkout/CI workspace and can be rerun without per-file instructions.

## What would materially advance this lane

Only two events change the frontier:

1. retained all-game sweep raw becomes available in the repository/workspace; or
2. a WinKawaks-local exact attack descriptor is independently proven.

When either happens, run the miner across all retained captures and regenerate:

- zero-cycle atlas;
- eventual-attack groups;
- final/tail2/tail3 tables;
- all transition pairs/triples;
- exact timer variants;
- normalized timer families;
- ambiguous-single-state branch points;
- cross-capture/scene/target stability;
- ranked Browser validation queue.

## Recapture decision

**No Collector task requested.** Existing evidence has not reached a point where one tiny WinKawaks recapture is the only missing discriminator. The immediate productive work is Browser prospective sequence validation of T18/T23 and automatic consumption of retained sweep raw when it appears.

## Lane completion state

`SEQMINER v1` infrastructure and current-corpus analysis are complete. The lane is parked at a genuine data boundary rather than an unresolved offline-computation step.
