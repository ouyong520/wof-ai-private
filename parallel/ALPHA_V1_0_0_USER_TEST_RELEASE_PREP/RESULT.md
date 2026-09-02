# RESULT — Alpha V1.0.0 User-Test Release Prep

Stage: `ALPHA_V1_0_0_USER_TEST_RELEASE_PREP_V1`

Status: **PASS — ALPHA V1.0.0 USER-TEST RELEASE PREP READY — PLAYER-FACING TEST EXPERIENCE PREPARED / FINAL RELEASE GATES STILL REQUIRED**

Release state: **NOT RELEASED**

Owner action: **NO**

Browser/WOF launched by this stage: **NO**

## Canonical dedup v2

This stage acquired the exclusive canonical claim for:

- dedupKey: `alpha.v1.0.0.user-test-release-prep`
- canonical path: `parallel/PM/DEDUP_CLAIMS/alpha.v1.0.0.user-test-release-prep.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/ALPHA_V1_0_0_USER_TEST_RELEASE_PREP_V1.json`

The canonical file was created with create-only semantics as the first mutation, re-read from current `main`, and its schema/key/mode/stage/prompt/state plus the worker's exact private claim token were verified before substantive release-prep work began. The stage claim was then created and later re-read with the same ownership token.

## Player-facing preparation delivered

Created a dedicated release-prep lane:

`parallel/ALPHA_V1_0_0_USER_TEST_RELEASE_PREP/`

### 1. `README.md` — Chinese-first first-test guide

A normal tester is told to use exactly one obvious player entry once the final package is released:

`WOF_一键工具.cmd`

The guide intentionally does not require understanding Recorder, PYLAUNCH, Transport, HUDANCHOR, DevTools, JavaScript injection, memory addresses or other project internals.

It explains the three visible V1.0.0 expectations:

- player-head danger reminder on the correct P1/P2/P3;
- enemy-head current target label `1P / 2P / 3P`;
- fixed HUD fallback / hiding when anchored positioning is not trustworthy.

It explicitly distinguishes correct fail-closed degradation from unacceptable behavior: persistent drift, wrong-player binding, wrong enemy/target, stale retarget labels or old screen coordinates are bugs, not acceptable cosmetic error.

The first-test flow is bounded to roughly 3–5 minutes and covers normal gameplay only:

- rapid left/right movement;
- depth/lane movement;
- jump ascent/apex/descent/landing;
- rapid advance with camera/stage scrolling;
- visible enemy labels and natural retarget when available;
- one resize/fullscreen transition where supported.

### 2. `BUG反馈模板.md` — minimal player-observable feedback

The template asks only for:

- what happened;
- what the player expected;
- approximate gameplay scene;
- whether the issue was drift / wrong player / wrong target / stale retarget / disappearance / resize offset / other;
- approximate enemy/scene description;
- whether it reproduces;
- optional screenshot or short video.

It explicitly does not ask a normal tester to collect memory addresses, Console/DevTools information, Recorder/PYLAUNCH/Transport internals or developer logs by default.

### 3. `RELEASE_NOTES_V1.0.0.md` — user-view release notes

The release notes describe V1.0.0 by player-visible value rather than internal commits. They cover:

- correct live player-head danger placement when authority is trustworthy;
- enemy-head `1P / 2P / 3P` target visibility;
- prompt retarget replacement;
- movement / jump / scroll / resize non-drift expectations;
- fail-closed fallback;
- read-only/no-input nature of the current warning product.

Known limitations are explicit:

- not universal attack coverage;
- silence is not a claim that every situation is safe;
- no movement-route guidance yet;
- no automatic movement/attack/evade input;
- no 0-damage or clear guarantee;
- uncertain anchoring may intentionally hide/fall back rather than draw a guessed coordinate.

The document also preserves version discipline: later V1.0.1/V1.0.2 releases are tied to user-visible improvements, not internal refactor/QA/tooling completion alone.

### 4. `FINALIZATION_CHECKLIST.md` — downstream release-finalization guard

A short internal checklist records what must still happen after upstream gates stabilize:

- all current P0/P1 release gates PASS;
- bounded real Browser/WOF acceptance PASS;
- real dynamic non-drift proof for both player-head warnings and enemy-head labels;
- retarget, movement/jump/scroll and resize/fullscreen validated live;
- fail-closed hiding/fixed-HUD behavior verified;
- Owner OneClick package regenerated from the final stable snapshot and then revalidated;
- player-facing docs included in the final delivery surface;
- only then may `NOT RELEASED` be changed to an actual player-test release state.

## Current release-gate boundary

This stage deliberately does **not** certify Alpha V1.0.0 for release.

Repository evidence already establishes substantial implementation/QA progress, but current product policy still requires bounded real Browser/WOF dynamic proof before release. In particular, repository/synthetic tests are not a substitute for visually proving that player-head danger reminders and enemy-head `1P / 2P / 3P` labels remain attached to the correct live objects during fast movement, depth movement, jump, whole-screen/camera scroll, retarget and resize/fullscreen.

During this stage, the strict player-head `warningSampleAt` implementation fix completed and a fresh QA V2 prompt was subsequently added on `main`. This release-prep stage does not self-certify that downstream QA, nor does it consume a not-yet-observed result as PASS.

The long-endurance release lane also continued advancing during this stage; the latest observed commit was still a checkpoint rather than a final genuine >=5h PASS. That upstream gate remains outside this stage.

The currently committed Owner OneClick package manifest remains an older immutable snapshot. Per the start prompt, this stage did **not** refresh or freeze a new final manifest while upstream product/tooling gates are still moving. A downstream release-finalization gate must regenerate the package from the eventual stable release snapshot.

Therefore the only correct release state at this stop is:

**NOT RELEASED**

## Scope compliance

Writes by this stage were limited to:

- `parallel/ALPHA_V1_0_0_USER_TEST_RELEASE_PREP/**`;
- the canonical dedup claim;
- the stage claim.

This stage did not modify:

- `product/alpha/**` behavior;
- danger rules or production danger thresholds;
- `target7E` / target semantics;
- Safe Transport authority;
- projection constants/profile activation;
- game input, enemy AI or RAM;
- the current Owner OneClick package manifest.

No Browser/WOF process was launched by this stage.

## Final verdict

**PASS — ALPHA V1.0.0 USER-TEST RELEASE PREP READY — PLAYER-FACING TEST EXPERIENCE PREPARED / FINAL RELEASE GATES STILL REQUIRED**

V1.0.0 release state remains **NOT RELEASED**.
