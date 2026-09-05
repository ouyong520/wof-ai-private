# Alpha V1 Final Acceptance — P29 Live Evidence Repair — Long 1 Worker Dispatch

Status: ACTIVE DISPATCH AUTHORITY

This dispatch supersedes the P25-terminal-then-live dispatch because P25 is now terminal COMPLETE and the first real Owner final-staging run exposed a concrete repository-side live-evidence contract defect.

## Worker allocation

Use exactly one Worker for the next repository step:

- Worker 1: `ALPHA_V1_PRODUCT_TAKEOVER_P29_FINAL_LIVE_EVIDENCE_CONTRACT_REPAIR`
- START prompt: `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P29_FINAL_LIVE_EVIDENCE_CONTRACT_REPAIR_START_PROMPT.md`
- dedupKey: `alpha.v1.product-takeover.final-live-evidence-contract-repair-v1`
- claim mode: NEW DEDUP-V2 EXCLUSIVE CLAIM AFTER PREFLIGHT

Do not occupy additional workers with filler. The W3 capture/analyzer and P16 staging-readiness defects are one coherent final-live evidence seam and should be repaired/tested together to avoid conflicting ownership.

## Current truth

- P25: terminal COMPLETE / integrationReady=true.
- P27: terminal COMPLETE.
- P28: terminal COMPLETE / integrationReady=true.
- P26: historical terminal BLOCKED; never reopen/recover.
- first real Owner staging: `FAILED_EVIDENCE_MISMATCH`; W3 `REJECTED`; P16 not exact-world/runtime ready; no visual acceptance; no promotion; alpha-live unchanged.
- final Owner live gate: BLOCKED until P29 repairs the repo-side contract.

## P29 acceptance boundary

P29 repairs false W3 rejection/epoch-stamping consistency plus staged P16 readiness/timing and the concrete maintained P1 binding defect if it is the reason P16 cannot become ready. It must preserve the direct renderer-proof truth boundary: structural-only evidence may become truthful `INCONCLUSIVE`, never fabricated `PASS`.

No real game run is required from the Worker. After P29 terminal COMPLETE and PM validates the durable tested candidate, PM may authorize exactly one fresh Owner bounded live run using the already-restored local environment.

Do not reinstall global Python, modify system PATH, reset browsers, delete the existing project venv, or redownload dependencies without a concrete missing-component reason.
