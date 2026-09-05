# Alpha V1 P12 — ACTIVE Claim New-Thread Reattach Continuation

Status: PM-authorized continuation of the existing ACTIVE logical task. This is not a new task and not a recovery.

Repository: `ouyong520/wof-ai-private`

## Existing ownership

- stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY`
- dedupKey: `alpha.v1.product-takeover.canonical-actor-generation-registry-v1`
- dedupMode: `exclusive`
- expected claimToken: `e31a17b35e9175681f7c7f26ff5af381`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.canonical-actor-generation-registry-v1.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY.json`
- original authority: `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY_START_PROMPT.md`
- current dispatch: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RUNTIME_P10_P12_P14_CONTINUATION_3_WORKER_V1.json`
- result JSON: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY_RESULT.json`
- result MD: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY_RESULT.md`

## Reattach procedure

1. Read latest `main` first.
2. Read the canonical claim and stage claim above.
3. Verify both are still `ACTIVE`, both contain exactly claimToken `e31a17b35e9175681f7c7f26ff5af381`, and both still point to the same P12 stage/dedupKey.
4. Do **not** create a new canonical claim.
5. Do **not** create a new stage claim.
6. Do **not** invent or request a recovery merely because this is a new chat.
7. If either claim is missing, not ACTIVE, or the token/identity differs, fail closed and report the exact mismatch; do not modify ownership.
8. After successful re-read verification, continue implementation under the original P12 START_PROMPT and current dispatch authority exactly as the existing logical worker.
9. Preserve the original file boundaries: do not edit P10 bridge/transport files, `alpha_runtime.py`, P11 HUD/product JS, W3 producer/capture/claims, or `alpha-live`.
10. Implementation first; minimum self-check only.
11. Finish by writing the original exact RESULT.json + RESULT.md and closing only the existing P12 claims with the same claimToken when the original task is truly terminal.

This document authorizes thread reattachment only. It does not change scope, dedup identity, ownership token, result paths, or acceptance criteria.
