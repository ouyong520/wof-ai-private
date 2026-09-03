# Alpha V3 — W2/W3 Integration Closeout Correction

Status: **AUTHORITATIVE ADDENDUM FOR THE ACTIVE V3 UMBRELLA WORKER**

This does not create a new recovery, dedup key, QA generation, or umbrella claim. The existing V3 canonical/stage claims remain authoritative and ACTIVE until this integration is complete.

## Accepted parallel outputs

W2 is SUBCOMPLETE and integration-ready:
- module: `parallel/PYLAUNCH/wof_launcher/zero_click_identity_acquisition.py`
- SUBRESULT: `parallel/PM/ALPHA_V1_RENDER_AUTHORITY_V3_W2_ZERO_CLICK_IDENTITY_ACQUISITION_SUBRESULT.md`

W3 is SUBCOMPLETE/claim-complete and its acceptance/package-readiness gate is ready:
- fixture: `parallel/PYLAUNCH/tests/fixtures/alpha_v3_w3_zero_click_acceptance.json`
- gate: `parallel/PYLAUNCH/tests/test_zero_click_acceptance_fixture_w3.py`
- SUBRESULT: `parallel/PM/RESULTS/ALPHA_V1_RENDER_AUTHORITY_V3_W3_ZERO_CLICK_ACCEPTANCE_FIXTURE_SUBRESULT.md`

Do not redo either subworkstream.

## Exact remaining integration defect

The current package manifest includes `zero_click_identity_acquisition.py`, but current `head_visual_tracker.py` still performs its own inline HUD-palette / scene-palette heuristic and does not consume W2's fail-closed identity/evidence adjudicator before automatic binding.

W2 explicitly found that a generic HUD palette crop is not semantic P1 character/portrait identity evidence. Therefore the package must not claim `auto P1 identity/HUD -> scene P1 -> safe head seed` merely because the inline palette matcher returned one unique visual peak.

A file being present in the package is not integration.

## Required umbrella integration

Before fallback click can be armed:

1. Reuse exact World 921031 and current P1 lifecycle (`active`, character `type`, generation).
2. Reuse the live canvas screenshot and screenshot digest.
3. Feed real proven HUD/portrait/tile/render identity evidence into W2. Do not manufacture HUD identity by copying runtime P1 type and do not treat a generic colorful HUD crop as a certified portrait.
4. Feed the scene-P1/head candidate produced by the current bounded visual search into W2 with actor=P1, character type, generation, confidence/margin, bounds and evidence/coarse-prior status.
5. Call `acquire_zero_click_p1_head(...)` (or an equivalent direct consumption of W2's exact contract).
6. Only W2 `ok=True` / `SAFE_UNIQUE` may automatically seed `HEAD_TRACKING` with `ownerClickCount=0`.
7. Any ambiguity/missing semantic identity must remain unbound and only then may the existing one-click P1-head fallback be armed.
8. Runtime/lifecycle/layout invalidation must revoke both the tracker seed and W2 identity authority and reacquire from zero.

If no real semantic HUD/portrait/tile/render identity signal is available in the current runtime, do not fake one. In that case keep fail-closed fallback and state the precise limitation in RESULT. However, first exhaust reuse of already-proven Alpha HUD/player identity/runtime evidence in the repository.

## Closeout gate

After integration, do one coherent focused V3 regression only:

- W2 focused identity acquisition tests;
- V3 zero-click-first tracker regression;
- W3 deterministic acceptance fixture;
- W3 candidate/package-readiness mode against the newly generated candidate;
- package manifest/blob pins prove the final corrected integration runtime is actually selected.

Do not rerun unrelated historical PASS suites.

Then regenerate the immutable successor from the final integrated source commit, publish durable V3 RESULT, and close only the existing V3 canonical/stage claims COMPLETE.

The old one-click-first V3 package and the intermediate zero-click package that merely contains W2 without consuming it must not be sent to Owner.

## Owner test boundary

Only after this closeout may Owner receive one bounded live test. Intended normal path remains:

`菜单6 -> 正常进入/复用 WOF -> 托盘状态可见 -> exact World -> 自动 P1 身份/场景 P1/头部 seed -> HEAD_TRACKING with ownerClickCount=0 -> 正常玩 -> 自动多样本 -> 丢失隐藏/恢复出现 -> 自动完成`

One P1-head click is fallback only after automatic semantic acquisition fails closed.
