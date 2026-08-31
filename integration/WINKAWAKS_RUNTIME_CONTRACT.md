# WinKawaks Runtime Integration Contract

Status: Integration enabled after bridge M14 PASS.

## Canonical bridge target identity

The WinKawaks bridge contract is `runtime_snapshot_v2-pointer-derived`.

Canonical target identity is:

```text
selectedPlayerLow16 observed at WinKawaks normalized +0x6D
BE1C -> P1 / selector 0
BEFC -> P2 / selector 4
BFDC -> P3 / selector 8
```

Raw WinKawaks `+0x81` is diagnostic/reference only and MUST NOT be exposed as a semantic target selector.

Player validity is split into immutable structure and mutable consistency diagnostics.

## Browser WOF-038 runtime fields that Future Danger rules currently consume

`wof_future_danger_descriptor_family_validator_v38.js` reads these browser/68000 semantics:

```text
enemy type        U16 +0x20
frameEnd          U32 +0x12
next              U32 +0x2C
state99           U8  +0x99
action2A          U8  +0x2A
b2B               U8  +0x2B
body              U16 +0x6E
attack            U16 +0x70
value30           U32 +0x30
timer34           U16 +0x34
payload6C         U16 +0x6C
enemy X/Y         S32 +0x04 / +0x08
target selector   U16 +0x7E
```

The current browser rule engine also derives target X/Y, dx/dy, absDx/absDy and side from the selected player.

## Critical compatibility rule

Do **not** assume the browser field offsets above are numerically identical in the current WinKawaks normalized enemy blob.

Bridge work already proved one concrete mismatch:

```text
browser selected-player low16 reference: +0x6A
WinKawaks proven selected-player low16:   +0x6D

browser target selector reference: +0x7E
WinKawaks old raw/reference byte:   +0x81
```

The `+0x81` value was dynamically disproven as semantic target identity while `+0x6D` was dynamically proven.

Therefore the first Integration milestone is a read-only runtime compatibility probe. It must identify the loaded WinKawaks game/revision where possible and audit the WOF-038 reference fields before any browser Future Danger rule is reused on WinKawaks.

## Integration sequence

```text
I1 runtime compatibility / revision / field-offset audit
-> I2 map the exact WinKawaks semantic fields required by WOF-038
-> I3 emit a Future-Danger-ready WinKawaks snapshot schema
-> I4 feed that schema into the existing WOF rule engine offline
-> only then run live WinKawaks Future Danger validation
```

No WinKawaks RAM writes or automatic key injection are part of this contract.
