# WOF Future Danger AI — Dependency Map

Updated: 2026-09-01

## Core product flow

```text
Reverse engineering foundation
        ↓
Browser state/target/descriptor observation
        ↓
retrospective / same-cycle discovery
        ↓
ordered-sequence discovery when single state is ambiguous
        ↓
prospective Browser validation
        ↓
multi-room / cross-target validation as appropriate
        ↓
production-shadow audit
        ↓
PM production freeze
        ↓
runtime + loader + HUD
        ↓
Alpha → Beta → v1
```

## Local coverage flow

```text
BASECAP retained raw ─┐
EFIELD semantics ─────┼→ RAWMINE reusable analysis
GEO geometry ─────────┘
        ↓
SWEEPATLAS / COVERAGE accounting
        ↓
identify real coverage gaps / high-value types
        ↓
minimal targeted recap only if existing data cannot close them
```

## Sequence flow

```text
Browser ambiguity (e.g. T18 single state)
        +
WinKawaks ordered executor structure
        ↓
SEQMINER ranked ordered candidates
        ↓
MAINLINE Browser prospective validator
        ↓
production-shadow only after repeated forward proof
```

## Current concrete P0 dependency

```text
WOF-051 T18 BODY4728 anchor
  → A4704 OR A4712 prospectively
        ↓
WOF-052 ordered context discovery
        ↓
shortest stable post-anchor discriminator
        ↓
new prospective validator
        ↓
repeat / target-side audit
        ↓
possible production promotion
```

## Coverage-to-recapture dependency

```text
SWEEPATLAS labels / authoritative scene data
        ↓
COVERAGE normalized type + scene + attack joins
        ↓
set-cover calculation
        ↓
ONLY THEN targeted human recap if residual gap exists
```

A missing label does not skip directly to physical collection.

## Productization dependency

Alpha does **not** depend on broad coverage expansion. It depends on the already validated subset plus:

```text
production freeze
+ loader/runtime guard
+ rule isolation
+ fail-closed warning engine
+ target/retarget correctness
+ HUD
+ regression / acceptance run
```

Beta/v1 breadth depends on refreshed COVERAGE and additional validated rules.
