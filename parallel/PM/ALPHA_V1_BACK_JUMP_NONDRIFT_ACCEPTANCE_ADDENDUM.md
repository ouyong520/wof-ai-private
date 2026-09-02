# Alpha V1 后跳（Back Jump）Non-Drift 实机验收补充

Status: **AUTHORITATIVE PM ACCEPTANCE ADDENDUM FOR ALPHA V1**

This addendum clarifies the existing Alpha V1 P0 non-drift requirement. It does not change danger rules, target semantics, Transport authority, input behavior, projection constants, or product UI scope.

## Why this is explicit

《三国志II / Warriors of Fate》的后跳是一个比普通跳跃更强的组合运动样本：角色在跳跃期间同时发生快速反向 X 位移、Z/垂直位移以及朝向/动画状态变化。它能够暴露“普通跳或普通左右移动单独看不出来”的头顶锚点滞后、旧坐标残留和投影不同步。

The existing authoritative requirement already includes complete jump plus rapid forward/back movement. This addendum makes the game-specific rear/back-jump action an explicit mandatory subcase of those existing P0 gates; it is not a new product feature.

## Final Browser/WOF acceptance requirement

In the final bounded real Browser/WOF session, perform at least one complete rear/back-jump cycle using normal gameplay input:

- start from a stable live player identity;
- execute the actual game rear/back-jump (jump followed by immediate movement opposite the current facing direction);
- retain evidence through takeoff, backward travel, apex, descent and landing;
- require the player-head anchor/reference to remain visually attached without repeatable lag, trailing, snapping to the takeoff coordinate, or using an old mapping/epoch;
- if the real Alpha danger warning is active during the rear-jump, the actual `[危险]` surface must remain attached to that player through the full action;
- if the warning is not naturally active during that exact action, the rear-jump still closes the combined X+Z projection stress subcase, while the actual player-warning surface must be proven separately under the existing fast-motion/jump live gates;
- any anchored rendering from stale/invalid authority remains a P0 failure and must fail closed to hide/fixed HUD as already specified.

Enemy `1P / 2P / 3P` semantics are unchanged. If supported enemies remain visible during the rear-jump, their labels must continue to track their own live enemy identities normally; no additional enemy behavior is inferred from the player action.

## Evidence / tooling boundary

This addendum does not require changing the current proof runtime or `RUN_MANIFEST.json` merely to add a new named phase. It is an explicit operator/visual subcase inside the existing jump + rapid forward/back + player-motion proof windows. The future live result should record that the rear-jump was exercised and whether any visible drift occurred.

Repository/synthetic evidence cannot satisfy this requirement. Only the bounded real Browser/WOF run can close it.

## Release rule

Any repeatable or clearly visible player-head overlay drift during the rear/back-jump is a **P0 release blocker**.
