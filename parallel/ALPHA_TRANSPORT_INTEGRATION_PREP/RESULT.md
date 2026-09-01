# WOF Alpha Safe Transport — Real Adapter Integration Prep Result

Date: 2026-09-01  
Stage: `ALPHA_TRANSPORT_REAL_ADAPTER_PREP_V1`  
Status: **ALPHA TRANSPORT REAL ADAPTER PREP READY**

## Result

A durable, isolated real-adapter preparation package now defines the bounded boundary between current PYLAUNCH/real runtime authority and the already-complete Alpha Safe Transport reference implementation.

No current live component or product file was modified by this stage. The package is confined to `parallel/ALPHA_TRANSPORT_INTEGRATION_PREP/**` plus the mandatory PM claim.

## Deliverables

1. **Discovery adapter contract**
   - consumes final authoritative PYLAUNCH Discovery V2 `TargetChoice`, not private topology helpers;
   - accepts current `worker/shared_worker/service_worker` target kinds and treats Worker URL shape as diagnostic only;
   - requires exact page config, one current pair, module+heap readiness, exact World 921031 authority, and explicit connection/page/Worker lifecycle epoch;
   - ambiguity/non-authoritative discovery fails closed for warnings.

2. **Native Worker runtime adapter contract**
   - fresh epoch-bound launcher identity, detector-local identity, install/status/stop interfaces;
   - observer authority is scoped to one runtime epoch;
   - replacement/reload/reconnect invalidates old authority;
   - safety remains read-only/no-input/no-replacement.

3. **Alpha detector adapter contract**
   - consumes release-pinned canonical `product/alpha/wof_alpha_core.js` through the existing reference detector adapter;
   - does not duplicate warning predicates;
   - state/warning/diag/stale authority remains the frozen reference behavior.

4. **Page/HUD contract**
   - page-owned monotonic generation plus fresh nonce;
   - old generation/nonce loses authority immediately;
   - fixed first-release HUD output is frozen independently from future player-head placement.

5. **Deterministic fixture/selftest package**
   - valid exact pair;
   - wrong World;
   - missing WASM/heap;
   - unsafe identity;
   - stale generation;
   - Worker runtime epoch replacement;
   - reconnect/rebind;
   - cross-tab/session isolation;
   - fixed HUD output vs future anchor separation;
   - canonical Alpha core consumption;
   - existing 67-vector reference result remains mandatory;
   - current-interface drift verification.

6. **Formal integration wiring plan**
   - exact expected later PYLAUNCH/Alpha files and adapter responsibilities are recorded in `INTEGRATION_WIRING_PLAN.md`;
   - formal integration is reduced to controlled adapter wiring rather than topology/identity/warning redesign.

7. **Current-HEAD drift baseline**
   - exact Git blob SHAs for all consumed reference/mock/PYLAUNCH/Recorder/Live Proof/Alpha interfaces are pinned in `DRIFT_BASELINE.json`;
   - `drift_check.mjs` recomputes Git-compatible blob SHAs from a checkout and fails on drift.

## Reuse of existing transport semantics

The prep package retains the existing semantic oracle:

```text
reference selftest: 8/8 PASS (upstream durable result)
reference acceptance: 67/67 PASS (upstream durable result)
mock vectors blob: 5a0cbe2ccfcf7eb6e875552f56748f736722c14d
canonical Alpha core blob: 267a44190744b6848b0685712c3d5572627d3a8a
World 921031 SHA-256: 5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
readOnly=true
ramWrites=0
inputInjection=false
workerReplacement=false
blobRewrite=false
```

No new/weaker vector catalog or duplicate detector predicate was introduced.

## Current drift / prerequisite findings

The prep layer is interface-compatible with the current PYLAUNCH Discovery V2 final-result shape. It intentionally does not depend on its unstable/private topology helpers or Worker URL heuristics.

Current formal-integration/release gates remain explicit:

- PYLAUNCH parentFrame authority fix: development complete, **fresh independent QA still required**;
- Unified Live Proof freshness fix: implementation + 43 regression/adversarial checks complete, **fresh independent QA still required**;
- WOF-052L Recorder hardening: fresh QA currently **BLOCKED** on the live/live shared-Worker-before-poll P0 and reused-target-id stale identity P1; current implementation blobs were unchanged at drift review;
- future player-head HUD anchor: non-blocking for fixed first-release warning semantics.

These gates are not defects in this isolated prep package and are not bypassed by it.

## Verification available in this package

Repository checkout command:

```text
node parallel/ALPHA_TRANSPORT_INTEGRATION_PREP/selftest.mjs
```

The selftest executes the prepared adapters against the existing reference runtime/canonical Alpha core and verifies the committed 67-vector result plus the pinned current-tree drift baseline. `RUN_PREP_SELFTEST.cmd` is the Windows entry.

The authored JavaScript files were syntax-checked during preparation. An isolated contract/runtime-shape smoke executed 11 behavior vectors and passed **11/11**; the committed default `selftest.mjs` adds the checkout-wide Git-blob drift vector as its 12th check and runs against the actual frozen reference modules/canonical Alpha core present in the checkout. A network checkout was not used as a substitute for GitHub source authority; the final baseline was built by re-reading current GitHub HEAD and exact content blob SHAs.

## Owner intervention

`你现在需要操作：NO`

## Stop condition

**ALPHA TRANSPORT REAL ADAPTER PREP READY**
