# Alpha V1 Proof-Authority Hardening V2 — ONE Final Fresh Independent QA

stageId: `ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA`
dedupProtocol: `v2`
dedupKey: `alpha.v1.proof-authority-hardening-v2.final-fresh-qa`
dedupMode: `exclusive`

Priority: **V1 FINAL REPOSITORY QA GATE — EXACTLY ONE INDEPENDENT QA BEFORE BOUNDED REAL WOF ACCEPTANCE**

## Owner / PM directive

This is the single allowed module-level independent QA after the Proof-Authority Hardening module became coherent and complete.

Follow `parallel/PM/TESTING_CADENCE_POLICY.md`:

- do not create second-opinion / cross-check / another QA generation after PASS;
- do not rerun historical PASS suites;
- do not turn this into implementation;
- if this QA finds a concrete defect, report that defect precisely so one focused implementation fix can repair it.

## Current completed implementation authority

Read first:

- `parallel/PM/RESULTS/ALPHA_V1_PROOF_AUTHORITY_HARDENING_INTEGRATION_FIX_V4_RECOVERY_V5_RESULT.md`
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/RUN_MANIFEST.json`
- `parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/PREP_RESULT.md`
- `parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/README.md`
- `parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/CASE_MATRIX.md`
- `parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/SUT_ADAPTER_CONTRACT.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`

Hardening Recovery V5 terminal result is authoritative:

`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING INTEGRATION FIX V4 RECOVERY V5 — AUTHORITY-V2 RUNNABLE PATH / TRUST ROOT / LIFECYCLE / MANIFEST COHERENT — READY FOR THE ONE FINAL FRESH QA`

Exact implementation candidate:

`dec5ffd9b1c3d29559d3af47b200ef7b2f71e4cf`

Manifest repin commit:

`cd19b462e31f7464669471e73b651843e5c716c9`

Manifest blob:

`f61abf058b997ed76a3d54e7e27ac0e017fa67a9`

Critical SUT pins recorded by the completed implementation result:

- external trust contract: `5a9a842e1dfac4fa98564ad6034eaa8439cee03a`
- proof core: `2ae605748728316f9b477bd057c19abb9da4998c`
- Top observer: `d0b8d0b833e9478c9e7ad67328d1312bf3642ad4`
- Worker observer: `e739d5b132cd8177148ff2e5e24f868dc656f971`
- authority-v2 loader: `be3c108ce76a6c9d9ada9a8a285886b70fdde692`
- implementation regression: `f93abb13c59053df4b76df1085fb27e188abf314`
- live-proof evidence schema: `f9213012502b4a307e6cab0df23fbe9f5812f769`

Do not float the QA onto newer unpinned SUT blobs. Later PM/docs/Collector commits are irrelevant if the manifest-selected proof/product blobs remain exact.

## Canonical claim

Before substantive QA work:

1. re-read current `main`, current relevant results and claims;
2. if an equivalent final Fresh QA already has a durable terminal RESULT, stop `ALREADY COMPLETE — SAFE TO CLOSE`;
3. otherwise create-only:
   `parallel/PM/DEDUP_CLAIMS/alpha.v1.proof-authority-hardening-v2.final-fresh-qa.json`
   with a fresh unpredictable `claimToken`;
4. re-read and verify exact ownership/token/state;
5. create the v2 stage claim:
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA.json`;
6. ambiguity or occupied claim => fail closed according to canonical dedup v2.

## Independent fixture authority

Use the already-frozen QA-owned fixture namespace:

`parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/`

The frozen 17 cases are the independent oracle. Do not replace their expected outcomes with the implementation-owned `proof_authority_regression.mjs` expectations.

Coverage:

1. untrusted witness/signer provenance;
2. repository/synthetic fake-live evidence;
3. exact proofSession / Worker generation / runtime epoch / pair generation / pair nonce binding;
4. old capability invalidation after authority change;
5. cross-authority aggregation rejection;
6. player respawn invalidating old calibration;
7. same-slot/same-type/near-position enemy replacement not becoming retarget without continuity;
8. enemy type-offset reuse across lifecycle rejection;
9. surface/drawing-buffer mapping authority mismatch;
10. malformed/coercible epoch rejection;
11. malformed/coercible/non-finite `warningSampleAt` rejection;
12. malformed/coercible target rejection;
13. public mutable/serialized state unable to force `IMPLEMENTATION_READY`;
14. stale/replayed transaction evidence rejection;
15. positive same-authority/same-lifecycle retarget/live flow;
16. exact safety invariants `readOnly=true / ramWrites=0 / inputInjection=false / workerReplacement=false`;
17. synthetic evidence unable to activate production projection/calibration profiles.

## Exact execution sequence

Run only the final independent gate:

1. verify exact Hardening V5 RESULT and exact authority-v2 `RUN_MANIFEST.json` pins;
2. run:
   `node parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/fixture_selftest.mjs`
3. run the exact-blob gate using:
   `parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/future_fresh_qa_preflight.mjs`
4. implement only the minimal QA-owned adapter allowed by `SUT_ADAPTER_CONTRACT.md` if needed to bind the frozen fixture to the final public SUT interface;
5. the adapter may translate public method/signature shape only; it may not alter fixture cases, expected outcomes, authority semantics, production code, or SUT behavior;
6. run:
   `node parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/future_fresh_qa_runner.mjs --adapter <QA-owned-adapter>`
7. independently inspect exact blob evidence and the 17 case results;
8. write one durable final RESULT and terminal-close this QA claim/stage.

## Forbidden

Do NOT:

- modify proof implementation to make QA pass;
- modify `product/alpha/**`;
- modify danger rules or target semantics;
- modify Transport / Recorder / PYLAUNCH / OneClick;
- launch Browser/WOF;
- activate production projection/calibration profiles;
- rerun historical player-head/enemy-label/Transport/Recorder/PYLAUNCH QA;
- run another second-opinion/cross-check after this;
- issue PASS from implementation-owned 11/11 regression alone.

## Verdict rules

PASS requires:

- exact candidate/blob preflight PASS;
- frozen fixture selftest PASS;
- all **17/17** independent cases PASS against the exact authority-v2 SUT;
- no production mutation;
- exact safety boundary remains `readOnly=true / ramWrites=0 / inputInjection=false / workerReplacement=false`.

PASS terminal wording:

`PASS — ALPHA V1 PROOF-AUTHORITY HARDENING V2 FINAL FRESH QA — 17/17 INDEPENDENT CASES PASS — READY FOR BOUNDED REAL WOF ACCEPTANCE`

BLOCKED terminal wording:

`BLOCKED — ALPHA V1 PROOF-AUTHORITY HARDENING V2 FINAL FRESH QA — <precise concrete defect / exact failed case>`

After PASS, stop. Do not schedule another repository QA. The next gate is the already-prepared bounded real WOF acceptance authorization/check, then Owner gameplay acceptance.