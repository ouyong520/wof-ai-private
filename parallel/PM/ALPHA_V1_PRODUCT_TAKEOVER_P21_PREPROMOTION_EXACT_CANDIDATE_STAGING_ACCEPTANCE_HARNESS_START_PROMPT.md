stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.prepromotion-exact-candidate-staging-acceptance-harness-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS`

# Alpha V1 Product Takeover P21 — Pre-Promotion Exact Candidate Staging + Acceptance Harness

Repository: `ouyong520/wof-ai-private`

This is a long product/release-integration task. Do not split it into micro-stages unless a genuine external blocker prevents one coherent implementation.

Read latest `main`, `AGENTS.md`, testing cadence, dedup guard, current dispatch, and at minimum:
- P15 COMPLETE result and canonical runtime candidate evidence;
- P16 COMPLETE Owner canonical status/evidence result;
- P17 COMPLETE final acceptance orchestrator/result;
- P18 COMPLETE canonical draw acknowledgement/result;
- P19 prompt/result/latest final candidate pointer if available;
- P20 promotion-gate prompt/result if available;
- W3 long qualification result/runner;
- W1 permanent Owner live-test bootstrap result;
- `WOF_ALPHA_SETUP_ONCE.cmd`;
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`;
- `parallel/OWNER_ACCEPTANCE/WOF_ALPHA_FINAL_ACCEPTANCE.cmd` and its orchestrator;
- package candidate/attestation tooling under `parallel/OWNER_ONECLICK/`.

## Why P21 exists

Final visual acceptance must happen **before** the permanent `alpha-live` release pointer is promoted, but the permanent W1 Owner channel normally runs only `alpha-live`.

P21 must remove that circular dependency without weakening release safety:

`P19 exact final candidate` -> `ephemeral local staging runtime` -> `P17/W3/P16/P18 acceptance evidence` -> `Owner visual yes/no later through P20` -> only then `alpha-live` promotion.

Do not solve this by moving `alpha-live`, force-pushing, inventing coordinates, or silently running moving `main`.

## Ownership

Perform normal dedup-v2 create-only canonical claim, exact claimToken re-read, create-only stage claim, exact-token re-read. Fail closed on any ownership failure. Do not invent recovery.

Do not modify P19/P20/W3 claims or RESULT files except reading them.

## Product goal

Implement one deterministic PM/Owner staging harness that can run the exact P19 candidate on the Owner machine **without mutating `alpha-live`** and while preserving the existing Browser/WOF session when safe.

The staged runtime must be cryptographically tied to the exact candidate source commit/package attestation and must leave the permanent managed Alpha release unchanged after staging ends.

## Workstream A — exact candidate resolver and gate

Create a new isolated area, preferably `parallel/OWNER_STAGING/`.

Implement a resolver that:
1. Reads P19 latest final candidate pointer/attestation and resolves one exact candidate source commit/package version/hash.
2. Requires P19 candidate/attestation state to be ready and self-consistent. If P19 is still ACTIVE/missing, return deterministic `WAITING_FOR_P19` and do not stage anything.
3. Requires P15/P16/P17/P18 implementation commits/results to be ancestors of the candidate source commit as represented by the P19 attestation.
4. Verifies candidate manifest hash and critical runtime blob SHAs before launch.
5. Rejects any candidate claiming unsupported W3/Owner visual PASS.
6. Records the observed current `alpha-live` commit but never moves it.
7. Refuses moving `main` as runtime authority. Staging authority is only the immutable candidate source commit.

## Workstream B — ephemeral staging worktree/runtime

Implement a Windows-friendly staging runner that uses an isolated local worktree or equivalent immutable checkout under a bounded staging directory such as `%LOCALAPPDATA%\WOF_ALPHA_STAGING\<candidate-id>`.

Requirements:
1. Fetch/resolve the exact candidate commit using the already-configured private Git transport; do not modify the `alpha-live` ref.
2. Create/reuse only a bounded staging checkout tied to that exact commit; verify `HEAD` equals the candidate source commit before launch.
3. Never `reset --hard` the permanent W1 managed repo to the candidate.
4. Never rewrite the permanent Desktop launcher or installer.
5. Stop/restart only Alpha-owned runtime processes when required; preserve current Browser/WOF when safe.
6. Launch the candidate's own package-selected Alpha runtime from the staging checkout with explicit environment identity such as candidate source commit/package version/acceptance mode.
7. Ensure evidence written by P16/P18/P17 can be tied back to that exact staged candidate identity.
8. If staging launch fails, terminate staged Alpha runtime and leave permanent `alpha-live`/managed repo untouched.
9. Provide deterministic cleanup for stale staging worktrees/processes. Cleanup must not delete unrelated repos, SSH keys, browser profiles, WOF data, or permanent managed Alpha files.
10. Safety remains read-only game interaction: `ramWrites=0`, `inputInjection=false`.

Do not introduce screenshot/world-projection fallback or any renderer-source shortcut.

## Workstream C — acceptance orchestration bridge

Provide one later-use command/wrapper that can:
1. resolve and stage the exact P19 final candidate;
2. start the staged Alpha runtime;
3. invoke/reuse P17 final acceptance orchestration for the same candidate;
4. allow the existing bounded W3 qualification flow to run during normal Owner play;
5. collect/retain P16 and P18 evidence for that candidate;
6. stop at P17's `READY_FOR_OWNER_VISUAL_CONFIRMATION` boundary;
7. optionally hand off to P20's visual confirmation wrapper if P20 is available, but do not duplicate P20 receipt/promotion logic;
8. never auto-promote `alpha-live`.

The Owner-facing instruction should remain simple: run one command, play normally for the bounded interval, answer the later single visual question. No DevTools, JSON editing, branch/hash selection, coordinate entry, or package hunting.

## Workstream D — restore/cleanup contract

After success, failure, cancellation, or timeout:
1. staged Alpha runtime is stopped cleanly;
2. staging state records exact candidate and outcome;
3. permanent W1 managed repo HEAD/ref is verified unchanged from pre-stage observation;
4. `alpha-live` remote/local refs are verified unchanged by P21;
5. optionally restart the prior permanent Alpha runtime only if it was running before staging and doing so is safe/deterministic;
6. preserve all acceptance evidence and logs under the existing Owner results area;
7. cleanup of the ephemeral checkout must be bounded and idempotent.

If the previous permanent runtime cannot be safely restored automatically, report a precise restore action; do not guess or mutate refs.

## Workstream E — truthful staging status/evidence

Produce a deterministic staging receipt/status artifact containing at least:
- candidate source commit;
- package version/candidate hash/attestation hash;
- observed alpha-live commit before and after;
- staging checkout path + resolved HEAD;
- runtime start/stop state;
- P17 acceptance bundle path/hash if generated;
- W3/P16/P18 state summaries;
- `ownerVisualAcceptance=NOT_RUN` unless an actual later P20 receipt exists;
- `alphaLiveMoved=false`;
- safety fields.

Never label a staged runtime start or P18 draw acknowledgement as visible PASS.

## File/write boundaries

Expected new files only under `parallel/OWNER_STAGING/` plus narrow focused tests/docs.

You may add a very small reusable helper elsewhere only if unavoidable, but prefer new isolated files.

Do not modify:
- P19 builder/candidate/attestation files while P19 owns them;
- P20 `parallel/OWNER_RELEASE/` files while P20 owns them;
- P18 HUD/draw evidence implementation;
- W3 producer/qualification implementation;
- P15 runtime semantics;
- `WOF_ALPHA_SETUP_ONCE.cmd`;
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`;
- `alpha-live` ref.

If a genuine integration defect in those owned files is discovered, fail closed with exact evidence rather than crossing ownership.

## Focused checks only

Implementation first. Run only narrow checks:
- Python/PowerShell/CMD parse/syntax as needed;
- exact-candidate resolver fixture;
- P19-missing/ACTIVE fail-closed fixture;
- local Git worktree fixture proving candidate HEAD is exact and permanent branch/ref remains unchanged;
- staged runtime command construction fixture with Browser-preservation/no-input-injection assertions;
- cleanup/idempotence fixture;
- acceptance bridge fixture showing P17 invocation stays bound to the same candidate;
- mismatch/stale candidate rejection;
- explicit assertion that no test updates `alpha-live`.

No broad QA, no real WOF, no actual alpha-live movement.

## Terminal result

Write exactly:
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS_RESULT.md`

Record implementation commits, changed files, focused checks, integrationReady, exact P19/P20/W3/Owner boundaries, safety, and nextAction.

Successful terminal state proves the staging/acceptance harness implementation only. It must state `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, and `alphaLiveMoved=false`.
