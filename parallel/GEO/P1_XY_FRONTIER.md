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

## Controlled attempt 1 — GEO-0008

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

RAWMINE verdict:

`CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

- reconstructed X (`+0x04/+0x0B`) changes: 0;
- reconstructed Z (`+0x0C/+0x11`) changes: 0;
- `+0x08` changes: 0;
- no byte satisfies the manipulation guardrail of >=5 P1 changes, >=0.80 P1-specificity, and <=0.05 untouched-P2/P3 change rate.

Interpretation: mechanically valid capture, ineffective depth manipulation. This is **not negative evidence against `+0x08`**.

## Controlled attempt 2 — RAWMINE-001 cross-lane evidence

Task:

`RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`

GEO consumed this read-only cross-lane result as discovery evidence only. Identity verified:

- `taskId = RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`
- `taskBlobSha = c630db7f31366f03e1e1b8565c9d2b5a95bdcf90`
- collector result `PASS`
- 8 s @ 60 Hz, 481 samples, achieved ~60.011 Hz
- distinct raw frames: 433
- read errors: 0
- frame-size errors: 0
- mapping: `xor3`
- read-only: true
- writes game memory: false
- raw: `captures/RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z.jsonl.gz`
- original SHA256: `62d9e7a48dbcaf5103d7e126d7a97860afb707db2934aa20c97c42134f4c5a79`
- compressed SHA256: `4ae3e3fff35a56c5727cec152219aa15d294f0ac65e28a3d4f2de988622b62e5`

The refreshed RAWMINE candidate screen commit `f3ec6cb984abd43c821038e59e666b644d039ee3` includes 13 raw runs and selects this retry as controlled depth attempt 2.

Automated verdict remains:

`CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

For attempt 2:

- X control: `PASS`, reconstructed X changes: 0;
- Z control: `PASS`, Z changes: 0;
- manipulation: `FAIL`;
- `+0x08` events: 0.

Interpretation: a second mechanically healthy capture again failed to contain a visible P1-specific depth trajectory in player-object evidence. This remains **coverage/manipulation failure**, not negative evidence against `+0x08`.

## Current discriminator — GEO-0009 only

Only question:

**When P1 visibly traverses lower lane -> upper lane -> lower lane, which offset changes continuously with depth while confirmed X and Z remain stable?**

Queued GEO-owned task:

`GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z`

Task purpose is explicitly limited to testing the P1 Y/floor-depth question and `U8(+0x08)` against orthogonal controls.

Required operator behavior encoded in the task gate:

- before READY, put P1 in a wide open walkable area where UP/DOWN visibly changes floor/depth lane;
- P2/P3 idle;
- run `READY_WOF_TASK.bat` only when ready to move immediately;
- immediately HOLD UP continuously for about 3 seconds — do not tap — and visually ensure substantial upper/deeper-lane travel;
- then HOLD DOWN continuously for about 3 seconds and visibly return toward the lower/near lane;
- repeat the same traverse if time remains;
- no LEFT/RIGHT;
- no attack;
- no jump;
- no other action;
- P2/P3 untouched.

Promotion rule for `+0x08`:

If `+0x08` shows repeated continuous small-step changes during the actual UP/DOWN traverse, reverses direction on return, while confirmed X composite is essentially stable, Z family is essentially stable, and P2/P3 `+0x08` are essentially stable, promote directly to:

`CONFIRMED — P1 floor/depth Y integer coordinate`

Otherwise classify strictly as:

- `CONFIRMED`
- `STRONG_CANDIDATE`
- `REJECTED`
- `UNKNOWN`

Do not reinterpret another ineffective manipulation as negative field evidence.

## Stop condition

The moment P1 X and P1 Y are both CONFIRMED, stop P1 X/Y research and advance only to:

`P2/P3 是否同结构同 offset`
