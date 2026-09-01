# PYLAUNCH Identity Cache Generation Fix — Fresh Stage

stageId: `PYLAUNCH_IDENTITY_CACHE_GENERATION_FIX_V1`
priority: `P1`

## Dedup / claim
Follow `parallel/PM/STAGE_DEDUP_GUARD.md`. If equivalent durable work is already complete or claimed, use the standard exact dedup stop message. Otherwise claim under `parallel/PM/STAGE_CLAIMS/PYLAUNCH_IDENTITY_CACHE_GENERATION_FIX_V1.json` and continue.

## Why now
Fresh independent QA accepted the new parentFrame production mapping but found one remaining P1: exact World identity authority is cached by `targetId` only, so a new browser/runtime generation that reuses the same Worker target id can inherit a prior generation's accepted World 921031 identity without a fresh probe.

Read first:
- `parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md`
- current `parallel/PYLAUNCH/**`
- current parentFrame authority regression
- QA fixture `parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/test_adversarial_generation_cache.py`

## Hard write scope
Write only under:
- `parallel/PYLAUNCH/**`
- mandatory PM claim file
Do not modify Recorder, Prospective, Live Proof, Alpha Transport, HUD, Owner OneClick.

## Required fix
1. Exact World identity cache authority must be scoped to a proven current browser/runtime/session generation, not `targetId` alone.
2. Replacing/reconnecting the CDP browser connection must invalidate prior identity authority.
3. A runtime/execution-context generation change with stable/reused target id must force a fresh exact identity probe, or conservatively avoid cache reuse across discovery generations.
4. Absorb the fresh QA adversarial case: generation 1 exact World, generation 2 wrong identity, same Worker target id -> generation 2 must re-probe and reject.
5. Preserve `Page.getFrameTree` production reachability and parentFrame association.
6. Preserve valid `parentId` priority, non-authoritative `openerId`, ambiguous-frame fail-closed behavior, endpoint confinement and exact World 921031 authority.
7. Preserve `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no Worker replacement/wrap, no Blob/ObjectURL rewrite and no gameplay Input capability.

## Regression
Run the new generation-cache regression plus existing parentFrame and Discovery V2 compatibility/safety regressions. Record exact counts and final blobs.

## Stop condition
Success:
`PYLAUNCH IDENTITY CACHE GENERATION FIX READY — READY FOR FRESH QA`
Or one precise blocker requiring different ownership.

No Owner Browser/WOF run. Owner action: `NO`.
