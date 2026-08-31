# RAWMINE Candidate-Screen Phase — Completion

Date: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`
Status: **COMPLETE for the current retained-raw / owner-question phase**

## Role boundary

RAWMINE is not a semantic reverse-engineering owner. It is the automatic candidate screener / evidence analyzer for GEO and EFIELD questions.

This completion therefore means the requested screening/evidence machinery is implemented and the current retained corpus has been exhausted against the active/bounded owner questions. It does **not** mean every object byte has a semantic name.

## Delivered automatic evidence

For all 23 normalized objects and all `0x00..0xDF` offsets, the bridge pipeline now emits:

1. offset change count and frequency;
2. zero->nonzero / nonzero->zero transitions;
3. value domains and compact frequency summaries;
4. neutral U8/U16/U32 minimum-reasonable-width evidence;
5. same-frame and neighboring-frame linkage (`lag -2..+2`);
6. transition/event windows;
7. pair correlation and connected clusters;
8. Top 10 rankings for concrete owner questions.

Bridge implementation / outputs:

- `analysis/rawmine/candidate_screen.py`
- `analysis/rawmine/candidate_screen_refine.py`
- `analysis/rawmine/candidate_screen_owner_sync.py`
- `.github/workflows/rawmine-candidate-screen.yml`
- `results/rawmine/candidate_screen.json`
- `results/rawmine/candidate_screen_summary.json`
- `results/rawmine/candidate_screen_summary.md`

Current corpus: 11 raw runs = 7 EFIELD + 4 GEO.

## Owner-question state

### GEO P1 X

Current raw provides a strong question-conditioned screen under the GEO-owned composite anchor. `+0x04` ranks first as a single-offset discriminator and `+0x0B` is a sparse highly specific companion. RAWMINE does not promote the coordinate semantics.

### GEO P1 Y

Current P1 raw contains only one `+0x08` anchor-change event. All Top 10 remain `INSUFFICIENT_COVERAGE`. This is the only current priority question that cannot be defensibly ranked from retained P1 evidence.

### EFIELD execution boundary

Owner question is closed: EFIELD found no better direct byte gate than `+0x24` in the retained corpus. RAWMINE now excludes owner-resolved/rejected fields and reports only residual boundary companions; all current Top 10 are weak evidence and do not reopen the owner conclusion.

### EFIELD retarget precursor

Owner question is closed: no selective universal pre-commit signal is established. RAWMINE now scopes out the confirmed target, stored association, split reference, synchronization checkpoint, resolved executor structures and owner-rejected same-frame alternatives before producing a residual Top 10. High residual scores are explicitly not interpreted as proof that a universal precursor exists.

### EFIELD executor / action-state neighborhood

RAWMINE added two owner-conditioned screens:

- coupling to logical executor cursor transitions;
- selectivity for owner-confirmed fine/coarse phase-transition frames.

The phase-transition screen places `+0x72` first and `+0x37` fourth, while `+0x2E` and `+0x2D` rank lower under that narrower exact-transition question. These are evidence rankings only and are compatible with EFIELD keeping all four at candidate level where appropriate.

EFIELD has formally closed its current bounded high-value field-mapping phase, so RAWMINE does not request additional generic EFIELD captures.

## Guardrails preserved

- read-only analysis only; no game-memory writes;
- no modification of Browser mainline or production-shadow rules;
- no WinKawaks numeric offset promoted directly into Browser/WASM;
- no `CONFIRMED` semantic labels issued by RAWMINE;
- GEO/EFIELD artifacts consumed read-only;
- RAWMINE writes remain in RAWMINE-owned paths and bridge RAWMINE analysis/results.

## Automatic continuation rule

The current phase is complete against existing raw. On any future eligible owner capture, the workflow automatically regenerates the generic evidence and owner-question rankings.

A new RAWMINE capture is justified only when an owner asks a concrete discriminative question that cannot be answered from already retained raw and is not already being collected by that owner lane.
