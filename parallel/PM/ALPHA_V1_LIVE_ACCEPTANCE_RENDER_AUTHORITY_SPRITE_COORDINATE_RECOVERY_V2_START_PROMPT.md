# Alpha V1 Live Acceptance — Render Authority Sprite Coordinate Recovery V2

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

This is a PM-authorized implementation recovery and architecture pivot. It supersedes the stalled Projection Transform + Owner UX Recovery V1 execution path; it is not QA and not a restart of already completed live-acceptance recoveries.

## 0. Explicit supersession / dedup authority

Superseded historical canonical claim (leave intact; do not overwrite/delete/close/reuse):

- dedupKey: `alpha.v1.live-acceptance.projection-transform-owner-ux-recovery-v1`
- canonical path: `parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.projection-transform-owner-ux-recovery-v1.json`
- historical claimToken: `07e671be-2f1d-4b36-a5db-9a1877249f2e`
- historical state observed by PM: `ACTIVE`
- historical stage: `ALPHA_V1_LIVE_ACCEPTANCE_PROJECTION_TRANSFORM_OWNER_UX_RECOVERY_V1`

PM rationale for supersession:

- V1 acquired claims but produced no implementation commit or durable RESULT before this recovery authorization;
- latest Owner real-WOF evidence showed the current one-click `Y-Z / Y+Z / Y` projection family and manual visual-confirmation UX is the wrong abstraction for a production overlay;
- current source explicitly derives candidate screen Y from `worldY-z`, `worldY+z` or `worldY` plus click bias and fixes camera sign/scale to 1; continuing to tune this manually risks more Owner-only calibration loops rather than converging on render truth;
- CPS1 hardware/emulator rendering already consumes an authoritative sprite/object list containing the coordinates that actually reach the renderer, so PM is redirecting the implementation toward render authority rather than another guessed world-to-screen formula generation.

Before task work, re-read current `main`, the superseded claim/result state, `STAGE_DEDUP_GUARD.md`, `TESTING_CADENCE_POLICY.md`, completed Camera READY result, and recent equivalent commits/results/claims. Then create-only acquire and verify this V2 canonical claim; after verification create and verify its stage claim. If this V2 key is already occupied, follow dedup v2 exactly.

## 1. Frozen successful contracts

Do not reopen or regress:

- exact World 921031 runtime identity / SHA authority;
- read-only Browser/Page/Worker/WASM access;
- lifecycle-aware active/inactive player identity;
- Camera `READY_LATCHED` stability and READY->click TOCTOU fix;
- room re-entry Worker rediscovery / runtime-generation revocation;
- low-overhead cached runtime health;
- one Tk owner thread / clean shutdown;
- enemy target raw semantics `0 -> 1P`, `4 -> 2P`, `8 -> 3P`;
- current production danger rules and fail-closed semantics;
- `readOnly=true`, `ramWrites=0`, `inputInjection=false`;
- automatic menu-6 evidence packaging.

Do not ask Owner to repeat the old Y/Y-Z/Y+Z flow. Do not tell Owner to test superseded packages while implementation is in progress.

## 2. Architecture objective — consume render truth, do not re-derive it

Primary objective:

**Obtain frame-synchronous screen-space actor coordinates from the exact CPS1 render authority already used by the running WOF emulator, then place production overlays from that authority.**

Do not begin by inventing another worldY/Z formula, another sign/scale grid, or another manual head-click calibration.

Useful upstream reference authority for understanding CPS1 only (not permission to hard-code assumptions without exact-runtime verification):

- MAME `src/mame/capcom/cps1.h`: `CPS1_OBJ_BASE`, `m_obj`, `m_buffered_obj`;
- MAME `src/mame/capcom/cps1_v.cpp`: `cps1_get_video_base`, `find_last_sprite`, `cps1_render_sprites`.

The worker must verify the exact World 921031 Browser/WASM runtime's corresponding data path. Public emulator sources are architectural references, not live authority.

Investigate in this order:

1. **Exact emulator render/object authority** — locate the runtime memory/register/renderer structure that provides the final CPS1 sprite/object entries used for the displayed frame. Prefer this if accessible read-only.
2. **CPS-A OBJ base + object/gfx RAM** — if the exact runtime exposes the emulated 68000/CPS1 memory map, derive object-list location from the live CPS-A object-base register rather than assuming one constant address; decode only after proving entry semantics against live renderer behavior.
3. **Renderer-side equivalent** — if the emulator transforms CPS1 object RAM into an internal sprite list before composition, consume that exact read-only list instead of re-deriving coordinates.
4. **Vision-assisted fallback** — only if render authority is genuinely unavailable, use canvas vision/tracking as a bounded secondary authority. It may confirm or bridge identity, but a single static head template must never be sole production authority.

## 3. Actor association and head/label anchor

Final sprite coordinates alone are not enough; associate them strictly with P1/P2/P3/enemy lifecycles.

Required:

- bind render entries/clusters to current RAM actor slots using frame/time continuity, actor world state, visible-state/lifecycle generation and any exact renderer/object identity available;
- reject ambiguous association; never label the nearest arbitrary sprite;
- support multi-tile/multi-object characters and animation changes;
- account for flip, multi-size composition and clipping as required by the exact renderer;
- derive a stable **above-character label anchor** from the rendered actor bounds/opaque body geometry or another proven render-level anchor;
- the label anchor does not need to sit on an anatomical pixel if that would require fragile per-animation guessing; it must remain visibly above the correct character and stable enough for production `1P/2P/3P` / `[危险]` UX;
- weapons/effects/independent projectiles must not silently expand the actor anchor into incorrect space;
- if grouping/head/anchor authority is ambiguous for a frame, suppress that actor's overlay for that frame.

ROM/sprite graphics may be read **locally and read-only** if needed to disambiguate tile opacity/body geometry. Do not commit ROM bytes or ROM-derived copyrighted sprite sheets/head PNGs to the repository. Any local cache must be keyed to the already-authorized ROM identity and remain local/evidence-safe.

## 4. Product behavior — no calibration-test UI in normal menu 6

Normal Owner success path must converge toward:

`menu 6 -> enter WOF -> normal play -> automatic render authority -> production overlay`

Hard requirements:

- no visible `Y`, `Y-Z`, `Y+Z`, candidate-model or coordinate-math labels in normal menu 6;
- no requirement to click P1 two or three times;
- target zero-click normal operation;
- if a one-time visual seed is absolutely unavoidable in a fallback path, maximum one P1 click per explicitly new/revoked authority, with one clear instruction;
- no checklist requiring Owner to deliberately do horizontal/depth/jump/resize/fullscreen actions just to unlock production;
- jump, fast scroll, room transition, respawn, resize/fullscreen or any frame where association/render authority is temporarily unsafe => suppress overlay, then automatically restore after authority restabilizes;
- prefer temporary absence over a wrong-position label;
- normal production view only shows enemy `1P/2P/3P` and player `[危险]` when an existing supported danger rule actually fires;
- `[危险]` absent without an exercised supported rule remains NOT EXERCISED, not Detection FAIL.

## 5. Bounded feasibility gate — fail fast, not another long dead end

Before broad integration, establish one deterministic implementation-owned feasibility proof from available exact-runtime/repository evidence:

A. identify the exact runtime source of render/object coordinates;
B. prove that at least one known actor's render coordinate changes consistently with its displayed movement across a synthetic/deterministic fixture or existing captured exact-runtime evidence;
C. prove stale/runtime-generation replacement is rejected;
D. prove ambiguous object association suppresses output.

If A cannot be established from repository/runtime introspection without another Owner run, do **not** fall back to guessed constants. Build one minimal automatic render-authority capture package that requires only normal gameplay, automatically records the relevant object/register/render tables for a bounded interval, packages the live evidence, and tells Owner only `正常玩 20-30 秒`; publish that immutable successor and state the exact one measurement still required.

Do not stop at a source-code research note or speculative address list.

## 6. Implementation / integration scope

Complete the coherent module before stopping:

1. exact-runtime render-authority discovery;
2. read-only object/sprite extraction with frame/runtime-generation identity;
3. actor-to-render association and ambiguity rejection;
4. stable above-character anchor or bounded local-graphics-assisted anchor;
5. production overlay integration for enemy target labels and existing player danger warning;
6. transition/jump/scroll/resize/ambiguous suppression + automatic recovery;
7. novice menu-6 UX with zero calibration math exposed;
8. automatic evidence timeline and unmistakable authoritative `WOF_LIVE_ACCEPTANCE_<session>.zip` handoff;
9. deterministic implementation-owned tests for object decode, actor association, multi-tile grouping, stale generation, ambiguity suppression, transition suppression/recovery and target/danger safety invariants;
10. necessary implementation regressions only — no new broad QA chain;
11. new immutable successor source/package; never reuse `2026.09.02.52c942085c99`;
12. Windows portable / Chinese+spaces path / last-known-good behavior as applicable;
13. durable RESULT with exact sourceCommit, packageVersion, manifestPublicationCommit, workflows and remaining real-WOF acceptance scope;
14. close V2 canonical and stage claims COMPLETE with the exact V2 claimToken.

## 7. Explicit non-goals

- no gameplay writes or input injection;
- no relaxed World identity;
- no guessed CPS1 address/entry format accepted as production authority;
- no ROM upload/commit;
- no long chain of QA/recovery/second-opinion stages;
- no reopening historical repository Fresh QA;
- no requiring Owner to debug DevTools/Python/shell;
- no trying to perfect arbitrary debug labels instead of the production overlay.

## 8. Exit

Only stop on one of:

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE RENDER AUTHORITY SPRITE COORDINATE RECOVERY V2 — SUCCESSOR PACKAGE READY — READY FOR ONE FOCUSED OWNER LIVE RETEST`

or, only if one unavoidable live measurement remains after publishing a complete automatic capture successor:

`COMPLETE — ... — BOUNDED AUTOMATIC RENDER-AUTHORITY MEASUREMENT PACKAGE READY — OWNER ACTION: NORMAL PLAY ONLY`

or

`BLOCKED — ALPHA V1 LIVE ACCEPTANCE RENDER AUTHORITY SPRITE COORDINATE RECOVERY V2 — <precise external/authority blocker>`

or canonical duplicate stop per dedup v2.

Do not stop at claim acquisition, research, address hypothesis, single patch, test PASS, workflow in progress, package publication or RESULT with claims still ACTIVE.
