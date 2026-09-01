# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC4 independent QA PASS / real Browser acceptance authorized

## P0 — One real Browser acceptance

Fresh independent RC4 QA completed with:

`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`

QA independently confirmed:
- RC3 P1 is closed: paired runtime disable/error/diag immediately invalidates old warnings;
- foreign-session diag cannot clear the current session;
- later legal state can recover normally;
- ordinary no-diag 1500 ms stale behavior is unchanged;
- exact `wof / World 921031` full 1 MiB CPU-logical SHA-256 identity remains authoritative;
- exactly two stateless current-level T18 production rules remain active;
- F1-F4 remain quarantined;
- same-type slot replacement cannot inherit warning history;
- session/cross-tab isolation, multi-warning HUD, legacy HUD cleanup, normal-user bootstrap, target/side, UNKNOWN silence, read-only/no-input and GL restoration remain passed.

Authoritative QA artifact:
- `parallel/ALPHAQA_RC4/AUDIT_STATUS.md`

## Browser acceptance tooling — READY

`parallel/ALPHAACCEPT/**` preparation is complete.
The helper remains functionally compatible with RC4 because RC4 preserved the existing product `release/session/schema` transport contract while changing the HUD fail-closed behavior.

Owner operation:
1. enable the normal product userscript and acceptance helper userscript;
2. refresh the real WOF Browser page;
3. wait for the Alpha acceptance panel;
4. click the acceptance button once;
5. return the single final JSON.

A PASS result must be exactly:
`PASS — REAL BROWSER ACCEPTANCE`

Do not declare Alpha released until PM consumes that JSON.

## SUPPORT — READY / NON-BLOCKING

- Runtime Speed Probe Tooling: complete; one paired ~15 s local/Browser measurement remains when convenient.
- Local WinKawaks ROM identity: one read-only local hash remains; retained evidence strongly indicates local World 921002 vs Browser World 921031.
- HUD Anchor Proof Tooling: complete; one bounded Browser projection proof remains for Beta.

## P1 — Alpha release decision after Browser PASS

If real Browser acceptance returns PASS, PM will perform the final Alpha release gate and then resume post-Alpha work, including WOF-052 / ordered T18 discrimination according to roadmap.

## PARK / COMPLETE

- Alpha RC4 implementation — complete / product regression PASS.
- Alpha RC4 independent QA — complete / PASS.
- Browser Acceptance Prep — complete / ready.
- RC3/RC2 and earlier Alpha stages — closed.
- Runtime Identity / Enemy Lifecycle / Bootstrap support audits — consumed.
- COVERAGE / SEQMINER / BASECAP / GEO / EFIELD / RAWMINE / SWEEPATLAS — closed or on-demand.

## Explicit stops

- STOP product changes before Browser acceptance unless the acceptance itself finds a concrete blocker.
- STOP reopening already-passed identity/lifecycle/rule-scope issues without new evidence.
- STOP broad collection / speculative rule promotion.
- STOP treating a Browser acceptance PASS as release declaration until PM records the final release decision.

## Current fastest path

**one real Browser acceptance -> PM release decision -> Alpha release**
