# GEO P2/P3 same-offset structure frontier

Updated: 2026-09-01

Scope: WinKawaks local discovery only. Read-only. No Browser mainline changes, no production-shadow changes, no RAM writes.

## Entry condition

P1 geometry is closed:

- `X = 256 * U8(+0x0B) + U8(+0x04)` — CONFIRMED.
- `Y_floor_depth = U8(+0x08)` — CONFIRMED.

Do not reopen P1. Current phase is only whether P2/P3 use the same structure and offsets.

## BASECAP v1 reuse rule — authoritative acquisition source

BASECAP v1 is COMPLETE. For the P2/P3 same-structure question, the canonical acquisition sources are now the BASECAP catalog entries below. Do not request or queue replacement P2/P3 movement captures unless the catalog is later shown to lack a genuinely new discriminator.

### B40-P2 — canonical controlled P2 XY

- taskId: `BASECAP-B40-P2-xy-16s60-20260901-0600Z`
- taskBlobSha: `5aa3fbbeb226ee411327ead0177e347841977a78`
- raw: `captures/BASECAP-B40-P2-xy-16s60-20260901-0600Z.jsonl.gz`
- 16 s @ ~60 Hz, 960 frames, 888 distinct frames
- 0 read errors; 0 frame-size errors; read-only PASS
- operator label: P2 only, open/no-camera-scroll scene, P1 still, P3 untouched
- sequence: RIGHT ~2 s -> idle ~1 s -> LEFT ~2 s -> idle ~1 s -> UP ~2 s -> idle ~1 s -> DOWN ~2 s -> idle to end
- no attack, jump, or extra action

### B40-P3 — canonical controlled P3 XY

- taskId: `BASECAP-B40-P3-xy-16s60-20260901-0601Z`
- taskBlobSha: `c54ea1e777e4004501bad37cf8f350da8d65f7ea`
- raw: `captures/BASECAP-B40-P3-xy-16s60-20260901-0601Z.jsonl.gz`
- 16 s @ ~60 Hz, 960 frames, 841 distinct frames
- 0 read errors; 0 frame-size errors; read-only PASS
- operator label: P3 only, open/no-camera-scroll scene, P1/P2 still
- same RIGHT / idle / LEFT / idle / UP / idle / DOWN / idle sequence
- no attack, jump, or extra action

BASECAP supplies acquisition truth only. GEO still owns the semantic decision about offsets and structure.

## Existing pre-BASECAP cross-slot evidence

RAWMINE neutral cross-slot structure report before B40 reuse already establishes:

- P2 X same-offset evidence: `SUPPORTED`
- P3 X same-offset evidence: `SUPPORTED`
- P2/P3 `+0x08` depth same-offset evidence: previously `INSUFFICIENT_COVERAGE`

P2 prior aggregate retained-block evidence:

- confirmed-X composite dynamic: 187 events
- `+0x04`: 187 events
- `+0x0B`: page coverage present

P3 prior aggregate retained-block evidence:

- confirmed-X composite dynamic: 44 events
- `+0x04`: 44 events

The previous depth coverage gap is exactly what canonical B40-P2/B40-P3 now cover. Therefore no new P2/P3 acquisition is justified.

## Superseded GEO acquisition attempts

`GEO-0012-p2-same-xy-offsets-12s60-20260901-0054Z` was mechanically healthy but manipulation/attribution-invalid for the P2 question. It is not negative evidence.

`GEO-0013-p2-attribution-depth-long-35s60-20260901-0104Z` is superseded for the current decision by BASECAP B40-P2. It must not be used as a reason to request another P2 capture.

## Current offline discriminator

Use the canonical B40 raws directly and test only the already-open structure question.

For B40-P2:

1. During catalog-labeled RIGHT/LEFT windows, verify retained P2 `256*U8(+0x0B)+U8(+0x04)` changes bidirectionally while P1/P3 controls remain stable except unrelated background noise.
2. During catalog-labeled UP/DOWN windows, verify retained P2 `U8(+0x08)` changes repeatedly, in small steps and both directions, while horizontal X and jump/Z family `+0x0C/+0x11` do not explain the depth trajectory.
3. Check `+0xA2` only as the known mirror/cache family; authoritative-Y promotion remains with `+0x08` if B40 preserves the same live-vs-lag relationship seen on P1.

Repeat the same test on B40-P3 with P1/P2 as untouched controls.

Decision rule:

- If B40-P2 satisfies the same X and +0x08 depth structure under its controlled label, promote P2 same X/Y offsets to CONFIRMED.
- If B40-P3 satisfies the same X and +0x08 depth structure under its controlled label, promote P3 same X/Y offsets to CONFIRMED.
- Do not infer operator actions from raw values; phase labels come only from the BASECAP catalog/task/operator evidence.
- Do not treat historical INVALID/SUPERSEDED captures as canonical.
- Do not advance to facing until both P2 and P3 are locked.

## Tooling note

The legacy bridge workflow `.github/workflows/rawmine-p2p3-cross-slot.yml` currently selects only `captures/GEO-*.jsonl.gz` and `captures/RAWMINE-*.jsonl.gz`; it does not yet include `BASECAP-*`. That is an analysis-input compatibility gap, not an acquisition gap. GEO must not compensate by re-capturing P2/P3.