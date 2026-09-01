# HUDANCHOR Player-Follow Priority Decision

Updated: 2026-09-01
Status: ACTIVE PM PRIORITY OVERRIDE

## Product requirement

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 提示稳定跟随该角色 -> 不漂移`

This corrects any older wording that placed the target marker above the enemy.

## Priority decision

Do not preempt current Alpha P0/P1 blockers or their required independent QA.

However, the **next three available non-core/P2-capable worker slots** are reserved for HUDANCHOR player-follow acceleration before unrelated P2 polish/research.

Run concurrently when slots are available:

1. `HUDANCHOR_PLAYER_PROJECTION_REVERSE_V1`
   - prompt: `HUDANCHOR_PLAYER_PROJECTION_REVERSE_START_PROMPT.md`
   - purpose: close player/camera/X/Y/Z/drawing-buffer projection unknowns using existing reverse-engineering evidence and offline analysis.

2. `HUDANCHOR_PLAYER_FOLLOW_REFERENCE_IMPL_V1`
   - prompt: `HUDANCHOR_PLAYER_FOLLOW_REFERENCE_IMPL_START_PROMPT.md`
   - purpose: implement the stable player-follow resolver/router/renderer reference architecture and synthetic retarget/non-drift tests without changing Alpha.

3. `HUDANCHOR_ONECLICK_BROWSER_PROOF_AUTOMATION_V1`
   - prompt: `HUDANCHOR_ONECLICK_BROWSER_PROOF_AUTOMATION_START_PROMPT.md`
   - purpose: remove the old Worker Console + Top Console + pasted-JS workflow and compress any irreducible real Browser proof into one bounded one-click session.

All stages obey dedup/atomic claim and one-stage-one-fresh-chat rules.

## Why this is worth parallel capacity

This feature is not the Alpha release blocker, but its underlying projection/camera/player-state solution is a strategic accelerator for:
- target-aware HUD;
- future danger presentation;
- geometry/threat overlays;
- Safe Path;
- later low/zero-damage guidance.

Therefore this work has durable reuse beyond visual polish.

## Convergence rule

Do not broaden into full-game reverse engineering. Stop once the stable player-anchor projection and integration contract are sufficient. If one intrinsic Browser visual fact remains, automate everything else and request only one bounded Owner proof.

## Owner action now

No real Browser/WOF proof yet. Repository-side work first.