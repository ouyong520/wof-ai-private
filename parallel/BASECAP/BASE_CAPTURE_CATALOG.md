# BASECAP Reusable Capture Catalog

Updated: 2026-09-01

This file is the authoritative index of reusable labeled WinKawaks raw captures for local discovery work.

## Reuse rule

Before GEO, EFIELD, RAWMINE, BASECAP, or another local research lane submits a basic Collector task, inspect this catalog first. Reuse a `VALID` entry when its material acquisition conditions match the current question.

Do not reuse an entry whose scene label is uncertain or whose relevant confounder invalidates the requested comparison.

## Dataset identity

A capture is identified by its unique Collector `taskId`.

Preferred retained raw path:

```text
captures/<taskId>.jsonl.gz
```

Task IDs are immutable and must never be reused. A repeated capture receives a new task ID.

## Entry template

Copy this section for each reusable capture:

```text
### <captureId/taskId>
status: VALID | SUPERSEDED | INVALID
rawPath: captures/<taskId>.jsonl.gz
capturedAtUtc:
taskBlobSha:
ROM/game/session:
playerOccupancy:
preCaptureScene:
operatorGate:
operatorActionDuringCapture:
durationSeconds:
hz:
layout: P1 + P2 + P3 + 20 enemies; stride 0xE0; 5152 bytes/frame
intentionalChangedVariables:
intentionalHeldStableVariables:
intendedReuseQuestions:
knownConfounders:
labelSourceEvidence:
supersedes:
supersededBy:
notes:
```

## Existing-capture audit

No existing GEO/EFIELD/RAWMINE capture is automatically declared canonical here. BASECAP must first verify that the acquisition condition can be recovered from authoritative task/result/artifact metadata. If it cannot, leave it out or register it as non-canonical exploratory evidence.

## Canonical reusable captures

None registered yet.

BASECAP should first audit retained existing captures, register those that already have trustworthy labels, and only then collect missing baseline scenes.
