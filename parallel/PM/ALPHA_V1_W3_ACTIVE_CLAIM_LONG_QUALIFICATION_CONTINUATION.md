# Alpha V1 W3 — ACTIVE Claim Long Qualification Continuation

Repository: `ouyong520/wof-ai-private`

This is a PM-authorized **new-thread reattach** to the existing ACTIVE W3 logical claim. It is not a new task, not recovery, and must not create a new canonical or stage claim.

Existing authority that must be re-read from latest `main` before work:
- stageId: `ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2`
- dedupKey: `alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2`
- exact claimToken: read from the existing canonical and stage claim; both must be ACTIVE and identical.
- existing canonical claim: `parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2.json`
- existing stage claim: `parallel/PM/STAGE_CLAIMS/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2.json`
- original execution authority: `parallel/PM/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2_START_PROMPT.md`
- current subresult: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_W3_RENDER_OBJECT_AUTHORITY_CONTINUATION_SUBRESULT.md`

If canonical/stage claim is no longer ACTIVE, tokens differ, or ownership changed, stop fail-closed and report the exact condition. Do not create, steal, edit, or recover the claim.

## Long-task goal

Continue W3 as one coherent renderer-source qualification workstream until the repository side is genuinely exhausted and the only remaining dependency, if any, is one bounded exact-World normal-play observation.

Do not split into micro-tasks. Spend the time to inspect the actual runtime/capture/analyzer chain, implement missing deterministic tooling, and leave one reproducible qualification route.

The non-negotiable truth boundary remains: no renderer/object source may become production position authority unless it is proven to correspond to the displayed CPS1 frame. Structural similarity, nearest objects, screenshots, world coordinates, row order, guessed offsets, stale buffers, or prior points are not proof.

## Required workstream A — exact renderer-source reverse trace

Read the existing W3 capture worker, launcher binding, measurement runner, canonical consumer, exact World/runtime identity code, and any maintained CPS1/WebAssembly/browser-side code that can materially identify the renderer/object submission path.

Trace, as far as repository/runtime evidence permits:
- where CPS1 sprite/object words are assembled or copied;
- whether there is a buffered object list, intermediate command buffer, renderer-side equivalent, or deterministic write sequence feeding the displayed frame;
- whether candidate 8-byte `[x,y,tile,attr]` regions can be causally linked to the render submission path rather than only pattern-matched;
- how buffer swaps/frame generations behave;
- what exact runtime/renderer epoch fields are required to prevent stale reuse.

If a source can be proven from code/runtime causality, document the full proof chain and update the qualification logic narrowly. If not, keep every candidate unverified.

## Required workstream B — deterministic qualification analyzer

Under `parallel/RENDER_AUTHORITY_V2/`, implement or substantially complete an offline/bounded analyzer that can consume the automatic W3 evidence bundle and produce a deterministic qualification report.

The analyzer should, where evidence supports it:
- correlate candidate table timelines with exact actor lifecycle/generation samples;
- correlate verification-only screenshots only as external confirmation, never as steady-state position authority;
- reject candidates with unstable layout, impossible native coordinates, inconsistent frame cadence, ambiguous actor association, generation mixing, or stale renderer epochs;
- identify whether one candidate/source remains uniquely consistent across movement/animation/scroll observations;
- emit explicit PASS / INCONCLUSIVE / REJECTED source qualification with reasons and evidence IDs;
- never choose a source merely because it has the highest score when uniqueness/proof thresholds are not met.

Prefer explicit machine-readable output so a later PM/Owner run produces a durable evidence bundle without manual JSON inspection.

## Required workstream C — one-command bounded live gate readiness

Make the existing normal-play capture path ready for one bounded Owner run without clicks, DevTools, coordinate calibration, file hunting, or repeated rituals.

Within W3-owned files only, ensure there is one clear entrypoint/runner that can:
1. bind exact World 921031 + runtime + fresh renderer epoch;
2. capture a bounded candidate timeline and verification frames while Owner simply plays normally;
3. stop automatically after the configured bounded interval/evidence threshold;
4. run the deterministic qualification analyzer automatically;
5. write one compact result/evidence bundle with exact source verdict and next action;
6. preserve `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

Do not move `alpha-live`, do not alter P15 package candidate files, and do not require Owner action in this implementation turn.

## Required workstream D — canonical producer contract readiness

If and only if a source is proven, ensure the emitted `wof-render-object-frame-v1` producer contract is complete enough for the already-complete P12/P10 chain:
- exact `worldSha256`, `authorityKey`, `runtimeEpoch`, `rendererEpoch`;
- native `384x224` contract;
- `rendererSource.proven=true` only under actual qualification;
- explicit actor association + generation rows;
- no ambiguous/implicit identity;
- multi-part body roles marked deterministically;
- no screenshot/world-projection coordinates as fallback.

If the source is not proven, keep producer frames `rendererSource.proven=false` / suppressed and leave P10 correctly hidden.

## File ownership

Allowed primarily:
- `parallel/RENDER_AUTHORITY_V2/**`
- `parallel/PYLAUNCH/wof_launcher/render_authority_capture.py`
- W3-specific evidence/qualification helpers beside those files
- exact W3 RESULT files

Forbidden:
- P15-owned `alpha_runtime.py`, canonical coordinator, field adapter semantic decoupling, package manifest/refresh candidate files;
- P10/P12/P11 implementation files except read-only inspection;
- `alpha-live` promotion;
- Collector / Unified Collector / Training Farm / 10训.

## Cadence

Implementation first. Run only focused checks needed for this W3 module: syntax/compile, deterministic analyzer fixtures, stale/ambiguous rejection, bounded runner dry/fake-CDP flow, and exact output contract checks. No broad QA or unrelated regression.

## Terminal result protocol

On this continuation terminal point, write:
- `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2_RESULT.md`

Use schema `wof-alpha-worker-result-v1` and the **existing** stageId/dedupKey/claimToken. If live evidence is still required, `SUBCOMPLETE` is correct; state the exact Owner gate and do not fabricate COMPLETE. If repository causality proves the source without live evidence, COMPLETE is allowed only with explicit evidence.

Final commit begins:
`WORKER_RESULT ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2 <STATE>`

Chat terminal only: `COMPLETE`, `SUBCOMPLETE`, or precise `BLOCKED`.