# Alpha V1 Canonical Finalization — P15 + P17 + P18 Long 3-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

This dispatch replaces the finished P16 slot and the repository-exhausted W3 slot with two independent finalization modules while preserving the existing ACTIVE P15 ownership.

## Current truth

- P15 remains ACTIVE under its existing dedup-v2 claim. Do not duplicate or recover it.
- W3 repository-side qualification is SUBCOMPLETE and exhausted. Its existing logical claim remains authoritative; do not modify W3 producer/qualification code from P17/P18. The only remaining W3 proof is one bounded Owner normal-play sample later.
- P16 is COMPLETE and integration-ready. Its Owner status/evidence files may be consumed but must not be rewritten by P17/P18 except where explicitly allowed below.
- No real-WOF run is required by this dispatch. Implementation first; final concentrated Owner gate remains later.

## Parallel slots

### Slot 1 — existing P15

Stage: `ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE`

Continue under the existing claim only. P15 owns runtime convergence, semantic/spatial decoupling, canonical coordinator, package candidate generation/pinning, and its own focused checks.

### Slot 2 — P17 Owner Final Acceptance Orchestrator

Stage: `ALPHA_V1_PRODUCT_TAKEOVER_P17_OWNER_FINAL_ACCEPTANCE_ORCHESTRATOR`

Own only the final Owner acceptance orchestration layer. Build a one-command/one-click bounded acceptance runner that can later invoke the existing W3 qualification entrypoint, consume P16 acceptance evidence, consume P18 draw evidence when present, and produce one deterministic final evidence bundle and decision state. It must not modify W3/P15 runtime/package code or alpha-live.

### Slot 3 — P18 Maintained HUD Canonical Draw Acknowledgement

Stage: `ALPHA_V1_PRODUCT_TAKEOVER_P18_MAINTAINED_HUD_CANONICAL_DRAW_ACKNOWLEDGEMENT`

Own the maintained HUD draw acknowledgement/evidence seam. Add bounded evidence that canonical draw intents actually reached maintained WebGL draw primitives, plus a read-only collector that writes verification evidence. This is stronger than HUD ingest but still must not be reported as visual PASS without Owner screen confirmation.

## Cross-worker interface contract

P17 and P18 are intentionally parallel and must not require one another to have landed before implementation.

P18 must eventually produce a verification-only JSON snapshot at the default path:

`~/Documents/WOF_RESULTS/ALPHA_CANONICAL_DRAW_EVIDENCE.json`

with a stable top-level schema/version and at minimum:
- evidence state;
- exact current authority/runtime/renderer identity if bound;
- bounded canonical draw acknowledgement entries;
- draw intent kind/actor/label or warning identity as available;
- maintained native coordinates used by the draw primitive;
- no screenshot/world-projection authority;
- `visibleProof: "NOT_PROVEN"`.

P17 must treat that file as optional until P18 exists. Missing P18 evidence may yield `WAITING_DRAW_EVIDENCE` / `READY_FOR_VISUAL_CONFIRMATION` only, never PASS. P17 must not invent or infer draw evidence.

## File ownership

P15 owns:
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`
- P15 canonical runtime coordinator
- `product/alpha/wof_alpha_field_adapter.js`
- `parallel/OWNER_ONECLICK/refresh_manifest.py`
- P15 candidate/pin files and related package candidate flow.

P17 owns preferably:
- new files under `parallel/OWNER_ACCEPTANCE/`
- its focused tests/docs/results.

P17 must not edit P15 files, W3 files, P16 state/tray modules, maintained HUD JS, package manifests, or alpha-live selection.

P18 owns preferably:
- `product/alpha/wof_alpha_hud.js`
- a new narrow draw-evidence collector/helper beside launcher code if needed, but not `alpha_runtime.py`;
- focused P18 JS/Python tests/docs/results.

P18 must not edit P15 package/runtime files, W3 producer/qualification files, target/danger policy, or alpha-live.

## Safety and product invariants

Always preserve:
- exact World 921031 authority;
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- no screenshot/template/world projection as production coordinates;
- no guessed actor identity/generation;
- canonical authority changes revoke stale state;
- fixed TEST and P5 direct P1 behavior remain independent;
- no `VISIBLE`, `DRAWN`, `PASS` claim from module load, fake fixture, HUD ingest, or draw acknowledgement alone.

## Testing cadence

Implementation first. Each worker performs only its narrow focused self-checks. Do not run broad Fresh QA, historical regression, real-WOF, or Owner acceptance now.

The next PM step after these modules finish is one final candidate refresh that includes P15 + P16 + P17 + P18, then the single bounded W3/Owner acceptance round.
