# BASECAP — Shared Labeled WinKawaks Capture Dataset

## Mission

BASECAP owns reusable, labeled WinKawaks raw captures so GEO, EFIELD, RAWMINE, and future local research do not repeatedly ask the operator to collect the same basic scenes.

BASECAP is an acquisition/data-catalog lane only. It does not own GEO/EFIELD semantic conclusions and must not modify Browser production rules.

## Ownership

BASECAP may write only:

```text
parallel/BASECAP/**
```

Collector task IDs must use:

```text
BASECAP-*
```

Do not modify `parallel/GEO/**`, `parallel/EFIELD/**`, `parallel/RAWMINE/**`, WOF mainline files, production-shadow, or game RAM.

## Core rule: reuse before recapture

Before creating any new BASECAP task:

1. inspect `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`;
2. inspect existing GEO/EFIELD captures when their scene metadata is authoritative enough to reuse;
3. register an existing capture instead of repeating it when the material conditions match;
4. collect only missing conditions or explicit discriminators.

Never invent a scene label from raw bytes alone.

## Immutability / no overwrite

Every capture uses a globally unique `taskId` and is treated as an immutable dataset identity.

Canonical raw path for reusable captures:

```text
captures/<taskId>.jsonl.gz
```

Use `uploadRawStream=true` for BASECAP unless there is a specific reason not to. Never reuse an old task ID for a new capture. If repeating a scene, create a new task ID and mark the old catalog entry `SUPERSEDED` only when justified.

## Required label for every reusable capture

Each catalog entry must include:

```text
captureId/taskId
status = VALID | SUPERSEDED | INVALID
rawPath
capturedAtUtc
ROM/game/session identity when known
player occupancy/configuration
pre-capture scene/setup
operatorGate instructions when used
operator action during capture
durationSeconds
hz
layout = P1 + P2 + P3 + 20 enemies, stride 0xE0, 5152 bytes/frame
intentionalChangedVariables
intentionalHeldStableVariables
intendedReuseQuestions
knownConfounders
sourceEvidence for the label
```

## Initial baseline suite

Do not blindly collect all of these if equivalent retained raw already exists. Audit first, then fill gaps.

Suggested baseline families:

```text
B00 static idle baseline
B10 P1 horizontal-only movement
B11 P1 vertical/floor-depth-only movement
B12 P1 facing/turn discriminator with minimal displacement
B13 P1 action/animation diversity while approximately position-stable
B20 camera-scroll discriminator
B30 ordinary combat diversity
B31 enemy lifecycle spawn/active/death diversity
B32 enemy target/retarget diversity
B40 P2/P3 structure replication only after P1 geometry is sufficiently understood
```

The exact scene instructions must be narrow and observable. Prefer short controlled bursts over generic 60-second natural captures.

## Operator interaction

Use `operatorGate.required=true` only for a scene that genuinely needs the operator.

The operator workflow is:

```text
prepare requested scene
-> run READY_WOF_TASK.bat once
-> perform any explicitly requested during-capture action
-> Collector finishes automatically
```

READY is bound to the active task and is not a persistent mode.

## Completion standard

BASECAP v1 is complete when:

- the catalog contains the reusable basic scenes actually needed by GEO/RAWMINE/EFIELD;
- every VALID entry has an unambiguous label and retained raw path;
- duplicate scenes are not recollected without a documented reason;
- GEO/RAWMINE can consume the catalog directly without asking the operator to move machine-readable data between chats.
