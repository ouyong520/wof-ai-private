# Alpha V1 Canonical Release — P18 / P19 / P20 Long 3-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

Purpose: keep the remaining Alpha product work in three coherent long-running modules instead of micro-stages.

Current accepted baseline:
- P15 canonical product convergence/package candidate: COMPLETE / integration-ready.
- P16 Owner canonical status + acceptance evidence: COMPLETE / integration-ready.
- P17 Owner final acceptance orchestrator: COMPLETE / integration-ready.
- W3 repository-side renderer qualification: SUBCOMPLETE; repository-side work exhausted, one bounded Owner normal-play sample remains the only legitimate live evidence dependency.
- P18 maintained HUD canonical draw acknowledgement: ACTIVE and continues under its existing exclusive claim.

This dispatch has three logical workers:

1. P18 — continue existing ACTIVE maintained HUD canonical draw acknowledgement. No new claim, no recovery, no ownership change.
2. P19 — Final Canonical Candidate Rebuild + Attestation. Build the one final package candidate from a source commit that includes the completed canonical stack and late acceptance/evidence modules, with deterministic pin/attestation and no alpha-live movement.
3. P20 — Owner Visual Confirmation + Alpha-Live Promotion Gate. Implement the final one-command visual-confirmation receipt and fail-closed promotion plan/apply gate, but do not execute any real promotion in this stage.

## Concurrency boundaries

P18 owns maintained HUD draw acknowledgement code/evidence. P19 and P20 must not modify P18-owned HUD/draw files while P18 is ACTIVE.

P19 owns final package candidate assembly/attestation. Prefer new final-candidate tooling under `parallel/OWNER_ONECLICK/` and candidate/attestation files. Do not modify canonical runtime semantics unless a concrete packaging defect makes it unavoidable.

P20 owns final visual-confirmation/release gating under a separate Owner release area. It may read P17/P19/P16/P18 evidence and W1 alpha-live update contracts, but must not modify P18 HUD code or move `alpha-live` during implementation.

## Product invariants

- No screenshot/template/world-projection coordinate fallback.
- No guessed renderer/object address.
- `readOnly=true`, `ramWrites=0`, `inputInjection=false`.
- No real-WOF PASS from fixtures, draw acknowledgement, module load, or package generation.
- W3 INCONCLUSIVE remains fail-closed.
- `alpha-live` remains unchanged until a later real acceptance reaches the explicit human visual confirmation gate.
- Existing permanent Owner channel remains `Desktop\WOF_ALPHA_TEST.cmd` backed by controlled `alpha-live`.
- No Collector / Unified Collector / Training Farm / 10训 work.

## Implementation cadence

Implementation first. Each worker should complete its whole bounded module before terminal state. Run only narrow parse/compile/controlled fixtures and package-integrity checks needed for the module. Do not create broad QA or historical regression work.

## Final intended flow after these modules

`final pinned candidate -> WOF_ALPHA_FINAL_ACCEPTANCE.cmd -> bounded W3 normal-play qualification -> P16/P18 evidence -> P17 acceptance bundle -> one Owner visual yes/no confirmation -> fail-closed alpha-live promotion plan/apply gate`.

A successful repository implementation still does not equal real-WOF visible PASS.
