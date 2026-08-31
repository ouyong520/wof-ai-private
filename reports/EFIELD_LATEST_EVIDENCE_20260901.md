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

A follow-up sampling-phase test rejects the simple idea that max-1/max-2 arrivals are merely observed one or two frames late: among 4820 sequential arrivals, a sub-ceiling arrival never rises back to the record ceiling in the following two same-record frames. Cursor residence normally ends with 0x34 at 1 (3533 cases) or 2 (981 cases). Current model: each record has a stable nominal/upper dwell ceiling, but some execution paths enter the same record with a genuinely reduced dwell value; the countdown then proceeds toward a small transition threshold.

## C6 player association is script-gated proximity bookkeeping

C6 is an independent three-valued player association layer, with exact redundant pointer encoding at 0x3D..0x3E:

- C6=0 -> BE1C (P1)
- C6=1 -> BEFC (P2)
- C6=2 -> BFDC (P3)

It is not the live target pointer (0x6D..0x6E). Across 60,271 type-present samples C6 agrees with nearest-X about 87.02%, while live target agrees with nearest-X only about 30.73%.

All 11 observed same-type C6 updates occur only in eight logical cursor values from the 0x02008Bxx/0x02008Cxx and 0x02005Exx script families; no same-type C6 update was observed at any other logical cursor in the current corpus. Five of the 11 updates coincide exactly with logical +0x0A record advance; six occur mid-record.

### Proximity-correction branch

Within the switch-capable cursor set:

- nearest-X mismatch exposures: 2097;
- C6 correction events: 8;
- all 8 updates corrected C6 to the nearest-X player;
- mismatch exposures outside the switch-capable cursor set: 5299, with zero C6 changes;
- within capable cursors, mismatch-state update rate is about 18x the already-matching update rate.

The proximity-correction branch has a clean state commit signature:

- all 8 corrections change 0x2D on the exact correction frame;
- 7/8 are 0x2D 04->06, 1/8 is 0C->06;
- 0x2D changes on 0/8 correction windows at offsets -3,-2,-1,+1,+2,+3: the transition is frame-exact;
- 0x2E also changes on all 8 exact correction frames, most often 08->00 or 0A->00;
- observed exact (0x2D transition, 0x2E transition) correction pairs have 100% event precision inside the narrowed capable-cursor + nearest-X-mismatch population.

This supports a three-layer mechanism in the current corpus:

1. execution reaches a C6-update-capable logical script record;
2. current C6 disagrees with nearest-X player;
3. a state transition ending in 0x2D=06 (with 0x2E reset/substate change) commits C6 to the nearest-X player.

### Separate non-proximity/P1-reset branch

Not every C6 update is a proximity correction. Three of the 11 updates switch C6 to P1 even though P1 is not the nearest-X player at the update frame. Those three do not use the 0x2D->06 proximity-correction signature. Current evidence therefore supports at least two C6 update paths rather than one universal rule.

## 0xCC emerging correction-path flag

0xCC is binary (00/FF) in the current type-present corpus and is not a deterministic encoding of C6. However, all 8 proximity-correction events observed so far change 0xCC 00->FF on the same frame, while the three non-proximity C6 update events leave 0xCC unchanged. This makes 0xCC a high-value candidate for a proximity-correction mode/pulse flag. Full transition-duration analysis is tracked in bridge result `results/efield/CC_PULSE.md`.

## New bridge evidence files

- results/efield/C6_SCRIPT_CHECKPOINTS.md
- results/efield/C6_MISMATCH_CORRECTION.md
- results/efield/C6_TRIGGER_RANK.md
- results/efield/C6_STATE_GATE.md
- results/efield/C6_COMMIT_STATE.md
- results/efield/C6_P1_RESET.md
- results/efield/C6_CC_ENCODING.md
- results/efield/RELOAD_HOLDOUT.md
- results/efield/RELOAD_CEILING.md
- results/efield/RELOAD_SAMPLING_PHASE.md
- results/efield/PLAYER_FINGERPRINT_CROSSCORPUS.md

## Next research decisions

1. Finish 0xCC pulse lifetime and reset-timing analysis; determine whether it is correction-path state, pulse, or latched mode.
2. Separate the three non-proximity/P1 C6 updates from the eight nearest-X corrections and search for a distinct reset/default trigger.
3. Decode 0x34 reduced-dwell entries: correlate per-record start value with branch source, embedded cursor flags and preceding logical record rather than instance metadata.
4. Continue offline while live fresh-discovery remains ambiguous. Do not weaken discovery uniqueness or request manual staging yet.
