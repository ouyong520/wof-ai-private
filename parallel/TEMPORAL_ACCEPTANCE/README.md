# Alpha V1 P24 — Canonical Temporal Stability / Continuity Acceptance

P24 is a passive, fail-closed acceptance analyzer. It does not produce actor identity or coordinates and it does not modify the maintained HUD/runtime. It consumes already-canonical identity/state evidence and reports temporal continuity, churn, lifecycle boundaries, replay/order defects, and draw-ack causality.

## Evidence contract

Each observation uses `wof-alpha-canonical-temporal-observation-v1` (`temporal_observation.schema.json`) and binds:

- exact `worldSha256`, `authorityKey`, `runtimeEpoch`, and `rendererEpoch`;
- exact `actor` (`P1`/`P2`/`P3`/`enemy-slot-N`) plus integer `generation`;
- local monotonic `sampleSeq` + `observedAt`, and source `frameSeq`;
- explicit `READY` or `SUPPRESSED` plus a suppression reason;
- optional explicit `actorPresence` for disappearance/reappearance evidence;
- optional canonical geometry only when its declared authority is `canonical-render-object-only`;
- optional P18 acknowledgement rows, retaining exact authority, actor/generation, ledger sequence/evidence generation, sample identity, and `visibleProof=NOT_PROVEN`;
- read-only safety (`readOnly=true`, `ramWrites=0`, `inputInjection=false`).

Coordinates/body bounds are retained only as already-canonical evidence. P24 never evaluates distance, speed, nearest objects, row order, screenshot positions, world projection, interpolation, or old cached coordinates to identify an actor or repair continuity. Large legitimate canonical movement therefore does not fail a stream; stale epoch/generation reuse does.

## Deterministic classifier

The analyzer independently tracks every actor and actor/generation stream. A new generation revokes the prior generation. A new runtime/renderer epoch revokes the prior epoch, and continuity is never claimed across that boundary. Returning to a revoked generation/epoch is rejected. Duplicate/out-of-order samples or actor frames are rejected before they can mutate lifecycle state or increase coverage.

A `SUPPRESSED` sample immediately has no canonical geometry authority. P18 acknowledgement rows are accepted only on a current `READY` sample with exact actor/generation/authority and, when supplied, matching transport sequence/canonical sample identity. Replayed ACKs do not increase evidence; ACKs after suppression, generation rollover, or epoch replacement are rejected as stale.

The result vocabulary is `PROVEN_CONTINUOUS`, `OBSERVED_WITH_CHURN`, `SUPPRESSED_SAFELY`, `STALE_OR_MISMATCH`, `INSUFFICIENT_EVIDENCE`, or `UNPROVEN`. Churn is reported (transitions, state-run duration, one-sample pulses, longest READY run and rates) without an invented hard failure threshold.

## Input / output seam

Input can be JSON, JSONL, or a bundle:

```json
{
  "schema": "wof-alpha-canonical-temporal-observation-bundle-v1",
  "observations": [],
  "sourceEvidence": {
    "p16": {},
    "p18Snapshots": []
  }
}
```

`sourceEvidence.p16` and `sourceEvidence.p18Snapshots` are **binding/proof-boundary metadata only**. A final P16 or P18 snapshot cannot manufacture temporal continuity; repeated time-ordered observations are required. This makes the seam compatible with a later P21/P17/P23 passive capture without changing those owners.

Run:

```text
python parallel/TEMPORAL_ACCEPTANCE/temporal_acceptance.py --input <observations.jsonl> [--p16-evidence <snapshot.json>] [--p18-evidence <snapshot.json> ...] [--output-root <dir>]
```

Default output root is `~/Documents/WOF_RESULTS/ALPHA_P24_TEMPORAL_ACCEPTANCE/` and contains deterministic:

- `ALPHA_CANONICAL_TEMPORAL_CONTINUITY_EVIDENCE.json`
- `ALPHA_CANONICAL_TEMPORAL_CONTINUITY_EVIDENCE.md`

P23 may consume these stable paths/schemas later. P24 does not edit P23 or claim that P16/P18 runtime evidence proves visible pixels.

## Proof boundary

Focused fixtures prove the analyzer/format only. This worker does not run real WOF, does not perform Owner visual acceptance, does not promote W3 renderer-source authority, does not infer HIT/DOWN/JUMP/DEATH, and does not move `alpha-live`.
