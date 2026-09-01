# SWEEPATLAS Attack Atlas

Updated: 2026-09-01

Evidence class: `WinKawaks-local-discovery-only`

## Semantic boundary

This atlas records **attack-associated executor phase structure**, not exact move names and not Browser Future Danger / ACTIVE semantics.

The retained EFIELD owner analysis uses:

- enemy `+0x73` U8 as a coarse attack-associated executor family;
- enemy `+0x6C` U8 as a finer executor subphase feeding that family;
- enemy `+0x77` U8 as a second phase family;
- enemy `+0x70` U8 as an upstream phase paired with `+0x77`.

SWEEPATLAS does not interpret one numeric value as a punch, slash, startup, hit, recovery, or exact game move.

## Aggregate attack-associated episode coverage

Mechanical episode definition used by the retained bridge analysis:

```text
+0x24 != 0
and contiguous +0x73 != 0 run
```

Observed aggregate:

- attack-associated episodes: **271**
- median dwell: **31 frames**
- mean dwell: **58.934 frames**
- maximum dwell: **345 frames**

These are structural episodes across the retained EFIELD corpus, not human-labeled attacks.

## Coarse family `+0x73`

Observed values:

| Value | Run count / dwell summary |
|---|---|
| `0x00` | 242 runs; median 7.5; mean 24.28; max 116 |
| `0x0A` | 220 runs; median 18; mean 54.01; max 345 |
| `0x0B` | 13 runs; median 21; mean 20.85; max 33 |
| `0x1B` | 312 runs; median 11; mean 12.11; max 36 |
| `0x1E` | 14 runs; median 2.5; mean 2.79; max 4 |

Most frequent transitions include:

- `0x1B -> 0x00`: 183
- `0x00 -> 0x1B`: 175
- `0x0A -> 0x1B`: 132
- `0x1B -> 0x0A`: 123
- `0x00 -> 0x0A`: 61
- `0x0A -> 0x00`: 45

## Fine family `+0x6C`

Observed values include:

`0x00, 0x40, 0x48, 0x50, 0x58, 0x70, 0x78, 0x90, 0xE0`.

Strong recurrent transitions include:

- `0x00 -> 0x40`: 129
- `0x40 -> 0xE0`: 123
- `0xE0 -> 0x40`: 114
- `0x40 -> 0x00`: 81
- `0x00 -> 0xE0`: 61
- `0xE0 -> 0x00`: 45

The high repeat counts and paired joint states support use as a structural phase index, but they do not establish move names.

## Second family `+0x77` / upstream `+0x70`

Observed `+0x77` values:

`0x00, 0x0A, 0x0B, 0x0C, 0x14`.

Observed `+0x70` values include:

`0x00, 0x10, 0x28, 0x58, 0x70, 0x78, 0x80, 0xA0, 0xD8, 0xF8`.

Frequent `+0x77` transitions:

- `0x00 -> 0x0C`: 195
- `0x0C -> 0x00`: 179
- `0x00 -> 0x0A`: 122
- `0x0B -> 0x00`: 119
- `0x00 -> 0x0B`: 93
- `0x0A -> 0x00`: 76
- `0x14 -> 0x00`: 62

## Joint structural states

Top retained `(6C,70,72,73,77)` states:

| Joint state | Frames |
|---|---:|
| `E0,A0,D8,0A,0C` | 10,640 |
| `40,00,E8,1B,00` | 2,660 |
| `E0,00,38,0A,00` | 1,242 |
| `00,00,00,00,00` | 1,086 |
| `00,80,00,00,0B` | 1,032 |
| `00,D8,00,00,14` | 990 |

The most frequent joint transition is:

```text
40,00,E8,1B,00 -> E0,A0,D8,0A,0C : 123
```

with the reverse observed 113 times.

## `Txx -> attack` and `attack -> Txx` status

The user-requested exact relation requires type-conditioned attack values per capture/scene. The current retained human-readable aggregate reports establish the type population and the attack-phase population, but the GitHub-visible corpus does not provide a trustworthy stage/scene/wave label and this SWEEPATLAS session cannot directly decompress the private gzip raw bodies to regenerate a full type×attack contingency table.

Therefore the exact matrices are currently marked:

```text
Txx -> exact attack-associated values: PARTIAL / not regenerated here
attack-associated value -> exact Txx list: PARTIAL / not regenerated here
stage/scene/wave -> attack: UNKNOWN
```

This is intentionally stricter than inferring relations from independent aggregate counts.

## Scene-specific attacks

**UNRESOLVED.** No authoritative scene labels are attached to the seven natural EFIELD captures. A phase value appearing in the EFIELD aggregate cannot be called scene-specific without a scene-labeled denominator and comparison corpus.

## BASECAP ordinary-attack controls

Two retained BASECAP runs provide acquisition controls for P1 ordinary standing attack behavior:

- `BASECAP-B13R-standing-attack-ungated-60s60-20260901-0543Z` — 3,600 samples, PASS, read-only, retained raw.
- `BASECAP-B13-attack-12s60-20260901-0558Z` — 720 samples, PASS, read-only, retained raw.

Their operator contracts identify the action as P1 ordinary attack and require P2/P3 untouched, but the BASECAP catalog/RAWMINE audit did not find a material new enemy attack/action ranking from B13 versus B00. These captures are therefore control/acquisition evidence rather than a basis for naming enemy attack values.
