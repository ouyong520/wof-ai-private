# Alpha V1 P28 — Post-Candidate Implementation Continuation

Status: PM continuation authority for the existing ACTIVE P28 claim.

Stage: `ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD`

Existing claimToken: `69884841cf571855163ab7db0ac663dc`

Do not create a new claim and do not recover P26.

## Durable state to reconcile

The last P28 PROGRESS checkpoint recorded candidate commit:

`9a02856edf9be1768cd0fc8b8235cb13ac3b4cfd`

and marked the stage ready to run fresh focused tests against that exact candidate.

However, Git history later contains a newer P28-owned implementation commit:

`765c08d676709b094b993849b048948aa74c2d58` — `WORKER_IMPL P28 durable session state machine`

which adds:

`parallel/OWNER_ACCEPTANCE_PROVENANCE/durable_session.py`

Therefore `9a02856...` is no longer eligible to be the final tested candidate for the complete P28 implementation. No terminal-significant test result may be bound to `9a02856...` as if it covered the newer implementation.

## Required continuation

1. Re-read latest main, the P28 canonical/stage claims, and verify the exact existing claimToken remains ACTIVE.
2. Read the current P28 PROGRESS and reconcile every P28 implementation commit newer than its recorded candidate/checkpoint.
3. Update P28 PROGRESS before final testing so `completed`, `remaining`, implementation commits, changed-file set, and candidate state reflect current Git reality.
4. Inspect the current full `parallel/OWNER_ACCEPTANCE_PROVENANCE/**` implementation and finish any remaining bounded implementation needed by the P28 START_PROMPT.
5. Create a new durable implementation candidate commit containing the exact complete bytes to be terminal-tested. This commit must be at or after `765c08d...` and must include every final P28-owned implementation file.
6. Git-readback that candidate and record its exact commit SHA plus the exact changed-file/blob map in PROGRESS.
7. Only then run fresh P28 focused tests against the exact read-back candidate bytes. Never reuse P26 historical 13/13 and never bind tests from `9a02856...` to newer bytes.
8. If any implementation byte changes after testing begins, create another candidate and rerun every affected terminal-significant focused check.
9. Publish RESULT with `testedCommit` bound only to the final actually tested candidate.
10. Close the exact-token canonical/stage claims, then update PROGRESS to TERMINAL/100 and write the final WORKER_RESULT commit.

Keep `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, and `alphaLiveMoved=false`. Do not run real WOF, Owner YES/NO, promotion, input injection, memory writes, screenshot/world-projection production coordinates, or guessed coordinate fallback.

If the execution window becomes constrained, updating P28 PROGRESS takes priority over optional additional work. Do not stop with chat-only state.
