# WOF ALPHA RC3 — FRESH INDEPENDENT QA START PROMPT

You own the fresh independent QA stage for the WOF / Warriors of Fate / 三国志II Future Danger Alpha RC3 candidate.

Repository:
- `ouyong520/wof-ai-private`

## Role and write boundary

This is an independent QA/release-audit stage.

You MUST NOT modify `product/alpha/**` to make the candidate pass.
You MUST NOT revive or continue the RC3 implementation stage.
You may write only under:
- `parallel/ALPHAQA_RC3/**`

If you find a product defect, record it precisely and stop at a release verdict. PM will open a new fresh fix stage if required.

## Read first

Read current GitHub state, especially:
- `product/alpha/ALPHA_RC3_REPORT.md`
- all current `product/alpha/**`
- `product/alpha/regression.mjs`
- `product/alpha/regression_result.json`
- `parallel/PM/RC2_REVIEW_BLOCKERS.md`
- `parallel/PM/RUNTIME_IDENTITY_CORRECTION.md`
- `parallel/PM/WORLD_921031_BROWSER_IDENTITY_RESULT.md`
- `parallel/ALPHALIFE/RECOMMENDED_INVALIDATION_POLICY.md`
- prior `parallel/ALPHAQA/**` only as historical/adversarial reference, not as the RC3 contract
- `parallel/PM/ALPHA_FREEZE_SPEC.md`
- `parallel/PM/RELEASE_READINESS.md`

## Authoritative RC3 identity contract

Supported Browser lineage:
- MAME set: `wof`
- `Warriors of Fate (World 921031)`
- canonical half SHA-1:
  - `10b8cb53a4600e3e76f471a3eee8a600e93096fc`
  - `52c2d05279623d93b27856e6b76830796a089eae`
- exact full 1 MiB CPU-logical SHA-256:
  `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

Positive warning eligibility must require exact full-program SHA-256 equality. Reset vectors, dispatch entries, RAM layout and historical `+0x34` dispatch delta may locate/sanity-check only; they must never be a fallback acceptance mechanism.

The stale positive label `wofr1 / World 921002` is not the supported Browser identity for RC3.

## Authoritative RC3 production-rule contract

User-facing active production rules are intentionally only:
1. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`
2. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`

Both are current-state / stateless / hold-only warnings:
- publish only while the exact current predicate matches;
- clear immediately on first current nonmatch;
- no inherited atMs/age/watch/cycle/history/target provenance;
- a same-type replacement may warn only from its own fresh current match.

The following frozen candidates must be quarantined from user-facing production until positive enemy continuity is proven:
- `T16_B4_DANGER_40`
- `T20_5136_B0_TO_B255_1250`
- `D867BA_3232_TM6_220`
- `D8811E_3232_TM6_135`

Do NOT fail RC3 merely because the old RC2 QA expected all six rules to remain production-visible. RC3 intentionally changed that contract for safety.

## Required independent QA

At minimum independently verify:

### Q1 — exact runtime/build identity
- exact supported 921031 digest accepts;
- wrong digest rejects;
- old 921002 / other digest rejects;
- one-byte or one-hex mutation rejects;
- missing/malformed/pending digest rejects;
- hash exception/failure rejects;
- vector + dispatch + layout without exact full digest rejects;
- no path emits a supported signature before exact hash acceptance;
- hash is startup-bound, not a per-poll expensive operation;
- warning state remains disabled/empty while identity is unresolved.

### Q2 — lifecycle / same-type replacement safety
Adversarially prove:
- hidden same-slot same-type replacement cannot inherit a history warning;
- previous occupant plus replacement current sample cannot synthesize an entry/transition warning from F1-F4;
- F1-F4 cannot publish to the user at all in RC3;
- F5/F6 exact current match shows;
- first current nonmatch clears immediately;
- neutral same-type replacement shows no old warning;
- independently matching replacement produces only fresh current evidence;
- multiple slots independently matching F5/F6 remain independent.

### Q3 — preserved RC2 safety fixes
- per-session/random transport binding and foreign-session rejection;
- two producers/two same-origin sessions cannot cross-feed in deterministic tests;
- all simultaneous valid warnings are represented, not only `[0]`;
- recognized legacy `WOFHUD` is disposed safely while required native GL bridge behavior is preserved;
- UNKNOWN/invalid target is silent;
- current target is reread and threat side recomputed;
- stale/error path clears/fails closed;
- no RAM writes;
- no gameplay input injection/autoplay.

### Q4 — frozen/discovery boundary
Confirm absent from user-facing production:
- T18 BODY4728/A4/B2/TM1 as A4704-specific;
- T23 ordered candidates;
- T24/retired variants;
- WinKawaks-local/discovery/provisional rules;
- WOF-052 runtime/research coordinator.

### Q5 — bootstrap/package review
Independently inspect the RC3 normal-user bootstrap candidate:
- user path does not require manually selecting the live `gstyphoon.js` Worker console;
- session binding is established before Worker/page pairing;
- failure to identify/intercept the intended worker fails closed;
- no release path silently falls back to the old two-console RC1 workflow.

## Real Browser boundary

Do all offline/static/adversarial QA possible from GitHub first.

Do NOT ask the owner to do broad gameplay testing.
If offline QA passes, reduce remaining work to one short Browser acceptance checklist covering only things fixtures cannot prove, such as:
- actual document-start bootstrap / target Worker interception under real CSP/options;
- live World 921031 exact SHA-256 acceptance;
- HUD/WebGL rendering and state restoration;
- two-tab isolation / reload pairing if not otherwise demonstrable;
- reasonable runtime overhead.

Do not require the owner to reproduce rare attacks merely to validate quarantined rules. F1-F4 are intentionally silent in RC3.

## Required outputs

Create under `parallel/ALPHAQA_RC3/**`:
- `README.md`
- `AUDIT_STATUS.md`
- `FINDINGS.md`
- `ACCEPTANCE_CHECKLIST.md`
- independent test/harness files as needed
- machine-readable or text test results

Final verdict must be exactly one of:
- `PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`
- `BLOCKED — P0/P1 PRODUCT FIX REQUIRED`
- `BLOCKED — ONE PRECISE REAL-BROWSER PROOF REQUIRED`

For every P0/P1 finding include:
- severity;
- exact file/function/behavior;
- adversarial reproduction;
- why it violates the RC3 contract;
- smallest safe required fix.

## Stop condition

Stop when either:
A. independent offline QA passes and only one bounded real-Browser acceptance remains; or
B. at least one concrete P0/P1 product blocker is proven and documented for a fresh next fix stage.

Do not modify Alpha product code, do not start WOF-052, do not broaden attack research, and do not turn this into Beta feature QA.