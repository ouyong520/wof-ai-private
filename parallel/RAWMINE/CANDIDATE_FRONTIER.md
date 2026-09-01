# RAWMINE Candidate Frontier

Updated: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

RAWMINE is a neutral candidate screener / evidence analyzer. GEO and EFIELD own semantic interpretation and promotion. No WinKawaks offset is promoted to Browser production truth here.

## Automated evidence contract

The bridge RAWMINE pipeline provides, across normalized objects and offsets:

1. change count / frequency;
2. zero->nonzero and nonzero->zero transitions;
3. value domains and minimum-reasonable-width evidence;
4. same-frame and neighboring-frame coupling;
5. transition/event windows;
6. pair / cluster correlation;
7. concrete owner-question Top 10 rankings;
8. controlled-manipulation guards and attempt history.

Authoritative bridge outputs include:

- `results/rawmine/candidate_screen.json`
- `results/rawmine/candidate_screen_summary.json`
- `results/rawmine/candidate_screen_summary.md`
- `results/rawmine/player_slot_depth_long_window.json`
- `results/rawmine/depth_pair_timing.json`

## GEO — P1 X

Existing owner-conditioned evidence remains unchanged:

- `+0x04` is the strongest single-offset discriminator under the GEO-owned composite-X anchor;
- `+0x0B` is a sparse, highly specific companion;
- RAWMINE does not assign final coordinate semantics.

## GEO — P1 floor/depth evidence

Earlier controlled attempts (`GEO-0008`, `RAWMINE-001`, and short attribution-calibration retries) were mechanically healthy but did not contain a usable controlled depth trajectory. Those failures were coverage failures, not negative evidence against `+0x08`.

The timing-robust wide-window task:

`RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`

completed successfully with:

- 2400 frames / 2399 transitions;
- ~59.981 Hz;
- 0 read errors;
- 0 frame-size errors;
- read-only contract PASS;
- P2/P3 untouched as controls.

The long-window screen found no reconstructed X motion in any player slot, so the optional movement-based slot-attribution guard remained `FAIL`. This prevents RAWMINE from using the missing horizontal segment as independent player-attribution proof. It does **not** erase the depth-manipulation evidence present in the Collector's structurally ordered P1 object.

Under P1 object 0, while reconstructed X/Z remained stable:

- `+0x08`: 536 changes, P2/P3 control change rate 0, P1 specificity 1.0, bidirectional score 0.955224;
- `+0xA2`: 536 changes, P2/P3 control change rate 0, P1 specificity 1.0, bidirectional score 0.966418;
- both have the same observed domain: 63..143 with 81 distinct values;
- `+0x16`: only 68 changes and a two-value domain {6,7}; its event Jaccard with `+0x08` is only 0.090253, so it is a sparse companion/state discriminator rather than a peer continuous-value candidate under this question.

Dedicated pair timing further separates `+0x08` and `+0xA2`:

- same-frame change hits: 424 / 536;
- same-frame event Jaccard: 0.654321;
- when both change, delta sign agrees 100%;
- best exact value-copy relationship is `A2[t] == 08[t-1]`;
- that one-frame trailing copy holds for 2116 / 2399 comparable frames = **0.882034**;
- same-frame equality is lower at 0.736667.

RAWMINE interpretation: this is strong neutral timing evidence that `+0x08` and `+0xA2` represent the same underlying continuously varying quantity at different temporal stages, with `+0xA2` trailing `+0x08` by one frame in the dominant relationship. This is consistent with GEO's prior live-vs-cache distinction, but RAWMINE does not promote either byte semantically.

### P1 Y/depth handoff status

`READY_FOR_GEO_OWNER_PROMOTION_DECISION`

No further RAWMINE capture is justified for this question unless GEO identifies a new concrete ambiguity that cannot be discriminated from the retained 2400-frame raw.

## EFIELD

EFIELD's bounded high-value mapping phase is complete. RAWMINE keeps the existing residual lifecycle, retarget, executor-transition, and action/state rankings evidence-only and requests no generic EFIELD acquisition.

## Current lane stop condition

- EFIELD: no further RAWMINE acquisition justified.
- GEO P1 X: already screened; semantic ownership remains GEO.
- GEO P1 Y/depth: wide-window controlled evidence and `+0x08/+0xA2` timing discriminator are complete and handed back to GEO.
- Active RAWMINE operator-gated tasks: **none**.

Current RAWMINE assignment is complete. Future work starts only from a new concrete owner question.
