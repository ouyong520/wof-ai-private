# Alpha Formal Integration Adversarial Review Result

Stage: `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1`

Status: **BLOCKED — P1**

## Precise blocker

`P1 — detector-local exact World 921031 identity is not freshly verified at formal observer install, so stale Discovery identity can survive a same-targetId runtime/execution-context replacement and grant warning authority to an unsupported runtime.`

The adapter first accepts Discovery V2's golden SHA, but later writes a constant `GOLDEN_SHA` into `launcherIdentitySha`. The installed Worker treats that constant plus RAM/self-index shape as sufficient local identity and emits a fixed golden `identitySignature` without hashing the current runtime's ROM. Current PYLAUNCH explicitly states that `targetId` is not a runtime/execution-context generation token, so the Discovery-to-install gap is an authority TOCTOU boundary.

Exact deterministic repro:

```bash
node parallel/ALPHA_FORMAL_INTEGRATION_REVIEW/repro_detector_local_identity_tocou.mjs
```

Detailed finding and repair acceptance criteria:

`parallel/ALPHA_FORMAL_INTEGRATION_REVIEW/CURRENT_HEAD_FINDINGS.md`

Pinned vulnerable blobs:

- `product/alpha/wof_alpha_real_worker.js` — `0088fcf60004cc8b773cff8b1f186cfe46e4572a`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py` — `6fbf569d9a9ef46a7502b1b979096cf757e8b105`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` — `ec9d27bfe26557a11187a23853893b898a3366d1`

Implementation recovery claim was still `ACTIVE` at blocker confirmation. Per review-lane stop rule, this review stops on this one concrete P1 and does not continue into lower-priority findings or modify `product/alpha/**`.

Owner action: **NO**.
