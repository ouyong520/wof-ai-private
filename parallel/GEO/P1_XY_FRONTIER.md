# GEO P1 X/Y frontier

Updated: 2026-08-31

Scope: WinKawaks local discovery only. Read-only. No Browser mainline changes, no production-shadow changes, no RAM writes.

## Current sole objective

1. Lock P1 X coordinate field.
2. Lock P1 Y/floor-depth coordinate field.

Do not advance to P2/P3 structure, facing, top/bottom, or camera until both are locked.

## P1 X candidates

| Candidate | Status | Evidence / interpretation |
|---|---|---|
| `U8(+0x04)` | STRONG_CANDIDATE | local/integer X byte; repeatedly changes with horizontal motion |
| `U8(+0x0B)` | STRONG_CANDIDATE | X page/high byte; repeated wraps `252/page0 -> 0/page1` and `254/page0 -> 2/page1` preserve continuous X |
| `256*U8(+0x0B)+U8(+0x04)` | STRONG_CANDIDATE | current authoritative world-X model; requires one controlled horizontal-only discriminator before promotion to CONFIRMED |
| `+0x9C` | REJECTED as authoritative X | lagged/render local-X cache |
| `+0xA3` | REJECTED as authoritative X page | cache/page mirror family |
| contiguous 4-byte X using `+0x06..07` | REJECTED | produces false ~252 px discontinuities at observed page wraps |

## P1 Y candidates

| Candidate | Status | Evidence / interpretation |
|---|---|---|
| `U8(+0x08)` | STRONG_CANDIDATE | floor/depth Y integer anchor; stable player anchors and prior natural movement evidence |
| `+0x09` as Y fraction | REJECTED | stable player/form-specific behavior; no dynamic fraction proof |
| `+0xA2` | REJECTED as authoritative Y | cached floor/depth value tracking `+0x08` |
| `+0x0C/+0x11` | REJECTED as floor/depth Y | vertical/Z jump displacement family |

## Required controlled sequence

### GEO-0007 — horizontal-only discriminator
Question: **Which P1 offsets change with horizontal-only motion, while the Y candidate remains stable?**

Success condition for X:
- composite `256*U8(+0x0B)+U8(+0x04)` changes monotonically/continuously with left/right P1 motion, including page wrap if encountered;
- `+0x08` remains stable except unavoidable scene noise;
- cache fields may lag/mirror but cannot replace the authoritative composite.

If passed, promote P1 X composite to CONFIRMED.

### Next only after GEO-0007
Run one vertical-only P1 burst.
Question: **Which P1 offset changes with up/down floor movement while confirmed X remains stable?**

Do not perform any unrelated geometry study before these two questions are closed.
