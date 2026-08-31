# RAWMINE Candidate Frontier

Updated: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

RAWMINE is a **candidate screener / evidence analyzer**, not a semantic owner. All classifications below describe evidence strength only. GEO/EFIELD own final interpretation and promotion.

## Corpus and automatic outputs

Current candidate screen consumes all existing eligible raw captures:

- 7 EFIELD runs
- 4 GEO runs
- 11 total runs

The bridge candidate-screen pipeline now automatically emits:

1. all 23 objects x all `0x00..0xDF` offsets: change count/frequency;
2. zero->nonzero / nonzero->zero counts;
3. value-domain statistics including unique count, min/max and compact explicit domains;
4. neutral `U8 / U16_CANDIDATE / U32_CANDIDATE / UNRESOLVED` minimum-width evidence;
5. same-frame pair linkage and best neighboring lag in `[-2,+2]`;
6. per-object event-window digests;
7. strong pair and connected correlation clusters;
8. problem-specific Top 10 candidate rankings.

Authoritative bridge outputs:

- `results/rawmine/candidate_screen.json`
- `results/rawmine/candidate_screen_summary.json`
- `results/rawmine/candidate_screen_summary.md`

## Question: P1 X candidate screening

Anchor supplied by GEO: changes in `256*U8(+0x0B)+U8(+0x04)`.
This screen is anchor-derived and therefore is **not independent confirmation** of the GEO model.

Anchor events: **815**.

| Rank | Offset | Score | Evidence class | Key screening evidence |
|---:|---:|---:|---|---|
| 1 | `+0x04` | 0.990552 | `STRONG_CANDIDATE` | horizontal recall 1.000000; precision 1.000000; vertical/Z-only recall 0; static noise 0; small circular delta 0.905521 |
| 2 | `+0x9C` | 0.961743 | `STRONG_CANDIDATE` | horizontal recall 0.952147; precision 0.950980; vertical/Z-only recall 0.015723; static noise 0.001386 |
| 3 | `+0x0C` | 0.690209 | `MODERATE_CANDIDATE` | horizontal recall 0.750920 but vertical/Z-only recall 0.927673, so poor discriminator |
| 4 | `+0x48` | 0.656759 | `MODERATE_CANDIDATE` | horizontal recall 0.873620 but vertical/Z-only recall 0.921384 |
| 5 | `+0x0B` | 0.655153 | `MODERATE_CANDIDATE` | only 12 change events; all aligned to horizontal-anchor events; no vertical/Z-only events |
| 6 | `+0x16` | 0.650429 | `INSUFFICIENT_COVERAGE` | only one candidate change event |
| 7 | `+0x11` | 0.636286 | `MODERATE_CANDIDATE` | horizontal recall 0.761963 but vertical/Z-only recall 0.811321 |
| 8 | `+0xA3` | 0.620018 | `MODERATE_CANDIDATE` | 12 change events; 0.833333 precision; low vertical/Z-only overlap |
| 9 | `+0x47` | 0.573754 | `WEAK_CANDIDATE` | sparse; best lag -1; horizontal recall only 0.011043 |
| 10 | `+0x4F` | 0.569726 | `WEAK_CANDIDATE` | horizontal recall 0.204908; vertical/Z-only recall 0.361635 |

RAWMINE conclusion: `+0x04` is the strongest single-offset screen under the GEO-provided X anchor. `+0x9C` is also highly correlated but RAWMINE does not decide which is authoritative. `+0x0B` is sparse but highly specific and should be treated as a companion candidate rather than rejected by low recall alone.

## Question: P1 floor/depth Y candidate screening

Anchor supplied by GEO: `U8(+0x08)` change events.

Current existing corpus contains only **1 anchor change event**. Therefore **all Top 10 are `INSUFFICIENT_COVERAGE`**, regardless of numerical score.

Tentative order only:

| Rank | Offset | Status |
|---:|---:|---|
| 1 | `+0x16` | `INSUFFICIENT_COVERAGE` |
| 2 | `+0x08` | `INSUFFICIENT_COVERAGE` |
| 3 | `+0x06` | `INSUFFICIENT_COVERAGE` |
| 4 | `+0x1B` | `INSUFFICIENT_COVERAGE` |
| 5 | `+0x00` | `INSUFFICIENT_COVERAGE` |
| 6 | `+0x14` | `INSUFFICIENT_COVERAGE` |
| 7 | `+0x04` | `INSUFFICIENT_COVERAGE` |
| 8 | `+0x98` | `INSUFFICIENT_COVERAGE` |
| 9 | `+0x07` | `INSUFFICIENT_COVERAGE` |
| 10 | `+0x90` | `INSUFFICIENT_COVERAGE` |

RAWMINE conclusion: existing raw cannot meaningfully discriminate P1 Y candidates. This is a coverage result, not negative evidence against `+0x08` or any other candidate. GEO owns the controlled depth-only follow-up.

## Question: EFIELD execution-boundary companion candidate

Owner question: around `+0x24` zero/nonzero lifecycle boundaries, is there an unresolved offset with more direct active/inactive execution behavior without conflating nonzero->nonzero type replacement?

Query scoping excludes owner-resolved/rejected `+0x00`, `+0x24`, `+0x34`, `+0x6D`, `+0x6E` so the ranking surfaces unresolved follow-up candidates.

Ranking rewards balanced enter/exit coverage and boundary/background enrichment, while explicitly penalizing changes on nonzero->nonzero type replacement.

| Rank | Offset | Score | Evidence class | Balanced boundary coverage | Type-replacement change coverage | Boundary/background enrichment |
|---:|---:|---:|---|---:|---:|---:|
| 1 | `+0x2E` | 0.618542 | `MODERATE_CANDIDATE` | 0.464991 | 0.101257 | 111.973x |
| 2 | `+0x35` | 0.579157 | `WEAK_CANDIDATE` | 0.140437 | 0.043680 | 75.152x |
| 3 | `+0x36` | 0.560762 | `WEAK_CANDIDATE` | 0.140437 | 0.044341 | 48.925x |
| 4 | `+0xA2` | 0.555361 | `WEAK_CANDIDATE` | 0.575396 | 0.424222 | 66.748x |
| 5 | `+0x08` | 0.553734 | `WEAK_CANDIDATE` | 0.562721 | 0.450033 | 66.053x |
| 6 | `+0x14` | 0.533003 | `WEAK_CANDIDATE` | 0.391659 | 0.348114 | 28.189x |
| 7 | `+0x0D` | 0.532336 | `WEAK_CANDIDATE` | 0.780632 | 0.861681 | 43.274x |
| 8 | `+0xBB` | 0.519982 | `WEAK_CANDIDATE` | 0.648226 | 0.866976 | 149.879x |
| 9 | `+0x32` | 0.519485 | `WEAK_CANDIDATE` | 0.415417 | 0.358041 | 28.838x |
| 10 | `+0xB9` | 0.517561 | `WEAK_CANDIDATE` | 0.642709 | 0.909332 | 37.578x |

RAWMINE conclusion: `+0x2E` is the current strongest **unresolved candidate for this EFIELD question** because it combines substantially lower type-replacement conflation with roughly 112x boundary enrichment. RAWMINE does not name its semantics; EFIELD must validate it against concrete execution-active/inactive episodes.

## Question: enemy same-type retarget precursor screening

Anchor supplied by EFIELD: same-type known-player changes of `U16BE(+0x6D..+0x6E)`.

This ranking is intentionally different from a simple commit-frame co-change list. It prioritizes:

- candidate value at `t-1` predicting the new target label without high-cardinality overfit;
- prior change coverage up to 600 frames;
- persistence of the most recent prior change for >=3 / >=30 frames;
- low background change rate;
- commit-neighborhood co-change only as a small secondary term.

| Rank | Offset | Score | Evidence class | Adjusted pre-target predictive purity | Prior <=600 coverage | Prior >=30 coverage | +/-2 commit coverage | Background change rate |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 1 | `+0x2D` | 0.896131 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 1.000000 | 1.000000 | 0.00193434 |
| 2 | `+0x68` | 0.858205 | `STRONG_CANDIDATE` | 1.000000 | 0.833333 | 0.833333 | 0.000000 | 0.00006412 |
| 3 | `+0x35` | 0.852759 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 1.000000 | 0.166667 | 0.00278716 |
| 4 | `+0xB0` | 0.849496 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 1.000000 | 0.000000 | 0.00025221 |
| 5 | `+0xD3` | 0.848681 | `STRONG_CANDIDATE` | 1.000000 | 1.000000 | 0.833333 | 0.166667 | 0.02565939 |
| 6 | `+0xC7` | 0.848611 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 1.000000 | 0.000000 | 0.00069465 |
| 7 | `+0xA6` | 0.847978 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 1.000000 | 0.000000 | 0.00101099 |
| 8 | `+0x2E` | 0.833339 | `STRONG_CANDIDATE` | 0.666667 | 1.000000 | 0.833333 | 1.000000 | 0.00416364 |
| 9 | `+0xAA` | 0.831968 | `STRONG_CANDIDATE` | 0.625000 | 1.000000 | 1.000000 | 0.000000 | 0.00276578 |
| 10 | `+0x31` | 0.827208 | `STRONG_CANDIDATE` | 0.500000 | 1.000000 | 1.000000 | 0.666667 | 0.00306288 |

RAWMINE conclusion: by the composite precursor score `+0x2D` ranks first. `+0x68` is a particularly high-value distinct candidate because its pre-target predictive purity is 1.0, it has 5/6 prior-600 and >=30-frame coverage, **zero** +/-2 commit co-change, and an extremely low background-change rate; that pattern deserves targeted EFIELD examination as a persistent precursor rather than a commit-frame follower. RAWMINE does not assign it a semantic name.

## Width / pair / cluster use

The detailed JSON retains per-object minimal-width evidence and pair/cluster relations. These are screening aids only:

- `U16_CANDIDATE` / `U32_CANDIDATE` means adjacent-byte carry/boundary behavior is strong enough that U8 alone may be incomplete.
- `U8` means no strong adjacent carry evidence was found; it does not prove the field is semantically scalar U8.
- cluster membership means offsets share change timing; it does not mean they are one logical field or share a semantic role.

## Next RAWMINE behavior

On every future eligible GEO/EFIELD/RAWMINE raw capture, the candidate-screen workflow reruns automatically and refreshes all per-object evidence plus the problem Top 10 lists.

RAWMINE should not request a new capture merely to improve generic statistics. A new `RAWMINE-*` capture is justified only when the owning GEO/EFIELD question cannot be discriminated from existing raw and the required scene is not already being collected by the owner lane.
