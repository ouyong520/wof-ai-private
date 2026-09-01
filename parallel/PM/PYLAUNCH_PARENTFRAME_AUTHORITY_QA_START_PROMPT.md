# PYLAUNCH parentFrame Authority — Fresh Independent QA Start Prompt

stageId: `PYLAUNCH_PARENTFRAME_AUTHORITY_QA_V1`
priority: `P1`

## Dedup / claim
Follow `parallel/PM/STAGE_DEDUP_GUARD.md` before work. If complete or claimed, stop with the standard exact dedup message. Otherwise claim under `parallel/PM/STAGE_CLAIMS/PYLAUNCH_PARENTFRAME_AUTHORITY_QA_V1.json`.

## Role
You are fresh independent QA. Do not trust the implementation-stage READY verdict.

## Read first
- `parallel/PYLAUNCH/PARENTFRAME_AUTHORITY_FIX_RESULT.md`
- current `parallel/PYLAUNCH/**`
- prior fresh QA blocker under `parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING/**`
- current Discovery V2 conformance expectations

## Independent questions
Prove against current production path, not isolated helpers:
1. `Page.getFrameTree` is actually reachable through the production page probe path.
2. two WOF pages + direct Worker + unique `parentFrameId` selects only the owning page.
3. child-frame id maps to the correct owning page.
4. duplicate/non-unique frame mapping fails closed.
5. valid `parentId` remains higher authority than conflicting `parentFrameId`.
6. Worker `openerId` never becomes parent authority.
7. multi-page direct fallback without real parent relation rejects.
8. reload/reconnect/stale target/session state cannot inherit authority.
9. remote/cross-port CDP surfaces remain fail closed.
10. exact World 921031 identity remains authoritative regardless of Worker URL shape.
11. `Page.getFrameTree` is the only newly needed read-only capability; no gameplay `Input.*`, no arbitrary `Runtime.callFunctionOn`.
12. safety remains `readOnly=true / ramWrites=0 / inputInjection=false`, with no Worker replacement/rewrite.

Construct at least one fresh adversarial fixture not copied mechanically from implementation tests.

## Write scope
Write only under:
- `parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/**`
- mandatory PM claim file
Do not modify `parallel/PYLAUNCH/**`.

## Verdict
PASS only if all production-path authority/safety checks pass on current HEAD.
If any defect exists, stop at the first precise P0/P1 blocker and identify the required fresh fix ownership.

Success stop condition:
`PASS — PYLAUNCH PARENTFRAME AUTHORITY FRESH QA`

No Owner Browser run.
Owner action: `NO`.
