# WOF PM Rolling Execution Queue

Updated: 2026-09-01

Authoritative inputs:
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/COMPLETED_WORK_PM_AUDIT_2026-09-01.md`
- `parallel/PM/PRIORITY_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`

## Owner rule

Owner does not read worker summaries or decide PASS/FAIL.

When Owner says `继续`, PM:
1. reads latest GitHub results/claims/commits;
2. independently reviews completed submissions;
3. closes/supersedes/blocks old stages;
4. creates only fresh next stages;
5. re-surfaces any still-needed QUEUED prompt the Owner may have missed;
6. never re-surfaces equivalent CLAIMED/COMPLETE work;
7. ranks by P0 -> P1 -> P2, but uses spare concurrency for stable, non-conflicting P1/P2 work that directly shortens the product path.

`ONE STAGE = ONE FRESH CHAT`

Concurrency is not a KPI, but **idle capacity should be used when there is real non-conflicting mainline work**. Do not leave P1/P2 work idle merely because P0 exists; instead ensure P0 owns the highest-priority write scopes and use remaining slots only for work that will stay useful after those fixes land.

## Current product mainline

`Discovery V2 correctness -> cross-component alignment -> global regression/preflight -> Alpha Safe Transport implementation -> one bounded real Windows/WOF proof -> integrated transport QA -> Browser Acceptance -> Alpha release decision`

Parallel evidence mainline:

`WOF-052L 10-room long capture -> auto analysis -> ordered discriminator -> discovery->prospective handoff -> research-only prospective validation -> broader Beta warning coverage`

Long capture is not authorized until short runtime/admission gates are clean, but all repository-side endurance/replay/analysis preparation should be exhausted first.

## ACTIVE / START NOW — 9 useful slots

### Core blockers — already claimed

| Rank | Priority | State | stageId | Prompt | Primary scope | Why now |
|---:|---|---|---|---|---|---|
| 1 | P0 | CLAIMED | `WOF052L_RECORDER_DISCOVERY_V2_HARDENING_V1` | `WOF052L_RECORDER_DISCOVERY_V2_HARDENING_START_PROMPT.md` | `parallel/WOF052L_RECORDER/**` | closes cross-page shared-Worker evidence ownership P0 plus endpoint/URL/direct-association and Chinese-runtime P1s |
| 2 | P0 | CLAIMED | `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_V1` | `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_START_PROMPT.md` | `parallel/PROSPECTIVE_VALIDATOR/**` | closes shared-Worker evidence P0 and false research PASS from ignored target/type/lifecycle gates |
| 3 | P1 | CLAIMED | `PYLAUNCH_DISCOVERY_V2_HARDENING_V1` | `PYLAUNCH_DISCOVERY_V2_HARDENING_START_PROMPT.md` | `parallel/PYLAUNCH/**` | closes authoritative proof path endpoint/URL/direct-association drift |
| 4 | P1 | CLAIMED | `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_V1` | `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_START_PROMPT.md` | `parallel/LIVE_PROOF_BUNDLE/**` | prevents retained fatal/blocker/stale child success from reaching false PASS |

### Spare concurrency — safe non-conflicting P1/P2 work

| Rank | Priority | State | stageId | Prompt | Primary scope | Why it stays useful |
|---:|---|---|---|---|---|---|
| 5 | P1 | QUEUED | `DISCOVERY_V2_CONFORMANCE_HARNESS_V1` | `DISCOVERY_V2_CONFORMANCE_HARNESS_START_PROMPT.md` | `parallel/DISCOVERY_V2_CONFORMANCE/**` | converts manual cross-component audit into reusable synthetic topology contract tests; does not modify components |
| 6 | P1 | QUEUED | `REGRESSION_ORCH_DISCOVERY_V2_GUARD_V1` | `REGRESSION_ORCH_DISCOVERY_V2_GUARD_START_PROMPT.md` | `parallel/REGRESSION_ORCH/**` | ensures new Discovery V2 safety tests cannot silently fall out of full-repo regression; final HEAD rescan catches parallel changes |
| 7 | P1 | QUEUED | `ALPHA_TRANSPORT_REFERENCE_IMPL_V1` | `ALPHA_TRANSPORT_REFERENCE_IMPLEMENTATION_START_PROMPT.md` | `parallel/ALPHA_TRANSPORT_IMPL/**` | implements frozen Safe Transport contract against existing 67-vector harness now, so later real integration is adapter wiring rather than starting from zero |
| 8 | P1 | QUEUED | `WOF052L_10ROOM_ENDURANCE_SIM_V1` | `WOF052L_10ROOM_ENDURANCE_SIM_START_PROMPT.md` | `parallel/WOF052L_ENDURANCE_SIM/**` | simulates 1h/2h/overnight 10-room orchestration/finalization/failure paths before spending Owner time on real long capture |
| 9 | P2 | QUEUED | `ALPHA_FIXED_HUD_STABILITY_QA_V1` | `ALPHA_FIXED_HUD_STABILITY_QA_START_PROMPT.md` | `parallel/ALPHA_FIXED_HUD_QA/**` | independently verifies fixed in-game HUD is stable/non-drifting Alpha fallback without blocking on head-anchored Beta HUD |

## NEXT GATES — open fresh stages only after prerequisites

| Priority | State | Task | Wait for |
|---|---|---|---|
| P1 | WAITING_GATE | Fresh Discovery V2 cross-component retest | component hardening complete; use new harness/current blobs |
| P1 | WAITING_GATE | Unified Live Proof fresh independent QA | fail-closed fix complete + current component contracts stable |
| P1 | WAITING_GATE | Unified Proof preflight hardening | same `parallel/LIVE_PROOF_BUNDLE/**` write scope as active fail-closed fix, so wait for that thread to finish |
| P1 | WAITING_GATE | Owner one-click unified proof package refresh | preflight/live-proof stack stable; refresh once |
| P1 | WAITING_GATE | Formal Alpha Safe Transport integration into real components/product | reference implementation ready + hardening component interfaces stable |
| P2 | WAITING_GATE | WOF-052L long-capture fresh QA retest | Recorder hardening complete + endurance sim findings consumed |
| P2 | WAITING_GATE | Beta manifest-set fresh QA retest | Prospective hardening complete |
| P2 | WAITING_GATE | WOF-052L handoff fresh QA | Prospective semantics stable |
| P2 | WAITING_GATE | 10-room 1h+ real capture | short unified live proof + fresh long-capture QA PASS |

## Accepted/closed — do not optimize now

- Browser Fleet Discovery V2 repository implementation;
- old Discovery V2 cross-component audit (later fresh retest only);
- Alpha Safe Transport Mock Harness 67/67;
- Alpha Acceptance V2 Prep;
- Beta manifests themselves until Validator fix/retest says otherwise;
- Owner package infrastructure until upstream stabilizes;
- head-anchored HUD research remains Beta/non-blocking; fixed HUD is Alpha fallback.

## Dedup

Every stage implements `STAGE_DEDUP_GUARD.md` and unique atomic claim. If already complete/claimed, worker stops and becomes idle. PM fills that slot from the next highest-value queued item.

## Owner action

`NO` for real WOF/Windows testing.

Owner may open the five queued fresh worker chats above. All are repository-side and should not request live gameplay.