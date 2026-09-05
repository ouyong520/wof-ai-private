# Alpha V1 P27 — P21 Staged Runtime Canonical Feed Exposure RESULT

State: **COMPLETE / INTEGRATION-READY**

## Outcome

P27 closes the upstream seam identified by P25. The P21 exact-candidate staged runtime now exposes the real maintained candidate `P10 CanonicalRuntimeCoordinator` status (`wof-alpha-canonical-runtime-coordinator-v1`) through the existing staged publisher, with the exact same-session identity tuple `worldSha256 + pageTargetId + authorityKey + runtimeEpoch + rendererEpoch`.

This is **implementation proof only**. `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, and `alphaLiveMoved=false`.

## Implementation

Implementation commits:

- `2eddd1194a886c80629e3b115587754d6279a74a` — add `parallel/OWNER_STAGING/p27_canonical_feed_interposer.py`.
- `32e4b9f31cf6ba10118282bb0ef78166a11d7c41` — add focused P27 self-checks.
- `291919841dd673ec1363565410f0431e88ac0e66` — wrap the P21 staged runtime command after its builder returns.

The wrapper is intentionally applied **after** `build_runtime_command(...)`. That means the existing P25 runtime-command tee remains inside the wrapped command and cannot bypass P27, while the detached exact-candidate checkout is not modified.

Inside the staged process P27 imports the candidate's maintained P12/P10 runtime modules, activates P10 against the exact page/candidate identity, and observes the existing W3 actor snapshot only for explicit actor-slot/name plus generation identity. The validated P10 coordinator result is then surfaced as `canonicalCoordinator` and `alpha_status.canonicalOverlay`; `renderAuthorityV3` remains a separate diagnostic surface.

## Canonical truth boundary

P27 does **not** rename or reinterpret W3/V3 measurement state as a canonical feed.

Current W3 renderer-source qualification is still unproven. P27 therefore constructs only an identity frame for P12 and explicitly keeps `rendererSource.proven=false`. W3 `x/y/z`, candidate regions, structural rows, screenshots, world projection and guessed coordinates are never copied into the canonical frame. The real P10 coordinator consequently emits legal coordinate-free `SUPPRESSED/RENDERER_SOURCE_UNPROVEN` records until a separately legitimate renderer-source proof exists.

Duplicate same-sample replay is not accepted as a new cycle. Conflicting replay, stale/out-of-order samples, renderer identity mismatch, actor-generation regression, malformed coordinator output, or coordinate-bearing `SUPPRESSED` output fail closed and clear/revoke the previous feed. Runtime/renderer replacement also clears the old feed before rebinding, so old-cycle reuse is not permitted.

## Focused checks

- P27 deterministic focused self-checks: **6/6 PASS**.
- W3 coordinate/candidate stripping: **PASS**.
- Exposed status is the real P10 coordinator schema rather than V3 status: **PASS**.
- Duplicate replay rejection: **PASS**.
- Stale renderer epoch revokes old feed: **PASS**.
- Actor-generation regression revokes old feed: **PASS**.
- Coordinate-bearing `SUPPRESSED` canonical output rejection: **PASS**.
- Committed P21 wrapper readback from `main`: **PASS**.
- Committed P27 publisher/coordinator readback from `main`: **PASS**.
- Real staged WOF / Owner visual acceptance: **NOT_RUN** by authority.

No broad QA and no real WOF were run.

## Release / ownership boundaries

P27 changes only the narrow P21 staged runtime/status seam plus its helper/test. It does not modify P25 or P26 ownership, P22/P24 evidence logic, W3 producer ownership, the permanent W1 updater, or `alpha-live`.

Safety remains read-only: no RAM writes, no input injection, no legacy spatial fallback, no screenshot/world-projection production coordinates, no guessed coordinates/addresses, and no exact-candidate checkout mutation.

## Owner / PM next action

PM/downstream can now rerun the existing exact-candidate P21/P25 staged acceptance path against the maintained P19 candidate. P22/P24/P25 must consume only same-session P10 coordinator cycles surfaced through this P27 seam and remain fail-closed if renderer-source proof or required dynamic/stability evidence is still absent.

P27 itself does not run a real WOF session, does not claim visible proof, and does not promote `alpha-live`.
