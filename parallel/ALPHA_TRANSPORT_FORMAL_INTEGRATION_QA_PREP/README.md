# Alpha Transport Formal Integration QA Prep

Stage: `ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP_V1`

Purpose: an independent, deterministic acceptance harness for the future formal real-adapter integration SUT. This lane does **not** certify integration and does not modify `product/alpha/**` or the integration implementation.

## Frozen provenance

The expected outcomes are derived from current-head public/frozen contracts:

- Safe Transport reference contract: `parallel/ALPHA_TRANSPORT_IMPL/README.md`, `constants.mjs`, `adapters.mjs`, `reference_runtime.mjs`.
- Stale-generation fresh QA: `parallel/ALPHA_TRANSPORT_QA_STALE_GENERATION/targeted_stale_generation_qa.mjs`.
- RC5 gameplay-first bootstrap contract: `product/alpha/ALPHA_RC5_REPORT.md`.
- Formal integration scope: `parallel/PM/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_START_PROMPT.md`.

The harness deliberately does not import implementation code from those lanes. `expected_outcomes.json` is the frozen oracle consumed by the runner.

## Expected SUT seam

Point the runner at a module with this named export:

```js
export const FORMAL_INTEGRATION_QA_SEAM = {
  schema: 'wof-alpha-formal-integration-qa-sut-v1',
  async createScenarioDriver() {
    return {
      async reset() {},
      async runScenario(spec) { /* exercise the real integrated path and return normalized observations */ }
    };
  }
};
```

`runScenario(spec)` receives the complete case object, including its injection. It must drive the real integration path and return observations matching the success/forbidden checks. The bridge may live beside the formal integration implementation, but this prep lane does not create or edit that bridge.

If the module is absent, the export/schema is absent, or either driver function is missing, the runner refuses PASS and exits non-zero with `WAITING_SUT` or `SEAM_DRIFT`.

## Commands

Harness validation only (never an integration PASS):

```text
node --check formal_integration_qa.mjs
node formal_integration_qa.mjs --selftest
```

Expected: 14/14 `SELFTEST_PASS`, plus a negative control proving a forbidden stale completion is detected.

Default with no SUT:

```text
node formal_integration_qa.mjs
```

Expected: `WAITING_SUT`, `passClaimed=false`, exit code 3.

Fresh QA after integration delivery:

```text
node formal_integration_qa.mjs --sut <path-to-formal-integration-qa-bridge.mjs>
```

Only 14/14 passing against the real bridge may report `PASS`.

## Coverage

1. Normal attach -> warning publish -> clear.
2. Adapter/discovery unavailable -> silent fail-closed, gameplay unaffected.
3. Old unresolved completion after pair rebind rejected.
4. New generation stays live after old completion returns.
5. Runtime epoch reset revokes prior tick authority.
6. Worker replacement/reinstall revokes prior authority.
7. Session/generation/nonce mismatch rejected.
8. Disconnect/reconnect clears stale state.
9. Heartbeat 250 ms, stale 1500/1501 ms, immediate clear/change behavior.
10. Unsupported identity/admission stays warning-silent.
11. One in flight, skipped overlap, no catch-up, queue depth zero.
12. Chinese owner-facing failure/status surface when exposed.
13. Exact read-only / zero-write / no-input / no-Worker-replacement / no-Blob-rewrite safety invariants.
14. RC5 bootstrap/transport failure leaves the game path unaffected.

Each case in `expected_outcomes.json` contains a concrete injection, success criteria, and forbidden outcomes.
