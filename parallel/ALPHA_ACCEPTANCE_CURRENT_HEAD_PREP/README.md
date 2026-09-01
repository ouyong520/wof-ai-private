# WOF Alpha — Current-HEAD Acceptance Prep

Stage: `ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP_V1`

Status: **PREPARED — WAITING RELEASE GATES**

Owner action now: **NO**.

This lane prepares one bounded later Windows/Browser/WOF acceptance. It does not contain runtime PASS evidence and it must not be used to infer Alpha release readiness by itself.

## Current frozen authority

The preparation is derived from current-head contracts/interfaces, without copying gameplay offsets or changing upstream runtime semantics:

- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`
  - blob `f8186d051862c16d0757a48a915fff338bc652a0`
- `parallel/PYLAUNCH/wof_launcher/browser.py`
  - Browser/CDP attestation via `probe_endpoint_diagnostic()`
  - blob `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py`
  - Discovery V2 admission, World 921031 Gate A, page bind, current pair authority, Gate B worker install/rebind
  - observed prep blob `6fbf569d9a9ef46a7502b1b979096cf757e8b105`
- `product/alpha/wof_alpha_real_worker.js`
  - detector-local identity and read-only transport runtime
  - observed prep blob `9c63a2c6a185ead8406487edd10038c035d41623`
- `parallel/ALPHAACCEPT/wof_alpha_acceptance.user.js`
  - support-only page collector / old-generation + wrong-nonce negative probes
  - blob `1ca2b4014bd7498a9cc9380ecd8194bee0e5da49`

Fixed identity:

```text
game/build: Warriors of Fate (World 921031)
release: wof-alpha-rc3
transport: wof-alpha-safe-transport-v1
CPU-logical bytes: 1048576
SHA-256: 5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
identity signature: wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8
ordinary stale: 1500 ms; offline exact boundary 1500/1501
```

## Files

- `acceptance_orchestrator.py` — future one-command bounded acceptance driver.
- `RUN_CURRENT_HEAD_ACCEPTANCE.cmd` — Windows one-click wrapper.
- `current_head_acceptance.schema.json` — compact final JSON schema.
- `failure_classification.json` — fail-closed result classification + Chinese messages.
- `fixtures/acceptance_result.template.json` — explicit fixture-only/non-evidence shape.

No file in this directory changes product Alpha, PYLAUNCH, Recorder, Unified Live Proof, HUD or Owner OneClick behavior.

## Hard release gate before Browser

The orchestrator exits `BLOCKED` **before Browser access** unless all of these are true at the checkout being accepted:

1. `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2` claim is `COMPLETE`;
2. `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1` claim is `COMPLETE`;
3. `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/RESULT.md` exists;
4. current checkout passes:
   - `node parallel/ALPHA_TRANSPORT_IMPL/run_all.mjs`;
   - `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs`;
   - full `parallel/PYLAUNCH/tests` unittest discovery.

This intentionally means the current prep state blocks owner acceptance while formal integration/review are still active.

## Single bounded owner procedure — later only

When PM/release says the release gates are green, use exactly this procedure:

1. On the exact release-candidate checkout, start the normal supported Windows Browser/WOF flow and enter one ordinary playable room. Do not open DevTools or Worker Console.
2. Double-click `parallel\ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP\RUN_CURRENT_HEAD_ACCEPTANCE.cmd`.
3. The tool first reruns repository gates. If any gate is not green it stops before Browser and prints a Chinese `BLOCKED` reason. Do not bypass it.
4. If gates are green, the tool performs strict local Browser `/json/version` attestation, Discovery V2 page/native-Worker/WASM/World 921031 Gate A, installs the fixed support-only collector, and asks one question only: `当前房间可以正常操作，开始验收？ [Y/N]`.
5. Enter `Y` once. Continue playing normally. Do not intentionally manufacture attacks. The tool waits a bounded interval for current-pair state / detector Gate B and optionally records naturally occurring approved T18 warnings.
6. The tool automatically exercises Alpha-only page clear/rebind and support-only old-generation/wrong-nonce BroadcastChannel rejection. It does not navigate the game, inject keyboard/mouse/controller input, write game RAM, replace/wrap the game Worker, or create a Blob Worker.
7. Keep the first generated `acceptance_result.json`. If it is `FAIL`, do not retry until it happens to pass. If it is `INCOMPLETE`, retry only after fixing the explicit environment/evidence issue. A Browser PASS remains evidence for PM; it is not a release declaration.

There is no second manual diagnostic path. No pasted JavaScript, no Worker selection, no RAM inspection and no ad-hoc Console fallback are allowed.

## Acceptance envelope

The compact result records:

- exact checkout `snapshotCommit`;
- repository/release gates;
- Browser/CDP startup attestation;
- unique page/Worker/WASM + launcher World 921031 Gate A;
- current `session / pairGeneration / pairNonce` and fresh rebind;
- detector-local Gate B identity;
- first current-pair state and natural warning sanity;
- immediate page-authority clear + exact offline 1500/1501 stale gate;
- old generation/wrong nonce rejection;
- render liveness / no navigation / no injected gameplay input;
- exact `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `windowWorkerReplacement=false` safety;
- deterministic English failure code plus Chinese owner status.

A naturally occurring approved T18 warning is recorded as `PASS`; if none appears within the bounded window, `firstValidWarning=NOT_EXERCISED`. This is not converted into fabricated runtime evidence and does not authorize attack/input synthesis.

## Current-head drift rule

The runtime result always pins `git rev-parse HEAD`. The one-click driver imports current PYLAUNCH and formal integration surfaces at execution time and reruns their gates. If a future upstream change removes or changes a required fixed interface, the run must fail closed rather than infer replacement field names.

Preparation success does **not** mean formal integration or release gates are already complete.

ALPHA CURRENT-HEAD ACCEPTANCE PREP READY — WAITING RELEASE GATES
