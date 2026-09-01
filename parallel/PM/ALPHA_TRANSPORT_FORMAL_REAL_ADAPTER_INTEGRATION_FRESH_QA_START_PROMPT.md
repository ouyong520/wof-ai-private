# WOF Alpha — Formal Real-Adapter Integration Fresh QA

stageId: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_V1`

Priority: **P0/P1 Alpha release gate**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md` before any work.

## PM reason / current upstream

This is a fresh independent QA stage. It is **not** another implementation/recovery stage.

At PM reconciliation baseline `a31f8940e4a7be7b18e8ad13b0754e2c00676c38`:

- `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2` is `COMPLETE` but explicitly hands off `READY FOR FRESH INTEGRATION QA`;
- durable recovery result exists at `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/RESULT.md` and machine result at `result.json`;
- current production blobs are expected to remain:
  - `product/alpha/wof_alpha_real_worker.js` -> `9c63a2c6a185ead8406487edd10038c035d41623`;
  - `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py` -> `1a5c6a255468c096ddd5df79993851e4d41e23cb`;
- prepared independent oracle/harness exists under `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/**`;
- delivered real SUT seam exists at `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/formal_integration_qa_sut.mjs` (baseline blob `46c36dca6e906b8134dda76068ada2b3aaedff5a`).

The historical `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1` BLOCKED result must remain historical. Do **not** rewrite it to COMPLETE. This fresh QA is the superseding independent gate for its detector-local identity blocker.

## Dedup / claim

Before claiming, re-read latest `main` and all equivalent formal-integration QA/result claims.

If a newer independent result already certifies the same current production blobs and all required attacks below, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If an equivalent fresh-QA claim is ACTIVE, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_V1.json`

with `state=ACTIVE` and exact current `main` start commit.

## Upstream gate

Proceed only if Recovery V2 is COMPLETE and current source still exposes the real QA seam. If any production blob relevant to this gate changed after the recovery result, do not silently reuse prior evidence: re-pin current blobs and test current source, or stop with precise drift/blocker if the change invalidates the prepared oracle.

## Goal

Independently decide whether current HEAD closes the old Formal Integration blocker and is release-gate eligible.

Required decision points:

1. exact detector-local World 921031 identity is freshly measured at observer install, not inherited from Discovery;
2. exact 1 MiB CPU-logical SHA-256 is required: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
3. same-`targetId` runtime/execution-context replacement between Discovery and observer install fails closed;
4. stale completion after pair/session/generation/nonce/runtime-epoch/rebind cannot publish or clear current authority;
5. Worker replacement/reinstall revokes old authority;
6. disconnect/reconnect clears old warning authority;
7. one tick in flight / no catch-up / queue depth 0 remains exact;
8. heartbeat/stale boundaries remain 249/250 ms and 1500/1501 ms as contracted;
9. RC5 bootstrap/transport failure leaves gameplay path unaffected;
10. safety remains exact: `readOnly=true`, `ramWrites=0`, no input injection, no Worker replacement, no Blob rewrite, no game postMessage control, no heap writes, no assist mode.

## Required execution

Use the independent prepared oracle against the delivered real seam, not self-reported Recovery V2 PASS alone.

At minimum run/check current equivalents of:

- `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/formal_integration_qa.mjs --sut parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/formal_integration_qa_sut.mjs`;
- `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/detector_local_identity_test.mjs`;
- `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs`;
- current formal adapter regression/selftests;
- frozen Safe Transport consumer gate / stale-generation regression that the recovery claims to preserve.

Add fresh adversarial cases only where needed to ensure the QA is independent. In particular, do not accept a SUT seam that merely returns expected booleans while bypassing current production sources; verify the seam consumes the exact current worker/bootstrap/HUD/real-adapter files it declares.

Retain raw machine-readable output and pin exact SUT/production blobs.

## Read / write boundary

Read/test current repository code and frozen contracts.

Write only:

- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_FRESH_QA/**`;
- the dedicated stage claim above.

Do **not** modify:

- `product/alpha/**`;
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/**` production/integration implementation;
- PYLAUNCH / Recorder / Live Proof / Owner OneClick / HUDANCHOR lanes;
- historical adversarial-review claim/result.

If QA finds an implementation defect, stop BLOCKED with exact repro/evidence. Do not fix it in this QA lane.

## Downstream consumer

A PASS is consumed by:

- Alpha current-HEAD acceptance gate reconciliation;
- Owner OneClick final current-snapshot refresh decision;
- Release Freeze current-HEAD recheck.

## Drift rule

Immediately before finalizing, re-read `main`. If any tested production blob changed, the PASS is stale; rerun against the new exact blobs or stop with `BLOCKED — SUT DRIFT`.

PM-only/result-only commits that do not alter tested production blobs do not invalidate the decision, but record the distinction explicitly.

## Success stop

Only after independent fresh execution is green on exact current production blobs:

`PASS — ALPHA FORMAL REAL-ADAPTER INTEGRATION FRESH QA — RELEASE GATE CLOSED`

Update the claim to COMPLETE with result path/commit, tested HEAD, exact production/SUT blobs, pass counts, and explicit statement that the historical adversarial blocker is superseded by this fresh evidence.

Owner action: **NO**.

## Failure stop

On any current P0/P1 defect, missing real seam, invalid identity proof, same-targetId replacement acceptance, regression failure, or unresolvable SUT drift:

`BLOCKED — ALPHA FORMAL REAL-ADAPTER INTEGRATION FRESH QA — <precise blocker>`

Update the claim BLOCKED and preserve the first deterministic repro. Do not broaden scope.