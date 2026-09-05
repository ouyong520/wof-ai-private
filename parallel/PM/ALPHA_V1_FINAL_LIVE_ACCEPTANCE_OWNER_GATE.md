# Alpha V1 Final Live Acceptance — Owner Gate

Status: READY FOR OWNER LIVE EXECUTION

P26 remains historical terminal BLOCKED and must not be reopened or recovered. Its successor P28 (`ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD`) is terminal COMPLETE / integrationReady=true with durable exact-tested provenance/session-chain evidence.

P25 (`ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION`) is now terminal COMPLETE / integrationReady=true. Its post-P27 deterministic committed readback confirms that the existing P25 composite path consumes the same-session maintained P10 canonical coordinator surface exposed through terminal P27.

Therefore all repository-side pre-live prerequisites are terminal. Do not create filler P29+ stages and do not reopen repo-side W3 reverse engineering merely to avoid the required Owner run.

## Final live sequence

1. On the Owner Windows machine, reuse the existing repository, managed Python/venv, browser, and already-present Git objects. Do not reinstall or redownload dependencies merely because a prior live attempt failed. The staging code fetches the exact P19 commit only if that commit is missing locally.
2. Stage the exact P19 candidate using `parallel\OWNER_STAGING\WOF_ALPHA_STAGE_FINAL_ACCEPTANCE.cmd`. This staging run creates an isolated detached Git worktree, starts the staged runtime, and invokes the bounded W3 qualification path through P17 without moving alpha-live.
3. During the bounded W3 normal-play capture, the Owner must play normally in exact World 921031. Require explicit W3 `PASS` / proven renderer source; otherwise STOP fail-closed and preserve the generated evidence bundle for diagnosis. Do not fabricate PASS and do not substitute screenshot/world-projection/guessed coordinates.
4. Bind the same acceptance session through terminal P28 provenance/session-chain implementation. Do not cross-run or synthesize P22/P24/P17/P20/P23 evidence.
5. Only when P17 reaches exact `READY_FOR_OWNER_VISUAL_CONFIRMATION`, run `parallel\OWNER_RELEASE\WOF_ALPHA_FINAL_RELEASE_GATE.cmd` and ask exactly: `游戏里的提示是否稳定跟随正确的人物/怪物？请输入 YES 或 NO`.
6. A real YES only creates the bound visual receipt/promotion plan; it does not itself move alpha-live. Promotion remains a separate guarded PM action with exact hashes, alpha-live CAS, fast-forward-only and no force push.
7. After confirmed guarded promotion, converge the permanent W1 channel and run `parallel\OWNER_RELEASE_POSTVERIFY\WOF_ALPHA_POST_PROMOTION_VERIFY.cmd`; P23 alone owns `ALPHA_V1_FINAL_COMPLETE`.

## Failure/retry semantics

A failed staging/W3/Owner-visible attempt does not authorize deleting the local repository, managed venv, browser environment, or cached Git objects. Preserve the existing environment and evidence, fix only the concrete blocker, then rerun the bounded step. Normal retry should not repeat a full dependency download/install cycle.

## Safety

Safety remains unchanged throughout: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no guessed addresses, no screenshot/world-projection production coordinates, and no alpha-live movement before the separately guarded promotion action.

Current truth at this gate refresh:
- P25: terminal COMPLETE / integrationReady=true; real WOF NOT_RUN; Owner visual NOT_RUN; visibleProof NOT_PROVEN; alphaLiveMoved=false.
- P28: terminal COMPLETE / integrationReady=true; real WOF NOT_RUN; Owner visual NOT_RUN; visibleProof NOT_PROVEN; alphaLiveMoved=false.
- P27: terminal COMPLETE and staged maintained P10 canonical-feed seam exposed.
- W3 live renderer-source qualification: still requires the bounded Owner normal-play run.
- Final live gate: READY FOR OWNER LIVE EXECUTION.
