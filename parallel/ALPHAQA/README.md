# WOF Alpha Independent QA

Updated: 2026-09-01
Owner: independent Alpha QA / release audit
Status: **QA BLOCKED**

This lane audits `product/alpha/**` as read-only. QA findings and independent tests live only under `parallel/ALPHAQA/**`.

## Current decision

Alpha RC1 is **not QA PASS**. The current artifact has one P0 and multiple P1 blockers documented in `FINDINGS.md`.

The strongest blocker is runtime identity: `validateIdentityProbe()` returns a positive `wofr1-world-921002-browser-layout-v1` signature from layout-only inputs that contain no actual game/build/revision identity. This violates the Alpha fail-closed build gate.

## Audit sources

Primary release specification:

- `parallel/PM/ALPHA_FREEZE_SPEC.md`
- `parallel/PM/ALPHA_ENGINEERING_TASKS.md`
- `parallel/PM/RELEASE_READINESS.md`
- `parallel/PM/RISK_REGISTER.md`
- `parallel/PM/PROJECT_DASHBOARD.md`

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

The script is intentionally adversarial and is separate from `product/alpha/regression.mjs`. While blockers remain, a non-zero exit is expected.

## QA stop rule

QA may become PASS only when:

- no P0/P1 finding remains open;
- all mandatory checks in `ACCEPTANCE_CHECKLIST.md` are PASS;
- the only remaining action is short real-Browser acceptance for rendering/performance/environment integration.

QA does not modify `product/alpha/**`.