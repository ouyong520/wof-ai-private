# Alpha PM Result Evidence Protocol V1

Scope: PM/Worker coordination evidence only. This protocol does not prove Alpha runtime, renderer, HUD, updater, or Owner-visible behavior.

## Purpose

`parallel/PM/tools/alpha_pm_result_evidence.py` is the read-only PM intake check that follows the C1 RESULT envelope validator. It answers one narrow question: do the `implementationCommits` and `changedFiles` declared by a structurally valid `wof-alpha-worker-result-v1` RESULT.json correspond to real local Git evidence?

It is not unit QA, regression QA, product QA, Fresh QA, or Owner acceptance.

## Command

```text
python parallel/PM/tools/alpha_pm_result_evidence.py verify \
  --result parallel/PM/RESULTS/<STAGE>_RESULT.json \
  --repo-root .
```

Add `--pretty` for indented JSON. Without it, the tool emits one compact machine-readable JSON line.

The checkout must contain the Git history needed to resolve the declared commits and ancestry. The verifier never fetches, checks out, commits, edits, or otherwise mutates Git.

## Verification order

1. Load RESULT.json and run the existing C1 `alpha_worker_result.validate_result` behavior first.
2. Require `startCommit` and every declared implementation SHA to resolve as local Git commits.
3. Read each implementation commit subject and changed paths.
4. Form the union of paths touched by declared implementation commits.
5. Require every declared `changedFiles` entry to occur in that union.
6. Report non-paperwork/material paths touched by declared implementation commits but omitted from `changedFiles`.
7. Classify obvious claim-only, result-only, dispatch/prompt-only commits as paperwork rather than implementation evidence.
8. When `integrationReady=true`, reject evidence that has no implementation-bearing commit.
9. Verify each implementation commit descends from `startCommit` when Git can answer ancestry; impossible or unavailable ancestry is fail-closed.
10. Preserve `productProof` as reported by C1 and set `productProofInference` to `NONE`. Structural Git consistency never upgrades product proof.

## Paperwork classification

The verifier treats these as coordination paperwork rather than implementation-bearing paths:

- `parallel/PM/DEDUP_CLAIMS/**`
- `parallel/PM/STAGE_CLAIMS/**`
- `parallel/PM/RESULTS/**`
- `parallel/PM/CURRENT_DISPATCH.json`
- `parallel/PM/**/*_START_PROMPT.md`
- `parallel/PM/DISPATCH_MANIFESTS/**`

A protocol/design document or PM tool outside those bookkeeping locations may still be legitimate implementation for a coordination-only stage. The classifier intentionally does not reject all Markdown or all `parallel/PM/**` files.

## Verdict contract

The emitted object uses schema `wof-alpha-result-evidence-verdict-v1` and includes at least:

- `acceptableForIntegration`: true only when the RESULT envelope is valid, RESULT itself says `integrationReady=true`, all declared implementation commits exist, ancestry is consistent, declared changed files are backed by those commits, no material files are omitted, and no declared implementation commit is obvious paperwork-only evidence;
- `discrepancies`: exact machine-readable discrepancy objects;
- `verifiedImplementationCommits`: resolved SHA, subject, classification, changed files, and start-commit ancestry result;
- `verifiedChangedFiles`: declared paths confirmed in the declared implementation commit union;
- `materialFilesTouched` and `omittedMaterialFiles`;
- `paperworkOnlyCommits`;
- `deeperPmInspectionRequired`;
- `productProof` copied from RESULT.json and `productProofInference: NONE`.

Common discrepancy codes include:

- `INVALID_RESULT_ENVELOPE`
- `START_COMMIT_MISSING`
- `IMPLEMENTATION_COMMIT_MISSING`
- `DECLARED_IMPLEMENTATION_COMMIT_IS_PAPERWORK_ONLY`
- `IMPLEMENTATION_COMMIT_HAS_NO_MATERIAL_FILES`
- `IMPOSSIBLE_START_ANCESTRY`
- `ANCESTRY_UNVERIFIABLE`
- `DECLARED_CHANGED_FILES_NOT_TOUCHED`
- `MATERIAL_FILES_OMITTED_FROM_RESULT`
- `NO_IMPLEMENTATION_COMMITS`
- `PAPERWORK_ONLY_FALSE_GREEN`
- `RESULT_NOT_INTEGRATION_READY`
- `VERIFIER_ERROR`

## Exit codes

- `0`: `acceptableForIntegration=true`.
- `1`: verification completed but evidence is not acceptable for integration.
- `2`: verifier could not perform the check, for example invalid repo/root access or malformed unreadable input.

## PM intake rule

A zero exit code means only that the worker's terminal RESULT claims are structurally consistent with the local Git evidence. PM may then inspect the verified implementation commits as needed for integration. It does not mean tests were independently rerun, runtime behavior is correct, machine draw occurred, or the Owner saw the claimed product behavior.
