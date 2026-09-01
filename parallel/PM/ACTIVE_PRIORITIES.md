# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC1 QA blocked

## P0 — Alpha RC2 fixes

RC1 is blocked by independent QA. Do not proceed to human Browser acceptance.

Fix exactly the four open QA blockers from `parallel/ALPHAQA/FINDINGS.md`:

1. positive supported-build/runtime identity rather than layout-only recognition;
2. same-type same-slot replacement must not inherit a prior enemy warning;
3. simultaneous warnings must not be silently reduced to the first row;
4. user bootstrap must not require researcher-level manual Worker-console selection.

Implementation bootstrap:
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`

Preserve the six-rule freeze and all RC1 exclusions/safety boundaries.

## P0 — Parallel Browser runtime identity audit

Run a read-only supporting lane from:
- `parallel/PM/ALPHA_RUNTIME_IDENTITY_AUDIT_START_PROMPT.md`

Goal: identify an implementation-ready positive `wofr1 / World 921002` Browser identity mechanism from retained evidence, or reduce the blocker to one minimal real-Browser probe.

This lane does not modify `product/alpha/**`.

## P1 — Fresh independent QA retest after RC2

Do not reuse RC1 QA PASS assumptions. Once RC2 exists, open a fresh QA-retest stage against the current artifact and specifically rerun all four adversarial blockers plus the frozen-rule/read-only/retarget checks.

Only after no P0/P1 remains should owner Browser acceptance begin.

## P2 — MAINLINE WOF-052 after Alpha release gate

WOF-052 ordered T18 discrimination remains valuable research, but it does not block the narrow Alpha because BODY4728 remains excluded.

Use owner Browser time first for Alpha release acceptance once RC2 QA clears.

## PARK — COVERAGE

Refresh complete. Human recap required: NO.

## PARK — SEQMINER

Current retained-corpus ordered information is exhausted; v3 is ready and no recapture is requested. Reopen only on a defined trigger/new evidence.

## Explicit stops

- STOP real Alpha Browser acceptance while QA P0/P1 blockers remain.
- STOP broad BASECAP collection.
- STOP generic EFIELD / RAWMINE / GEO work.
- STOP broad unlabeled sweep collection.
- STOP speculative rule promotion.
- STOP treating WinKawaks offsets as Browser/WASM production evidence.
- STOP extending completed COVERAGE/SEQMINER work merely to keep threads busy.

## Current fastest path

**RC2 fixes + identity audit in parallel -> fresh QA retest -> one Browser acceptance -> Alpha release.**