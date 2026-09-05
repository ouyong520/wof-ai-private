stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P19_FINAL_CANONICAL_CANDIDATE_REBUILD_ATTESTATION`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.final-canonical-candidate-rebuild-attestation-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P19_FINAL_CANONICAL_CANDIDATE_REBUILD_ATTESTATION_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P19_FINAL_CANONICAL_CANDIDATE_REBUILD_ATTESTATION_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P19_FINAL_CANONICAL_CANDIDATE_REBUILD_ATTESTATION`

# Alpha V1 Product Takeover P19 — Final Canonical Candidate Rebuild + Attestation

Repository: `ouyong520/wof-ai-private`

This is intentionally a long finalization module. Do not split into micro-stages unless a genuine external dependency prevents one coherent implementation.

Read latest `main`, `AGENTS.md`, testing cadence, dedup guard, the current dispatch, and at minimum:
- P15 RESULT.json
- P16 RESULT.json
- P17 RESULT.json
- P18 RESULT.json if/when present
- W3 long qualification RESULT.json
- `parallel/OWNER_ONECLICK/refresh_manifest.py`
- P15 canonical package candidate JSON
- package manifest/test tooling actually used by Owner one-click
- final acceptance/evidence files referenced by P16/P17/P18.

## Ownership

Normal dedup-v2 create-only canonical claim -> exact token re-read -> create-only stage claim -> exact token re-read. Fail closed on ownership failure. Do not invent recovery.

## Goal

Replace the earlier P15-only immutable candidate with one **final canonical release candidate** whose single source commit includes the completed late-stage product/evidence code and whose manifest/attestation proves exactly what will be selected later.

P19 is packaging/attestation work. It must not fabricate W3 live proof, must not claim visual PASS, and must not move `alpha-live`.

## Workstream A — deterministic final-candidate builder

Implement a reusable final candidate builder, preferably as a new narrow module under `parallel/OWNER_ONECLICK/`, reusing existing `refresh_manifest.py` validation/generation instead of duplicating package selection logic.

The builder must:
1. Resolve one exact source commit.
2. Require P15, P16, and P17 terminal COMPLETE/integration-ready evidence.
3. Require P18 terminal COMPLETE/integration-ready before emitting the actual final candidate; if P18 is still ACTIVE/missing, the builder must return a deterministic `WAITING_FOR_P18`/not-emitted state rather than pinning an incomplete source.
4. Require the source commit to contain all required result/evidence implementation commits as ancestors.
5. Pin the full canonical runtime stack from P15 plus P16 Owner status/evidence, P17 acceptance orchestrator, and P18 draw acknowledgement/evidence collector code.
6. Preserve the no-legacy-spatial-fallback safety invariants.
7. Preserve P15 package integrity and exact blob verification.
8. Never silently read arbitrary runtime files from moving `main` after candidate creation.

## Workstream B — final candidate attestation

Produce a deterministic attestation alongside the candidate. It must include at least:
- schema/version;
- source commit;
- package version;
- candidate manifest path + SHA-256;
- selected file count;
- exact required stage/result states for P15/P16/P17/P18;
- implementation commit ancestry evidence;
- critical runtime blob SHAs;
- safety flags;
- `w3LiveQualification=NOT_RUN/INCONCLUSIVE/PASS` as evidence actually permits;
- `ownerVisualAcceptance=NOT_RUN` at repository-build time;
- `alphaLivePromoted=false`;
- previous/current observed alpha-live commit if safely discoverable from repository refs, without mutating it.

Attestation must be deterministic for a fixed source commit and fixed inputs.

## Workstream C — final candidate integrity / stale-input rejection

Fail closed on:
- missing/ACTIVE/non-integration-ready P18;
- result stage/dedup mismatch;
- candidate source commit that predates required implementation commits;
- required canonical file missing;
- blob mismatch;
- legacy spatial fallback enabled;
- real-WOF/visible PASS claims unsupported by live evidence;
- alpha-live movement during this stage.

Do not treat the P15 candidate as the final candidate merely because it passed its own tests; P16/P17/P18 were added later.

## Workstream D — operator-facing one-command build/verify

Provide one Windows-friendly and/or Python command that PM can run after P18 finishes to rebuild + verify the final candidate without hand-editing JSON. It should leave a stable `LATEST_FINAL_CANONICAL_CANDIDATE` pointer or equivalent deterministic path suitable for P20/P17 consumption.

## Write boundaries

Expected:
- new final-candidate builder/verifier under `parallel/OWNER_ONECLICK/`;
- final candidate/attestation files under `parallel/OWNER_ONECLICK/CANDIDATES/` or a dedicated final-candidate directory;
- narrow focused tests.

May modify `refresh_manifest.py` only if a narrow reusable API/selection omission is genuinely required. Do not modify P18-maintained HUD/draw files while P18 is ACTIVE. Do not modify W3 producer. Do not move `alpha-live`.

## Focused checks

Only narrow checks:
- Python parse/compile;
- deterministic builder fixture;
- missing-P18 fail-closed fixture;
- required-commit ancestry + blob-integrity fixture;
- regeneration equality for fixed source;
- final candidate verification against actual main if P18 has completed by then.

No broad QA, no real WOF, no alpha-live promotion.

## Terminal result

Write exactly the specified RESULT.json/RESULT.md. Record implementation commits, changed files, candidate path/version/source commit if emitted, attestation path/hash, focused checks, integrationReady, P18/W3/Owner boundaries, and safety.

A correct COMPLETE may mean the builder/attestation module is fully implemented while actual final candidate emission remains truthfully WAITING_FOR_P18 if P18 is still ACTIVE. If P18 is already COMPLETE by the emission step, emit and verify the actual final candidate in the same task.
