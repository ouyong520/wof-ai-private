# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01

Statuses here are management bands, not fake precision.

## Alpha — LATE / START PRODUCTIZATION NOW

### Already strong enough

- core Browser reverse engineering foundation;
- multiple repeated prospective production-shadow warnings;
- target/side evidence for the mature subset;
- read-only research/collector discipline;
- explicit evidence hierarchy and known exclusions;
- enough validated behavior to make a narrow product useful.

### Must close before Alpha release

- [ ] frozen production rule manifest separated from discovery/experimental rules;
- [ ] reliable loader/bootstrap for the declared Browser/game build;
- [ ] runtime identity/version guard;
- [ ] fail-closed automatic reader/warning runtime;
- [ ] live target reread + retarget correctness retained in release artifact;
- [ ] simple non-Console HUD: danger enemy + target + side + supported lead indication;
- [ ] UNKNOWN silence policy implemented;
- [ ] regression audit of every frozen production rule;
- [ ] verify no game RAM writes / no gameplay input injection;
- [ ] short real Browser acceptance run on release candidate.

### Not required for Alpha

- all enemy types;
- all attacks;
- T23 completion;
- stage/scene/boss atlas completion;
- rare branch coverage;
- Safe Path.

## Beta — MID

Must add beyond Alpha:

- [ ] refreshed authoritative coverage denominator;
- [ ] common enemy/common dangerous-attack coverage is high enough for routine play;
- [ ] important ambiguous branches use validated ordered sequence/context;
- [ ] broader scene/room validation;
- [ ] strong P1/P2/P3 target and retarget evidence for common rules;
- [ ] polished HUD and multi-danger prioritization;
- [ ] simple user configuration/install/update flow;
- [ ] acceptable runtime overhead and stability over extended play;
- [ ] automated release regression suite;
- [ ] supported-version messaging and graceful unsupported-version behavior.

## v1 — EARLY-MID

V1 becomes justified when:

- Beta has demonstrated stable ordinary-user operation;
- COVERAGE/SWEEPATLAS provide a defensible common-event denominator;
- production warnings cover a high proportion of that common dangerous-event set;
- remaining unsupported/ambiguous events are intentionally UNKNOWN/silent;
- no P0 risk remains for false promotion, target/retarget, namespace/version identity, read-only isolation or production-rule separation;
- release regression and support matrix are established;
- documentation/packaging no longer assumes research expertise.

PM will set a numeric v1 coverage target only after the denominator is trustworthy. `100% all attacks` is explicitly not the criterion.

## Current release judgment

**Do not release Alpha today as a user build unless the unchecked engineering gates above already exist elsewhere and pass audit. Do start Alpha engineering immediately.**

Research expansion is no longer a reason to defer this work.
