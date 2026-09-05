# Alpha V1 Owner Release Gate (P20)

This directory implements the final human/release boundary. It does **not** move `alpha-live` during normal `run`, `confirm`, or `plan` operation.

## Owner flow

Run `WOF_ALPHA_FINAL_RELEASE_GATE.cmd` after P19 has emitted the final pinned candidate/attestation. The wrapper reuses P17's bounded final-acceptance flow with that exact candidate. Only when P17 ends at `READY_FOR_OWNER_VISUAL_CONFIRMATION` with W3 PASS, P16 HUD ingest, P18 canonical draw acknowledgement, exact identity consistency, and unchanged safety does it ask one question:

> 游戏里的提示是否稳定跟随正确的人物/怪物？请输入 YES 或 NO

`YES` records a real Owner visual PASS receipt. `NO` records an immutable FAIL receipt for that candidate/bundle combination and cannot be overwritten into PASS. Missing/stale/mismatched evidence writes a WAITING/REJECTED status and does not ask the question.

Test-only `confirm --fixture-mode --fixture-answer YES|NO` receipts are permanently marked `promotionEligible=false`; they cannot authorize a promotion plan.

## Promotion plan

A READY plan binds exact hashes for the P19 candidate/attestation, P17 bundle, and P20 real PASS receipt; records current `alpha-live` as the rollback/CAS old value; requires the candidate commit to be a fast-forward descendant; validates the exact W1 permanent updater release-file list; preserves read-only/no-input/no-fallback safety; and hashes a canonical `planCore` so the plan hash is deterministic for fixed inputs.

The plan path is immutable-by-name (`ALPHA_LIVE_PROMOTION_PLAN_<hash>.json`). Preparing it never updates a Git ref.

## Guarded apply

`apply` defaults to dry-run. A later PM-only execution must separately supply `--execute` and the exact `--confirm-plan-hash <hash>`. Apply re-hashes every artifact, re-reads `alpha-live`, rejects stale CAS state, re-checks fast-forward ancestry and W1 files, and never constructs a force push.

For a local bare repository, apply uses an exact-old `git update-ref <new> <old>` after transferring objects, which gives the fixture an atomic compare-and-swap ref update. For a real remote, Git's non-force push protocol does not expose an expected-old refspec without force-style options; therefore P20 re-reads immediately before a normal fast-forward push and fails on observed drift or push rejection. Force/force-with-lease/+refspec are intentionally forbidden.

A promotion result artifact is written only after the release ref is confirmed at the target commit. W1's existing updater then retains its own local last-known-good reset/rollback behavior.

## Commands

- `python parallel/OWNER_RELEASE/owner_release_gate.py confirm ...` — evidence gate + one Owner YES/NO receipt.
- `python parallel/OWNER_RELEASE/owner_release_gate.py plan --receipt <receipt> ...` — dry planning only.
- `python parallel/OWNER_RELEASE/owner_release_gate.py apply --plan <plan> --confirm-plan-hash <hash>` — verify/dry-run.
- `python parallel/OWNER_RELEASE/owner_release_gate.py apply --plan <plan> --confirm-plan-hash <hash> --execute` — explicit later PM apply path; **not invoked by P20 implementation**.
- `WOF_ALPHA_FINAL_RELEASE_GATE.cmd` — one command P17 -> visual question -> plan; always stops before actual promotion.
