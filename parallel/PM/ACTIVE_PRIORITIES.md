# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC2 parallel repair active

## P0 — Alpha RC2 implementation

RC1 is blocked by independent QA. Do not proceed to human Browser acceptance.

The RC2 owner must close **every current OPEN P0/P1** in `parallel/ALPHAQA/FINDINGS.md` / `AUDIT_STATUS.md`, not just the original four findings. Six known blockers currently exist, including cross-session warning provenance and legacy HUD teardown.

Bootstrap:
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`

Only this lane may edit `product/alpha/**`.

## P0 — Positive runtime/build identity audit

Read-only support lane. Canonical launcher:
- `parallel/PM/RUNTIME_IDENTITY_START_PROMPT.md`

Goal: find a real positive `wofr1 / World 921002` Browser identity mechanism or reduce the issue to one minimal precise Browser probe.

## P1 — Enemy lifecycle / slot-reuse audit

Read-only support lane. Canonical launcher:
- `parallel/PM/ENEMY_LIFECYCLE_START_PROMPT.md`

Goal: prevent a watch from enemy episode A being inherited by a same-type replacement in the same slot, using Browser-proven continuity or a conservative fail-closed invalidation policy.

## P1 — Ordinary-user bootstrap audit

Read-only support lane. Canonical launcher:
- `parallel/PM/ALPHA_BOOTSTRAP_START_PROMPT.md`

Goal: remove the requirement for the user to manually locate/switch to the live `gstyphoon.js` Worker console.

## P1 — RC2 must also close release-path isolation defects

Current QA adds two release-path blockers beyond the original four:
- ALPHAQA-005 P0 — isolate same-origin sessions/tabs so a HUD cannot display another runtime's warning.
- ALPHAQA-006 P1 — fully dispose a prior research `WOFHUD` during Alpha takeover while preserving the native safe WebGL bridge.

These are implementation responsibilities of RC2 and require deterministic regression coverage.

## P1 — Fresh independent QA retest after RC2

Once RC2 exists, open a **new** QA-retest stage rather than reviving the RC1 QA thread.

Retest must rerun all latest RC1 adversarial blockers plus frozen-rule fidelity, read-only/no-input, target/retarget/side, UNKNOWN silence, warning lifecycle, session isolation, legacy HUD teardown and user bootstrap checks.

Only after no P0/P1 remains should owner Browser acceptance begin.

## P2 — MAINLINE WOF-052 after Alpha release gate

Ordered T18 discrimination remains valuable but does not block narrow Alpha because BODY4728 is excluded.

## PARK

- COVERAGE — complete; human recap required: NO.
- SEQMINER — current retained-corpus ordered information exhausted; no recapture requested.
- BASECAP/GEO/EFIELD/RAWMINE/SWEEPATLAS — closed or on-demand only.

## Explicit stops

- STOP real Alpha Browser acceptance while QA P0/P1 blockers remain.
- STOP broad collection / generic field research.
- STOP speculative rule promotion.
- STOP treating WinKawaks offsets as Browser/WASM production evidence.
- STOP extending completed old work threads merely to keep thread count high.

## Current fastest path

**RC2 implementation + identity audit + lifecycle audit + bootstrap audit in parallel -> fresh RC2 QA retest -> one Browser acceptance -> Alpha release.**
