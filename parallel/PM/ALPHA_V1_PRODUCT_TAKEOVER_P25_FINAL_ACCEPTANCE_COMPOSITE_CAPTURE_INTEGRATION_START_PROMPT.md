stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.final-acceptance-composite-capture-integration-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION`

# Alpha V1 Product Takeover P25 — Final Acceptance Composite Capture Integration

Repository: `ouyong520/wof-ai-private`

This is intentionally a long final-integration task. Do not split into micro-patches. Implement the complete bounded module, then terminalize once.

Read latest `main`, root `AGENTS.md`, PM playbook/testing cadence/dedup guard/current dispatch, then at minimum read the COMPLETE results and implementation interfaces for P17, P18, P19, P20, P21, P22, P24, P16, and the existing W3 bounded qualification result/runner.

## Why P25 exists

P21 can stage the exact P19 candidate and invoke P17. P22 and P24 are now complete passive acceptance analyzers, but their live inputs are not yet automatically captured as part of the same staged acceptance run. Leaving them as manual post-processing would permit operator mistakes and would fail to prove that dynamic-state and temporal evidence came from the exact staged candidate session.

P25 must close that integration seam:

`exact P19 candidate -> P21 staged runtime -> passive canonical observation capture -> P22 dynamic coverage + P24 temporal continuity -> P16/P18/W3 -> P17 final bundle`

All of those artifacts must come from one bounded run identity. This stage implements the capture/integration path only; it does not run real WOF and does not claim W3 PASS or visible PASS.

## Ownership

Acquire normal dedup-v2 canonical and stage claims with exact-token readback. Fail closed on ownership ambiguity. Do not recover or steal old claims.

P17/P18/P19/P20/P21/P22/P24/W3 are existing authorities. Prefer a new isolated implementation area under `parallel/OWNER_ACCEPTANCE_COMPOSITE/`. Do not rewrite their implementations unless a concrete, narrowly evidenced integration defect makes a tiny compatibility patch unavoidable; if so, record the exact reason and keep ownership-safe boundaries.

## Goal

Implement one deterministic composite capture supervisor that can later run alongside P21's exact-candidate staging and automatically feed P22/P24 from existing canonical/runtime/HUD evidence, then bind the resulting artifacts back into the P17 acceptance session.

The Owner later should still only need the normal bounded staging command/play interval; no hand-authored JSON, coordinates, actor labels, generation numbers, runtime epochs, or DevTools work.

## Workstream A — one-run composite session identity

Create a bounded composite run record before capture starts. It must bind at least:
- exact P19 source commit;
- package version;
- candidate SHA256 + attestation SHA256;
- P21 staging run/receipt identity when available;
- expected exact World identity;
- later observed pageTargetId/authorityKey/runtimeEpoch/rendererEpoch;
- start/end timestamps and a random/non-guessable run nonce or equivalent unique run id.

The run record is not a source of gameplay truth. It only prevents cross-run evidence mixing.

If candidate identity or P21 receipt changes mid-run, stop and mark the run rejected; never merge evidence across candidates.

## Workstream B — passive canonical cycle capture

Implement a read-only sampler that consumes only maintained/existing canonical status/evidence surfaces. It may use existing CDP/page read APIs or P21/P16/P18 output seams, but must not introduce new RAM addresses, renderer guesses, screenshot coordinates, world projection, nearest-object identity, row-order identity, input injection, or cached spatial fallback.

Each accepted sample must preserve exact authority fields and enough existing data to construct:
1. a valid `wof-alpha-p22-cycle-bundle-v1` for P22;
2. one or more valid `wof-alpha-canonical-temporal-observation-v1` rows for P24.

Rules:
- coordinates, if present, must originate only from P10 canonical READY anchors;
- SUPPRESSED rows must not carry coordinates;
- actor/generation comes only from the canonical actor/generation authority;
- stale runtime/renderer/page identity is rejected;
- duplicate/out-of-order samples are retained/rejected exactly according to P24/P22 contracts, not silently repaired;
- P18 draw acknowledgements are causal evidence only, never visible PASS;
- rare HIT/DOWN/RECOVERY/JUMP/DEATH states remain UNPROVEN/NOT_OBSERVED unless an existing maintained exact semantic producer already proves them.

Bound memory/disk usage and make capture cancellation/timeout deterministic.

## Workstream C — direct P22 + P24 integration

Use the real public/internal callable contracts from the completed P22/P24 modules rather than copying their logic.

During or immediately after the same bounded run:
- feed every accepted cycle to `DynamicActorStateCoverageRecorder.record_cycle(...)` or the maintained equivalent;
- feed time-ordered observations to the P24 analyzer;
- write their normal deterministic JSON/MD evidence outputs into the same run evidence root;
- record hashes of those outputs in the composite run record.

P22/P24 analyzer failures must fail closed for the composite session. Do not replace missing evidence with synthetic PASS.

## Workstream D — P21/P17 bridge

Provide one Windows-friendly wrapper or Python supervisor under the P25-owned area that can later:
1. resolve the exact P19 candidate through existing P21 logic;
2. stage/start the exact candidate using P21 rather than duplicating staging code;
3. start passive composite capture;
4. allow the existing bounded W3 qualification/P16/P18/P17 flow to execute;
5. stop capture deterministically;
6. run/finalize P22 and P24 for that same run;
7. emit a composite evidence index containing hashes/paths/states for P21, W3, P16, P18, P22, P24 and P17;
8. stop at `READY_FOR_OWNER_VISUAL_CONFIRMATION` at most;
9. leave P20 as the only Owner YES/NO visual/promotion gate;
10. never move `alpha-live`.

Do not create a new permanent Desktop launcher. This is a final acceptance integration command, not a new install/update channel.

## Workstream E — lifecycle and failure handling

Handle success, timeout, cancellation, browser/page replacement, runtime/renderer epoch replacement, staged runtime failure, and evidence writer failure.

Required:
- no orphan P25-owned capture process;
- do not kill unrelated Browser/WOF;
- preserve P21 cleanup/restore semantics;
- archive partial evidence truthfully;
- exact rejected reason in final run index;
- no attempt to repair continuity with old coordinates/interpolation;
- no cross-epoch evidence merge.

## Expected write boundary

Prefer only new files under:
`parallel/OWNER_ACCEPTANCE_COMPOSITE/`

Narrow focused tests/docs/wrapper in the same area are expected.

Do not modify:
- W3 producer/qualification ownership;
- P18 HUD/draw implementation;
- P15 runtime semantics;
- P19 candidate/attestation;
- P20 release gate;
- permanent W1 updater/setup;
- `alpha-live`.

## Focused checks only

Implementation first. Run only minimum focused checks:
- Python/CMD syntax/compile;
- exact candidate/P21 binding fixture;
- accepted canonical sample -> valid P22 + P24 input fixture;
- SUPPRESSED/no-coordinate fixture;
- stale runtime/renderer/page rejection;
- duplicate/out-of-order preservation/rejection;
- bounded capture/timeout/cancel cleanup;
- same-run P22/P24 output hash binding;
- P17/composite candidate mismatch rejection;
- source scan proving no alpha-live mutation, input injection, screenshot/world-projection spatial fallback.

No broad QA, no real WOF, no Owner visual question, no promotion.

## Terminal result

Write the specified RESULT.json/RESULT.md with implementation commits, exact changed files, focused checks, integrationReady, composite evidence contract, later Owner action, boundaries and safety.

Successful COMPLETE proves the composite acceptance capture integration only. It must state:
- `realWofAcceptance=NOT_RUN`;
- `ownerVisualAcceptance=NOT_RUN`;
- `alphaLiveMoved=false`;
- `visibleProof=NOT_PROVEN`.
