# WOF Alpha Independent QA

Updated: 2026-09-01
Owner: independent Alpha QA / release audit
Status: **QA BLOCKED**

This lane audits `product/alpha/**` as read-only. QA findings and independent tests live only under `parallel/ALPHAQA/**`.

## Current decision

Alpha RC1 is **not QA PASS**. The current artifact has two P0 and three P1 blockers documented in `FINDINGS.md`:

- `ALPHAQA-001` P0 — runtime/build identity is layout-only and can fail open on a lookalike revision;
- `ALPHAQA-002` P1 — same-type same-slot replacement can inherit a prior enemy warning;
- `ALPHAQA-003` P1 — HUD silently reduces simultaneous warnings to `warnings[0]`;
- `ALPHAQA-004` P1 — supported load path still requires researcher-level live Worker-console selection plus top-page load;
- `ALPHAQA-005` P0 — fixed origin-global `BroadcastChannel('wof-alpha-v1')` is not bound to one page/runtime session and can cross-contaminate warnings between same-origin Alpha sessions/tabs.

Frozen-rule fidelity itself passed QA. No product code is modified by this lane.

## Audit sources

Primary release specification:

- `parallel/PM/ALPHA_FREEZE_SPEC.md`
- `parallel/PM/ALPHA_ENGINEERING_TASKS.md`
- `parallel/PM/RELEASE_READINESS.md`
- `parallel/PM/RISK_REGISTER.md`
- `parallel/PM/PROJECT_DASHBOARD.md`
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`
- `parallel/PM/ALPHA_RUNTIME_IDENTITY_AUDIT_START_PROMPT.md`

Release artifact audited:

- `product/alpha/rules_manifest.json`
- `product/alpha/wof_alpha_core.js`
- `product/alpha/wof_alpha_loader.js`
- `product/alpha/wof_alpha_hud.js`
- `product/alpha/regression.mjs`
- `product/alpha/README.md`
- `product/alpha/ALPHA_RC_REPORT.md`

Browser evidence checked directly:

- `reports/WOF-051_ANALYSIS.md`
- `wof_future_danger_descriptor_family_validator_v38.js`
- `wof_future_danger_cycle_validator_v41r.js`
- `wof_future_danger_cycle_validator_v43r.js`
- `wof_future_danger_cycle_validator_v45r.js`
- `wof_future_danger_cycle_validator_v46r.js`
- `wof_future_danger_cycle_validator_v47r.js`
- `wof_future_danger_cycle_validator_v48r.js`
- `wof_future_danger_cycle_validator_v51r.js`

Supporting lifecycle evidence consulted read-only:

- `parallel/EFIELD/ROUND_002_LIFECYCLE_ACTIVE.md`
- `parallel/EFIELD/ROUND_008_INSTANCE_METADATA.md`

The EFIELD material is used only to prove that same-type replacement is a real lifecycle class. It is **not** used to copy WinKawaks offsets into Browser release code.

## Independent test

Run from repository root:

```text
node parallel/ALPHAQA/independent_qa.mjs
```

The script is intentionally adversarial and is separate from `product/alpha/regression.mjs`. Current suite id is `wof-alpha-independent-qa-v2`; while blockers remain, a non-zero exit is expected.

The v2 harness includes explicit rejection of the exact RC1 fixed-channel/schema-only warning transport in addition to the prior identity, lifecycle, multi-warning, load-path and read-only checks.

## RC2 monitoring state

PM has opened the bounded RC2 product-fix stage and a separate read-only runtime identity audit. At the latest check:

- current `product/alpha/wof_alpha_core.js`, `wof_alpha_loader.js`, and `wof_alpha_hud.js` are still the RC1 blobs;
- `product/alpha/ALPHA_RC2_REPORT.md` does not yet exist;
- `parallel/ALPHAID/README.md` does not yet exist.

Fresh independent QA should restart as soon as RC2/ALPHAID outputs land in GitHub.

## QA stop rule

QA may become PASS only when:

- no P0/P1 finding remains open;
- all mandatory checks in `ACCEPTANCE_CHECKLIST.md` are PASS;
- supported build identity is positively established and lookalikes fail closed;
- warning transport is isolated to the intended page/runtime session;
- the only remaining action is short real-Browser acceptance for rendering/performance/environment integration.

QA does not modify `product/alpha/**`.