# GEO P2/P3 same-structure closure

Updated: 2026-09-01

Scope: WinKawaks local discovery only. Read-only. No Browser production promotion. No RAM writes.

This closure supersedes the provisional `SUPPORTED_NOT_LOCKED` stop line in `P2_P3_STRUCTURE_FRONTIER.md` for the narrow owner question **“P2/P3 是否和 P1 使用同一 player-object structure / same relative geometry offsets?”**. It does **not** claim a fresh direct controlled P3 Y trajectory that the retained corpus does not contain.

## Final phase verdict

- P1 reference: `X = 256*U8(+0x0B)+U8(+0x04)`, `Y_floor_depth = U8(+0x08)` — already CONFIRMED.
- P2 same player-object layout / same relative X/Y offsets — **CONFIRMED**.
- P3 same player-object layout / same relative X/Y offsets — **STRUCTURALLY_CONFIRMED**.
- `+0xA2` remains mirror/cache family, not authoritative Y.
- Direct P3 controlled `+0x08` bidirectional Y trajectory — **NOT OBSERVED / LIMITATION RETAINED**.

The GEO P2/P3 same-structure phase is therefore **CLOSED**. The next permitted GEO phase is `facing`.

## Why same player-object layout is not a guess

Collector/session discovery does not locate three unrelated records and name them P1/P2/P3 heuristically. The live CPS block is defined from:

- `PLAYER_P1 = 0xFFBE1C`
- `PLAYER_STRIDE = 0xE0`
- exactly three consecutive player objects before the enemy pool
- player object indexes `[0,1,2]`

Fresh-session discovery requires the P1/P2/P3 identity triple at exact `0xE0` spacing and validates the same immutable relative offsets on all three objects:

- `+0x20 = 0/1/2`
- `+0x21 = 0x1A/0x1B/0x1C`
- `+0x26 = 0/1/2`
- `+0x62 = 0/2/4`
- `+0x7C = 0/4/8`
- `+0x92 = 0/4/8`

The discovery method is explicitly `immutable-player-structure-v3`; it does not use coordinates, enemy state, cached addresses, target state, or transient player state as discovery gates.

The ROM-side player table independently contains the same three player-object pointers at one common indexed table:

- P1 `0xFFBE1C`
- P2 `0xFFBEFC`
- P3 `0xFFBFDC`

with the shared `0/4/8` player index route. This is independent structural evidence that P1/P2/P3 are instances of one player-object layout, not three separately typed coordinate records.

## Dynamic geometry evidence already available

### P2 X

Independent retained raw has real same-offset X dynamics including page coverage. Example from GEO-0003:

- local `+0x04`: `1 -> 254`
- page `+0x0B`: `2 -> 1`
- reconstructed X: `513 -> 510`

Aggregate cross-slot screen: 187 P2 reconstructed-X events.

### P3 X

Independent retained raw has a real page wrap in EFIELD-003:

- local `+0x04`: `248 -> 0`
- page `+0x0B`: `0 -> 1`
- reconstructed X: `248 -> 256`

This directly establishes the same relative X fields on P3.

### P2 `+0x08` / `+0xA2`

Canonical BASECAP B40-P2 (`BASECAP-B40-P2-xy-16s60-20260901-0600Z`) is VALID, read-only PASS, 960 frames, with P1/P3 untouched by acquisition label. Neutral post-BASECAP analysis finds:

- P2 `+0x08`: 10 changes, small-step ratio 1.0, player specificity 1.0, domain about `99..112`
- P2 `+0xA2`: 11 changes, specificity 1.0, domain about `99..113`
- the live/cache temporal orientation reproduces P1: approximately `A2[t] ~= 08[t-1]`

This is sufficient replication of the same relative depth-family field layout on P2 when combined with P1's already-closed semantic proof.

## P3 evidence limitation and why it does not justify re-capture

Canonical B40-P3 (`BASECAP-B40-P3-xy-16s60-20260901-0601Z`) is VALID acquisition evidence, but its retained P3 block has no usable within-run changes at `+0x04/+0x0B/+0x08/+0xA2`. A full retained-corpus scan also found no independent P3-specific `+0x08` depth episode: only isolated shared/control-contaminated events exist.

Therefore GEO does **not** claim that B40-P3 directly re-proves the Y semantic dynamically.

What is locked is the narrower owner question: P3 is the third `0xE0` instance of the same player-object structure; its X fields at the same offsets are dynamically proven; historical geometry snapshots place the depth/cache family at the same relative `+0x08/+0xA2` locations; and the common immutable structure / common player table independently fixes the record identity and relative layout.

The absence of a direct P3 Y trajectory is recorded as an evidence limitation, not converted into a request to repeat a canonical BASECAP scene. BASECAP v1 already contains the B40-P3 acquisition and the catalog contains no missing base-scene discriminator for this phase.

## Canonical BASECAP sources

### B40-P2

- taskId: `BASECAP-B40-P2-xy-16s60-20260901-0600Z`
- taskBlobSha: `5aa3fbbeb226ee411327ead0177e347841977a78`
- raw: `captures/BASECAP-B40-P2-xy-16s60-20260901-0600Z.jsonl.gz`
- VALID / read-only PASS / 960 frames

### B40-P3

- taskId: `BASECAP-B40-P3-xy-16s60-20260901-0601Z`
- taskBlobSha: `c54ea1e777e4004501bad37cf8f350da8d65f7ea`
- raw: `captures/BASECAP-B40-P3-xy-16s60-20260901-0601Z.jsonl.gz`
- VALID / read-only PASS / 960 frames

## Superseded acquisition path

Historical `GEO-0012` / `GEO-0013` are not used to justify new P2/P3 capture. They are superseded for this owner question by canonical BASECAP plus the offline structural proof above.

## Next phase

Proceed only to:

`facing`

Reuse canonical BASECAP B12/B12R before considering any new acquisition.