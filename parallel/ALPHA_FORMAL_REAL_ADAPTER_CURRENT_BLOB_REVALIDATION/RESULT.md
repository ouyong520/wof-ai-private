# Alpha Formal Real-Adapter — Current Alpha Blob Fresh Revalidation Result

Stage: `ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION_V1`

Status: **PASS — ALPHA FORMAL REAL-ADAPTER CURRENT-BLOB REVALIDATION — FRESHNESS GATE CURRENT**

Owner action: **NO**.

This was an independent repository-only QA. No Alpha/Formal implementation was modified and no Browser/WOF process was launched.

## Current-HEAD / dedup / freshness

- claim-start HEAD: `25b664fea50a593cd46a8aca1ae7259351b8687c`
- atomic claim commit: `9c8d690624413e06853bf5d11b2d11ff5b530bea`
- final pre-result inspection HEAD: `8110c539452288244763197478bd5c0b7c6aab29`
- fresh inspection evidence: `parallel/ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION/INSPECTION.json`
- no equivalent current-blob Formal claim/result existed when this stage acquired its claim.

The historical Formal Recovery V2 PASS pinned an older worker (`9c63a2c6a185ead8406487edd10038c035d41623`) and older HUD (`f41838c760ee9f7c40f3c91c71687e72ba740803`). It was used only as the accepted invariant baseline, not as freshness proof for this result.

## Audited current production blobs

| Path | Blob |
|---|---|
| `product/alpha/wof_alpha_real_worker.js` | `924d02eb575d1031b168b3bb7450c34107447c85` |
| `product/alpha/wof_alpha_hud.js` | `b6f9cbf23ec1c00fe969aa2a2b59ad5e0d5433f4` |
| `product/alpha/wof_alpha_bootstrap.user.js` | `5aed15ff14aa39d95eade187cefb63dbd00848e6` |
| `product/alpha/wof_alpha_loader.js` | `b1d2bd5cc3f5e4e7a3bed084d6d35ea71489717b` |
| `product/alpha/wof_alpha_core.js` | `267a44190744b6848b0685712c3d5572627d3a8a` |
| `product/alpha/wof_alpha_enemy_target_labels.js` | `3f6f4410376756e6935a4236e40e76574b289169` |
| `product/alpha/wof_alpha_enemy_head_projection.json` | `8de57739818503a0e14702d2fa0bb4eba58228d2` |
| `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py` | `1a5c6a255468c096ddd5df79993851e4d41e23cb` |

Current Formal QA seam/test blobs also remain:

- `formal_integration_qa_sut.mjs` — `46c36dca6e906b8134dda76068ada2b3aaedff5a`
- `detector_local_identity_test.mjs` — `4140d22114a6e10a8cef345f388b0b479dea1f5b`
- `integration_test.mjs` — `4b2b2eccb83e16e149a6ddd4f36c438c325c50b9`

Fresh pre-result rechecks confirmed the worker, HUD, bootstrap, loader, core, and real-adapter blobs still matched these pins after concurrent QA-document commits.

## Required revalidation results

### 1. Detector-local exact World 921031 identity — PASS

The current worker still performs detector-local authority measurement rather than trusting a launcher constant:

- locates exactly one 1 MiB CPU-logical ROM candidate using reset-vector/dispatch sanity;
- requires current Worker Web Crypto SHA-256;
- requires exact digest `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- validates the current CPS RAM window and exact P1/P2/P3 self indexes `0/4/8`;
- returns fail-closed identity state on mismatch.

`real_adapter.py` separately requires the installed current worker identity object, SHA, identity signature, read-only fields, and `queueDepth=0` before accepting the observer.

### 2. Same-targetId runtime/execution-context replacement — PASS

`FormalRealAdapter.step()` invokes Discovery V2 with a fresh `identity_cache={}` on every step. Existing authority survives only if the current page/worker target IDs still match *and* current page/worker status contains the exact current pair/session/generation/nonce/runtime epoch plus fresh detector-local identity and safety fields.

If a runtime/execution context is replaced under the same targetId, stale launcher evidence alone is insufficient: a missing/drifted worker status forces rebind, and the new observer must freshly pass worker-local SHA-256 identity again.

### 3. Pair / session / generation / nonce / runtime epoch — PASS

The current worker `validBinding()` remains exact over release/schema/transport, 32-hex session, pair nonce, positive generation, 32-hex runtime epoch, exact launcher identity SHA, and session-derived channel. `createTickAuthorityGate()` freezes session/generation/nonce/runtime epoch into each in-flight authority.

Bootstrap `matchesCurrentPair()` still accepts only the exact current session / transport / generation / nonce. Adapter current-authority checks independently require exact matching page and worker authority fields.

### 4. Late old in-flight completion — PASS

`gate.revoke()` disables the gate and clears `inFlight`; `finish()` rejects completion after revocation or any authority mismatch. Adapter rebind clears current authority first, resets old page warning authority, and requires the old observer to stop when the same Worker target remains addressable. A new page pair increments generation and receives a new random nonce/runtime epoch.

The marker additions did not add a second publication authority or a queue that can bypass this gate.

### 5. Disconnect / stale warning authority revocation — PASS

- adapter `revoke()` clears `self.current` and performs best-effort page reset / worker stop without creating replacement authority;
- bootstrap `resetPair()` increments generation, clears pair nonce, and calls HUD `transportReset()`;
- HUD `transportReset()` clears warning state and marker state;
- HUD `diag` clears warning state immediately and also clears marker state.

Gameplay remains fail-open while warning authority fails closed.

### 6. One-in-flight / no catch-up / queue-depth-zero — PASS

The current tick gate still rejects overlapping `start()` calls, increments `skippedTicks`, exposes `queueDepth: 0`, and contains no catch-up queue. The new marker channel is emitted only after the same detector tick's authority successfully finishes; it does not create an independent detector tick scheduler.

### 7. Warning heartbeat / freshness compatibility — PASS

Normal warning publication remains:

- immediate on warning-set change; or
- heartbeat when `sampledAt - lastPublishedAt >= 250` ms.

HUD warning freshness remains `STALE_MS=1500`. Only `kind==='state'` writes `lastMsg` / `lastRx`; stale warning display therefore still expires independently of marker traffic.

### 8. Marker channel remains decorative — PASS

The current worker publishes target metadata only as `kind: 'enemy-target-markers'`. The HUD receive path stores those messages only in `lastMarkerMsg` / `lastMarkerRx`; marker arrival does **not** modify warning `lastMsg`, warning `lastRx`, warning diagnostics, bootstrap pairing state, or adapter authority.

Bootstrap only changes warning/attach authority for exact-pair `state` or `diag`; `enemy-target-markers` is ignored for those transitions.

Therefore marker traffic cannot authorize, recover, or extend danger-warning authority.

### 9. Marker fields/payloads do not weaken adapter/transport authority — PASS

Worker marker envelopes use the same session / pair generation / pair nonce / runtime epoch authority envelope as state messages. HUD applies schema/session/`TRANSPORT.matches(m)` before accepting *any* message, including marker messages. Marker payload fields are not consulted by `real_adapter.py` admission or current-authority checks.

### 10. Current HUD pair checks / warning revocation — PASS

Current HUD still requires exact `TRANSPORT.matches(m)`. Warning freshness and marker freshness are separate (`1500 ms` vs `300 ms`). Diagnostic and transport reset paths revoke warning state regardless of marker state.

### 11. Read-only safety invariants — PASS

Current inspected contract remains:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `workerReplacement=false`
- `blobRewrite=false`
- `gamePostMessageControl=false`
- `heapWrites=false`
- `assistMode=false`

Bootstrap continues to leave the game Worker constructor untouched; Formal adapter contains no gameplay input-dispatch or heap-write surface.

### 12. Formal QA seam still targets current production — PASS

The current QA seam and integration test read these repository paths directly at runtime rather than embedding copied implementations:

- `product/alpha/wof_alpha_real_worker.js`
- `product/alpha/wof_alpha_bootstrap.user.js`
- `product/alpha/wof_alpha_hud.js`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py`

The detector-local identity regression likewise reads the current worker and real adapter. Therefore the seam has not drifted into a stale copied SUT after the marker-channel changes.

## Current projection state / marker activation

`product/alpha/wof_alpha_enemy_head_projection.json` remains:

- `verdict: UNPROVEN`
- `status: FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`

`loadEnemyHeadProjection()` accepts a profile only when the label helper validates an `IMPLEMENTATION_READY` proof. On the current blob, no usable projection profile is produced and `markerSnapshot()` returns null; target-head markers are therefore silent while normal danger-warning publication continues.

This repository QA does **not** convert synthetic or source inspection into Browser/WOF projection proof.

## Deterministic test execution

Fresh execution was attempted only to the point of validating execution prerequisites:

- Node available: `v22.16.0`
- repository checkout in the execution container: **absent**
- direct GitHub network probe: `git ls-remote https://github.com/ouyong520/wof-ai-private.git HEAD` -> `Could not resolve host: github.com`

Because the execution environment cannot obtain a private repository checkout, the following current-file tests were **not falsely reported as freshly executed**:

- `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs`
- `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/detector_local_identity_test.mjs`

Historical Recovery V2 logs were not reused as current execution proof. The PASS verdict is based on the fresh exact-current-blob repository inspection recorded in `INSPECTION.json`, which the start prompt permits when fresh deterministic execution is not possible.

## Concurrent Head Labels QA BLOCKED — release implication

During this revalidation, the independent `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V1` completed **BLOCKED** because the label helper coercively accepts malformed numeric-string `target7E` values (`"0"`, `"4"`, `"8"`) under a synthetically valid projection and can render a false decorative label.

That is a real Head Labels fail-closed defect and remains an independent release blocker. It does **not** constitute a Formal warning-authority breach on the audited current blobs:

- normal worker-produced `target7E` is numeric because it comes from `U16(...)`;
- the current projection profile is `UNPROVEN`, so current production marker publication is silent;
- marker receipt is isolated from warning freshness/authority;
- marker messages cannot pair the bootstrap or satisfy adapter authority.

Accordingly:

- **Formal Real-Adapter current-blob freshness gate:** **PASS / CURRENT**.
- **Alpha V1 overall release candidate:** **NOT READY**, because the separate Head Labels independent QA is BLOCKED and its fix requires fresh downstream revalidation on any changed release-consumed blobs.
- **Browser/WOF target-head projection acceptance:** still pending and not covered by this result.

## Ship-gate recommendation

Consume this result only as the current Formal authority/lifecycle/warning-freshness gate for the exact blob set above. Do **not** use it to override the Head Labels BLOCKED result, and do not reuse it after any subsequent change to the pinned worker/HUD/bootstrap/loader/core/real-adapter blobs without a fresh drift/revalidation check.

## Stop condition

**PASS — ALPHA FORMAL REAL-ADAPTER CURRENT-BLOB REVALIDATION — FRESHNESS GATE CURRENT**
