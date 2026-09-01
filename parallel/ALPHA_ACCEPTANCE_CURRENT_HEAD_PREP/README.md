# WOF Alpha — Current-HEAD Acceptance Prep

Stage: `ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP_V1`  
Status: **PREPARED — WAITING RELEASE GATES**  
Owner action now: **NO**.

This lane prepares one bounded later Windows/Browser/WOF acceptance. It contains no runtime PASS evidence and does not declare Alpha released.

## Current authority and provenance

The prep reuses current production contracts/interfaces and does not copy gameplay offsets or change upstream runtime semantics.

| authority | current blob observed during final drift audit | use |
| --- | --- | --- |
| `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md` | `f8186d051862c16d0757a48a915fff338bc652a0` | frozen Safe Transport semantics |
| `parallel/PYLAUNCH/wof_launcher/browser.py` | `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332` | strict local Browser/CDP startup attestation |
| `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` | `ec9d27bfe26557a11187a23853893b898a3366d1` | unique page/native Worker/WASM/World Gate A |
| `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py` | `1a5c6a255468c096ddd5df79993851e4d41e23cb` | page pair + fresh detector-local Gate B + rebind |
| `product/alpha/wof_alpha_real_worker.js` | `9c63a2c6a185ead8406487edd10038c035d41623` | detector-local identity/read-only runtime |
| `parallel/ALPHAACCEPT/wof_alpha_acceptance.user.js` | `1ca2b4014bd7498a9cc9380ecd8194bee0e5da49` | support-only collector and negative pair probes |

The drift audit observed `real_adapter.py` advance during this prep from an earlier blob to `1a5c6a25…`; the current implementation now explicitly requires fresh detector-local `identity.ok`, exact current SHA-256 and identity signature. The prep imports the current module at execution time instead of freezing the earlier implementation bytes.

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

## Prepared artifacts

- `acceptance_orchestrator.py` — future one-command bounded acceptance driver.
- `RUN_CURRENT_HEAD_ACCEPTANCE.cmd` — Windows one-click wrapper.
- `current_head_acceptance.schema.json` — compact final JSON schema.
- `failure_classification.json` — fail-closed English codes + Chinese owner messages.
- `fixtures/acceptance_result.template.json` — explicit fixture-only/non-evidence result shape.

No file in this directory changes `product/alpha/**`, PYLAUNCH, Recorder, Unified Live Proof, HUD or Owner OneClick behavior.

## Hard gate before Browser

The orchestrator exits `BLOCKED` **before Browser access** unless the release-candidate checkout has:

1. `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2` claim `COMPLETE`;
2. `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1` claim `COMPLETE`;
3. durable `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/RESULT.md`;
4. fresh local PASS for:
   - `node parallel/ALPHA_TRANSPORT_IMPL/run_all.mjs`;
   - `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs`;
   - complete `parallel/PYLAUNCH/tests` unittest discovery.

At this prep's final drift audit, formal integration recovery is still `ACTIVE`, while the adversarial review is `BLOCKED` on the previously observed stale detector-local identity P1. Therefore **the current checkout is deliberately not authorized for Owner Browser acceptance**. The newer real-adapter code appears to address that risk direction, but this prep does not self-certify the blocker closed; the independent release gate must do so.

## Single bounded owner procedure — later only

When PM/release says the release gates are green:

1. On the exact release-candidate checkout, start the normal supported Windows Browser/WOF flow and enter one ordinary playable room. Do not open DevTools or Worker Console.
2. Double-click `parallel\ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP\RUN_CURRENT_HEAD_ACCEPTANCE.cmd`.
3. The tool first reruns repository gates. Any non-green gate stops before Browser with a Chinese `BLOCKED` reason; do not bypass it.
4. If green, the tool performs strict local `/json/version` attestation, Discovery V2 unique page/native-Worker/WASM/World Gate A, then installs the fixed support-only collector and asks exactly one Owner question: `当前房间可以正常操作，开始验收？ [Y/N]`.
5. Enter `Y` once and continue playing normally. The tool waits a bounded interval for current-pair state / detector Gate B and records approved T18 warnings only if they occur naturally. It never injects gameplay input to manufacture one.
6. The tool automatically exercises Alpha-only page authority clear/rebind and support-only old-generation/wrong-nonce BroadcastChannel rejection. It does not navigate the game, write RAM, inject keyboard/mouse/controller input, replace/wrap the game Worker, or create a Blob Worker.
7. Keep the first generated `acceptance_result.json`. Preserve a real `FAIL`; do not retry until it happens to pass. Retry an `INCOMPLETE` only after fixing its explicit environment/evidence issue. Browser PASS is evidence for PM, not a release declaration.

There is no fallback involving pasted JavaScript, Worker selection, RAM inspection or ad-hoc Console diagnosis.

## Acceptance envelope

The compact JSON records the exact `snapshotCommit`, repository gates, Browser/CDP attestation, unique page/Worker/WASM + World Gate A, current session/generation/nonce and fresh rebind, detector-local Gate B, first current-pair state, natural warning sanity, immediate page-authority clear, exact offline 1500/1501 stale gate, old-generation/wrong-nonce rejection, render liveness, and exact safety:

```text
readOnly=true
ramWrites=0
inputInjection=false
windowWorkerReplacement=false
```

A naturally observed approved T18 warning records `firstValidWarning=PASS`; if none appears in the bounded window, it records `NOT_EXERCISED`. Missing natural warning evidence is never fabricated and never authorizes attack/input synthesis.

## Drift rule

Every real result pins `git rev-parse HEAD`, imports current PYLAUNCH/formal-integration modules, and reruns current repository gates. If an upstream interface needed by the bounded driver disappears or changes incompatibly, execution fails closed rather than guessing replacement fields.

ALPHA CURRENT-HEAD ACCEPTANCE PREP READY — WAITING RELEASE GATES
