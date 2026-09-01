# PYLAUNCH Identity Cache Generation Fresh QA Start Prompt

stageId: `PYLAUNCH_IDENTITY_CACHE_GENERATION_QA_V1`
priority: `P1`

## Purpose
Independently re-audit the current PYLAUNCH implementation after `PYLAUNCH_IDENTITY_CACHE_GENERATION_FIX_V1`. Do not trust the implementation thread's READY verdict. Prove that exact World identity authority cannot survive a discovery/browser/runtime generation boundary merely because `targetId` is reused, while preserving parentFrame/parentId discovery compatibility and fail-closed safety.

## Dedup / claim guard
Before any work:
1. Read `parallel/PM/STAGE_CLAIMS/PYLAUNCH_IDENTITY_CACHE_GENERATION_QA_V1.json` if present.
2. If already COMPLETE/PASS with durable current result: return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`.
3. If ACTIVE by another thread: return `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.
4. Otherwise claim the stage under that exact claim path.

## Allowed write scope
- `parallel/PYLAUNCH_QA_IDENTITY_GENERATION/**`
- `parallel/PM/STAGE_CLAIMS/PYLAUNCH_IDENTITY_CACHE_GENERATION_QA_V1.json`

Do NOT modify `parallel/PYLAUNCH/**`, `parallel/OWNER_ONECLICK/**`, workflows, Alpha product code, Recorder, Prospective, or other implementation lanes.

## Required fresh QA
At minimum independently test/audit:
1. generation 1 correct World accepted; generation 2 wrong World with same `targetId` must reprobe and reject;
2. generation 2 correct World with same `targetId` may only be accepted after its own fresh exact World proof;
3. browser-level CDP replacement clears all identity authority before new connection becomes authoritative;
4. same current discovery generation may reuse only authority proven inside that generation where required for duplicate observation paths;
5. `parentId` remains higher authority than `parentFrameId`; `openerId` remains non-authoritative;
6. Page.getFrameTree / direct parentFrame association still works for two-page topologies;
7. ambiguous duplicate frame/page mappings fail closed;
8. blob/data/hashed/no-extension Worker URL remains diagnostic only, never identity authority;
9. exact World 921031 SHA remains the only accepted identity;
10. loopback/exact-port confinement and read-only allowlist remain intact;
11. no `Input.*`, no RAM writes, no Worker replacement/wrap, no Blob/ObjectURL rewrite;
12. re-run current PYLAUNCH regression suites against current HEAD, not cached historical artifacts.

## Delivery reassessment requirement
The final result must explicitly state whether this QA actually removes PYLAUNCH from the current Alpha critical blocker list, what downstream stage it unlocks, and whether Owner action is needed.

## Stop conditions
PASS:
`PASS — PYLAUNCH IDENTITY CACHE GENERATION FRESH QA — READY FOR CROSS-COMPONENT RETEST`

BLOCKED:
`BLOCKED — PYLAUNCH IDENTITY CACHE GENERATION FRESH QA — <exact P0/P1 blocker>`

Owner Browser/WOF should remain NO unless the repository-side question is intrinsically impossible to answer offline.