# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC2 parallel repair started

## Current owner action required: NO

Owner reports all four new RC2-stage work threads are open:

1. Alpha RC2 implementation — edits `product/alpha/**`.
2. Runtime Identity audit — read-only support under `parallel/ALPHAID/**`.
3. Enemy Lifecycle / slot-reuse audit — read-only support under `parallel/ALPHALIFE/**`.
4. Normal-user Bootstrap audit — read-only support under `parallel/ALPHABOOT/**`.

Canonical short launcher paths now exist:
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`
- `parallel/PM/RUNTIME_IDENTITY_START_PROMPT.md`
- `parallel/PM/ENEMY_LIFECYCLE_START_PROMPT.md`
- `parallel/PM/ALPHA_BOOTSTRAP_START_PROMPT.md`

## RC1 QA blocker set

RC1 is not releasable. QA currently has six known open P0/P1 findings and RC2 must always reread the latest QA files rather than rely on a stale count:

- ALPHAQA-001 P0 — layout-only runtime/build identity can fail open.
- ALPHAQA-002 P1 — same-type same-slot replacement can inherit an old warning.
- ALPHAQA-003 P1 — HUD silently drops simultaneous warnings after the first row.
- ALPHAQA-004 P1 — normal-user load path requires manual Worker-console selection.
- ALPHAQA-005 P0 — fixed origin-global BroadcastChannel can cross-contaminate warnings between same-origin sessions/tabs.
- ALPHAQA-006 P1 — prior research `WOFHUD` is hidden rather than fully disposed during Alpha takeover.

RC2 bootstrap has been updated so **all current QA OPEN P0/P1 findings** are mandatory, including findings added after the original four-item RC1 audit.

## Human gameplay action — NOT YET

Do not run real Browser Alpha acceptance while any P0/P1 remains.

Wait for:
1. support audits to write implementation-ready results or one exact minimal human probe;
2. RC2 implementation to close all offline-fixable blockers;
3. a fresh independent RC2 QA retest.

Only after fresh QA reports no open P0/P1 should PM request one short real Browser acceptance.

## Closed / parked work

- COVERAGE — complete / PARK; human recap = NO.
- SEQMINER — current retained corpus exhausted / PARK; no recapture requested.
- RC1 QA — its stage output is the blocker list; do not keep extending the old thread.
- Original Alpha RC1 implementation — completed stage; RC2 is a new implementation stage.

## Next PM trigger

No copying between work threads is needed. When the four active threads have written GitHub results, return to PM and say `继续`. PM will read GitHub directly, route support findings into RC2, and decide when a fresh QA-retest thread should start.
