# PM Stage Dedup — Canonical Claim Hardening

stageId: `PM_STAGE_DEDUP_CANONICAL_CLAIM_HARDENING_V1`

Priority: **P1 execution-safety / duplicate-work prevention**

Purpose: harden PM duplicate protection so accidental copy/paste of the same or semantically equivalent task cannot make multiple workers perform the same implementation/ordinary QA work, while still allowing explicitly scheduled independent second-opinion/cross-check QA.

## Start / dedup

Before any writes, re-read latest `main`, recent PM/start-prompt commits, `parallel/PM/PM_CORE_OPERATING_CHARTER.md`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current `parallel/PM/STAGE_CLAIMS/**`, and representative recent implementation/QA prompts that use atomic claims.

If an equivalent canonical-dedup hardening is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.
If equivalent work is ACTIVE/CLAIMED, stop `ALREADY CLAIMED — SAFE TO CLOSE`.
Otherwise atomically create `parallel/PM/STAGE_CLAIMS/PM_STAGE_DEDUP_CANONICAL_CLAIM_HARDENING_V1.json` before changing PM protocol files.

## Problem to close

Current guard correctly says the stage claim must be atomic, but operational gaps remain:

1. two accidentally duplicated tasks with different `stageId` values can both run even when their real objective/write-domain/stop-condition is equivalent;
2. a worker can perform meaningful analysis/tests/writes before acquiring its claim if a prompt is not explicit enough about claim-first ordering;
3. after a create-file race, the losing worker may not re-read and prove that it does not own the claim;
4. intentional independent second-opinion/cross-check QA must remain possible and must not be confused with accidental duplicate work.

## Required hardening

Design and commit a small, deterministic PM protocol that provides a canonical logical duplicate key in addition to `stageId`.

At minimum:

1. define a stable `dedupKey` for every new task, representing the real logical work item rather than merely its prompt filename/stageId;
2. require claim acquisition as the first mutating/execution action: no implementation changes, expensive tests, Browser/WOF launch, or durable result work before ownership is acquired;
3. introduce a canonical atomic duplicate lock/claim path keyed by `dedupKey` (or an equivalently strong mechanism) so different stageIds for the same logical task still contend on one atomic resource;
4. after creating the lock/claim, require the worker to re-read it and verify ownership using an unambiguous owner/claim token before continuing;
5. if canonical lock creation fails or ownership verification fails, re-read current result/claims and stop `ALREADY CLAIMED — SAFE TO CLOSE` or `ALREADY COMPLETE — SAFE TO CLOSE` as appropriate;
6. distinguish accidental duplicates from explicitly scheduled independent validation using an explicit field/mode such as `dedupMode` / `independentValidationGroup`; second-opinion QA is allowed only when the PM/start prompt explicitly declares it;
7. ordinary implementation/fix and ordinary QA must default to exclusive canonical dedup;
8. stale canonical claims follow PM recovery/supersession rules; ordinary workers may not steal them;
9. preserve historical stage claims; do not rewrite old evidence merely to retrofit the new scheme;
10. provide migration guidance: existing prompts remain readable, while all newly created PM prompts after this hardening must use the stronger fields/rules.

## Verification

Add deterministic repository-side examples/tests or a validator script sufficient to demonstrate at least:

- same stageId, same dedupKey: only one owner proceeds;
- different stageIds, same dedupKey: only one owner proceeds;
- losing claimant exits without doing task work;
- completed equivalent work returns `ALREADY COMPLETE`;
- explicitly declared independent cross-check QA can use a distinct authorized validation key/group and proceed without weakening ordinary dedup;
- stale/ACTIVE claim cannot be stolen by a normal worker;
- malformed/missing required dedup metadata fails closed for new-protocol prompts.

Do not fabricate a distributed lock stronger than GitHub can actually provide. Use atomic create semantics that are genuinely available in the repository workflow and document exact race behavior.

## Write boundary

Write only PM protocol/tooling/test surfaces needed for this hardening, for example:

- `parallel/PM/STAGE_DEDUP_GUARD.md`
- a small `parallel/PM/*DEDUP*` helper/validator/test if useful
- protocol/example docs under `parallel/PM/**`
- this stage claim/result lane.

Do not modify product, Alpha, Formal, Unified, PYLAUNCH, Recorder, Browser, Owner OneClick, or Safe Transport implementation.

## Stop conditions

Success:
`PASS — PM CANONICAL DEDUP CLAIM HARDENING — ACCIDENTAL DUPLICATES FAIL CLOSED`

Failure:
`BLOCKED — PM CANONICAL DEDUP CLAIM HARDENING — <precise blocker>`

Owner action: **NO**.
