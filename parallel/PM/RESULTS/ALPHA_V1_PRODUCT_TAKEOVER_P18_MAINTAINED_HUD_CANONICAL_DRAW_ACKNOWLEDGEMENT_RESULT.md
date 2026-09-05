# Alpha V1 P18 — Maintained HUD Canonical Draw Acknowledgement

## Outcome

**COMPLETE.** P18 now advances canonical evidence from HUD ingest to a bounded acknowledgement that is created only after the maintained WebGL draw primitive actually completes. This is **not visual PASS**; `visibleProof` remains `NOT_PROVEN`.

## Changes

- Added a 128-entry bounded canonical draw ledger inside the maintained HUD. Rebind, revoke, and transport reset start a fresh evidence generation.
- Enemy target-label acknowledgement is recorded only after the maintained label-atlas native draw completes; player danger acknowledgement is recorded only after the maintained warning-texture native draw completes.
- Ledger rows preserve canonical actor/generation or warning identity, 384×224 native anchor, drawing-buffer rectangle, sample identity, and exact authority/runtime/renderer/World binding.
- Added read-only `WOFALPHAHUD.canonicalDrawEvidence()`; no evidence mutator is exported. Fixed TEST and P5 direct-P1 paths do not populate the canonical ledger.
- Added a read-only CDP collector that attaches only to an explicit accepted page target, validates exact World/authority/runtime/renderer identity, rejects stale/mismatched evidence, and atomically writes `~/Documents/WOF_RESULTS/ALPHA_CANONICAL_DRAW_EVIDENCE.json`.
- Aligned the external snapshot to the completed P17 reader contract: `wof-alpha-canonical-draw-evidence-v1`, version `1`, with explicit `identity`.

Implementation commits: `b018d27643d157d47a82ed54a0023770a727b600`, `519a27d6cf1e91545c6495812b1472c876d0e565`.

## Tests

- `node --check product/alpha/wof_alpha_hud.js` — PASS.
- `node --check product/alpha/maintained_hud_canonical_draw_evidence_selfcheck.mjs` — PASS.
- Focused maintained-HUD fixture — PASS: ingest alone produces no row; canonical enemy/player primitives acknowledge only after native draw; mismatch/rebind/revoke/bounded-ledger behavior is fail-closed; fixed TEST/P5 are excluded.
- Python compile for collector/tests — PASS.
- Fake-CDP collector suite — PASS, 5 tests covering exact acceptance, runtime/renderer mismatch, page mismatch, HUD API missing, no-draw state, atomic output, and P17-compatible schema/identity.
- Real WOF / Owner visual acceptance — **NOT RUN** by design.

## Integration

P18 evidence chain is: P9/P8 canonical authority and draw intent → maintained WebGL primitive completion → bounded HUD ledger → read-only HUD API → explicit-target CDP collector → P17 `ALPHA_CANONICAL_DRAW_EVIDENCE.json` reader. P15 package/runtime and W3 were not modified, and alpha-live was not moved.

## Owner Action

After PM refreshes the final selected candidate to contain P15 + P16 + P17 + P18, use the P17 one-command acceptance flow and visually confirm the overlay follows the correct actors during normal WOF play. Draw acknowledgement must not be interpreted as visible proof.

## Recommended Next

PM should integrate/refresh the final candidate without moving alpha-live. P17 may treat `CANONICAL_DRAW_ACKNOWLEDGED` as the highest automatic draw-evidence gate, but final acceptance remains `READY_FOR_OWNER_VISUAL_CONFIRMATION` until Owner visual confirmation.
