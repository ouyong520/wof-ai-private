# GEO P2/P3 same-offset structure frontier

Updated: 2026-09-01

Scope: WinKawaks local discovery only. Read-only. No Browser mainline changes, no production-shadow changes, no RAM writes.

## Entry condition

P1 geometry is closed:

- `X = 256 * U8(+0x0B) + U8(+0x04)` — CONFIRMED.
- `Y_floor_depth = U8(+0x08)` — CONFIRMED.

Do not reopen P1. Current phase is only whether P2/P3 use the same structure and offsets.

## Existing cross-slot evidence

RAWMINE neutral cross-slot structure report after GEO-0012:

- report: `results/rawmine/player_cross_slot_structure.json`
- input runs: 12, including `GEO-0012-p2-same-xy-offsets-12s60-20260901-0054Z`
- P2 X same-offset evidence: `SUPPORTED`
- P3 X same-offset evidence: `SUPPORTED`
- P2/P3 `+0x08` depth same-offset evidence: `INSUFFICIENT_COVERAGE`

P2 aggregate retained-block evidence:

- confirmed-X composite dynamic across prior corpus: 187 events
- `+0x04`: 187 events
- `+0x0B`: 1 event / page coverage present
- `+0x08`: 0 dynamic events so far
- `+0xA2`: 0 dynamic events so far

P3 aggregate retained-block evidence:

- confirmed-X composite dynamic across prior corpus: 44 events
- `+0x04`: 44 events
- `+0x0B`: no page transition yet
- `+0x08`: 0 dynamic events so far

## GEO-0012 result

`GEO-0012-p2-same-xy-offsets-12s60-20260901-0054Z`

- taskBlobSha `a491357a1800710e618867eba5692279670852f5`
- collector DONE / PASS
- 12 s @60 Hz, 720 samples, achieved ~59.957 Hz
- distinct raw frames 676
- read errors 0; frame-size errors 0
- readOnly true; writesGameMemory false
- raw `captures/GEO-0012-p2-same-xy-offsets-12s60-20260901-0054Z.jsonl.gz`
- original SHA256 `1fcb87f8da1b92f97fbc55766b60ea3cd790ecc2498dd001967c816f35bd5b15`
- compressed SHA256 `b9067de4040b552bfee1fa363af309c8de35014d249011ff613b37608bd00166`

The refreshed cross-slot report does not list GEO-0012 as a run containing P2 X motion or P2 `+0x08` motion. It also adds no corresponding new P1/P3 motion. Therefore GEO-0012 is treated as a mechanically healthy but manipulation/attribution-invalid P2 experiment, not negative evidence against the same-offset hypothesis.

## Current discriminator — GEO-0013

`GEO-0013-p2-attribution-depth-long-35s60-20260901-0104Z`

taskBlobSha `7c4ff7922e9464fe0b5db063902f2665af9dc2ac`

Single question:

**After retained P2 is positively calibrated by repeated bidirectional motion in the already-supported P2 X composite, does `U8(+0x08)` on that same P2 block show repeated small-step bidirectional floor/depth motion during repeated UP/DOWN travel while P1/P3 remain untouched?**

The first horizontal phase is only an attribution/calibration control; it does not reopen X semantics.

Decision rule:

- If retained P2 X is positively calibrated and P2 `+0x08` then shows repeated bidirectional small-step depth motion with P1/P3 stable, promote P2 same X/Y offsets to CONFIRMED.
- If P2 X calibration does not appear on any retained player block, do not interpret depth semantics and do not count the run against `+0x08`.
- Once P2 is confirmed, validate P3 with the same narrow structure question; do not advance to facing before both P2 and P3 are locked.
