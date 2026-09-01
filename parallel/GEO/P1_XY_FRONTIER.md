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
| `+0x9C` | REJECTED as authoritative X | lagged/render local-X mirror/cache |
| `+0xA3` | REJECTED as authoritative X page | page/cache mirror family |
| contiguous X high bytes `+0x06..07` | REJECTED | false ~252 px discontinuities at real page wraps |

Confirmation basis includes repeated cross-page continuity (`252 -> 0` with page `0 -> 1`, and `254 -> 2` with page `0 -> 1`) plus the 815-event RAWMINE X screen. No further horizontal-only P1 X acquisition is justified. Horizontal motion may only be reused as an orthogonal calibration control inside a P1-Y experiment.

## P1 Y / floor-depth — OPEN

| Candidate | Status | Evidence / interpretation |
|---|---|---|
| `U8(+0x08)` | **STRONG_CANDIDATE** | floor/depth Y integer anchor; natural corpus shows clean player-separated values and horizontal/jump stability, but only one retained +0x08 change event |
| `+0x09` as Y fraction | REJECTED | no dynamic fraction evidence |
| `+0xA2` | REJECTED as authoritative Y | cached/mirror value tracking `+0x08` |
| `+0x0C/+0x11` | REJECTED as floor/depth Y | jump/Z/vertical-displacement family |

Current classification:

`P1 +0x08 = STRONG_CANDIDATE / NOT CONFIRMED / INSUFFICIENT_COVERAGE`

Historical independent local-discovery evidence remains supportive but not sufficient for promotion:

- `+0x08` commonly gives P1/P2/P3 values `48/72/96`, exactly 24 apart;
- it remains stable during horizontal movement and ordinary jump/Z dynamics;
- `+0xA2` repeatedly mirrors the same floor/depth integer anchor;
- none of this substitutes for a captured depth-changing trajectory.

## Controlled depth attempts — all mechanically healthy, manipulation invalid

### Attempt 1 — GEO-0008

`GEO-0008-p1-depth-only-5s60-20260831-2115Z`

- taskBlobSha `177ca63865714623037e8ff1a097a7698e3bf75e`
- PASS, 300 samples, read-only, zero read/frame-size errors
- X changes 0; Z changes 0; `+0x08` changes 0
- RAWMINE: `CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

### Attempt 2 — RAWMINE-001 cross-lane discovery evidence

`RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`

- taskBlobSha `c630db7f31366f03e1e1b8565c9d2b5a95bdcf90`
- PASS, 481 samples, read-only, zero read/frame-size errors
- X changes 0; Z changes 0; `+0x08` changes 0
- RAWMINE: `CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

### Attempt 3 — GEO-0009

`GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z`

Identity/result verified:

- taskBlobSha `3b5b892ee75c4b29634a161c34c8b7b5bad0eab4`
- collector DONE / PASS
- 8 s @ 60 Hz, 480 samples, achieved ~59.986 Hz
- distinct raw frames 439
- bytes/frame 5152
- read errors 0; frame-size errors 0
- mapping `xor3`
- readOnly true; writesGameMemory false
- raw `captures/GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z.jsonl.gz`
- original SHA256 `a16b9e69a10c69545033947cb437fcce314bec89e2196aa6323292b4b7269aeb`
- compressed SHA256 `31fc6df75f345f65cb7146f6121e2ab66466fca8a87d1c517d4e517ec6b38187`

Latest RAWMINE neutral screen commit `0a0d5aac6e6aefc73d51e5bfe99c5b3da384300f` consumes GEO-0009. For this attempt:

- controlValidity `PASS`
- manipulationValidity `FAIL`
- reconstructed X changes `0`
- Z changes `0`
- `+0x08` anchor events `0`
- manipulationEvidenceOffsets `[]`
- strongest dynamic byte was `+0x7F`, but P1 change rate ~0.524 and untouched P2/P3 rate ~0.507 with specificity ~0.508, so it is shared/background dynamics, not P1-specific floor/depth evidence.

Interpretation: **GEO-0009 is not negative evidence against `+0x08`.** The raw is mechanically valid but still contains no P1-specific movement signature at all. Three nominal depth-only attempts now show the same failure mode, so another identical UP/DOWN-only retry is not scientifically justified.

Cross-corpus player fingerprints remain structurally stable: `+0x20`, `+0x21`, `+0x26`, `+0x62`, `+0x7C`, and `+0x92` distinguish the three retained player blocks with zero mismatches across 27,663 compatible frames. This validates block ordering/fingerprints, but does not by itself prove that the operator-controlled character during a particular gated burst is the retained P1 block that the experiment expects.

## Current discriminator — GEO-0010 attribution-calibrated depth traverse

Queued task:

`GEO-0010-p1-attribution-depth-calibration-10s60-20260901-0033Z`

taskBlobSha:

`cae503ec7fbaff99ea791d6f57eb376a52afef7a`

Single owner question:

**Can the tracked P1 object first be validated in-burst by the already-confirmed X composite responding to a brief RIGHT -> LEFT calibration, and then, on that same validated object, which offset changes continuously/reversibly during UP -> DOWN floor/depth travel while Z and untouched P2/P3 provide controls?**

The horizontal segment is not a reopened X study; it is only a positive-control attribution marker for the Y experiment.

Required sequence encoded in the gate:

1. wide open area where both axes visibly move;
2. READY;
3. HOLD RIGHT ~1.5 s;
4. HOLD LEFT ~1.5 s;
5. HOLD UP ~2.5 s;
6. HOLD DOWN ~2.5 s;
7. no attack/jump/extra action; P2/P3 untouched.

Decision rule after GEO-0010:

- If confirmed X responds in the RIGHT/LEFT calibration on retained P1, P1 attribution for this burst is validated.
- Conditional on that validation, if `+0x08` then shows repeated small-step UP/DOWN changes and reverses on return while Z and P2/P3 remain stable, promote `+0x08` directly to `CONFIRMED — P1 floor/depth Y integer coordinate`.
- If X calibration validates P1 but a different P1-specific offset cleanly follows UP/DOWN, evaluate that offset against `+0x08` and promote/reject only from the observed trajectory.
- If X calibration does **not** appear on retained P1, do not interpret the subsequent UP/DOWN segment semantically; the next problem is operator/player attribution, not another Y-field retry.

## Stop condition

The moment P1 X and P1 Y are both CONFIRMED, stop P1 X/Y research and advance only to:

`P2/P3 是否同结构同 offset`
