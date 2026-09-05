stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P20_OWNER_VISUAL_CONFIRMATION_ALPHA_LIVE_PROMOTION_GATE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.owner-visual-confirmation-alpha-live-promotion-gate-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P20_OWNER_VISUAL_CONFIRMATION_ALPHA_LIVE_PROMOTION_GATE_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P20_OWNER_VISUAL_CONFIRMATION_ALPHA_LIVE_PROMOTION_GATE_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P20_OWNER_VISUAL_CONFIRMATION_ALPHA_LIVE_PROMOTION_GATE`

# Alpha V1 Product Takeover P20 — Owner Visual Confirmation + Alpha-Live Promotion Gate

Repository: `ouyong520/wof-ai-private`

This is a long release-safety/product-finalization module. Implement the complete final confirmation + promotion gate, but do **not** perform a real alpha-live promotion in this stage.

Read latest `main`, `AGENTS.md`, testing cadence, dedup guard, current dispatch, and at minimum:
- P17 final acceptance orchestrator/result;
- P19 prompt/result/candidate/attestation if available;
- P16 canonical acceptance evidence contract;
- P18 draw evidence contract/result if available;
- W3 qualification result/runner contract;
- W1 permanent live-test bootstrap result;
- `WOF_ALPHA_SETUP_ONCE.cmd`;
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`;
- current controlled `alpha-live` update/rollback behavior.

## Ownership

Normal dedup-v2 create-only canonical claim -> exact-token readback -> create-only stage claim -> exact-token readback. Fail closed. No recovery invention.

## Goal

Close the last human/release gap after repository/runtime evidence has reached P17's `READY_FOR_OWNER_VISUAL_CONFIRMATION` boundary:

`P17 acceptance bundle + P19 final candidate attestation -> one simple Owner visual yes/no receipt -> fail-closed promotion plan -> optional guarded alpha-live apply capability`.

The Owner must never be asked to inspect DevTools, JSON, coordinates, package hashes, branches, or implementation details.

## Workstream A — one-question visual confirmation receipt

Implement a Windows-friendly final confirmation command/module under a dedicated release area such as `parallel/OWNER_RELEASE/`.

It must:
1. Read the latest P17 final acceptance bundle and P19 final candidate attestation/path.
2. Refuse to ask for visual PASS unless P17 is exactly at the automatic `READY_FOR_OWNER_VISUAL_CONFIRMATION` boundary and all exact World/runtime/renderer/package identities are internally consistent.
3. Ask one plain Owner question equivalent to: `游戏里的提示是否稳定跟随正确的人物/怪物？` with explicit YES/NO.
4. YES writes an immutable-ish bounded local receipt with candidate source commit, package version, acceptance-bundle hash, exact authority/runtime/renderer identity, timestamp, and `ownerVisualVerdict=PASS`.
5. NO writes `ownerVisualVerdict=FAIL` and must permanently block promotion for that receipt/bundle combination.
6. Missing/ambiguous input, stale evidence, W3 INCONCLUSIVE, draw evidence missing, or identity mismatch must produce WAITING/REJECTED and never ask a misleading success question.
7. Never infer PASS from draw acknowledgement, screenshots, fixtures, or module-load status.

Prefer deterministic JSON + concise Markdown/text evidence under `Documents\WOF_RESULTS` when run on Owner Windows, with repository-side fixtureable path overrides for tests.

## Workstream B — promotion plan / CAS gate

Implement a promotion planner/verifier that consumes:
- P19 final candidate + attestation;
- P17 final acceptance bundle;
- P20 Owner visual receipt;
- current observed `alpha-live` commit.

A READY promotion plan must record:
- exact `fromAlphaLiveCommit`;
- exact `toCandidateCommit`;
- package version/candidate hash;
- acceptance bundle hash;
- visual receipt hash;
- rollback/previous commit metadata;
- fast-forward ancestry requirement;
- safety invariants;
- one deterministic plan hash.

Fail closed if:
- Owner verdict is not PASS;
- P17 is not acceptance-ready for the same identity/candidate;
- candidate/attestation hashes disagree;
- `alpha-live` changed after the plan was prepared;
- target is not a descendant of current alpha-live (unless repository policy explicitly proves another safe non-force mechanism);
- target lacks permanent W1 live-update required files;
- target claims unsupported W3/visible evidence;
- any safety flag is weakened.

## Workstream C — guarded apply capability, never executed here

Implement an **optional** explicit apply path suitable for later PM use, but do not invoke it in this worker stage.

Requirements:
1. Default behavior is dry-run/plan only.
2. Apply requires the exact expected promotion-plan hash as an argument/confirmation token.
3. Re-read current remote/local alpha-live just before apply and perform compare-and-swap style rejection if it differs from `fromAlphaLiveCommit`.
4. Promotion must be non-force / fast-forward only. Do not use force-push.
5. On push/update failure, report no promotion; do not partially rewrite release metadata.
6. Preserve W1 Owner updater's local last-known-good apply/rollback behavior.
7. Record a promotion result artifact only after confirmed ref movement.
8. Never auto-promote merely because the Owner said YES; all cryptographic/ancestry/evidence gates still apply.

If repository execution context cannot safely perform remote Git mutation, implement and test the guarded apply command contract with a local bare-repo fixture and leave actual PM invocation for later.

## Workstream D — final one-command UX

Provide one final wrapper command that, when used later after P19/P18/W3 are ready, can:
1. invoke/reuse P17 final acceptance flow;
2. only if ready, ask the one Owner visual question;
3. produce the visual receipt and promotion plan;
4. stop before real promotion unless an explicit PM-only apply action is separately invoked.

This should preserve the permanent `Desktop\WOF_ALPHA_TEST.cmd` update channel; do not create a new permanent Owner install path.

## Write boundaries

Expected new files under `parallel/OWNER_RELEASE/` plus narrow tests/docs. Reading W1/P17/P19/P16/P18 contracts is allowed. Avoid modifying P18 HUD/draw files, P15 runtime semantics, W3 producer, or `alpha-live` itself.

Do not modify `WOF_ALPHA_SETUP_ONCE.cmd` / `owner_live_retest_loop.ps1` unless a concrete release-gate integration defect requires a narrow change. Prefer keeping the already-proven W1 channel unchanged.

## Focused checks

Run only:
- Python/PowerShell/CMD syntax or parse checks as appropriate;
- PASS/FAIL/WAITING visual receipt fixtures;
- candidate/bundle/receipt mismatch rejection;
- stale alpha-live CAS rejection;
- local bare Git fast-forward promotion success and non-fast-forward rejection;
- no-force assertion;
- required W1 release-file validation;
- deterministic plan hash fixture.

No broad QA, no real WOF, no real alpha-live movement.

## Terminal result

Write the specified RESULT.json/RESULT.md with implementation commits, changed files, focused checks, integrationReady, exact later Owner/PM actions, safety, and explicit `alphaLiveMoved=false`.

Successful terminal state proves the release gate implementation only. It must not claim that the Owner has visually accepted the game or that alpha-live has been promoted.
