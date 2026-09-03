# Alpha V1 Head Anchor Mainline — 3 Worker Dispatch

## Authority

This is not a new Alpha version, recovery, or independent workstream family. It is execution guidance under the existing Alpha V1 mainline and `ALPHA_V1_DELIVERABLE_ONLY_HEAD_ANCHOR_LOCK.md`.

## Product blocker

Owner has confirmed both enemy and player top-of-head positions are wrong. Therefore no business label, package, CI, Collector, Training Farm, diagnostic bundle, or zero-click polish counts as product progress until the head anchors themselves are correct.

The only current acceptance target is:

1. enemy head anchor follows the actual enemy head through normal movement/scroll/depth;
2. player head anchor follows the actual P1/P2/P3 head through normal movement/depth/jump;
3. both use the same correct drawing-buffer/screen mapping and hide rather than drift when authority is stale;
4. only after 1-3 are true may enemy `1P/2P/3P` and player `危险` be considered product-ready.

## Reuse-first constraint

Do not reopen broad RAM scans, Collector, Training Farm, new camera research, video counting, or manual multi-stage calibration.

Reuse the retained bounded evidence in:

- `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md`
- `product/alpha/wof_alpha_enemy_target_labels.js`
- `product/alpha/wof_alpha_player_head_warning.js`
- current Alpha HUD/WebGL drawing-buffer mapping

The prior proof already narrowed vertical candidates to `Y-Z`, `Y+Z`, or `Y`, plus sign/bias/head-clearance and current-frame viewport mapping. Owner reports prior candidates visually moved with the actors but direction appeared reversed; treat that as evidence that the data path may already be connected and prioritize sign/origin/mapping correction before inventing a new model.

## Worker A — Enemy head anchor

Only diagnose and fix enemy top-of-head anchor geometry.

Focus on:
- `enemyX/enemyY/enemyZ` -> native head anchor;
- camera X sign/bias;
- `Y-Z` / `Y+Z` / `Y` sign/origin interpretation;
- per-type head clearance only after the common transform is correct;
- no target-label business changes except what is necessary to display a neutral anchor during focused validation.

Do not modify player anchor code, Owner menu, package selection, Collector/Training Farm, or umbrella claims.

Terminal state: exact integration-ready commit + focused evidence, or precise BLOCKED identifying the unresolved transform component.

## Worker B — Player head anchor

Only diagnose and fix player top-of-head anchor geometry.

Focus on:
- P1/P2/P3 world X/Y/Z -> native head anchor;
- camera X sign/bias;
- floor/depth/jump vertical sign;
- head clearance;
- reuse the direct P1 visual tracker as a comparator when useful, but do not let tracker-only success substitute for correct production head placement.

Do not modify enemy anchor code, Owner menu, package selection, Collector/Training Farm, or umbrella claims.

Terminal state: exact integration-ready commit + focused evidence, or precise BLOCKED identifying the unresolved transform component.

## Worker C — Shared screen mapping / integration

Only validate and correct the common native-to-WebGL-drawing-buffer mapping used by both enemy and player anchors.

Focus on:
- WebGL viewport origin/top conversion;
- native 384x224 -> drawing buffer mapping;
- resize/fullscreen recovery;
- CSS/DPR must not be hard-coded;
- stale/lost authority hides anchors rather than leaving old positions;
- focused integration regression that exercises both enemy and player anchor coordinates using the same mapping contract.

Do not change game logic, danger logic, target selection, Collector/Training Farm, or package publishing.

Terminal state: shared mapping integration-ready commit + focused evidence, or precise BLOCKED.

## Merge / product gate

Do not publish an Owner package merely because any one worker passes. The mainline may advance to business labels only when enemy head anchor + player head anchor + shared screen mapping are all coherent.

After all three integrate, the product-visible check is intentionally simple:

- enemy marker stays on enemy head while moving/scrolling/depth changes;
- player marker stays on player head while moving/depth/jump changes;
- no reversed vertical movement;
- no air/feet/body drift;
- loss hides; recovery restores.

Only then add/restore the core business text:

- enemy head: `1P` / `2P` / `3P` according to actual target;
- player head: `危险` when a qualified incoming attack applies.

Keep the existing Alpha V1 umbrella. No new recovery/version/workstream numbering. Minimal reporting; execute to integration-ready or exact BLOCKED.