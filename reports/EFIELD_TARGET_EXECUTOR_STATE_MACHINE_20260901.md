# EFIELD Target / Executor State Machine — 2026-09-01

Evidence class: **WinKawaks-local discovery only**. This report does not establish Browser/WASM offset equivalence and does not change any production rule.

- read-only: `true`
- writes game memory: `false`
- valid EFIELD raw captures: `7`
- corpus frames: `23,400`
- enemy-object samples: `468,000`

## 1. Two player-reference layers are now structurally separated

### Association / selection layer

`0xC6` is a U8 player index with an exact redundant U16 BE pointer at `0x3D..0x3E`:

- `C6=00 -> 0xBE1C` = P1
- `C6=01 -> 0xBEFC` = P2
- `C6=02 -> 0xBFDC` = P3

Across 60,271 type-present samples, this association agrees with nearest-X player about 87%, but it is not recomputed every frame. Match-to-mismatch onset analysis found 40 events: 37 were caused by nearest-X identity changing while C6 stayed latched; only 3 were caused by C6 itself changing away from nearest-X.

### Live / materialized target layer

`0x6D..0x6E` is a U16 BE live target pointer with only the same three player values in the retained corpus.

Across all 8 observed known-player target changes:

- new live target == post-frame `0x3D..0x3E` association: **8/8**;
- six same-type target changes copy an association that had already been stable for approximately 57, 217, 278, 492, 537 and 715 frames respectively;
- two nonzero-type -> nonzero-type replacements change association and live target together to P1 on the same frame.

Therefore the strongest current structural model is:

**player association (`C6` / `3D..3E`) -> delayed state-gated materialization -> live target (`6D..6E`)**.

The observed `6D..6E` field should not be treated as the upstream player-selection source merely because it is a precise live target pointer.

## 2. `0xCC` is a nearest-X synchronization checkpoint for C6

`0xCC` is binary `00/FF` and is a long-lived mode/latch, not a one-frame pulse.

- same-type `00->FF` entries: `65`
- before entry C6 already equals nearest-X: `57/65`
- before entry C6 differs from nearest-X: `8/65`
- after entry C6 equals nearest-X: **65/65**
- the 57 already-correct cases retain C6
- the 8 stale cases change C6 on that exact frame and all 8 land on nearest-X

Thus in the retained corpus:

**`CC 00->FF` is an exact nearest-X synchronization checkpoint for the C6 association.**

All eight stale->corrected synchronization events also end in `0x2D=06` and change `0x2E` on the same frame, but global analysis shows `0x2D->06` is much broader: 221 such transitions exist and only 14 change C6. CC entry is the more selective direct synchronization marker.

`CC=FF` commonly persists for roughly tens to >100 frames. During `CC=FF`, C6/nearest-X agreement rises to 95.13% versus 85.59% during `CC=00`, while horizontal motion is substantially reduced. Common exit paths include `CC FF->00`, `2D 06->02`, a coarse attack phase return from `0x73=1B` toward `0x0A`, and a logical cursor advance.

Current state-machine label:

1. `CC=00`: sampled association can become stale as geometry changes;
2. `CC 00->FF`: synchronize C6 to nearest-X;
3. `CC=FF`: engaged/action-mode interval with C6 latched;
4. `CC FF->00`: release/return path.

## 3. Separate exceptional P1-reset path

Three same-type C6 changes are not nearest-X corrections. In all three, C6 changes `P3->P1` while nearest-X remains P3 and CC stays `00`.

All three share the exact three-field transition signature:

- `0xA6: FF->04`
- `0xD1: FF->00`
- `0xB0: 90->80`

Across the seven-run corpus, the conjunction that all three fields change with those common transitions predicts exactly `3` events and all `3` are the exceptional C6->P1 resets: precision `1.0`, recall `1.0` in current data.

This is a distinct C6 write path and must not be merged with the CC nearest-X synchronization rule.

## 4. Live-target materialization uses a later state transition

Target commits do not occur on the C6 synchronization frame in general.

Of 8 live-target commits:

- 5 occur while `CC` remains `FF`;
- 3 occur while `CC` remains `00`;
- none requires a CC transition on the target-commit frame;
- 6/8 change `0x2D` to `00` on the commit frame;
- the other two are the simultaneous type-replacement P1 commits (`2D 06->06` and `06->04`).

For the six same-type commits, association is already the final target tens to hundreds of frames before the live pointer changes. `0x2D->00` is therefore a high-value commit-neighborhood state change, but not a universal or sufficient target-copy rule: the corpus contains 49 nonzero->zero 0x2D transitions and only 6 same-type target commits among them.

Current unresolved question is the exact second-stage copy trigger that makes `6D..6E := 3D..3E` at one of these sparse state transitions.

## 5. Script / animation executor is record-driven

U32 BE `0x2F..0x32` behaves as a flagged 10-byte logical record cursor. After masking observed flag bits `0x001C0000`:

- logical pointer changes: `5,539`
- logical `+0x0A`: `4,323` = `78.05%`
- repeated logical `-0x32` backloops are present
- destination logical record predicts the post-arrival full `(0x6C,0x70,0x72,0x73,0x77)` phase tuple with **99.9769% modal purity**

The removed flag bits are semantically meaningful phase modifiers rather than noise. For example, flag `0x080000` maps 100% to one major `0x73=0A` phase tuple in current data, and `0x140000` is restricted to the rare `0x73=1E` boundary family.

## 6. `0x34` is a record dwell/countdown with timed, wait and delayed-init behavior

Normal logical-record residence strongly supports `0x34` as a remaining dwell/countdown value:

- 6,737 multi-frame record residences analyzed in the dedicated residence pass;
- 6,684/6,737 = 99.21% have no positive `0x34` step;
- terminal values cluster strongly at 1 and 2;
- common timed records have actual residence within about one frame of their entry `0x34` value.

Record-local ceiling validation is cross-run stable: on 4,323 sequential `+0x0A` arrivals, holdout reload exceeds the maximum learned from the other runs only 11/4,321 = 0.25%; 92.34% lie within one below the learned ceiling.

### True terminal-wait records

A robust trailing-`0x34==1` analysis separates repeatable waits from one-off long outliers:

- logical `0x02008D08`: 22/22 full segments hold terminal `1` for >=30 frames, then exit `+0x0A`; long-hold exits are consistently `2D 02->02`, `2E 02->04`;
- logical `0x02005FF8`: 13/13 hold terminal `1` for >=30 frames, then exit `+0x0A`;
- logical `0x02008D12`: 22/22 hold terminal `1` for >=10 frames, median trailing hold about 23 frames;
- logical `0x02006372`: 9/24 segments have >=30-frame terminal holds and then take a fixed large branch delta around `-1240`;
- logical `0x0200906E`: 13/46 have >=10-frame terminal holds, with long-hold exits predominantly a fixed large branch around `-1176`.

This proves the executor contains both ordinary timed records and conditional/wait/branch records that stall at a terminal countdown value until another condition permits exit.

### Narrow delayed-initialization family

A separate `0x73=1B` family shows delayed dwell initialization rather than immediate record-entry load:

- 52 observed record residences enter with `0x34=8` and then load a larger value `9..17` after 1-3 frames;
- 37/52 load on +1 frame, 13/52 on +2, 2/52 on +3;
- entry fine/coarse phase tuple is consistently `40,00,E8,1B,00` apart from the omitted 0x73 component in the source report;
- only a handful of logical records participate, including `0x02008E68`, `0x02008DE2`, `0x02008D98`, `0x020060D2`, `0x02006088`, `0x02006158`.

Therefore `0x34` is not governed by one universal 'load exactly on cursor arrival' rule. Most records initialize immediately, true wait records stall at terminal values, and a narrow 1B-phase family performs delayed dwell initialization.

## Current strongest structural map

- `0x24` U8: current type / type-present lifecycle
- `0xC6` U8 + `0x3D..0x3E` U16 BE: sampled physical-player association
- `0xCC` U8 binary: association synchronization / engaged-mode latch
- `0xA6`, `0xD1`, `0xB0`: exact observed exceptional P1-reset transition signature as a conjunction
- `0x6D..0x6E` U16 BE: materialized live target copied from association in all 8 observed retargets
- `0x2D` / `0x2E`: broad action/mode transition fields participating in both association synchronization and target commit neighborhoods
- `0x2F..0x32` U32 BE flagged: 10-byte logical script/animation-record cursor
- `0x34` U8: record dwell/countdown, with conditional terminal holds and a narrow delayed-load family
- `0x6C/0x70/0x72/0x73/0x77`: hierarchical record-driven attack/animation phase outputs

## Evidence sources in bridge

- `results/efield/C6_CC_SYNC.md`
- `results/efield/C6_RULE_VALIDATION.md`
- `results/efield/C6_CC_LATCH.md`
- `results/efield/C6_MISMATCH_ONSET.md`
- `results/efield/C6_P1_RESET_SIGNATURE.md`
- `results/efield/TARGET_COPY_ALL.md`
- `results/efield/LIVE_TARGET_CC_TIMELINE.md`
- `results/efield/TARGET_2D00_GATE.md`
- `results/efield/POINTER_PHASE_MAPPING.md`
- `results/efield/POINTER_FLAG_SEMANTICS.md`
- `results/efield/RELOAD_CEILING.md`
- `results/efield/RELOAD_SAMPLING_PHASE.md`
- `results/efield/RELOAD_RESIDENCE.md`
- `results/efield/RECORD_EXIT_CLASSES.md`
- `results/efield/TERMINAL_HOLD.md`

## Collection status

EFIELD-007, 008 and 009 failed before capture because fresh immutable CPS RAM discovery was not uniquely qualified. No game-memory write occurred. EFIELD-009 was removed from the active queue after diagnosis to stop an old local Collector process from repeatedly retrying it. Existing seven-run raw evidence remains sufficient for productive offline field analysis, so the discovery gate must not be weakened merely to resume capture.
