# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — post completed-wave PM audit

Authoritative operating rules:
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/COMPLETED_WORK_PM_AUDIT_2026-09-01.md`
- `parallel/PM/EXECUTION_QUEUE.md`
- `parallel/PM/OWNER_SHORTHAND_CONVENTIONS.md`

## Product north star

The product target is not “finish more tools”.

Current path is:

`trustworthy real-time danger warning -> broader validated coverage -> safe movement / safe path -> progressively lower damage -> eventual stable 0-damage clear objective`

WOF-052/WOF-052L is core evidence/R&D infrastructure supporting that target, not the final user product by itself.

## P0 — WOF-052L Recorder evidence ownership hardening

Later cross-component audit invalidated the earlier blanket `READY FOR 10-ROOM LONG CAPTURE` claim.

Current P0:
- one exact supported shared Worker can be associated with >1 page and current Recorder logic may effectively select evidence ownership by scan order.

Same fresh stage also closes related P1s in the same write domain:
- endpoint confinement;
- URL-scheme gate drift;
- direct fallback/openerId association drift;
- English-only long-capture runtime status found by independent QA.

Fresh stage:
- `parallel/PM/WOF052L_RECORDER_DISCOVERY_V2_HARDENING_START_PROMPT.md`

**Do not start 1h/2h/overnight capture until this closes and fresh QA retest passes.**

## P0 — Prospective Validator evidence/gate hardening

Local Discovery V2 regression is useful (16/16 PASS) but not sufficient.

Current blockers:
- cross-page shared Worker evidence ownership ambiguity;
- READY manifests declare conservative `minDistinctTargets`, `minObservedTypes`, `requireLifecycleReset`, but current final Validator verdict does not execute them.

Fresh stage:
- `parallel/PM/PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_START_PROMPT.md`

Must remain research-only; no automatic production promotion.

## P1 — PYLAUNCH authoritative Discovery V2 hardening

The old real-Chrome `no gstyphoon worker target` defect was meaningfully addressed and 13/13 local regression passed.

Later cross-component audit still found P1 drift before another Owner proof:
- endpoint host/port confinement;
- existing Worker URL-scheme semantics;
- direct fallback must not use Worker `openerId` as parent authority.

Fresh stage:
- `parallel/PM/PYLAUNCH_DISCOVERY_V2_HARDENING_START_PROMPT.md`

**Owner live proof remains paused.**

## P1 — Unified Windows Live Proof fail-closed fix

Development bundle initially reached repository READY, but fresh independent QA found a real P1:
- retained fatal/blocker can coexist with final PASS;
- stale PASS/admission after child exit can remain authoritative;
- Owner playability Y/N may still be asked after a blocker.

Fresh stage:
- `parallel/PM/UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_START_PROMPT.md`

Until fresh fix + fresh QA pass, no unified Owner run is authorized.

## ACCEPTED / DO NOT OPTIMIZE NOW

### Browser Fleet Discovery V2
Repository-side 15/15 PASS. Fleet remains deliberately `cheap-indicator-only`; exact World identity remains consumer authority. Reopen only for a concrete later live defect.

### Discovery V2 cross-component audit
Audit completed successfully by finding precise P0/P1 ownership. Old audit thread is closed. After fixes, use a fresh retest stage.

### Alpha Safe Transport Mock Harness
67/67 PASS. Keep closed and consume when transport implementation starts.

### Alpha Acceptance V2 Prep
Ready and waiting for actual transport integration. Do not redesign now.

### Beta manifest compilation
Manifest set remains research-only and correctly keeps unresolved T18 branches NOT_READY. Fix Validator gate enforcement first, then fresh QA retest.

### Owner one-click infrastructure
Useful immutable/hash/Windows CI work exists. Do not keep refreshing intermediate packages while core components are changing; refresh once after the live-proof stack stabilizes.

## WAITING GATES — next sequence

After the four current P0/P1 stages:

1. fresh Discovery V2 cross-component retest;
2. Discovery V2 conformance final run / global regression guard refresh;
3. fresh Unified Live Proof QA;
4. decide how much Alpha Safe Transport implementation + mock QA can be completed before any Owner run;
5. final repository preflight + one-click package refresh;
6. only then one bounded real Windows/WOF run if an intrinsically real-runtime fact remains;
7. transport integration QA / bounded Browser acceptance;
8. Alpha release decision;
9. then WOF-052L long capture / broader Beta evidence expansion.

## Owner action

**NO.**

Repository-side code/audit/regression work remains. Owner must not be used as an exploratory debugger.
