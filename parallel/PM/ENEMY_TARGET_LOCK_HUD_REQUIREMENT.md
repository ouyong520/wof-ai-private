# WOF Future Danger — Target-Lock Player-Head HUD Requirement

Updated: 2026-09-02
Status: **AUTHORITATIVE ALPHA V1 PRODUCT REQUIREMENT**

## Product decision

Alpha V1 has exactly two mandatory in-game presentation surfaces:

1. **player-head danger reminder** — when current authoritative danger/target evidence says a supported enemy threatens P1/P2/P3, the warning is rendered above the targeted live player;
2. **enemy-head target tracker** — each supported live enemy shows its current target as `1P` / `2P` / `3P` above that enemy.

A fixed HUD remains a fail-closed fallback/diagnostic surface only when the player-head anchor cannot be proven current and valid. It is no longer sufficient as the primary Alpha V1 warning presentation.

This decision supersedes the earlier statement that player-head anchored warnings could wait for Beta.

## Player-head warning behavior

Enemy target/lock state determines **which player should be warned**. Required behavior:

- detect which player (P1 / P2 / P3) the supported danger belongs to;
- show the danger reminder above that targeted player's head;
- follow the targeted live player continuously;
- when targeting changes, immediately invalidate the old target-bound reminder and resolve the new target;
- never leave the reminder attached to the wrong player or at a stale screen coordinate;
- if player/camera/projection authority is stale, malformed, ambiguous, out of bounds or otherwise untrustworthy, suppress the anchored reminder and use the fixed fail-closed fallback.

## Enemy-head target tracker behavior

For supported live enemies:

- `target7E == 0` -> `1P`;
- `target7E == 4` -> `2P`;
- `target7E == 8` -> `3P`;
- unsupported/malformed/ambiguous target -> no confident enemy-head label;
- retarget must replace the old label immediately;
- disappearance, replacement, stale projection or epoch mismatch must not inherit an old label.

## P0 non-drift requirement

Alpha V1 is not accepted merely because either overlay can be drawn above a sprite once.

Both the player-head danger reminder and enemy-head target tracker must remain visually attached to the correct live object without noticeable drift during:

- player horizontal movement;
- player depth / lane movement;
- jump / vertical displacement, including ascent, apex, descent and landing;
- rapid forward/back movement;
- enemy horizontal/depth movement;
- simultaneous player + enemy movement;
- camera / stage scrolling, including rapid whole-screen scrolling;
- resize / fullscreen / DPR / drawing-buffer changes;
- P1 / P2 / P3 simultaneous presence;
- death / respawn / player object replacement;
- enemy disappearance / same-slot replacement;
- live retarget between P1 / P2 / P3.

**Any repeatable or clearly visible whole-screen/relative overlay drift in these scenarios is a P0 release blocker.**

The render path must follow fresh live identity + current projection state, not a cached screen coordinate. When fresh authority cannot keep up, fail closed by hiding/falling back rather than visibly drifting.

## Retarget / lifecycle safety

If an enemy retargets from P1 to P2:

1. invalidate the old P1 target-bound warning immediately;
2. resolve current P2 player anchor from fresh player/camera/projection state;
3. render above P2 only on a current valid anchor;
4. if P2 anchor is invalid or stale, use the fixed HUD fallback — never leave the marker above P1;
5. update the enemy-head target tracker from `1P` to `2P` with no stale hold.

A stale target warning/label must never survive across player respawn, enemy replacement, runtime/projection epoch change, resize mapping change, or uncertain continuity.

## Presentation scope

Alpha V1 may keep presentation minimal. No separate polished desktop GUI is required for release.

Minimum useful surfaces are:

- concise player-head danger reminder;
- compact enemy-head `1P` / `2P` / `3P` label;
- fixed HUD fallback / startup / disabled diagnostics.

Later additions such as richer icons, lead-time text, threat aggregation and UI polish are non-blocking after Alpha V1 unless separately promoted.

## Repository QA versus live proof

Repository/synthetic QA must aggressively cover bounds, stale state, epoch mismatch, lifecycle replacement, resize mapping and retarget behavior, but synthetic PASS is not proof that real Browser/WOF dynamic projection is visually stable.

Before Alpha V1 release, bounded real Browser/WOF acceptance must visibly exercise at minimum:

- left/right player movement;
- depth/lane movement;
- jump/vertical displacement;
- rapid forward movement with stage scrolling;
- player movement while camera moves;
- enemy movement while target labels are visible;
- at least one live P1 -> P2/P3 retarget;
- simultaneous supported enemies where practical;
- resize/fullscreen or equivalent drawing-buffer remap if used by the release environment.

The acceptance invariant is:

`玩家头顶危险提醒 + 怪物头顶目标跟踪 -> 跟随真实对象 -> 快速移动/跳跃/卷屏不明显漂移 -> 不确定时隐藏/降级 -> 改锁立即切换。`

## Safety

Presentation must not weaken existing Alpha safety constraints:

- read-only observer path;
- `ramWrites = 0`;
- no gameplay input injection;
- no Worker replacement;
- no Blob Worker rewrite;
- no target-selection or enemy-AI modification;
- no stale projection/identity authority fabricated for visual continuity.
