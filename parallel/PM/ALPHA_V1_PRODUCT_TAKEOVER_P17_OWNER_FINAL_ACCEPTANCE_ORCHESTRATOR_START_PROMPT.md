stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P17_OWNER_FINAL_ACCEPTANCE_ORCHESTRATOR`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.owner-final-acceptance-orchestrator-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P17_OWNER_FINAL_ACCEPTANCE_ORCHESTRATOR_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P17_OWNER_FINAL_ACCEPTANCE_ORCHESTRATOR_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P17_OWNER_FINAL_ACCEPTANCE_ORCHESTRATOR`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_FINALIZATION_P15_P17_P18_LONG_3_WORKER_V1.json`

# Alpha V1 P17 — Owner Final Acceptance Orchestrator

Repository: `ouyong520/wof-ai-private`

This is a larger finalization task. Do not split into micro-stages unless there is a genuine external blocker.

Read latest `main` first, then at minimum:
- `AGENTS.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/ALPHA_V1_CANONICAL_FINALIZATION_P15_P17_P18_LONG_3_WORKER_DISPATCH.md`
- `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE_RESULT.json`
- current P15 candidate/result if available; if P15 result is not terminal yet, consume only stable checked-in candidate metadata and do not block implementation on P15 terminal wording.
- `parallel/RENDER_AUTHORITY_V2/run_long_qualification.py`
- `parallel/PYLAUNCH/wof_launcher/canonical_acceptance_evidence.py`
- existing permanent Owner test-channel/bootstrap entrypoints only as reference; do not modify their selection/promotion semantics.

## Ownership

Perform normal dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on ownership failure. Do not invent recovery.

## Goal

Build the final Owner-facing acceptance orchestration module so the eventual real gate is one simple bounded action instead of several commands, manual file hunting, DevTools, calibration, or interpretation of implementation internals.

The orchestrator is **not** the runtime position authority and must not alter production coordinates. It only coordinates existing proof/evidence producers and creates one deterministic final acceptance bundle.

Preferred implementation area:
- new directory `parallel/OWNER_ACCEPTANCE/`
- main entrypoint such as `final_acceptance_orchestrator.py`
- optional Windows wrapper such as `WOF_ALPHA_FINAL_ACCEPTANCE.cmd`
- focused local tests and a concise protocol/readme in the same directory.

## Required workflow

Implement a deterministic state machine that can later perform, in order:

1. Preflight exact environment and candidate metadata.
   - Locate the current selected/candidate metadata without weakening package integrity.
   - Record source commit/package version/candidate identity if available.
   - Do not move alpha-live.

2. W3 renderer-source qualification step.
   - Reuse the existing checked-in `parallel/RENDER_AUTHORITY_V2/run_long_qualification.py` entrypoint.
   - Do not modify W3 producer/analyzer/claim.
   - Support a mode that invokes the bounded qualification command as a subprocess and waits for its deterministic output.
   - Support an offline mode that consumes an already-produced qualification JSON for focused tests.
   - PASS only if W3's own qualification result explicitly says the renderer/object causal proof passed. INCONCLUSIVE/BLOCKED remains fail-closed.

3. P16 canonical runtime acceptance evidence step.
   - Consume the automatic `~/Documents/WOF_RESULTS/ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.json` snapshot.
   - Validate exact World/page/worker/runtime/renderer/authority identities if present.
   - Treat `HUD_INGEST_ACCEPTED` as runtime evidence only, never visual proof.
   - Missing/stale/mixed-authority evidence must fail closed.

4. P18 draw-evidence step.
   - Consume optional default `~/Documents/WOF_RESULTS/ALPHA_CANONICAL_DRAW_EVIDENCE.json` when available.
   - P17 must not depend on P18 implementation existing at coding time; define a stable reader for the interface declared in the shared dispatch.
   - Missing draw evidence => `WAITING_DRAW_EVIDENCE`, not failure of W3/P16 and never PASS.
   - Draw acknowledgement still means maintained primitive execution, not Owner-visible proof.

5. Final decision state.
   Provide an explicit deterministic state vocabulary, for example:
   - `WAITING_W3_QUALIFICATION`
   - `W3_INCONCLUSIVE`
   - `WAITING_CANONICAL_RUNTIME_EVIDENCE`
   - `CANONICAL_RUNTIME_SUPPRESSED`
   - `WAITING_DRAW_EVIDENCE`
   - `READY_FOR_OWNER_VISUAL_CONFIRMATION`
   - `OWNER_VISUAL_CONFIRMATION_REQUIRED`
   - `FAILED_EVIDENCE_MISMATCH`

   Do not emit final `PASS` automatically from repository/runtime evidence. The highest automatic state before the human screen check is `READY_FOR_OWNER_VISUAL_CONFIRMATION`.

6. Evidence bundle.
   Write a deterministic bundle under the Owner results directory, preferably:
   - `ALPHA_FINAL_ACCEPTANCE_BUNDLE.json`
   - `ALPHA_FINAL_ACCEPTANCE_BUNDLE.md`
   - optional ZIP containing only generated evidence/metadata, not source secrets.

   Bundle must contain:
   - exact timestamps and source paths;
   - candidate/package identity;
   - W3 qualification summary;
   - P16 canonical status summary;
   - P18 draw evidence summary if present;
   - authority/runtime/renderer identity consistency result;
   - safety fields;
   - final automatic decision;
   - `visibleProof: "NOT_PROVEN"` until explicit Owner confirmation is supplied externally.

7. One-command Owner path.
   - Provide one Windows-friendly entrypoint that later starts the bounded acceptance workflow.
   - Owner should not need DevTools, JSON editing, file-path knowledge, calibration clicks, coordinate choices, or package hunting.
   - The command should explain only simple Chinese instructions: start/keep WOF normal play, wait, then visually answer whether the overlay follows correctly.

## Evidence consistency rules

Fail closed if any available evidence disagrees on:
- World SHA;
- authority key;
- runtime epoch;
- renderer epoch;
- page target identity where applicable;
- candidate/source commit identity where applicable.

Do not silently choose the newest file when multiple incompatible evidence files exist. Require an explicit current/latest pointer or deterministic discovery rule and record which file was selected.

## Safety

Must preserve:
- read-only operation;
- zero RAM writes;
- no input injection;
- no screenshot/template/world-projection as production position authority;
- screenshots, if present in W3 bundles, are verification-only;
- no guessed renderer/object address;
- no alpha-live movement.

## Write boundaries

Expected writes:
- new files under `parallel/OWNER_ACCEPTANCE/`
- P17 result files.

Do not modify:
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`
- P15 coordinator/package files
- `product/alpha/wof_alpha_field_adapter.js`
- `product/alpha/wof_alpha_hud.js`
- P16 `state.py`/`tray.py`/evidence implementation
- W3 capture/analyzer files or W3 claims
- package manifests/pins
- alpha-live selection.

## Focused self-check only

Implementation first. Then run only narrow checks:
- Python parse/compile;
- synthetic W3 PASS + P16 READY + P18 draw evidence -> `READY_FOR_OWNER_VISUAL_CONFIRMATION`;
- W3 INCONCLUSIVE -> no advance;
- mixed renderer/runtime identity -> `FAILED_EVIDENCE_MISMATCH`;
- missing P18 evidence -> `WAITING_DRAW_EVIDENCE`;
- bundle write/read determinism;
- Windows wrapper resolves the intended orchestrator without requiring DevTools/manual JSON.

No real WOF run. No broad QA. No alpha-live promotion.

## Terminal

Write exact RESULT.json + RESULT.md declared above. Record implementation commits, changed files, focused checks, productProof boundary, safety, blocker, integrationReady, and nextAction.

A successful result means the final acceptance workflow is repository-ready, not that real-WOF visibility has passed.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P17_OWNER_FINAL_ACCEPTANCE_ORCHESTRATOR <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.
