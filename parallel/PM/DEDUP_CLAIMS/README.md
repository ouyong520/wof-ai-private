# PM Canonical Dedup Claims

This directory contains canonical logical-work claims introduced by `STAGE_DEDUP_GUARD.md` protocol v2.

- Ordinary work: `parallel/PM/DEDUP_CLAIMS/<dedupKey>.json`
- Explicit independent validation: `parallel/PM/DEDUP_CLAIMS/<dedupKey>--iv--<group>--<validationKey>.json`

These files are durable ownership/history records. Workers acquire ownership only by GitHub create-only semantics on a path that does not yet exist, then re-read the committed file and verify their exact `claimToken` before doing task work.

Do not delete or overwrite an occupied claim to obtain ownership. Ordinary workers do not steal stale/ACTIVE/BLOCKED claims. PM-authorized recovery/supersession uses a fresh recovery prompt/key while preserving old evidence.

Historical `parallel/PM/STAGE_CLAIMS/**` remain in place; v2 stage claims reference the canonical claim.
