# WinKawaks player coordinate layout audit — GEO line

Scope: WinKawaks normalized CPS RAM discovery evidence only. Read-only offline analysis; no WOF-045 or production-shadow changes.

## Input

- `GEO-0004-action-diversity-10s60-20260831-1604Z`
- 600 frames
- P1/P2/P3 full `0xE0` objects
- normalized logical CPS byte order from Collector

## Result

The primary coordinate families at `+0x04`, `+0x08`, and `+0x0C` are better modeled as 16-bit 8.8 components than as ordinary 32-bit 16.16 values.

### X local component `+0x04..05`

Moving P2:

- `U16BE(+0x04)/256`: range about `64..238`, 90 changing frames, median absolute nonzero delta `2 px`, P95 `8 px`.
- `S32BE(+0x04)/65536`: range about `-32768..32256`, median absolute nonzero delta `512`, P95 `2048`.

The 32-bit 16.16 interpretation produces implausible scale/wrap behavior; the U16 8.8 interpretation produces ordinary gameplay-sized motion.

### Floor/depth `+0x08..09`

Static examples in GEO-0004:

- P1 `48.359375`
- P2 `72.515625`
- P3 `96.1796875`

These are naturally represented by `U16BE(+0x08)/256`.

### Z / vertical displacement `+0x0C..0D`

P1 produced a jump-like range about `0.203..30.203` with typical nonzero steps around `2 px` under `U16BE/256`.

P2 reached `0xFFxx` values. This strongly suggests the Z family should next be tested as signed 8.8 (`S16BE/256`), where `0xFFxx` becomes a small negative displacement rather than ~255 px.

## Horizontal world-X model

Current best local discovery model remains:

`worldX ~= page * 256 + localX`

where:

- `localX = U16BE(+0x04..05) / 256`
- page/high complement is carried by the `+0x0A..0x0B` family, with observed page transitions at `+0x0B` across local 0/255 wraps.

The exact screen-X transform still requires the controlled camera-scroll discriminator in `GEO-0005`.

## Guardrail

Historical Browser scripts that read `S32(a+4)/65536` remain only experiment-design clues. This WinKawaks audit does not promote Browser numeric semantics and instead follows the observed normalized raw byte behavior.
