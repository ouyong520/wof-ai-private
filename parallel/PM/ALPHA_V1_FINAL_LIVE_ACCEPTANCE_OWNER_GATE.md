# Alpha V1 Final Live Acceptance — Owner Gate

Status: BLOCKED — P33/P34/P35 COMPLETE; P36/P37/P38 DISPATCHED

P25, P27, P28, P29, P30, P31, P33, P34 and P35 are terminal COMPLETE at their repository-side authority boundaries. P26 remains historical terminal BLOCKED and must not be reopened or recovered. P32 is terminal BLOCKED with a truthful renderer-source causal-edge blocker.

The first real Owner Windows final-staging run reached the actual browser/game runtime and failed closed with `FAILED_EVIDENCE_MISMATCH`. Repo-side false-rejection, P9/P16 staging readiness, Page/Worker/WASM association, deterministic rebuild, retry-readiness gating and accepted-repair integration lineage are now terminally repaired/tested. The critical remaining product blocker is authoritative native-player-marker source tracing.

## PM-reviewed state

- P29 PM-accepted terminal COMPLETE, testedCommit `c02f7e108e73665f22eb950573622acb6f452732`.
- P30 PM-accepted terminal COMPLETE, testedCommit `90094a656ab311f18b0a758716dc97c3f8df092d`.
- P31 PM-accepted terminal COMPLETE, testedCommit `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731`.
- P32 terminal BLOCKED, testedCommit `bd75c3b5f7fd20fe004fae21142a0fa19942e076`, blocker `NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN`; its qualifier remains fail-closed and cannot be rewritten as PASS.
- P33 terminal COMPLETE: deterministic post-repair rebuild mechanism, testedCommit `c8c61112efbccdef5794ee68cd27767eacb72e96`.
- P34 terminal COMPLETE: isolated retry-readiness gate; current repository truth remains BLOCKED until renderer authority and one exact eligible containing candidate exist.
- P35 terminal COMPLETE: exact accepted-repair integration sourceCommit `82b0b09ecd902f502ae5509bcb3ee5a713f43fee`, tree `e5dba33a2cd579826704d3f78ec2587ee2305a5a`; P29/P30/P31 exact tested commits are true Git ancestors and accepted blobs matched 13/13.

## Product requirement — zero click

Final Alpha behavior must require **zero manual avatar/portrait clicks and zero manual player seeding**. Owner starts/plays the game; P1/P2/P3 acquisition and reacquisition must be automatic. Historical manual-click tracking may be used only as implementation evidence, never as the final interaction contract.

## Current three Worker lanes

1. P36 `ALPHA_V1_PRODUCT_TAKEOVER_P36_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_TRACE`
   - owns the critical direct displayed CPS1 renderer/object submission -> exact native `1P/2P/3P + down-arrow` object/cluster -> actor generation source trace;
   - may build a bounded read-only live proof producer, but no real game run under Worker authority;
   - P29/P32 proof criteria cannot be weakened.

2. P37 `ALPHA_V1_PRODUCT_TAKEOVER_P37_ZERO_CLICK_NATIVE_MARKER_AUTO_ACQUISITION_BASELINE`
   - restores an isolated zero-click automatic native-label/arrow acquisition baseline using historical tracker evidence;
   - explicitly verifies Y-axis orientation and loss/reacquisition behavior;
   - output is non-authoritative diagnostic evidence only and can never satisfy rendererSourceProof/P34 readiness.

3. P38 `ALPHA_V1_PRODUCT_TAKEOVER_P38_ACCEPTED_REPAIR_INTEGRATED_CANDIDATE_MATERIALIZATION`
   - consumes exact P35 source through P33 rebuild mechanics;
   - materializes and exact-readbacks one fresh accepted-repair integrated candidate/provenance;
   - must remain explicitly `NOT_RETRY_ELIGIBLE_PENDING_P36` while P36 is unresolved.

## Retry rule

No Owner rerun is authorized now. Do not spend the one bounded retry while P36 renderer-source authority is unresolved.

P37 may improve functional/visible automatic tracking confidence, but it is intentionally not authority. P38 may prove packaging/integration provenance, but it remains non-retry-eligible pending P36. After PM validates terminal P36 plus exact candidate/readiness truth, exactly one fresh bounded Owner live retry may be authorized.

Reuse the existing Windows repo, managed project venv, browser and Git objects; no unnecessary reinstall or redownload is authorized. Codex performs local deployment/run only; Owner performs actual game interaction and visual judgment.

Only explicit W3 `PASS` plus exact P16/P17 readiness may advance to the Owner visual question. A truthful `INCONCLUSIVE` remains fail-closed and must not be looped into blind normal-play retries.

Safety remains unchanged: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no guessed addresses, no screenshot/world-projection production coordinates, and no alpha-live movement before a separately guarded promotion action.
