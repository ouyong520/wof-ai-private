# WOF Future Danger AI — Alpha Freeze Specification

Updated: 2026-09-01
Status: PM release specification; **not yet a production manifest**

## Purpose

Define the smallest conservative rule/product subset worth turning into the first user Alpha while MAINLINE research continues independently.

This document does not promote any rule by prose. The eventual release implementation must copy exact match semantics from the latest audited Browser production-shadow source and must pass release-artifact regression before a rule becomes `production`.

## Alpha freeze principles

1. Only Browser prospective / repeated production-shadow evidence is eligible.
2. WinKawaks-local discovery is never sufficient.
3. Discovery/experimental rules are physically/logically excluded from the release bundle.
4. If a rule predicts danger but not one unique attack, the UI says danger; it does not invent an attack name.
5. Target is reread live; warning-entry target is never frozen through retarget.
6. UNKNOWN / unsupported branches stay silent.
7. Failure of runtime identity, state read, parser or rule engine disables warnings rather than guessing.
8. Audit horizon is an operational warning horizon, not a claimed causal boundary.

## Initial Alpha freeze candidates

These are **freeze candidates pending release regression**, based on the current WOF-051 audited frontier.

### F1 — T16 B4 imminent danger

Current evidence:
- 98 / 98 strict;
- lead 8.9..21.0 ms;
- A6432=97, A4840=1;
- target/side 98 / 98.

Release semantics:
- warn `IMMINENT DANGER`;
- do **not** label this as A6432-exclusive;
- attack-specific UI field may be omitted/UNKNOWN for this rule.

### F2 — T20 B0->B255 branch -> A5136

Current evidence:
- 5 / 5 strict;
- lead 380.9..639.7 ms;
- target/side audited clean in current production audit.

Release semantics:
- attack-specific warning is eligible if exact audited branch signature is preserved.

### F3 — descriptor D867BA -> A3232

Current evidence:
- 10 / 10 strict;
- lead 99.1..109.4 ms;
- observed across T33/T9;
- P1/P2/P3 targets covered.

Release semantics:
- attack-specific warning eligible;
- descriptor identity and live-target path must be preserved exactly.

### F4 — descriptor D8811E -> A3232

Current evidence:
- 22 / 22 strict;
- lead 98.6..119.2 ms;
- observed across T34/T11.

Release semantics:
- attack-specific warning eligible after release regression.

### F5 — T18 BODY7512/TM4 -> A5440

Current evidence:
- 4 / 4 strict;
- lead 62.3..70.9 ms.

Release semantics:
- eligible only if exact match semantics and target/side regression remain clean in release artifact.

### F6 — T18 BODY7520/TM4 -> A5424

Current evidence:
- 4 / 4 strict;
- lead 69.1..70.0 ms.

Release semantics:
- eligible only if exact match semantics and target/side regression remain clean in release artifact.

## Explicitly excluded from Alpha freeze

### X1 — T18 BODY4728/A4/B2/TM1 as A4704 rule

Excluded because direct prospective validation produced:
- A4704 @ 19.9 ms;
- A4712 @ 100.4 ms.

It is forward-relevant but attack-ambiguous. It cannot enter the attack-specific production manifest unless ordered context later resolves the branch prospectively.

### X2 — T23 ordered candidates

Current T23 sequences are discovery/ordered evidence, not production proof. They remain in Browser validation queue.

### X3 — T24 zero-coverage rules / retired fixed-lag variants

Zero coverage does not validate or falsify them for release. Retired variants remain retired.

### X4 — provisional/one-off/WinKawaks-local candidates

Not eligible for Alpha release.

## Required release modules

Alpha should be structured as four boundaries rather than one research coordinator:

1. `identity/runtime guard`
2. `read-only Browser state reader`
3. `frozen production rule engine`
4. `user HUD/output`

Optional debug/research telemetry must be outside the production rule path and disabled by default.

## Existing engineering assets already worth reusing

Repository history contains:
- production-shadow / danger-map runtime work;
- direct WebGL HUD;
- reload-safe persistent WebGL hook;
- BroadcastChannel state-to-HUD path;
- stale-data/HUD hold behavior;
- in-game load confirmation.

These reduce Alpha implementation risk, but they are not by themselves proof that a release artifact currently satisfies all gates.

## Alpha manifest promotion gate

A freeze candidate becomes `production` only after all are true:

- exact rule implementation traced to current audited Browser source;
- experimental rules absent from release bundle;
- supported runtime/build identity passes;
- unsupported identity fails closed;
- no RAM writes and no gameplay input injection;
- target is live-reread through retarget;
- side is recomputed from current target/geometry;
- UNKNOWN stays silent;
- release-artifact regression reproduces the rule's claimed behavior;
- HUD clears stale/error state safely.

## Scope decision

Alpha may ship with fewer than F1-F6 if one candidate fails release regression. Correct silence is preferred over keeping a marginal rule for feature count.
