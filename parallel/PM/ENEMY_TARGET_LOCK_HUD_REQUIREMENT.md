# WOF Future Danger — Enemy Target-Lock HUD Requirement

Updated: 2026-09-01
Status: AUTHORITATIVE PRODUCT REQUIREMENT

## Product intent

The preferred future in-game target indicator is **enemy-anchored**, not player-anchored.

For every visible/trackable enemy:
- determine which player that enemy is currently targeting/locking;
- render `1P`, `2P`, or `3P` above that enemy;
- when the enemy retargets, change the label immediately to the new player;
- the label must follow that enemy's visual position continuously.

Example:
- enemy A targets P2 -> show `2P` above enemy A;
- enemy B targets P3 -> show `3P` above enemy B;
- if enemy A retargets P1 -> its marker changes to `1P` without leaving stale `2P` on the old state.

## Non-drift requirement

This feature is not accepted merely because a label can be drawn near an enemy once.

The marker must remain visually attached to the same enemy without noticeable drift during:
- enemy horizontal movement;
- depth / lane movement;
- jump / knockback / vertical displacement when applicable;
- camera / stage scrolling;
- resize / fullscreen / DPR / drawing-buffer changes;
- multiple simultaneous enemies;
- enemy slot reuse / despawn / respawn;
- retarget between P1/P2/P3.

A stale marker must never survive onto a reused enemy slot or another enemy.

## Identity / lifecycle rule

Anchor identity must follow the current live enemy lifecycle identity, not merely `slot + type`.

If continuity is uncertain, fail closed for the anchored label rather than display it on the wrong enemy.

Retarget must invalidate any target-bound display state immediately.

## Presentation

Minimum label:
- `1P` / `2P` / `3P`.

Optional later additions may include:
- downward arrow;
- warning color / urgency;
- attack family/danger icon;
- lead time.

These additions must not compromise stable anchoring.

## Alpha / Beta scope

This requirement must **not delay the first trustworthy Alpha**.

- Alpha may retain the proven fixed in-game HUD as the safe fallback / first-release surface.
- Enemy-anchored non-drifting target labels are a high-value Beta/near-term presentation goal and may use independent accelerator/reverse-engineering work when it does not conflict with Alpha blockers.
- Once enemy anchoring is promoted, fixed HUD remains fallback whenever projection/anchor state is invalid or stale.

## Acceptance direction

Final acceptance must prove the marker remains on the correct enemy while both enemy and camera move, and that P1/P2/P3 retarget changes occur without stale labels or cross-enemy inheritance.

The desired user experience is:

`怪物锁定谁 -> 怪物头顶稳定显示对应 1P / 2P / 3P -> 跟随怪物移动 -> 不漂移。`
