# Alpha V1 Final Live Acceptance — Owner Gate

Status: BLOCKED — P30/P31 ACTIVE + P32 NATIVE MARKER PROOF-PRODUCER PREP

P25 and P28 remain terminal COMPLETE / integrationReady=true. P26 remains historical terminal BLOCKED and must not be reopened or recovered. P27 remains terminal COMPLETE and its staged maintained P10 canonical-feed seam remains authoritative.

The first real Owner Windows final-staging run reached the actual browser/game runtime and failed closed with `FAILED_EVIDENCE_MISMATCH`. The run exposed three repository-side defects plus the still-missing direct displayed-frame renderer/object causal edge needed for W3 authority.

## PM-reviewed state

- P29 `ALPHA_V1_PRODUCT_TAKEOVER_P29_W3_LIVE_EVIDENCE_CONTRACT_REPAIR` is PM-accepted terminal COMPLETE for the repository-side W3 evidence contract. Its durable tested candidate is `c02f7e108e73665f22eb950573622acb6f452732`. Timeline epoch stamps, same-offset BE16/LE16 semantics and stale/mixed-epoch rejection are repaired; structural-only evidence remains INCONCLUSIVE and no rendererSourceProof/PASS was fabricated. Real WOF and Owner visual acceptance remain NOT_RUN.
- P30 `ALPHA_V1_PRODUCT_TAKEOVER_P30_P16_P9_BINDING_AND_STAGING_READINESS_REPAIR` remains ACTIVE. It owns only exact staged P19 manifest binding, maintained P9/P1 dependency binding, and P16 readiness hardening.
- P31 `ALPHA_V1_PRODUCT_TAKEOVER_P31_WOF_PAGE_ASSOCIATION_AMBIGUITY_REPAIR` remains ACTIVE. It owns only deterministic Page/Worker/WASM association and stale/duplicate target rejection.
- P32 `ALPHA_V1_PRODUCT_TAKEOVER_P32_NATIVE_PLAYER_MARKER_RENDERER_ANCHOR_QUALIFICATION` is newly dispatched to prepare a read-only authoritative proof path for WOF's own native `1P` / `2P` / `3P` downward player marker as a possible native 384x224 player anchor.

## Remaining proven live blockers

1. P16/P9/P1 staging readiness:
   - prior live error `ProductionP1OverlayError: maintained Alpha HUD P1 binding failed`;
   - prior live error `Error: WOF Alpha canonical anchor envelope P9 missing`;
   - prior P16 was captured at `VERIFYING_WORLD`, `world.accepted=false`, with incomplete runtime identity.
2. Page association ambiguity:
   - prior discovery reported `WOF page association ambiguous: 2 page targets` despite Page/Worker/WASM/HEAP being present.
3. Renderer-source authority:
   - P29 repaired false REJECTED contract behavior but did not and must not invent the missing direct displayed-frame renderer/object causal edge;
   - WOF's native player marker is now being qualified by P32 as a potentially cleaner anchor source, but structural HEAP matches, screenshot/OCR/template coordinates, world projection, ordering, timing and nearest-distance guesses remain non-authoritative.

## Retry rule

Do not ask the Owner to rerun the game while P30 or P31 is non-terminal. Also do not spend the one bounded retry blindly if P32 has not yet either (a) reached COMPLETE with a durable read-only marker/direct-render proof producer ready for live verification, or (b) terminally identified an exact unavoidable live causal dependency/blocker that PM explicitly accepts.

After PM validates terminal P30/P31 and the P32 proof-producer state on latest main, exactly one fresh bounded Owner live retry may be authorized. Reuse the existing Windows repo, managed project venv, browser and Git objects; no unnecessary reinstall or redownload is authorized. Codex performs local deployment/run only; Owner performs actual game interaction and visual judgment.

Only explicit W3 `PASS` plus exact P16/P17 readiness may advance to the existing P20 Owner question. A truthful `INCONCLUSIVE` remains fail-closed and must not be looped into blind normal-play retries.

Safety remains unchanged: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no guessed addresses, no screenshot/world-projection production coordinates, and no alpha-live movement before a separately guarded promotion action.
