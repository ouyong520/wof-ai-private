# Alpha V1 P34 — Final Retry Readiness Gate — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P34_FINAL_RETRY_READINESS_GATE`

DedupKey:
`alpha.v1.product-takeover.final-retry-readiness-gate-v1`

Mission: create one deterministic repo-side gate that answers only whether the repaired Alpha V1 repository/candidate chain is eligible for exactly one bounded Owner live retry. It must prevent another blind retry and must never be confused with release/promotion approval.

Fresh PM state when this task is dispatched:
- P29 terminal COMPLETE / PM accepted.
- P30 terminal COMPLETE / PM accepted.
- P31 remains ACTIVE.
- P32 remains ACTIVE.
- Owner live retry remains blocked until P31 terminalizes and P32 reaches a PM-reviewable terminal proof-producer/live-dependency state.

Read latest main, root AGENTS.md, full dedup/progress/result protocols, current final live gate, P29/P30 terminal RESULTs, P31/P32 START/PROGRESS, current final candidate and Owner staging/release contracts. Prefer a new isolated `parallel/OWNER_RETRY_READINESS/**` surface so active worker ownership is not disturbed.

Dedup-v2: if equivalent ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Ownership is limited to retry-readiness aggregation/gating and focused deterministic tests. Do not modify P31 Page/Worker/WASM association code, P32 renderer/marker qualification code, P29 analyzer semantics, P30 staging/P16/P9 implementation files, or promotion behavior.

Required gate semantics:
- consume authoritative terminal RESULT + canonical/stage claim state for required repair stages; PROGRESS alone is never enough;
- require P29 and P30 terminal COMPLETE with their exact tested commits;
- remain fail-closed while P31 or P32 is non-terminal;
- once P31/P32 terminalize, require a PM-approved acceptable terminal state and exact tested commit/proof-producer provenance; BLOCKED/INCONCLUSIVE semantics must remain truthful and must not be rewritten to PASS;
- require one selected final candidate whose source commit contains every required accepted tested commit and whose manifest/candidate identity is exact;
- reject stale candidate, missing result, mismatched claim token, unclosed claim, source-commit ancestry failure, manifest hash mismatch, or any alpha-live movement before retry;
- output a machine-readable state such as `READY_FOR_ONE_BOUNDED_OWNER_RETRY` only when all repo-side prerequisites are satisfied;
- otherwise output precise blockers and remain non-ready;
- this gate authorizes at most a later local retry by Codex + Owner; it never runs the game, never promotes, never asks Owner YES/NO, and never moves alpha-live.

Focused deterministic tests must cover at least:
- P29/P30 complete but P31/P32 active => blocked;
- all required terminal results but stale candidate missing one tested commit => blocked;
- mismatched claim token or non-COMPLETE claim => blocked;
- exact terminal chain + exact containing candidate => READY_FOR_ONE_BOUNDED_OWNER_RETRY;
- truthful P32 live dependency metadata is preserved, not converted to W3 PASS;
- alpha-liveMoved=true anywhere before retry => blocked.

Terminal COMPLETE means the readiness gate implementation itself is durable/focused-tested. It does not mean the current repo is necessarily READY, does not run real WOF, does not prove visible correctness, and does not authorize promotion.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun of affected checks.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.
