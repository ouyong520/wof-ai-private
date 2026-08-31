# RAWMINE Role

Updated: 2026-09-01
Lane: `RAWMINE-*` only
Namespace: WinKawaks normalized Collector raw evidence

## Responsibility

RAWMINE is the automatic candidate screener / evidence analyzer for the GEO and EFIELD lanes.

RAWMINE does **not** own final field semantics. A high correlation, clean transition, narrow value domain, or strong cluster is evidence for a candidate only. Semantic naming and promotion remain with the owning research lane after targeted validation.

RAWMINE may read:

- `parallel/GEO/**`
- `parallel/EFIELD/**`
- existing `GEO-*`, `EFIELD-*`, and `RAWMINE-*` Collector raw captures
- bridge-side discovery reports needed as statistical substrate

RAWMINE may write only:

- `parallel/RAWMINE/**`
- bridge-side `analysis/rawmine/**`, RAWMINE workflows, and `results/rawmine/**` analysis outputs
- Collector task/status/result paths using the `RAWMINE-` prefix when a new capture is genuinely required

It must not modify GEO/EFIELD-owned files, mainline coordinator files, production-shadow rules, WOF-045, or game memory.

## Authoritative output contract

For existing raw data RAWMINE should automatically provide:

1. per-object / per-offset change frequency;
2. zero->nonzero and nonzero->zero counts;
3. value domain statistics;
4. neutral U8/U16/U32 minimum-reasonable-width evidence;
5. same-frame and neighboring-frame linkage;
6. transition/event windows;
7. pair and cluster correlation;
8. a Top 10 candidate list for each concrete question supplied by GEO/EFIELD.

Generic rows use offsets and evidence only. Avoid generic semantic labels such as `coordinate`, `target`, `attack`, `timer`, `state`, or `flag` unless the term appears only in the owning lane's question/anchor description.

## Candidate strength vocabulary

RAWMINE may classify evidence strength as:

- `STRONG_CANDIDATE`
- `MODERATE_CANDIDATE`
- `WEAK_CANDIDATE`
- `INSUFFICIENT_COVERAGE`

These labels describe screening evidence, not semantic confirmation.

RAWMINE must not emit `CONFIRMED` for field meaning.

## Current upstream questions

Read-only upstream frontiers currently define the following screening questions:

### GEO

- `GEO_P1_X`: rank P1 offsets against the GEO-owned world-X movement anchor.
- `GEO_P1_Y`: rank P1 offsets against the GEO-owned `+0x08` floor/depth movement anchor.

The anchor is supplied by GEO and therefore cannot be independently confirmed by RAWMINE using the same anchor-derived labels.

### EFIELD

- `EFIELD_EXECUTION_BOUNDARY`: around `+0x24` zero/nonzero lifecycle boundaries, rank other offsets that may distinguish execution active/inactive behavior more directly; exclude the `+0x24` anchor and owner-rejected `+0x00`.
- `EFIELD_RETARGET_PRECURSOR`: around same-type known-player `+0x6D..0x6E` retarget events, rank possible precursor offsets using exact/neighbor windows plus prior lookback evidence.

RAWMINE must report the winning offsets only as candidates for these questions; EFIELD decides whether any candidate deserves a semantic name.

## Current implementation

Bridge-side authoritative candidate screener:

- `analysis/rawmine/candidate_screen.py`
- `.github/workflows/rawmine-candidate-screen.yml`

Outputs:

- `results/rawmine/candidate_screen.json` — detailed per-object evidence
- `results/rawmine/candidate_screen_summary.json` — compact machine-readable Top 10 + digests
- `results/rawmine/candidate_screen_summary.md` — compact human-readable report

Historical RAWMINE reports remain useful statistical substrate, but older heuristic/semantic-ish labels are not authoritative under this role definition.

## Evidence boundary

All results are `WinKawaks-local-discovery-only` and read-only.

Never assume WinKawaks normalized offsets equal Browser/WASM offsets. RAWMINE cannot promote a local candidate into a Browser production rule; Browser/Web prospective validation remains required for production-context conclusions.
