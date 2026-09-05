# Alpha V1 Product Takeover W1 — Owner Permanent Live-Test Bootstrap Recovery V1 SUBRESULT

State: **SUBCOMPLETE / INTEGRATION-READY**

Scope: Alpha Owner-visible product only. No Collector / Unified Collector / Training Farm / 10训 code, runtime, tests, claims, packages, or evidence were used.

Recovery authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP_DEDUP_RECOVERY_START_PROMPT.md`

Recovery dedup key:
`alpha.v1.product-takeover.owner-permanent-live-test-bootstrap.claim-recovery-v1`

Recovery claim token:
`3ff0c1d49f83901d85f1c49e1d4f07e878da3965a3fab20d`

Implementation commit:
`d664618403b1ae83f6880ca4d3833202c299415f`

Controlled live ref established:
`refs/heads/alpha-live -> d664618403b1ae83f6880ca4d3833202c299415f`

## Implemented

- `WOF_ALPHA_SETUP_ONCE.cmd` now genuinely bootstraps when `%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN` / managed `.git` is absent. It creates only the dedicated Alpha SSH key when missing, reconstructs only its `.pub` when possible, performs one clear GitHub key-authorization step, then clones the private repo over GitHub SSH port 22.
- Git transport is SSH-only for the update channel (`git@github.com...` for bootstrap; `git@wof-alpha-github...` after install) with explicit port 22. No Git HTTPS/443 remote/fetch/clone path is used.
- Existing `%USERPROFILE%\.ssh` is preserved. The installer edits only the bounded `# WOF_ALPHA_BEGIN` / `# WOF_ALPHA_END` config block and never deletes/overwrites unrelated SSH/VPS keys.
- A controlled `alpha-live` branch is now the permanent Owner update pointer. `owner_live_retest_loop.ps1` fetches only `refs/heads/alpha-live`, not `main`, so unrelated main/docs/claim commits do not restart Alpha.
- Exactly one permanent Desktop entry remains: `Desktop\WOF_ALPHA_TEST.cmd`.
- Normal live updates stop/restart only `render_authority_measurement_entry.py`; Browser/Chrome is deliberately absent from the stop filter. Existing Alpha browser reuse behavior remains available to preserve current Browser/WOF when safe.
- Updater self-update is guarded by before/after hash, exact mutex release, controller relaunch, required-release-file validation, and rollback to the previous commit when a reset cannot be applied.
- `Documents\WOF_RESULTS\LATEST_ALPHA_FEEDBACK.txt` is continuously maintained as the obvious latest status/feedback path.
- No subsequent ZIP/CMD/versioned launcher handoff is required; future controlled fixes are delivered by moving `alpha-live` and the same Desktop path detects/applies them.

## Focused implementation acceptance

Focused contract test added:
`parallel/PYLAUNCH/tests/test_owner_permanent_live_bootstrap_w1.py`

Result against the exact blobs committed in `d664618403b1ae83f6880ca4d3833202c299415f`:

`7 passed`

The committed blob SHAs were verified equal to the tested local candidate blobs for all five W1 implementation/test files.

Acceptance mapping:

- A absent-managed-dir bootstrap: PASS by zero-state setup contract (`git clone` occurs before any managed-repo installer dependency; missing/partial managed repo is created/replaced only inside the dedicated managed path).
- B no Git HTTPS/443 dependency: PASS by SSH remote + explicit `-p 22` bootstrap and SSH host block/fetch path.
- C same `WOF_ALPHA_TEST.cmd` detects controlled release: PASS by permanent shim + `alpha-live` polling contract.
- D update applied + Alpha runtime restart: PASS by controlled fetch/reset + Alpha-runtime-only stop/start contract.
- E updater self-update safety: PASS by hash/mutex/relaunch + required-file validation/rollback contract.
- F no new ZIP/CMD/path: PASS by single Desktop entry and controlled live ref.

## External live boundary

A repository/Linux execution environment cannot truthfully prove the Owner machine's real outbound TCP/22 reachability, Windows OpenSSH/Git installation, or the one-time GitHub SSH-key authorization. Those are intentionally reduced to one precise setup gate and are **not** a reason to reintroduce manual package/version downloads.

Per the unified PM audit, do not ask the Owner to test W1 alone yet. W1 is integration-ready for PM to combine with W2 before the single real-WOF fixed-TEST gate.
