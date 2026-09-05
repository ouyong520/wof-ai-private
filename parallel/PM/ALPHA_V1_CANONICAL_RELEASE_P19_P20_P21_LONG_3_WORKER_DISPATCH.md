# Alpha V1 Canonical Release — P19 / P20 / P21 Long 3-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

Purpose: keep the final Alpha V1 release path implementation-first while using three genuinely independent long-running workers.

## Slot 1 — P19

Continue the already ACTIVE `ALPHA_V1_PRODUCT_TAKEOVER_P19_FINAL_CANONICAL_CANDIDATE_REBUILD_ATTESTATION` ownership exactly as claimed. Do not create a new claim or recovery. P19 owns final candidate rebuild/attestation and final package pointer generation. It must not move `alpha-live`.

Authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P19_FINAL_CANONICAL_CANDIDATE_REBUILD_ATTESTATION_START_PROMPT.md`

## Slot 2 — P20

Continue the already ACTIVE `ALPHA_V1_PRODUCT_TAKEOVER_P20_OWNER_VISUAL_CONFIRMATION_ALPHA_LIVE_PROMOTION_GATE` ownership exactly as claimed. Do not create a new claim or recovery. P20 owns Owner visual receipt, promotion plan, CAS/fast-forward guarded apply contract and release UX. It must not actually move `alpha-live` in worker execution.

Authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P20_OWNER_VISUAL_CONFIRMATION_ALPHA_LIVE_PROMOTION_GATE_START_PROMPT.md`

## Slot 3 — P21

New long task: `ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS`.

P21 solves the pre-promotion acceptance circular dependency: run the exact P19 candidate from an ephemeral immutable staging checkout, invoke the existing acceptance chain, and prove the permanent W1 managed repo / `alpha-live` ref remain unchanged. It owns only the isolated staging harness area and must not cross P19/P20/W3/P18/P15 ownership.

Authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS_START_PROMPT.md`

## Shared safety / cadence

- Alpha Owner-visible product only.
- No Collector / Unified Collector / Training Farm / 10训 scope.
- Implementation first; only focused self-checks during these tasks.
- No broad Fresh QA or repeated regression workers.
- No screenshot/template/world-projection production coordinate fallback.
- No guessed renderer addresses.
- `readOnly=true`, `ramWrites=0`, `inputInjection=false`.
- No worker may move `alpha-live` in this dispatch.
- P19/P20 active claims are not to be duplicated, recovered, or stolen.
- P21 performs normal dedup-v2 create-only claim/stage flow before implementation.
- Terminal workers write their specified RESULT.json/RESULT.md and final `WORKER_RESULT ...` commit.

The remaining external product gate after repository finalization is still one bounded W3 normal-play qualification plus one simple Owner visual confirmation. Repository implementation must not fabricate either.
