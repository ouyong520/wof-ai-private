# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — old PYLAUNCH proof exposed a real Worker-discovery defect; do not rerun it yet

## Current owner action required: YES — open fresh work stages only

Do **not** reopen the game or rerun the old `RUN_WINDOWS_PROOF.cmd` now.

The previous real Windows run already gave enough evidence:
- Chrome/CDP connected;
- game entered normally and remained playable;
- readOnly=true / ramWrites=0;
- but Launcher failed to find the real WOF page/Worker and reported `no gstyphoon worker target`.

That is now an engineering fix task, not an owner-operation task.

## Fresh stage A — PYLAUNCH Worker discovery fix (P0)

Use:
- `parallel/PM/PYLAUNCH_WORKER_DISCOVERY_FIX_START_PROMPT.md`

This stage must fix real Chrome/WOF target discovery, keep the game fail-open/read-only, and return with a new direct-download one-click proof.

## Fresh stage B — Chinese owner UX pass

Use:
- `parallel/PM/TOOLS_CHINESE_UX_PASS_START_PROMPT.md`

This stage localizes Browser Fleet / WOF-052L / Operator Toolkit owner-facing text to Simplified Chinese. It must not modify PYLAUNCH while stage A owns that directory.

## Fresh stage C — Owner one-click package/bootstrap

Use:
- `parallel/PM/OWNER_ONECLICK_PACKAGE_START_PROMPT.md`

This stage solves the owner installation problem: one direct download link -> one Chinese file/tiny ZIP -> double-click -> tools install/update automatically -> Chinese WOF Toolkit opens.

## Old stages that can remain closed

Do not reopen these old implementation/prep threads:
- RC5 independent QA — PASS and closed;
- Browser Fleet implementation — repository-side READY, waiting combined live proof;
- WOF-052L Recorder implementation — READY for live proof, but wait for Worker discovery fix;
- Operator Toolkit core implementation — Windows V1 READY;
- Safe Transport Integration Prep — contract complete;
- previous PYLAUNCH proof stage — its result is now the discovered P0 evidence.

## Human testing policy

No more human Browser tests until the fresh PYLAUNCH fix stage explicitly says:

`FIX READY — 只剩一次新的真人 Windows 一键 Proof`

At that point PM should give the owner a direct downloadable Chinese one-click file. Do not ask the owner to browse GitHub directories, use DevTools, select Worker Console, or paste JavaScript.

## Alpha Browser acceptance

Still PAUSED. It resumes only after:
1. PYLAUNCH real Worker/WASM/World proof PASS;
2. fresh Alpha safe transport integration implementation;
3. integrated regression PASS.
