# Alpha V1 Final Acceptance — P25 Resume + P28 Provenance Durable Rebuild — Long 2 Worker Dispatch

## Authority state

- P27 is terminal `COMPLETE` and resolved the P25 staged canonical-feed exposure blocker.
- P26 is terminal `BLOCKED` under its original claim because the original 13/13-tested unpublished bytes lacked a recoverable durable path-to-blob-SHA map. P26 must not be reopened or recovered again.
- P25 remains the original ACTIVE claim and requires only bounded post-P27 repository-level revalidation plus terminal publication.
- P28 is a fresh successor stage that rebuilds the P26 provenance capability as newly committed/newly tested bytes. It must not inherit historical P26 test provenance.

No real WOF, Owner YES/NO, promotion, alpha-live movement, or P23 real close is authorized by this dispatch.

## Worker 1 — P25 continuation

Stage:
`ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION`

Continue the existing claim only:
`claimToken=1a8e410f279e1450057986f7e8212959`

Do not create a new claim or recovery.

Read:
- `parallel/PM/ALPHA_V1_P25_AFTER_P27_BLOCKER_RESOLVED_CONTINUATION.md`
- P25 PROGRESS;
- terminal P27 RESULT;
- P25 original START prompt.

Only perform the minimum post-P27 deterministic revalidation that the existing P25 composite path can consume the same-session maintained P10 canonical coordinator feed now exposed by P27 and no longer fails solely with `NOT_EXPOSED_BY_STAGED_RUNTIME_STATUS`.

Do not rewrite P25, manufacture P22/P24 cycles, run real WOF, or claim visible proof.

If repository-level revalidation passes, publish P25 `COMPLETE`, `integrationReady=true`; otherwise publish a new precise `BLOCKED` result. Close the exact original claim and update PROGRESS to `TERMINAL`/100 only after durable RESULT publication.

## Worker 2 — P28 fresh provenance rebuild

Stage:
`ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD`

START prompt:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD_START_PROMPT.md`

This is a fresh dedup-v2 stage. Acquire a new exact P28 canonical + stage claim and immediately create P28 PROGRESS.

Rebuild the provenance/session-chain capability under `parallel/OWNER_ACCEPTANCE_PROVENANCE/**` from the P26 contract, but treat all P28 bytes/tests as new. Preserve terminal P26 history unchanged.

Mandatory discipline: create a durable implementation candidate commit, read back its exact files, then run fresh focused checks against that committed candidate. If changed after tests, commit a new candidate and rerun affected checks. Never bind historical P26 `13/13 PASS` to P28 bytes.

No real WOF, Owner visual question, promotion, alpha-live movement, input injection, memory writes, or coordinate fallback.

## Shared progress rule

Both workers must obey `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md` and update PROGRESS before any nonterminal stop/window exhaustion.

A chat-only summary is never sufficient.

## Downstream gate

After P25 and P28 are terminal, PM must fresh-read their RESULT/claims/PROGRESS and decide whether the repository is ready to move to the real final acceptance/live sequence. Do not pre-open later stages while either remains nonterminal unless a genuinely independent blocker emerges.
