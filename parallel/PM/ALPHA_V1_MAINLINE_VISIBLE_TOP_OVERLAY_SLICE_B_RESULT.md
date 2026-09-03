# Alpha V1 Mainline Visible Top Overlay — Slice B Result

Status: **PACKAGE_READY / SUBCOMPLETE**

Authority: `parallel/PM/ALPHA_V1_MAINLINE_VISIBLE_TOP_OVERLAY_PARALLEL_2_WORKER_DISPATCH.md`

Scope executed: Slice B Owner entry / visible status / OWNER_ONECLICK manifest-generator-bootstrap package selection only. This Slice did **not** modify `head_visual_tracker.py` or maintained Alpha HUD/tracker algorithms. It does not publish an independent package and does not close the umbrella.

## Exact pins

- Slice A production runtime snapshot: `fe18750eb186bb85887af3a5b53ce6e85ce819c6`
- Selected immutable package source: `65422137bc1e20f640edf645532d0a924424c12f`
- Final manifest-selection commit: `08ed4d8a55ba45934343ac13682a02bd0337e48d`
- Package version selected by manifest: `2026.09.03.65422137bc1e`
- Runtime pin: `parallel/OWNER_ONECLICK/visible_overlay_runtime_pin.json`

The Slice A pin is validated as a complete critical runtime snapshot across Render Authority runner, semantic evidence producer, zero-click acquisition, head tracker, production overlay adapter, and maintained Alpha HUD dependencies. Package generation rejects source drift in those pinned blobs.

## Owner menu 6

Menu 6 is now owner-facing `打开 WOF 头顶显示` and is fail-closed behind the selected immutable manifest. It launches `parallel/PYLAUNCH/render_authority_measurement_entry.py` only when the manifest selects `production-top-overlay` and proves:

- `productionOverlayEnabled=true`
- `productionOverlaySuppressed=false`
- `diagnosticOnly=false`
- white acquisition marker is not the product
- automatic P1 acquisition precedes fallback
- fallback is bounded to at most one real P1-head click per authority generation
- read-only / RAM writes 0 / input injection false
- manual calibration false / legacy projection not selected

Empty-browser success is not a selected product state. Existing WOF is reused when available; otherwise runtime remains in the WOF-wait path instead of declaring success.

## Owner-visible states

The tray/status surface explicitly presents:

- 等待 WOF
- 正在自动找 P1
- 需要一次点击 P1 真实头部
- 正在建立头顶显示
- 头顶已显示
- 暂时丢失，恢复中
- BLOCKED

`头顶已显示` is not inferred from tracker state alone. It requires the maintained Alpha production HUD overlay to report visible plus actual draw evidence (`drawCount > 0` and `drawHooked=true`). During loss the product state reports recovery and the runtime contract hides the top overlay until authority recovers.

## Package selection/gates

`parallel/OWNER_ONECLICK/refresh_manifest.py` now produces only the visible production-top-overlay generation and refuses to generate a publishable manifest without the durable Slice A exact pin. It rejects overlay-disabled/suppressed, diagnostic-only, legacy projection/manual calibration, removed forked overlay, unsafe click ordering, and critical Slice A runtime drift.

`parallel/OWNER_ONECLICK/bootstrap_v2.ps1` independently rejects a manifest that fails the visible-overlay product contract and preserves last-known-good installation state.

The selected manifest contains 73 immutable runtime files from source `65422137...`, selects maintained `product/alpha/wof_alpha_hud.js`, records `emptyBrowserMayCountAsSuccess=false`, and pins Slice A `fe18750...`.

## Focused validation

GitHub Actions Owner One-Click Package run `33726121912` for manifest-selection commit `08ed4d8...` completed with all three jobs PASS:

- `integrity`: PASS — deterministic immutable manifest, mutation/LKG and package gates.
- `field-recovery-self-check`: PASS — identity/generation, re-entry recovery, discovery, live-proof Alpha gate, Owner menu integration, frozen Alpha product regression, syntax checks.
- `windows-oneclick`: PASS — immutable manifest load, fresh install in Chinese/space path, package-selected launcher smoke without Browser, explicit update preserving LKG, idempotent repeat update.

The preceding candidate generation on package source `65422137...` also generated the exact selected manifest with `sliceA=fe18750...` and 73 files.

## Handoff

Slice B is **package-ready** for the umbrella/mainline worker. No independent Owner package/release was emitted, and no umbrella claim was closed here. Umbrella may consume this manifest selection together with Slice A runtime acceptance for final mainline closeout.
