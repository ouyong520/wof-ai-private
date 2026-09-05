# Alpha V1 Final Retry Readiness Gate

This directory is an isolated, read-only repository-side gate for one question only:

`READY_FOR_ONE_BOUNDED_OWNER_RETRY`

It is **not** a promotion gate, does not run WOF, does not move alpha-live, does not ask the Owner YES/NO, and does not convert live `BLOCKED` / `INCONCLUSIVE` evidence into PASS.

## Authority order

`final_retry_readiness.py` deliberately does not read worker PROGRESS as terminal authority. For each required repair stage it reads exactly:

1. `parallel/PM/RESULTS/<stageId>_RESULT.json`
2. `parallel/PM/DEDUP_CLAIMS/<dedupKey>.json`
3. `parallel/PM/STAGE_CLAIMS/<stageId>.json`

The RESULT and both claims must agree on stage, dedup key, exact claim token, terminal state, tested commit, and RESULT path. The accepted terminal state for P29/P30/P31/P32 is `COMPLETE`; a truthful P32 `BLOCKED` therefore remains a blocker.

## Final-candidate provenance contract

The default provenance path is:

`parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json`

A retry-eligible provenance object must provide all of:

- `sourceCommit`: exact 40-hex repository commit.
- `packageVersion`: non-empty exact package version.
- `candidatePath`: repository-relative immutable candidate JSON path.
- `candidateSha256`: SHA-256 of the exact candidate bytes.
- `manifestPath`: repository-relative immutable manifest JSON path.
- `manifestSha256`: SHA-256 of the exact manifest bytes.
- `requiredTestedCommits`: exact mapping from every required repair `stageId` to that stage's terminal `testedCommit`.
- no `alphaLiveMoved=true`, `alphaLivePromoted=true`, or `promotionPerformed=true`.

The candidate JSON and manifest JSON must both read back the same exact `sourceCommit` and `packageVersion`. Their bytes must match the SHA-256 values in provenance.

The selected `sourceCommit` must exist and `git merge-base --is-ancestor <testedCommit> <sourceCommit>` must succeed for every required tested commit. This makes a stale P19-era candidate fail closed even if its historical pointer says `state: READY`.

## Deterministic output

The command emits a machine-readable JSON object. It returns state `READY_FOR_ONE_BOUNDED_OWNER_RETRY` only when there are zero blockers; otherwise it returns `BLOCKED` with ordered precise blocker records.

A READY result still has:

- `ownerRetryBudget = 1`
- `promotionAuthorized = false`
- `alphaLiveMoveAuthorized = false`
- `realGameRunPerformed = false`

Run from repository root:

```bash
python parallel/OWNER_RETRY_READINESS/final_retry_readiness.py
```

Exit status is `0` only for READY and `2` for BLOCKED.

## Current intended state

P34 implementation completion does not imply repository readiness. In the dispatch state, P32's terminal/live dependency must remain truthful and the historical pre-repair final candidate must not be accepted as containing later repair commits. The gate is expected to stay BLOCKED until PM-approved terminal repair authority and one fresh exact containing final candidate provenance both exist.
