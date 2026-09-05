# Alpha V1 Product Takeover — Unified Audit / Resume Decision

Date: 2026-09-05

Scope: Alpha Owner-visible product only. Collector / Unified Collector / Training Farm / 10训 are out of scope and were not used as Alpha evidence.

Parent authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_CONVERGENCE_3_WORKER_DISPATCH.md`

## PM verdict

Do **not** continue by pasting old recovery text into already-finished worker chats. Resume from clean new worker threads only after authority state is clean.

Current product sequence remains:

`permanent Owner live-test channel -> maintained production fixed TEST -> one Owner real-WOF draw gate -> W3 bounded renderer qualification -> deterministic P1 anchor -> enemy target labels -> danger UX -> zero-click polish`

No Alpha V4/V5 and no new product-recovery tree is authorized.

## W1 audit — Owner permanent live-test bootstrap

Original canonical:
`alpha.v1.product-takeover.owner-permanent-live-test-bootstrap`

State: `BLOCKED`.

Blocker:
`DEDUP_V2_STAGE_CLAIM_CREATE_RACE`.

The original W1 worker correctly stopped before implementation/tests and safely closed its exact-token canonical claim after stage-claim creation raced with unrelated main advancement.

PM already authorized a narrow ownership-continuity recovery:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP_DEDUP_RECOVERY_START_PROMPT.md`

Recovery dedup key:
`alpha.v1.product-takeover.owner-permanent-live-test-bootstrap.claim-recovery-v1`

At this audit point the recovery canonical has **not** been claimed, so W1 is cleanly available for one fresh worker thread.

Decision: **START ONE FRESH W1 THREAD using only the W1 dedup-recovery prompt.** Do not reuse the old W1 chat and do not modify/revive the historical blocked canonical.

## W2 audit — Maintained production HUD fixed TEST

Original W2 canonical/stage were acquired by the PM coordination session during dispatch but no production implementation or tests were started.

PM has therefore closed its own exact-token original W2 canonical/stage pair as `BLOCKED` with:
`PM_COORDINATOR_CLAIM_ONLY_NO_IMPLEMENTATION`.

No W2 SUBRESULT exists yet and no fixed-production-TEST implementation has been accepted.

PM now authorizes a clean worker execution recovery:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W2_FIXED_DRAW_SMOKE_EXECUTION_RECOVERY_START_PROMPT.md`

Recovery dedup key:
`alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke.execution-recovery-v1`

Decision: **START ONE FRESH W2 THREAD using only this W2 execution-recovery prompt.** Do not reuse the PM-owned historical W2 claim or old worker context.

## W3 audit — deterministic renderer/object head authority

Durable result:
`parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_W3_RENDER_OBJECT_AUTHORITY_CONTINUATION_SUBRESULT.md`

State: `SUBCOMPLETE`; existing logical claim remains `ACTIVE` intentionally.

Accepted implementation-owned progress:

- bounded exact-runtime object-table candidate timeline capture;
- runtime + renderer epoch binding;
- automatic verification-only screenshot capture during normal play;
- fail-closed canonical `384x224` render-object anchor consumer;
- ambiguity / stale runtime / stale renderer suppression;
- focused implementation tests passed.

Remaining dependency is deliberately **live evidence**, not another research worker:

- identify/prove the renderer/object source actually consumed by displayed CPS1 frames;
- show at least one known actor renderer coordinate moving consistently with displayed movement.

Decision: **DO NOT OPEN A NEW W3 THREAD NOW.** W3 waits until W1+W2 reach the first controlled Owner gate. Then PM will resume W3 live qualification through the permanent Owner channel, with normal play only and no click/calibration/DevTools ritual.

## Immediate worker allocation

Use exactly **two** fresh worker threads now:

1. W1 permanent live-test bootstrap / controlled auto-update.
2. W2 maintained production fixed `TEST` draw smoke.

The third worker slot remains unused until one of these returns, because W3's next missing evidence is Owner live evidence and cannot be truthfully completed in parallel from repository-only work.

## Owner interaction policy

Do not ask the Owner to test yet.

First integrate W1 + W2. Only after both are integration-ready should PM publish one controlled candidate and ask one real-WOF question:

`固定 TEST 是否持续显示在真实游戏画面？`

After that first gate passes, W3 bounded live capture is delivered automatically through the same permanent launcher.

## Start condition

This audit supersedes ad-hoc chat continuation instructions. New workers must read latest main plus this audit decision plus their exact recovery/start prompt and perform dedup-v2 normally.
