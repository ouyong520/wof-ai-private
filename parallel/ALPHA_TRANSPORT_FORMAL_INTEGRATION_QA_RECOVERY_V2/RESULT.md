# Alpha Formal Real-Adapter Integration Fresh QA Recovery V2 — Result

Stage: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_RECOVERY_V2`

## Verdict

**PASS — ALPHA FORMAL REAL-ADAPTER FRESH QA RECOVERY V2 — READY FOR NEXT RELEASE GATES**

Owner action: **NO**.

This was an independent QA recovery for the abandoned V1 `ACTIVE` claim. No Alpha Transport / real adapter / worker implementation was modified.

## Current-HEAD audit / dedup disposition

- Claim-start main HEAD: `b9058081f283d109eac73777d3c9d39dda234427`.
- Recovery QA claim commit: `9a17afffc2a9fa457133e2eb7aaea94fffaaed39`.
- Final pre-result audit HEAD: `7000773ed13f542f66e6ad3b3a543f896c1d63da`.
- Original V1 fresh-QA claim remains historical `ACTIVE` with no durable result; this recovery stage did not rewrite it.
- `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2` is durably `COMPLETE` and hands off to fresh QA.
- No equivalent V1 PASS/BLOCKED result and no pre-existing Recovery V2 claim/result existed when this stage acquired its atomic claim.

The only commits added by this QA before finalization were its own claim and QA evidence. Final drift recheck confirmed the tested production blobs remained unchanged.

## Tested / audited current production blobs

- `product/alpha/wof_alpha_real_worker.js` — `9c63a2c6a185ead8406487edd10038c035d41623`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py` — `1a5c6a255468c096ddd5df79993851e4d41e23cb`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/formal_integration_qa_sut.mjs` — `46c36dca6e906b8134dda76068ada2b3aaedff5a`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/detector_local_identity_test.mjs` — `4140d22114a6e10a8cef345f388b0b479dea1f5b`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs` — `4b2b2eccb83e16e149a6ddd4f36c438c325c50b9`
- `product/alpha/wof_alpha_bootstrap.user.js` — `5aed15ff14aa39d95eade187cefb63dbd00848e6`
- `product/alpha/wof_alpha_hud.js` — `f41838c760ee9f7c40f3c91c71687e72ba740803`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` — `ec9d27bfe26557a11187a23853893b898a3366d1`
- `parallel/PYLAUNCH/wof_launcher/probe.py` — `789a6849b826b35542b22d56a4d2ca3628d285a1`
- `parallel/PYLAUNCH/wof_launcher/cdp.py` — `def308bed2a5609be1da26505a15d621395b66aa`

These are the same worker / adapter / PYLAUNCH interface blobs pinned by Recovery V2; the Recovery V2 regression fixture therefore still targets current production rather than a historical snapshot.

## Independent adversarial QA method

The recovery prompt explicitly allows an independent QA fixture/runner **or independent adversarial inspection**. This stage used a fresh current-source adversarial inspection and recorded the machine-readable vector matrix at:

`parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_RECOVERY_V2/INSPECTION.json`

Result: **14 / 14 independent inspection vectors PASS**.

Implementation-authored PASS counts were re-read only as supporting regression evidence and were not used as the sole basis for this verdict.

## Decisive findings

### 1. Historical detector-local identity TOCTOU is closed

The historical adversarial blocker was exact: Discovery could report the golden SHA, then the runtime/execution context could be replaced under the same `targetId`, while the old observer trusted a constant launcher-side golden assertion.

Current source no longer does that:

1. Discovery identity authority is explicitly generation-local; `discover()` clears the supplied identity cache each call and documents that `targetId` is not a runtime/execution-context generation token.
2. `real_adapter.py` carries the current Discovery SHA as measured provenance instead of substituting the constant golden SHA.
3. At observer install, `wof_alpha_real_worker.js` independently locates the current 1 MiB CPU-logical ROM candidate in the current Worker heap and computes a fresh Web Crypto SHA-256.
4. The Worker fails closed unless that current digest equals exactly `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62` and current RAM/self-index sanity is valid.
5. The adapter does not accept the installed observer merely because it reports `running=true`; it also requires the returned current detector-local identity object to be `ok`, carry the exact SHA and exact identity signature, and satisfy read-only safety fields.

Therefore the old sequence “golden Discovery evidence -> same-targetId replacement -> stale launcher assertion authorizes unsupported runtime” no longer grants warning authority.

**Historical `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1` BLOCKED is superseded for its recorded blocker by current successor implementation + this fresh QA.** The historical result remains untouched as required.

### 2. Runtime instance / state update lifecycle is fail-closed

`FormalRealAdapter.step()` performs fresh Discovery V2 and:

- revokes current authority and returns `warningAuthority=false` when discovery is unsupported/ambiguous;
- keeps an existing binding only when both the exact current page/Worker target IDs and live page/worker status still match the binding;
- otherwise performs a strict rebind.

The current-authority check requires the exact page session/pair generation/pair nonce plus Worker `running`, detector-local identity, runtime epoch, session, generation, nonce, `queueDepth=0`, and safety fields. A stale status object missing any of those exact properties cannot remain authoritative.

### 3. Rebind / Worker lifecycle preserves generation isolation

Before a new generation is established:

- current binding is cleared;
- same-page rebind requires old page warning authority to be provably reset;
- same-Worker rebind requires the old observer to be provably stopped;
- replacement Worker paths revoke page authority before best-effort cleanup of a possibly dead old Worker;
- the new binding receives a new random pair nonce and runtime epoch, while the page increments pair generation.

Inside the Worker, the tick-authority gate is immutable over session / pair generation / pair nonce / runtime epoch. `revoke()` disables the gate and clears in-flight state; a late old completion cannot publish or clear the fresh generation. One tick in flight / no catch-up / queue depth zero remains exact.

### 4. Disconnect / stale warning behavior remains safe

- Adapter disconnect / exception cleanup calls `revoke()` and does not create replacement authority.
- Bootstrap pair reset increments generation, clears pair nonce, and clears HUD authority.
- HUD accepts only the exact current transport pair.
- Worker heartbeat publication boundary remains `>=250 ms`.
- HUD freshness remains through `1500 ms`, with warning state stale after that boundary.

Gameplay remains fail-open while warning authority fails closed.

### 5. QA seam is tied to current production

The delivered formal QA SUT seam reads these repository files directly at runtime:

- real worker;
- RC5 bootstrap;
- HUD;
- real adapter.

It is not a separate copied implementation that could pass while production drifts. Its expected oracle covers rebind late completion, runtime epoch reset, Worker replacement, pair mismatch, disconnect/reconnect, 249/250 heartbeat, 1500/1501 stale behavior, one-in-flight/no-catch-up, identity rejection, Chinese owner status, safety, and bootstrap failure/gameplay-unaffected behavior.

## Safety invariants

Current inspected contract remains exact:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `workerReplacement=false`
- `blobRewrite=false`
- `gamePostMessageControl=false`
- `heapWrites=false`
- `assistMode=false`

No Owner Browser/WOF run was needed for this repository-side gate.

## Release-gate disposition

- **Formal Real-Adapter fresh QA gate:** **CLOSED / PASS**.
- **Historical Formal Integration adversarial blocker:** **SUPERSEDED by current successor implementation + this fresh QA**, without rewriting historical evidence.
- **True 5h endurance:** **UNBLOCKED TO A FRESH RERUN, but NOT already PASS**. The existing endurance result remains BLOCKED because it executed only ~0.417 h of the intended 5.417 h; this QA cannot fabricate the missing duration.
- **Current-head Alpha acceptance / release:** this QA removes the formal-integration independent-QA blocker, but does **not** by itself declare the global release complete. Acceptance prep remains a downstream consumer waiting for the remaining release gates, including a legitimate endurance completion and any other current-head PM gates.
- **Owner action:** **NO**.

## Stop condition

**PASS — ALPHA FORMAL REAL-ADAPTER FRESH QA RECOVERY V2 — READY FOR NEXT RELEASE GATES**
