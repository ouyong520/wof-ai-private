stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.final-acceptance-session-provenance-durable-rebuild-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD`

# Alpha V1 Product Takeover P28 — Final Acceptance Session Provenance Durable Rebuild

Repository: `ouyong520/wof-ai-private`

## Mission

Rebuild the P26 final-acceptance session provenance-chain capability on latest `main` as a fresh, durably committed, freshly tested implementation.

P26 is terminal `BLOCKED` because its original 13/13-tested implementation bytes were never durably tied to an exact file-path -> blob-SHA map. P28 is **not** a recovery of P26 and must never claim that historical 13/13 result for new bytes. Preserve P26 terminal history exactly as-is.

P28 succeeds only by producing a new implementation candidate, committing it durably, reading it back, then running fresh focused checks against that committed candidate and binding the new result to the exact tested commit.

## Required preflight

Before any implementation mutation:

1. read latest `main` and root `AGENTS.md`;
2. read `parallel/PM/STAGE_DEDUP_GUARD.md`;
3. read `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`;
4. read `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`;
5. read the terminal P26 RESULT and P26 START prompt;
6. verify P26 canonical/stage claim is terminal `BLOCKED` and do not edit/reopen it;
7. inspect `parallel/OWNER_ACCEPTANCE_PROVENANCE/` on latest main; if conflicting active ownership unexpectedly exists, fail closed;
8. acquire a **new** normal dedup-v2 P28 canonical + stage claim using this P28 dedup key and re-read exact matching claimToken.

Immediately after claim verification create:
`parallel/PM/PROGRESS/ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD_PROGRESS.json`.

## Mandatory durable-test discipline

This stage exists specifically to prevent a repeat of P26's publication failure.

Therefore:

- never treat workspace-only/unpublished bytes as final test provenance;
- implement in coherent bounded commits under the P28 claim;
- before the final focused test pass, create a durable implementation candidate commit and record its exact SHA in PROGRESS;
- re-read the committed files from Git and verify the expected changed-file set;
- run the fresh focused test suite against that exact committed candidate;
- if any fix is needed afterward, create a new candidate commit and re-run the affected focused checks; the final RESULT must point only to the final tested candidate;
- RESULT must explicitly distinguish the old P26 historical `13/13 PASS` from P28's newly executed test result; never reuse or inherit the P26 test claim;
- before any nonterminal stop/window exhaustion, update PROGRESS with latest candidate/test state.

No exact path-to-blob-SHA recovery of old P26 bytes is required or allowed. No historical bytes may be reconstructed and labeled as original P26 tested bytes.

## Functional requirements

Reimplement the P26 provenance-chain contract as a production-shaped, deterministic, fail-closed module under:
`parallel/OWNER_ACCEPTANCE_PROVENANCE/`

It must provide a deterministic causal chain:

`P19 candidate -> P21 staged run -> W3/P16/P18 -> P22/P24 -> P17 bundle -> P20 Owner receipt/promotion plan -> P23 close verification`

The chain proves only evidence/session consistency. It never upgrades repository evidence into Owner-visible PASS.

### Session root

Create an immutable session root containing at minimum:
- schema/version;
- sessionId/run nonce;
- exact P19 sourceCommit;
- packageVersion;
- candidate SHA256;
- attestation SHA256;
- exact World identity;
- P21 staging/run identity when available;
- createdAt metadata;
- safety invariants;
- state=`OPEN`.

Candidate identity must never be rebound to another candidate within the same session.

### Artifact ledger

Support binding/verification for at least:
- W3 qualification report/artifact;
- P16 canonical Owner evidence;
- P18 draw evidence;
- P22 dynamic-state coverage;
- P24 temporal-continuity evidence;
- P17 final acceptance bundle;
- P20 Owner visual receipt;
- P20 promotion plan/result;
- P23 post-promotion verification/final-close artifact;
- optional P25 composite evidence index when present.

For each artifact verify its own identity/hash/schema fields. Do not trust filename alone.

### Cross-artifact consistency

Fail closed on incompatible candidate/session/World/page/authority/runtimeEpoch/rendererEpoch identities, stale generation/draw ACK, cross-run P22/P24 output, P17 dependency hash mismatch, fixture evidence in a real slot, P20 receipt/plan/result mismatch, or P23 cross-session close evidence.

Runtime/renderer replacement may be accepted only as an explicit ordered transition with before/after authority evidence.

### State machine

Expose deterministic monotonic states including:
- `OPEN`
- `WAITING_FOR_LIVE_W3`
- `WAITING_FOR_CANONICAL_EVIDENCE`
- `WAITING_FOR_DYNAMIC_TEMPORAL_EVIDENCE`
- `READY_FOR_OWNER_VISUAL_CONFIRMATION`
- `WAITING_FOR_PROMOTION`
- `WAITING_FOR_POST_PROMOTION_VERIFY`
- `CHAIN_COMPLETE`
- `REJECTED`

`CHAIN_COMPLETE` is provenance consistency only. Final Alpha completion remains governed by the real P23 close contract.

### Digest / persistence / CLI

Provide:
- canonical JSON session manifest;
- concise Markdown summary;
- deterministic chain digest over normalized root + ordered artifact hashes + explicit transitions;
- exact rejection reason/first incompatible artifact;
- verify-only reload from disk;
- atomic writes;
- terminal immutability;
- bounded artifact counts;
- Windows-friendly and Python CLI for open/bind/status/finalize operations.

## Ownership

Expected writes are limited to:
- `parallel/OWNER_ACCEPTANCE_PROVENANCE/**`;
- P28 PROGRESS/RESULT/claim files required by governance.

Do not modify P16-P27 implementations, P20 promotion logic, P21 staging logic, P22/P24 analyzers, W3 producer, permanent W1 updater, or `alpha-live`.

If a concrete incompatible upstream schema is discovered, fail closed and report the exact blocker rather than widening ownership.

## Safety

Must remain:
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- no coordinate guessing/fallback;
- no screenshot production coordinates;
- no world-projection production coordinates;
- no alpha-live movement.

Do not run real WOF, do not ask Owner YES/NO, and do not execute promotion.

## Fresh focused checks

Run fresh checks against the exact final committed P28 candidate, including at minimum:
- Python/CMD compile/syntax;
- same-session valid-chain fixture;
- cross-candidate rejection;
- World/page/authority/runtime/renderer mismatch rejection;
- allowed explicit epoch transition vs unrelated epoch rejection;
- stale generation/P18 ACK rejection;
- P17 bundle dependency-hash mismatch rejection;
- fixture Owner receipt cannot satisfy real evidence slot;
- promotion plan/result hash/CAS mismatch rejection;
- P23 cross-session close rejection;
- deterministic digest stability for fixed normalized inputs;
- terminal immutability/atomic-write fixture;
- static scan showing no alpha-live mutation, input injection, memory write, or coordinate fallback.

Do not copy the old P26 `13/13` count into P28 unless P28 independently happens to execute exactly 13 checks. Report the actual fresh P28 check count.

## Acceptance

P28 may report `COMPLETE` only when:

1. the provenance module is durably present on latest integrated main history under the permitted path;
2. the final tested candidate commit is explicitly recorded and read back;
3. fresh focused tests pass against that exact candidate;
4. changed-files/ownership readback is exact;
5. no old P26 blob/test provenance is reused;
6. RESULT truthfully states `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, `alphaLiveMoved=false`;
7. canonical + stage claims close using the exact P28 claimToken;
8. PROGRESS becomes `TERMINAL`/100 only after RESULT publication and claim close.

If fresh implementation cannot satisfy the contract within this boundary, publish precise `BLOCKED`; do not reopen P26 or manufacture historical provenance.
