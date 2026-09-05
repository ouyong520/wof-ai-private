# Alpha V1 P25 — Final Acceptance Composite Capture Integration

P25 is an acceptance-tooling supervisor. It does **not** change the exact P19 candidate checkout, W3/P16/P17/P18/P21/P22/P24 semantics, or `alpha-live`.

The one-command path delegates exact candidate staging/runtime/W3/P16/P18/P17 orchestration to P21. P25 substitutes only P21's runtime command with `p25_runtime_tee.py`, which imports and executes the exact candidate's own `render_authority_measurement_entry.py` unchanged while teeing its existing publisher status into one bounded atomic ring. No HUD function is wrapped and no page/game-memory value is written by the tee.

After P21 cleanup, P25 replays only exact `wof-alpha-canonical-runtime-coordinator-v1` snapshots from that same run into P22 `DynamicActorStateCoverageRecorder.record_cycle(...)` and converts literal P10 READY/SUPPRESSED records into P24 observations. The ring is initialized with a fresh P25 nonce before staging and the nonce is verified after cleanup, so evidence from an older session cannot be reused. READY geometry is copied only from P10 `wof-render-object-anchor-v1`; SUPPRESSED records never get coordinates. Page/runtime/renderer replacements are explicit identity transitions. Duplicate/out-of-order transport snapshots are rejected.

P25 then calls the maintained P22/P24 report writers and hashes P21/W3/P16/P18/P22/P24/P17/P25 artifacts into `ALPHA_FINAL_ACCEPTANCE_COMPOSITE_INDEX.json`. Exact candidate identity is checked against both pre-run P19 resolution and final P21/P17 evidence. Missing canonical cycles, ring truncation, analyzer failure or identity mismatch fail closed. Maximum automatic state is `READY_FOR_OWNER_VISUAL_CONFIRMATION`; P20 remains the Owner visual/promotion gate.

Safety boundary: read-only, zero game RAM writes, no input injection, no screenshot/world-projection production coordinates, no nearest-object/row-order/cached-position fallback, and no `alpha-live` mutation.

## Current exact-candidate capability boundary

P25 intentionally does not manufacture a canonical feed. The current P19/P21 exact-candidate `render_authority_measurement_entry.py` publishes V3 measurement status but does not expose the maintained P10 canonical coordinator feed. In that case P25 still runs the existing P21/P17/W3/P16/P18 flow and emits deterministic incomplete P22/P24 evidence with `canonicalFeed.state=NOT_EXPOSED_BY_STAGED_RUNTIME_STATUS`. This is a fail-closed blocker, not permission to derive production coordinates from W3 actor/world values, P18 draw rectangles, screenshots, legacy projection, or HUD closure-private state. A future exact candidate that exposes the maintained coordinator through the existing publisher seam is consumed automatically without changing P22/P24 semantics.
