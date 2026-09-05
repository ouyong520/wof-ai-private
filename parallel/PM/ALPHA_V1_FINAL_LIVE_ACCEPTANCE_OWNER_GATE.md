# Alpha V1 Final Live Acceptance — Owner Gate

Status: BLOCKED — P29 LIVE EVIDENCE CONTRACT REPAIR REQUIRED

P25 and P28 remain terminal COMPLETE / integrationReady=true. P26 remains historical terminal BLOCKED and must not be reopened or recovered. P27 remains terminal COMPLETE and its staged maintained P10 canonical-feed seam remains authoritative.

A real Owner Windows staging run against exact P19 candidate `0752796369f1687435a1b1647e66ea0b5ab07688` reached the browser/game runtime and produced bounded evidence, but the final live path failed closed with `FAILED_EVIDENCE_MISMATCH`. This is now a concrete repository-side acceptance-contract defect, not an instruction to repeat blind normal-play.

Observed live facts:
- W3 result: `REJECTED`, not `INCONCLUSIVE` and not `PASS`.
- rejection: `same heap offset appears with inconsistent byte order`.
- evidence gaps include no stable candidate, missing per-frame runtime/renderer/authority epoch stamps, and absent `rendererSourceProof`.
- P16 captured `world.accepted=false`, canonical state `VERIFYING_WORLD`, and null runtime authority/epoch/renderer fields while the independent W3 measurement later locked the exact World identity.
- the staged runtime also surfaced a maintained P1 binding failure before terminal cleanup.
- safety held: readOnly=true, ramWrites=0, inputInjection=false, alpha-live did not move, Owner visual acceptance was NOT_RUN.

The checked-in W3 authority explicitly says structural HEAP candidates remain `UNVERIFIED_CANDIDATE_ONLY`, direct displayed-frame renderer/object causality must never be fabricated, and a valid safe capture that still lacks that causal proof must remain `INCONCLUSIVE` rather than becoming a guessed PASS. P29 must repair the live evidence contract without weakening that truth boundary.

## P29 required repair boundary

P29 owns only the final live-evidence/staging seam needed to make the existing contract internally coherent:

1. W3 bounded capture/analyzer consistency:
   - carry exact `runtimeEpoch`, `rendererEpoch`, and `authorityKey` on every timeline frame used by the analyzer;
   - remove the current false-rejection conflict where the scanner intentionally considers both BE16/LE16 candidates at one heap offset but the analyzer rejects that diagnostic state as an inconsistent byte order;
   - preserve the rule that structural/stable candidates never self-qualify as renderer authority;
   - if no legitimate `rendererSourceProof` exists, a safe structurally valid run must be `INCONCLUSIVE`, not fabricated `PASS` and not a contract-artifact `REJECTED`.
2. P16 staged evidence timing:
   - do not snapshot a fresh-but-still-`VERIFYING_WORLD` P16 record as final staged P16 evidence;
   - require exact World accepted identity plus the runtime authority fields needed downstream before treating P16 as usable;
   - diagnose and repair the staged maintained P1/HUD binding failure only insofar as it prevents P16 exact-World/runtime readiness.
3. Keep P21/P25/P27/P28 terminal truth intact. Do not reopen their claims. Do not modify alpha-live.
4. Do not invent the missing direct displayed-frame renderer/object causal edge. If, after contract repair, the repository still cannot produce `wof-renderer-source-proof-v1`, preserve a truthful `INCONCLUSIVE` live result and report the remaining product blocker precisely.

## Retry rule

Do not ask the Owner to rerun the game until a durable P29 candidate has passed focused deterministic self-checks for the repaired contract. Reuse the existing Windows repo, managed project venv, browser and Git objects; no unnecessary re-download/reinstall is authorized.

Only after P29 terminal COMPLETE / integrationReady=true may PM authorize one fresh bounded Owner live run. Only an explicit W3 `PASS` plus exact P16/P17 readiness may advance to the existing P20 Owner visual question. If W3 remains truthful `INCONCLUSIVE`, stop fail-closed and report the remaining direct renderer-proof blocker instead of looping Owner normal-play.

Safety remains unchanged: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no guessed addresses, no screenshot/world-projection production coordinates, and no alpha-live movement before a separately guarded promotion action.
