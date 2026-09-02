# Alpha Transport Formal Real-Adapter Integration Current-HEAD Fresh QA V3 — Recovery V4 Result

Date: 2026-09-02
Stage: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3_RECOVERY_V4`

## Verdict

**PASS — ALPHA FORMAL REAL-ADAPTER INTEGRATION CURRENT-HEAD FRESH QA V3 RECOVERY V4 — CURRENT RELEASE RUNTIME VERIFIED / V3 INTERRUPTION SUPERSEDED**

Owner action: **NO**.

This recovery closes the interrupted V3 release gate without modifying production and without launching Browser/WOF. The original V3 canonical/stage claims remain historical `ACTIVE` evidence and were not overwritten, deleted, reused, or closed by this recovery.

## Canonical ownership

- dedup protocol: `v2`
- dedup key: `alpha.transport.formal-real-adapter-integration.current-head-fresh-qa-v3-recovery-v4`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/alpha.transport.formal-real-adapter-integration.current-head-fresh-qa-v3-recovery-v4.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3_RECOVERY_V4.json`
- claim token: `8043a101-0319-4034-9502-9e2795f18a31`
- claim start commit: `36808b1ecdfbd1b72a85c76e64e8839883cc65b7`

The canonical claim was create-only and the exact token/key/mode/stage/state were re-read from `main` before QA work. The stage claim was then create-only and re-read with the same token.

## Recovered V3 execution evidence

Durable V3 current-source execution evidence exists at:

- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3/EXECUTION_RESULT.json`
- execution matrix finalization commit: `6e1bd40c5fe1878b92deb8b56c0e562c46bf1653`
- evidence class: `FRESH_REPOSITORY_ONLY_CURRENT_SOURCE_EXECUTION_NOT_BROWSER_WOF`
- status: `PASS`
- total: **85/85 PASS, 0 FAIL**

Fresh counted runs:

- exact current worker adversarial: 8/8
- exact current HUD authority adversarial: 8/8
- exact current player-head transport adversarial: 20/20
- exact current formal adapter regression: 10/10
- exact current bootstrap adversarial: 3/3
- exact current integration regression: 20/20
- exact current detector-local identity regression: 2/2
- exact current formal-SUT-equivalent replay: 14/14

Historical Recovery V2 / historical frozen 67/67 remain supportive only and were not counted as current fresh execution.

## Final current-head blob revalidation

Immediately before this successor verdict, `main` was fixed to verification snapshot:

`6bed94ed5a21bbbfc95afbb1b281fc5b590aa77e`

Every source blob pin recorded by V3 `EXECUTION_RESULT.json` was re-read at that exact snapshot and matched byte-for-byte by Git blob SHA. Therefore **14/14 tested source pins are current and there is no runtime/SUT drift requiring a rerun**.

Exact verified pins:

- `product/alpha/wof_alpha_real_worker.js` = `b7f4506fc90b681ede059df5ad3316e665c6f15e`
- `product/alpha/wof_alpha_hud.js` = `50d944c451ac94b114e4f86441aeae8ad6b25c78`
- `product/alpha/wof_alpha_player_head_warning.js` = `af7f2359514dc6f86f74fac0c47858e8a6acf107`
- `product/alpha/wof_alpha_bootstrap.user.js` = `5aed15ff14aa39d95eade187cefb63dbd00848e6`
- `product/alpha/wof_alpha_loader.js` = `66aee09fc2dd009c2f295d2092f3129548605efb`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py` = `1a5c6a255468c096ddd5df79993851e4d41e23cb`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/adapter_test.py` = `824323123cef3d736efb0d8152264303a59d14a9`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs` = `4b2b2eccb83e16e149a6ddd4f36c438c325c50b9`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/detector_local_identity_test.mjs` = `4140d22114a6e10a8cef345f388b0b479dea1f5b`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/formal_integration_qa_sut.mjs` = `46c36dca6e906b8134dda76068ada2b3aaedff5a`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/formal_integration_qa.mjs` = `4eaa6c6f24d885a3036391bc8bcd20a1f2230a91`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/expected_outcomes.json` = `f5bed29cc31f57288f2f17f0b0549322e5a8a510`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` = `ec9d27bfe26557a11187a23853893b898a3366d1`
- `parallel/PYLAUNCH/wof_launcher/probe.py` = `789a6849b826b35542b22d56a4d2ca3628d285a1`

The commits after the V3 execution matrix did not change any of these exact tested blobs. PM/result/claim/endurance/proof-tooling commits do not invalidate the tested runtime under the Recovery V4 rule.

## Contract coverage recovered from raw V3 evidence

### Detector-local World 921031 identity / same-targetId replacement

`DETECTOR_LOCAL_IDENTITY_RESULT.json` is PASS 2/2 and proves:

- production source requires detector-local SHA-256;
- same-`targetId` replacement with a golden Discovery assertion fails closed on the fresh local hash.

The current worker execution matrix also covers the exact 1 MiB CPU-logical World 921031 SHA-256 contract:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.

### Generation / epoch / stale authority

The fresh worker, player-head transport, adapter, integration and formal-SUT runs cover:

- session / pair-generation / pair-nonce / runtime-epoch isolation;
- stale completion rejection after revoke/rebind;
- generation rebind;
- runtime replacement / runtime-epoch reset;
- Worker replacement/reinstall;
- disconnect/reconnect;
- foreign pair rejection;
- old completion cannot clear or mutate a fresh slot.

The current player-head spatial publication is accepted only after current gate completion and does not weaken generation/epoch authority.

### HUD warning authority

The current HUD adversarial run proves:

- all inbound kinds are filtered to the exact current pair;
- only semantic `state` refreshes warning lastRx;
- spatial data cannot create warning semantic state;
- render requires fresh semantic state;
- anchored warning binds semantic state epoch/sample;
- diag/reset revoke both state and spatial authority;
- warning count is based on semantic state freshness rather than spatial traffic.

Thus the current player-head/enemy-head HUD additions do not widen warning authority or bypass formal binding.

### Cadence / stale boundaries

Fresh formal-SUT and player-head transport evidence covers exact boundaries:

- heartbeat: 249 ms does not publish; 250 ms publishes;
- stale visibility: 1500 ms remains visible; 1501 ms is stale/hidden;
- player-head spatial freshness: 80/81 ms boundary;
- one detector tick in flight;
- queue depth remains 0;
- skipped ticks do not produce catch-up bursts.

### Safety / gameplay unaffected

Fresh formal-SUT safety is exact:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `workerReplacement=false`
- `blobRewrite=false`
- `gamePostMessageControl=false`
- `heapWrites=false`
- `assistMode=false`

Bootstrap/transport failure remains fail-closed for warning authority and fail-open for gameplay: game Worker is untouched and gameplay remains playable.

## Raw result paths

- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3/EXECUTION_RESULT.json` — 85/85 aggregate
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3/ADAPTER_RESULT.json` — 10/10
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3/INTEGRATION_RESULT.json` — 20/20
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3/DETECTOR_LOCAL_IDENTITY_RESULT.json` — 2/2
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3/FORMAL_SUT_RESULT.json` — 14/14

## Recovery disposition

- runtime/SUT blob drift: **NO**
- affected current-head rerun required: **NO**
- production modified: **NO**
- formal/PYLAUNCH/Recorder/OneClick implementation modified: **NO**
- Browser/WOF launched: **NO**
- old V3 canonical claim mutated: **NO**

The historical V3 canonical/stage claims remain `ACTIVE` only because the original worker was interrupted after producing durable execution evidence. For release gating, they are explicitly **superseded by this Recovery V4 successor PASS**.

## Release-gate handoff

Owner OneClick Current-HEAD Release Refresh V3 previously stopped `WAITING_GATE` because no durable formal real-adapter fresh-QA successor certified current `real_worker=b7f450...` / `HUD=50d944...`.

This result is that successor gate. Owner OneClick V3 may now re-read its other hard gates and retry candidate generation using this Recovery V4 PASS as the current formal real-adapter integration QA gate. This result does not itself claim that all other release gates are green and does not generate or mutate the OneClick package.

## Stop condition

**PASS — ALPHA FORMAL REAL-ADAPTER INTEGRATION CURRENT-HEAD FRESH QA V3 RECOVERY V4 — CURRENT RELEASE RUNTIME VERIFIED / V3 INTERRUPTION SUPERSEDED**
