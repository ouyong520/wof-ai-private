# WOF Future Danger — Target-Lock Player-Head HUD Requirement

Updated: 2026-09-01
Status: AUTHORITATIVE PRODUCT REQUIREMENT

## Product intent

The preferred future in-game target indicator is **player-head anchored**.

Enemy target/lock state determines **which player should be warned**, but the visual indicator is rendered above the targeted player character, not above the enemy.

Required behavior:
- detect which player (P1 / P2 / P3) an enemy is currently targeting/locking;
- show the corresponding target warning above that targeted player's head;
- the indicator follows the targeted player character continuously;
- when targeting changes, immediately remove the old target-bound indicator and move/show the warning above the newly targeted player;
- do not leave the indicator attached to the enemy.

Example:
- an enemy targets P2 -> warning appears above P2's character;
- that enemy retargets P3 -> P2 warning is invalidated immediately and the warning appears above P3;
- if multiple enemies target the same player, their warning information may later be aggregated near that player's anchor without changing target correctness.

## Non-drift requirement

This feature is not accepted merely because a label can be drawn above a player once.

The marker must remain visually attached to the correct player without noticeable drift during:
- player horizontal movement;
- depth / lane movement;
- jump / vertical displacement;
- camera / stage scrolling;
- resize / fullscreen / DPR / drawing-buffer changes;
- P1 / P2 / P3 simultaneous presence;
- death / respawn / player object replacement;
- live enemy retarget between P1 / P2 / P3.

The anchor must follow the current live player identity and projection state, not a stale screen coordinate.

## Retarget / lifecycle safety

Target-bound display identity includes the target player.

If an enemy retargets from P1 to P2:
1. invalidate the old P1 target-bound indicator immediately;
2. resolve current P2 player anchor from fresh player/camera/projection state;
3. render on P2 on the next fresh update;
4. if P2 anchor is invalid or stale, use the fixed HUD fallback — never leave the marker above P1.

A stale target marker must never survive across player respawn/object replacement or uncertain continuity.

## Presentation

Minimum useful target indication may include:
- `1P` / `2P` / `3P` target identity;
- downward arrow / lock indicator;
- warning color / urgency.

Later additions may include:
- attack family / danger icon;
- lead time;
- multiple-threat aggregation.

The visual design must not compromise stable anchoring.

## Alpha / Beta scope

This requirement must **not delay the first trustworthy Alpha**.

- Alpha may retain the proven fixed in-game HUD as the safe fallback / first-release surface.
- Player-head anchored, non-drifting target warnings are a high-value near-term/Beta presentation goal.
- Existing HUDANCHOR player projection research is the relevant technical lineage.
- Fixed HUD remains fallback whenever player/camera/projection state is invalid or stale.

## Acceptance direction

Final acceptance must prove the warning remains above the correct targeted player while the player and camera move, jump, scroll, resize/fullscreen, and while live enemy targeting changes between P1/P2/P3.

The desired user experience is:

`怪物锁定谁 -> 在被锁定角色头顶显示提示 -> 跟随角色移动 -> 不漂移 -> 换锁时立即切到新角色。`
