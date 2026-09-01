# GEO P1 X/Y frontier

Updated: 2026-09-01

Scope: WinKawaks local discovery only. Read-only. No Browser mainline changes, no production-shadow changes, no RAM writes.

## Current sole objective

1. P1 X: **CLOSED / CONFIRMED**.
2. P1 Y/floor-depth: **OPEN** — only remaining GEO question.

Do not advance to P2/P3 structure, facing, top/bottom, or camera until P1 Y is locked.

## P1 X — CONFIRMED

Authoritative model:

`X = 256 * U8(+0x0B) + U8(+0x04)`

**Status: CONFIRMED — P1 world/local-page X coordinate.**

| Candidate | Status | Evidence / interpretation |
|---|---|---|
| `U8(+0x04)` | STRONG_CANDIDATE | local/integer low-byte component of the confirmed composite; RAWMINE horizontal event recall 1.0, precision 1.0, vertical/Z-only recall 0, score ~0.9906 |
| `U8(+0x0B)` | STRONG_CANDIDATE | page/high-byte component of the confirmed composite; sparse but highly specific page changes, precision 1.0 |
| `256*U8(+0x0B)+U8(+0x04)` | **CONFIRMED** | authoritative P1 world/local-page X coordinate |
| `+0x9C` | REJECTED as authoritative X | strong lagged/render local-X mirror/cache; cannot replace authoritative composite |
| `+0xA3` | REJECTED as authoritative X page | page/cache mirror family |
| contiguous 4-byte X using `+0x06..07` | REJECTED | produces false ~252 px discontinuities at real page wraps |

Confirmation basis:

- observed real page wrap: local `252 -> 0`, page `0 -> 1`, composite `252 -> 256`;
- second observed wrap family: local `254 -> 2`, page `0 -> 1`, preserving continuous composite X;
- RAWMINE P1-X screen: 815 owner-anchor events; `+0x04` is the strongest single-offset horizontal discriminator with recall/precision 1.0 and zero vertical/Z-only recall;
- `+0x0B` is sparse but specific and supplies the required page transition component;
- alternative cache/mirror fields lag and the contiguous `+0x06..07` interpretation fails at observed wraps;
- the superseded `GEO-0007-p1-horizontal-only-5s60-20260831-2038Z` operator gate was removed by bridge commit `7307287fe0568211e3eb4068da3fae88f31f9d4c` (`GEO: cancel superseded P1 X gate after offline confirmation`).

No further horizontal-only natural or controlled acquisition is justified for P1 X.

## P1 Y / floor-depth — OPEN

| Candidate | Status | Evidence / interpretation |
|---|---|---|
| `U8(+0x08)` | **STRONG_CANDIDATE** | floor/depth Y integer anchor; prior natural evidence exists but retained corpus has only one anchor event |
| `+0x09` as Y fraction | REJECTED | no dynamic fraction evidence |
| `+0xA2` | REJECTED as authoritative Y | cached/mirror value tracking `+0x08` |
| `+0x0C/+0x11` | REJECTED as floor/depth Y | jump/Z/vertical-displacement family |

Current classification for `P1 +0x08`:

**STRONG_CANDIDATE / NOT CONFIRMED / INSUFFICIENT_COVERAGE.**

## GEO-0008 controlled result

Task:

`GEO-0008-p1-depth-only-5s60-20260831-2115Z`

Identity verified:

- `taskId = GEO-0008-p1-depth-only-5s60-20260831-2115Z`
- `taskBlobSha = 177ca63865714623037e8ff1a097a7698e3bf75e`
- collector result `PASS`
- 5 s @ 60 Hz, 300 samples, achieved ~60.005 Hz
- distinct raw frames: 273
- read errors: 0
- frame-size errors: 0
- mapping: `xor3`
- read-only: true
- writes game memory: false
- raw: `captures/GEO-0008-p1-depth-only-5s60-20260831-2115Z.jsonl.gz`
- original SHA256: `cf7bb9093f0389ac629e4937da866d8217a8eaf89ebf479f3797e821776678cb`
- compressed SHA256: `81f30d0ff7d68d1bb98c09d20e11474d49023ac09bb0119941f45244d876a2b3`

RAWMINE controlled-screen verdict:

`CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

Important interpretation:

- reconstructed X (`+0x04/+0x0B`) changes: 0;
- reconstructed Z (`+0x0C/+0x11`) changes: 0;
- `+0x08` changes: 0;
- no byte satisfies the manipulation guardrail of >=5 P1 changes, >=0.80 P1-specificity, and <=0.05 untouched-P2/P3 change rate;
- therefore the capture is mechanically valid but the intended visible P1 depth traversal did not occur in the recorded player-object dynamics.

This is **not negative evidence against `+0x08`**. GEO-0008 is an ineffective manipulation capture and cannot discriminate the Y field.

## Next discriminator — one visible depth traverse only

Only question:

**When P1 visibly traverses from the lower lane to the upper lane and back, which offset changes continuously with depth while confirmed X and the Z family remain stable?**

Required operator behavior for the next usable controlled burst:

- open walkable area with obvious upper/lower floor-depth separation;
- P1 only: hold UP long enough to produce a clearly visible depth displacement;
- then hold DOWN long enough to return through a clearly visible distance;
- repeat if capture time permits;
- no LEFT/RIGHT;
- no attack;
- no jump;
- P2/P3 untouched;
- 6–8 seconds at 60 Hz is sufficient.

Promotion rule for `+0x08`:

If it shows repeated continuous small-step changes during UP/DOWN, reverses direction on the return traversal, while confirmed X composite is essentially stable, Z family is essentially stable, and P2/P3 `+0x08` are essentially stable, then promote directly to:

`CONFIRMED — P1 floor/depth Y integer coordinate`

Otherwise classify the evidence strictly as one of:

- `CONFIRMED`
- `STRONG_CANDIDATE`
- `REJECTED`
- `UNKNOWN`

Do not reinterpret an ineffective operator manipulation as negative field evidence.

## Current collector coordination

A cross-lane RAWMINE operator-gated retry already exists and is currently first in the serialized Collector queue:

`RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`

Its instructions are materially the same visible UP/DOWN-only discriminator described above, and RAWMINE remains evidence-only while GEO owns semantic promotion.

Because Collector execution is serialized and duplicate operator-gated captures would answer the same single question, GEO does **not** queue a redundant `GEO-0009` while that cross-lane retry is active. GEO task IDs, when GEO itself submits the next task, must use the `GEO-*` prefix only.

After the active retry completes, GEO must first consume the resulting RAWMINE evidence with clear task/result identity. If it yields a valid visible depth trajectory, use it as discovery evidence for the owner decision. Only if the GEO owner question still remains unresolved should a new minimal `GEO-0009-p1-depth-visible-traverse-*` task be submitted.

## Stop condition

The moment P1 X and P1 Y are both CONFIRMED, stop P1 X/Y research and advance only to:

`P2/P3 是否同结构同 offset`
