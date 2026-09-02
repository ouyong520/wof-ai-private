# Alpha V1 Proof-Authority Hardening V2 — Final Fresh QA Independent Fixture Prep Result

## Result

**COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING V2 FINAL FRESH-QA FIXTURE PREP — INDEPENDENT FIXTURE READY / NO SUT VERDICT ISSUED**

## Scope actually performed

QA-prep only. No Browser/WOF launch. No `product/alpha/**` change. No proof implementation change. No danger-rule/target-semantics/Transport/PYLAUNCH/Recorder/OneClick/input/AI change. No production projection/calibration activation.

The current proof implementation was inspected only enough to identify the public surface and avoid copying implementation-owned regression. It was **not executed for a PASS/BLOCKED verdict**.

At prep close, the Hardening V2 canonical claim remained `ACTIVE`; this prep therefore did not create the final Fresh-QA canonical claim and did not start the one allowed post-Hardening Fresh QA.

## Independent oracle basis

The fixture expectations were derived from:

1. `parallel/PM/ALPHA_V1_ANCHORED_OVERLAYS_PROOF_AUTHORITY_HARDENING_FIX_V2_START_PROMPT.md`;
2. `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/PROOF_AUTHORITY_FIX_CROSSCHECK_V2_RESULT.md` blocker semantics.

`proof_authority_regression.mjs` was read only to avoid accidental duplication. Its expected outputs are not fixture authority and are not consumed by the future oracle runner.

## Deliverables

QA-owned namespace:

`parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/`

Contains:

- `fixture_catalog.json` — frozen 17-case oracle/assertions;
- `fixture_vectors.mjs` — deterministic authority, lifecycle, mapping and malformed/coercible vectors;
- `CASE_MATRIX.md` — exact independent attack recipe for every case;
- `fixture_selftest.mjs` — fixture-only schema/coverage check;
- `future_fresh_qa_preflight.mjs` — exact fixed-commit/blob gate;
- `future_fresh_qa_runner.mjs` — 17-case oracle runner;
- `SUT_ADAPTER_CONTRACT.md` — QA-owned thin binding rules for the post-fix public SUT;
- `README.md` — exact future execution sequence and fixed pin set.

## Coverage frozen for the one future Fresh QA

The 17 cases cover:

1. untrusted witness/signer provenance;
2. repository/synthetic fake-live evidence;
3. exact proofSession / Worker generation / runtime epoch / pair generation / pair nonce binding;
4. old capability invalidation after authority change;
5. cross-authority aggregation rejection;
6. player respawn invalidating old calibration;
7. same-slot/same-type/near-position enemy replacement not becoming retarget without continuity;
8. unsafe enemy type-offset reuse across lifecycle;
9. surface/drawing-buffer mapping authority mismatch;
10. malformed/coercible epoch rejection;
11. malformed/coercible/non-finite `warningSampleAt` with no freshness fallback;
12. malformed/coercible target rejection;
13. public mutable/serialized state unable to force `IMPLEMENTATION_READY`;
14. stale/replayed transaction evidence rejection;
15. positive same-authority/same-lifecycle retarget/live scoring control;
16. exact safety invariants `readOnly=true / ramWrites=0 / inputInjection=false / workerReplacement=false`;
17. synthetic evidence unable to activate production projection/calibration profiles.

## Fixture-only validation performed now

Executed against the QA fixture files only:

```text
node parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/fixture_selftest.mjs
```

Observed:

```text
PASS — fixture schema/coverage self-check only — 17/17 — NO SUT LOADED — NO SUT VERDICT
```

Also syntax-checked the fixture vector/selftest/preflight modules used by the prep. No proof SUT module was loaded by this validation.

## Future Fresh-QA gate and command

Only after Hardening V2 closes `COMPLETE` with a durable RESULT and exact fixed commit/blobs:

1. create the **single** final Fresh-QA canonical claim;
2. check out/pin the exact Hardening V2 fixed commit;
3. run `fixture_selftest.mjs`;
4. run `future_fresh_qa_preflight.mjs` with the Hardening RESULT, post-fix `RUN_MANIFEST.json`, and exact fixed commit;
5. bind the final fixed public interface through one QA-owned adapter obeying `SUT_ADAPTER_CONTRACT.md`;
6. run `future_fresh_qa_runner.mjs --adapter <QA-owned fixed-SUT adapter>`;
7. issue the one final Fresh-QA PASS/BLOCKED verdict from those 17 independent cases plus exact blob evidence.

The future adapter may translate method names/signatures if Hardening V2 changes the public surface, but may not alter `fixture_catalog.json`, case IDs, expected outcomes or assertion requirements.

## Exact fixed blobs that must be pinned post-Hardening

At minimum:

- `RUN_MANIFEST.json` itself;
- proof core;
- proof Top;
- proof Worker;
- proof loader;
- production real Worker used by authority binding;
- player warning helper;
- enemy target-label helper;
- evidence schema;
- every new signer-provenance / authority-root / attestation blob added by Hardening V2;
- every new lifecycle / mapping-authority blob added by Hardening V2;
- any additional authority-critical blob selected by the post-fix manifest.

Execution floating on `main` is not authoritative.

## Explicit non-verdict

This prep result makes **no claim** that the current SUT passes or fails Hardening V2. It only certifies that the independent fixture/oracle is ready for the one post-Hardening Fresh QA.
