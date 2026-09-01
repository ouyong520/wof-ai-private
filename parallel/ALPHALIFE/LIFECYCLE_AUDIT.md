# WOF Alpha lifecycle audit

Updated: 2026-09-01  
Audit target: ALPHAQA-002 — same-type same-slot replacement inherits an old warning.

## 1. Exact failure in current Alpha

RC1 keeps per-slot state in `prev`, `current`, `cycle`, `armed`, and `watches`.

A live watch is cleared on two observed lifetime events:

- slot becomes absent (`slotGone`)
- slot remains present but enemy `type` changes (`typeChanged`)

A same-type replacement with no observed absent sample crosses neither guard. The old watch therefore remains live.

`warningRows()` then obtains the current snapshot from the reused slot and checks only that the current object still has the watch's type and `attack === 0`. Target and side are recomputed from the current occupant. This allows:

`episode A signal -> A watch survives -> episode B occupies same slot/type -> B target/side rendered under A watch`.

The independent QA fixture demonstrates this with the long-horizon T20 A5136 warning.

## 2. Browser reader contract

The Alpha worker polls 20 fixed enemy slots every 10 ms. A Browser snapshot currently contains:

- slot
- type
- target selector
- state99 / action2A / b2B
- body / attack
- frameEnd / next / value30 / timer34 / payload6C
- enemy X and target X

The reader returns `null` when the type is outside the accepted enemy range or both `frameEnd` and `next` are zero.

There is no episode ID, generation counter, allocation serial, spawn ID, or other field whose retained Browser evidence proves one-to-one identity with an enemy episode.

The 10 ms polling interval also does not prove that a short inactive/reset interval cannot occur entirely between polls.

## 3. Retained Browser research behavior

The retained Browser production-shadow / validator lineage uses the same basic lifetime assumption:

- censor on observed slot disappearance
- censor on observed type change
- otherwise keep slot/type watches and resolve them against later ACTIVE transitions of the same slot/type

This was adequate for prospective rule validation, but it is not a proof of object identity. High precision of the frozen attack rules does not establish that every same-type replacement boundary was observable or correctly segmented.

The Browser evidence does prove useful live semantics such as current target selection and exact precursor predicates. Those semantics should remain separate from lifetime identity.

## 4. WinKawaks negative-assumption evidence

EFIELD lifecycle work establishes that typed enemy episodes and replacements exist and that same-type replacement cannot be ruled out.

Round 008 observed 11 same-type replacement boundaries. Two episode-stable profile fields were characterized:

- `+0xB4`: constant within all 1,604 observed episodes, but changed on only 3/11 same-type replacement boundaries.
- `+0xB6`: constant within all 1,604 observed episodes, but changed on 9/11 same-type replacement boundaries.

These results are valuable because they invalidate the assumption that same slot + same type identifies an instance. They do **not** provide a release identity field:

- neither field is unique;
- both may be reused by another episode;
- two same-type replacements retained the same `+0xB6` value;
- the observations are WinKawaks-local and their offsets must not be imported into Browser Alpha without Browser proof.

Round 002 likewise did not find a stronger generic lifecycle gate than the local type-present discriminator.

## 5. Why target, position, state, or timing cannot substitute for identity

### Target / retarget

A real enemy can retarget while remaining the same episode. Retained evidence explicitly treats the live target as dynamic. Therefore target change is not a valid lifetime boundary.

### Enemy position

A large X jump may look like replacement, but no Browser-proven movement bound says a particular jump is impossible for the same enemy, and a replacement may appear near the previous enemy. Position is therefore only a heuristic and is unsuitable for a release safety guard.

### Rule-state fingerprint

The frozen state fields are executor/descriptor state. They legitimately change inside one episode. A replacement can also enter with values that are reachable in another episode. Fingerprint changes are not instance boundaries, and fingerprint equality is not identity.

### Time gap / polling jitter

A longer gap is a good reason to invalidate history, but a short gap is not positive proof of continuity. Even adjacent 10 ms samples may straddle a hidden replacement.

## 6. Information boundary

With the current snapshot contract, consider two executions that produce the same sampled values:

1. one enemy episode evolves from sample `p` to sample `s`;
2. episode A produced `p`, then was replaced between polls by same-type episode B that produced `s`.

If all Alpha-observed fields in `p` and `s` are identical in both executions, the engine has no information that can distinguish them.

Therefore a release guarantee of “do not cross enemy episodes” cannot be obtained by a more clever comparison of the existing fields alone. Any policy that preserves a history-derived watch across an unproven boundary can still be fooled by an observationally equivalent replacement.

This is the key audit conclusion.

## 7. Rule-family consequences

### A. History / edge rules

These rules require a relation between two samples:

- `T16_B4_DANGER_40`: entry into exact B4 state
- `T20_5136_B0_TO_B255_1250`: exact B0 -> B255 transition
- `D867BA_3232_TM6_220`: entry into exact descriptor state
- `D8811E_3232_TM6_135`: entry into exact descriptor state

Without positive episode continuity, `p` and `s` may belong to different enemies. The edge itself is therefore not release-safe.

A later neutral same-type occupant can also inherit an already armed watch. Clearing only on null/type change fixes neither the false-edge problem nor the stale-watch problem in full.

### B. Current-level rules

These two rules are defined by the current sample alone:

- `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`
- `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`

A replacement occupant that independently matches the exact frozen predicate supplies fresh evidence for the same current-level warning. A replacement occupant that does not match the predicate must not inherit an old warning.

Thus these rules can remain release-safe without an instance ID if output is tied to the exact current predicate and no warning is carried after the predicate ceases to hold.

## 8. Stop condition

**Stop condition B.** No Browser-proven positive instance identifier or unmissable reset boundary was found in the retained release evidence.

A conservative implementation-ready policy is available and does not require additional Browser testing to be logically safe. If maintaining the four history-dependent warnings is a product requirement, a separate minimal Browser identity investigation becomes necessary; until then they should be safety-quarantined.
