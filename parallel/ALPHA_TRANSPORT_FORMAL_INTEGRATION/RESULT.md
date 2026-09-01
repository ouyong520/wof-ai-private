# Alpha Formal Real-Adapter Integration Recovery V2 Result

Stage: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2`

Status: **PASS**

Repository status: **ALPHA FORMAL REAL-ADAPTER INTEGRATION READY — READY FOR FRESH INTEGRATION QA**

Owner action: **NO**

## Recovery completed

The V1 integration was recovered against the current repository and current PYLAUNCH interfaces. During recovery, an independent adversarial review identified a concrete P1 TOCTOU: Discovery could accept the exact World 921031 SHA, then the runtime/execution context could be replaced under the same `targetId` before formal observer install, while the old implementation trusted a constant launcher-side golden assertion.

The recovery fixes that authority gap:

- `product/alpha/wof_alpha_real_worker.js` now independently locates the current 1 MiB CPU-logical ROM candidate inside the installed native Worker runtime and computes a fresh Web Crypto SHA-256 at observer installation.
- The observer fails closed unless that detector-local digest equals exactly `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62` and the current RAM/self-index sanity also passes.
- `real_adapter.py` carries the Discovery SHA as measured provenance, not as a substitute for local proof, and does not accept the observer until its current `identity.sha256` and identity signature both match the exact World 921031 authority.
- Same-`targetId` runtime replacement between Discovery and install is now deterministically rejected.
- Existing session / pair-generation / pair-nonce / runtime-epoch authority, strict rebind revocation, stale-completion rejection, one-in-flight/no-catch-up behavior, and disconnect fail-closed semantics remain intact.

## Deterministic verification

| Gate | Result |
|---|---:|
| detector-local identity TOCTOU regression | **2 / 2 PASS** |
| formal adapter regression | **10 / 10 PASS** |
| formal integration regression | **20 / 20 PASS** |
| stale in-flight generation regression | **5 / 5 PASS** |
| reference implementation selftest | **8 / 8 PASS** |
| frozen Safe Transport consumer gate | **67 / 67 PASS** |
| prepared fresh-integration-QA SUT seam preflight | **14 / 14 PASS** |

The prepared 14-case harness run is a SUT-seam preflight only. It proves that the current integration exposes the required fresh-QA seam and satisfies those expected observations in deterministic replay; it does **not** claim or replace a later independent fresh integration-QA endorsement.

Relevant RC4/RC5 behavior is covered by the current formal integration tests, the 1500/1501 ms stale and 249/250 ms heartbeat checks, Chinese fail-closed status coverage, the RC5 game-unaffected bootstrap failure case, and the frozen existing-regression preservation vectors.

## Safety invariants

All verified exact:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `workerReplacement=false`
- `blobRewrite=false`
- `gamePostMessageControl=false`
- `heapWrites=false`
- `assistMode=false`

No game RAM writes, gameplay input injection, Worker replacement, Blob Worker rewrite, or gameplay command/control path was introduced.

## Current-interface recheck

Before finalization, the recovery re-read the current PYLAUNCH interfaces. `cdp.py` remains read-only; `discovery_v2.py` still explicitly treats `targetId` as non-authoritative across runtime/execution-context generations and clears identity authority per discovery generation; `probe.py` still uses the exact full 1 MiB CPU-logical SHA-256 World 921031 identity gate. The formal adapter is compatible with those current interfaces.

Machine-readable evidence: `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/result.json`

**ALPHA FORMAL REAL-ADAPTER INTEGRATION READY — READY FOR FRESH INTEGRATION QA**
