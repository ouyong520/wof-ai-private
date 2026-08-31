# RAWMINE Post-Completion Continuation

Date: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

## Why this file exists

`COMPLETION_20260901.md` closed the retained-raw candidate-screen phase. Work continued afterward only to keep the automatic evidence pipeline synchronized with owner-lane state and to answer concrete owner questions with discriminative evidence. No Browser mainline or production-shadow rule is modified here.

## EFIELD owner synchronization

EFIELD subsequently closed its bounded high-value field-mapping phase in `parallel/EFIELD/COMPLETION_20260901.md`, with Round 010 retaining `+0x2D`, `+0x2E`, `+0x37`, and the earlier `+0x72` at owner-level `STRONG_CANDIDATE` where appropriate while refusing narrower gameplay semantics.

RAWMINE bridge follow-up records that owner boundary explicitly so a question-specific RAWMINE numerical class cannot be confused with an EFIELD semantic classification.

Bridge changes:

- `analysis/rawmine/candidate_screen_completion_sync.py`
- workflow stage `Synchronize owner completion state`
- candidate-screen workflow refreshes from latest `main` before analysis to avoid stale-report rebase conflicts

No generic EFIELD capture is requested by RAWMINE.

## GEO P1 depth discriminator — first controlled attempt

Owner task:

`GEO-0008-p1-depth-only-5s60-20260831-2115Z`

The collector produced a mechanically valid 300-frame read-only raw. RAWMINE consumed it automatically and added a second validation layer beyond collector health.

Owner-specified orthogonal controls passed cleanly:

- reconstructed X (`+0x04/+0x0B`) changes: 0
- reconstructed Z (`+0x0C/+0x11`) changes: 0

But the intended P1 UP/DOWN manipulation was not present in player-object evidence:

- `+0x08` controlled-run changes: 0
- only `+0x7F` was strongly dynamic on P1, but it was similarly dynamic on untouched P2/P3 (`P1 specificity ~0.5133`)
- no byte passed the minimum repeated P1-specific manipulation guardrail

Automated verdict:

`CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

This is an ineffective manipulation capture, **not** negative evidence against `+0x08` and not support for `+0x7F` as depth. Detailed evidence is in `parallel/RAWMINE/GEO_0008_DEPTH_SCREEN.md`.

## Targeted retry

Because the GEO-owned depth question remains unresolved and the original owner task is already complete, RAWMINE routed one narrow evidence-only retry rather than generic acquisition:

`RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`

The retry requires:

- an open walkable area;
- visibly repeated P1 UP/DOWN traversal for the full capture;
- P2/P3 untouched;
- no LEFT/RIGHT, jump, attack, or other action;
- the same reconstructed X/Z contamination guards.

Current task state: `WAITING_FOR_OPERATOR`.

`analysis/rawmine/candidate_screen_geo_depth.py` now consumes both the original GEO discriminator and this RAWMINE retry. A mechanically healthy raw is accepted for ranking only if at least one byte has >=5 P1 changes, >=0.80 P1-specificity, and <=0.05 untouched-P2/P3 change rate. Otherwise it remains insufficient manipulation evidence.

## Lane stop condition

Existing EFIELD raw is exhausted and requires no generic continuation. Existing GEO-0008 raw is explicitly bounded as ineffective for P1 depth. The only active RAWMINE work item is the already-routed discriminative retry above. No additional capture should be queued in parallel with that operator gate.
