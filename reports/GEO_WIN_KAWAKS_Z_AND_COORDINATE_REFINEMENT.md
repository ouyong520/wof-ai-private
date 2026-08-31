# WinKawaks player Z / coordinate refinement — GEO line

> Discovery-only WinKawaks evidence. Read-only analysis. This report does not advance WOF-045 and does not modify/promote production-shadow rules.

## Evidence

Analyzed complete normalized P1/P2/P3 objects from:

- GEO-0001 — 600 frames
- GEO-0003 — 600 frames
- GEO-0004 — 600 frames
- EFIELD-003 reuse — 3600 frames

Collector normalization reconstructs logical CPS offsets before writing `rawBlockHex`; conclusions below are not host `xor3` byte-lane artifacts.

## X: local byte + page byte

The earlier contiguous-32-bit / word-pair model is rejected by wrap continuity.

Repeated independent events show `+0x04` wrapping at the same frame that `+0x0B` changes by one page:

- GEO-0003 P1: local `252 -> 0`, page `0 -> 1` => reconstructed X `252 -> 256`.
- GEO-0003 P2: local `1 -> 254`, page `2 -> 1` => reconstructed X `513 -> 510`.
- EFIELD-003 P1: local `254 -> 2`, page `0 -> 1` => `254 -> 258`.
- EFIELD-003 P3: local `248 -> 0`, page `0 -> 1` => `248 -> 256`.

Using the adjacent `+0x06..07` word as X high instead leaves false ~252 px discontinuities at these same events.

Current strongest integer model:

`worldX ~= 256 * U8(+0x0B) + U8(+0x04)`

`+0x05` has remained zero in the current controlled/natural samples, so a fractional-X role is not established.

## Floor/depth Y

The previously used `U16BE(+0x08..09)/256` interpretation is no longer preferred.

The integer byte `+0x08` gives the especially clean P1/P2/P3 values:

- P1 = 48
- P2 = 72
- P3 = 96

These are exactly 24 px/depth units apart and stay stable during horizontal movement and ordinary jumps in the analyzed scenes.

`+0x09` is player/form-specific and remained fixed while these scenes evolved; no current evidence proves it is a fractional Y byte. Treat `+0x08` as the floor/depth anchor and `+0x09` as unknown until a controlled depth-only capture changes it.

## Z / vertical displacement

### `+0x0D` is not the fraction byte

Across repeated positive jump arcs and long negative trajectories, `+0x0D` remains fixed per player/form (examples: P1=52, P2=64, P3=0). It therefore cannot be the live low/fractional component of `+0x0C`.

### `+0x11` is the strongest subpixel/fraction candidate

`+0x11` changes almost one-for-one with `+0x0C` and takes quantized values such as:

`0, 32, 64, 96, 128, 160, 192, 224`

This is consistent with a 1/8-pixel-style phase represented in an 8-bit fraction slot.

Normal positive arc examples include:

`0 -> 7 -> 10 -> 13 -> 16 -> ... -> 30 -> ... -> 7 -> 3 -> 0`

while `+0x11` supplies the changing subpixel phase.

Negative trajectories begin as:

`0 -> 255 -> 254 -> 253 -> 251 -> 248 -> ...`

and later cross:

`... 140 -> 129 -> 118 -> 106 -> 93 -> ...`

Interpreting the `+0x0C` byte modulo 256 and unwrapping the path makes these trajectories continuous below -128 instead of creating a false signed-byte discontinuity.

Current working model:

`Z ~= unwrap_mod256( U8(+0x0C) + U8(+0x11)/256 )`

The sign/origin convention is scene/action dependent and still discovery-only, but this model is materially better supported than `S16BE(+0x0C..0x0D)/256`.

## Render/cache correction

A systematic scan of `+0x90..+0xAF` across GEO-0003, GEO-0004 and EFIELD-003 found no byte that consistently equals, lags, or shares the delta of `+0x0C` on Z-changing frames.

In particular:

- `+0xA4` remained 0 in all checked player streams.
- The old `+0xA4 = render-Z` hypothesis is retired.
- `+0x9C` remains an X/render-cache candidate.
- `+0xA2` remains a cache of integer floor/depth `+0x08`.
- `+0xA3` remains associated with X page `+0x0B`.

There is currently no proven live render-Z cache in `+0x90..+0xAF`.

## Current coordinate summary

| Offset | Current meaning | Confidence |
|---|---|---|
| `+0x04` | local X integer | high discovery |
| `+0x0B` | X page/high (`*256`) | high discovery |
| `+0x08` | floor/depth Y integer | high candidate |
| `+0x0C` | vertical/Z integer byte, modulo 256 | high discovery |
| `+0x11` | Z subpixel/fraction phase candidate | medium-high |
| `+0x05` | unknown/zero in present samples | low |
| `+0x09` | unknown player/form-specific byte; not proven Y fraction | low |
| `+0x0D` | unknown player/form-specific byte; not Z fraction | medium exclusion |
| `+0x9C` | lagged/render X cache | high discovery |
| `+0xA2` | cached integer floor/depth | high discovery |
| `+0xA3` | X page/cache family | high discovery |
| `+0xA4` | not render-Z in current evidence | high exclusion |

## Remaining discriminators

- Controlled depth-only movement is needed to locate any Y page/fraction companion.
- Controlled camera scroll is still needed for world-X vs screen-X transformation; passive 23-object common-mode analysis found no usable scroll episode.
- The exact top/bottom sprite extent still appears likely to require frame/ROM geometry rather than a live Z cache byte.
