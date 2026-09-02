# PM Start Prompt — Canonical Dedup v2 Template

Use this template only for newly created PM stages after canonical dedup v2 hardening.

stageId: `REPLACE_WITH_UPPER_SNAKE_STAGE_ID`
dedupProtocol: `v2`
dedupKey: `replace.with-stable-logical-work-key`
dedupMode: `exclusive`

> `dedupKey` is assigned from the real logical work item, not copied from the stageId or filename. Equivalent accidental prompts must use the same key.

## Start / dedup — mandatory order

1. Re-read latest `main`, relevant RESULT/STATUS, recent equivalent commits, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/STAGE_CLAIMS/**`, and relevant `parallel/PM/DEDUP_CLAIMS/**`.
2. If equivalent work is already complete, stop `ALREADY COMPLETE — SAFE TO CLOSE`.
3. Do not perform task implementation, durable result work, expensive tests, Browser/WOF launch, or other meaningful task execution yet.
4. Generate a fresh random `claimToken`.
5. Derive the exact canonical path using `parallel/PM/pm_stage_dedup_v2.py` semantics.
6. Attempt GitHub **create-file** on the exact canonical path. This must be create-only; do not update an occupied path.
7. If create fails, re-read current canonical/stage claims and results. Stop `ALREADY COMPLETE — SAFE TO CLOSE` or `ALREADY CLAIMED — SAFE TO CLOSE`.
8. If create succeeds, re-read the canonical claim from current `main` and verify the exact `claimToken`, stageId, promptPath, dedupKey/effectiveDedupKey/mode, schema and `ACTIVE` state.
9. Only after canonical ownership verifies, create the v2 `STAGE_CLAIMS/<stageId>.json` mirror with create-only semantics. If that fails, re-read and fail closed.
10. Only then start task work.

## Independent validation variant

Use only when PM explicitly wants a second opinion/cross-check QA. Replace `dedupMode` and add both fields:

```text
dedupMode: `independent-validation`
independentValidationGroup: `pm-assigned-stable-group`
independentValidationKey: `pm-assigned-opinion-slot`
```

Each intentional opinion gets a different PM-assigned validation key. A copied instance of the same opinion must retain the same key and therefore collide on the same canonical path. Workers may not invent a new validation key to bypass an occupied claim.

## Close

Before updating canonical/stage claims to COMPLETE or BLOCKED, re-read the canonical claim and verify the same `claimToken`. Use the current blob SHA for updates; update races fail closed.

Validate metadata before publishing a new prompt:

```bash
python parallel/PM/pm_stage_dedup_v2.py validate-prompt parallel/PM/<NEW_START_PROMPT>.md
```
