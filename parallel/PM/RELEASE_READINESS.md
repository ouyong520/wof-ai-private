# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01

Statuses here are management bands, not fake precision.

## Alpha — LATE / ENGINEERING FOUNDATION PRESENT / NOT RC

The second PM audit found that Alpha is closer than the initial conservative checklist implied: the repository already has reusable production-shadow/danger-map work and a direct WebGL HUD with reload-safe hook, BroadcastChannel state path, stale/hold behavior and in-game load confirmation.

Those assets reduce implementation work, but they are still historical/research assets until integrated into a bounded release artifact and regression-tested as that artifact.

### Already strong enough

- core Browser reverse engineering foundation;
- multiple repeated prospective production-shadow warnings;
- target/side evidence for the mature subset;
- read-only research/collector discipline;
- explicit evidence hierarchy and known exclusions;
- production-shadow / danger-map runtime history exists;
- direct WebGL HUD implementation exists and has prior reload/load-confirmation hardening;
- enough validated behavior to make a narrow product useful.

### Alpha gate status

| Gate | Status | PM judgment |
|---|---|---|
| frozen production rule manifest | OPEN | `ALPHA_FREEZE_SPEC.md` now defines candidates/exclusions; machine-readable exact manifest still needed |
| reliable loader/bootstrap | PARTIAL | research loading/resume paths exist; one user release load path is not yet release-audited |
| runtime identity/version guard | OPEN/PARTIAL | module/RAM discovery guards exist in research scripts; supported-build positive identity + fail-closed release guard still required |
| fail-closed automatic reader/warning runtime | OPEN | must be separated from research coordinator |
| live target reread + retarget | STRONG RESEARCH / OPEN RELEASE | Browser logic is mature; must be retained and regression-tested in release artifact |
| non-Console HUD | PARTIAL-STRONG | direct WebGL HUD exists; must be wired to frozen release runtime and product semantics |
| UNKNOWN silence policy | OPEN RELEASE | policy defined; implementation audit required |
| frozen-rule regression | OPEN | must test release artifact, not only research coordinator |
| no RAM writes / no input injection | STRONG RESEARCH / OPEN RELEASE | existing evidence is strong; final artifact audit still required |
| real Browser RC acceptance | OPEN | owner action only after RC exists |

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

**Do not release Alpha yet. Do start the bounded PRODUCT/ALPHA implementation workstream now, using existing HUD/runtime assets rather than rebuilding from scratch.**

Research expansion is no longer a reason to defer release engineering.
