# Unified Live Proof — Current-HEAD Repository Preflight Fresh QA V2 Result

Date: 2026-09-02  
Stage: `UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V2`

## Verdict

**PASS — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT FRESH QA V2 — REPOSITORY PREFLIGHT GREEN**

Owner action: **NO**.

This was repository-only fresh independent QA. No production/preflight implementation was modified, no Browser/WOF was launched, and no WOF-052/WOF-052L long capture was started.

## Dedup / audited HEAD

- start HEAD: `c0343c12d99574e176765f5dd8ab843a92f2580d`
- atomic claim commit: `26fe29f442193246bf3d131a8c57d5a4cde39dea`
- final pre-result re-read HEAD: `25b664fea50a593cd46a8aca1ae7259351b8687c`
- concurrent movement after the claim was an unrelated Alpha enemy-target-head-label QA claim only;
- all four audited preflight blobs remained unchanged across the final drift check.

Audited blobs:

- `parallel/LIVE_PROOF_BUNDLE/unified_preflight.py` -> `c756b3da7a8a0c092efe20f2587e131d497f5f72`
- `parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py` -> `1a73d02f8171dbbd50cabff52a83c989541de2f7`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_preflight.py` -> `c59edb55e3d99da219bb78d8dffc427cfd2fbb75`
- `parallel/LIVE_PROOF_BUNDLE/UNIFIED_PREFLIGHT_STATUS.json` -> `6dc53eee9bc235d43b466ff83ff0aec2b6bfafe1`

These are exactly the selector-fix blobs documented as ready for independent QA.

## Current authoritative successor evidence

### PYLAUNCH Startup Attestation

Current preflight consumes:

- `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.md`
- `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.json`
- `parallel/PM/STAGE_CLAIMS/PYLAUNCH_STARTUP_ATTESTATION_QA_V1.json`

Fresh re-read semantics are valid:

`PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED`

The claim is `COMPLETE` with the exact PASS result, and the machine result has the expected schema/stage/status/decision.

Current production blobs still exactly equal the successor pins:

- `browser.py` -> `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332`
- `monitor.py` -> `8e3c5c527fdd5a845bbfc135f55014de22078cf4`
- `discovery_v2.py` -> `ec9d27bfe26557a11187a23853893b898a3366d1`

The historical ParentFrame QA remains durably BLOCKED at:

`parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md`

That historical evidence was not rewritten. Current selector logic does not treat it as an authoritative release gate when the current Startup Attestation successor is valid.

### Recorder in-flight generation atomicity

Current preflight consumes:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.json`
- `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1.json`

Fresh re-read semantics are valid:

`PASS — RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA — READY FOR CURRENT-HEAD UNIFIED PREFLIGHT`

The machine result requires PASS plus safety semantics, the claim is `COMPLETE` with the exact stop condition, and the current production blob remains exactly pinned:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py` -> `8df637d370d187660592fe8de0f1c73ff3057804`

The historical Unified freshness BLOCKED evidence remains preserved, but is no longer selected as current authority.

## Browser Fleet / Discovery / safety evidence

Current consumed repository evidence remains compatible:

- Browser Fleet: `BROWSER FLEET DISCOVERY V2 READY`;
- PYLAUNCH: `PYLAUNCH DISCOVERY V2 HARDENING READY`;
- Recorder: `WOF052L RECORDER DISCOVERY V2 HARDENING READY`;
- `FRESHNESS_FIX_STATUS.json`: `state=COMPLETE`, combined validation PASS, `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `windowWorkerReplacement=false`, `longCaptureAutoStarted=false`.

`UNIFIED_PREFLIGHT_STATUS.json` is correctly marked as a repository selector-policy example rather than runtime authority. Runtime preflight still requires a fresh snapshot and fresh regression execution.

## Source-exact current implementation regression

The execution environment had no native private checkout and no network access to GitHub. Per the start prompt, current GitHub blobs were reconstructed source-exact in an isolated directory.

Before execution, Git blob SHA-1 was recomputed locally and matched GitHub exactly for all three executed files:

- `unified_preflight.py` -> `c756b3da7a8a0c092efe20f2587e131d497f5f72`
- `unified_preflight_entrypoint.py` -> `1a73d02f8171dbbd50cabff52a83c989541de2f7`
- `test_unified_preflight.py` -> `c59edb55e3d99da219bb78d8dffc427cfd2fbb75`

Executed:

```text
python -m unittest -v test_unified_preflight.py
Ran 22 tests
OK
```

Result: **22 PASS / 0 FAIL**.

This directly revalidated the current implementation-side suite, but was not used alone as independent acceptance.

## Fresh independent attack matrix

A separate transient QA harness exercised additional vectors beyond the committed 22-case suite.

Result: **10 PASS / 0 FAIL**.

Fresh independent vectors included:

1. historical ParentFrame + Unified freshness BLOCKED evidence present while current successors PASS -> repository preflight remains PASS;
2. malformed Startup Attestation machine JSON -> BLOCKED;
3. missing Startup Attestation RESULT.md -> BLOCKED;
4. Startup claim `COMPLETE` without required PASS result -> BLOCKED;
5. malformed Recorder successor machine JSON -> BLOCKED;
6. Recorder claim `COMPLETE` with wrong/non-PASS stop condition -> BLOCKED;
7. future snapshot beyond tolerance -> BLOCKED;
8. current PYLAUNCH production blob drift -> BLOCKED and guarded live runner invocation count remains zero;
9. current `unified_live_proof.py` blob drift -> BLOCKED and guarded live runner invocation count remains zero;
10. valid PASS path invokes only the supplied guarded test seam exactly once.

Combined with the current exact 22-case suite, the required stale snapshot, mixed commit, missing test/file, unsupported Discovery, regression failure, Chinese-first owner output, safety mismatch, and blocked-live-launch behaviors remain fail closed.

## Required prompt checks

1. Historical PYLAUNCH ParentFrame BLOCKED no longer false-blocks current Startup Attestation PASS — **PASS**.
2. Missing/BLOCKED/malformed Startup successor blocks — **PASS**.
3. PYLAUNCH production blob drift blocks — **PASS**.
4. Historical Unified freshness BLOCKED no longer false-blocks current Recorder successor PASS — **PASS**.
5. Missing/BLOCKED/malformed Recorder successor blocks — **PASS**.
6. `unified_live_proof.py` drift blocks — **PASS**.
7. `COMPLETE` claim without required PASS semantics blocks — **PASS**.
8. stale/future snapshot, mixed component commit, missing files/tests, unsupported Discovery, failed regression, safety mismatch block — **PASS**.
9. Chinese-first blocker output, `ownerActionRequired=false`, `longCaptureAutoStarted=false`, `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `windowWorkerReplacement=false` preserved — **PASS**.
10. BLOCKED preflight never invokes live runner; PASS invokes only guarded test seam — **PASS**.
11. Current exact implementation-side 22-case suite remains green — **PASS, 22/22**.

## Execution boundary

This QA does **not** claim native execution of all nine repository regression entrypoints from a private checkout. A private checkout was unavailable. The selector implementation and its exact 22-case suite were source-exact reconstructed and hash-verified, while current repository gate evidence and successor production pins were independently re-read from GitHub.

No synthetic result is represented as Browser/WOF proof. No live Browser/WOF projection or capture evidence was produced or required by this repository-only stage.

## Safety / scope

Preserved exactly:

- repository-only QA;
- production implementation writes: **0**;
- Browser/WOF started: **false**;
- long capture auto-started: **false**;
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- `windowWorkerReplacement=false`;
- Owner action: **NO**.

Writes are limited to:

- `parallel/LIVE_PROOF_BUNDLE_QA_CURRENT_HEAD_PREFLIGHT_V2/**`
- `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V2.json`

## Stop condition

**PASS — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT FRESH QA V2 — REPOSITORY PREFLIGHT GREEN**
