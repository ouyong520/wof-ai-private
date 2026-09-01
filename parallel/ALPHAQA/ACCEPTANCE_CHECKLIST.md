# WOF Alpha Acceptance Checklist

Updated: 2026-09-01
Artifact: `wof-alpha-rc1`
Overall: **BLOCKED**

Legend: PASS / FAIL / PENDING-BROWSER / N/A

## A. Frozen production rules

- [x] PASS — release core contains only six frozen candidates.
- [x] PASS — T16 exact predicate preserved.
- [x] PASS — T16 UI semantics are danger-only, not A6432-exclusive.
- [x] PASS — T20 exact B0->B255 transition preserved.
- [x] PASS — D867BA exact descriptor preserved and not incorrectly type-constrained.
- [x] PASS — D8811E exact descriptor preserved and not incorrectly type-constrained.
- [x] PASS — T18 BODY7512/TM4 cycle-level predicate preserved.
- [x] PASS — T18 BODY7520/TM4 cycle-level predicate preserved.
- [x] PASS — T18 BODY4728/A4/B2/TM1 is not shipped as A4704-specific.
- [x] PASS — T23/T24/discovery/WinKawaks-local rules absent from production path.

## B. Runtime identity / namespace safety

- [ ] FAIL P0 — supported build is not positively distinguished from a layout-compatible unknown revision (`ALPHAQA-001`).
- [x] PASS — missing module fails closed.
- [x] PASS — missing/out-of-range RAM base fails closed.
- [x] PASS — wrong P1/P2/P3 self-index layout fails closed.
- [ ] FAIL P0 — add and pass a negative lookalike-revision regression after the build guard is fixed.
- [x] PASS — Browser/WinKawaks offsets are not dynamically guessed or mixed in the release reader.
- [ ] FAIL P0 — HUD/runtime transport is not bound to one page/runtime session; fixed `BroadcastChannel('wof-alpha-v1')` can accept foreign same-origin state (`ALPHAQA-005`).
- [ ] FAIL P0 — add deterministic foreign-session rejection coverage for state and diagnostic messages.

## C. Read-only / gameplay interference

- [x] PASS static — no game RAM assignment found.
- [x] PASS static — no heap-alias `.set()` write found.
- [x] PASS static — no keyboard/gameplay input injection found.
- [x] PASS static — worker exception stops warning runtime and clears engine state.
- [x] PASS static — HUD wraps changed WebGL state in snapshot/restore/finally.
- [ ] PENDING-BROWSER — verify HUD does not visibly corrupt game rendering.
- [ ] PENDING-BROWSER — verify HUD draw/upload overhead is acceptable during real gameplay.
- [ ] PENDING-BROWSER — verify repeated install/reload does not damage the emulator GL path.

## D. Target / retarget / side

- [x] PASS — target selector is live `enemy+0x7E`.
- [x] PASS — only selector 0/4/8 resolves to P1/P2/P3.
- [x] PASS — unknown selector is silent.
- [x] PASS — invalid target geometry is silent.
- [x] PASS — warning target is recomputed from the current sample.
- [x] PASS — threat side is recomputed from current enemy/target X.
- [x] PASS — synthetic P1 -> P3 retarget updates warning target and side.
- [ ] FAIL P1 — same-type replacement can make a stale watch follow a new enemy (`ALPHAQA-002`).
- [ ] FAIL P0 — foreign same-origin runtime state can supply a different session's target/side to the local HUD (`ALPHAQA-005`).
- [ ] PENDING-BROWSER — repeat real P1/P2/P3 retarget smoke test after lifecycle/session fixes.

## E. Warning lifecycle

- [x] PASS — duplicate suppression exists per slot/rule/cycle.
- [x] PASS — warning expires after operational horizon.
- [x] PASS — attack transition resolves slot watches.
- [x] PASS — slot disappearance clears watches.
- [x] PASS — type change clears watches.
- [x] PASS — prior worker runtime is stopped/cleared before reinstall in the same Worker context.
- [x] PASS — HUD ignores stale state after 500 ms.
- [ ] FAIL P1 — same-type slot replacement is not safely invalidated (`ALPHAQA-002`).
- [ ] FAIL P1 — HUD silently drops warning rows after the first simultaneous threat (`ALPHAQA-003`).
- [ ] FAIL P0 — fixed origin-global warning channel is not isolated per Alpha page/runtime session (`ALPHAQA-005`).
- [ ] PENDING-BROWSER — scene-transition smoke test after lifecycle fix.

## F. Regression independence

- [x] PASS — QA did not accept product regression as sole proof.
- [x] PASS — direct Browser source predicates were compared separately.
- [x] PASS — independent adversarial harness exists at `parallel/ALPHAQA/independent_qa.mjs`.
- [ ] FAIL expected — independent harness must become clean after P0/P1 fixes.
- [x] PASS — QA explicitly treats the product 143-count replay as synthetic aggregate reconstruction, not retained raw Browser replay.
- [ ] FAIL expected — RC2/fresh QA must add a deterministic two-session/foreign-message rejection test for `ALPHAQA-005`.

## G. Packaging / user path

- [x] PASS — repository/raw artifact is publicly fetchable; no private GitHub token is required for the documented raw URL.
- [x] PASS — one loader expression is documented.
- [ ] FAIL P1 — the user must manually choose the live `gstyphoon.js` Worker console and then separately load the top-page HUD (`ALPHAQA-004`).
- [ ] FAIL P0 — bootstrap/transport does not establish a unique page/runtime pairing (`ALPHAQA-005`).
- [ ] PENDING-BROWSER — verify final supported load path under actual page CSP/network conditions.
- [ ] PENDING-BROWSER — verify user-visible load confirmation and disabled diagnostic behavior.

## H. Final QA gate

QA PASS requires all of the following:

- [ ] zero open P0 findings;
- [ ] zero open P1 findings;
- [ ] independent QA harness passes;
- [ ] supported build positive identity passes;
- [ ] unsupported/unknown build negative identity fails closed;
- [ ] same-type replacement/scene lifecycle is safe;
- [ ] simultaneous threats are not silently hidden;
- [ ] two same-origin Alpha sessions cannot cross-contaminate warning/diagnostic state;
- [ ] normal-user load path is acceptable;
- [ ] short real-Browser HUD/retarget/reload acceptance passes.

Current decision: **DO NOT SHIP AS QA-PASSED ALPHA**.