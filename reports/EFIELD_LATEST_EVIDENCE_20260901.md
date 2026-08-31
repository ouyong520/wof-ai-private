# EFIELD Latest Evidence Addendum — 2026-09-01

This addendum records WinKawaks-local EFIELD discovery evidence produced after the seven-capture atlas consolidation. It is discovery-only and read-only. It does not imply Browser/WASM offset equivalence, WOF-045 progression, production-shadow changes, or any game-memory write.

## Corpus boundary

The valid raw corpus remains seven EFIELD captures (EFIELD-001, 002, 003, 004, corrected 005, 005R, 006), totaling 23,400 frames / 468,000 enemy-object samples. EFIELD-007, 008 and 009 all failed before raw sampling because fresh immutable CPS RAM discovery was not uniquely qualified.

## Collector discovery blocker

The immutable player fingerprint was strengthened to v3 using stable P1/P2/P3 triplets at offsets 0x20, 0x21, 0x26, 0x62, 0x7C and 0x92. Cross-corpus validation covers 13 compatible captures / 26,402 frames with zero mismatches for all six triplets.

GitHub-side queue logic now treats a matching FAILED task blob as terminal so failed discovery probes cannot starve later tasks. Future failure status generation also includes freshDiscovery candidate count/list. The currently running local Collector process did not hot-load that newer code for EFIELD-009, so its status still contains only the generic non-unique-discovery error. The uniqueness gate must not be weakened and cached RAM addresses must not be substituted merely to resume sampling.

## Script/animation executor refinement

The U32 BE structure at 0x2F..0x32 is strongly supported as a flagged logical 10-byte record cursor.

- after masking 0x001C0000 flag bits, 4323/5539 logical pointer changes are +0x0A;
- logical -0x32 is exactly -50 bytes, consistent with a five-record backward loop for 10-byte records;
- masked logical cursor predicts steady-state full phase tuple (0x6C,0x70,0x72,0x73,0x77) with 96.3117% weighted modal purity;
- destination logical record after a sequential +0x0A step predicts the post-arrival phase tuple with 99.9769% modal purity;
- retaining embedded raw flags raises steady-state phase purity to 97.2955%, supporting phase-modifier semantics rather than noise.

## 0x34 record dwell/countdown

0x34 behaves as a record-local dwell/countdown field.

- while logical record is stable, dominant changes are -1 and -2;
- before sequential +0x0A record advance, 0x34 <= 2 in 97.29% of the original sequential-step pass;
- record-wide reload ceilings are highly stable: leave-one-run-out destination coverage 4321/4323, holdout reload exceeds training maximum only 11/4321 = 0.25%;
- holdout reload equals training record ceiling 73.59%, lies within 1 below it 92.34%, and within 2 below it 94.40%.

A follow-up sampling-phase test rejects the simple idea that max-1/max-2 arrivals are merely observed one or two frames late: among 4820 sequential arrivals, a sub-ceiling arrival never rises back to the record ceiling in the following two same-record frames.

Logical-record residence analysis strengthens the countdown interpretation:

- 6737 multi-frame logical-record residences were observed;
- 6684/6737 = 99.21% contain no positive 0x34 step at all;
- residence terminal values are strongly concentrated at 1 (4410) and 2 (1191), followed by 3 (446);
- only 53/6737 residences contain a positive step; almost all of those are a special coarse-0x73=1B family that starts around 0x34=8 and then loads 9..17 before resuming countdown.

Current model: each record has a stable nominal/upper dwell ceiling, but some execution paths enter the same record with a genuinely reduced dwell value. The normal record residence then counts down toward a small transition threshold. A narrow 0x73=1B family appears to use delayed dwell initialization after record entry.

## C6 player association: nearest-X sample-and-hold state

C6 is an independent three-valued player association layer, with exact redundant pointer encoding at 0x3D..0x3E:

- C6=0 -> BE1C (P1)
- C6=1 -> BEFC (P2)
- C6=2 -> BFDC (P3)

It is not the live target pointer (0x6D..0x6E). Across 60,271 type-present samples C6 agrees with nearest-X about 87.02%, while live target agrees with nearest-X only about 30.73%.

All 11 observed same-type C6 updates occur only in eight logical cursor values from the 0x02008Bxx/0x02008Cxx and 0x02005Exx script families; no same-type C6 update was observed at any other logical cursor in the current corpus. Five of the 11 updates coincide exactly with logical +0x0A record advance; six occur mid-record.

### 0xCC is the nearest-X synchronization checkpoint

0xCC is binary (00/FF) in the current type-present corpus. It is not a C6 mirror and it is not a one-frame pulse: full-corpus analysis found 65 same-type 00->FF transitions and 70 FF->00 transitions, with FF runs commonly lasting tens to more than one hundred frames.

The key synchronization result is exact in the retained corpus:

- same-type CC 00->FF entries: 65;
- before entry C6 already equals nearest-X: 57/65;
- before entry C6 differs from nearest-X: 8/65;
- after entry C6 equals nearest-X: **65/65**;
- the 57 already-correct cases keep C6 unchanged;
- the 8 mismatched cases change C6 on that exact frame and all 8 land on nearest-X.

A global rule pass over 58,667 same-type transitions confirms:

- `C6 != nearest-X` alone: 7396 predictions, 8 true corrections;
- `C6 != nearest-X AND CC 00->FF`: **8 predictions, 8 true corrections, precision 1.0, recall 1.0**;
- adding the previously observed script-cursor gate does not change the 8/8 result, so the cursor family is best treated as upstream execution context for CC entry rather than the minimal direct synchronization condition.

This gives the current strongest operational model:

**CC 00->FF is a nearest-X synchronization checkpoint for C6. If the stored association is already nearest-X, it is retained; if stale, it is replaced by nearest-X on the same frame.**

### State signature of the correction frame

All eight stale->synchronized corrections also have a clean action-state signature:

- 8/8 change 0x2D on the exact correction frame;
- 7/8 are 0x2D 04->06; 1/8 is 0C->06;
- 0x2D changes in 0/8 event windows at offsets -3,-2,-1,+1,+2,+3: the transition is frame-exact;
- 0x2E also changes on all 8 correction frames, most often 08->00 or 0A->00.

0x2D/0x2E therefore describe the same synchronization-mode entry, but CC 00->FF is the more selective direct checkpoint in the current corpus.

### Why C6 later becomes stale

CC=FF has a much higher C6/nearest-X match rate than CC=00:

- CC=00: 43,905 match / 7,389 mismatch = 85.59%;
- CC=FF: 8,540 match / 437 mismatch = 95.13%.

After CC 00->FF synchronization, match remains 100% through age 0..40 frames in the current corpus. Later mismatch can appear because C6 is a sample-and-hold value, not a continuously recomputed nearest-player function.

Match->mismatch onset analysis found 40 events:

- 34: nearest-X player changed while C6 stayed fixed and CC remained 00;
- 3: nearest-X player changed while C6 stayed fixed and CC remained FF;
- 3: C6 itself changed while nearest-X did not, all while CC remained 00.

The final three are the separate non-proximity/P1-reset branch described below. Thus the normal stale-state mechanism is geometry changing after the last synchronization checkpoint while C6 remains latched.

### Separate non-proximity/P1-reset branch

Not every C6 update is a nearest-X synchronization. Three of the 11 same-type C6 changes set C6 from P3 to P1 while nearest-X remains P3. They all occur while CC remains 00 and do not use the 0x2D->06 / CC-on synchronization signature. Current evidence therefore supports a distinct P1-default/reset path in addition to nearest-X synchronization.

The other two non-P1->P1 events in the corpus are ordinary nearest-X corrections and do use the synchronization signature, so they must not be mixed with these three exceptional reset events.

## New bridge evidence files

- results/efield/C6_SCRIPT_CHECKPOINTS.md
- results/efield/C6_MISMATCH_CORRECTION.md
- results/efield/C6_TRIGGER_RANK.md
- results/efield/C6_STATE_GATE.md
- results/efield/C6_COMMIT_STATE.md
- results/efield/C6_P1_RESET.md
- results/efield/C6_CC_ENCODING.md
- results/efield/CC_PULSE.md
- results/efield/C6_RULE_VALIDATION.md
- results/efield/C6_CC_SYNC.md
- results/efield/C6_CC_LATCH.md
- results/efield/C6_MISMATCH_ONSET.md
- results/efield/RELOAD_HOLDOUT.md
- results/efield/RELOAD_CEILING.md
- results/efield/RELOAD_SAMPLING_PHASE.md
- results/efield/RECORD_RESIDENCE.md
- results/efield/PLAYER_FINGERPRINT_CROSSCORPUS.md

## Next research decisions

1. Isolate the three CC=00 P3->P1 reset events and identify the common upstream state/record trigger without conflating them with nearest-X synchronization.
2. Decode the special 0x73=1B delayed 0x34 initialization family and determine whether 0x34=8 is an entry sentinel/default before record-local dwell load.
3. Continue separating C6 association from live target 0x6D..0x6E; current evidence strongly supports two independent player-reference layers.
4. Continue offline while live fresh-discovery remains ambiguous. Do not weaken discovery uniqueness or request manual staging yet.
