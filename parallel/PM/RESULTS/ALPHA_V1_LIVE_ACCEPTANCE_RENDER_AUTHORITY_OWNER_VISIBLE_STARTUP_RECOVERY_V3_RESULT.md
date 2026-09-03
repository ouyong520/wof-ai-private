# Alpha V1 Live Acceptance Render Authority Owner-Visible Startup Recovery V3 — Result

Status: **COMPLETE**

## Authority

- Existing V3 only; no new recovery/QA generation.
- Canonical dedup key: `alpha.v1.live-acceptance.render-authority-owner-visible-startup-recovery-v3`.
- Defect correction authority: `parallel/PM/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_OWNER_VISIBLE_STARTUP_RECOVERY_V3_ZERO_CLICK_DEFECT_CORRECTION.md`.

## Corrected behavior

The V3 startup path no longer enters `ONE_CLICK_REQUIRED` merely because no head template exists.

1. Exact World/current runtime P1 lifecycle identifies the active P1 type/generation and exposes existing `x/y/z` only as a bounded consistency prior; no world-to-screen projection constant is introduced.
2. The current game-canvas screenshot first derives a bounded P1 HUD/identity visual signature. The HUD region can identify P1 but is explicitly excluded from the final live-scene seed region.
3. The live-scene search rejects low-detail, low-saturation and bright/effect-heavy patches, requires one safely unique P1-like candidate, and requires two consecutive consistent frames before seeding.
4. Safe unique automatic acquisition enters `HEAD_TRACKING` with `ownerClickCount=0`, `seedSource=AUTO_P1_HUD_SCENE_UNIQUE`, and no click surface is armed.
5. Only after the bounded automatic window is exhausted by ambiguity/failure may V3 enter `ONE_CLICK_REQUIRED`; the fallback is capped at one actual live-scene P1 head click per authority generation. HUD-zone clicks and second clicks remain fail-closed.
6. P1 generation/inactive transitions and canvas layout changes revoke stale visual authority. Confidence loss hides the marker and bounded local reacquisition restores it only after confidence returns.

Safety remains: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, production overlay suppressed during measurement, exact World/runtime generation binding retained.

## Implementation evidence

Corrected runtime commits/blobs selected by the immutable package include:

- `parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py` — blob `061925e2aef9a45efbc3bc09f15d6371953c0433`.
- `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js` — blob `e802b65f43eef71e7c0997ac2937b6aa8dcce234`.
- `parallel/PYLAUNCH/wof_launcher/render_authority_capture.py` — blob `38b9dd7fff3354750866bcf6def8953cad44d636`.
- `parallel/RENDER_AUTHORITY_V3/measurement_runner.py` — blob `dddbb8be8669a91ee272226df14622058c25d829`.
- `parallel/PYLAUNCH/wof_launcher/render_measurement_ui.py` — blob `2fde395bf83258a7a433a9c5f5784868205e89ae`.
- `parallel/OPTOOLKIT/owner_zh_cn.py` — blob `1224ec5841d63ea06f9a03796748313e64559f55`.
- accepted zero-click adjudication helper `parallel/PYLAUNCH/wof_launcher/zero_click_identity_acquisition.py` — blob `0c1cead751a7f6ee949c84eb61ab342062df9a57`.

Focused V3 source commit: `aabd8d24480c2056bb8772b2107098c121a37356`.

## Focused regression

Only the V3 zero-click correction behavior was exercised in the focused functional harness; result: **8/8 PASS**.

Covered gates:

- safe unique automatic P1 head seed -> `HEAD_TRACKING`, click count 0, click UI never armed;
- ambiguous lookalike -> no marker, bounded exhaustion -> exactly one fallback arm;
- second click and HUD portrait click impossible;
- HUD-only, scene lookalike/enemy-like duplicate, and bright effect evidence cannot silently become the wrong seed;
- P1 generation and canvas layout invalidation revoke stale templates/center;
- confidence loss hides marker and confident local reacquisition restores tracking;
- inactive P1 does not seed or arm a click.

The automatically triggered repository-wide legacy workflow was not used as this correction's focused gate. It contains stale assertions that still hard-code the pre-V3 package revision and an older Menu 6 route. Those assertions fail independently of the zero-click correction and were intentionally not modified because this task permits only the module-focused regression. Package integrity tests in that run nevertheless proved current runtime cannot drift/outgrow the manifest, every selected blob matches the pinned commit, mutation is rejected, and manifest immutability/safety checks pass.

## Immutable package

Corrected manifest commit: `5c53128ec584c1470873f305e0c3d3df77095f6a`.

Manifest: `parallel/OWNER_ONECLICK/package_manifest.json`

- package version: `2026.09.03.aabd8d24480c`
- source commit: `aabd8d24480c2056bb8772b2107098c121a37356`
- selection policy: `owner-oneclick-runtime-v6-render-authority-v3-zero-click-first-head-visual`
- `ownerClickExpectedNormal=0`
- `ownerClickFallbackMaximumPerAuthorityGeneration=1`
- `automaticSeedRequiredBeforeFallback=true`
- `hudPortraitMayIdentifyButNeverSeedSceneHead=true`
- `confidenceLossBehavior=HIDE_AND_AUTO_RECOVER`

GitHub Actions `Owner One-Click Package` run `33717341072`, job `windows-oneclick` completed successfully after this manifest was committed: immutable manifest load, fresh Chinese/space-path install, package-selected launcher smoke without Browser, LKG/current-pointer repair, and idempotent updater all PASS.

The previous V3 package is superseded for Owner testing. Do not test the old package.

## Final verdict

**COMPLETE — zero-click-first P1 head acquisition is implemented, the one-click path is fallback-only, the corrected runtime is immutably package-selected, focused regression is green, and V3 is ready for canonical/stage COMPLETE closeout.**
