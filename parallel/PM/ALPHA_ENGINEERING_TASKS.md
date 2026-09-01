# WOF Future Danger AI — Alpha Engineering Tasks

Updated: 2026-09-01
Status: ACTIVE PRODUCT WORKSTREAM

## Management decision

Do not add another **research** lane.

Do create one bounded **PRODUCT / ALPHA implementation workstream** because MAINLINE must remain focused on Browser prospective research and because release code must be isolated from research coordinators.

This is not scope expansion. It is the productization track already required by the project roadmap.

## Inputs

Product work consumes read-only:

- `WOF_AI_CURRENT_FRONTIER.md`
- `WOF_AI_MASTER_PROGRESS.md`
- latest Browser production-shadow/coordinator sources
- `parallel/PM/ALPHA_FREEZE_SPEC.md`
- `parallel/PM/RELEASE_READINESS.md`
- `parallel/PM/RISK_REGISTER.md`
- existing `wof_canvas_hud.js`
- existing production danger-map / HUD bridge assets

Product work must not reinterpret research evidence or promote new candidates.

## Output boundary

Recommended implementation ownership:

`product/**` or another clearly dedicated release directory chosen by the implementation owner.

Do not overwrite:
- `parallel/BASECAP/**`
- `parallel/GEO/**`
- `parallel/EFIELD/**`
- `parallel/RAWMINE/**`
- `parallel/SWEEPATLAS/**`
- `parallel/SEQMINER/**`
- `parallel/COVERAGE/**`
- WOF-0xx research coordinators except for read-only reference.

PM remains under `parallel/PM/**`.

## P0 tasks

### A1 — Inventory reusable user-facing assets

Audit current HEAD for:
- WebGL HUD implementation;
- HUD data bridge/BroadcastChannel producer;
- production danger-map shadow;
- loader/bootstrap helpers;
- runtime/WASM identity discovery;
- stale/error clear behavior.

Output a short reuse matrix: `reuse as-is / adapt / research-only / retire`.

### A2 — Create frozen production rule manifest

Build a machine-readable manifest from `ALPHA_FREEZE_SPEC.md` candidates, but preserve exact match semantics from the latest audited Browser source.

Rules start as `freeze-candidate`, never auto-promote.

Manifest fields should include at minimum:
- rule id;
- status;
- Browser type in canonical decimal + raw hex notation;
- exact predicate source/version;
- warning class;
- attack-specific vs danger-only;
- validated lead evidence;
- target policy;
- side policy;
- evidence reference;
- unsupported/unknown behavior.

Exclude T18 BODY4728 attack-specific rule and all other explicitly excluded candidates.

### A3 — Separate release runtime from research coordinator

Implement a small release runtime with these modules:

1. runtime identity guard;
2. read-only state reader;
3. frozen rule engine;
4. warning state publisher;
5. HUD consumer.

Research miners, large JSON reports, candidate discovery and experiment arms must not be in the production execution path.

### A4 — Fail-closed identity/version guard

Warnings must stay disabled unless the declared supported game/runtime identity is positively recognized.

Unknown/missing module, RAM base, field identity or unsupported revision => no warning + concise diagnostic.

Never fall back to guessed offsets.

### A5 — Live target/retarget rule

Release runtime must:
- use the Browser-proven target selector path;
- reread target while warning is active;
- recompute side against current target;
- never freeze warning-entry target through a retarget.

### A6 — HUD integration

Reuse the existing direct WebGL HUD where safe.

User default view should show only useful product information:
- danger / attack where actually attack-specific;
- target P1/P2/P3;
- left/right;
- timing class or approximate lead where validated.

Debug fields are optional and off by default.

SAFE/UNKNOWN state should be visually silent after load confirmation.

## P1 tasks

### A7 — Release regression harness

For each frozen rule verify:
- signal count;
- evaluable cycles;
- hard miss count in claimed coverage;
- actual active attack distribution;
- target/retarget correctness;
- side correctness;
- stale warning cleanup.

The harness must test the release artifact logic, not only research coordinator logic.

### A8 — Read-only / interference audit

Prove:
- zero game RAM writes;
- no automatic input injection;
- no accidental hook damage on reload;
- HUD state restoration does not corrupt game WebGL state;
- exceptions do not stop or modify gameplay.

### A9 — Minimal packaging

Provide one supported load path for Alpha.

Do not optimize installation UX prematurely; reliable and documented is enough for Alpha.

### A10 — Release candidate report

Produce a single Alpha RC report with:
- exact artifact/version;
- included production rules;
- excluded/UNKNOWN classes;
- supported runtime/build;
- regression results;
- known limitations;
- owner acceptance steps.

## Stop condition

The Alpha engineering workstream is complete when:

- a user-facing release candidate exists;
- it contains only frozen validated rules;
- all release-blocking gates in PM `RELEASE_READINESS.md` are either passed or explicitly failed;
- the only remaining Alpha action is a short real-Browser owner acceptance run.

It must not turn into a new discovery/reverse-engineering lane.
