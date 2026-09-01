# Recommended RC2 enemy-lifecycle invalidation policy

Updated: 2026-09-01  
Purpose: implementation guidance only. This lane does not modify Alpha product code.

## Release invariant

> A user-facing warning must never depend on historical state from an enemy episode whose continuity with the current slot occupant is not positively established.

`slot` and `type` are routing attributes, not an identity key.

## 1. Separate two concepts that RC1 currently mixes

Implementation should distinguish:

- **slot presence** — a readable enemy record currently exists at slot `i`;
- **episode continuity** — the current occupant is positively known to be the same enemy episode as the previous occupant.

The current Browser contract proves the first but does not prove the second for same-type consecutive samples.

Do not create a synthetic `episodeId` merely by incrementing on null/type-change and then treat it as proof of continuity. Such an epoch is useful bookkeeping, but it still merges a hidden same-type replacement into the old epoch.

## 2. Default continuity state

For RC2, continuity between two consecutive samples is **UNKNOWN** unless a future Browser-proven identity mechanism says otherwise.

Recommended conceptual API:

```text
continuity(previous, current) -> PROVEN | BROKEN | UNKNOWN
```

Current evidence supports:

```text
current absent                       => BROKEN
previous absent                      => BROKEN / new observation
previous.type != current.type        => BROKEN
same slot + same type                => UNKNOWN
```

There is currently no `PROVEN` case for cross-sample enemy identity.

`UNKNOWN` must be treated like `BROKEN` for history-derived user warnings.

## 3. History/edge-triggered rules

Affected frozen rules:

- `T16_B4_DANGER_40`
- `T20_5136_B0_TO_B255_1250`
- `D867BA_3232_TM6_220`
- `D8811E_3232_TM6_135`

### Arming rule

Do not evaluate a predicate that combines `previous` and `current` unless `continuity(previous,current) === PROVEN`.

With the current Browser snapshot contract, that means these four rules are **fail-closed / user-warning quarantined** for RC2.

This is stronger than only clearing an existing watch on a suspicious replacement. It also prevents a hidden replacement from manufacturing a false transition such as:

```text
episode A: T20 B0
(hidden same-type replacement)
episode B: T20 B255
```

which is observationally indistinguishable from a true B0 -> B255 edge if no identity signal exists.

### Existing watches

If an implementation temporarily retains internal watches for diagnostics, they must never be published after continuity becomes `UNKNOWN` or `BROKEN`.

A watch may not be transferred to a new local epoch merely because slot/type match.

## 4. Current-level T18 rules

Affected frozen rules:

- `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`
- `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`

These predicates are current-sample facts and therefore do not require previous-sample identity to decide whether the current occupant matches.

### Publication rule

For RC2 safety, treat them as **hold-only current-level warnings**:

```text
publish(rule, current) iff exactFrozenPredicate(rule, current) === true
```

On the first sampled state where the exact predicate becomes false, the user-facing warning must disappear immediately in that engine step.

Do not preserve the original 90 ms watch after the predicate is no longer present unless positive episode continuity is later proven.

### Replacement behavior

- A same-type replacement that is neutral/nonmatching: warning clears on that sample.
- A same-type replacement that independently matches the exact T18 predicate: warning may be shown because B itself supplies current-level evidence.
- Such a warning must be treated as fresh current evidence. It must not inherit A's `atMs`, age, target provenance, watch ID, or cycle suppression state.

Implementation may realize this most simply by making these user-facing rows stateless rather than watch-backed.

## 5. Invalidation order inside a step

The safe ordering is:

1. read/normalize current snapshots;
2. determine slot presence and continuity status;
3. invalidate all history-derived watches whose continuity is not `PROVEN`;
4. only then evaluate history/edge predicates whose continuity is `PROVEN`;
5. evaluate current-level predicates from `current` alone;
6. build warning rows from still-valid evidence;
7. resolve ACTIVE / diagnostics.

The important property is that warning rendering never has a chance to pair an old watch with a new occupant before invalidation.

## 6. Target and side policy

Keep target and side live; do not freeze them at arm time as an identity workaround.

Retargeting is legitimate within one enemy episode and the Browser research lineage intentionally treats `enemy+0x7E` as live target state.

However, a history watch may only follow live target changes while episode continuity is positively established. Under the current RC2 conservative policy, history rules are quarantined, so this condition is naturally satisfied.

For current-level T18 warnings, target/side may be computed from the same current sample that satisfies the predicate.

## 7. Polling gaps and runtime interruptions

Even after a future continuity token exists, the engine should invalidate historical evidence on:

- worker/runtime restart;
- engine `clearAll()`;
- unsupported-runtime transition;
- scene/ROM/runtime identity change;
- any reader exception;
- any future explicit episode-token change.

A large timer gap should also invalidate history because samples may have been missed. The exact allowed gap must be based on Browser evidence; do not turn the current `TICK_MS=10` into an unproven identity guarantee.

## 8. What not to use as an RC2 identity guard

Do not use any of these alone or in combination as a claimed instance ID without new Browser proof:

- same slot
- same type
- same target
- same enemy X / small movement distance
- same descriptor fingerprint
- same attack-zero cycle
- same `state99/action2A/b2B`
- WinKawaks `+0xB4`, `+0xB6`, or other local offsets
- absence of an observed null sample
- elapsed time shorter than one poll interval

They may be useful research features but do not satisfy the release invariant.

## 9. Minimal future path to restore quarantined rules

Only needed if product requires the four history-dependent warnings to return.

The Browser investigation must produce a **positive continuity contract**, not another heuristic. Acceptable outcomes would be one of:

1. a Browser-visible generation/instance value proven invariant within an episode and changed on every staged same-type replacement across broad coverage; or
2. a Browser/game-update lifecycle event proven to emit an unmissable reset/new-object boundary before a slot can be reused; or
3. another mechanism with equivalent one-episode continuity semantics.

The proof must include same-type same-slot replacement cases and sampling-jitter cases. A field that changes on 9/11 replacements, like WinKawaks `+0xB6`, is not sufficient.

Until such proof exists, release safety is achieved by suppression, not inference.

## 10. RC2 acceptance condition for ALPHAQA-002

ALPHAQA-002 can be marked fixed when all of the following hold in implementation/regression:

- no armed history warning survives a same-type replacement with no observed null/type-change;
- no history/edge rule can arm from `previous=A` and `current=B` when continuity is unproven;
- current-level T18 rows disappear on the first nonmatching current sample;
- a matching replacement T18 row is fresh current evidence, not inherited watch state;
- existing slot-gone/type-change cleanup still works;
- no WinKawaks-only field has entered the Browser release contract.
