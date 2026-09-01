# Alpha Transport Formal Integration QA Prep — Result

Stage: `ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP_V1`  
Status: **HARNESS READY — WAITING SUT**  
Start commit: `6e453a467608430e1c9610511df458ab3c62505b`  
Validation/current-head snapshot before result write: `250f8cb7715b6c9c2acb69e855cb06b62ce94576`

## Scope / write boundary

This stage prepared only independent fresh-QA assets. It did **not** certify formal integration and did not modify:

- `product/alpha/**`;
- `parallel/ALPHA_TRANSPORT_IMPL/**`;
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/**`;
- PYLAUNCH / Recorder / Live Proof / Owner One-Click / HUD / Prospective lanes.

Files created by this stage:

- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/expected_outcomes.json`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/formal_integration_qa.mjs`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/README.md`
- this `RESULT.md`
- mandatory PM claim file only.

## Contract provenance re-read

The harness was derived independently from current-head frozen/public contracts, not by importing implementation assertions:

- `parallel/ALPHA_TRANSPORT_IMPL/README.md`
- `parallel/ALPHA_TRANSPORT_IMPL/constants.mjs`
- `parallel/ALPHA_TRANSPORT_IMPL/adapters.mjs`
- `parallel/ALPHA_TRANSPORT_IMPL/reference_runtime.mjs`
- `parallel/ALPHA_TRANSPORT_QA_STALE_GENERATION/targeted_stale_generation_qa.mjs`
- `product/alpha/ALPHA_RC5_REPORT.md`
- `parallel/PM/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_START_PROMPT.md`

`parallel/ALPHA_TRANSPORT_REAL_ADAPTER_PREP/**` was checked and is not present under that exact path on current HEAD, so no nonexistent asset was treated as authority.

Frozen acceptance constants include:

- transport `wof-alpha-safe-transport-v1`;
- World 921031 golden SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- stale boundary 1500/1501 ms;
- heartbeat bound 250 ms;
- exact safety: read-only, `ramWrites=0`, no input injection, no Worker replacement, no Blob rewrite, no game postMessage control, no heap writes, no assist mode.

## Harness structure

`expected_outcomes.json` is the machine-readable acceptance oracle. Every case states:

- deterministic injection;
- required success observations;
- explicit forbidden outcomes.

`formal_integration_qa.mjs` is a dependency-free Node runner. A real integration must expose a QA bridge as:

- named export `FORMAL_INTEGRATION_QA_SEAM`;
- schema `wof-alpha-formal-integration-qa-sut-v1`;
- `createScenarioDriver()`;
- driver functions `reset()` and `runScenario(spec)`.

No SUT path => `WAITING_SUT`, `passClaimed=false`, exit 3.  Missing/wrong seam => `SEAM_DRIFT`, no PASS. Only a real pointed SUT producing all required observations can report formal runner `PASS`.

## Required coverage implemented

14 deterministic cases cover all prompt requirements:

1. normal attach -> warning publish -> clear;
2. adapter/discovery unavailable -> silent fail-closed, game unaffected;
3. old unresolved completion after pair rebind rejected;
4. new generation remains live after old completion returns;
5. runtime epoch reset revokes prior tick authority;
6. Worker replacement/reinstall revokes prior authority;
7. session / generation / nonce mismatch rejected;
8. disconnect/reconnect clears stale state and rejects old state;
9. heartbeat 249/250 ms, stale 1500/1501 ms, immediate clear/change timing;
10. unsupported identity/admission cannot produce warning;
11. one tick in flight, skipped overlap, no catch-up, queueDepth 0;
12. Chinese owner-facing failure/status surface where exposed;
13. exact safety invariants;
14. RC5 bootstrap/transport failure leaves game path playable and game Worker untouched.

## Actual validation results

Executed against the exact local copies subsequently committed to this lane:

```text
node --check formal_integration_qa.mjs
=> PASS

node formal_integration_qa.mjs --selftest
=> SELFTEST_PASS
=> caseCount=14 passCount=14 failCount=0
=> negativeControl.detected=true
```

The negative control injects forbidden `oldCompletion.published=true`; the assertion engine rejects it.

Default no-SUT behavior was also executed:

```text
node formal_integration_qa.mjs
=> status=WAITING_SUT
=> passClaimed=false
=> exit code=3
```

Therefore the harness itself is runnable/checkable, while refusing to misreport integration PASS before a real SUT exists.

## Formal-integration consumer instructions

After the formal integration lane delivers a real QA bridge:

```text
cd parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP
node formal_integration_qa.mjs --sut <path-to-formal-integration-qa-bridge.mjs>
```

Fresh independent QA must pin the exact SUT/bridge Git blob or commit it consumes and retain the raw JSON output. This prep result must not be reused as final integration certification.

## Current-head drift re-read

Immediately before closing this prep stage:

- `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_V1.json` still reports `state=ACTIVE`;
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/RESULT.md` is absent.

Therefore formal integration is **not yet delivered** for this prep thread. The required drift-rule outcome is `HARNESS READY — WAITING SUT`. No integration blob is recorded because there is not yet a delivered result/SUT to pin.

## Remaining caveats

- This is harness readiness, not product/integration PASS.
- The future integration lane must supply a bridge that drives the real integrated path; a mock/self-reported outcome is not sufficient for fresh QA certification.
- If the delivered integration exposes a seam incompatible with `wof-alpha-formal-integration-qa-sut-v1`, fresh QA must stop as seam drift rather than weakening this oracle.
- Owner action required: **NO**.

## Acceptance

The independent fresh-QA design is complete, deterministic, machine-readable, locally validated, fail-closed when SUT is missing/drifted, and ready to consume the formal integration as soon as that SUT is delivered.

ALPHA FORMAL INTEGRATION QA HARNESS READY — WAITING FRESH QA SUT
