# WOF HUDANCHOR — Player-Follow Confidence Fail-Closed Fix Start Prompt

stageId: `HUDANCHOR_PLAYER_FOLLOW_CONFIDENCE_FAILCLOSED_FIX_V1`

Priority: **P1 — product-experience mainline**

## Dedup / claim

Before doing work, follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If this stage is already claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise claim this stage under:
`parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_FOLLOW_CONFIDENCE_FAILCLOSED_FIX_V1.json`

## Role

You own the narrow implementation fix for the current HUDANCHOR player-head warning confidence-authority blocker.

Authoritative product behavior remains:

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随角色 -> 不漂移 -> 换锁立即切换`

Fixed HUD is fail-closed fallback only when anchored spatial authority is invalid/stale/untrusted.

## Read first

Re-read current HEAD, especially:

- `parallel/HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference.js`
- `parallel/HUDANCHOR_PLAYER_FOLLOW/test/**`
- `parallel/HUDANCHOR_PLAYER_FOLLOW_LONG_STRESS/RESULT.md`
- `parallel/HUDANCHOR_PLAYER_FOLLOW_LONG_STRESS/matrix.json`
- `parallel/HUDANCHOR_PLAYER_FOLLOW_LONG_STRESS/long_stress_matrix.js`
- `parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md`
- `parallel/PM/DELIVERY_REASSESSMENT_GATE.md` if present

## Current blocker

Fresh long-stress analysis found:

**P1 — invalid/non-finite projection confidence can authorize anchored rendering instead of fixed-HUD fail-closed fallback.**

Current behavior normalizes a non-finite confidence such as `NaN` through a fallback value (observed as `1`), which can leave `anchor.ok === true` even though projection confidence itself is invalid.

This is unacceptable because player-head placement asserts spatial authority over a specific live player.

## Goal

Make every confidence value that participates in player-head anchor authority fail closed when it is non-finite/invalid.

At minimum cover the current blocker and the same narrow confidence-authority family already identified by the long-stress result:

- projection confidence;
- projected/player confidence where used for anchor authority;
- drawing-buffer/mapping confidence where used for anchor authority.

Do **not** expand into unrelated rendering/projection research or guess Browser constants.

## Hard write boundary

Write only under:

- `parallel/HUDANCHOR_PLAYER_FOLLOW/**`
- mandatory claim file under `parallel/PM/STAGE_CLAIMS/**`

Do not modify:

- Browser proof automation;
- `parallel/HUDANCHOR/**` reverse-engineering research;
- `product/alpha/**`;
- PYLAUNCH / Recorder / Prospective / Transport / Live Proof.

## Required semantics

1. `NaN`, `Infinity`, `-Infinity`, missing/invalid confidence must never be promoted to trusted anchored authority by a permissive fallback.
2. Invalid confidence must yield a deterministic fail-closed anchor result and route to fixed HUD.
3. Invalid confidence after a valid frame must clear follow/smoothing authority; no reuse of old player-head coordinates.
4. Retarget during invalid confidence must remove the old player's cue immediately; do not leave stale ownership.
5. Valid finite confidence behavior must remain unchanged.
6. Existing finite out-of-bounds fail-closed behavior must remain intact.

## Regression

Add targeted deterministic regression covering at least:

- projection confidence = NaN / +Infinity / -Infinity;
- equivalent non-finite confidence surfaces participating in authority;
- invalid confidence after valid anchored frame clears state;
- retarget P1 -> P2 during invalid confidence does not retain P1 cue;
- valid finite confidence near threshold behaves according to existing contract;
- existing bounds regression remains PASS;
- existing full 15-case synthetic player-follow regression remains PASS;
- the long-stress blocker-directed case now PASS against the real SUT.

Do not weaken the long-stress invariant or change its expected fail-closed semantics.

## Safety

Preserve:

- read-only presentation;
- no RAM writes;
- no gameplay input injection;
- no Worker replacement/wrap;
- no guessed Browser projection constants.

## Delivery reassessment

Before finishing, state explicitly:

- whether this actually closes the P1 long-stress blocker;
- what downstream stage is newly unblocked;
- whether long-stress V2 can now restart;
- whether any real Browser/WOF fact is still required.

## Stop condition

Success:

`HUDANCHOR PLAYER-FOLLOW CONFIDENCE FAIL-CLOSED FIX READY — READY FOR FRESH QA + LONG-STRESS V2`

Or one precise blocker requiring a different ownership lane.

Owner action: **NO**.
