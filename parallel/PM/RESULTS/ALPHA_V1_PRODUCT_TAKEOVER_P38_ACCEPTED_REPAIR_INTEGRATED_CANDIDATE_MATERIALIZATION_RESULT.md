# Alpha V1 P38 — Accepted Repair Integrated Candidate Materialization

## Terminal state

**COMPLETE** for the P38 materialization scope.

The exact P35 integrated source `82b0b09ecd902f502ae5509bcb3ee5a713f43fee` was materialized through the P33 tested deterministic rebuild mechanism into a fresh P38-only candidate/provenance set. This does **not** make the product retry-eligible: the terminal retry state remains **`NOT_RETRY_ELIGIBLE_PENDING_P36`**.

P32 remains terminal **BLOCKED** with `NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN`; P38 did not rewrite it to PASS. P36 remains ACTIVE without a terminal RESULT at final P38 readback.

## Exact materialized binding

- sourceCommit: `82b0b09ecd902f502ae5509bcb3ee5a713f43fee`
- source tree: `e5dba33a2cd579826704d3f78ec2587ee2305a5a`
- packageVersion: `2026.09.05.82b0b09ecd90`
- candidate SHA256: `53e4e2f2ad4c6c697b64d628b21576f341b3839bea8e2409057c0372fac56449`
- attestation SHA256: `5fdb606ee2aeb747a8bcda64c8009bb8d704820bcfa0000d1fd099c20fa6b68e`
- rebuild manifest SHA256: `1761fc613ccd84f2e7dc7bfe629113f2d2d07e4871996adc92260696d4cf906c`
- P38 pointer SHA256: `a2e676f8f08316ebbe50a6b032bde06159562615af66ad03c28f20d6a2ac7330`
- selected runtime file pins: `90`

The five published P38 artifacts on main exactly match the worker-tested Git blobs:

- candidate: `ee00156eb0a3fd94349ef1344f7f7651aee91a83`
- attestation: `d2102f3f2bf923c42a7d3fb7ff1d0ca7c459410c`
- rebuild manifest: `adb0611998e8da9fed78f675c156ecdc5d269a2a`
- P38 pointer: `48c6ca920a1b2ed93314e01bcfcd4c005521b367`
- P38 provenance: `3d1af5e3ba9d23472519d97e178f244fb4ea775a`

## Required accepted repair ancestry

Fresh independent compare readback reconfirmed all exact required tested commits are true ancestors of the source, with `behind_by=0` and each merge-base equal to that exact commit:

- P29: `c02f7e108e73665f22eb950573622acb6f452732`
- P30: `90094a656ab311f18b0a758716dc97c3f8df092d`
- P31: `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731`

## Deterministic verification

Durable tested materialization commit: `3e9ae7e725e3dd32d1172866fef11d3ff89e163f`, tree `2434e11c718741fae0c9186238d748df17c37abb`.

GitHub Actions run `33979187125`, job `101341180297`, completed SUCCESS. It used the P33 mechanism and verified:

- exact P35 source/tree,
- P29/P30/P31 ancestry,
- build-verify,
- a second identical-source build with identical SHA256 inventory,
- stale historical P19 source rejection via `STALE_P19_SOURCE_COMMIT_REJECTED`,
- P32 BLOCKED preservation,
- P36 pending state at materialization,
- unchanged alpha-live ref.

The exact tested artifacts were published to main by `107850cb8409dd3f2f1135022375114f96469035`; the temporary runner workflow was not published to main.

## Isolation and safety

P38 did not overwrite `parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json`; that global pointer remains on the historical `0752796369f1687435a1b1647e66ea0b5ab07688` source. This avoids silently implying retry readiness while P36 is unresolved.

No real WOF run occurred. No Owner visual acceptance was claimed. No RAM writes or input injection were performed. No promotion occurred. `alpha-live` remained `d664618403b1ae83f6880ca4d3833202c299415f`.

## Next action

Keep Owner retry blocked. After P36 reaches an accepted terminal state, rerun the deterministic final retry readiness gate against this fresh P38 candidate/provenance. Only an explicit successful readiness result may authorize the bounded Owner retry; P38 itself grants no retry or promotion authority.
