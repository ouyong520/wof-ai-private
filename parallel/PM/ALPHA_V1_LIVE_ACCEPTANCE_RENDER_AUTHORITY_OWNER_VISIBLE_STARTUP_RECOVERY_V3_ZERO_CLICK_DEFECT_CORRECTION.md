# Alpha V1 Render Authority Owner-Visible Startup Recovery V3 — Zero-Click Defect Correction

Status: **AUTHORITATIVE ADDENDUM FOR THE CURRENT ACTIVE V3 WORKER**

This does not create a new task, recovery, claim, or QA generation. It corrects a concrete defect found in the current V3 implementation.

## Concrete defect

Current `parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py` immediately falls through to `ONE_CLICK_REQUIRED` when `self._templates` is empty. It calls `_arm_once()` without first attempting the required automatic P1 head acquisition path.

That violates the product target already established by Owner/PM: **default zero-click automatic identification; one P1-head click is fallback only when automatic acquisition cannot safely establish a unique initial head authority.**

Do not close V3 with the current behavior.

## Required correction inside the existing V3

1. Preserve all already-landed V3 work: read-only screenshot capture, exact World/runtime authority, persistent tray/status, WOF browser reuse, lifecycle binding, multi-template tracking, confidence-loss hide/recovery, automatic packaging and current focused regression.
2. Add a real **automatic seed attempt before arming any click**. Reuse existing durable/runtime evidence first. The automatic path should use the strongest available combination of:
   - P1 current character identity / HUD portrait or equivalent existing character authority;
   - existing P1 lifecycle and RAM-derived coarse location only as bounded search prior, not final screen authority;
   - current game canvas screenshot;
   - bounded visual/sprite/tile evidence sufficient to distinguish the scene P1 from HUD portraits, enemies, weapons, effects and unrelated sprites.
3. If automatic acquisition yields one safe unique P1 head candidate, seed the first visual template automatically and proceed to `HEAD_TRACKING` with `ownerClickCount=0`.
4. Only after a bounded automatic attempt has failed safely or remained ambiguous may the state become `ONE_CLICK_REQUIRED` and arm the single click fallback.
5. Do not silently bind a HUD portrait itself as the scene head. HUD/portrait evidence may identify the character, but the final seed must be on the live scene P1 head.
6. Preserve fail-closed behavior: ambiguous automatic candidates => no overlay/marker; one-click fallback remains maximum one per authority generation.
7. After seed, continue automatic standing / walking / facing-change multi-template accumulation. If confidence is lost, hide immediately and auto-recover when the current live head is confidently reacquired.
8. Owner normal success path is now explicitly:

   `菜单6 -> 正常进游戏 -> 自动识别P1角色/头像 -> 自动定位场景P1头部 -> 正常玩 -> 自动多模板跟踪 -> 自动完成`

   Expected normal click count: **0**.

   Allowed fallback only when automatic seed cannot safely resolve: **最多点一次 P1 人物实际头部**.

## Focused regression requirement

Do not open a new QA generation. Extend the existing V3 focused module regression so it proves at least:

- safe automatic seed => `HEAD_TRACKING` with `ownerClickCount == 0` and click UI never armed;
- ambiguous/unsafe automatic seed => no wrong marker, then exactly one fallback click may be armed;
- second click remains impossible;
- HUD portrait / lookalike / enemy / effect candidates are not accepted as scene P1 head;
- lifecycle/runtime/layout invalidation revokes stale authority;
- confidence loss hides and confident reacquisition restores;
- package manifest contains the corrected zero-click-first runtime.

Run one coherent focused regression after the correction; do not repeat already-green unrelated suites.

## Exit

V3 may proceed to immutable package / durable RESULT / claim COMPLETE only after the zero-click-first path above is implemented and the final package actually selects that corrected runtime. Do not ask Owner to test the current pre-correction package.
