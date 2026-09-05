# Alpha V1 P37 — Zero-Click Native Marker Auto-Acquisition Baseline — RESULT

## State

`COMPLETE`

Classification remains **`UNVERIFIED_AUTO_BASELINE`**. P37 completed the isolated functional/diagnostic baseline required by the START prompt. This is not renderer authority and does not make any Owner retry or promotion eligible.

## Durable implementation

Tested candidate: `64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530`

Tested tree: `ea78cd46a7270f53804c22eef7b62d396a9a3956`

Owned files:

- `parallel/AUTO_MARKER_BASELINE/native_marker_auto_acquisition_baseline.js` — blob `2a0094b3588d4a27c8c7a6f9940b8a3b1941f8c4`
- `parallel/AUTO_MARKER_BASELINE/test_native_marker_auto_acquisition_baseline.js` — blob `ed0a4135d7f4ba00f8bad04f0112655aba7ff228`
- `parallel/AUTO_MARKER_BASELINE/README.md` — blob `092ddd78f12ffad359c054479ee3750115239de2`

The baseline recovers the useful historical `6eeebf4a00ce7751ce9ba6008982e8136d1c4290` mechanics: player-color masking, native label/down-arrow structural grouping, bounded velocity continuity, and two-observation automatic reacquisition. Its historical F6/F7/manual-click seed path is deliberately absent. All P1/P2/P3 players are scanned automatically on every supplied native frame.

`d30a071c668c716cd8d9b5d02932808c76c7a3a7` was used only as historical evidence that Alpha HUD had consumed a screen-space tracker. P37 did not modify maintained HUD, P36 source-trace, P29/P32 qualification, P38 candidate materialization, promotion, or alpha-live paths.

## Focused self-check

After all implementation bytes were durable, GitHub exact readback matched the three blob identities above. The terminal-significant suite was then rerun against that exact candidate and passed **6/6**.

Coverage:

- zero-click startup/acquisition;
- automatic P1/P2/P3 distinction;
- jump-like movement, bounded short loss, long-loss automatic reacquisition;
- left/right coordinate preservation;
- explicit up/down Y-axis non-inversion regression;
- multi-candidate ambiguity fail-closed;
- invalid native-frame fail-closed;
- proof boundary: output can never emit `rendererSourceProof` or qualify P29/P32/P36/P34/promotion authority.

Real WOF / Owner visual acceptance: `NOT_RUN` by explicit P37 scope.

## Coordinate and reacquisition behavior

P37 uses native `384x224` with top-left origin: X increases right and Y increases down. Deterministic fixtures prove left lowers X, right raises X, upward movement lowers native Y, downward movement raises native Y, and viewport mapping preserves that orientation without `224-y` or equivalent GL-style inversion.

After a unique structural marker is acquired, bounded velocity prediction is allowed only for continuity. When the track is lost or a unique candidate jumps beyond the continuity envelope, automatic reacquisition requires a second nearby observation within the bounded window. No click or player seed is accepted.

If a player has more than one distinct structurally valid label+down-arrow cluster in a frame, P37 returns `AMBIGUOUS` and exposes no current X/Y. History, nearest distance, row order, timing, or prior player focus are never used to choose among multiple structural candidates.

## Authority and product-proof boundary

Every baseline envelope is labeled `UNVERIFIED_AUTO_BASELINE`, sets `coordinateAuthority=DIAGNOSTIC_FRAME_PIXEL_NATIVE_384X224_NOT_RENDERER`, and keeps `rendererSourceProof=null`. P29 PASS, P32 native-marker qualification, P36 renderer source trace, P34 retry readiness and promotion eligibility are all permanently false at this boundary.

Therefore P37 proves only deterministic baseline behavior on fixtures. It does **not** prove real WOF visible correctness, exact displayed CPS1 renderer/object submission, actor-generation causality, or native marker authority. P36 alone owns the missing direct renderer source-trace lane.

## Safety and next action

- read-only: `true`
- RAM writes: `0`
- input injection: `false`
- real game run: `NOT_RUN`
- Owner YES/NO: `NOT_RUN`
- promotion performed: `false`
- alpha-live moved: `false`

Next: PM may use this baseline only as non-authoritative correlation input for P36 or a later bounded diagnostic. P37 itself must not authorize an Owner retry or promotion.
