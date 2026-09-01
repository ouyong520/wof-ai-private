# RAWMINE-004 Player-Slot Attribution Result

Date: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

## Scope

This note records the neutral player-slot attribution analysis for `RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z`. RAWMINE does not assign final geometry semantics.

## Capture integrity

The Collector result is mechanically healthy and read-only:

- 600 frames / 599 transitions
- requested 10 s at 60 Hz
- achieved ~59.955 Hz
- 5152 bytes/frame
- zero read errors
- zero frame-size errors
- `writesGameMemory: false`
- raw uploaded as `captures/RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z.jsonl.gz`

## Three-slot attribution scan

The operator contract was RIGHT ~1.5 s -> LEFT ~1.5 s -> UP ~2.5 s -> DOWN ~2.5 s. To test whether the controlled character was mislabeled as P2/P3 rather than P1, RAWMINE scanned reconstructed X = `256*U8(+0x0B)+U8(+0x04)` on all three Collector player objects over the calibration interval.

| Collector slot | X calibration changes | reversal |
|---|---:|---|
| P1 / object 0 | 0 | false |
| P2 / object 1 | 0 | false |
| P3 / object 2 | 0 | false |

Result: `CONTROLLED_PLAYER_SLOT_ATTRIBUTION_FAILED`.

This rules out the simple explanation that the operator-controlled character was merely P2 or P3 in the Collector ordering. No one of the three player objects contains the intended RIGHT->LEFT calibration during the analyzed capture window.

## Depth-phase screen

On the default selected object, the intended depth-phase control values are mechanically stable:

- reconstructed X changes: 0
- reconstructed Z changes: 0
- `+0x08` changes: 0
- no P1-specific manipulation-evidence offset passes the gate
- dynamic `+0x7F` remains shared across player controls (specificity ~0.50), so it is not accepted as a depth-coordinate candidate

This is not negative evidence against `+0x08`. The capture did not prove that the requested movement sequence overlapped the raw acquisition window.

## Next acquisition design

The next bounded discriminator is `RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`.

It removes fixed phase alignment from the analysis:

1. long 40-second raw window;
2. repeated bidirectional LEFT/RIGHT motion for roughly 15 seconds to attribute the actually controlled player object;
3. repeated UP/DOWN traversal for roughly 20 seconds;
4. analysis attributes the player slot from all-window X motion, then ranks unresolved offsets only on selected-slot transitions where confirmed X and Z remain unchanged;
5. P2/P3 remain controls;
6. final Y/depth semantics remain GEO-owned.

No Browser/production promotion and no game-memory writes are permitted.
