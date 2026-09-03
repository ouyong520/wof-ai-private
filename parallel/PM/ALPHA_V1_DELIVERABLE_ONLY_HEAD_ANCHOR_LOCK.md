# Alpha V1 Deliverable-Only Head Anchor Lock

## Owner directive

This thread and this mainline are Alpha V1 only. Collector, Training Farm / 10-train, diagnostic collectors, research packages, and unrelated infrastructure are not Alpha V1 deliverables and must not be counted as progress here.

## Only product deliverables that matter now

1. Enemy head tracking: each active enemy gets a stable head anchor, and the product can render its current target as `1P` / `2P` / `3P` above that enemy.
2. Player head tracking: P1/P2/P3 get stable head anchors, and the product can render `危险` above the attacked player when a warning is active.

## Current blocker definition

Both enemy and player head anchors are currently not trustworthy in real Owner use. Therefore business labels, warning semantics, package generation, CI green status, semantic-producer work, diagnostic capture, and other subprojects cannot be used to claim Alpha V1 product readiness.

The existing production projection profiles are explicitly unproved/disabled:
- `product/alpha/wof_alpha_enemy_head_projection.json`
- `product/alpha/wof_alpha_player_head_projection.json`

Until real head anchors are visibly correct, the mainline must focus only on the coordinate path needed to place both enemy and player head anchors correctly.

## Simplification rule

Reuse prior evidence that Y / Y-Z / Y+Z movement was directionally connected when useful. If the observed error is a sign/direction/mapping convention issue, fix that directly. Do not reopen broad research programs, do not require manual calibration, and do not create new diagnostic workstreams merely to postpone visible output.

Prefer the shortest demonstrable path from runtime state to screen-space head anchor. A temporary simple marker is acceptable for validating head tracking, but it must be the same coordinate path that will carry the final labels.

## Acceptance order

1. Enemy head marker visibly follows enemy head during movement and scrolling.
2. Player head marker visibly follows P1/P2/P3 head during movement and scrolling.
3. Loss hides the marker; recovery restores it without stale drift.
4. Only then attach `1P/2P/3P` to enemy anchors and `危险` to player anchors.
5. Only after those are visibly correct may an Owner package be called Alpha V1 deliverable-ready.

## Forbidden false progress

Do not count any of the following as Alpha V1 delivery:
- Collector / Unified Collector work
- Training Farm / 10-train work
- diagnostic-only or capture-only packages
- package/manifest generation while head anchors remain wrong
- CI/test PASS without visible head-anchor correctness
- overlay-enabled flags without actual correct on-screen placement

## Terminal status

Continue current Alpha V1 mainline until either:
- DELIVERABLE-READY: enemy + player head anchors visibly correct and final labels attached, or
- BLOCKED: one exact technical fact that cannot be resolved safely without Owner real-WOF evidence.
