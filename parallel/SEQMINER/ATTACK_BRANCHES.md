# SEQMINER Attack Branches

Updated: 2026-09-01

This file separates **Browser attack-labelled branches** from **WinKawaks-local structural branchpoints**. Numeric local offsets/records are never copied into Browser production logic.

## A. Browser-labelled branch: T18 shared BODY4728 anchor

Shared state:

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

WOF-051 prospective outcomes:

| eventual attack | count | lead | target/side |
|---|---:|---:|---|
| A4704 | 1 | 19.9 ms | stable |
| A4712 | 1 | 100.4 ms | stable |

Verdict: **single-state attack ambiguity proven prospectively**.

Required discriminator search order:

```text
anchor
-> first distinct post-anchor state
-> post-anchor pair
-> post-anchor triple
-> descriptor/next progression
-> exact timer path
-> normalized timer/hold path
-> pre-anchor tail only if post-anchor remains ambiguous
```

Do not reuse the anchor itself as an A4704 rule.

## B. Browser-labelled branch: T23 A4792 / A4920 / A5888

WOF-047 same-cycle sample:

| eventual attack | cycles |
|---|---:|
| A4792 | 3 |
| A4920 | 3 |
| A5888 | 2 |

### A5888 ordered tail

```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
-> A5888
```

The first state also occurs on A4792, so this is direct evidence that order carries information that single-state membership does not.

### A4792 is multi-branch

Observed immediate tails are not uniform. They include a BODY4952 branch ending in `S0/A2/B0`, a BODY4936 `S0/A8/B2` branch, and an S2 BODY4952 -> BODY4936 chain ending in `S2/A8/B2`.

Therefore the candidate object should be a **branch set**, not one forced universal fingerprint.

### A4920 is also multi-family

Observed examples span distinct BODY4976 and BODY4952 finals/tails. No universal A4920 final is asserted.

## C. WinKawaks structural branch hotspot: `02008BE0`

Record-exit evidence:

```text
full segments = 355
sequential +0x0A exits = 199
branch/other exits = 141
```

Common direct paths include:

```text
02008BE0 -> 02008BEA        # common sequential path, 170
02008BE0 -> 02009006        # alternate jump, 30
```

`02008BE0` also has highly variable terminal timer-1 residence:

```text
median terminal hold = 2 frames
max = 276
>=10 frames = 51 segments
>=30 frames = 37 segments
```

Interpretation: strong **conditional branch/wait node**. Once exact local move labels exist, test pre-BE0 path + time already held at TM1 + exit destination + mode35 transition against eventual local attack.

Evidence class: `discovery_correlation`.

## D. Logical-cursor ambiguity split by embedded flags

### `02008BD6`

Same logical cursor spans materially different phase families.

- flag `0x100000`: 354/354 -> `E0,00,38,0A,00`;
- flag `0x140000`: rare `1E` termination family.

### `02005E9A`

- flag `0x100000`: 210/210 -> `E0,00,38,0A,00`;
- flag `0x140000`: rare `70/78 ... 1E` termination family.

Conclusion: `logicalCursor` alone is not a complete state identifier. `cursorFlags` is mandatory core context.

## E. Loop/reset branch nodes

Three records are overwhelmingly branch/reset rather than sequential:

| record | segments | +10 exits | branch/other |
|---|---:|---:|---:|
| `02008C12` | 144 | 0 | 142 |
| `02008C52` | 113 | 0 | 107 |
| `02005ED6` | 75 | 0 | 75 |

Examples:

```text
02008C12 -> 02008BE0   # -0x32 loop reset, 135
02005ED6 -> 02005EA4   # -0x32 loop reset, 80
```

The same phase family can recur on different loop iterations. SEQMINER v2 therefore counts a signature only once per cycle for confidence while preserving the full repeated path in cycle output.

## F. Conditional-wait family

Long terminal timer-1 holds:

| record | median TM1 hold | max |
|---|---:|---:|
| `02008D08` | 32 | 40 |
| `02005FF8` | 32 | 42 |
| `02008D12` | 23 | 24 |
| `02006002` | 23 | 24 |
| `02008BE0` | 2 | 276 |
| `0200906E` | 2 | 1518 |

This creates a branch feature missed by literal `TM1`:

```text
same cursor/state/TM1 + short hold
versus
same cursor/state/TM1 + long conditional hold
```

v2 records exact terminal hold frames plus normalized hold buckets.

## G. Mode35 branch axis

Notable transitions:

```text
00->FF 353
FF->00 237
02->00 128
FF->02 74
00->01 67
00->02 52
01->FF 39
```

Useful alignments:

- `00->FF` frequently occurs on `+0x0A` cursor progression;
- `02->00` can occur with cursor unchanged;
- `FF->02` frequently accompanies coarse phase `0A->1B`;
- `01->FF` frequently accompanies `1B->0A`.

Mode35 progression remains separate from timer34.

## H. Structural phase branches

Frequent compressed path:

```text
40,00,E8,1B,00
-> E0,A0,D8,0A,0C
-> 40,00,E8,1B,00
```

count 41.

Longer terminal branch:

```text
40,00,E8,1B,00
-> E0,A0,D8,0A,0C
-> 40,00,E8,1B,00
-> 48,00,00,1B,00
```

count 24.

Alternate entry:

```text
E0,00,38,0A,00
-> E0,A0,D8,0A,0C
```

count 38.

Rare boundary-only families `78,78,78,1E,0B` and `70,70,70,1E,0B` had no interior samples in retained boundary analysis.

## I. Context dimensions that must not be collapsed

Every candidate evaluation preserves or stratifies by:

- local type;
- cursor + embedded flags;
- exact and normalized timer path;
- terminal TM1 hold duration;
- mode35/gate37;
- full phase tuple;
- live target `+0x6D..+0x6E`;
- association `+0x3D..+0x3E/+0xC6`;
- split player reference `+0x6F/+0x68`;
- synchronization checkpoint `+0xCC`;
- profile `+0xB0/+0xB4/+0xB6`;
- capture, true scene label when available, slot/episode;
- target changes including the event edge.

## Promotion boundary

Local structural hotspots remain `discovery_correlation` until an exact local attack label creates same-cycle outcome evidence.

A Browser candidate remains only prospective until a separate Browser validator arms before ACTIVE and reports all future outcomes, misses, targets and sides.