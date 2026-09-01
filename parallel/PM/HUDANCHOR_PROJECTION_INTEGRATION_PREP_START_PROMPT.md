# HUDANCHOR Projection Integration Prep — Fresh Stage

stageId: `HUDANCHOR_PROJECTION_INTEGRATION_PREP_V1`
priority: `P1`

## Dedup / claim
Read `parallel/PM/STAGE_DEDUP_GUARD.md` and current default-branch state first. If equivalent work is complete or already claimed, stop with the standard dedup message. Otherwise claim `parallel/PM/STAGE_CLAIMS/HUDANCHOR_PROJECTION_INTEGRATION_PREP_V1.json` before work.

## Why now
The player-head follow reference implementation is already built. Reverse work has closed all useful offline facts and the one-click Browser proof automation is active. Fresh QA found a bounded fail-closed edge bug in the follow lane. The goal of this stage is to remove integration waiting time after the Browser proof returns.

## Product requirement
Authoritative UX:
`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随角色移动 -> 不漂移 -> 换锁立即切到新角色`

Fixed HUD is fallback only.

## Write scope
Write only under:
- `parallel/HUDANCHOR_INTEGRATION_PREP/**`
- mandatory claim file

Do not modify current follow implementation, proof automation, Alpha product, PYLAUNCH, Recorder, Prospective, or transport implementation.

## Required work
Prepare a bounded, executable integration handoff that consumes a future `IMPLEMENTATION_READY` Browser projection result without guessing constants:

1. Define exact machine-readable projection input contract: camera address/read form, native X formula/bias, chosen Y/Z model, above-character offset, viewport/native raster, version/epoch/freshness metadata.
2. Define adapter boundary from real Browser player/camera state into existing `PlayerAnchorResolver.projectNative(...)`.
3. Define exact invalid/stale/out-of-bounds behavior -> fixed HUD fallback, no last-known-coordinate reuse.
4. Define retarget P1->P2->P3 lifecycle wiring and immediate old-player clear.
5. Define resize/fullscreen/DPR/current WebGL viewport remap path.
6. Define integration tests that can run immediately after proof constants are frozen, including movement, camera scroll, depth, jump, retarget, respawn, viewport change, stale epoch, and out-of-bounds anchor.
7. Provide a one-command repository-side integration selftest skeleton using synthetic/frozen fixture injection only; do not fake Browser proof.
8. Provide exact patch plan / file ownership for the later real integration stage so no redesign decision remains.

## Hard boundaries
- No guessed real WOF projection constants.
- No broad RAM reverse engineering.
- No new danger semantics.
- No gameplay input or RAM writes.
- No Worker replacement/wrap or URL rewrite.
- Do not modify `product/alpha/**` in this prep stage.

## Stop condition
`HUDANCHOR PROJECTION INTEGRATION PREP READY — WAITING ONLY FOR PROVED BROWSER TRANSFORM AND FOLLOW FIX QA`

Owner action: NO.
