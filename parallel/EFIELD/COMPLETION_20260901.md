# EFIELD Bounded Field-Mapping Phase — Completion

Date: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Status: **COMPLETE for the current bounded high-value field-mapping phase**

## Scope completed

The EFIELD lane was explicitly re-scoped away from attempting to name the entire enemy `0xE0` object. The completion criterion is therefore not “all 224 bytes named.” It is:

- resolve the highest-value lifecycle fields;
- resolve target/association/retarget layers as far as existing evidence allows;
- resolve movement-specific fields and bound coordinate candidates;
- resolve timer/countdown/executor structure;
- resolve coarse/fine attack-associated state hierarchy without inventing hit semantics;
- resolve stable instance/profile metadata;
- classify residual high-value fields honestly when the current corpus cannot support narrower semantics;
- stop generic acquisition loops once existing evidence is exhausted.

That criterion is now met.

## Evidence base

Seven valid EFIELD raw captures were mined:

- 23,400 frames
- 468,000 enemy-object samples
- 60,271 type-present samples
- 407,729 type-absent samples
- 1,604 type episodes
- 74 enter + 74 exit lifecycle boundaries
- 8 confirmed live-target changes
- two WinKawaks process sessions
- zero game-memory writes

EFIELD-007/008/009 acquisition failures occurred before sampling because fresh RAM discovery was not uniquely qualified. They were treated correctly as collector-environment faults, not field evidence, and were not repeated as an undirected capture loop.

## Delivered formal map

The authoritative consolidated map is `parallel/EFIELD/FIELD_FRONTIER.md`.

### 17 CONFIRMED structural field entries

1. `+0x24` — U8 current type-present/lifecycle discriminator + type code
2. `+0x6D..+0x6E` — U16 BE materialized live player-target pointer
3. `+0x34` — U8 executor record dwell/countdown
4. `+0xC6` — U8 stored player-association index
5. `+0x3D..+0x3E` — U16 BE stored player-association pointer
6. `+0xB9` — U8 horizontal-locomotion cyclic phase counter
7. `+0xBB` — U8 horizontal-locomotion decrementing step/countdown state
8. `+0x2F..+0x32` — U32 BE flagged logical executor record cursor
9. `+0x35` — U8 executor dwell/control-mode state
10. `+0x6C` — U8 fine executor/attack-associated phase code
11. `+0x73` — U8 coarse executor/attack-family phase code
12. `+0x70` — U8 second fine executor/attack-associated phase code
13. `+0x77` — U8 second coarse executor/attack-family phase code
14. `+0xB4` — U8 episode-stable coarse profile/variant metadata bit
15. `+0xB6` — U8 episode-stable instance/profile initialization code
16. `+0xCC` — U8 stored-association nearest-X synchronization checkpoint state
17. split `+0x6F` + `+0x68` — two U8 lanes jointly encoding a distinct P1/P2/P3 player-reference layer

### 7 STRONG_CANDIDATE entries intentionally not over-promoted

- `+0x07..+0x0A` — first signed fixed-point coordinate-bearing block
- `+0x0B..+0x0E` — second signed fixed-point coordinate-bearing block
- `+0x72` — executor joint-phase companion payload
- `+0x2D` — compact executor/control state
- `+0x2E` — compact executor/control companion state
- `+0x37` — attack/executor-family gate or substate
- `+0xB0` — slowly-changing profile/runtime state

These remain candidates because the current data does not provide the independent discriminator needed for a narrower semantic name.

## Major rejected overclaims

The phase also explicitly closed several misleading hypotheses:

- `+0x00` is not current enemy active/presence.
- No byte-level active/inactive gate beats the proven `+0x24` type-present discriminator in the retained corpus.
- `+0x42` is not a lifecycle gate despite changing on all lifecycle edges.
- `+0x6D..+0x6E` is not the upstream selector.
- `+0x99` is not a universal/pre-commit retarget signal.
- C6 association is not the live target and is not a selective imminent-retarget signal.
- split `+0x6F/+0x68` is not a live-target alias.
- `+0x34` is not a simple universal wall-clock/frame timer.
- U16 `+0x34..+0x35` is not one countdown.
- U16 `+0x37..+0x38` is not a timer.
- `+0xB0` is not immutable instance-initialization metadata.
- coarse/fine phase values are not promoted to hitbox-active, damage onset, startup, recovery, or visual animation semantics.

## Round artifacts

- `FIELD_FRONTIER.md` — authoritative consolidated frontier
- `ROUND_002_LIFECYCLE_ACTIVE.md`
- `ROUND_003_TARGET_ASSOCIATION_AND_RETARGET.md`
- `ROUND_004_MOVEMENT_COORDINATES.md`
- `ROUND_005_EXECUTOR_CURSOR_AND_MODE.md`
- `ROUND_006_COARSE_FINE_ATTACK_PHASE.md`
- `ROUND_007_SECOND_PHASE_PROJECTION.md`
- `ROUND_008_INSTANCE_METADATA.md`
- `ROUND_009_ASSOCIATION_SYNC_AND_THIRD_REFERENCE.md`
- `ROUND_010_ACTION_CONTROL_RESIDUALS.md`

Round 001 is incorporated in the original frontier history and covers the first formal locks: `+0x24`, `+0x6D..+0x6E`, and `+0x34`.

## Remaining explicit unknowns

These are intentionally **not** treated as unfinished generic-capture work:

1. Which coordinate-bearing block is the final game-space X versus floor-depth/Y field, what is the minimum packed authoritative width, and what is the scale/fraction convention?
2. What independent semantic dimension does `+0x72` carry inside the joint executor phase tuple?
3. What do individual values of `+0x2D`, `+0x2E`, `+0x37`, and `+0x35` mean behaviorally?
4. What is the downstream engine role of the split third player-reference layer beyond its confirmed P1/P2/P3 identity?
5. Does a genuinely selective pre-commit retarget trigger exist, distinct from long-lived association and same-frame copy states?

A future EFIELD phase should reopen only when a concrete question or a deliberately discriminative game scene can answer one of those items. It should not restart undirected 60-second collection.

## Isolation / production boundary

All conclusions here are WinKawaks-local discovery evidence. They do not promote any numeric offset into Browser/WASM, do not modify production-shadow, do not advance any WOF-0xx coordinator/validator, and do not establish Browser production proof.

The current bounded EFIELD field-mapping phase is therefore closed cleanly with confirmed fields, bounded candidates, explicit rejected hypotheses, and no outstanding generic capture requirement.
