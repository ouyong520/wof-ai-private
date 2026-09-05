# Alpha V1 P21 — Pre-Promotion Exact Candidate Staging

This directory owns the isolated pre-promotion acceptance harness only. It never rebuilds P19, never applies P20, never updates `alpha-live`, and never edits the permanent W1 updater.

## Owner / PM entry

Run `WOF_ALPHA_STAGE_FINAL_ACCEPTANCE.cmd` from a checkout that contains the P19 maintained latest pointer. The harness:

1. resolves and verifies the exact READY P19 pointer, final candidate and attestation;
2. verifies P15/P16/P17/P18 ancestry plus every attested critical runtime blob at the candidate source commit;
3. snapshots `alpha-live` and the permanent W1 managed repo, then creates a detached worktree under `%LOCALAPPDATA%\WOF_ALPHA_STAGING\...`;
4. starts the candidate's own `render_authority_measurement_entry.py` with explicit staged acceptance commit/package identity while preserving Browser/WOF and disabling fixed-draw/legacy staging ambiguity;
5. invokes the staged candidate's P17 orchestrator, lets P17 run the existing bounded W3 qualification, snapshots fresh same-package P16 evidence, collects P18 draw evidence through read-only CDP when exact P16 identity is available, then reruns P17 against those run-specific evidence files;
6. stops the staged runtime, removes the detached worktree, verifies source/permanent refs and worktree state are unchanged, and restores a previously running permanent Alpha runtime only through the deterministic W1 runtime command contract.

Run receipts are written under `~/Documents/WOF_RESULTS/ALPHA_P21_STAGING_ACCEPTANCE/`. `READY_FOR_OWNER_VISUAL_CONFIRMATION` is the highest automatic state. It is **not** visible proof, does not record Owner visual acceptance, and does not promote `alpha-live`.

If P19 is missing or not READY the harness returns `WAITING_FOR_P19` before staging. Any candidate/attestation/hash/ancestry/blob mismatch fails closed.
