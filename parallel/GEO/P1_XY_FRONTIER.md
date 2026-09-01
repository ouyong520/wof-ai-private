# GEO P1 X/Y frontier

Updated: 2026-09-01

Scope: WinKawaks local discovery only. Read-only. No Browser mainline changes, no production-shadow changes, no RAM writes.

## Current objective

1. P1 X: **CLOSED / CONFIRMED**.
2. P1 Y/floor-depth: **CLOSED / CONFIRMED**.
3. Advance only to: **P2/P3 same structure / same offsets**.

Do not reopen P1 X/Y unless new evidence directly contradicts the confirmed models.

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

Confirmation basis includes repeated cross-page continuity (`252 -> 0` with page `0 -> 1`, and `254 -> 2` with page `0 -> 1`) plus the 815-event RAWMINE X screen. No further horizontal-only P1 X acquisition is justified.

## P1 Y / floor-depth — CONFIRMED

Authoritative field:

`Y_floor_depth = U8(+0x08)`

**Status: CONFIRMED — P1 floor/depth Y integer coordinate.**

| Candidate | Status | Evidence / interpretation |
|---|---|---|
| `U8(+0x08)` | **CONFIRMED** | authoritative P1 floor/depth Y integer coordinate |
| `+0x09` as Y fraction | REJECTED | no dynamic fraction evidence |
| `+0xA2` | REJECTED as authoritative Y | cached/mirror value tracking `+0x08` |
| `+0x0C/+0x11` | REJECTED as floor/depth Y | jump/Z/vertical-displacement family |

### Confirmation run — RAWMINE-005 cross-lane evidence

`RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`

Identity/result verified:

- taskBlobSha `3d91bb9b77e3618500db9bde8b2145d909d4b441`
- Collector `DONE / PASS`
- readOnly `true`; writesGameMemory `false`
- 40 s @ 60 Hz, 2400 samples, achieved ~59.981 Hz
- bytes/frame 5152
- readErrors 0; frameSizeErrors 0
- distinctRawFrameCount 2097
- raw `captures/RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z.jsonl.gz`
- original SHA256 `7ad6545814fcdca86efd683103154a3699e6d6b3d2ce40b243fdd17ef20f6c62`
- compressed SHA256 `2389b53ff00ff6c23b4ab39ae8d46c059f87c4bf8f65b04df11d2132005c1efd`

Operator execution was explicitly confirmed after capture: exact READY task accepted, visible RIGHT/LEFT traversal for roughly 15 s, then visible UP/DOWN floor-depth traversal for roughly 20 s, with no attack/jump/extra action and P2/P3 untouched.

Neutral RAWMINE long-window report:

- sourceRun matches RAWMINE-005 exactly
- `+0x08` eligibleChangeEvents: **536**
- other P2/P3 `+0x08` change rate: **0.0**
- selected-slot specificity: **1.0**
- small circular delta ratio: **1.0**
- bidirectional delta score: **0.955224**
- `+0xA2` also changes 536 times and remains the previously rejected mirror/cache partner

The RAWMINE helper itself reports `LONG_WINDOW_PLAYER_ATTRIBUTION_FAILED` only because its positive-control gate requires reconstructed X motion and recorded zero X events in all three retained player slots. That gate failure is retained as an analyzer/positive-control anomaly, not treated as evidence that the operator manipulation failed: the operator explicitly confirmed visible motion, the retained player fingerprints remain stable, and the controlled run contains a dense, P1-specific, bidirectional, small-step `+0x08` trajectory while untouched P2/P3 remain static at that offset.

This closes the coverage gap that kept `+0x08` at STRONG_CANDIDATE. Combined with earlier independent evidence that `+0x08` is stable under horizontal movement/jump-Z dynamics and that `+0xA2` mirrors it, GEO promotes:

`P1 +0x08 = CONFIRMED — floor/depth Y integer coordinate`

## Earlier insufficient attempts

GEO-0008, RAWMINE-001, GEO-0009, GEO-0010 and GEO-0011 remain useful negative-control/history records. Their lack of `+0x08` motion is treated as ineffective or attribution-limited manipulation, not contradiction of the confirmed field.

## Stop condition reached

P1 X and P1 Y are both CONFIRMED. P1 research stops here.

Next and only permitted GEO stage:

`P2/P3 是否同结构同 offset`
