# EFIELD Round 010 — residual action/control neighborhood

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Question

> Can `+0x2D`, `+0x2E`, and `+0x37` be given narrow structural roles from existing evidence without inventing attack-stage semantics?

No new capture was queued. The available corpus is sufficient to bound these fields but not to assign value-by-value gameplay meanings.

## Field 1 — `+0x2D`

**Operational interpretation:** small-domain executor/control state byte
**Width:** `U8`
**Observed domain:** exactly `00,02,04,06,08,0C,0E`
**Classification:** `STRONG_CANDIDATE`

### Evidence

Across 60,271 type-present samples `+0x2D` changes 741 times and occupies a compact seven-value domain. It is highly non-random and repeatedly participates in frame-exact executor state transitions.

The clearest independent event family is the confirmed `+0xCC 00->FF` association-synchronization checkpoint:

- all eight stale->nearest-X C6 correction events coincide with a `+0x2D` change;
- seven are `04->06` and one is `0C->06`;
- no `+0x2D` change occurs at lags -3,-2,-1,+1,+2,+3 in those eight event windows;
- however `+0x2D->06` is not selective enough to equal the synchronization event itself: there are many non-C6-update exposures.

Movement-vs-attack conditioning also places it on the executor/action side rather than locomotion: attack-selectivity is about 6.6x relative to the clean movement partition.

### Why not CONFIRMED to a narrower semantic

The same values and transitions occur in multiple executor contexts. Neither `06` nor any other code uniquely identifies association synchronization, attack entry, target commit, lifecycle, or another single event. Existing evidence establishes a compact control-state role but not what each state means.

**Status:** `STRONG_CANDIDATE`

---

## Field 2 — `+0x2E`

**Operational interpretation:** small-domain executor/control companion state byte
**Width:** `U8`
**Observed domain:** exactly `00,02,04,06,08,0A,FF`
**Classification:** `STRONG_CANDIDATE`

### Evidence

Across 60,271 type-present samples `+0x2E` changes 1,492 times. Its seven-value domain is stable and strongly execution-conditioned.

At the eight confirmed stale-association corrections it changes on all eight exact frames, commonly `08->00`, `0A->00`, or `04->00`. Yet the same transition families also occur without a C6 correction, proving that `+0x2E` is a broader executor state rather than the specific association trigger.

It was already rejected as a direct lifecycle gate: only 37/74 type-enter and 32/74 type-exit edges change it, while it changes many times within a type episode. Movement-vs-attack conditioning nevertheless gives ~7.36x attack-side selectivity over the clean movement partition.

### Why not CONFIRMED to a narrower semantic

The field participates in several known event families but no single value/transition has a universal and selective behavioral interpretation in the current corpus. Naming codes as action, attack stage, wait state, or retarget state would be overreach.

**Status:** `STRONG_CANDIDATE`

---

## Field 3 — `+0x37`

**Operational interpretation:** attack/executor-family gate or substate byte
**Width:** `U8`
**Observed domain:** exactly `00,80,02`
**Classification:** `STRONG_CANDIDATE`

### Evidence

Across the full type-present corpus:

- values: `00` dominates, `80` is repeatedly populated, `02` is rare;
- transitions: 1,528;
- movement-vs-attack selectivity is strong: movement support ~0.0079 versus attack-event support ~0.4387, a ratio ~55.6x;
- `+0x38` is constant `0x84`, so the old U16-timer interpretation is structurally unsupported.

Coarse-phase conditioning further bounds the role:

- `+0x37=80` occurs in `+0x73=00` and `+0x73=1B` families;
- `+0x73=0A`, `0B`, and `1E` are observed with `+0x37=00` in the retained corpus;
- repeated `00<->80` transitions cluster around entry/exit paths involving the `1B` family, but both directions can occur at similar coarse boundaries.

Thus the byte is clearly part of a narrow executor/attack-family control mechanism, but `80` is not a simple attack-on bit and the rare `02` state lacks enough repeated discriminative events for a specific name.

### Rejected interpretation

`U16(+0x37..+0x38)` as a countdown/timer is **REJECTED**: `+0x38` is constant `0x84`, while all meaningful changes reside in the U8 byte `+0x37` and are mostly `00<->80` state flips rather than small numeric decrements.

**Status:** `STRONG_CANDIDATE`

## Round 010 conclusion

The existing corpus supports all three fields as compact executor/control states, but not value-level gameplay semantics. Under the bounded-field policy they remain candidate-level rather than forcing names from correlation.

No generic new capture is justified. Promoting any of these to a narrower semantic would require a deliberately discriminative scene/event tied to a concrete question, not more undirected runtime volume.

## Next step

The high-value EFIELD priorities are now exhausted against the existing seven-run corpus. Consolidate the formal frontier, preserve remaining ambiguities, and close the current bounded field-mapping phase without attempting to name the rest of the 0xE0 object.

## Evidence sources

- bridge `results/efield/TIMER_SEMANTICS.md`
- bridge `results/efield/MOVE_ATTACK.md`
- bridge `results/efield/C6_COMMIT_STATE.md`
- bridge `results/efield/C6_CC_SYNC.md`
- bridge `results/efield/ATTACK_TIMERS.md`
