# RAWMINE Post-Completion Continuation

Date: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

## Why this file exists

`COMPLETION_20260901.md` closed the retained-raw candidate-screen phase. Work continued only to answer the remaining concrete GEO P1 floor/depth question with discriminative evidence. No Browser mainline or production-shadow rule is modified here.

## Earlier controlled attempts

`GEO-0008-p1-depth-only-5s60-20260831-2115Z` and the subsequent short retries were mechanically valid read-only captures but did not contain a usable P1 depth trajectory. They remain recorded as coverage/manipulation failures, not as negative evidence against `+0x08`.

`RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z` also failed the intended RIGHT->LEFT player-attribution calibration: all three reconstructed player X composites recorded zero changes during that 10-second raw. Its result is therefore bounded as a capture-window attribution failure.

## Final timing-robust wide-window task

RAWMINE routed one final broad timing window specifically to remove the short-window alignment failure:

`RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`

Collector result:

- status: PASS;
- frames: 2400;
- achieved rate: 59.981 Hz;
- read errors: 0;
- frame-size errors: 0;
- read-only: true;
- writesGameMemory: false.

The horizontal calibration segment still produced no reconstructed X changes in any player slot, so movement-based slot attribution remained invalid. RAWMINE therefore does not use that segment as independent player-attribution proof.

However, the same raw contains a strong P1-only continuously varying candidate family during X/Z-stable transitions:

- `+0x08`: 536 changes, P1 specificity 1.0, untouched P2/P3 rate 0, bidirectional score 0.955224;
- `+0xA2`: 536 changes, P1 specificity 1.0, untouched P2/P3 rate 0, bidirectional score 0.966418;
- both domains: 63..143, 81 distinct values;
- `+0x16`: 68 changes, domain {6,7}, only 0.090253 event Jaccard with `+0x08`.

## +0x08 / +0xA2 timing discriminator

`analysis/rawmine/depth_pair_timing.py` was added to distinguish the two strong continuous candidates without assigning semantics.

Key result:

- change-event counts: 536 / 536;
- same-frame change overlap: 424;
- same-frame event Jaccard: 0.654321;
- same-sign delta ratio when both change: 1.0;
- best exact copy relation: `A2[t] == 08[t-1]`;
- one-frame trailing-copy ratio: 2116 / 2399 = 0.882034;
- same-frame value equality: 0.736667.

Neutral RAWMINE conclusion: `+0x08` and `+0xA2` track the same underlying varying quantity but the dominant temporal relationship places `+0xA2` one frame behind `+0x08`. This is timing evidence consistent with the GEO owner's pre-existing live/cache distinction; RAWMINE does not rename or promote either field.

Bridge outputs:

- `results/rawmine/player_slot_depth_long_window.json`
- `results/rawmine/player_slot_depth_long_window.md`
- `results/rawmine/depth_pair_timing.json`
- `results/rawmine/depth_pair_timing.md`

## Handoff / stop condition

P1 floor/depth evidence is now `READY_FOR_GEO_OWNER_PROMOTION_DECISION`.

There is no active RAWMINE operator gate and no further RAWMINE capture is justified for the current GEO/EFIELD questions. Future RAWMINE acquisition starts only if an owner lane poses a new concrete ambiguity that the retained corpus cannot discriminate.
