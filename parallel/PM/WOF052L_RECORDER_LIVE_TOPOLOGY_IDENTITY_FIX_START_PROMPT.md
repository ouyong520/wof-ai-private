# WOF-052L Recorder Live Topology + Identity Cache Fix Start Prompt

stageId: `WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_FIX_V1`
priority: `P0`

## Dedup / claim
Before work, follow `parallel/PM/STAGE_DEDUP_GUARD.md`.
If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`
If already claimed, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`
Otherwise atomically claim this stage under `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_FIX_V1.json` and continue.

## Read first
Read current HEAD, especially:
- `parallel/WOF052L_RECORDER_QA_HARDENING/RESULT.md`
- `parallel/WOF052L_RECORDER/**`
- the fresh adversarial QA fixture under `parallel/WOF052L_RECORDER_QA_HARDENING/**`
- relevant Browser Fleet / Discovery V2 contracts for association semantics

## Exact blockers to close
Fresh independent QA found:
1. **P0**: two already-live pages can drift onto the same Worker during the 10-second live-topology audit gap; the next `poll_rooms()` can still collect evidence before the ambiguity is discovered.
2. **P1**: recreated/reloaded Worker authority can reuse cached exact-World identity keyed only by `targetId`; a replacement runtime must not inherit stale World 921031 authority.

## Required fix properties
### P0 live topology
- before any evidence polling for a live room, current Worker↔page ownership must still be freshly proven unique;
- no positive-duration audit gap may permit evidence polling after topology has become ambiguous;
- if one Worker is now related to multiple live pages, finalize/censor affected rooms before later evidence polling;
- unrelated rooms remain isolated and may continue;
- do not hide transitions by skipping already-live pages when their current ownership must be re-proven.

### P1 identity lifecycle
- exact World 921031 identity authority must belong to the current Worker runtime/lifecycle, not merely `targetId`;
- reload/recreation/session replacement must invalidate old identity authority;
- a reused target id with a new runtime must receive a fresh identity probe before admission;
- wrong identity after recreation must fail closed;
- do not weaken exact SHA authority.

## Regression
Absorb the independent QA adversarial fixtures into Recorder-side tests and add targeted production-path tests proving:
- live/live unique -> shared Worker transition finalizes before next evidence poll;
- two distinct Workers remain independent;
- topology reproof failure censors/finalizes rather than deferring evidence;
- reused targetId after runtime recreation cannot inherit cached identity;
- correct fresh recreation can re-admit only after a new exact identity proof;
- endpoint confinement / Chinese UX / 10-room isolation remain unchanged.

## Safety
Keep:
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no `window.Worker` replacement/wrap
- no Blob/Data/ObjectURL Worker rewrite
- no game RAM writes
- no game input injection

## Write scope
Write only under:
- `parallel/WOF052L_RECORDER/**`
- minimal existing Recorder-owned wrapper adaptation only if strictly required by the same fix
- mandatory claim file
Do not modify PYLAUNCH, Prospective, Alpha, LIVE_PROOF_BUNDLE, Browser Fleet core, or product/alpha.

## Stop condition
Success:
`WOF052L RECORDER LIVE TOPOLOGY + IDENTITY FIX READY — READY FOR FRESH QA`
Or one precise blocker.

Do not request Owner Windows/WOF testing.
Owner action: `NO`.
