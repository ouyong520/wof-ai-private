# WOF AI × WinKawaks Integration Frontier

Updated: 2026-08-31

## Status

```text
Integration enabled = true
Bridge M1-M14 = closed
Current Integration milestone = I1 runtime compatibility / revision / field-offset audit
```

The Browser/MAME Future Danger research frontier remains independently at `WOF-038` and is not replaced by this track.

## Proven bridge contract entering Integration

```text
runtime_snapshot_v2-pointer-derived
selectedPlayerLow16 @ WinKawaks normalized +0x6D = canonical target identity
BE1C -> P1 / selector0
BEFC -> P2 / selector4
BFDC -> P3 / selector8
raw +0x81 = diagnostic/reference only, semantic=false
```

Player immutable structure is separated from mutable consistency diagnostics.

## Why I1 is required before reusing WOF-038 rules

The current WOF-038 browser rule engine consumes exact 68000/browser field semantics including:

```text
U16 +0x20 type
U32 +0x12 frameEnd
U32 +0x2C next
U8  +0x99 state99
U8  +0x2A action2A
U8  +0x2B b2B
U16 +0x6E body
U16 +0x70 attack
U32 +0x30 value30
U16 +0x34 timer34
U16 +0x6C payload6C
S32 +0x04/+0x08 X/Y
U16 +0x7E target selector
```

Those numeric offsets are not yet proven equivalent in the current WinKawaks runtime representation. A concrete target-layout mismatch is already known (`browser +0x6A` reference vs proven WinKawaks `+0x6D`; raw `+0x81` is not semantic).

Therefore no Browser Future Danger rule is allowed to run against WinKawaks by blindly copying offsets.

## I1 probe

Bridge code:

```text
ouyong520/wof-winkawaks-bridge
bridge/i1_runtime_compatibility_probe.py
commit = c21d360ee439eed75dbd46cff1b2da4da02d044b
blob = 301fb3af328bc13169777c69b1c4cf8cf1dcb1bd
```

Output:

```text
results/i1_runtime_compatibility_latest.json
```

I1 is read-only. It records WinKawaks window titles where available, performs fresh CPS RAM discovery, audits the exact WOF-038 reference offsets on active enemy objects, and searches narrow neighborhoods for candidate semantic offsets. It preserves `+0x6D` as canonical target identity and `+0x81` as non-semantic raw reference.

## Next

```text
I1 result -> WEB maps exact WinKawaks semantic fields
I2 -> prove field map required by WOF-038
I3 -> emit Future-Danger-ready WinKawaks snapshot
I4 -> feed snapshot into WOF rule engine offline
```

No RAM writes or automatic input injection are part of this Integration track yet.
