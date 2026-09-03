# Alpha V1 Render Authority Owner-Visible Startup Recovery V3 — PM Scope Correction

Status: **AUTHORITATIVE ADDENDUM FOR THE ACTIVE V3 WORKER**

This addendum does not create a new task, dedup key, claim, recovery, or QA generation. It refines the already ACTIVE V3 implementation scope.

## Product success path

The required normal path is now:

`菜单 6 -> 正常进游戏 -> Camera 自动准备 -> 最多点一次 P1 头顶 -> 正常玩 -> 自动完成`

The Owner must not be asked to perform the old long calibration workflow, inspect candidate math, choose Y / Y-Z / Y+Z, or manually run menu 7/8 packaging.

## Mandatory head-visual authority

V3 must add automatic P1 head-visual acquisition/tracking instead of relying only on RAM x/y/z or unverified memory-structure candidates.

Required behavior:

1. After exact World 921031 and current runtime generation are accepted, automatically capture the live game image/canvas surface needed for bounded visual head tracking.
2. For P1, automatically crop a bounded head region from the current actor image. If the system cannot establish the initial head region safely, it may request **at most one** Owner click on P1 head for the current/revoked authority generation.
3. Automatically retain a small multi-sample head template set rather than one static image. At minimum cover samples from ordinary standing / walking / facing-direction changes when observed naturally.
4. Track P1 head center continuously across frames using the live visual samples plus existing lifecycle/runtime authority. Do not treat one static template as sole long-term authority.
5. If head confidence becomes ambiguous or drops below the safe threshold, suppress the overlay immediately. When confidence returns, restore automatically. Prefer no overlay over wrong placement.
6. Do not silently bind weapons, effects, projectiles, UI portraits, or unrelated sprites as the actor head.
7. Room re-entry, respawn, runtime-generation replacement, resize/fullscreen/layout changes, or any invalidated visual authority must revoke stale tracking and rediscover/reacquire safely.

## Sprite/ROM architecture context

The implementation must respect the real CPS1 composition model: graphical ROM data is tiles/sprite pieces plus palette and runtime composition; a character head is generally part of a composed animated sprite, not one independent permanent bitmap. Therefore:

- do not assume one immutable head PNG represents all actions;
- standing / walking / turning samples should be accumulated automatically when available;
- ROM/tile data may be used locally/read-only as supporting disambiguation, never as committed game content and never as sole live authority;
- action/flip/tile composition changes must be handled by bounded multi-template/live tracking rather than one frozen crop.

## Owner interaction rule

Normal successful use must not require the Owner to:

- remember a left/right/depth/jump/fullscreen checklist;
- inspect Y / Y-Z / Y+Z candidates;
- choose a projection model;
- repeat multi-click calibration;
- manually package evidence with menu 7/8.

If one missing motion/state is genuinely required, show only **one instruction at a time** (for example, `现在跳一次`). Detect completion automatically, clear that instruction, and advance automatically. Do not present a checklist.

## Visible state

The V3 owner-visible status surface must reflect the real automatic flow, including at least:

- STARTING / WAITING_FOR_WOF
- EXACT_WORLD_LOCKED
- CAMERA_PREPARING
- HEAD_ACQUIRING or ONE_CLICK_REQUIRED when genuinely needed
- HEAD_TRACKING
- optional one-action request when evidence is missing
- MEASURING / RUNNING
- RUNTIME_REDISCOVERY
- COMPLETE with automatic ZIP path
- precise BLOCKED

`pythonw.exe` must not hide the only authoritative status channel.

## Safety / frozen contracts

Keep exact World 921031, current Worker/runtime-generation binding, read-only CDP, `ramWrites=0`, `inputInjection=false`, fail-closed overlay suppression, automatic evidence packaging, and all previously completed identity/re-entry/safety contracts.

Do not return to guessed projection constants or manual Y/Y-Z/Y+Z calibration.

## Testing cadence

Implement this as one coherent functional module together with the V3 visible-startup fix, then run focused regression for visual acquisition/tracking, one-click maximum, confidence loss/recovery, lifecycle/runtime invalidation, browser/menu-6 startup, status propagation, and automatic packaging. Do not test every small edit and do not open a parallel QA/recovery chain.

## Exit

V3 is not COMPLETE merely because the tray/status UI is restored. Completion requires a new immutable successor package whose intended Owner path is exactly:

`菜单 6 -> 正常进游戏 -> Camera 自动准备 -> 最多点一次 P1 头顶 -> 正常玩 -> 自动完成`

If an environment/setup problem appears, continue automatic diagnosis and all safe repairable fixes until task COMPLETE / SETUP COMPLETE, or a precise blocker that genuinely requires Owner action. 少汇报，直接执行。
