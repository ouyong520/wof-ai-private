# RAWMINE Candidate-Screen Phase — Completion

Date: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`
Status: **COMPLETE for the current GEO/EFIELD owner-question assignment**

## Role boundary

RAWMINE is not a semantic reverse-engineering owner. It is the automatic candidate screener / evidence analyzer for GEO and EFIELD questions.

Completion means the requested automatic screening machinery is implemented and the currently active owner questions have either been exhausted or handed back with discriminative evidence. It does not mean every byte has a semantic name.

## Delivered automatic evidence

The RAWMINE bridge pipeline now covers:

1. per-object offset change count/frequency;
2. zero->nonzero / nonzero->zero transitions;
3. value domains and compact frequency summaries;
4. neutral minimum-reasonable-width evidence;
5. same-frame and neighboring-frame linkage;
6. transition/event windows;
7. pair correlation and clusters;
8. concrete owner-question Top 10 rankings;
9. controlled-manipulation validity guards;
10. controlled attempt history and timing discriminators.

Key implementations / outputs:

- `analysis/rawmine/candidate_screen.py`
- `analysis/rawmine/candidate_screen_refine.py`
- `analysis/rawmine/candidate_screen_owner_sync.py`
- `analysis/rawmine/candidate_screen_geo_depth.py`
- `analysis/rawmine/player_slot_depth_long_window.py`
- `analysis/rawmine/depth_pair_timing.py`
- `.github/workflows/rawmine-candidate-screen.yml`
- `.github/workflows/rawmine-slot-attribution.yml`
- `results/rawmine/candidate_screen*.json`
- `results/rawmine/player_slot_depth_long_window.json`
- `results/rawmine/depth_pair_timing.json`

## Owner-question state

### GEO P1 X

Existing evidence remains sufficient for RAWMINE's screening role: `+0x04` is the strongest single-offset discriminator under the GEO-owned composite-X anchor and `+0x0B` is a sparse highly specific companion. RAWMINE does not assign final coordinate semantics.

### GEO P1 Y / floor-depth

The final timing-robust controlled raw is:

`RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`

Collector health:

- 2400 frames;
- 59.981 Hz;
- 0 read errors;
- 0 frame-size errors;
- read-only PASS.

The optional horizontal movement-attribution guard failed because all reconstructed player X composites stayed unchanged. That failure is explicitly scoped to independent slot-attribution via horizontal motion.

The retained raw nevertheless contains strong P1-only controlled depth-correlated evidence in the Collector's structurally ordered P1 object:

- `+0x08`: 536 events, specificity 1.0, untouched P2/P3 rate 0, bidirectional score 0.955224;
- `+0xA2`: 536 events, specificity 1.0, untouched P2/P3 rate 0, bidirectional score 0.966418;
- equal observed domain: 63..143 / 81 values.

The dedicated timing discriminator finds the dominant exact relationship:

`A2[t] == 08[t-1]`

for 2116 / 2399 comparable frames = 0.882034. Same-frame equality is only 0.736667. When both bytes change, their delta sign agrees 100%.

This is strong neutral evidence that the two fields track the same varying quantity at different temporal stages, with `+0xA2` trailing `+0x08` by one frame in the dominant relationship. GEO owns the final decision about current/live vs cached depth semantics, width, scale, and promotion.

Handoff state: `READY_FOR_GEO_OWNER_PROMOTION_DECISION`.

### EFIELD

EFIELD has formally closed its bounded high-value field-mapping phase. RAWMINE retains its residual lifecycle, retarget, executor, and action/state rankings as evidence only and requests no further generic capture.

## Guardrails preserved

- read-only analysis only; no game-memory writes;
- no modification of Browser mainline or production-shadow rules;
- no WinKawaks numeric offset promoted directly into Browser/WASM;
- no `CONFIRMED` semantic labels issued by RAWMINE;
- GEO/EFIELD artifacts consumed read-only;
- RAWMINE private writes remain under `parallel/RAWMINE/**`.

## Final stop rule

There are no active RAWMINE operator-gated tasks. The current RAWMINE assignment is complete.

Future work is justified only by a new concrete GEO/EFIELD ambiguity that cannot be discriminated from the retained corpus.
