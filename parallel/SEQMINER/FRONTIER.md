# SEQMINER Frontier

Updated: 2026-09-01  
State: **current retained-corpus ordered information exhausted; miner v2 ready; no recapture requested**

## Current verdict

Ordered context is mandatory for the unresolved attack-selection frontier.

- T18 has direct prospective proof that one exact zero-attack state leads to both A4704 and A4712.
- T23 has eight Browser attack-labelled cycles across A4792/A4920/A5888 and contains single-state overlap between attack branches.
- WinKawaks EFIELD supplies a reproducible ordered executor but not an exact move-valued `activeAttack` label.

The correct model class is sequence/branch context, not another isolated offset equality.

## Corpus status correction

`parallel/SWEEPATLAS/**` now exists.

It confirms broad retained local coverage, including all T1..T31 and explicit local T18/T23 presence. Its authoritative capture index simultaneously states:

```text
stageSceneWaveLabelsAvailable = false
fullSweepSeriesPresent = false
```

So the old statement “SWEEPATLAS absent” is obsolete. The actual blocker is narrower:

1. no labeled `BASECAP-SWEEP-*` full-game series on GitHub main;
2. no separately proven WinKawaks-local exact move/attack value suitable for grouping Axxxx-like outcomes.

No stage/scene labels or exact local attack matrix are fabricated.

## Offline information now exhausted

### Cursor topology

The record graph contains sequential `+0x0A` chains, `-0x32` loop resets, flag/bank transitions and large branch jumps. Destination phase prediction from logical cursor survives leave-one-run-out at `4818/4819` accuracy on covered events.

### Branch hotspots

Highest-value structural nodes from retained raw-derived reports:

- `02008BE0`: 199 sequential vs 141 branch/other exits; alternate `->02009006`; variable conditional hold.
- `02005EA4`: 114 sequential vs 108 branch/other.
- `02008BD6`: logical-state ambiguity split partly by cursor flags.
- `02005E9A`: same.
- `02008C12`, `02008C52`, `02005ED6`: dominant branch/reset nodes.

### Timer progression

`+0x34` is not adequately represented by literal timer equality alone.

SEQMINER now preserves:

- exact start/end/min/max timer profile;
- record-ceiling normalized timer family;
- terminal `timer34==1` residence length.

The last feature matters because `02008D08` / `02005FF8` commonly wait about 32 frames at timer1, `02008BE0` can wait up to 276, and `0200906E` up to 1518.

### Mode / flag progression

- `+0x35` is an independent state-machine branch axis.
- embedded cursor flags materially split ambiguous logical cursors.
- `+0x37` remains useful gate/substate context.

### Target/reference context

The miner keeps separate live target, stored association, split third reference and association synchronization checkpoint, preventing target transitions from masquerading as attack-specific sequences.

## SEQMINER v2 completion

`seqminer.py` has been strengthened to:

- discover retained raw automatically;
- use physical-slot/type/B4/B6 episode continuity;
- avoid using mutable B0 as object identity;
- compress core executor states while preserving context separately;
- save frame start/end/dwell;
- save exact + normalized timer progression;
- save terminal TM1 hold duration;
- capture event-edge target changes;
- count feature support once per cycle;
- rank final/tail2/tail3/pair/triple exact/context/normalized families;
- automatically identify ambiguous anchors and next-state divergence;
- record capture/scene/target stability without inventing scene labels;
- emit branchpoint and candidate machine-readable outputs.

## Browser prospective queue

Priority remains:

1. **P0 T18 post-BODY4728 split** — first post-anchor state/pair/triple, then timer/descriptor context.
2. **P1 T23 A5888 BODY4936 tail3** — complete ordered tail only.
3. **P2 T23 branch-set validator** — do not force one universal A4792/A4920/A5888 fingerprint.
4. **P3 cross-target invariance** for surviving branches.

WOF-052 is a Browser-mainline responsibility and is not modified by SEQMINER.

## Recapture decision

**No Collector task.**

A new local capture is not justified merely to increase volume. Reopen local acquisition only if a specific already-ranked discriminator is one bounded experiment away from resolution.

## Reopen triggers

This lane should automatically resume full exact-label mining when either:

- a labeled retained full-sweep series becomes available; or
- an exact WinKawaks-local attack/move field is proven.

Then regenerate:

```text
zero cycle
-> ordered distinct states
-> final/tail2/tail3
-> pair/triple
-> exact timer
-> normalized timer + terminal-hold family
-> ambiguous anchor branchpoints
-> eventual exact local attack
-> cross capture/scene/target stability
-> Browser prospective candidate ranking
```

Until one of those triggers occurs, there is no remaining generic offline sequence-mining step that can honestly produce a new exact attack rule from the connector-visible corpus.