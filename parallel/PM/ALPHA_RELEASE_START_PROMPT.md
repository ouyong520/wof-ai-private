# WOF Alpha Release — Start Prompt

Use this stage only after the owner returns a real Browser acceptance result whose top-level verdict is exactly:

`PASS — REAL BROWSER ACCEPTANCE`

Repositories:
- `ouyong520/wof-ai-private`
- `ouyong520/wof-winkawaks-bridge`

## Role

You own the final Alpha release packaging/recording stage. This is not a research stage and not a product redesign stage.

## Read first

- `product/alpha/ALPHA_RC4_REPORT.md`
- `product/alpha/regression_result.json`
- `parallel/ALPHAQA_RC4/FINDINGS.md`
- `parallel/ALPHAQA_RC4/AUDIT_STATUS.md`
- `parallel/ALPHAQA_RC4/RESULT.json`
- `parallel/ALPHAACCEPT/**`
- latest `parallel/PM/RELEASE_READINESS.md`
- owner-provided Browser acceptance JSON recorded by PM or otherwise supplied to this stage

## Required gate

Do not proceed unless all are true:

1. RC4 product regression = PASS.
2. RC4 independent QA verdict = `PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`.
3. Owner real Browser acceptance verdict = `PASS — REAL BROWSER ACCEPTANCE`.
4. No newer P0/P1 blocker exists on GitHub.

If any gate is missing or fails, stop and report the exact blocker. Do not modify product code to manufacture a release.

## Release contract to preserve

- supported Browser build: `wof / Warriors of Fate (World 921031)`;
- exact full 1 MiB CPU-logical SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- exactly two active stateless/current-level T18 warning rules;
- F1-F4 remain quarantined;
- BODY4728/A4704-specific prediction excluded;
- T23/T24/WOF-052/Beta/discovery/local-only rules excluded;
- same-type slot reuse cannot inherit old warning state;
- accepted runtime disable/error/diag immediately invalidates old warning authority;
- session/cross-tab isolation preserved;
- simultaneous warnings preserved;
- legacy HUD cleanup preserved;
- normal-user document-start bootstrap preserved;
- live target/side recomputation and UNKNOWN silence preserved;
- read-only, `ramWrites=0`, no gameplay input injection/autoplay;
- fixed in-game HUD is acceptable for Alpha; player-anchored HUD remains Beta work.

## Allowed work

Final release-stage changes should be limited to release metadata, user-facing Alpha instructions, version/release notes, final manifests/reports, and any strictly necessary version-label consistency updates that do not change warning semantics.

Do not expand attack research, production rule scope, gameplay automation, HUD Beta features, or local-ROM assumptions.

## Required outputs

Produce a concise final Alpha release record under `product/alpha/**` and/or the existing release documentation location, containing:

- release identifier;
- exact supported build/hash;
- active production rule inventory;
- explicit exclusions;
- product regression evidence;
- independent RC4 QA evidence;
- real Browser acceptance evidence;
- install/start instructions for an ordinary user;
- known Alpha limitations;
- rollback/fail-closed note;
- clear statement whether Alpha is RELEASED or BLOCKED.

Run the existing product regression again if release-stage metadata/version-label edits touch `product/alpha/**`.

## Stop condition

Stop with one of exactly two outcomes:

- `ALPHA RELEASED` — all three gates pass and final release artifacts are committed;
- `ALPHA RELEASE BLOCKED` — name the exact missing/failed gate.

Do not start Beta or WOF-052 inside this stage.
