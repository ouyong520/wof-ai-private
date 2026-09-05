# Alpha V1 Final Live Acceptance — Owner Gate

Status: BLOCKED — P29/P30/P31 PARALLEL REPAIR REQUIRED

P25 and P28 remain terminal COMPLETE / integrationReady=true. P26 remains historical terminal BLOCKED and must not be reopened or recovered. P27 remains terminal COMPLETE and its staged maintained P10 canonical-feed seam remains authoritative.

The first real Owner Windows final-staging run reached the actual browser/game runtime and failed closed with `FAILED_EVIDENCE_MISMATCH`. The live evidence now proves three independent repository-side defects, so the prior unclaimed monolithic P29 repair was superseded by three project Workers. Codex remains local deployment/runtime operator only and must not implement repository code.

## Proven live blockers

1. W3 evidence-contract defect:
   - W3 `REJECTED` with `same heap offset appears with inconsistent byte order`;
   - timeline frames lacked bound runtime/renderer/authority epoch stamps;
   - no legitimate `rendererSourceProof` exists;
   - structural candidates remain `UNVERIFIED_CANDIDATE_ONLY` and must never self-qualify.
2. P16/P9/P1 staging defect:
   - `ProductionP1OverlayError: maintained Alpha HUD P1 binding failed`;
   - `Error: WOF Alpha canonical anchor envelope P9 missing`;
   - P16 was captured at `VERIFYING_WORLD`, `world.accepted=false`, with incomplete runtime identity;
   - P1 live gate remained false and production overlay did not draw.
3. Page association ambiguity:
   - discovery reported `WOF page association ambiguous: 2 page targets` despite browser/Page/Worker/WASM/HEAP being present;
   - association must become deterministic from authoritative evidence or remain fail-closed.

## Current repair ownership

- P29 `ALPHA_V1_PRODUCT_TAKEOVER_P29_W3_LIVE_EVIDENCE_CONTRACT_REPAIR`: W3 capture/analyzer/runtime evidence contract only.
- P30 `ALPHA_V1_PRODUCT_TAKEOVER_P30_P16_P9_BINDING_AND_STAGING_READINESS_REPAIR`: maintained P9/P1 binding and P16 staging readiness only.
- P31 `ALPHA_V1_PRODUCT_TAKEOVER_P31_WOF_PAGE_ASSOCIATION_AMBIGUITY_REPAIR`: Page/Worker/WASM discovery and ambiguity resolution only.

All three must preserve fail-closed truth. No Worker may fabricate the missing direct displayed-frame renderer/object causal edge, use screenshot/world projection as production coordinates, guess addresses, move alpha-live, run promotion, or claim Owner visual acceptance.

## Retry rule

Do not ask the Owner to rerun the game until P29/P30/P31 have terminal results and PM validates their integration on latest main. Reuse the existing Windows repo, managed project venv, browser and Git objects; no unnecessary reinstall or redownload is authorized.

After integrated repo-side repair, Codex may perform the local deployment/run only. Owner performs actual game interaction and visual judgment. Only explicit W3 `PASS` plus exact P16/P17 readiness may advance to the existing P20 Owner question. A truthful `INCONCLUSIVE` remains fail-closed and must not be looped into blind retries.

Safety remains unchanged: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no guessed addresses, no screenshot/world-projection production coordinates, and no alpha-live movement before a separately guarded promotion action.
