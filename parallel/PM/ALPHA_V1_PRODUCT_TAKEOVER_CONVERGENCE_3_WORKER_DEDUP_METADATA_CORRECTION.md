# Alpha V1 Product Takeover — W1/W2 Dedup-v2 Metadata Correction

Status: **PM AUTHORITY CORRECTION**

Parent dispatch:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_CONVERGENCE_3_WORKER_DISPATCH.md`

Reason:
The parent dispatch correctly defined W1/W2 scope and file boundaries, but did not publish dedicated executable start prompts containing the mandatory dedup-v2 metadata block. Under `parallel/PM/STAGE_DEDUP_GUARD.md`, workers must fail closed and may not invent these fields.

Therefore the PM authorizes these dedicated start prompts as the executable authority for the same W1/W2 logical work:

## W1

`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP_START_PROMPT.md`

Metadata:

- stageId: `ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP`
- dedupProtocol: `v2`
- dedupKey: `alpha.v1.product-takeover.owner-permanent-live-test-bootstrap`
- dedupMode: `exclusive`

## W2

`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W2_MAINTAINED_PRODUCTION_HUD_FIXED_DRAW_SMOKE_START_PROMPT.md`

Metadata:

- stageId: `ALPHA_V1_PRODUCT_TAKEOVER_W2_MAINTAINED_PRODUCTION_HUD_FIXED_DRAW_SMOKE`
- dedupProtocol: `v2`
- dedupKey: `alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke`
- dedupMode: `exclusive`

This correction does not create a new Alpha version, umbrella, or recovery lineage. It only repairs missing PM scheduling metadata so the already-authorized W1/W2 work can lawfully contend for canonical ownership.

Workers previously stopped with `DEDUP_V2_W1_METADATA_MISSING` or the equivalent W2 missing-metadata blocker should re-read latest `main` and resume from the relevant dedicated START_PROMPT. They must still perform the normal create-only canonical claim and post-create token verification before any task work.

W3 authority remains unchanged: continue the already ACTIVE `alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2`; do not create another recovery.
