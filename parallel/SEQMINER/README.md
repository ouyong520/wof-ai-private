# SEQMINER — WinKawaks enemy attack ordered-sequence mining

Status: **bounded current-corpus mining complete / reusable miner v3 ready / WinKawaks-local only**

Write boundary: `parallel/SEQMINER/**` only.

## Mission

SEQMINER exists because one pre-attack state is not necessarily enough to determine the eventual attack.

Browser evidence already proves this twice:

- T18: exact `BODY4728/A4/B2/TM1` was prospectively followed by both `A4704` and `A4712`.
- T23: WOF-047 resolved eight zero-cycle traces across `A4792=3`, `A4920=3`, `A5888=2`; at least one state belongs to more than one eventual-attack branch.

The unit of analysis is therefore:

```text
zero attack / zero structural proxy
-> ordered distinct executor states
-> tail2 / tail3
-> transition pair / triple
-> cursor/flag/mode progression
-> exact + normalized timer progression
-> cross-state timer reload edges / conditional holds
-> future same-object nonzero event / ACTIVE
```

Nothing in this lane is a Browser production rule.

## Corpus boundary

`parallel/SWEEPATLAS/**` confirms:

- seven retained EFIELD natural-gameplay runs;
- 23,400 frames;
- 468,000 enemy-slot samples;
- 60,271 type-present samples;
- all local types T1..T31 observed;
- T18 (`+0x24=0x12`) present for 528 samples;
- T23 (`+0x24=0x17`) present for 2,140 samples.

Its capture index also explicitly reports:

```text
stageSceneWaveLabelsAvailable = false
fullSweepSeriesPresent = false
```

There is still no retained `BASECAP-SWEEP-*` full-game labeled series on GitHub `main`. This is an evidence boundary, not a request for manual raw transfer and not permission to invent scene labels.

## Local executor backbone

SEQMINER reuses EFIELD's confirmed/strong fields:

| local field | sequence role |
|---|---|
| `+0x24` | type/type-present lifecycle |
| `+0x2D/+0x2E` | compact control/action context |
| `+0x2F..+0x32` | flagged U32 BE logical record cursor |
| `+0x34` | record dwell/countdown |
| `+0x35` | independent dwell/control mode |
| `+0x37` | attack/executor gate/substate candidate |
| `+0x6C/+0x73` | fine -> coarse phase projection |
| `+0x70/+0x77` | second fine -> coarse projection |
| `+0x72` | joint-phase companion |
| `+0x6D..+0x6E` | live/materialized target |
| `+0x3D..+0x3E/+0xC6` | stored association |
| split `+0x6F/+0x68` | separate player-reference layer |
| `+0xCC` | association synchronization checkpoint |
| `+0xB0/+0xB4/+0xB6` | profile/runtime context |
| `+0xB9/+0xBB` | locomotion context |
| `+0x28/+0x99` | sparse context only |

`+0x73 != 0` remains only a structural executor-phase proxy. It is not semantic attack ACTIVE.

## Automatic miner v3

`seqminer.py` automatically discovers retained `.jsonl` / `.jsonl.gz` files.

```bash
python wof-ai-private/parallel/SEQMINER/seqminer.py \
  --captures wof-winkawaks-bridge/captures \
  --output wof-ai-private/parallel/SEQMINER/generated
```

Default mode is conservative:

```text
zero proxy  = enemy+0x73 == 0
event proxy = first same-object enemy+0x73 != 0
label       = first nonzero +0x73 value
```

Explicit attack mode is allowed only after an exact WinKawaks-local move/attack field has independently been proven:

```bash
python .../seqminer.py \
  --captures .../captures \
  --output .../parallel/SEQMINER/generated \
  --attack-offset 0xNN --attack-width 2 --attack-endian be
```

### Cycle identity

The miner follows physical `(capture, enemy slot)` continuity and splits an episode when type becomes absent/changes or episode-invariant `+0xB4/+0xB6` changes. It deliberately does **not** use mutable `+0xB0` as object identity.

### Distinct state

The core key is:

```text
type
+ 2D/2E
+ logical cursor + cursor flags
+ 35/37
+ (6C,70,72,73,77)
```

Target, association, split reference, profile, locomotion and sparse flags are retained as context but do not fragment the core signature. This permits real cross-target/cross-profile stability measurement.

Each compressed state saves frame start/end/dwell plus timer start/end/min/max and terminal `timer34==1` residence.

## Exact and normalized timer families

Record-relative arrival evidence:

- ceiling: `3192/4323 = 73.84%`;
- within one: `4000/4323 = 92.53%`;
- within two: `4090/4323 = 94.61%`.

SEQMINER therefore mines exact timer profiles and normalized ceiling-distance buckets `0 | 1 | 2 | 3-5 | 6-10 | 11+`.

It also records terminal timer-1 hold buckets `0 | 1 | 2-3 | 4-9 | 10-29 | 30+`, because literal `TM1` can conceal long conditional waits.

### v3 cross-state reload correction

Retained delayed-`1B` analysis contains **52** residences that enter with `+0x34=8` and load upward shortly afterward. Critically, `+0x35` changes on `52/52` of those reload frames and `+0x42` also changes on `52/52`.

Because `+0x35` is part of the core state, a reload that coincides with the mode transition crosses a compressed-state boundary. A state-local `positiveTimer34Reloads` list can therefore miss exactly the delayed-load edge we care about.

v3 fixes that by also tracking every positive `+0x34` load at the **cycle prefix** level, before the future event, preserving:

```text
from/to timer34
coreFrom/coreTo
cursorFrom/cursorTo
mode35From/mode35To
phaseFrom/phaseTo
timer42From/timer42To
timer1 hold before reload
sameCore / cursorChanged / mode35Changed / timer42Changed
exact + record-normalized reload family
```

The future event edge is deliberately excluded from predictor features to prevent leakage.

## Confidence and scene-label rules

The machine-readable contract is `FEATURE_CONTRACT.json`.

Core rules:

- feature support is counted at most once per resolved cycle per signature;
- ambiguous-anchor attack support is also cycle-based;
- repeated loop visits remain visible separately as raw occurrence counts but never create independent confidence;
- capture filename fallback is not treated as authoritative scene evidence;
- if explicit stage/scene/room/wave fields exist later, all present dimensions are retained rather than silently keeping only the first one.

## Generated outputs

A run writes:

- `CYCLES.generated.jsonl` — resolved same-object cycles, including cycle-level timer reload edges;
- `CANDIDATES.generated.json` — final/tail/pair/triple/reload exact/normalized rankings;
- `BRANCHPOINTS.generated.json` — ambiguous anchors plus cycle-based next/previous/timer outcome distributions and separate raw loop counts;
- `SEQUENCE_ATLAS.generated.md`;
- `ATTACK_BRANCHES.generated.md`.

## Evidence classes

- `discovery_correlation` — local association only.
- `same_cycle_evidence` — ordered context precedes the same object's later event.
- `potentially_prospectively_testable_candidate` — only used in explicit exact-attack mode after repeated/pure support; still not production.

## Current highest-value results

Browser-return ranking:

1. T18 post-`BODY4728` ordered split for A4704 vs A4712.
2. T23 A5888 `BODY4936` ordered tail.
3. T23 multi-branch tail2/tail3 set for A4792/A4920/A5888.
4. Cross-target validation for surviving Browser sequences.

WinKawaks-local structural hotspots for future exact-label mining:

- `0x02008BE0` — high-volume mixed exit/conditional-wait node;
- `0x02008BD6` and `0x02005E9A` — logical-cursor ambiguity materially split by embedded flags;
- delayed-`1B` timer reload edge — a real cross-state event, not safely representable by literal `TM` or one compressed state alone;
- `0x02008C12`, `0x02008C52`, `0x02005ED6` — loop/reset branch nodes;
- long terminal-hold records `0x02008D08`, `0x02005FF8`, `0x02008D12`, `0x02006002`;
- `+0x35` transitions as an independent branch axis.

These are structural candidates only and must never be numerically copied into Browser/WASM logic.

## Stop condition

The connector-visible retained raw-derived information has been mined to the point where more generic offline reading is not expected to produce an exact all-game attack discriminator.

No Collector task is requested. Reopen exact local mining when either a labeled retained full-sweep series appears or an exact WinKawaks-local move/attack value is independently established. v3 will then regenerate exact attack-labelled final/tail/pair/triple/reload families without changing the evidence rules above.
