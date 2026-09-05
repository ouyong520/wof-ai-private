# Alpha V1 P32 — Native Player Marker Renderer Anchor Qualification — RESULT

## State

`BLOCKED`

P32 produced a durable, fail-closed native player-marker qualification seam and exact-byte focused regressions, but the repository still lacks the authoritative direct renderer causal edge required to prove the real WOF `1P` / `2P` / `3P` + down-arrow marker as production position authority.

## Durable implementation

Tested candidate: `bd75c3b5f7fd20fe004fae21142a0fa19942e076`.

Owned implementation:

- `parallel/RENDER_AUTHORITY_V2/native_player_marker_anchor_qualification.py`
- `parallel/RENDER_AUTHORITY_V2/test_native_player_marker_anchor_qualification.py`
- `parallel/RENDER_AUTHORITY_V2/NATIVE_PLAYER_MARKER_RENDERER_ANCHOR_QUALIFICATION.md`

The qualifier requires exact native `384x224` coordinates, explicit `P1` / `P2` / `P3` plus actor generation, exact `runtimeEpoch` / `rendererEpoch` / `authorityKey`, explicit non-guessed source derivation, direct displayed-frame causal linkage, deterministic explicit cluster membership, and exactly one down-arrow anchor member. Duplicate/ambiguous/stale/mixed/generation-mismatched evidence fails closed with no proof object.

No P29 analyzer, P30 staging/P16/P9 binding readiness, P31 Page/Worker/WASM association, HUD, promotion, or alpha-live path was modified.

## Focused self-check

Terminal-significant tests were run only after the implementation was durable. GitHub candidate readback matched the exact local Git blob identities:

- qualifier: `dd1cf633193312d65bc241b86eb23dace0656508`
- regression: `1131c5c24b5558d5419b90cec24fa82b34219fef`
- qualification document: `1ebbf944bdede60406da839e327ab6227b2dd72f`

Checks:

- `python -m py_compile native_player_marker_anchor_qualification.py test_native_player_marker_anchor_qualification.py` — PASS.
- `python -m unittest -v test_native_player_marker_anchor_qualification.py` — 7/7 PASS.
- Coverage includes all P1/P2/P3 slots, exact generation binding, single-object and deterministic row-order-independent multi-object markers, duplicate ambiguity rejection, stale runtime/renderer/authority rejection, generation mismatch rejection, visual/structural-only rejection, and no proof when the displayed-frame causal link is absent.
- P29 `qualification_analyzer.py` at the tested candidate remains blob `a412faa31ac8d946e25f72868a57ae234d92b4b2`; its PASS/INCONCLUSIVE/REJECTED criteria were not weakened.

The positive direct-source rows in the unit test are contract fixtures only. They are not real WOF evidence, are not W3 PASS evidence, and are not accepted as product proof.

## Exact blocker

`NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN`

The current checked-in W3 worker records actor lifecycle plus structural HEAP candidates and explicitly labels renderer source qualification as `UNVERIFIED_CANDIDATE_ONLY`. No checked-in source-traced pointer, direct renderer hook, or exported renderer pointer proves:

`displayed CPS1 renderer/object submission -> exact native 1P/2P/3P marker object/cluster identity + explicit actor generation association`

Without that edge, producing real `rendererSourceProof` would be synthetic. Structural HEAP, screenshot/OCR/template coordinates, world projection, nearest-distance, row order, and timing are not substituted.

## Product-proof truth

- real WOF acceptance: `NOT_RUN`
- Owner visual acceptance: `NOT_RUN`
- visible proof: `NOT_PROVEN`
- W3 live marker PASS: not claimed
- promotion: not performed
- alpha-live moved: `false`
- RAM writes: `0`
- input injection: `false`

Repo-side qualification behavior is tested; the real native player marker authority is not proven.

## Next action

PM should schedule a successor only after an exact source-traced native-marker renderer submit hook/exported pointer is available. That successor can feed one bounded real-game direct capture through the P32 fail-closed seam; it must not reopen this BLOCKED claim or downgrade the P29 direct-proof contract.
