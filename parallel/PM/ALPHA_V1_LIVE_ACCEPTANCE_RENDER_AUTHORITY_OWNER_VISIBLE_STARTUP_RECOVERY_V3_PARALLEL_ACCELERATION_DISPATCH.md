# Alpha V1 Render Authority Owner-Visible Startup Recovery V3 — Parallel Acceleration Dispatch

Status: **PM AUTHORIZED — SUBWORKSTREAMS ONLY**

This dispatch accelerates the already ACTIVE V3 umbrella. It does not create a new Alpha recovery generation and does not supersede the current V3 canonical/stage claim. The current V3 umbrella worker remains integration/package/closeout authority.

## Objective

Shortest path to a usable Alpha V1:

`menu 6 -> correct/reused WOF -> visible tray/status -> zero-click-first P1 identity/head acquisition -> multi-template head tracking -> confidence-loss hide/auto-recover -> normal play -> automatic package/evidence`

The Owner must not be used as an engineering/debugging fixture. No Owner retest until the umbrella worker has integrated all accepted subresults and published a corrected immutable package.

## Parallel structure

### W1 — Umbrella / integration worker (already ACTIVE)

Owner: current V3 canonical claimant.

Responsibilities:
- keep current umbrella claim;
- integrate accepted W2/W3 outputs;
- own edits to existing integration/runtime files, especially:
  - `parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py`
  - `parallel/RENDER_AUTHORITY_V3/measurement_runner.py`
  - `parallel/OPTOOLKIT/owner_zh_cn.py`
  - package manifest/generator and V3 RESULT/claims;
- implement any glue needed for zero-click-first behavior;
- one coherent focused regression after integration;
- immutable package + durable RESULT + V3 canonical/stage COMPLETE.

W1 must not require an Owner click before attempting all safe zero-click acquisition paths.

### W2 — Zero-click identity/acquisition module

stageId: `ALPHA_V1_RENDER_AUTHORITY_V3_W2_ZERO_CLICK_IDENTITY_ACQUISITION`

dedupKey: `alpha.v1.render-authority-v3.w2-zero-click-identity-acquisition`

dedupProtocol: `v2`

dedupMode: `exclusive`

Scope:
- inspect existing HUD/player identity, exact World 921031 runtime state, sprite/tile/render evidence and current visual surfaces;
- implement a **separate, integration-ready zero-click acquisition module** that can determine P1 character identity and bounded scene-P1/head seed candidates without Owner input when safely unique;
- prefer reuse of existing proven identity/runtime signals and current canvas screenshots; ROM/tile data may only be read-only supporting evidence;
- return explicit confidence/ambiguity reasons and fail closed;
- expose an API that W1 can call before `ONE_CLICK_REQUIRED`;
- add module-owned deterministic fixtures for safe unique acquisition, ambiguity, wrong-HUD/portrait rejection and no-input safety;
- publish durable W2 SUBRESULT.

Write ownership:
- may create new files under `parallel/PYLAUNCH/wof_launcher/` with a distinct zero-click identity/acquisition filename;
- may create W2-specific tests/fixtures/results;
- **must not edit** `head_visual_tracker.py`, `measurement_runner.py`, `owner_zh_cn.py`, package manifests/generator, or V3 umbrella RESULT/claims.

Exit: `SUBCOMPLETE` with integration contract or precise `BLOCKED`.

### W3 — Zero-click fixture / acceptance / package-readiness gate

stageId: `ALPHA_V1_RENDER_AUTHORITY_V3_W3_ZERO_CLICK_ACCEPTANCE_FIXTURE`

dedupKey: `alpha.v1.render-authority-v3.w3-zero-click-acceptance-fixture`

dedupProtocol: `v2`

dedupMode: `exclusive`

Scope:
- no production implementation;
- build/read existing deterministic fixtures needed to prove the corrected user path:
  - zero-click-first is attempted before fallback click;
  - safe unique auto seed can reach head tracking with `ownerClickCount=0`;
  - ambiguity never silently binds a wrong actor/head;
  - one-click maximum only appears after automatic acquisition failure;
  - tray/status remains visible;
  - correct/reused WOF browser path, not blank browser;
  - confidence loss hides marker and recovery restores it;
  - lifecycle/runtime/layout invalidation revokes stale tracking;
  - package selects corrected runtime files;
  - read-only / `ramWrites=0` / `inputInjection=false` remain enforced.
- prefer existing tests/fixtures; do not rerun already-green unrelated suites;
- publish a durable W3 SUBRESULT with exact remaining live-only assertions.

Write ownership:
- tests/fixtures/docs/results only;
- **no production edits**, no package publication, no umbrella claim mutation.

Exit: `SUBCOMPLETE` or precise `BLOCKED`.

## Integration / conflict rules

- W2 and W3 must perform canonical dedup v2 preflight and obtain only their subworkstream claims.
- Neither may obtain or mutate the V3 umbrella claim.
- No two workers may edit the same production file.
- If an equivalent subworkstream is already ACTIVE/COMPLETE, return `ALREADY ACTIVE / COMPLETE — NO EXECUTION`.
- W1 is responsible for consuming subresults and resolving integration defects.
- Do not create V4/V5 or an independent QA chain from this dispatch.

## Testing cadence

Each subworker may run only module-owned focused self-checks. W1 runs the single integrated V3 regression after merging the coherent module. Do not test every small edit and do not repeat unrelated historical PASS suites.

## Owner gate

No Owner test until W1 has:
1. consumed W2/W3 or independently satisfied their contracts;
2. proven zero-click-first behavior in repository fixtures;
3. published a corrected immutable package;
4. written durable V3 RESULT and closed V3 claims, or documented one precise live-only gate.
