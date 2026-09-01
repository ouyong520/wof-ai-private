# HUDANCHOR Player-Follow Bounds — Fresh Independent QA Result

Stage: `HUDANCHOR_PLAYER_FOLLOW_BOUNDS_QA_V1`

Terminal status: **PASS — HUDANCHOR PLAYER-FOLLOW BOUNDS FRESH QA — BOUNDS CLOSED; WAITING PROJECTION PROOF**

## Independent verdict

The out-of-bounds fail-closed fix is accepted for repository-side bounds semantics.

The current `PlayerAnchorResolver.resolve()` rejects final finite head anchors when:

- `anchorXNative < 0`;
- `anchorXNative >= nativeWidth`;
- `anchorYNative < 0`;
- `anchorYNative >= nativeHeight`.

That rejection occurs before native -> drawing-buffer mapping and before warning-rectangle clamping. Therefore a valid body/reference with an invalid derived head anchor routes to fixed HUD with `PROJECTION_OUT_OF_BOUNDS`; it cannot be converted into an anchored cue clamped to the screen edge.

## Fresh independent execution

Added and executed:

`parallel/HUDANCHOR_PLAYER_FOLLOW_BOUNDS_QA/fresh_bounds_qa.js`

Fresh result:

```json
{"status":"PASS","passed":18,"total":18,"fixture":"FRESH_INDEPENDENT_SYNTHETIC_BOUNDS_QA_NOT_BROWSER_PROOF"}
```

This QA did not rely on the implementation lane's prior 8/8 or 15/15 result as proof.

The current implementation source was reconstructed in the execution environment and verified byte-for-byte by Git blob SHA before running the fresh matrix:

- GitHub/current source blob: `4beb7f8d4c9f815e125ed795aca536f02562f5d1`;
- locally executed source `git hash-object`: `4beb7f8d4c9f815e125ed795aca536f02562f5d1`.

The committed fresh QA file was likewise verified against the executed file:

- committed QA blob: `66496dbe4870e8922839cb41e302eb11cc0a68b3`;
- locally executed QA `git hash-object`: `66496dbe4870e8922839cb41e302eb11cc0a68b3`.

The implementation blob was re-read after execution and remained `4beb7f8d4c9f815e125ed795aca536f02562f5d1`; no implementation change occurred during QA.

## Adversarial matrix covered

Fresh execution validated:

1. final anchor X below 0 -> fixed HUD;
2. X exactly `nativeWidth` and beyond -> fixed HUD;
3. Y below 0 -> fixed HUD;
4. Y exactly `nativeHeight` and beyond -> fixed HUD;
5. valid body/reference + invalid derived head anchor -> fixed HUD, never edge-clamped anchored cue;
6. valid near-edge anchor stays anchored while only the warning rectangle clamps;
7. valid -> invalid clears smoothing/follow state; next valid frame starts from the fresh coordinate;
8. P1 -> P2 -> P3 retarget invalidates the old player immediately; invalid new target only fixed-fallbacks;
9. NaN/Infinity projection values plus zero/negative/malformed viewport dimensions fail closed;
10. resize/fullscreen/DPR mapping discontinuity resets smoothing and cannot reuse pre-change coordinates;
11. camera discontinuity, respawn/disappearance and lifecycle/object replacement reset follow state;
12. rapid alternating valid/out-of-bounds transitions never leave a stale anchored cue at an edge;
13. simultaneous P1/P2/P3 routing and same-player multi-warning aggregation remain intact;
14. presentation path remains read-only: only frame/draw adapter calls were observed and no gameplay-input/RAM-write primitive is present;
15. non-finite validation bounds fail closed;
16. projection-version changes reset smoothing;
17. epoch discontinuity fails closed and clears prior follow state;
18. stale projection/drawing-buffer samples fail closed instead of reusing old coordinates.

## QA harness note

The first fresh run stopped at the valid-near-edge case because the QA fixture used `384 - Number.EPSILON * 64`, which rounds to exact `384` at that magnitude and therefore correctly triggered the implementation's exclusive upper bound. The fixture was corrected to an unambiguously in-bounds `width/height - 1e-9`, after which the entire matrix passed 18/18. This was a QA-input correction, not an implementation defect.

## Product / safety semantics

Preserved:

- target identity remains P1/P2/P3-aware;
- retarget removes the old target-bound cue immediately;
- invalid/stale state falls back to fixed HUD;
- no stale coordinate reuse across invalid frames or mapping/lifecycle discontinuities;
- no RAM writes;
- no gameplay input injection;
- no implementation edit from this QA lane.

## Scope boundary

This PASS closes the known repository-side out-of-bounds drift blocker only.

It **does not** prove real Browser/WOF projection constants, camera/Y-Z behavior, head offset, or real live non-drift correctness. Synthetic bounds PASS must not be promoted into Browser projection proof.

The player-head HUD path may advance to the separate projection proof/integration gate.

Owner action: `NO`.

## Stop condition

**PASS — HUDANCHOR PLAYER-FOLLOW BOUNDS FRESH QA — BOUNDS CLOSED; WAITING PROJECTION PROOF**
