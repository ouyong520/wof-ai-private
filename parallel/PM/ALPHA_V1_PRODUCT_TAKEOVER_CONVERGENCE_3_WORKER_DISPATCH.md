# Alpha V1 Product Takeover — Convergence 3-Worker Dispatch

Authority baseline: `747c5b09d7a3d510a2df4bb8f9cb480ca8101da4`

Repository: `ouyong520/wof-ai-private`

Scope: **Alpha Owner-visible product only**. Collector and Training Farm / 10训 are strictly out of scope: do not read, run, modify, test, schedule, or use their claims/results/runtime as Alpha evidence.

## 0. PM takeover verdict

Status: **RED — salvageable product, major convergence failure; not an unsolved-technology blocker.**

The current failure is architectural and execution-priority related:

- recent work has advanced permanent live-retest/bootstrap infrastructure faster than the Owner-visible top-of-character product;
- the maintained HUD/draw path has not first been isolated with a trivial fixed production draw in real WOF;
- P1 steady-state position authority still relies on screenshot/template tracking rather than deterministic exact-runtime renderer/object screen-space authority;
- enemy display is coupled to P1 head authority, so P1 authority failure can suppress both player and enemy overlays and make the whole product appear dead;
- repeated packages/recoveries/Owner file handoffs have created unacceptable test friction.

This takeover freezes process expansion and restores one product sequence:

`permanent Owner test channel -> prove maintained production draw -> deterministic actor screen-space anchors -> player follow -> enemy target labels -> danger UX -> zero-click polish`

## 1. Frozen product rules

Until these three workstreams converge:

- no Alpha V4/V5 or new recovery lineage;
- no new package/version churn for Owner;
- no new zero-click feature work;
- no danger-model expansion;
- no broad QA/research stages;
- no artificial completion based only on fixtures, CI, docs, claims, package manifests, tray state, or diagnostic overlays;
- no screenshot-template tracker as steady-state production position authority;
- vision/click may be used only as bounded seed/verification fallback;
- `readOnly=true`, `ramWrites=0`, `inputInjection=false` remain mandatory;
- exact World 921031 identity/runtime-generation safety remains mandatory.

Owner-visible UX rule after anchor authority exists:

- urgent information belongs on/near the user character, not far away;
- monster-head label `1P/2P/3P` expresses that monster's current target;
- lock/attack/danger information intended to trigger immediate player action is ultimately displayed near the affected player's head;
- `target7E` semantics remain `0 -> P1`, `4 -> P2`, `8 -> P3`.

## 2. Existing authority / dedup handling

Do not create a new umbrella claim. Continue under the currently ACTIVE Alpha V3 Owner-visible umbrella:

`alpha.v1.live-acceptance.render-authority-owner-visible-startup-recovery-v3`

W3 is **not a new logical claim**. It resumes/converges the already ACTIVE render-authority sprite-coordinate claim:

`alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2`

with its existing prompt:

`parallel/PM/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2_START_PROMPT.md`

Do not create W3 Recovery V3/V4. If claim ownership/handoff prevents lawful continuation, stop and report the exact claim conflict to PM rather than create another equivalent claim.

W1 and W2 must do normal dedup-v2 preflight before acquiring a narrowly scoped subworkstream claim. If an equivalent ACTIVE claim exists, do not duplicate it.

## 3. Parallel W1 — Owner permanent live-test bootstrap / delivery channel

Priority: P0

### Objective

Make Owner testing a one-time installation followed by one permanent launcher. The Owner must never again download a new Alpha ZIP/CMD for each fix.

The Owner has explicitly cleared `%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN`; the bootstrap must therefore work from that missing/empty managed directory.

The Owner's existing `%USERPROFILE%\.ssh` must be preserved. Reuse `wof_alpha_github_ed25519` when valid; do not delete or overwrite unrelated keys such as VPS keys.

### Required behavior

- One bootstrap entry establishes the managed Alpha environment from zero state.
- Do not require an already existing managed `.git` repository.
- Do not depend on Git HTTPS/443.
- Use GitHub SSH port 22 for the Alpha update channel.
- Reuse the existing dedicated Alpha SSH key if present; if absent, generate only the dedicated Alpha key and guide the one unavoidable GitHub authorization once.
- Install exactly one permanent Desktop entry: `WOF_ALPHA_TEST.cmd`.
- After installation, Owner workflow is only: run once -> test -> send screenshot/feedback -> leave test controller running -> receive automatic update/restart.
- Separate Owner live releases from arbitrary development/documentation commits. Introduce/use a controlled Alpha live ref/branch (preferred `alpha-live`) or an equivalent explicit release pointer; do not restart Owner runtime for every unrelated `main` commit.
- On a live update, stop/restart Alpha control/runtime only; preserve the existing browser/WOF page whenever technically safe.
- Updater must self-update safely.
- Keep results under `Documents\WOF_RESULTS`; provide one obvious latest-feedback artifact/path rather than requiring Owner to hunt through internal JSON files.
- Fail with a single precise actionable message if SSH authorization, Git, Python, or browser prerequisites are genuinely missing.

### File ownership

W1 owns only Owner delivery/update/bootstrap files, principally:

- `WOF_ALPHA_SETUP_ONCE.cmd`
- `WOF_ALPHA_TEST.cmd`
- `parallel/PYLAUNCH/install_live_retest_once.ps1`
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`
- one narrowly named new bootstrap/update helper only if required
- focused tests/docs/subresult for this workstream

W1 must not modify HUD drawing, head tracker/anchor algorithms, enemy target logic, danger logic, Collector, or Training Farm.

### Acceptance

Implementation-owned acceptance must prove from an absent managed directory that bootstrap can establish the local managed repo and permanent launcher without HTTPS/443, and that a simulated/new live release is detected/applied while using the same permanent launcher.

Windows networking/auth that cannot be emulated may remain one narrowly defined Owner gate, but W1 must not send Owner a chain of manual download instructions.

Deliver one integration-ready commit + durable W1 subresult, or precise BLOCKED.

## 4. Parallel W2 — Maintained production HUD fixed-draw smoke

Priority: P0

### Objective

Prove or precisely break the common rendering chain before touching P1/enemy coordinate algorithms.

The first real-WOF visual checkpoint is intentionally trivial:

**the maintained production HUD must be able to draw a fixed `TEST` label at a known game-space position without any P1 tracker, semantic identity, enemy data, screenshot tracking, or world projection.**

### Required behavior

- Use the **same maintained production WebGL HUD/draw hook** that final Alpha uses. A DOM/Tk/diagnostic canvas/acquisition marker does not count.
- Add a narrowly controlled live-smoke mode that can render fixed `TEST` at canonical native game coordinates (preferred native `384x224`, e.g. center `192,112`) and map once to the real drawing buffer.
- This smoke mode must be independent of P1/enemy authority and therefore survive missing semantic/visual trackers.
- Expose machine-readable status sufficient to distinguish at least: HUD injection missing, game canvas/context missing, draw hook not firing, drawing-buffer invalid, fixed label actually drawn.
- `drawCount`/hook state must be tied to the maintained production renderer rather than a diagnostic surrogate.
- Smoke mode must be opt-in/test-channel-only and must not become permanent normal-product clutter.
- No changes to actor coordinate formulas, semantic identity, screenshot tracking, or danger policy.

### File ownership

W2 owns only the maintained HUD smoke/draw proof and its narrow production adapter integration, principally:

- `product/alpha/wof_alpha_hud.js`
- `parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py` only as needed to expose/invoke the fixed production smoke
- focused tests/fixtures/subresult

Avoid W1 files and W3 render/object discovery files.

### Acceptance

Implementation-owned tests must prove the smoke cannot be falsely green from DOM/diagnostic draws and that the normal mode is unchanged when smoke is disabled.

The first Owner gate after W1+W2 integration is exactly one question: **does fixed `TEST` visibly remain in the real WOF game render?**

If yes, common production draw chain is PASS and PM advances to W3 live anchor validation. If no, W2 must surface one precise upstream draw-layer blocker; do not ask Owner to diagnose DevTools.

Deliver one integration-ready commit + durable W2 subresult, or precise BLOCKED.

## 5. Parallel W3 — deterministic exact-runtime screen-space actor/head authority

Priority: P0/P1

### Authority

Continue the existing ACTIVE logical workstream:

`alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2`

Do not create another recovery or equivalent claim.

### Objective

Replace screenshot/template matching as the **steady-state production position authority** with exact-runtime renderer/object authority.

Canonical target architecture:

`actor runtime identity/generation -> exact CPS1 renderer/object entry or proven renderer-side equivalent -> canonical native 384x224 screen-space actor bounds -> stable above-character anchor -> one drawing-buffer mapping -> production HUD`

World/camera data may assist association/verification, but do not return to an unproven Y / Y-Z / Y+Z guessing/calibration loop.

### Required implementation order

1. Locate/prove exact World 921031's live CPS1 object/sprite/render authority used by the displayed frame, read-only.
2. Obtain frame/runtime-generation-qualified final screen-space object coordinates or the nearest proven renderer-side equivalent.
3. Associate renderer entries/clusters to P1/P2/P3 and enemy lifecycle slots. Reject ambiguity rather than label nearest arbitrary sprites.
4. Handle multi-tile actors, animation, flip, clipping, weapon/effect separation enough to derive a stable above-character anchor.
5. Normalize actor anchor output to one canonical native `384x224` coordinate contract.
6. Player first: prove P1 anchor continuity for horizontal move, depth move, jump/attack animation, camera scroll/room transition; temporarily suppress unsafe frames and recover automatically.
7. Extend the same authority to enemies. Reuse already-established target semantics to support monster-head `1P/2P/3P` labels.
8. Vision/click may only seed or verify association when unavoidable. A static screenshot template must not determine every production frame.
9. Runtime/lifecycle/generation/renderer epoch changes revoke stale authority.

### File ownership

W3 owns render/object discovery/extraction/association and a new deterministic anchor module/tests. Prefer new narrowly named modules over colliding with W2 HUD files.

It may modify `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js` only when exact renderer/object data must be surfaced from the accepted runtime, and associated focused launcher modules/tests required to consume that authority.

Do not modify W1 bootstrap/updater files. Avoid `wof_alpha_hud.js` unless PM integration later proves an unavoidable interface change; W3 should deliver canonical anchor data, not redesign rendering.

### Acceptance

Before requesting Owner action, establish a bounded implementation-owned feasibility proof:

- exact renderer/object coordinate source identified and tied to exact World/runtime generation;
- at least one known actor renderer coordinate changes consistently with known/displayed movement in available fixture/evidence;
- ambiguous association suppresses output;
- stale generation/epoch suppresses output;
- canonical anchor contract is deterministic.

If exact render authority genuinely cannot be established without one live capture, produce one automatic bounded capture path requiring only normal play for a short interval. Do not ask Owner for coordinate clicks/calibration or repeated packages.

Deliver integration-ready deterministic anchor authority + focused tests + durable continuation/subresult, or precise BLOCKED.

## 6. PM integration order / Owner gates

The three workers may run in parallel because file ownership and immediate objectives are independent.

PM integration order is strict:

1. integrate W1 permanent testing channel;
2. integrate W2 fixed maintained-production draw smoke;
3. publish one controlled Owner live candidate;
4. Owner installs/runs once and reports only screenshot/simple observation;
5. after fixed draw PASS, integrate W3 P1 deterministic anchor and publish automatically through the same permanent live channel;
6. Owner continues using the same `WOF_ALPHA_TEST.cmd`; no new download;
7. after P1 follow PASS, enable enemy anchors + monster-head `1P/2P/3P` using the same screen-space authority;
8. only then build player-near danger/attack UX;
9. only after geometry/product loop is stable, restore zero-click semantic acquisition as normal-path polish.

No fourth worker/recovery is opened merely because an intermediate check fails. Failure returns to the worker owning the failed layer.

## 7. Product completion truth

These do **not** count as product completion by themselves:

- CI/test PASS;
- fixture PASS;
- package/manifest generated;
- tray/status visible;
- semantic producer selected;
- white acquisition marker;
- diagnostic overlay;
- code says `productionOverlayEnabled=true`;
- fixed smoke PASS alone.

Milestone truth is Owner-visible behavior:

- M0: same permanent launcher can receive subsequent fixes automatically;
- M1: maintained production HUD fixed `TEST` visibly draws in real WOF;
- M2: `1P` stays visibly above the player's character while normal gameplay moves/scrolls/animates;
- M3: each supported enemy stays correctly anchored and displays current target `1P/2P/3P`;
- M4: relevant lock/attack/danger warning is shown near the affected player, keeping user focus on their character;
- M5: normal acquisition becomes zero-click where semantic authority is safe, with fail-closed bounded fallback only when needed.

## 8. Owner-intervention policy

Owner time is the scarce resource.

Do not request Owner testing for implementation questions that code/fixtures can answer. When Owner evidence is unavoidable, bundle changes so one test answers one clear product question. Owner should never be asked which ZIP/CMD/version to download, how to inspect DevTools, or how to manually locate internal evidence files.

Expected Owner interaction after bootstrap: **keep running the same permanent test entry, play normally, send screenshot or one-line observation; fixes arrive automatically.**

## 9. Exit condition for this dispatch

The takeover dispatch remains active until W1/W2/W3 have each returned integration-ready/PASS or a precise external blocker and PM has reached at least the first controlled Owner fixed-draw gate.

Do not declare Alpha COMPLETE from this dispatch. Its job is to restore a reliable development/test loop and converge the fundamental render/anchor authority so that subsequent product milestones can be judged by real Owner-visible behavior.
