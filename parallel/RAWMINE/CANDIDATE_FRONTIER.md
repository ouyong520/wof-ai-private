# RAWMINE Candidate Frontier

Updated: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

RAWMINE is a **candidate screener / evidence analyzer**, not a semantic owner. GEO/EFIELD own all semantic interpretation and promotion. RAWMINE evidence labels never mean semantic confirmation.

## Corpus / automated evidence contract

Current screen consumes **12 retained raw runs**:

- 7 EFIELD runs
- 5 GEO runs, including `GEO-0008-p1-depth-only-5s60-20260831-2115Z`

The bridge pipeline emits for all 23 objects and all `0x00..0xDF` offsets:

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

Current ranking revision: `v7-owner-sync-plus-geo-depth-manipulation-guard`.

## GEO — P1 X screen

Anchor supplied by GEO: changes in `256*U8(+0x0B)+U8(+0x04)`. This is anchor-derived evidence, not independent semantic confirmation.

Anchor events: **815**.

| Rank | Offset | Score | Evidence | Key control |
|---:|---:|---:|---|---|
| 1 | `+0x04` | 0.990552 | `STRONG_CANDIDATE` | horizontal recall 1.000000; precision 1.000000; vertical/Z-only recall 0 |
| 2 | `+0x9C` | 0.961746 | `STRONG_CANDIDATE` | horizontal recall 0.952147; vertical/Z-only recall 0.015723 |
| 3 | `+0x0C` | 0.690209 | `MODERATE_CANDIDATE` | vertical/Z-only recall 0.927673 |
| 4 | `+0x48` | 0.656761 | `MODERATE_CANDIDATE` | vertical/Z-only recall 0.921384 |
| 5 | `+0x0B` | 0.655153 | `MODERATE_CANDIDATE` | sparse 12 changes; precision 1.0; vertical/Z-only recall 0 |
| 6 | `+0x16` | 0.650429 | `INSUFFICIENT_COVERAGE` | one candidate event |
| 7 | `+0x11` | 0.636286 | `MODERATE_CANDIDATE` | vertical/Z-only recall 0.811321 |
| 8 | `+0xA3` | 0.620018 | `MODERATE_CANDIDATE` | sparse cache-family behavior |
| 9 | `+0x47` | 0.573755 | `WEAK_CANDIDATE` | sparse; best lag -1 |
| 10 | `+0x4F` | 0.569728 | `WEAK_CANDIDATE` | horizontal recall 0.204908 |

RAWMINE only records that `+0x04` is the strongest single-offset discriminator under the GEO-owned anchor and `+0x0B` is a sparse highly specific companion. GEO remains the semantic owner.

## GEO — P1 floor/depth Y screen

The original retained natural corpus still has only **1** `+0x08` anchor change and therefore remains insufficient for owner-independent ranking.

The owner then supplied a dedicated controlled task:

`GEO-0008-p1-depth-only-5s60-20260831-2115Z`

RAWMINE added a manipulation-validity guard on top of collector health. The raw is mechanically healthy and its orthogonal controls are clean:

- frames / transitions: `300 / 299`
- reconstructed X (`+0x04/+0x0B`) changes: `0`
- reconstructed Z (`+0x0C/+0x11`) changes: `0`
- X/Z control validity: `PASS`

But the intended P1 floor/depth manipulation is absent from player-object evidence:

- `+0x08` changes: `0`
- no byte reaches all of: `>=5` P1 changes, `>=0.80` P1-specificity, `<=0.05` untouched-P2/P3 change rate
- `+0x7F` is dynamic but is similarly dynamic in untouched P2/P3, so it is not a P1-specific controlled candidate

Automated verdict:

`CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

This is **not negative evidence against `+0x08`** and not support for `+0x7F`. It means the first controlled scene failed to create a discriminative P1 depth trajectory.

A single narrow retry is already queued:

`RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`

It requires visible repeated P1 UP/DOWN traversal in an open walkable area, P2/P3 untouched, no LEFT/RIGHT/jump/attack, with the same X/Z contamination guards. The bridge consumes this retry automatically when its raw arrives.

## EFIELD — owner-bounded residual screens

EFIELD has completed the current bounded high-value field-mapping phase. RAWMINE therefore keeps all EFIELD screens evidence-only and does **not** request generic capture.

### Lifecycle / execution-boundary residual

Owner question remains closed: no byte-level direct active/inactive gate is better supported than owner-confirmed `+0x24`. Current unresolved residual Top 10 remain weak:

`+0x36, +0xA2, +0x08, +0x14, +0x0D, +0xBA, +0xD1, +0xAA, +0x19, +0xB7`.

No residual candidate reopens the direct-gate hypothesis.

### Retarget precursor residual

Owner question remains closed: no selective universal pre-commit signal is established in the current corpus. High residual scores are dominated by persistent pre-state association under a tiny same-type event set and are not universal-precursor proof.

Current Top 10:

`+0xB0, +0xD3, +0xC7, +0xA6, +0xAA, +0x08, +0xA2, +0xC0, +0x41, +0x7E`.

### Executor transition

Owner-supplied logical cursor transition anchor remains evidence-only. Current Top 10:

`+0x14, +0x42, +0x72, +0x1B, +0x37, +0x36, +0x04, +0x9C, +0x71, +0x09`.

No unresolved byte is semantically renamed by RAWMINE.

### Action/state neighborhood

Anchor: same-type frames where any owner-confirmed phase projection `+0x6C/+0x70/+0x73/+0x77` changes. `+0x72` is intentionally excluded from the anchor to avoid circularity.

Current Top 10:

1. `+0x72` — 0.942900 `STRONG_CANDIDATE`
2. `+0x14` — 0.773813 `MODERATE_CANDIDATE`
3. `+0x1B` — 0.720564 `MODERATE_CANDIDATE`
4. `+0x37` — 0.690211 `MODERATE_CANDIDATE`
5. `+0x36` — 0.645758 `MODERATE_CANDIDATE`
6. `+0x71` — 0.642964 `MODERATE_CANDIDATE`
7. `+0x42` — 0.607922 `MODERATE_CANDIDATE`
8. `+0xCE` — 0.527360 `WEAK_CANDIDATE`
9. `+0x6A` — 0.517619 `WEAK_CANDIDATE`
10. `+0xC9` — 0.513613 `WEAK_CANDIDATE`

Owner spotlight under this exact narrow screen:

- `+0x72`: rank 1
- `+0x37`: rank 4
- `+0x2E`: rank 17
- `+0x2D`: rank 27

This does not override EFIELD owner-level `STRONG_CANDIDATE` classifications for `+0x2D/+0x2E/+0x37/+0x72` on broader structural evidence.

## Current stop / continuation condition

- EFIELD: no generic acquisition justified; current bounded phase is complete.
- GEO P1 X: existing owner anchor is already well screened; no RAWMINE-owned semantic promotion.
- GEO P1 Y/depth: first controlled raw is bounded as **ineffective manipulation**, not as a field verdict.
- Active RAWMINE acquisition: only `RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`.

No second parallel retry or generic capture should be queued while that operator-gated task is active. Once it completes, the bridge pipeline automatically reruns all neutral evidence and the controlled manipulation guard, after which RAWMINE either hands a valid ranked candidate set back to GEO or records another explicit coverage failure without inventing semantics.
