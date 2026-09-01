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

The previous depth coverage gap is exactly what canonical B40-P2/B40-P3 were intended to cover. Therefore no new P2/P3 acquisition is justified merely because the old GEO attempts were weak.

## Superseded GEO acquisition attempts

`GEO-0012-p2-same-xy-offsets-12s60-20260901-0054Z` was mechanically healthy but manipulation/attribution-invalid for the P2 question. It is not negative evidence.

`GEO-0013-p2-attribution-depth-long-35s60-20260901-0104Z` is superseded for the current decision by BASECAP B40-P2. It must not be used as a reason to request another P2 capture.

## Canonical B40 offline semantic evaluation

Authoritative acquisition labels remain the BASECAP catalog/task/operator evidence. The following numerical findings come from the existing RAWMINE post-completion BASECAP audit and are consumed read-only by GEO.

### B40-P2

Known P1 geometry offsets measured in the P2 slot across all 960 frames:

- `+0x04`: 0 changes; constant `234`.
- `+0x0B`: 0 changes; constant `0`.
- reconstructed same-offset X therefore has 0 changes in this capture.
- untouched P1 and P3 controls are also static at these offsets.
- `+0x08`: 10 changes; domain `99..112`; 11 distinct values; all 10 deltas negative; small-step ratio `1.0`; player-slot specificity `1.0`.
- `+0xA2`: 11 changes; domain `99..113`; 12 distinct values; player-slot specificity `1.0`.
- `+0x08/+0xA2` same-frame event Jaccard: `0.615385`.
- best exact-value lag for source `+0x08` relative to target `+0xA2` is `-1`, exact-value ratio `0.990615` over 959 comparable frames.

GEO interpretation:

- The P2 depth-family evidence is positive for same-offset `+0x08`: it changes only in the manipulated player slot while untouched player controls remain stable.
- The `+0xA2` relation reproduces the already-established P1 live/cache ordering: `+0xA2` is overwhelmingly explained as a one-frame trailing mirror/cache of `+0x08`, not as the authoritative coordinate.
- However, the canonical B40-P2 raw does **not** contain observable RIGHT/LEFT motion in the known X composite despite the authoritative operator label, and its `+0x08` trajectory is one-directional rather than the expected UP/DOWN bidirectional path.
- Therefore B40-P2 is not sufficient by itself to promote the complete P2 X/Y same-structure claim to CONFIRMED.

Current P2 verdict:

- X same-offset structure: `SUPPORTED` from pre-BASECAP retained evidence, but **not independently replicated by canonical B40-P2**.
- Y `+0x08` same-offset structure: `SUPPORTED_STRONGLY` by canonical B40-P2 specificity and small-step motion.
- `+0xA2`: `MIRROR_CACHE_SUPPORTED`, subordinate to authoritative `+0x08`.
- overall P2 same X/Y structure: `SUPPORTED_NOT_LOCKED`.

### B40-P3

Known P1 geometry offsets measured in the P3 slot across all 960 frames:

- `+0x04`: 0 changes; constant `245`.
- `+0x0B`: 0 changes; constant `0`.
- `+0x08`: 0 changes; constant `69`.
- `+0xA2`: 0 changes; constant `69`.
- all-offset ranking shows no P3-specific dynamic geometry candidate; only the shared `+0x7F` animation/timer-like activity is dynamic.

GEO interpretation:

- The authoritative operator label says P3 was moved RIGHT/LEFT/UP/DOWN, but the retained P3 object record does not show corresponding geometry motion at the known same offsets or at any strong P3-specific alternative offset.
- This is a canonical-capture evidence contradiction / observability gap, not negative proof that P3 uses a different structure.
- Because earlier retained aggregate evidence already showed P3 same-offset X activity (44 reconstructed-X events / 44 `+0x04` events), the B40-P3 static trace does not erase that prior support.
- It does mean the depth replication question remains unresolved from canonical B40-P3 alone.

Current P3 verdict:

- X same-offset structure: `SUPPORTED` from pre-BASECAP retained evidence, but **not independently replicated by canonical B40-P3**.
- Y `+0x08` same-offset structure: `INSUFFICIENT_CANONICAL_OBSERVABILITY`.
- overall P3 same X/Y structure: `SUPPORTED_NOT_LOCKED`.

## Decision / stop line

Both P2 and P3 are **not yet simultaneously locked**, so GEO must **not advance to facing** yet.

The failure mode is not a missing BASECAP scene: B40-P2 and B40-P3 already canonically cover the requested movement protocol and must not be replaced by GEO-0013 or any equivalent re-capture. GEO therefore does not queue or request another human P2/P3 capture.

Next permissible work is offline only:

1. reuse any newer RAWMINE/BASECAP-derived report that can explain why the B40 operator manipulation is not visible in the expected player object records;
2. test whether player-slot identity during B40 can be reconciled from immutable task/result/raw evidence without inferring operator actions from values;
3. search existing retained corpus for independent P3 depth episodes with reliable slot attribution and untouched-player controls;
4. retain `+0x08` as authoritative and `+0xA2` as mirror/cache wherever the live-vs-lag discriminator is present.

No human acquisition is currently justified. Facing remains blocked until both P2 and P3 same-structure/same-offset are locked.
