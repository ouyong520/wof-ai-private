# SEQMINER Frontier

Updated: 2026-09-01  
State: **current retained-corpus ordered information exhausted; miner v3 ready; no recapture requested**

Authoritative current-corpus completion record: `COMPLETION_20260901.md`  
Exact local move-label proof audit: `EXACT_ATTACK_DESCRIPTOR_AUDIT.md`

## Current verdict

Ordered context is mandatory for the unresolved attack-selection frontier.

- T18 has direct prospective proof that one exact zero-attack state leads to both A4704 and A4712.
- T23 has eight Browser attack-labelled cycles across A4792/A4920/A5888 and contains single-state overlap between attack branches.
- WinKawaks EFIELD supplies a reproducible ordered executor but not an exact move-valued `activeAttack` label.

The correct model class is sequence/branch context, not another isolated offset equality.

## Corpus status

`parallel/SWEEPATLAS/**` confirms broad retained local coverage, including all T1..T31 and explicit local T18/T23 presence. Its capture index simultaneously states:

```text
stageSceneWaveLabelsAvailable = false
fullSweepSeriesPresent = false
```

The actual blockers are therefore narrow:

1. no labeled `BASECAP-SWEEP-*` full-game series on GitHub main;
2. no separately proven WinKawaks-local exact move/attack value suitable for grouping Axxxx-like outcomes.

No stage/scene labels or exact local attack matrix are fabricated.

## Exact local attack-label audit

Existing attack-themed bridge outputs remain phase/lifecycle anchored rather than move-valued:

- `ATTACK_CYCLE.md` defines its episode as contiguous `+0x73 != 0`;
- `MOVE_ATTACK.md` ranks bytes by association with those attack-phase transitions;
- `ACTIVE_STATE.md` uses type-present/lifecycle activity rather than Browser semantic attack ACTIVE;
- the retained EFIELD summary exposes no named `activeAttack` field.

Consequently, strong attack association for `+0x6C/+0x73/+0x70/+0x72/+0x77/+0x37` or sparse transition-selective candidates does not satisfy exact move-label proof. `EXACT_ATTACK_DESCRIPTOR_AUDIT.md` records the acceptance criteria and the current `UNPROVEN` verdict.

## Offline structural information exhausted

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

SEQMINER preserves:

- exact start/end/min/max timer profile;
- record-ceiling normalized timer family;
- terminal `timer34==1` residence length;
- positive timer reload edges across compressed-state boundaries when those edges lie inside the selected event prefix.

The terminal-hold feature matters because `02008D08` / `02005FF8` commonly wait about 32 frames at timer1, `02008BE0` can wait up to 276, and `0200906E` up to 1518.

### v3 delayed-load correction

A concrete representation bug was found by comparing the miner with retained delayed-`1B` evidence.

The EFIELD delayed-dwell analysis contains 52 residences that enter `+0x73=1B` with `+0x34=8` and then load upward. On those load frames:

- `+0x35` changes `52/52`;
- `+0x42` changes `52/52`;
- the load occurs within the first few frames of the residence.

Because `+0x35` belongs to SEQMINER's compressed core key, the old state-local reload list could split immediately before the load and fail to encode the cross-state reload edge.

`seqminer.py` v3 now tracks positive `+0x34` loads at cycle-prefix scope in addition to state-local scope. Every prefix-valid reload keeps pre/post core, cursor, mode35, phase tuple, timer42, timer1 hold context, and exact/normalized timer family. Future-event-edge state remains excluded to avoid label leakage.

### Event-boundary correction

The 52 known delayed-`1B` reloads occur after `+0x73` has already become nonzero. Therefore they are **post-event** under default `phase73-structural-proxy` mode and do not contribute predictor support there.

They become eligible only under a future independently proven explicit attack event definition whose attack field remains zero until after the reload. The feature representation is ready for that case; no current predictive claim is made from the 52 events.

This closes both a compression bug and a possible post-event leakage bug without any new capture.

### Confidence correction

Candidate feature support was already de-duplicated per cycle. v3 applies the same rule explicitly to ambiguous branchpoint support:

```text
one anchor in one resolved cycle = one confidence unit
```

Repeated loop visits are still retained as `raw_occurrence_distribution` but cannot inflate attack support.

### Scene-label correction

Capture filenames remain fallback provenance only. They no longer contribute to an `explicit_scene_count`.

If future raw supplies multiple authoritative dimensions, v3 composes all present `stage/scene/sceneId/room/wave` fields instead of silently retaining only the first one.

### Mode / flag progression

- `+0x35` is an independent state-machine branch axis.
- embedded cursor flags materially split ambiguous logical cursors.
- `+0x37` remains useful gate/substate context.

### Target/reference context

The miner keeps separate live target, stored association, split third reference and association synchronization checkpoint, preventing target transitions from masquerading as attack-specific sequences.

## SEQMINER v3 completion

`seqminer.py` now:

- discovers retained raw automatically;
- uses physical-slot/type/B4/B6 episode continuity;
- avoids mutable B0 as object identity;
- compresses core executor states while preserving context separately;
- saves frame start/end/dwell;
- saves exact + normalized timer progression;
- saves terminal TM1 hold duration;
- captures same-core and cross-core positive timer reload edges when prefix-valid;
- captures event-edge target changes but excludes event-edge state from predictor features;
- counts candidate and branchpoint confidence once per cycle;
- keeps repeated loop visits only as raw occurrence diagnostics;
- ranks final/tail2/tail3/pair/triple/reload exact/context/normalized families;
- automatically identifies ambiguous anchors and next-state divergence;
- separates explicit scene evidence from capture-filename fallback;
- emits branchpoint and candidate machine-readable outputs.

The stable machine-readable semantics are formalized in `FEATURE_CONTRACT.json`, and synthetic regression coverage is in `test_seqminer.py`.

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
-> prefix-valid cross-state timer reload edges
-> ambiguous anchor branchpoints
-> eventual exact local attack
-> cross capture / explicit-scene / target stability
-> Browser prospective candidate ranking
```

Until one of those triggers occurs, there is no remaining generic offline sequence-mining step that can honestly produce a new exact attack rule from the connector-visible corpus.
