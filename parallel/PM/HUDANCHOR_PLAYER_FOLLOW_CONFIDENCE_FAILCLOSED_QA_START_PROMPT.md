# HUDANCHOR Player-Follow Confidence Fail-Closed Fresh QA

stageId: `HUDANCHOR_PLAYER_FOLLOW_CONFIDENCE_FAILCLOSED_QA_V1`

Priority: **P1 product-experience release support**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`; re-read current HEAD. If equivalent PASS exists return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`; if claimed return `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.

Claim `parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_FOLLOW_CONFIDENCE_FAILCLOSED_QA_V1.json`.

Independently QA the completed confidence fail-closed fix. Do not modify HUD implementation. Allowed writes only under `parallel/HUDANCHOR_PLAYER_FOLLOW_QA_CONFIDENCE/**` plus own claim.

Attack NaN, +Infinity, -Infinity, undefined/null/string/object confidence, threshold boundaries, stale high-confidence value after invalid transition, retarget P1→P2 during invalid confidence, body coords valid while projection confidence invalid, invalid→valid recovery, valid→invalid immediate fixed-HUD fallback, and interaction with the already-closed bounds edge-clamp bug.

Require no stale player-follow cue, no edge clamp masquerading as attachment, and fixed HUD fail-closed when confidence is not finite/admissible. Re-run existing player-follow synthetic/bounds regressions.

Success: `PASS — HUDANCHOR CONFIDENCE FAIL-CLOSED FRESH QA — READY FOR LONG-STRESS V2`.

Failure: one precise P1 blocker. Owner action: **NO**.