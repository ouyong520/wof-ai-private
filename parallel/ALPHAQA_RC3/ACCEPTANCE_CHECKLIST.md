# WOF Alpha RC3 — Independent Acceptance Checklist

Updated: 2026-09-01
Current result: **BLOCKED — P1 ALPHAQA-RC3-001**

## A. Identity — World 921031

- [x] accepted Browser identity is `wof / Warriors of Fate (World 921031)`
- [x] golden full CPU-logical SHA-256 is `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- [x] runtime hashes exactly 1 MiB normalized CPU-logical bytes
- [x] hash equality is mandatory in the positive gate
- [x] vectors/dispatch/layout cannot accept by themselves
- [x] pending hash fails closed
- [x] missing/malformed hash fails closed
- [x] mismatched hash fails closed
- [x] hash error/timeout fails closed
- [x] unsupported/old build cannot pass unless it is byte-identical to the golden digest
- [x] identity signature is produced only after exact digest acceptance

## B. Enemy lifecycle / slot reuse

- [x] production engine has no watch/history map
- [x] same slot + same type cannot establish history continuity
- [x] matching T18 -> neutral same-type replacement clears immediately
- [x] old episode history cannot create a new warning
- [x] direct same-type ACTIVE nonmatch cannot inherit an old warning
- [x] a new same-type replacement that itself exactly matches T18 is allowed only as fresh current evidence

## C. Production rule scope

- [x] exactly two rules are evaluated in production
- [x] T18 BODY7512/TM4 current-level rule is production
- [x] T18 BODY7520/TM4 current-level rule is production
- [x] F1 T16 candidate is quarantined
- [x] F2 T20 transition candidate is quarantined
- [x] F3 D867BA candidate is quarantined
- [x] F4 D8811E candidate is quarantined
- [x] BODY4728/A4704 excluded
- [x] T23 excluded
- [x] T24 excluded
- [x] WOF-052 excluded
- [x] Beta/provisional/local candidates excluded

## D. Warning publication and clearing

- [x] T18 warning uses current sample only
- [x] first current nonmatch removes T18 warning
- [x] invalid/UNKNOWN target is silent
- [x] simultaneous warnings are all represented by HUD model
- [x] ordinary disconnected/stale state stops being fresh after `STALE_MS`
- [ ] **runtime `diag` immediately invalidates every prior warning** — FAIL / P1
- [ ] exception path is user-visible fail-closed with zero stale warning interval — FAIL / P1

## E. Session / bootstrap

- [x] userscript is `@run-at document-start`
- [x] per-page 128-bit random session created before Worker interception
- [x] channel includes session
- [x] Worker and page share the same bootstrap config
- [x] messages require exact schema + session equality
- [x] current RC3 path does not require old two-console RC1 loading
- [ ] intended live Worker interception verified in Browser — deferred because P1 already blocks release
- [ ] reload/cross-tab live isolation verified in Browser — deferred because P1 already blocks release

## F. HUD / cleanup

- [x] legacy `WOFHUD.dispose()` exists in current historical canvas HUD
- [x] legacy dispose removes callback/listener/channel/resources
- [x] persistent GL bridge is preserved for safe takeover
- [x] Alpha HUD refuses takeover if legacy HUD cannot be disposed
- [x] HUD model does not drop warnings after index 0
- [ ] runtime diag beats/invalidates fresh warning — FAIL / P1

## G. Target / side / UNKNOWN

- [x] target selector is reread each poll
- [x] target X is current
- [x] threat side is current/recomputed
- [x] selector outside 0/4/8 is silent
- [x] invalid geometry is silent
- [ ] error diagnostic clears prior warning immediately — FAIL / P1

## H. Read-only / no-input / GL safety

- [x] no detector RAM writes found
- [x] no input injection/autoplay path found
- [x] runtime self-reports read-only / zero writes / no input injection
- [x] HUD draw/upload use GL snapshot/restore in `finally`
- [ ] exception path leaves no user-visible stale warning — FAIL / P1

## Release gate

- [ ] Offline independent QA PASS
- [ ] Eligible for one bounded owner Browser acceptance

Blocked by `ALPHAQA-RC3-001`.
