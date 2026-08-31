# RAWMINE Post-Completion Continuation

Date: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

## Why this file exists

`COMPLETION_20260901.md` closed the retained-raw candidate-screen phase. Work continued afterward only to keep the automatic evidence pipeline synchronized with owner-lane state and to prepare for the next already-queued GEO discriminator. No Browser mainline or production-shadow rule is modified here.

## EFIELD owner synchronization

EFIELD subsequently closed its bounded high-value field-mapping phase in `parallel/EFIELD/COMPLETION_20260901.md`, with Round 010 retaining `+0x2D`, `+0x2E`, `+0x37`, and the earlier `+0x72` at owner-level `STRONG_CANDIDATE` where appropriate while refusing narrower gameplay semantics.

RAWMINE bridge follow-up now records that owner boundary explicitly so a question-specific RAWMINE numerical class cannot be confused with an EFIELD semantic classification.

Bridge changes:

- `analysis/rawmine/candidate_screen_completion_sync.py`
- workflow stage `Synchronize owner completion state`
- summary revision `v6-owner-sync-through-efield-round010-completion`

No generic EFIELD capture is requested by RAWMINE.

## GEO P1 depth discriminator continuation

GEO has queued the concrete operator-controlled task:

`GEO-0008-p1-depth-only-5s60-20260831-2115Z`

Question: P1 UP/DOWN-only floor/depth discriminator, with reconstructed X (`+0x04/+0x0B`) and Z (`+0x0C/+0x11`) expected to remain stable.

RAWMINE prepared `analysis/rawmine/candidate_screen_geo_depth.py` so the next eligible raw is consumed automatically. The screen is deliberately evidence-only and evaluates:

- P1 change-event support per byte;
- untouched P2/P3 control change rate;
- P1-specificity;
- small circular delta behavior;
- bidirectional delta evidence;
- exact co-change precision/recall relative to `+0x08` as supporting evidence only;
- contamination guardrails from reconstructed X and Z control changes.

If the controlled X/Z guardrails fail, the screen reports `CONTAMINATED_CONTROL` rather than forcing a coordinate conclusion.

## Current mechanical state

At the time of this continuation the GEO task status is `WAITING_FOR_OPERATOR`. That is an owner-controlled scene gate, not a RAWMINE evidence failure. RAWMINE must not duplicate it with a separate `RAWMINE-*` capture or bypass the operator gate.

Once `captures/GEO-0008-p1-depth-only-5s60-20260831-2115Z.jsonl.gz` exists, the bridge workflow automatically reruns the generic evidence, owner-scoped rankings, controlled GEO depth screen, and owner-completion synchronization.

## Lane stop condition

There is no additional unattended RAWMINE acquisition justified before that owner raw arrives. Existing EFIELD raw is exhausted; existing GEO raw has insufficient P1 depth coverage; a concrete discriminative GEO task is already active. The correct RAWMINE behavior is therefore automatic consumption of that result, not more generic collection.
