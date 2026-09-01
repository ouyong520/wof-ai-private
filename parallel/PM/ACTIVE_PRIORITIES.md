# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC1 QA blocked / RC2 parallel repair

## P0 — Alpha RC2 implementation

RC1 is blocked by independent QA. Do not proceed to human Browser acceptance.

The RC2 owner must close all four open findings from `parallel/ALPHAQA/FINDINGS.md` without widening the six-rule freeze.

Bootstrap:
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`

## P0 — Positive runtime/build identity audit

Read-only support lane:
- `parallel/PM/ALPHA_RUNTIME_IDENTITY_AUDIT_START_PROMPT.md`

Goal: find a real positive `wofr1 / World 921002` Browser identity mechanism or reduce the issue to one minimal Browser probe.

## P1 — Enemy lifecycle / slot-reuse audit

Read-only support lane:
- `parallel/PM/ALPHA_LIFECYCLE_AUDIT_START_PROMPT.md`

Goal: prevent a watch from enemy episode A being inherited by a same-type replacement in the same slot, using Browser-proven continuity or a conservative fail-closed invalidation policy.

## P1 — Ordinary-user bootstrap audit

Read-only support lane:
- `parallel/PM/ALPHA_BOOTSTRAP_AUDIT_START_PROMPT.md`

Goal: remove the requirement for the user to manually locate/switch to the live `gstyphoon.js` Worker console.

## P1 — Fresh independent QA retest after RC2

Once RC2 exists, open a new QA-retest stage. It must rerun all four RC1 adversarial blockers plus frozen-rule fidelity, read-only, retarget/side, UNKNOWN silence and warning lifecycle checks.

Only after no P0/P1 remains should owner Browser acceptance begin.

## P2 — MAINLINE WOF-052 after Alpha release gate

Ordered T18 discrimination remains valuable but does not block the narrow Alpha because BODY4728 is excluded.

## PARK — COVERAGE

Refresh complete. Human recap required: NO.

## PARK — SEQMINER

Current retained-corpus ordered information exhausted; v3 ready and no recapture requested.

## Explicit stops

- STOP real Alpha Browser acceptance while QA P0/P1 blockers remain.
- STOP broad BASECAP / EFIELD / RAWMINE / GEO collection/research.
- STOP broad unlabeled sweep collection.
- STOP speculative rule promotion.
- STOP treating WinKawaks offsets as Browser/WASM production evidence.
- STOP extending completed COVERAGE/SEQMINER/RC1-QA stages merely to keep threads busy.
- Only the RC2 implementation owner may edit `product/alpha/**` during this stage.

## Current fastest path

**RC2 implementation + identity audit + lifecycle audit + bootstrap audit in parallel -> fresh QA retest -> one Browser acceptance -> Alpha release.**