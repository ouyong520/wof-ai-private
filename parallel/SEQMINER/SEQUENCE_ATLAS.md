# SEQMINER Sequence Atlas

Evidence namespace: **WinKawaks-local discovery unless explicitly marked Browser evidence**.

No entry in this file is a Browser production rule.

## 1. What the retained data already establishes

The retained seven-run EFIELD corpus supplies a strong executor topology even though it does not yet expose a separately proven WinKawaks-local exact `activeAttack` descriptor.

### Stable executor chain

The strongest reusable ordered state is the combination:

```text
logicalCursor(+0x2F..0x32)
+ timer34(+0x34)
+ mode35(+0x35)
+ gate37(+0x37)
+ phaseTuple(+0x6C,+0x70,+0x72,+0x73,+0x77)
+ target(+0x6D..0x6E)
+ association(+0x3D..0x3E,+0xC6)
+ profile(+0xB0,+0xB4,+0xB6)
```

Sequential logical cursor `+0x0A` destination records predict the destination phase tuple with effectively deterministic cross-run behavior: aggregate leave-one-run-out coverage `4819/4820`, accuracy `4818/4819` on covered events. This makes the cursor chain a better ordered backbone than any isolated phase byte.

### Structural nonzero-phase cycles

Using only `+0x73 != 0` as a **structural phase proxy**, not semantic attack ACTIVE, the retained phase-boundary analysis contains 508 episodes. Common compressed paths include:

| compressed path | count | interpretation |
|---|---:|---|
| `E0,A0,D8,0A,0C` | 216 | dominant single-family/core episode |
| `40,00,E8,1B,00 -> E0,A0,D8,0A,0C -> 40,00,E8,1B,00` | 41 | bridge -> core -> bridge |
| `E0,00,38,0A,00 -> E0,A0,D8,0A,0C` | 38 | alternate entry -> core |
| `50,00,18,1B,00` | 28 | short boundary-enriched family |
| `40,00,E8,1B,00 -> E0,A0,D8,0A,0C -> 40,00,E8,1B,00 -> 48,00,00,1B,00` | 24 | longer terminating bridge branch |
| `E0,A0,D8,0A,0C -> 40,00,E8,1B,00` | 21 | core -> bridge |
| `58,00,30,1B,00` | 20 | short boundary-enriched family |
| `40,00,E8,1B,00 -> E0,A0,D8,0A,0C -> E0,00,38,0A,00` | 17 | core exit into alternate 0A family |
| `40,00,E8,1B,00 -> E0,A0,D8,0A,0C` | 16 | bridge -> core |
| `40,00,E8,1B,00 -> E0,A0,D8,0A,0C -> 50,00,18,1B,00` | 14 | branch into boundary-enriched 1B family |

The rare tuples `78,78,78,1E,0B` and `70,70,70,1E,0B` had no interior samples in that analysis and are therefore useful **termination/boundary context candidates**, not attack labels.

The most interior-dominant tuple is `90,00,88,0B,00` (`257/271`, 94.83% interior), which is useful for distinguishing a long dwell/core state from a transition edge.

## 2. Timer progression atlas

`+0x34` behaves as a record dwell/countdown and should be represented in two forms.

### Exact timer

Exact timer is retained because some branches can be timing-specific. Pointer-stable changes are dominated by `-1/-2`; pointer transitions normally reload upward.

### Record-normalized timer

For logical `+0x0A` destination arrivals:

- exact record ceiling: `3192/4323 = 73.84%`;
- within one below ceiling: `4000/4323 = 92.53%`;
- within two below ceiling: `4090/4323 = 94.61%`.

Leave-one-run-out remains stable, so SEQMINER normalizes timer as:

```text
ceilingMinusTimer = recordCeiling(logicalCursor) - timer34
bucket = 0 | 1 | 2 | 3-5 | 6-10 | 11+
```

This specifically prevents one- or two-tick sampling jitter from falsely splitting the same ordered family.

## 3. Independent timer/mode branch axis

`+0x35` is not redundant with `+0x34`. Its retained transition matrix contains strong state-machine structure:

- `00->FF`: 353
- `FF->00`: 237
- `02->00`: 128
- `FF->02`: 74
- `00->01`: 67
- `00->02`: 52
- `01->FF`: 39
- `04->00`: 25

A large part of `00->FF` aligns with logical cursor `+0x0A` (`251` events), but many other mode changes encode distinct transitions. Therefore pair/triple mining should include mode35 and not collapse the executor to cursor+timer alone.

`+0x37` (`00/80/02`) is retained as an attack-associated gate/substate candidate and used as another branch-context feature.

## 4. Target and reference context

The live/materialized target pointer `+0x6D..0x6E` and the sticky proximity/player-association layer `+0x3D..0x3E/+0xC6` must remain separate features.

A sequence is tagged with:

- target at zero-cycle start;
- target at future event;
- whether target changed inside the cycle;
- association index/pointer progression.

This prevents an apparently attack-specific sequence from actually being a target-transition artifact.

## 5. Browser-labelled ordered evidence used only for validation prioritization

### T23

WOF-047 already contains eight same-cycle zero->ACTIVE traces from one T23 room:

- `A4792`: 3
- `A4920`: 3
- `A5888`: 2

The strongest direct order lesson is the A5888 tail3:

```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
-> A5888
```

The first state also occurs on an A4792 cycle, so membership in `S0/A8/B2 BODY4936` is not sufficient; the transition path carries information.

A4792 itself is multi-branch, with three different immediate tails, so SEQMINER must not search for one universal short T23 fingerprint at the expense of branch-specific rules.

### T18 A4704 / A4712

WOF-051 prospectively proved exact-state ambiguity:

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

produced:

```text
A4704 @ 19.9 ms
A4712 @ 100.4 ms
```

with target and side stable in both cases. The correct next unit is therefore the ordered context immediately **after** this shared state, plus the preceding tail if the post-state path remains ambiguous.

## 6. What is not yet available on connector-visible main

At this pass, `parallel/SWEEPATLAS/` is absent and no pushed all-game `SWEEP*` retained capture is visible in `wof-winkawaks-bridge/captures/`. Therefore exact all-game attack-labelled pair/triple frequency tables cannot be honestly emitted yet from GitHub-visible raw.

This is a data-availability boundary, not a request for manual transfer. `seqminer.py` is already written to discover and consume retained raw automatically from a checkout/CI environment whenever those files are present.

## 7. Sequence ranking policy

A candidate is ranked upward when all of the following improve:

1. same-cycle support;
2. purity for one eventual attack;
3. number of independent captures;
4. number of scenes;
5. number of starting targets;
6. robustness when exact timer is replaced by normalized timer;
7. ability to split a known ambiguous final/single state.

A candidate is ranked downward when:

- it appears only once;
- support comes from one capture/scene;
- it requires exact timer equality but collapses after normalization;
- its apparent specificity disappears after conditioning on target/profile;
- it is only an in-sample correlation.
