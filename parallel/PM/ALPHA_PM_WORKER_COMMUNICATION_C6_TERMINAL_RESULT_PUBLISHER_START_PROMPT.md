stageId: `ALPHA_PM_WORKER_COMMUNICATION_C6_TERMINAL_RESULT_PUBLISHER`
dedupProtocol: `v2`
dedupKey: `alpha.pm.worker-communication.terminal-result-publisher-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C6_TERMINAL_RESULT_PUBLISHER_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C6_TERMINAL_RESULT_PUBLISHER_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C6_TERMINAL_RESULT_PUBLISHER`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_PM_WORKER_COMMUNICATION_C6_TERMINAL_RESULT_PUBLISHER_V1.json`

# Alpha PM Worker Communication C6 — Terminal Result Publisher

Repository: `ouyong520/wof-ai-private`

Read first:
- latest `main`;
- `parallel/PM/ALPHA_PM_DISPATCH_CONTRACT_V1.md`;
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`;
- `parallel/PM/ALPHA_PM_RESULT_INBOX_PROTOCOL_V1.md`;
- `parallel/PM/TESTING_CADENCE_POLICY.md`;
- this prompt's immutable dispatch manifest.

Scope: PM/Worker coordination implementation only. Do not modify Alpha runtime/HUD/renderer/updater/product logic. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## Mandatory ownership

Use dedup-v2 exactly as declared above: latest-main preflight -> create-only canonical claim -> re-read exact claimToken -> create-only stage claim -> re-read exact claimToken. Any create/verification failure is fail-closed. Do not invent recovery.

## Goal

Finish the worker side of the Git communication loop. A worker that has completed implementation should not manually assemble two terminal artifacts field-by-field. Provide one deterministic helper that consumes the immutable dispatch manifest plus a compact worker finish payload, resolves immutable metadata/claim identity from Git state, validates the final envelope with the existing C1 validator, and create-only writes the exact RESULT.json and RESULT.md paths declared by the manifest.

The desired terminal flow is:

`finish implementation -> minimal self-check -> close/retain own claims according to terminal state -> run one result publisher -> commit exact RESULT pair with WORKER_RESULT prefix -> PM reads RESULT.json`

Do not make the publisher perform GitHub pushes or steal/close ownership. Claim mutation stays with the worker under existing dedup authority.

## Preferred implementation

Create new coordination-only files, preferably:

- `parallel/PM/tools/alpha_worker_finish.py`
- `parallel/PM/templates/alpha_worker_finish_input_v1.json`
- `parallel/PM/ALPHA_WORKER_FINISH_PROTOCOL_V1.md`

Avoid modifying C1/C2/C3/C4/C5 implementation files while C4/C5 are ACTIVE. Reuse/import the existing C1 result validator instead of duplicating its schema rules.

## Required behavior

A command similar to:

`python parallel/PM/tools/alpha_worker_finish.py publish --manifest <manifest.json> --slot <N> --input <finish.json> --repo-root .`

must:

1. load and validate the immutable dispatch manifest and requested slot;
2. resolve exact `stageId`, `dedupKey`, `resultProtocol`, `resultJsonPath`, `resultMdPath`, and `terminalCommitPrefix` from the manifest, never from user-provided redirection;
3. read the canonical claim and stage claim for that worker, require exact same claimToken, and hydrate `claimToken` + `startCommit` from canonical authority;
4. enforce terminal ownership state:
   - COMPLETE: canonical/stage are terminal COMPLETE for the same token;
   - BLOCKED: canonical/stage are terminal BLOCKED for the same token;
   - SUBCOMPLETE: exact same token must still be valid; ACTIVE or terminal COMPLETE may be accepted only when consistent with the declared remaining dependency;
5. accept only the worker-variable result fields needed by `wof-alpha-worker-result-v1` (verdict, implementation commits, integration readiness, changed files, tests, proof, owner gate, blocker, next action, evidence paths, safety);
6. construct the full canonical RESULT JSON using immutable manifest/claim metadata;
7. validate the constructed JSON through the existing C1 validator before any terminal file is written;
8. render a concise human-readable RESULT.md from the same canonical in-memory result object so JSON and Markdown cannot drift;
9. write the exact RESULT.json and RESULT.md using create-only semantics; refuse overwrite of either path and avoid leaving a half-written pair on failure;
10. print a compact machine-readable success summary containing exact result paths and exact terminal commit subject `WORKER_RESULT <stageId> <STATE>`;
11. fail closed on malformed manifest, wrong slot, claim-token mismatch, wrong claim state, unsupported state, invalid result payload, redirected paths, or pre-existing result files.

No shared mutable dashboard/index is allowed.

## Dogfood requirement

After implementation and claim closeout, use the new publisher itself to create this C6 stage's own exact RESULT.json and RESULT.md if doing so is compatible with the completed tool. This is the primary end-to-end proof of the mechanism.

## Testing cadence

Implementation first. Do not build a large QA suite. Run only the minimum self-check needed to avoid shipping an obviously broken publisher, such as:

- Python parse/compile check;
- one valid temporary publish path;
- one fail-closed malformed/mismatch case;
- one create-only overwrite refusal case;
- dogfood publication of C6's own terminal result.

Do not open Fresh QA, second-opinion, or broad regression work for C6.

## Terminal reporting

Terminal output must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md` using the exact paths declared above. Final terminal result commit subject must begin:

`WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C6_TERMINAL_RESULT_PUBLISHER <STATE>`

Return only COMPLETE / SUBCOMPLETE / precise BLOCKED in chat.