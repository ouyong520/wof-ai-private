# WOF PRODUCT / ALPHA RC4 FAIL-CLOSED FIX — START PROMPT

You own one extremely narrow WOF Alpha product-fix stage after fresh independent RC3 QA blocked the candidate on exactly one P1.

Repository:
- `ouyong520/wof-ai-private`

Read first:
- `parallel/ALPHAQA_RC3/FINDINGS.md`
- `parallel/ALPHAQA_RC3/AUDIT_STATUS.md`
- `parallel/ALPHAQA_RC3/RESULT.json` if present
- `product/alpha/ALPHA_RC3_REPORT.md`
- current `product/alpha/wof_alpha_hud.js`
- current `product/alpha/wof_alpha_loader.js`
- current `product/alpha/regression.mjs`

## Role

This is a fresh PRODUCT FIX stage. It supersedes the completed RC3 implementation thread.

You may modify `product/alpha/**` only as necessary to close the single blocker below.
Do not modify `parallel/ALPHAQA_RC3/**` findings or tests to make them pass.

## Only blocker — ALPHAQA-RC3-001 P1

Current failure:

- a valid warning state can be displayed;
- Worker runtime then emits a `diag` / disabled/error message;
- page HUD retains the previous `lastMsg` / `lastRx`;
- stale warning may remain user-visible for up to `STALE_MS = 1500` ms even though the detector has already disabled itself.

Required invariant:

> Any paired/current Alpha runtime diagnostic that represents disable/error/fail-closed state must immediately invalidate all prior user warning authority.

The user must not see a prior warning after the runtime has explicitly disabled itself.

Acceptable implementation directions include, but are not limited to:
- clearing `lastMsg` and warning freshness immediately on accepted `diag`;
- or making current disable diagnostics take precedence over all prior state.

Choose the smallest robust implementation.

## Required regressions

Add deterministic coverage for at least:

1. valid warning state -> runtime disable/error diag -> warning count becomes zero immediately;
2. valid warning state -> diag -> HUD chooses disabled/diagnostic/silent rendering immediately, not until stale timeout;
3. foreign-session diag is still ignored;
4. a later fresh valid state after a recoverable/new paired runtime session behaves according to the existing pairing/session contract and does not resurrect stale state;
5. ordinary state staleness behavior remains unchanged where no explicit diag occurred.

## Preserve all RC3 passes

Do NOT reopen or weaken these already-passed areas:

- exact `wof / World 921031` full 1 MiB CPU-logical SHA-256 identity gate;
- no sparse vector/dispatch fallback;
- only two active current-level T18 production rules;
- F1-F4 quarantined / cannot user-alert;
- no same-type slot/history inheritance;
- current nonmatch clears T18 immediately;
- per-session/cross-tab isolation;
- simultaneous multi-warning HUD;
- legacy `WOFHUD.dispose()` cleanup;
- document-start normal-user bootstrap;
- live target reread / side recompute;
- UNKNOWN invalid target silence;
- no game RAM writes;
- no gameplay input injection/autoplay;
- BODY4728 A4704-specific remains excluded;
- no T23/T24/WOF-052/Beta feature promotion.

Do not expand rule coverage or attack research in RC4.

## Required outputs

Update/create under `product/alpha/**` as needed:
- minimal implementation fix;
- regression coverage;
- updated regression result;
- `ALPHA_RC4_REPORT.md` describing exactly the one fix and preserved RC3 contract.

## Stop condition

Stop only when:

A. RC4 candidate exists, product regression passes, and ALPHAQA-RC3-001 is concretely addressed, ready for a fresh independent RC4 QA stage; or

B. an unexpected blocker prevents the invariant from being implemented safely, documented precisely without guessing.

Do not run final Browser acceptance in this thread. Do not modify QA evidence. Do not start WOF-052, Beta HUD work, timing tuning, local ROM research, or broad collection.