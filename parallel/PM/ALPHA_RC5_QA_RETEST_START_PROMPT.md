# WOF Alpha RC5 Fresh Independent QA / Retest — Start Prompt

You own a fresh, independent QA stage for the current WOF Alpha RC5 candidate.

Repository:
- `ouyong520/wof-ai-private`

## Authoritative owner Browser evidence

The owner has now performed the one required real-Browser RC5 room-entry retest:

- current `WOF Future Danger Alpha RC5 Safe Bootstrap` enabled;
- Browser Acceptance Helper disabled;
- game **can enter a room normally**;
- there is currently **no Alpha HUD / warning output**.

Interpret the two observations separately:

1. The former P0 "Alpha prevents room entry" is now real-Browser CLOSED if source/regression independently supports the RC5 no-Worker-replacement design.
2. No HUD/warnings is currently expected when no safe non-replacing external live-Worker transport pairs with RC5. Do not misclassify intentional `WAITING_EXTERNAL_TRANSPORT` / warning-silent behavior as proof that the detector itself passed Browser acceptance.

## QA scope

Read and independently audit:
- `product/alpha/ALPHA_RC5_REPORT.md`
- `product/alpha/wof_alpha_bootstrap.user.js`
- `product/alpha/regression.mjs`
- `product/alpha/regression_result.json`
- current Alpha core/loader/HUD/manifest as needed
- prior RC4 independent QA evidence
- `parallel/PM/ALPHA_BROWSER_ACCEPTANCE_BLOCKER.md`

Do NOT modify `product/alpha/**`.

Independently verify at minimum:
- RC5 never replaces/wraps `window.Worker`;
- no Blob Worker / rewritten game Worker URL path remains in the normal RC5 bootstrap;
- gameplay remains fail-open when Alpha cannot attach;
- warnings remain fail-closed/silent without an authoritative detector transport;
- no pre-pair HUD/loader attach can block gameplay;
- session/channel isolation remains safe;
- RC4 runtime-diag immediate warning invalidation remains preserved;
- exact World 921031 full 1 MiB CPU-logical SHA-256 gate remains preserved in the detector path;
- exactly two T18 current-level production rules remain active;
- F1-F4 remain quarantined;
- same-type slot replacement safety remains preserved;
- target/side/UNKNOWN safety remains preserved;
- read-only / `ramWrites=0` / no gameplay input injection remains true.

## Required verdict separation

Your result must explicitly distinguish:

### A. RC5 room-entry repair verdict

Can independent QA accept the owner's real-Browser result plus the source/regression evidence and close the specific P0 "Alpha prevents room entry"?

### B. Alpha release verdict

Do **not** declare Alpha release-ready merely because room entry is fixed. A usable Alpha still requires a proven safe non-replacing live-Worker transport that actually connects the detector and allows the bounded real Browser acceptance to exercise HUD/warnings.

The active Python Launcher foundation is allowed to investigate that external transport separately. Do not duplicate its implementation and do not modify `parallel/PYLAUNCH/**`.

## Stop condition

Stop with one of:

- `PASS — RC5 ROOM-ENTRY REPAIR QA`; specific P0 closed, but Browser Alpha remains blocked on safe live-Worker transport / later full Browser acceptance; or
- a precise P0/P1 finding in RC5 source/regression that invalidates the room-entry repair.

Write independent QA findings under a fresh non-product area such as `parallel/ALPHAQA_RC5/**` and commit them to GitHub.
