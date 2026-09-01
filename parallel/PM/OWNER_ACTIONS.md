# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC3 QA blocked on one P1; open fresh RC4 fix

## Current owner action required: YES — thread management only

Fresh independent RC3 QA is complete and found one concrete P1:

`ALPHAQA-RC3-001` — when the paired runtime emits a disable/error diagnostic, the HUD can keep the previous warning visible for up to 1500 ms instead of clearing it immediately.

All other major RC3 release gates audited before the stop condition passed.

## Action O1 — close completed RC3 QA thread

Do not ask QA to edit `product/alpha/**`.
It reached stop condition B with a deterministic product blocker.

## Action O2 — open fresh Alpha RC4 Fix thread

Use:

`parallel/PM/ALPHA_RC4_FIX_START_PROMPT.md`

RC4 is intentionally tiny:
- fix immediate warning invalidation on accepted runtime disable/error diagnostic;
- add regression;
- preserve World 921031 SHA-256 identity;
- preserve two-rule stateless T18 scope and F1-F4 quarantine;
- preserve session isolation, multi-warning HUD, bootstrap, legacy teardown, target/side, UNKNOWN, read-only/no-input.

Do not expand attack research or Beta scope.

## Completed support threads to close/park

### Browser Acceptance Prep

Preparation is complete under `parallel/ALPHAACCEPT/**`.
Do not run final acceptance yet. After a future QA PASS, the prepared user operation is already one refresh + one button + one result JSON.

### HUD Anchor Proof Tooling

Tooling/handoff artifacts are prepared. Human Browser projection proof is Beta-support and does not block Alpha.

### Runtime Speed Probe Tooling

If this tooling thread is still active, let it continue independently. It does not block RC4 or Alpha.
If it has not yet published `parallel/RUNTIMESPEED_PROBE/**`, do not duplicate the thread.

## Optional non-blocking owner probes — not required now

- Local ROM hash command: proves local World 921002 vs Browser World 921031.
- Runtime speed paired measurement: once tooling is ready.
- HUD Anchor Browser projection proof: Beta only.

Do not spend owner time on these before RC4 is running unless convenient.

## Do not do yet

- Do not run final Alpha Browser acceptance.
- Do not revive RC3 implementation or RC3 QA as a fix thread.
- Do not restart WOF-052 as an Alpha blocker.
- Do not perform broad collection.

## Next PM trigger

After RC4 publishes a candidate, PM will close that implementation stage and open a fresh independent RC4 QA stage.
