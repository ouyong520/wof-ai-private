# WOF Alpha RC4 — Fresh Independent QA Start Prompt

You own a fresh independent QA stage for the WOF / Warriors of Fate / 三国志II Alpha RC4 candidate.

Repository:
- `ouyong520/wof-ai-private`

## Stage boundary

This is QA, not product development.

Do NOT modify `product/alpha/**`.
Do NOT fix defects from inside QA.
Do NOT extend attack research, WOF-052, Beta HUD Anchor, coverage, or local-ROM work.

Write only under:
- `parallel/ALPHAQA_RC4/**`

## Read first

Read current GitHub state, especially:
- `product/alpha/ALPHA_RC3_REPORT.md`
- latest RC4 product commits/report/regression result
- `parallel/ALPHAQA_RC3/FINDINGS.md`
- `parallel/ALPHAQA_RC3/AUDIT_STATUS.md`
- `parallel/PM/ALPHA_RC4_FIX_START_PROMPT.md`
- Browser identity evidence for `wof / World 921031`

Authoritative Browser identity remains:
- `wof / Warriors of Fate (World 921031)`
- full 1 MiB CPU-logical SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

## Primary RC4 regression gate

Independently prove closure of `ALPHAQA-RC3-001`:

1. a valid current warning is visible/authoritative;
2. the paired current-session runtime emits a disable/error/diag;
3. the old warning becomes non-authoritative immediately, not after the ordinary 1500 ms stale timeout;
4. HUD warning count is immediately zero / diagnostic-or-silent state wins;
5. a foreign-session diag must NOT clear the valid current session warning;
6. a later valid paired state may become authoritative again;
7. ordinary no-diag stale behavior remains unchanged.

Do not accept a source-only string check as the only proof. Use an independent adversarial harness/state-machine reproduction matching the actual message precedence.

## Mandatory preserved RC3 gates

Because RC4 was supposed to be a one-defect patch, verify it did not regress:

- exact World 921031 full SHA-256 positive identity;
- pending/missing/malformed/mismatch/error identity fail-closed;
- no sparse vector/dispatch fallback enabling warnings;
- exactly two production T18 current-level rules;
- F1-F4 remain quarantined and cannot user-alert;
- BODY4728/A4704-specific rule remains excluded;
- no T23/T24/WOF-052/local/discovery promotion;
- same-type same-slot replacement cannot inherit old warning/history;
- first F5/F6 current nonmatch clears immediately;
- random per-page session/cross-tab isolation;
- simultaneous warning aggregation;
- legacy HUD disposal;
- normal-user document-start bootstrap contract;
- live target reread / side recomputation;
- UNKNOWN/invalid target silence;
- read-only game RAM / zero input injection;
- WebGL state restoration.

Do not use the obsolete RC2 requirement that all six frozen candidates be production-visible.

## Required outputs

Create:
- `parallel/ALPHAQA_RC4/FINDINGS.md`
- `parallel/ALPHAQA_RC4/AUDIT_STATUS.md`
- an independent adversarial harness if useful
- a machine-readable result JSON

Final verdict must be exactly one of:
- `PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`
- `BLOCKED — P0`
- `BLOCKED — P1`

If blocked, identify one or more concrete deterministic product defects and stop. Do not modify product code.

## Browser boundary

Do not perform the final human Browser acceptance from this QA lane. Browser acceptance is already prepared under `parallel/ALPHAACCEPT/**` and becomes owner-runnable only after this fresh QA returns PASS.

## Stop condition

Stop when RC4 is independently certified for the one bounded real Browser acceptance, or when a concrete P0/P1 is proven.