# HUDANCHOR Player-Head Priority Decision

Date: 2026-09-01
Status: AUTHORITATIVE PM PRIORITY DECISION
Priority: P1 PRODUCT EXPERIENCE MAINLINE

## Product rationale

WOF gameplay visual attention is centered on the controlled player character, not on a fixed corner of the screen. Therefore the preferred warning presentation is:

`怪物锁定谁 -> 在被锁定角色头顶显示提示 -> 跟随角色移动 -> 不漂移 -> 换锁立即切换`

Fixed HUD remains a fail-closed fallback, not the preferred final presentation.

## Priority rule

- Safety / identity / transport correctness P0 remains higher.
- HUDANCHOR player-head warning is promoted from ordinary P2/Beta polish to P1 product-experience mainline.
- Any non-conflicting free concurrency slot should prefer this work over lower-value research or packaging polish until the player-head path reaches implementation-ready + fresh QA.
- Do not broaden into unrelated sprite/game internals.

## Parallel execution plan

1. Bounds/fail-closed fix for out-of-bounds anchor behavior.
2. One-click Browser projection proof automation / bounded live-proof preparation.
3. Projection integration preparation so a successful proof can be consumed immediately without architectural redesign.

## Stop condition

Player-head path is considered repository-ready when:
- follow reference implementation passes fresh independent QA;
- Browser projection proof produces authoritative implementation-ready transform, or only one bounded Owner live run remains;
- integration wiring is frozen and ready to consume that transform;
- fixed-HUD fallback remains fail-closed.

## Convergence rule

加速器必须让现有产品路线变短，不能只是让项目变大。

No broad geometry research, no unrelated renderer reverse engineering, no new danger semantics.
