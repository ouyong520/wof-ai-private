# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC4 candidate PASS / fresh independent QA next

## P0 — Fresh independent Alpha RC4 QA

RC4 narrow product-fix stage reached its stop condition.

Authoritative product regression:
- artifact: `wof-alpha-rc4`
- tests: `PASS`
- supported Browser lineage: `wof / Warriors of Fate (World 921031)`
- golden full 1 MiB CPU-logical SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- `runtimeDiagImmediateWarningInvalidation: true`
- ordinary stale behavior preserved
- exactly two current-level T18 production rules
- F1-F4 remain quarantined
- same-type replacement/session/read-only/no-input safety preserved

Fresh QA bootstrap:
- `parallel/PM/ALPHA_RC4_QA_START_PROMPT.md`

RC4 implementation thread should now be closed. QA must not modify `product/alpha/**` and must independently prove closure of `ALPHAQA-RC3-001` plus the already-passed RC3 gates.

## P1 — Browser acceptance preparation COMPLETE

`parallel/ALPHAACCEPT/**` is complete and waiting.
The final owner acceptance has already been reduced to normal game refresh + one acceptance button click + one summary JSON.

Do not run it until fresh RC4 QA returns exactly:
`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`.

## SUPPORT — Runtime Speed Probe Tooling

`parallel/RUNTIMESPEED_PROBE/**` has implemented the local read-only capture, Browser read-only capture, common-heartbeat analyzer, one-shot orchestrator, operator steps and result JSON schema.
This support tooling is non-blocking for Alpha and can now wait for the owner's paired measurement.

## BETA SUPPORT — HUD Anchor Proof Tooling

HUD Anchor proof tooling has produced bounded Browser proof tooling/handoff.
Human projection proof remains non-blocking and can wait until after the Alpha release gate.

## HUMAN-GATED / NON-BLOCKING

- Local WinKawaks ROM identity: one read-only local hash probe remains; retained evidence strongly indicates local World 921002 vs Browser World 921031.
- Runtime simulation speed: tooling is ready for one paired ~15 s local/Browser measurement and automatic JSON verdict.
- HUD Anchor: one bounded Browser projection proof remains.

## P2 — MAINLINE WOF-052 after Alpha release gate

Ordered T18 discrimination remains valuable but is not an Alpha blocker.

## PARK / COMPLETE

- Alpha RC4 implementation — COMPLETE CANDIDATE / product regression PASS; close thread.
- Alpha RC3 independent QA — COMPLETE / one P1 found and routed into RC4; closed.
- Browser Acceptance Prep — COMPLETE / waiting for QA PASS.
- Runtime Speed Probe Tooling — COMPLETE support tooling / human measurement pending.
- HUD Anchor Proof Tooling — COMPLETE tooling / human proof pending.
- RC3/RC2 and earlier implementation stages — closed; do not revive.
- Runtime Identity / Enemy Lifecycle / Bootstrap support audits — consumed.
- COVERAGE / SEQMINER / BASECAP / GEO / EFIELD / RAWMINE / SWEEPATLAS — closed or on-demand.

## Explicit stops

- STOP final Browser acceptance before fresh RC4 QA PASS.
- STOP asking completed RC4 implementation to self-certify.
- STOP reopening passed identity/lifecycle/rule-scope issues without new evidence.
- STOP broad collection / speculative production-rule promotion.

## Current fastest path

**fresh RC4 independent QA -> one-click Browser acceptance -> Alpha release**
