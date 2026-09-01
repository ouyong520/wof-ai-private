# Unified Live Proof Recorder Authority Heartbeat — Fresh Fix Start Prompt

## PM stage

- stageId: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_FIX_V1`
- priority: **P1 mainline release gate**
- purpose: close the fresh-QA blocker where arbitrary Recorder stdout can refresh stale Recorder admission authority.
- Owner Browser/WOF: **NOT REQUIRED**.

## Mandatory dedup / claim guard

Before substantive work, inspect `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_FIX_V1.json`.

- durable result already exists -> `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`
- exact stage ACTIVE elsewhere -> `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`
- otherwise claim and continue.

## Read first

Re-read current default-branch HEAD and at minimum:

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/PRIORITY_POLICY.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE/PREFLIGHT_HARDENING_RESULT.md`
- current `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- current Recorder supervisor/output behavior under `parallel/WOF052L_RECORDER/**` so trusted heartbeat syntax is derived from real producer semantics, not invented permissive matching.

## Write scope

Implementation may modify only:

- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_FIX_V1.json`

Do not modify PYLAUNCH, Recorder, Browser Fleet, Prospective, Alpha Transport, HUD, or product/alpha.

The preflight hardening stage is already complete. Preserve it and rerun its tests after this fix.

## Exact blocker to close

Current `RecorderEvidence.feed()` treats every non-empty stdout fragment as freshness authority before semantic classification. Therefore a stale historical admission can be revived by arbitrary diagnostic text / carriage-return output.

Required authority semantics:

1. distinguish generic Recorder stdout diagnostics from **trusted authority heartbeat/admission**;
2. only a fresh recognized admission or semantically recognized current supervisor heartbeat may advance Recorder authority freshness/generation;
3. generic stdout may be logged/diagnosed but must not reset success freshness or make `current_healthy=true`;
4. trusted heartbeat recognition must be narrowly derived from actual Recorder producer output; malformed/near-match arbitrary text must fail closed;
5. fatal/revocation always overrides heartbeat/admission authority;
6. stale/missing/future/malformed authority timestamps remain fail-closed;
7. current health and automated readiness depend on trusted authority generation/freshness, not generic output generation;
8. CR-aware reader support must remain intact;
9. Owner pre/post confirmation generation gates and process-health completeness remain intact;
10. `longCaptureAutoStarted=false` remains unchanged.

## Required regressions

Add/extend deterministic repository tests proving at least:

- valid admission -> age stale -> arbitrary `diagnostic text\r` cannot revive;
- valid admission -> age stale -> genuine current supervisor heartbeat can refresh only through the recognized authority path;
- malformed/near-match heartbeat cannot refresh;
- repeated arbitrary lines cannot advance authority generation;
- fatal marker after valid authority makes health false and cannot be revived by later generic output;
- valid CR-delimited heartbeat parsing still works;
- stale/future/missing child authority fails closed;
- preflight hardening tests still pass and still blocks known repository P1s until their fresh QA closes;
- all safety invariants remain `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no Worker replacement/wrap, no gameplay input capability.

Do not solve this by accepting every periodic status line. Authority renewal must be semantically narrow and auditable.

## PM meaning

READY from this implementation stage does not count as final PASS. It must be followed by a fresh independent Unified Live Proof freshness QA. Closing this blocker is required before repository preflight may honestly permit a bounded real Browser/WOF run.

## Stop conditions

READY only when the precise blocker is fixed and targeted + existing + preflight regressions are green:

`UNIFIED LIVE PROOF RECORDER AUTHORITY HEARTBEAT FIX READY — READY FOR FRESH QA`

If another precise P0/P1 blocker prevents safe completion, record it and stop:

`BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY HEARTBEAT FIX — <precise blocker>`

Owner action: `NO`.