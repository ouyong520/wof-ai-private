# RAWMINE Candidate Frontier

Updated: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

RAWMINE is a **candidate screener / evidence analyzer**, not a semantic owner. GEO/EFIELD own all semantic interpretation and promotion. RAWMINE evidence labels never mean semantic confirmation.

## Corpus / automated evidence contract

Current screen consumes 11 retained raw runs:

- 7 EFIELD runs
- 4 GEO runs

The bridge pipeline automatically emits for all 23 objects and all `0x00..0xDF` offsets:

1. change count / frequency;
2. zero->nonzero and nonzero->zero counts;
3. value domain / unique count / min / max / concentration digest;
4. neutral `U8 / U16_CANDIDATE / U32_CANDIDATE / UNRESOLVED` minimum-width evidence;
5. same-frame and neighboring-frame linkage, lag `[-2,+2]`;
6. transition/event windows;
7. pair correlation and connected clusters;
8. owner-question Top 10 candidate rankings.

Authoritative bridge outputs:

- `results/rawmine/candidate_screen.json`
- `results/rawmine/candidate_screen_summary.json`
- `results/rawmine/candidate_screen_summary.md`

Current ranking revision: `v5-owner-sync-through-efield-round009-action-neighborhood`.

## GEO — P1 X screen

Anchor supplied by GEO: changes in `256*U8(+0x0B)+U8(+0x04)`. This is anchor-derived evidence, not independent semantic confirmation.

Anchor events: **815**.

| Rank | Offset | Score | Evidence | Key control |
|---:|---:|---:|---|---|
| 1 | `+0x04` | 0.990552 | `STRONG_CANDIDATE` | horizontal recall 1.000000; precision 1.000000; vertical/Z-only recall 0 |
| 2 | `+0x9C` | 0.961743 | `STRONG_CANDIDATE` | horizontal recall 0.952147; vertical/Z-only recall 0.015723 |
| 3 | `+0x0C` | 0.690209 | `MODERATE_CANDIDATE` | vertical/Z-only recall 0.927673, weak discriminator |
| 4 | `+0x48` | 0.656759 | `MODERATE_CANDIDATE` | vertical/Z-only recall 0.921384 |
| 5 | `+0x0B` | 0.655153 | `MODERATE_CANDIDATE` | sparse 12 changes; precision 1.0; vertical/Z-only recall 0 |
| 6 | `+0x16` | 0.650429 | `INSUFFICIENT_COVERAGE` | one candidate event |
| 7 | `+0x11` | 0.636286 | `MODERATE_CANDIDATE` | vertical/Z-only recall 0.811321 |
| 8 | `+0xA3` | 0.620018 | `MODERATE_CANDIDATE` | sparse cache-family behavior |
| 9 | `+0x47` | 0.573754 | `WEAK_CANDIDATE` | sparse; best lag -1 |
| 10 | `+0x4F` | 0.569726 | `WEAK_CANDIDATE` | horizontal recall 0.204908 |

RAWMINE only records that `+0x04` is the strongest single-offset discriminator under the GEO-owned anchor and `+0x0B` is a sparse highly specific companion. GEO remains the semantic owner.

## GEO — P1 floor/depth Y screen

Anchor supplied by GEO: `U8(+0x08)` changes.

Existing RAWMINE corpus contains only **1 P1 anchor event**, so every numerical rank remains `INSUFFICIENT_COVERAGE`:

`+0x16, +0x08, +0x06, +0x1B, +0x00, +0x14, +0x04, +0x98, +0x07, +0x90`.

This is a coverage statement only. RAWMINE does not use a one-event ranking to validate or reject GEO's Y hypothesis.

## EFIELD — lifecycle / execution-boundary residual screen

EFIELD has closed the owner question: in the retained corpus no byte-level direct active/inactive gate is better supported than owner-confirmed `+0x24` type-present. RAWMINE therefore scopes already resolved/rejected structures out and reports only residual boundary-companion evidence.

Top 10 unresolved residual offsets:

| Rank | Offset | Score | Evidence | Balanced boundary coverage | Replacement coverage |
|---:|---:|---:|---|---:|---:|
| 1 | `+0x36` | 0.560762 | `WEAK_CANDIDATE` | 0.140437 | 0.044341 |
| 2 | `+0xA2` | 0.555361 | `WEAK_CANDIDATE` | 0.575396 | 0.424222 |
| 3 | `+0x08` | 0.553734 | `WEAK_CANDIDATE` | 0.562721 | 0.450033 |
| 4 | `+0x14` | 0.533003 | `WEAK_CANDIDATE` | 0.391659 | 0.348114 |
| 5 | `+0x0D` | 0.532336 | `WEAK_CANDIDATE` | 0.780632 | 0.861681 |
| 6 | `+0xBA` | 0.513066 | `WEAK_CANDIDATE` | 0.023406 | 0.005956 |
| 7 | `+0xD1` | 0.511290 | `WEAK_CANDIDATE` | 0.027027 | 0.012574 |
| 8 | `+0xAA` | 0.500802 | `WEAK_CANDIDATE` | 0.132405 | 0.078094 |
| 9 | `+0x19` | 0.487723 | `WEAK_CANDIDATE` | 0.023406 | 0.020516 |
| 10 | `+0xB7` | 0.467850 | `WEAK_CANDIDATE` | 0.046812 | 0.042356 |

No residual candidate reopens the owner-closed direct-gate hypothesis.

## EFIELD — retarget precursor residual screen

EFIELD has also closed the current universal pre-commit precursor question: existing raw supports no selective universal pre-commit signal. RAWMINE now excludes owner-resolved/rejected live-target, stored-association, split-reference, synchronization, executor, same-frame companion and locomotion fields before ranking residuals.

Top 10 residual offsets:

| Rank | Offset | Score | Evidence | Adjusted pre-target purity | Prior <=600 | Prior >=30 | +/-2 commit |
|---:|---:|---:|---|---:|---:|---:|---:|
| 1 | `+0xB0` | 0.849496 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 1.000000 | 0 |
| 2 | `+0xD3` | 0.848681 | `STRONG_CANDIDATE` | 1.000000 | 1.000000 | 0.833333 | 0.166667 |
| 3 | `+0xC7` | 0.848611 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 1.000000 | 0 |
| 4 | `+0xA6` | 0.847978 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 1.000000 | 0 |
| 5 | `+0xAA` | 0.831968 | `STRONG_CANDIDATE` | 0.625000 | 1.000000 | 1.000000 | 0 |
| 6 | `+0x08` | 0.812610 | `STRONG_CANDIDATE` | 0.600000 | 1.000000 | 1.000000 | 0 |
| 7 | `+0xA2` | 0.812589 | `STRONG_CANDIDATE` | 0.600000 | 1.000000 | 1.000000 | 0 |
| 8 | `+0xC0` | 0.807401 | `STRONG_CANDIDATE` | 0.833333 | 0.833333 | 0.833333 | 0 |
| 9 | `+0x41` | 0.798589 | `STRONG_CANDIDATE` | 0.500000 | 1.000000 | 1.000000 | 0 |
| 10 | `+0x7E` | 0.797935 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 0.666667 | 0 |

These scores mainly express persistent pre-state association in a tiny six-event same-type retarget set. They are follow-up candidates only and do not contradict EFIELD's closed result that no universal selective precursor is established.

## EFIELD — executor transition screen

Anchor supplied by EFIELD: same-type logical `U32BE(+0x2F..+0x32)` transitions after masking `0x001C0000`; exact logical `+0x0A` sequence steps are scored separately. Known cursor/dwell/control and confirmed fine/coarse projection bytes are excluded.

Top 10:

| Rank | Offset | Score | Evidence | Cursor exact recall | +0x0A recall | +/-2 recall |
|---:|---:|---:|---|---:|---:|---:|
| 1 | `+0x14` | 0.820887 | `STRONG_CANDIDATE` | 0.962268 | 0.973398 | 0.970753 |
| 2 | `+0x42` | 0.737803 | `MODERATE_CANDIDATE` | 0.979419 | 0.975249 | 0.987362 |
| 3 | `+0x72` | 0.594821 | `MODERATE_CANDIDATE` | 0.612565 | 0.621559 | 0.628092 |
| 4 | `+0x1B` | 0.589484 | `MODERATE_CANDIDATE` | 0.619968 | 0.573676 | 0.644340 |
| 5 | `+0x37` | 0.428125 | `WEAK_CANDIDATE` | 0.275862 | 0.328013 | 0.284347 |
| 6 | `+0x36` | 0.393155 | `WEAK_CANDIDATE` | 0.288319 | 0.254916 | 0.295541 |
| 7 | `+0x04` | 0.373897 | `WEAK_CANDIDATE` | 0.344467 | 0.352533 | 0.389240 |
| 8 | `+0x9C` | 0.370214 | `WEAK_CANDIDATE` | 0.343564 | 0.339116 | 0.389059 |
| 9 | `+0x71` | 0.364088 | `WEAK_CANDIDATE` | 0.210146 | 0.201018 | 0.220979 |
| 10 | `+0x09` | 0.357545 | `WEAK_CANDIDATE` | 0.317927 | 0.326162 | 0.340495 |

This is coupling evidence only. It does not assign executor semantics to any unresolved offset.

## EFIELD — action/state-neighborhood screen

Current owner-bounded question concerned `+0x2D`, `+0x2E`, `+0x37` without inventing attack-stage semantics. RAWMINE uses only owner-confirmed phase projections as the event anchor: same-type frames where any of `+0x6C/+0x70/+0x73/+0x77` changes, with same-type non-transition frames as controls. The anchor intentionally excludes unresolved `+0x72` to avoid circularity.

Top 10:

| Rank | Offset | Score | Evidence | Exact phase recall | Candidate precision | Control rate | Lift |
|---:|---:|---:|---|---:|---:|---:|---:|
| 1 | `+0x72` | 0.942900 | `STRONG_CANDIDATE` | 0.969118 | 0.788466 | 0.00179130 | 541.012x |
| 2 | `+0x14` | 0.773813 | `MODERATE_CANDIDATE` | 0.964706 | 0.471739 | 0.03711075 | 25.995x |
| 3 | `+0x1B` | 0.720564 | `MODERATE_CANDIDATE` | 0.717353 | 0.571864 | 0.01802160 | 39.805x |
| 4 | `+0x37` | 0.690211 | `MODERATE_CANDIDATE` | 0.448824 | 0.796867 | 0.00003619 | 12402.565x |
| 5 | `+0x36` | 0.645758 | `MODERATE_CANDIDATE` | 0.412941 | 0.700949 | 0.00360070 | 114.684x |
| 6 | `+0x71` | 0.642964 | `MODERATE_CANDIDATE` | 0.342353 | 0.836207 | 0 | very high / zero-control denominator |
| 7 | `+0x42` | 0.607922 | `MODERATE_CANDIDATE` | 0.968824 | 0.071343 | 0.61280692 | 1.581x |
| 8 | `+0xCE` | 0.527360 | `WEAK_CANDIDATE` | 0.121765 | 0.799228 | 0.00025332 | 480.684x |
| 9 | `+0x6A` | 0.517619 | `WEAK_CANDIDATE` | 0.115000 | 0.765166 | 0.00057901 | 198.616x |
| 10 | `+0xC9` | 0.513613 | `WEAK_CANDIDATE` | 0.092353 | 0.805128 | 0.00019903 | 464.006x |

Owner-requested spotlight under the same neutral score:

- `+0x72`: rank 1, `STRONG_CANDIDATE`;
- `+0x37`: rank 4, `MODERATE_CANDIDATE`;
- `+0x2E`: rank 17, `WEAK_CANDIDATE`;
- `+0x2D`: rank 27, `WEAK_CANDIDATE`.

This does not conflict with EFIELD Round 010, which keeps `+0x2D/+0x2E/+0x37` candidate-level on broader structural evidence and explicitly refuses value-level gameplay semantics. The RAWMINE ranking asks a narrower question: exact coupling to confirmed phase-transition frames.

## Current owner state / stop condition

EFIELD has completed its current bounded high-value field-mapping phase. Its remaining unknowns are explicitly not generic-capture work. RAWMINE therefore does not enqueue more EFIELD raw merely to improve statistics.

For existing raw, RAWMINE's required automatic evidence contract is implemented and current owner-scoped Top 10 screens are regenerated automatically by the bridge workflow. Future eligible GEO/EFIELD/RAWMINE captures trigger the same pipeline.

GEO P1 Y remains the only priority question here that is still coverage-limited in the retained RAWMINE corpus. RAWMINE will consume a future owner-provided discriminative capture automatically; it will not infer semantic confirmation from the present one-event set.
