stageId: `ALPHA_PM_WORKER_COMMUNICATION_C8_RESULT_EVIDENCE_VERIFIER`
dedupProtocol: `v2`
dedupKey: `alpha.pm.worker-communication.result-evidence-verifier-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C8_RESULT_EVIDENCE_VERIFIER_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C8_RESULT_EVIDENCE_VERIFIER_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C8_RESULT_EVIDENCE_VERIFIER`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_PM_WORKER_COMMUNICATION_C7_C8_2_WORKER_V1.json`

# Alpha PM Worker Communication C8 — Result Evidence Verifier

Repository: `ouyong520/wof-ai-private`

Read first:
- latest `main`;
- `parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C7_C8_2_WORKER_DISPATCH.md`;
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`;
- `parallel/PM/ALPHA_PM_RESULT_INBOX_PROTOCOL_V1.md`;
- `parallel/PM/TESTING_CADENCE_POLICY.md`;
- this dispatch manifest.

Scope is PM/Worker coordination implementation only. Do not modify Alpha runtime/HUD/renderer/updater/product logic. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## Ownership

Perform dedup-v2 exactly as declared: latest-main preflight -> create-only canonical claim -> re-read exact claimToken -> create-only stage claim -> re-read exact same claimToken. Any create/verification failure is fail-closed. Do not invent recovery.

## Goal

Make terminal worker feedback quickly trustworthy without turning every stage into QA. Given a valid `wof-alpha-worker-result-v1` RESULT.json and a local Git checkout, structurally verify that the worker's declared implementation commits and changed files correspond to real Git evidence.

Preferred new files:
- `parallel/PM/tools/alpha_pm_result_evidence.py`
- `parallel/PM/ALPHA_PM_RESULT_EVIDENCE_PROTOCOL_V1.md`
- optional narrow template/output example.

Do not rewrite C1-C7 implementation files. Reuse C1 result validation before evidence verification.

## Required behavior

A command similar to:

`python parallel/PM/tools/alpha_pm_result_evidence.py verify --result parallel/PM/RESULTS/<STAGE>_RESULT.json --repo-root .`

must:
1. validate the RESULT envelope with existing C1 behavior before trusting fields;
2. require every `implementationCommits` SHA to exist in the local Git repository;
3. inspect the union of files materially changed by those implementation commits;
4. verify every declared `changedFiles` path is actually touched by at least one declared implementation commit;
5. report implementation files touched by declared commits but omitted from `changedFiles` when material;
6. distinguish implementation commits from obvious claim-only/result-only/prompt-only commits using commit subject and changed path evidence; do not accept a terminal result whose implementation evidence is only claim/result paperwork when integrationReady=true;
7. optionally verify implementation commits descend from or are reachable after `startCommit` where Git history permits, and fail closed on impossible ancestry claims;
8. emit one compact machine-readable verdict with at least `acceptableForIntegration`, exact discrepancies, verified implementation commits, verified changed files, and whether deeper PM inspection is required;
9. never infer product-visible PASS from structural Git evidence; preserve `productProof`/Owner-gate separation from C1;
10. work read-only and never mutate Git, claims, RESULT files, manifests, or current pointer.

The verifier is not a unit/regression/product QA runner. It verifies evidence consistency only.

## Implementation-first cadence

Implement the complete verifier first. Minimum self-checks only: one valid real RESULT from C1/C2/C3/C4/C5, one missing/fake commit failure, one changedFiles mismatch, and one paperwork-only false-green rejection. No broad QA, Fresh QA, or second opinion.

## Terminal reporting

Write the exact manifest-declared RESULT.json and RESULT.md. Result must state what evidence can now be verified, implementation commit(s), changed files, minimum self-checks, integrationReady, blocker if any, and exact PM next action. Final result commit subject begins:

`WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C8_RESULT_EVIDENCE_VERIFIER <STATE>`

Return only COMPLETE / SUBCOMPLETE / precise BLOCKED in chat.
