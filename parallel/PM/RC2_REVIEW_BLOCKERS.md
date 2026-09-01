# WOF Alpha RC2 — PM Review Blockers

Updated: 2026-09-01
Status: **RC2 NOT READY FOR FRESH BROWSER QA**

## PM judgment

The RC2 implementation closed several RC1 defects, but two release-critical issues remain after comparing the implementation against the support audits and the owner's new real-Browser evidence.

Do not proceed to final Browser acceptance with the current RC2.

## Blocker R2-1 — P0 — RC2 ROM fingerprint can accept the wrong revision and label it `wofr1 / World 921002`

Current RC2 identity implementation in `product/alpha/wof_alpha_core.js` / loader accepts:

- expected reset vectors;
- the five historical dispatch entries at `0x25DC` with any uniform delta up to `0x1000`;
- RAM/self-index layout.

On success it emits:

```text
wofr1-world-921002-browser-rom-v2
```

This conflicts with `parallel/ALPHAID/RECOMMENDED_GUARD.md`, which explicitly rejected sparse vectors/dispatch anchors as final build identity and recommended exact full 1 MiB program content identity.

More importantly, the owner's current real-Browser ALPHAID probe produced an exact canonical `wof / World 921031` half-ROM SHA-1 match while also reporting the historical live dispatch delta `+52 / +0x34`. Historical Browser commit `4e6f32865302d2ed390f129b5c66123fdf5f04d0` explicitly accepted that same live `+0x34` delta.

Therefore the RC2 sparse guard is demonstrably capable of treating the actual 921031 Browser lineage as the old assumed 921002 label. This is a P0 provenance/identity defect.

Required fix:

1. use full 1 MiB CPU-logical SHA-256 exact equality as the authoritative positive build gate;
2. bind the golden digest only after exact canonical `wof / World 921031` half-ROM SHA-1 match;
3. correct product labels/support matrix from stale `wofr1 / World 921002` to the cryptographically observed `wof / World 921031` lineage unless later evidence explicitly adds 921002 as a separate supported build;
4. no sparse-vector/dispatch fallback may enable warnings;
5. wrong/missing/pending hash must fail closed.

PM evidence: `parallel/PM/RUNTIME_IDENTITY_CORRECTION.md`.

## Blocker R2-2 — P1 — RC2 lifecycle logic still assumes hidden same-type continuity in cases the audit says are UNKNOWN

`parallel/ALPHALIFE/RECOMMENDED_INVALIDATION_POLICY.md` established:

```text
same slot + same type => continuity UNKNOWN
UNKNOWN must be treated like BROKEN for history-derived user warnings
```

It recommended quarantining the four history/edge-derived frozen rules until a positive Browser instance/continuity mechanism exists.

Current RC2 instead keeps history watches while the exact zero-attack base remains observable. It also processes:

```text
p same type + p.attack==0 + s.attack!=0
=> resolveSlot(slot,s)
```

before zero-state drift invalidation.

And entry/transition rule matching still evaluates `previous` and `current` snapshots without any positively proven episode continuity token.

This leaves at least two unsafe classes:

1. enemy A arms a watch; hidden same-type replacement B appears directly ACTIVE/nonzero before any null/type-change/nonmatching-zero sample; old A watch can resolve against B;
2. previous snapshot belongs to enemy A and current snapshot belongs to same-type enemy B; a history/entry/transition predicate can be manufactured across the hidden replacement because `p` and `s` are treated as one episode.

Required fix for the narrow Alpha:

- follow the ALPHALIFE conservative policy exactly;
- without a positive Browser continuity token, do not publish history-derived warnings that combine previous/current across samples;
- quarantine F1–F4 history/edge rules from user-facing production for this release if necessary;
- F5/F6 T18 current-level rules may remain only as hold-only current-state warnings: show iff the exact current predicate matches, clear on the first nonmatch, and do not preserve inherited age/watch state;
- add adversarial tests for direct same-type replacement into ACTIVE and cross-episode false entry/transition.

Correct silence is preferred over preserving six-rule feature count.

## What RC2 did successfully

The following RC2 work remains useful and should be preserved unless new QA disproves it:

- session-bound transport / cross-tab isolation;
- multi-threat HUD aggregation;
- legacy research HUD disposal;
- one-step user bootstrap candidate;
- read-only/no-input constraints;
- UNKNOWN silence and live target/side logic.

## Stage decision

Current RC2 implementation stage has reached its stop point but its candidate is rejected by PM review.

Next implementation stage must be a **fresh Alpha RC3 / identity+lifecycle correction thread**, not a revival of the completed RC2 implementation chat.

RC3 should start only after, or may prepare while waiting for, the one remaining owner read-only 921031 full SHA-256 probe. Final RC3 identity cannot be completed until that digest exists.
