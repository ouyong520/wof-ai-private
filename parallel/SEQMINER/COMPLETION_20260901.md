# SEQMINER Current-Corpus Completion — 2026-09-01

Lane: `parallel/SEQMINER/**`  
Evidence namespace: **WinKawaks-local discovery unless explicitly marked Browser evidence**  
Status: **COMPLETE for the current connector-visible retained corpus**

## Completion criterion

SEQMINER is complete for the current corpus when all useful ordered information can be represented and ranked without:

- pretending a structural phase is an exact move label;
- counting repeated script loops as independent evidence;
- leaking post-event state into precursor features;
- inventing stage/scene/wave labels;
- assuming WinKawaks offsets equal Browser/WASM offsets;
- requesting generic recapture merely to grow sample volume.

That criterion is now met.

## Why this lane exists

Browser evidence already proves that isolated-state prediction is insufficient:

### T18

The exact state:

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

was prospectively followed by both:

```text
A4704 @ 19.9 ms
A4712 @ 100.4 ms
```

with target/side stable. The next useful unit is ordered post-anchor context.

### T23

WOF-047 resolved:

```text
A4792 = 3
A4920 = 3
A5888 = 2
```

and the A5888 path:

```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
-> A5888
```

contains a first state that also occurs on A4792. A4792/A4920 are themselves multi-branch, so a branch-set model is required.

## Retained local corpus consumed

The current local evidence base provides:

- 7 valid EFIELD natural-gameplay captures;
- 2 WinKawaks sessions;
- 23,400 frames;
- 468,000 physical enemy-slot samples;
- 60,271 type-present samples;
- all local nonzero types T1..T31;
- 1,604 same-type episodes;
- local T18: 528 samples;
- local T23: 2,140 samples.

`parallel/SWEEPATLAS/CAPTURE_INDEX.json` additionally establishes that current retained data is not the intended labeled full-game sweep:

```text
stageSceneWaveLabelsAvailable = false
fullSweepSeriesPresent = false
```

No fake stage/scene/wave reverse index is created.

## Executor topology exhausted

The retained local executor is represented as:

```text
logical cursor + embedded flags
-> timer34 / mode35 / gate37
-> phase tuple (6C,70,72,73,77)
-> sequential successor / branch / loop reset / wait
```

Key structural results incorporated by SEQMINER:

- logical `+0x0A` cursor destination phase prediction remains near deterministic across held-out runs;
- `02008BE0` is a high-volume conditional branch/wait hotspot;
- `02008C12`, `02008C52`, `02005ED6` are loop/reset-heavy nodes;
- embedded flags materially split ambiguous logical cursor values;
- `+0x35` is an independent state-machine axis rather than part of the `+0x34` numeric countdown;
- literal `TM1` is insufficient because several records can hold at timer1 for tens to hundreds of frames.

## v3 representation correction completed

Retained EFIELD reports contain 52 delayed `+0x73=1B` residences that enter at `+0x34=8` and load upward to 9..17 within the first 1..3 frames.

At the delayed reload edge:

```text
+0x35 changes = 52/52
+0x42 changes = 52/52
```

Because `+0x35` is part of the compressed core state, the positive `+0x34` load can cross a compressed-state boundary. State-local timer history is therefore insufficient.

`seqminer.py` v3 now has cycle-prefix reload features that preserve:

```text
coreFrom/coreTo
cursorFrom/cursorTo
mode35From/mode35To
phaseFrom/phaseTo
timer34 from/to
timer42 from/to
terminal timer1 hold before reload
exact + normalized reload family
```

Feature families:

```text
timer34_reload_exact
timer34_reload_norm
cross_core_reload_exact
cross_core_reload_norm
```

### Event-boundary guard

The known 52 delayed-`1B` reloads occur after `+0x73` has already become nonzero. Therefore:

```text
default +0x73 proxy mode -> reload is post-event -> NOT a predictor
future explicit exact-attack mode -> reload is eligible only if exact attack is still zero before it
```

This closes a potential leakage/overclaim bug. The 52-event set validates the representation, not default-mode predictive support.

## Confidence contract completed

The machine-readable rules are in `FEATURE_CONTRACT.json`.

Important guarantees:

- one feature signature contributes at most one support unit per resolved cycle;
- one ambiguous anchor contributes at most one attack-support unit per resolved cycle;
- repeated loop visits remain separately visible as raw occurrence diagnostics;
- capture filename is provenance fallback, not authoritative scene evidence;
- all explicit `stage/scene/sceneId/room/wave` dimensions are preserved together when they exist;
- event-edge target changes are retained for auditing;
- event-edge and post-event state are excluded from predictor features.

Synthetic regression coverage is provided by `test_seqminer.py` for:

- cross-core timer reload retention;
- same-core reload retention;
- cycle-based branchpoint support versus raw loop count;
- explicit multi-dimension scene labels;
- capture-filename fallback semantics.

## Exact attack descriptor audit completed

`EXACT_ATTACK_DESCRIPTOR_AUDIT.md` closes the most important semantic risk.

Current result:

```text
exactLocalAttackDescriptor = UNPROVEN
```

The bridge's attack-themed reports remain structurally anchored:

- `ATTACK_CYCLE.md` defines an episode as contiguous `+0x73 != 0`;
- `MOVE_ATTACK.md` ranks fields by association with attack-phase transitions;
- `ACTIVE_STATE.md` uses lifecycle/type-present activity rather than Browser semantic attack ACTIVE;
- the retained statistical summary does not expose a named `activeAttack` field.

Therefore `+0x6C/+0x73/+0x70/+0x72/+0x77/+0x37` and other attack-selective candidates remain executor phase/gate context, not exact move identities.

No offset is relabeled merely to unblock SEQMINER.

## Current Browser return queue

Highest-value prospective work remains outside this local write lane:

1. T18 post-BODY4728 first distinct state / pair / triple split.
2. T23 A5888 complete BODY4936 ordered tail.
3. T23 A4792/A4920/A5888 branch-set validator.
4. Cross-target invariance for any surviving branch.

`BROWSER_VALIDATION_QUEUE.md` remains the handoff. SEQMINER does not modify Browser production code or advance WOF-052.

## Delivered artifacts

- `README.md`
- `SEQUENCE_ATLAS.md`
- `ATTACK_BRANCHES.md`
- `CANDIDATES.json`
- `BROWSER_VALIDATION_QUEUE.md`
- `FRONTIER.md`
- `FEATURE_CONTRACT.json`
- `EXACT_ATTACK_DESCRIPTOR_AUDIT.md`
- `seqminer.py` v3
- `test_seqminer.py`
- this completion record

## No-recature decision

```text
newGenericCollectorTask = NO
bulkCollectorTasks = NO
manualRawTransferRequest = NO
```

A new local capture is justified only if a concrete, already-ranked ambiguity becomes one bounded discriminative experiment away from resolution. Current blockers are not generic sample-count blockers.

## Reopen triggers

SEQMINER exact-label mining resumes only when at least one of these becomes true:

1. a retained labeled full-game sweep series becomes available; or
2. a WinKawaks-local exact move/attack descriptor is independently proven.

Then run `seqminer.py` v3 across retained raw and regenerate:

```text
zero-prefix cycles
-> ordered states
-> final / tail2 / tail3
-> pair / triple
-> exact timer / normalized timer
-> terminal-hold families
-> prefix-valid cross-state reload edges
-> ambiguous branchpoints
-> exact eventual local attacks
-> cross-capture / explicit-scene / target stability
-> Browser prospective candidate ranking
```

Until one of those triggers occurs, current-corpus SEQMINER work is cleanly complete at a genuine evidence boundary.
