# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01 — post completed-wave PM audit

## Alpha — **BLOCKED / REPOSITORY-SIDE DISCOVERY + LIVE-PROOF HARDENING REQUIRED**

The former RC5 room-entry blocker remains closed.

Confirmed retained PASS:
- RC4 product regression;
- fresh RC4 independent QA;
- RC5 product regression;
- owner real-Browser room entry with RC5 enabled;
- fresh independent RC5 room-entry repair QA;
- real Windows Chrome/CDP connection;
- base game remains playable while attached;
- read-only / ramWrites=0 / no gameplay input injection in the prior real proof.

## Important correction to older release status

The old file treated PYLAUNCH Worker discovery as the sole immediate blocker.

That is now outdated.

PYLAUNCH's first Discovery V2 fix made real progress, but later independent/cross-component review found additional repository-side blockers and drift that should be closed **before** asking the Owner for another real run.

## Current gate status

| Gate | Current PM judgment |
|---|---|
| RC5 room-entry safety | PASS / CLOSED |
| Browser Fleet Discovery V2 repository implementation | PASS / CLOSED FOR NOW |
| PYLAUNCH Discovery V2 base fix | LOCAL PASS, **P1 HARDENING REQUIRED** |
| WOF-052L Recorder Discovery V2 | **P0/P1 HARDENING REQUIRED** |
| Prospective Validator Discovery V2 | LOCAL PASS, **P0/P1 HARDENING REQUIRED** |
| Discovery V2 cross-component audit | COMPLETE / useful blockers identified |
| Unified Windows Live Proof bundle | **BLOCKED P1 — fail-closed aggregation** |
| Regression Orchestrator core | READY, later Discovery V2 coverage refresh required |
| Alpha Safe Transport contract | READY |
| Alpha Safe Transport mock harness | READY / 67 of 67 |
| Alpha Acceptance V2 prep | READY / WAITING TRANSPORT |
| Real unified Windows/WOF proof | PAUSED — repository hardening first |
| Alpha Safe Transport implementation | WAITING CURRENT DISCOVERY/LIVE-PROOF REPOSITORY GATES |
| Integrated Browser acceptance | PAUSED |
| Alpha release | BLOCKED |

## Current P0/P1 blockers

### P0 — Recorder cross-page shared-Worker evidence ownership
Evidence admission must never choose page/room ownership by scan order when one exact supported Worker is related to multiple pages.

### P0 — Prospective cross-page shared-Worker evidence ownership
Same principle for prospective evidence admission; ambiguous relations must admit none/censor current evidence safely.

### P1 — Prospective conservative gate enforcement
Final prospective verdict must actually execute manifest-declared target/type/lifecycle gates, not merely document them.

### P1 — PYLAUNCH endpoint/URL/direct-association drift
Close before next authoritative Owner proof.

### P1 — Unified Proof false PASS risk
Fresh QA proved retained fatal/blocker or stale child success can still reach final PASS. Must fail closed before any Owner run.

## Release sequence — optimized to minimize Owner work

1. close the current Recorder / Prospective / PYLAUNCH / Unified Proof repository P0/P1 stages;
2. fresh Discovery V2 cross-component retest;
3. global regression/conformance/preflight refresh against the new blobs;
4. PM decides how much Alpha Safe Transport implementation and mock/independent QA can be completed **before** any real Owner run;
5. refresh the one-click live-proof package once after the stack stabilizes;
6. only if an intrinsically real-runtime fact remains, perform one bounded real Windows/WOF run that proves as many remaining gates as possible;
7. finish integrated transport QA and bounded real Browser warning/HUD acceptance;
8. PM Alpha release decision.

## WOF-052L / Beta / zero-damage direction

The final product goal is not the recorder itself.

After a trustworthy Alpha warning product exists:
- WOF-052L long capture supplies broader natural attack evidence;
- ordered-sequence analysis resolves ambiguous states;
- fresh prospective validation expands reliable warning coverage;
- Beta then moves toward geometry/threat fusion and Safe Path;
- later stages target progressively lower damage and eventually stable 0-damage clear capability.

Do not spend Owner hours on long capture until short runtime/admission gates and fresh QA are clean.

## Safety requirements retained

Must remain true:
- exact supported World identity authority;
- validated production rules only;
- ambiguous/unsupported evidence fails closed;
- session/room/Worker isolation;
- live target/side safety;
- UNKNOWN silent;
- read-only Alpha;
- ramWrites=0;
- no gameplay input injection in warning mode;
- no `window.Worker` replacement/wrap;
- base game fail-open;
- no automatic production promotion from discovery/prospective research.

## Owner action

**NO.**

There are still repository-side P0/P1 fixes that must be completed before another real test is justified.
