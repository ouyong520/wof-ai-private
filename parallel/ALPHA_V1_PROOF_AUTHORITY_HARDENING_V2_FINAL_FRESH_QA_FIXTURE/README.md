# Alpha V1 Proof-Authority Hardening V2 — Final Fresh QA Independent Fixture

Status: **PREP ONLY — QA-OWNED FIXTURE READY — NO CURRENT-SUT VERDICT**

This namespace is independent from Hardening V2 implementation regressions. Its oracle is frozen from the PM Hardening V2 contract and the independent Cross-check V2 blocker semantics.

## Files

- `fixture_catalog.json` — frozen 17-case oracle and assertion names.
- `fixture_vectors.mjs` — deterministic authority/lifecycle/mapping/malformed input vectors.
- `CASE_MATRIX.md` — independent adversarial construction for each case.
- `fixture_selftest.mjs` — fixture schema/coverage self-check only; loads no SUT.
- `future_fresh_qa_preflight.mjs` — post-Hardening exact-commit/blob preflight.
- `future_fresh_qa_runner.mjs` — final 17-case oracle runner using a QA-owned thin SUT adapter.
- `SUT_ADAPTER_CONTRACT.md` — rules for binding the exact fixed public interface without changing fixture expectations.

## Self-check now

```bash
node parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/fixture_selftest.mjs
```

Expected output:

`PASS — fixture schema/coverage self-check only — 17/17 — NO SUT LOADED — NO SUT VERDICT`

Running that command is allowed during prep because it does not import or execute proof implementation.

## Future single Fresh-QA execution

Do this only after the Hardening V2 canonical claim is `COMPLETE` and its durable RESULT identifies the fixed commit/blobs. The future Fresh-QA stage first pins/checks out that exact commit and creates its own canonical Fresh-QA claim, then runs:

```bash
node parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/fixture_selftest.mjs && \
node parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/future_fresh_qa_preflight.mjs \
  --hardening-result parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/PROOF_AUTHORITY_HARDENING_FIX_V2_RESULT.md \
  --manifest parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/RUN_MANIFEST.json \
  --fixed-commit <HARDENING_V2_COMPLETE_COMMIT> && \
node parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/future_fresh_qa_runner.mjs \
  --adapter <QA_OWNED_POST_HARDENING_SUT_ADAPTER.mjs>
```

The adapter may only translate final fixed public interfaces into the frozen case oracle. It cannot import implementation regressions or change expected outcomes.

## Exact SUT pin set required after Hardening V2 closes

The final Fresh QA must record fixed commit SHA plus path + Git blob SHA for, at minimum:

- `RUN_MANIFEST.json` itself;
- proof `proof_core.js`;
- proof Top;
- proof Worker;
- proof loader;
- production real Worker selected by the proof/runtime authority;
- player warning helper;
- enemy target-label helper;
- evidence schema;
- every new authority-root / signer-provenance / attestation module introduced by Hardening V2;
- every new lifecycle or mapping-authority module introduced by Hardening V2.

If the post-fix manifest references additional authority-critical blobs, they are mandatory pins too. No `main`-floating execution is authoritative.

## Frozen independence rules

- Do not copy `proof_authority_regression.mjs`, `tooling_regression.mjs`, or Hardening V2 selftest expected outputs.
- Implementation regressions are supportive evidence only after the independent 17-case run.
- Negative cases must fail for the intended mismatch, not an unrelated missing prerequisite.
- `QA-PA-015` is mandatory positive control so hardening cannot pass by globally disabling proof.
- Synthetic/repository evidence may never activate production projection/calibration profiles.
- Prep and final QA are repository-only unless PM separately authorizes Browser/WOF; this prep does not launch Browser/WOF.

## Prep boundary

This prep stage does **not** create the final Fresh-QA canonical claim and does **not** issue PASS/BLOCKED against the current proof implementation.
