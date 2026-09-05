# Alpha V1 Final Acceptance — P25 / P26 Long 2-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

This dispatch replaces revision 13 after P22/P23/P24 reached terminal COMPLETE.

## Worker 1 — P25 Final Acceptance Composite Capture Integration

- stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION`
- dedupKey: `alpha.v1.product-takeover.final-acceptance-composite-capture-integration-v1`
- prompt: `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_START_PROMPT.md`
- RESULT JSON: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_RESULT.json`
- RESULT MD: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_RESULT.md`

Mission: wire the already-complete P22/P24 passive analyzers into the exact P21/P17 staged acceptance session so one bounded live run later automatically produces dynamic-state and temporal-continuity evidence without manual JSON/coordinate handling.

## Worker 2 — P26 Final Acceptance Session Provenance Chain

- stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN`
- dedupKey: `alpha.v1.product-takeover.final-acceptance-session-provenance-chain-v1`
- prompt: `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN_START_PROMPT.md`
- RESULT JSON: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN_RESULT.json`
- RESULT MD: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN_RESULT.md`

Mission: build deterministic chain-of-custody/session binding across P19/P21/W3/P16/P18/P22/P24/P17/P20/P23 so evidence from different candidates or runtime sessions can never be accidentally combined into acceptance.

## Parallelism / ownership

The tasks are intentionally independent:
- P25 owns new composite capture/orchestration files, preferably under `parallel/OWNER_ACCEPTANCE_COMPOSITE/`.
- P26 owns new provenance/session-chain files, preferably under `parallel/OWNER_ACCEPTANCE_PROVENANCE/`.

Both consume existing completed authorities read-only. Neither may steal or rewrite W3/P16-P24 ownership, move `alpha-live`, modify the permanent W1 updater/setup, invent coordinates/actor identity, run real WOF, or fabricate visible PASS.

Implementation-first testing cadence applies: complete the bounded module, run only minimum focused self-checks, then write the specified terminal RESULT files.

After P25/P26, no further repository implementation should be invented merely to keep workers busy. The remaining intended path is the single real W3/P21/P17/P22/P24 acceptance run -> P20 Owner YES/NO -> guarded promotion -> P23 post-promotion close verification.
