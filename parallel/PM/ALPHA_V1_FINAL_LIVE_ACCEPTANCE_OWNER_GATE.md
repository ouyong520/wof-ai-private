# Alpha V1 Final Live Acceptance — Owner Gate

Status: DEFERRED UNTIL P25 TERMINAL

P26 is historical terminal BLOCKED and must not be reopened or recovered. Its successor P28 (`ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD`) is now terminal COMPLETE / integrationReady=true with durable exact-tested provenance/session-chain evidence.

Current remaining pre-live implementation authority:
- P25 Final Acceptance Composite Capture Integration — still ACTIVE and must terminalize truthfully before the real-WOF final acceptance/release sequence begins.

Do not begin the real-WOF final acceptance/release sequence while P25 remains non-terminal. Do not create filler P29+ stages merely to occupy workers.

After P25 terminalizes and PM validates its RESULT evidence, resume this existing release path:

1. Stage the exact P19 candidate using `parallel\OWNER_STAGING\WOF_ALPHA_STAGE_FINAL_ACCEPTANCE.cmd` and consume the current staged canonical coordinator seam delivered by terminal P27.
2. Require W3 bounded normal-play qualification to reach explicit PASS/proven renderer source; otherwise STOP fail-closed. Repo-side W3 reverse engineering is exhausted and must not be reopened merely to avoid the Owner run.
3. Bind the same acceptance session through the terminal P28 provenance/session-chain implementation; do not fabricate or cross-run P22/P24/P17/P20/P23 evidence.
4. Only when P17 reaches exact `READY_FOR_OWNER_VISUAL_CONFIRMATION`, run `parallel\OWNER_RELEASE\WOF_ALPHA_FINAL_RELEASE_GATE.cmd` and ask exactly: `游戏里的提示是否稳定跟随正确的人物/怪物？请输入 YES 或 NO`.
5. A real YES only creates the bound visual receipt/promotion plan; promotion remains a separate guarded PM action with exact hashes, alpha-live CAS, fast-forward-only and no force push.
6. After confirmed promotion, converge the permanent W1 channel and run `parallel\OWNER_RELEASE_POSTVERIFY\WOF_ALPHA_POST_PROMOTION_VERIFY.cmd`; P23 alone owns `ALPHA_V1_FINAL_COMPLETE`.

Safety remains unchanged: readOnly=true, ramWrites=0, inputInjection=false, no guessed addresses, no screenshot/world-projection production coordinates, and no alpha-live movement before the guarded promotion action.

Current truth at this gate refresh:
- P28: terminal COMPLETE, real WOF NOT_RUN, Owner visual NOT_RUN, visibleProof NOT_PROVEN, alphaLiveMoved=false.
- P25: ACTIVE / non-terminal.
- Therefore real Owner live acceptance remains deferred only by P25 terminalization, not by P26/P28.
