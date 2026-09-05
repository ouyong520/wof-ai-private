stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.final-acceptance-session-provenance-chain-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P26_FINAL_ACCEPTANCE_SESSION_PROVENANCE_CHAIN`

# Alpha V1 Product Takeover P26 — Final Acceptance Session Provenance Chain

Repository: `ouyong520/wof-ai-private`

This is intentionally a long final-evidence integrity module. Complete the entire bounded provenance/chain-of-custody implementation before terminal result; do not split into micro-tasks.

Read latest `main`, root `AGENTS.md`, PM playbook/testing cadence/dedup guard/current dispatch, then read the COMPLETE results/contracts for P16-P24, P19 exact final candidate/attestation, P20 receipt/promotion-plan format, P21 staging receipt, P22 dynamic coverage, P24 temporal evidence, P17 acceptance bundle, P18 draw evidence, and the existing W3 bounded qualification result/report contract. If P25 exists while this worker runs, consume its documented composite evidence index contract only after verifying it from Git; do not depend on uncommitted assumptions.

## Why P26 exists

Alpha's final automatic evidence comes from several independent modules. Even if each artifact is individually valid, a false acceptance could occur if artifacts from different runs/candidates/epochs are accidentally combined.

P26 must make that impossible by providing a deterministic, fail-closed provenance chain:

`P19 candidate -> P21 staged run -> W3/P16/P18 -> P22/P24 -> P17 bundle -> P20 Owner receipt/promotion plan -> P23 close verification`

The chain proves only that evidence belongs together; it never upgrades repository/runtime evidence into visual PASS.

## Ownership

Acquire normal dedup-v2 canonical and stage claims with exact-token readback. Fail closed on collision. No recovery invention.

Prefer a new isolated area under:
`parallel/OWNER_ACCEPTANCE_PROVENANCE/`

Do not modify P16-P25/W3 implementations unless an actual schema incompatibility is proven and a tiny compatibility change is explicitly justified. Never move `alpha-live`.

## Goal

Implement one deterministic session manifest/verifier which can be created at the start of a final acceptance run, incrementally bind artifacts as they appear, and later verify that every accepted artifact belongs to the same exact candidate and same causal session.

## Workstream A — immutable session root identity

Create a session-root document before live evidence begins containing at minimum:
- schema/version;
- sessionId/run nonce;
- exact P19 sourceCommit;
- packageVersion;
- candidate SHA256;
- attestation SHA256;
- expected exact World identity;
- P21 staging receipt/run identity when available;
- createdAt;
- safety invariants;
- state=`OPEN`.

The session root must be hash-addressed/deterministically hashed except for the explicitly random session nonce/timestamp fields. Once candidate identity is bound, it may never be mutated to another candidate.

## Workstream B — artifact binding ledger

Implement append/bind operations for at least:
- W3 qualification artifact/report;
- P16 canonical Owner evidence;
- P18 draw evidence;
- P22 dynamic-state coverage output;
- P24 temporal-continuity output;
- P17 final acceptance bundle;
- P20 real Owner visual receipt;
- P20 promotion plan/result;
- P23 post-promotion verification receipt/final close artifact;
- optional P25 composite evidence index.

For each artifact record:
- path/reference;
- SHA256/content hash;
- schema/version;
- source candidate identity;
- pageTargetId when applicable;
- worldSha256;
- authorityKey;
- runtimeEpoch;
- rendererEpoch;
- evidence generation / session/run id fields when available;
- observed/created timestamp as metadata only;
- whether it is live, fixture, synthetic, or repository-only evidence according to the artifact's own contract.

Never trust filenames alone. Parse and verify the artifact's own identity fields and hashes.

## Workstream C — cross-artifact causal consistency

Fail closed on any incompatible mix, including:
- different sourceCommit/packageVersion/candidate hash;
- different World identity;
- pageTargetId mismatch where exact same page is required;
- authorityKey/runtimeEpoch/rendererEpoch mismatch without an explicitly represented and allowed replacement transition;
- stale generation/draw acknowledgement;
- P22/P24 output from a different P21 run;
- P17 bundle whose W3/P16/P18 hashes do not match the bound artifacts;
- P20 receipt bound to a different P17 bundle/candidate;
- promotion result bound to a different plan hash or different fromAlphaLive/toCandidate pair;
- P23 close artifact bound to a different promoted commit/session;
- fixture/synthetic evidence occupying a slot that requires real evidence.

Runtime/renderer replacement may be represented only as an explicit ordered transition within the same final session, with before/after authority evidence. Do not silently treat unrelated epochs as one continuous run.

## Workstream D — chain state machine

Expose deterministic states such as:
- `OPEN`
- `WAITING_FOR_LIVE_W3`
- `WAITING_FOR_CANONICAL_EVIDENCE`
- `WAITING_FOR_DYNAMIC_TEMPORAL_EVIDENCE`
- `READY_FOR_OWNER_VISUAL_CONFIRMATION`
- `WAITING_FOR_PROMOTION`
- `WAITING_FOR_POST_PROMOTION_VERIFY`
- `CHAIN_COMPLETE`
- `REJECTED`

State advancement must be monotonic and evidence-based. Missing evidence keeps WAITING. Conflicting evidence becomes REJECTED. No test fixture may reach a real final/production state unless explicitly marked fixture-only in a separate test namespace.

`CHAIN_COMPLETE` means provenance consistency only; the project itself reaches final completion only through the existing P23 real close contract.

## Workstream E — deterministic chain digest and receipts

Emit:
- a canonical JSON session manifest;
- concise Markdown summary;
- deterministic chain digest/hash over normalized root identity + ordered bound artifact hashes + transition records;
- rejection reasons and exact first incompatible artifact when rejected.

Support verify-only re-reading from disk so PM can prove the chain later without re-running WOF.

Use atomic writes and bounded artifact counts. Never overwrite a prior terminal REJECTED/COMPLETE session with a different meaning.

## Workstream F — Windows/PM operator seam

Provide a Windows-friendly and Python CLI that can:
1. open a session for the exact latest P19 candidate;
2. bind/verify artifacts as they appear;
3. print one compact current state;
4. finalize provenance after P23 evidence exists.

Do not create a new permanent Owner install/update path and do not ask the Owner to edit hashes/JSON manually.

P26 may later be invoked by P25 or PM orchestration, but the provenance verifier must remain independently usable.

## Write boundaries

Expected new files only under:
`parallel/OWNER_ACCEPTANCE_PROVENANCE/`

Narrow tests/docs/wrapper are allowed in that area.

Do not modify:
- P19 candidate builder/attestation;
- P20 release/promotion implementation;
- P21 staging implementation;
- P22/P24 analyzers;
- P18 HUD;
- W3 producer/qualification;
- permanent W1 updater/setup;
- `alpha-live`.

## Focused checks only

Implementation first. Run only narrow checks:
- Python/CMD syntax/compile;
- same-session valid artifact chain fixture;
- cross-candidate rejection;
- World/page/authority/runtime/renderer mismatch rejection;
- explicit allowed epoch-transition fixture vs unrelated epoch rejection;
- stale generation/P18 ACK rejection;
- P17 bundle hash mismatch rejection;
- fixture Owner receipt cannot satisfy real slot;
- promotion plan/result hash/CAS mismatch rejection;
- P23 different-session close rejection;
- deterministic chain digest for fixed normalized inputs;
- terminal-session immutability/atomic write fixture;
- source scan proving no alpha-live mutation, no input injection, no coordinate guessing/fallback.

No broad QA, no real WOF, no Owner visual question, no promotion.

## Terminal result

Write the specified RESULT.json/RESULT.md with implementation commits, exact changed files, focused checks, integrationReady, schemas/state machine, safety, later integration action, and proof boundaries.

Successful COMPLETE proves only the provenance-chain implementation. It must state:
- `realWofAcceptance=NOT_RUN`;
- `ownerVisualAcceptance=NOT_RUN`;
- `alphaLiveMoved=false`;
- `visibleProof=NOT_PROVEN`.
