# WOF PM Completed-Work Audit — 2026-09-01

Status: **PM REVIEW COMPLETE — WORKER SELF-DECLARED PASS/READY IS NOT AUTHORITATIVE**

This audit follows `parallel/PM/PM_CORE_OPERATING_CHARTER.md`.

The Owner reported that the current worker wave had finished. PM therefore reviewed the recent durable GitHub results as a group rather than asking the Owner to remember which exact chat produced which result.

## Executive judgment

Do **not** continue optimizing every completed lane.

The shortest path to a real-user Alpha is now dominated by four repository-side issues:

1. WOF-052L Recorder Discovery V2 evidence association/admission hardening;
2. Prospective Validator Discovery V2 evidence association + conservative gate enforcement hardening;
3. PYLAUNCH Discovery V2 endpoint/URL/direct-association hardening before the next real proof;
4. Unified Windows Live Proof fail-closed aggregation fix.

Everything else below is either accepted and should be left alone, or should wait until those four are closed.

---

## Audit classifications

### 1. PYLAUNCH Discovery V2 fresh fix

Worker result:
- `parallel/PYLAUNCH/RESULT.md`
- self-verdict: `FIX READY — 只剩一次新的真人 Windows 一键 Proof`
- 13/13 local regression PASS.

PM review:
- the core old `Target.getTargets + gstyphoon URL` blocker was meaningfully addressed;
- however later `parallel/DISCOVERY_V2_AUDIT/RESULT.md` found remaining P1 drift in endpoint confinement, URL-scheme admission, and direct fallback association/openerId semantics.

Classification:

`NEEDS_FRESH_FIX — P1 BEFORE OWNER PROOF`

Action:
- do **not** ask Owner to rerun proof yet;
- use fresh stage `PYLAUNCH_DISCOVERY_V2_HARDENING_V1`;
- after that, fresh QA/cross-component audit decides whether live proof is authorized.

### 2. Browser Fleet Discovery V2

Worker result:
- `parallel/BROWSER_FLEET/RESULT.md`
- 15/15 repository regression PASS;
- explicit `cheap-indicator-only` role;
- strong per-endpoint port confinement.

Later cross-component audit says Fleet role differences are intentional and should not be “fixed” into a second identity authority.

Classification:

`ACCEPTED_COMPLETE — DO NOT OPTIMIZE NOW`

Action:
- keep closed;
- only reopen if a later bounded real proof finds a concrete Fleet defect.

### 3. WOF-052L Recorder Discovery V2 / 10-room long capture readiness

Worker results initially said:
- `WOF-052L DISCOVERY V2 READY`;
- `READY FOR 10-ROOM LONG CAPTURE`.

Later evidence invalidated that full readiness claim:
- independent long-capture QA found owner-facing English P1;
- cross-component audit found P0 cross-page shared-Worker ambiguity in evidence ownership;
- audit also found endpoint confinement, URL-scheme and direct-association P1 drift.

Classification:

`NEEDS_FRESH_FIX — P0/P1; LONG CAPTURE NOT AUTHORIZED`

Action:
- consolidate the technical + Chinese UX fixes in one Recorder hardening stage;
- do not spend one hour of Owner capture time before fresh QA and cross-component retest pass.

### 4. Prospective Validator Discovery V2

Worker result:
- `parallel/PROSPECTIVE_VALIDATOR/DISCOVERY_V2_REGRESSION_RESULT.json`;
- 16/16 fresh Discovery V2/entrypoint tests PASS.

This is useful local progress, but later independent evidence found two material issues:
- cross-component audit: P0 cross-page shared-Worker evidence ownership ambiguity;
- Beta manifest QA: Validator final verdict ignores declared `minDistinctTargets`, `minObservedTypes`, `requireLifecycleReset` conservative gates.

Classification:

`NEEDS_FRESH_FIX — P0/P1`

Action:
- one consolidated fresh Prospective Validator hardening stage should close both the Discovery admission and false research-PASS risks.

### 5. Discovery V2 cross-component audit

Result:
- `parallel/DISCOVERY_V2_AUDIT/RESULT.md`;
- explicitly identified one grouped P0 and four P1 drift groups;
- correctly separated Fleet advisory role from authoritative evidence consumers;
- did not modify component implementations.

Classification:

`ACCEPTED_COMPLETE — HIGH-VALUE AUDIT`

Action:
- close this audit thread;
- after component fixes land, run a **fresh cross-component retest**, not the old audit thread.

### 6. Unified Windows Live Proof Bundle

Development result originally said:
- `UNIFIED LIVE PROOF READY — ONE OWNER WOF RUN REMAINS`;
- 9/9 bundle regression PASS.

Fresh independent QA then found:
- P1 fail-closed aggregation can still return PASS while a fatal/blocker is retained;
- stale positive state after child exit can remain eligible for PASS;
- owner Y/N question can be reached after blocker/fatal state.

Classification:

`NEEDS_FRESH_FIX — P1; OWNER RUN NOT AUTHORIZED`

Action:
- fresh fail-closed fix stage in `parallel/LIVE_PROOF_BUNDLE/**`;
- fresh independent QA afterward;
- only then may preflight/package work become current.

### 7. Regression Orchestrator

Result:
- `parallel/REGRESSION_ORCH/RESULT.md`;
- orchestrator contract proven on Windows;
- correctly exposed component failures rather than hiding them.

Later cross-component audit found a new coverage gap:
- Prospective Discovery V2 safety test not yet required globally;
- Recorder official V2 owner integration surface not fully represented.

Classification:

`ACCEPTED_CORE / NEEDS P1 REFRESH AFTER COMPONENT FIXES`

Action:
- do not rebuild orchestrator core;
- wait until Recorder/Prospective/PYLAUNCH hardening tests land;
- then fresh `REGRESSION_ORCH_DISCOVERY_V2_GUARD` stage updates only required safety coverage.

### 8. Alpha Safe Transport Mock Harness

Result:
- `parallel/ALPHA_TRANSPORT_MOCK/**`;
- 67/67 contract vectors PASS;
- identity/session/stale/backpressure/failure/safety vectors covered;
- no product implementation changes.

Classification:

`ACCEPTED_COMPLETE — WAITING_GATE`

Action:
- do not add more mock vectors now without a concrete gap;
- consume it when Alpha Safe Transport implementation starts.

### 9. Alpha Transport-Aware Browser Acceptance V2 Prep

Result:
- `parallel/ALPHAACCEPT/PREP_STATUS.md`;
- `ACCEPTANCE PREP READY — WAITING FOR TRANSPORT INTEGRATION`;
- compact result schema/validator/collector/Chinese flow prepared.

Classification:

`ACCEPTED_COMPLETE — WAITING_GATE`

Action:
- do not redesign acceptance now;
- wait for actual transport implementation and fresh integrated regression.

### 10. Beta prospective manifest set

Compilation produced research-only READY manifests and correctly kept unresolved T18 branches NOT_READY.

Fresh QA found the blocker in the **Validator execution of gates**, not primarily in manifest generation.

Classification:

`ACCEPTED_WAITING_GATE — DO NOT REBUILD MANIFESTS YET`

Action:
- first fix Prospective Validator gate enforcement;
- then fresh Beta manifest-set QA retest;
- only change manifests if that fresh QA finds manifest-specific defects.

### 11. WOF-052L automatic discovery -> prospective handoff

Development path has one-click handoff, frozen manifest hash and discovery/prospective separation with local regression.

However the requested fresh independent QA result is not present as a durable final QA result in its expected QA lane, and the underlying Prospective Validator is currently being hardened.

Classification:

`ACCEPTED_DEV / QA WAITING_GATE`

Action:
- do not spend a worker re-QAing it while Validator semantics are changing;
- after Prospective hardening, open a fresh handoff QA stage.

### 12. Owner one-click package/bootstrap

The package line added immutable snapshot/hash checks, stale-cache protections and Windows CI proof, and has useful owner UX value.

But PYLAUNCH/Recorder/Unified Proof are changing again.

Classification:

`ACCEPTED_INFRA / WAITING_GATE`

Action:
- do not keep refreshing package version on every intermediate commit;
- refresh once after the current P0/P1 component stack and Unified Proof fresh QA are green.

---

## Current priority decision

### START NOW

P0/P1 only, disjoint write scopes:

1. `WOF052L_RECORDER_DISCOVERY_V2_HARDENING_V1` — P0/P1
2. `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_V1` — P0/P1
3. `PYLAUNCH_DISCOVERY_V2_HARDENING_V1` — P1 before authoritative live proof
4. `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_V1` — P1 before owner run

### WAIT

Do not start yet:
- Discovery V2 conformance final retest — wait for component hardening blobs;
- Regression Orchestrator Discovery V2 guard — wait for new component tests;
- Unified Proof preflight/package refresh — wait for fail-closed fix + component alignment;
- Long-capture QA retest — wait for Recorder hardening;
- Beta manifest QA retest — wait for Prospective hardening;
- WOF-052L handoff QA — wait for Prospective hardening;
- Alpha Safe Transport implementation — decide immediately after Discovery/Unified stack repository gates are green; prefer doing as much implementation/mock QA as possible before asking Owner for a real run.

## Owner action

`NO`

There is still substantial repository-side code/audit/regression work that must be completed before another real Windows/WOF run is justified.
