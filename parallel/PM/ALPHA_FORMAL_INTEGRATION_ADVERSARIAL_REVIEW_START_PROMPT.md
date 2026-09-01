# Alpha Formal Integration Adversarial Review Start Prompt

stageId: `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1`

Priority: **P1 Alpha release support**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`; re-read current HEAD repeatedly because the formal integration lane is active. If equivalent durable review already exists, return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`; if claimed, return `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.

Claim `parallel/PM/STAGE_CLAIMS/ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1.json`.

This lane must not modify `product/alpha/**`. It is an independent read/review/failure-injection lane that follows the active formal real-adapter integration commits and prepares reproducible adversarial fixtures under `parallel/ALPHA_FORMAL_INTEGRATION_REVIEW/**`.

Review current-head integration for authority confusion, stale pair/session/generation publication, detector-local identity mismatch, reconnect/runtime replacement, Worker replacement, no-transport behavior, unsupported identity fail-closed, RC5 bootstrap safety, warning clear/change semantics, accidental input/RAM write capability, and interface drift against PYLAUNCH current HEAD.

As new integration commits land, re-read affected files and rerun the review. Do not self-certify PASS while the implementation claim remains ACTIVE; instead maintain CURRENT_HEAD_FINDINGS.md and deterministic fixtures. If a concrete P0/P1 defect is found, stop immediately with exact repro and blocker result. If the implementation formally completes with no blocker, produce a handoff that the fresh integration QA can consume.

Success/stop: `ALPHA FORMAL INTEGRATION ADVERSARIAL REVIEW READY — NO CURRENT-HEAD BLOCKER FOUND` only after implementation COMPLETE; otherwise one precise blocker.

Owner action: **NO**.