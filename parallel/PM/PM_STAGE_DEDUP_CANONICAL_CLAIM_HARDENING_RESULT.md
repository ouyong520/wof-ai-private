# PM Stage Dedup Canonical Claim Hardening — RESULT

Stage: `PM_STAGE_DEDUP_CANONICAL_CLAIM_HARDENING_V1`

Verdict:

`PASS — PM CANONICAL DEDUP CLAIM HARDENING — ACCIDENTAL DUPLICATES FAIL CLOSED`

Owner action: **NO**

## Fresh preflight / ownership

- Initial audited `main`: `072e0429d3c44eb29c7852fd7486284aca8bda57`; immediately before claim, refreshed `main` was `ed469e4b36f5b638c0894928978e5b2dcc313709`.
- Re-read `PM_CORE_OPERATING_CHARTER.md`, `STAGE_DEDUP_GUARD.md`, current stage claims, recent atomic-claim prompts/claims and recent commits.
- No equivalent canonical `dedupKey` hardening/result/claim existed.
- Stage claim was acquired with GitHub create-only semantics in commit `9f86c8e69c1a2767e4a345d91d686841b68211c2` and re-read with exact owner token `6f3c1a9e-9d27-4d18-b3b4-50f2b8be7e71` before protocol implementation.

## Implemented protocol

1. `parallel/PM/STAGE_DEDUP_GUARD.md`
   - upgraded to canonical dedup protocol v2;
   - every newly created PM prompt must declare `dedupProtocol: v2`, stable semantic `dedupKey`, and `dedupMode`;
   - task work is forbidden before canonical ownership is acquired and re-read/verified;
   - ordinary implementation/fix/QA defaults to exclusive canonical dedup;
   - canonical path is `parallel/PM/DEDUP_CLAIMS/<effectiveDedupKey>.json`;
   - exact `claimToken`, not a display owner name, proves ownership;
   - canonical create failures and ownership mismatches fail closed;
   - stage claim becomes a durable v2 mirror/history record after canonical ownership;
   - stale/ACTIVE/BLOCKED canonical claims cannot be stolen by ordinary workers;
   - PM-only recovery/supersession preserves old evidence and uses an explicitly authorized recovery key;
   - historical v1 prompts/claims remain readable and are not rewritten.

2. Explicit second-opinion / cross-check QA remains supported only through PM-declared:
   - `dedupMode: independent-validation`;
   - `independentValidationGroup`;
   - `independentValidationKey`.

   Its effective lock key is `<dedupKey>--iv--<group>--<validationKey>`. Separate PM-authorized opinion slots can proceed, while copied instances of the same slot collide on one canonical path. Workers may not self-authorize a new slot.

3. `parallel/PM/pm_stage_dedup_v2.py`
   - deterministic prompt metadata validator;
   - canonical/effective key and claim-path derivation;
   - canonical claim payload builder;
   - exact post-create ownership/token verifier;
   - fail-closed occupied-claim classification;
   - deterministic create-only test double/self-test.

4. `parallel/PM/test_pm_stage_dedup_v2.py`
   - 8 repository-side regressions covering all required cases.

5. `parallel/PM/PM_START_PROMPT_DEDUP_V2_TEMPLATE.md`
   - mandatory claim-first ordering for new prompt authors;
   - explicit independent-validation variant.

6. `parallel/PM/DEDUP_CLAIMS/README.md`
   - canonical claim lane/race/recovery semantics.

7. `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
   - section 6 aligned with v2 canonical dedup and explicit independent validation.

## Real GitHub atomic-create proof

The protocol does not fabricate a distributed lock stronger than GitHub provides.

A real canonical fixture was created at:

`parallel/PM/DEDUP_CLAIMS/pm.protocol.atomic-create-fixture.json`

First create-only writer succeeded in commit:

`aff028b566b6f1d21795a64b375ea284d8bef65d`

with token:

`fixture-owner-4d6e6de8`

A second GitHub `create_file` attempt against the exact same canonical path, using a different stage/token, was rejected by GitHub with HTTP `422` / `"sha" wasn't supplied` because the path already existed. No update SHA was supplied, so the loser could not replace the existing file.

The path was re-read afterward and still contained the first writer's token/state. This demonstrates the exact create-only contention behavior used by the protocol. Any create/API failure is treated as no ownership and fails closed.

## Verification

Committed helper/test blobs were re-read from current GitHub, then reconstructed source-exact in an isolated local directory because the execution container has no network access to clone the private repository.

Commands/equivalent execution:

- `python pm_stage_dedup_v2.py self-test` -> PASS
- `python test_pm_stage_dedup_v2.py` -> `Ran 8 tests ... OK`

Covered regressions:

1. same `stageId`, same `dedupKey`: one owner only;
2. different `stageId`, same `dedupKey`: one owner only;
3. losing claimant exits before task-work callback can run;
4. occupied equivalent `COMPLETE` returns `ALREADY COMPLETE — SAFE TO CLOSE`;
5. two explicitly authorized independent-validation slots use distinct locks, while a copied slot still loses;
6. existing/stale `ACTIVE` claim is unchanged and cannot be stolen;
7. missing/malformed protocol/key/mode/independent metadata raises fail-closed validation errors;
8. post-create verification rejects the wrong `claimToken`.

## Key commits

- `1f378e9a5d9d40d322679473323092002d0c6bb6` — canonical v2 guard
- `16929ed39cca5b007e61c727fd9fce6c3ae959cf` — validator/helper
- `f2c748c1739d5c7a225f361c19aa73606966236f` — regression suite
- `3c116dccabad108efe30bf19da67b8371f65f016` — v2 prompt template
- `6762ed53a9b084d78e2bdb5f3b496984b3deee12` — canonical claim lane docs
- `aff028b566b6f1d21795a64b375ea284d8bef65d` — live canonical atomic-create fixture winner
- `d3d7baf14ca752237268231a5b14240054fa21bf` — core charter alignment

## Scope boundary

No product, Alpha, Formal, Unified, PYLAUNCH, Recorder, Browser, OneClick, Safe Transport, or gameplay implementation was modified by this stage.
