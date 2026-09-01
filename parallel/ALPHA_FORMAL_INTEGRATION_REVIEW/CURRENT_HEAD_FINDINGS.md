# Alpha Formal Integration Adversarial Review — Current HEAD Findings

Stage: `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1`
Reviewed at UTC: `2026-09-01T16:12:35Z`

Implementation lane state at stop: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2 = ACTIVE`.

Pinned reviewed blobs:

- `product/alpha/wof_alpha_real_worker.js` blob `0088fcf60004cc8b773cff8b1f186cfe46e4572a`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py` blob `6fbf569d9a9ef46a7502b1b979096cf757e8b105`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` blob `ec9d27bfe26557a11187a23853893b898a3366d1`
- `product/alpha/wof_alpha_bootstrap.user.js` blob `5aed15ff14aa39d95eade187cefb63dbd00848e6`

## P1 blocker — detector-local exact identity is not freshly verified at observer install

The formal adapter correctly requires the Discovery V2 result to report the golden World 921031 SHA before binding. However, after that admission check it does **not** carry immutable fresh identity evidence into the detector or re-probe exact identity at detector install time.

Current `real_adapter.py` creates the Worker binding with:

```python
"launcherIdentitySha": GOLDEN_SHA
```

That is a constant assertion, not a fresh detector-local measurement of the execution context receiving the observer.

Current `wof_alpha_real_worker.js::localIdentity()` accepts that constant plus module/RAM shape and P1/P2/P3 self-index values. It does not locate/hash the current ROM and does not compute a fresh SHA-256 before returning `ok:true` and the fixed `IDENTITY_SIGNATURE`.

This is incompatible with current PYLAUNCH Discovery V2 authority semantics. `discover()` explicitly documents that a `targetId` is **not** a browser/runtime/execution-context generation token and that accepted exact identity authority must not be carried across generations.

### Adversarial sequence

1. Discovery V2 observes target `worker-X` while runtime A is exact World 921031 and returns the golden SHA.
2. Before Alpha's later CDP attach/eval installs the observer, runtime/execution context B replaces A while retaining/reusing the same target identity surface.
3. Alpha still injects `launcherIdentitySha = GOLDEN_SHA` because the binding value is a constant derived from the accepted configuration, not a fresh detector-local hash.
4. Runtime B only needs the expected heap/RAM shape and P1/P2/P3 self-index values to make `localIdentity()` return `ok:true`.
5. The observer reports the fixed golden `identitySignature`, and `real_adapter.py` accepts that status.
6. State envelopes from runtime B then carry a fresh pair/session/generation/nonce and pass the page transport gate.

Result: an unsupported/non-921031 runtime can obtain current warning publication authority during the Discovery-to-install TOCTOU window.

This violates the required detector-local identity authority, runtime replacement fail-closed behavior, and unsupported identity fail-closed semantics.

## Deterministic repro

Fixture:

`parallel/ALPHA_FORMAL_INTEGRATION_REVIEW/repro_detector_local_identity_tocou.mjs`

Run from repository root:

```bash
node parallel/ALPHA_FORMAL_INTEGRATION_REVIEW/repro_detector_local_identity_tocou.mjs
```

The fixture executes the current production Worker source in a fake native-Worker scope containing only:

- a valid RAM base;
- the three expected self-index values `0/4/8`;
- no World 921031 ROM image and no fresh ROM SHA-256 evidence;
- a binding containing the constant golden launcher SHA.

Current vulnerable code reaches a running observer with `identity.ok=true` and the golden `identitySignature` even though `identity.sha256` is absent. The fixture prints `BLOCKER_REPRODUCED` when this condition exists; it is intentionally shaped to fail once detector-local exact identity is fixed.

## Existing regression gap

Current formal integration regressions check:

- pair/session/generation/nonce authority;
- tick revocation;
- runtime epoch inequality;
- Worker replacement teardown;
- discovery-side wrong-SHA rejection;
- exposed `identitySignature` and safety fields.

They do not inject a runtime/execution-context replacement **between** Discovery identity acceptance and observer installation, and they do not require the installed detector to return a freshly computed exact ROM SHA from its own current execution context.

## Required fix acceptance

A repair must ensure the exact World 921031 identity used for warning authority is fresh and detector-local to the installed runtime generation. Acceptable implementations may differ, but the proof must establish all of the following:

- no constant/stale launcher assertion can substitute for detector-local exact identity;
- the installed observer computes or consumes generation-bound exact identity evidence that cannot survive runtime/execution-context replacement;
- same-targetId runtime replacement between Discovery and install fails closed;
- the adapter verifies fresh detector-local evidence before page warning authority becomes usable;
- the adversarial fixture no longer reaches a running authoritative observer;
- fresh independent integration QA adds this TOCTOU case.

No `product/alpha/**` files were modified by this review lane.
