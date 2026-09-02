# Alpha V1 Proof-Authority Final Fresh QA — Preflight Compatibility Recovery V2

stageId: `ALPHA_V1_PROOF_AUTHORITY_FINAL_FRESH_QA_PREFLIGHT_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.proof-authority-final-fresh-qa.preflight-recovery-v2`
dedupMode: `exclusive`

Priority: **V1 FINAL REPOSITORY QA GATE — PM-AUTHORIZED RECOVERY OF THE SAME BLOCKED FINAL QA OBJECTIVE**

## Why this recovery exists

The single Final Fresh QA already ran far enough to fail closed before SUT execution. Its durable result is:

`parallel/PM/RESULTS/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_RESULT.md`

Exact blocker:

`future_fresh_qa_preflight.mjs` hard-codes an obsolete `ALPHA V1 DUAL-OVERLAY PROOF-AUTHORITY HARDENING FIX V2` COMPLETE marker, while the current authoritative implementation completion is Recovery V5:

`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING INTEGRATION FIX V4 RECOVERY V5 — AUTHORITY-V2 RUNNABLE PATH / TRUST ROOT / LIFECYCLE / MANIFEST COHERENT — READY FOR THE ONE FINAL FRESH QA`

The prior Final QA did **not** execute the 17 SUT cases. This recovery is therefore not a second opinion or another QA generation. It is PM authorization to repair the one QA-owned preflight compatibility defect and then finish the same final independent QA objective once.

## Current authoritative candidate

Read first:

- `parallel/PM/RESULTS/ALPHA_V1_PROOF_AUTHORITY_HARDENING_INTEGRATION_FIX_V4_RECOVERY_V5_RESULT.md`
- `parallel/PM/RESULTS/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_RESULT.md`
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/RUN_MANIFEST.json`
- `parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/PREP_RESULT.md`
- `parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/CASE_MATRIX.md`
- `parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/SUT_ADAPTER_CONTRACT.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`

Exact implementation candidate:

`dec5ffd9b1c3d29559d3af47b200ef7b2f71e4cf`

Exact manifest repin / runnable fixed-tree commit:

`cd19b462e31f7464669471e73b651843e5c716c9`

Authoritative manifest blob:

`f61abf058b997ed76a3d54e7e27ac0e017fa67a9`

Critical pins from Recovery V5:

- external trust contract: `5a9a842e1dfac4fa98564ad6034eaa8439cee03a`
- proof core: `2ae605748728316f9b477bd057c19abb9da4998c`
- Top observer: `d0b8d0b833e9478c9e7ad67328d1312bf3642ad4`
- Worker observer: `e739d5b132cd8177148ff2e5e24f868dc656f971`
- authority-v2 loader: `be3c108ce76a6c9d9ada9a8a285886b70fdde692`
- implementation regression: `f93abb13c59053df4b76df1085fb27e188abf314`
- evidence schema: `f9213012502b4a307e6cab0df23fbe9f5812f769`

Later PM/docs/Collector/Training-Farm commits are irrelevant to the SUT if these exact manifest-selected blobs remain unchanged.

## Canonical recovery ownership

The old Final Fresh QA canonical claim is terminal BLOCKED and must remain historical evidence. Do not overwrite/delete/reuse it.

Use this new PM-authorized recovery dedup key only:

`alpha.v1.proof-authority-final-fresh-qa.preflight-recovery-v2`

Follow canonical dedup v2 exactly: create-only canonical claim, re-read exact token/state, then create the v2 stage claim. Any ambiguity fails closed.

## Narrow permitted repair

You are explicitly authorized to modify **only**:

`parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/future_fresh_qa_preflight.mjs`

for the concrete compatibility defect identified by the blocked Final QA.

The repaired preflight must truthfully recognize the current authoritative Recovery V5 COMPLETE result and must remain fail-closed. Prefer exact Recovery V5 terminal semantics, not a loose generic `COMPLETE` match.

It must continue to enforce:

- required result/manifest/fixed-commit inputs;
- exact current manifest pin presence;
- valid 40-hex blob SHAs;
- working-tree file hashes equal manifest blob pins;
- exact fixed-tree commit check;
- fixture contract integrity;
- no floating current-main SUT acceptance.

For the runnable fixed tree, use the exact manifest-repin commit `cd19b462e31f7464669471e73b651843e5c716c9`, because that tree contains the coherent authority-v2 candidate plus the authoritative repinned `RUN_MANIFEST.json`.

## Frozen oracle — MUST NOT CHANGE

Do not modify:

- `fixture_catalog.json`
- `fixture_vectors.mjs`
- `CASE_MATRIX.md`
- `fixture_selftest.mjs`
- `future_fresh_qa_runner.mjs`
- `SUT_ADAPTER_CONTRACT.md`
- any of the 17 case IDs
- expected outcomes
- assertion names or semantics

Do not modify any proof implementation, `product/alpha/**`, danger rules, target semantics, Transport, Recorder, PYLAUNCH, OneClick, input/AI, or production projection/calibration profile.

## Finish the same Final Fresh QA in this recovery

After the narrow preflight compatibility repair:

1. confirm only the permitted QA preflight changed before execution;
2. run the frozen fixture selftest unchanged;
3. execute the repaired exact-blob preflight against the authoritative Recovery V5 result, authority-v2 manifest, and exact fixed tree `cd19b462e31f7464669471e73b651843e5c716c9`;
4. create/use only the minimal QA-owned SUT adapter permitted by `SUT_ADAPTER_CONTRACT.md` if required;
5. run the frozen `future_fresh_qa_runner.mjs` unchanged;
6. require all 17/17 independent cases PASS for success;
7. verify exact safety invariants remain `readOnly=true / ramWrites=0 / inputInjection=false / workerReplacement=false`;
8. write one durable Recovery V2 RESULT and terminal-close this recovery canonical/stage claim.

Do not rerun historical PASS suites or implementation-owned 11/11 regression as a substitute oracle.

## Forbidden proliferation

Do NOT create:

- second opinion;
- cross-check;
- another QA V2/V3/V4 chain;
- another readiness audit;
- another closeout QA;
- Browser/WOF repository test;
- any implementation fix unless one of the frozen 17 cases exposes a concrete SUT defect.

If a frozen 17-case exposes a real SUT defect, stop BLOCKED with the exact case/defect. Do not repair production in this QA recovery.

## Terminal verdicts

Success only:

`PASS — ALPHA V1 PROOF-AUTHORITY FINAL FRESH QA RECOVERY V2 — PREFLIGHT COMPATIBILITY REPAIRED / 17/17 INDEPENDENT CASES PASS — READY FOR BOUNDED REAL WOF ACCEPTANCE`

Failure only:

`BLOCKED — ALPHA V1 PROOF-AUTHORITY FINAL FRESH QA RECOVERY V2 — <exact preflight or frozen-case defect>`

After PASS, stop repository QA. The next step is the already-prepared bounded real WOF acceptance authorization/check and then Owner gameplay acceptance.