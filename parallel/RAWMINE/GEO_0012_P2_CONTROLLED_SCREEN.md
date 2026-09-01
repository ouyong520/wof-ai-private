# RAWMINE — GEO-0012 P2 controlled-screen result

Date: 2026-09-01
Lane: RAWMINE evidence-only
Evidence class: `WinKawaks-local-discovery-only`

Source owner task:

`GEO-0012-p2-same-xy-offsets-12s60-20260901-0054Z`

## Collector validity

- Collector: DONE / PASS
- read-only: true
- writes game memory: false
- 720 frames, target 60 Hz
- zero read/frame-size errors
- raw retained in the bridge repo

## Operator contract

P2 only: RIGHT ~2 s -> LEFT ~2 s -> UP ~3 s -> DOWN ~3 s -> idle; P1/P3 untouched.

## RAWMINE controlled scan

The raw was scanned independently across P1/P2/P3 and all offsets `0x00..0xDF`, both by nominal action phase and across the entire 720-frame run.

Observed in all three player slots:

- reconstructed X changes: 0
- `+0x04`: 0 changes
- `+0x0B`: 0 changes
- `+0x08`: 0 changes
- `+0x9C/+0xA3/+0xA2`: 0 geometry-family changes
- reconstructed Z changes: 0
- the only dominant per-slot activity is shared `+0x7F` oscillation, including during the nominal idle phase

Therefore GEO-0012 does **not** contain a discriminative controlled P2 geometry trajectory. RAWMINE treats it as an acquisition/action-window attribution failure, not as evidence that P2 uses different coordinate offsets.

## Existing cross-slot evidence retained

Across the broader retained corpus before/including GEO-0012:

- P2 X same-offset structure remains `SUPPORTED` by natural dynamic runs: `+0x04/+0x0B` composite activity is observed repeatedly.
- P2 floor/depth `+0x08` remains `INSUFFICIENT_COVERAGE` because no retained P2-controlled run yet contains dynamic `+0x08` motion.
- P3 X same-offset structure remains `SUPPORTED`.
- P3 floor/depth `+0x08` remains `INSUFFICIENT_COVERAGE`.

No RAWMINE semantic promotion is made. GEO remains the owner for P2/P3 same-structure/same-offset confirmation.

## Continuation rule

Do not route a duplicate RAWMINE P2 capture while GEO is actively handling the P2 verification stage. Automatically consume the next GEO P2 controlled raw if/when the owner retries, then hand neutral evidence back to GEO.
