# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC3 independent QA blocked on one P1; RC4 next

## P0 — Alpha RC4 narrow fail-closed fix

Fresh independent RC3 QA completed and returned:
- overall: `BLOCKED / P1`
- human Browser acceptance: `NOT READY`
- product files changed by QA: `0`

Single blocker:
- `ALPHAQA-RC3-001` — after a paired runtime disable/error diagnostic, the HUD can retain the previous warning for up to `STALE_MS = 1500` ms because diagnostic handling does not immediately invalidate `lastMsg` / `lastRx`.

Fresh fix bootstrap:
- `parallel/PM/ALPHA_RC4_FIX_START_PROMPT.md`

RC4 must only close this fail-closed warning-clearing defect and preserve the already-passed RC3 contract.
Only the fresh RC4 product-fix owner may modify `product/alpha/**` in this stage.

## Passed RC3 areas — do not reopen without new evidence

Independent QA already passed:
- exact `wof / World 921031` full 1 MiB CPU-logical SHA-256 identity gate;
- no sparse identity fallback;
- exactly two stateless current-level T18 production rules;
- F1-F4 quarantined / cannot user-alert;
- same-type slot reuse / hidden replacement safety;
- session/cross-tab isolation;
- simultaneous warning HUD;
- legacy HUD disposal;
- document-start normal-user bootstrap;
- live target / side recomputation;
- UNKNOWN target silence;
- read-only / no-input;
- GL restoration.

## P1 — Fresh independent RC4 QA after RC4 candidate

Do not reuse the completed RC3 QA thread as product engineering.
After RC4 fixes the single P1, open a fresh independent QA stage that reruns the blocker regression plus the preserved RC3 gates.

Only after QA returns:
`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`
may owner Browser acceptance begin.

## P1 — Browser acceptance preparation COMPLETE

`parallel/ALPHAACCEPT/**` reached its stop condition.
Final owner acceptance is already reduced to:
- normal game refresh;
- one acceptance button click;
- automatic auxiliary same-origin tab/reload/close;
- one summary JSON.

Do not run it while RC4/QA is pending.

## SUPPORT — Runtime Speed Probe Tooling

`parallel/RUNTIMESPEED_PROBE/**` may continue independently if that tooling thread is active.
Goal remains one local command + one Browser loader + automatic analyzer/result JSON.
This does not block Alpha.

## BETA SUPPORT — HUD Anchor Proof Tooling

HUD Anchor proof tooling has produced bounded Browser proof artifacts/handoff.
Do not implement Beta HUD inside Alpha.
Human Browser projection proof can be scheduled after the Alpha gate unless convenient earlier.

## HUMAN-GATED / NON-BLOCKING

- Local WinKawaks ROM identity: one read-only local ROM hash command remains; strong retained evidence indicates local World 921002 vs Browser World 921031.
- Runtime simulation speed: one paired 15 s measurement remains after tooling is ready.
- HUD Anchor: one bounded Browser projection proof remains.

## P2 — MAINLINE WOF-052 after Alpha release gate

Ordered T18 discrimination remains valuable but is still not an Alpha blocker.

## PARK / COMPLETE

- Alpha RC3 implementation — complete candidate; closed.
- Alpha RC3 independent QA — complete / BLOCKED on one P1; close thread.
- Browser Acceptance Prep — complete; wait for QA PASS.
- Runtime Speed audit — complete support verdict.
- HUD Anchor audit — complete support handoff.
- RC2 and earlier Alpha stages — closed; do not revive.
- Runtime Identity / Enemy Lifecycle / Bootstrap support audits — consumed.
- COVERAGE / SEQMINER / BASECAP / GEO / EFIELD / RAWMINE / SWEEPATLAS — closed or on-demand.

## Explicit stops

- STOP final Browser acceptance before fresh RC4 QA PASS.
- STOP asking completed RC3 QA to modify product code.
- STOP reopening already-passed identity/lifecycle/rule-scope issues without new evidence.
- STOP broad collection / speculative rule promotion.

## Current fastest path

**RC4 one-defect fix -> fresh RC4 independent QA -> one-click Browser acceptance -> Alpha release**
