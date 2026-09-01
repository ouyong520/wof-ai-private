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
7. leaves slots idle rather than manufacture non-mainline work.

`ONE STAGE = ONE FRESH CHAT`

## Current product mainline

`Discovery V2 correctness -> cross-component alignment -> global regression/preflight -> as much Alpha Safe Transport implementation/mock QA as safely possible -> one bounded real Windows/WOF proof -> integrated transport QA -> Browser Acceptance -> Alpha release decision`

Parallel evidence mainline:

`WOF-052L 10-room long capture -> auto analysis -> ordered discriminator -> discovery->prospective handoff -> research-only prospective validation`

Long capture is not authorized until short runtime/admission gates are clean.

## START NOW — only highest-priority work

These four primary write scopes are disjoint and directly close current P0/P1 mainline blockers.

| Rank | Priority | State | stageId | Prompt | Primary scope | Why now |
|---:|---|---|---|---|---|---|
| 1 | P0 | QUEUED | `WOF052L_RECORDER_DISCOVERY_V2_HARDENING_V1` | `WOF052L_RECORDER_DISCOVERY_V2_HARDENING_START_PROMPT.md` | `parallel/WOF052L_RECORDER/**` | closes cross-page shared-Worker evidence ownership P0 plus endpoint/URL/direct-association and Chinese-runtime P1s; prerequisite for non-waste 10-room capture |
| 2 | P0 | QUEUED | `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_V1` | `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_START_PROMPT.md` | `parallel/PROSPECTIVE_VALIDATOR/**` | closes shared-Worker evidence P0 and false research PASS from ignored target/type/lifecycle gates |
| 3 | P1 | QUEUED | `PYLAUNCH_DISCOVERY_V2_HARDENING_V1` | `PYLAUNCH_DISCOVERY_V2_HARDENING_START_PROMPT.md` | `parallel/PYLAUNCH/**` | authoritative proof path still has endpoint/URL/direct-association drift; fix before any Owner rerun |
| 4 | P1 | QUEUED | `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_V1` | `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_START_PROMPT.md` | `parallel/LIVE_PROOF_BUNDLE/**` | fresh QA proved current aggregator can falsely PASS with retained fatal/blocker; must close before live proof |

## WAITING_GATE — do not consume workers yet

These are legitimate next steps but should wait so their results are not immediately stale.

| Priority | State | Task | Wait for |
|---|---|---|---|
| P1 | WAITING_GATE | Fresh Discovery V2 cross-component retest | Recorder + Prospective + PYLAUNCH hardening complete |
| P1 | WAITING_GATE | Discovery V2 conformance final run | component hardening blobs stable |
| P1 | WAITING_GATE | Regression Orchestrator Discovery V2 guard refresh | new component safety tests landed |
| P1 | WAITING_GATE | Unified Live Proof fresh independent QA | fail-closed fix complete + component contracts stable |
| P1 | WAITING_GATE | Unified Proof preflight hardening | fresh Unified QA passes and component blockers closed |
| P1 | WAITING_GATE | Owner one-click unified proof package refresh | preflight/live-proof stack stable; refresh once, not every intermediate commit |
| P1/P2 | WAITING_GATE | Decide/start Alpha Safe Transport implementation | Discovery/Unified repository gates green; PM should maximize mock/implementation work before Owner proof |
| P2 | WAITING_GATE | WOF-052L long-capture fresh QA retest | Recorder hardening complete |
| P2 | WAITING_GATE | Beta manifest-set fresh QA retest | Prospective gate enforcement complete |
| P2 | WAITING_GATE | WOF-052L handoff fresh QA | Prospective semantics stable |
| P2 | WAITING_GATE | 10-room 1h+ real capture | short unified live proof + fresh long-capture QA PASS |

## Accepted/closed — do not optimize now

- Browser Fleet Discovery V2 repository implementation;
- Discovery V2 cross-component audit (old audit thread closed; later use fresh retest);
- Alpha Safe Transport Mock Harness 67/67;
- Alpha Acceptance V2 Prep;
- Beta manifests themselves until Validator fix/retest says otherwise;
- Owner package infrastructure until upstream stabilizes.

## Dedup

Every new stage must implement `STAGE_DEDUP_GUARD.md` and a unique atomic claim. If already complete/claimed, worker stops and becomes idle; PM later fills the slot only if a higher-value queued task exists.

## Owner action

`NO`

Repository-side P0/P1 work remains. Do not use Owner as an exploratory debugger.
