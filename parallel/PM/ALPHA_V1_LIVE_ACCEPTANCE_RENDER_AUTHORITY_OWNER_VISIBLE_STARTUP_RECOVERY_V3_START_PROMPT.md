# Alpha V1 Live Acceptance — Render Authority Owner-Visible Startup Recovery V3

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_OWNER_VISIBLE_STARTUP_RECOVERY_V3`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.render-authority-owner-visible-startup-recovery-v3`
dedupMode: `exclusive`

## PM authority

Owner live evidence on the published Render Authority V2 measurement package shows a real product-entry defect: menu 6 prints that capture started, then only opens a browser; the prior tray/status icon is gone and there is no visible WAITING / WORLD LOCKED / MEASURING / COMPLETE / BLOCKED feedback. Current code launches the measurement child via `pythonw.exe`, so runner stdout is invisible, and when no CDP endpoint exists it calls `launch_debug_browser(..., game_url=None)`, so it may open only a debug browser without taking Owner to the existing WOF entry.

This is a narrow implementation recovery. Preserve the completed V2 read-only capture core and exact World 921031 authority. Do not return to projection calibration and do not ask Owner to retest the broken V2 package.

Superseded historical authority remains untouched:
- V2 dedupKey: `alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2`
- V2 RESULT: `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2_RESULT.md`
- V2 historical canonical/stage claims currently remain ACTIVE; do not rewrite, close, steal or reuse them.

## Required scope

1. Re-read latest `main`, root `AGENTS.md`, `STAGE_DEDUP_GUARD.md`, `TESTING_CADENCE_POLICY.md`, V2 RESULT and current claims. Do duplicate preflight first. If this V3 logical task is already ACTIVE/COMPLETE/superseded, NO EXECUTION.
2. Acquire fresh V3 canonical + stage claims create-only before implementation.
3. Reuse the existing known-good Alpha/PYLAUNCH Owner browser-entry path so menu 6 opens or reconnects to the correct WOF flow; do not guess a new game URL and do not disturb an already valid Owner browser session.
4. Restore immediate Owner-visible status, preferably by reusing the existing tray/status architecture rather than creating another UI stack. At minimum expose: STARTING/WAITING_FOR_WOF, EXACT_WORLD_LOCKED, MEASURING with progress, RUNTIME_REDISCOVERY, COMPLETE with ZIP path, and precise BLOCKED. The status surface must remain visible while the browser/game is open.
5. Do not let `pythonw.exe` silently swallow the only progress/error channel. Background execution is allowed only when an equivalent visible status surface receives the same authoritative state.
6. Preserve V2 safety and behavior: exact World 921031, current Worker/runtime generation, read-only CDP, `ramWrites=0`, `inputInjection=false`, no manual calibration, legacy projection disabled, production overlay suppressed until render authority is proven, automatic evidence ZIP.
7. Finish the coherent module, then run only focused regression/self-checks for menu-6 startup, browser reuse/launch, visible state propagation, completion/blocking, runtime-generation rediscovery and package manifest integrity. No step-by-step QA chain.
8. Publish a new immutable successor package, durable RESULT, then close only this V3 canonical/stage claims COMPLETE. Next Owner action must again be only menu 6 + normal play 20–30 seconds.

## Exit

Only: `COMPLETE` with new immutable Owner package ready for one focused live run; precise `BLOCKED` that truly requires Owner manual intervention; or duplicate `NO EXECUTION`.

If an environment/setup problem appears, do not stop at one error line. Continue automatic diagnosis and all safe repairable environment fixes until `SETUP COMPLETE` / task `COMPLETE`, or a precise blocker that genuinely requires Owner action. Use complete functional modules as the test boundary; do not test every small edit. 少汇报，直接执行。
