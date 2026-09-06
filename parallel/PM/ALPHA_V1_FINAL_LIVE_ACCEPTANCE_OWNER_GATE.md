# Alpha V1 Final Live Acceptance — Owner Gate

Status: BLOCKED — P39 COMPLETE; P40 TERMINAL BLOCKED; P42/P43 DISPATCHED; no Owner retry yet

P25, P27, P28, P29, P30, P31, P33, P34, P35, P36, P37, P38 and P39 are terminal COMPLETE at their repository-side authority boundaries. P26 remains historical terminal BLOCKED and must not be reopened. P32 remains historical terminal BLOCKED authority; its direct renderer proof requirement is still enforced by the unchanged qualifier. P40 is a newer terminal BLOCKED runtime-exposure successor and must not be rewritten to PASS.

## Fresh PM-reviewed state

- P36 terminal COMPLETE, testedCommit `162e50b6c65fd1d3901ad694854563b686b2ce22`, integrationReady=true. A durable zero-click read-only renderer-submit source observer/proof producer exists, but real WOF live source authority is NOT_PROVEN.
- P37 terminal COMPLETE, testedCommit `64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530`, classification `UNVERIFIED_AUTO_BASELINE`.
- P39 terminal COMPLETE, testedCommit `ac5387f00d8c2382dcf3ed435ffcfa0acc1a2f05`. The zero-click P1/P2/P3 baseline is now wired into the maintained HUD under a diagnostic/staging gate, with non-inverted native 384x224 mapping, fail-closed stale/lost/ambiguity handling, and unchanged production-authority behavior when the gate is closed. Real WOF visibility remains NOT_RUN.
- P40 terminal BLOCKED, testedCommit `5a3b9bce01e794e030974a94f7511a39fa56e818`, blocker `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`. Fresh checked-in runtime inspection found only generic WebGL draw hooking plus HEAP/ROM/CPS RAM/world-projection surfaces, not one truthful exported/source-traced per-object gstyphoon displayed submit carrying marker identity, actor generation, native 384x224 coordinates and runtime authority identity.
- The failed P41 attempt never acquired a canonical/stage claim and created no PROGRESS/RESULT/implementation. It is not ownership and is superseded by P43 with a fresh dedup key.

## Product requirement — zero click

Final Alpha behavior requires zero manual avatar/portrait clicks, zero manual player selection and zero manual seed. Owner starts/plays the game; P1/P2/P3 discovery/reacquisition must be automatic.

## Current two Worker lanes

1. P42 `ALPHA_V1_PRODUCT_TAKEOVER_P42_GSTYPHOON_RENDERER_SUBMIT_CORRELATION_PROBE`
   - successor to terminal BLOCKED P40, not recovery;
   - build bounded read-only diagnostic capture of actual gstyphoon/WebGL/WASM submission context;
   - may correlate P37/P39 `UNVERIFIED_AUTO_BASELINE` coordinates only to narrow the renderer mapping for a later authority successor;
   - cannot emit rendererSourceProof or the P36 direct-source surface.

2. P43 `ALPHA_V1_PRODUCT_TAKEOVER_P43_BOUNDED_ZERO_CLICK_LIVE_DIAGNOSTIC_HARNESS`
   - clean successor to the failed pre-claim P41 attempt;
   - preserve exact source/candidate/manifest/attestation, Page/Worker/WASM, P16/P17/P9, runtimeEpoch/rendererEpoch/authorityKey, P36 raw source/events/producer/P32 result, P39 diagnostic visibility, optional P42 bundle and complete raw runtime/console/staging logs;
   - machine-read the first failing gate instead of collapsing failures to one summary string;
   - no real game run under Worker authority.

## Next-run rule

No Owner final retry is authorized yet. P42/P43 must terminalize first. PM will then materialize one fresh exact diagnostic candidate containing accepted P36/P37/P39 and the new probe/harness as appropriate.

Because P40 is terminal BLOCKED, the next real-WOF run—if separately authorized after candidate/readiness checks—must be treated as a bounded diagnostic/source-mapping run unless a truthful direct renderer source is already present. It may confirm P39 visible automatic following and collect the evidence needed to resolve P40, but it must not be mislabeled as final renderer authority or promotion acceptance.

The run must preserve complete raw logs/receipts and exact gate transitions so any failure can be attributed to the actual source/identity/gate stage.

Reuse the existing Windows repo, dedicated project venv, browser and Git objects; no unnecessary reinstall/redownload and no global Python/PATH/site-packages changes. Codex performs local deployment/run only; Owner performs actual game interaction and visual judgment.

Only explicit live renderer authority plus exact P16/P17 readiness may advance to the final Owner visual acceptance question. A truthful INCONCLUSIVE/BLOCKED remains fail-closed.

Safety remains unchanged: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no guessed addresses, no screenshot/world-projection production coordinates, and no alpha-live movement before a separately guarded promotion action.
