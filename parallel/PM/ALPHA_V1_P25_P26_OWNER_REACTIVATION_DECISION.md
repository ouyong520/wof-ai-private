# Alpha V1 P25/P26 — Owner Reactivation Decision

Status: ACTIVE OWNER CORRECTION

The Owner has explicitly clarified that P25 and P26 are currently being worked on. This later decision supersedes `parallel/PM/ALPHA_V1_P25_P26_SUPERSEDED_SCOPE_STOP_AT_P24_DECISION.md` for P25/P26 execution authority.

Authorized in-flight stages:
- `ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION`
- `ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN`

Use the existing prompts and immutable dispatch manifest:
- `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_START_PROMPT.md`
- `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN_START_PROMPT.md`
- `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_FINAL_ACCEPTANCE_P25_P26_LONG_2_WORKER_V1.json`

Dedup-v2 still applies. Each Worker must acquire its own canonical claim and stage claim before implementation. A missing claim means Git authority has not yet reflected Worker ownership; it does not authorize duplicate dispatch.

P25/P26 are the only restored post-P24 tasks. Do not create P27+ merely to occupy workers. After both terminalize, PM returns to the existing real-WOF final acceptance/release path.

Safety and release boundaries remain unchanged: no real-WOF execution by these implementation workers, no guessed coordinates/addresses, no screenshot/world-projection production coordinates, no input injection, no alpha-live movement.
