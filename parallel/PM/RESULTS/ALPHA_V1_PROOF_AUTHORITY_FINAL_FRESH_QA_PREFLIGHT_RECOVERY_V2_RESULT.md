# Alpha V1 Proof-Authority Final Fresh QA — Preflight Compatibility Recovery V2 Result

## Terminal verdict

**PASS — ALPHA V1 PROOF-AUTHORITY FINAL FRESH QA RECOVERY V2 — PREFLIGHT COMPATIBILITY REPAIRED / 17/17 INDEPENDENT CASES PASS — READY FOR BOUNDED REAL WOF ACCEPTANCE**

## Scope / authority

This is the PM-authorized recovery of the same previously blocked Final Fresh QA objective, not a second opinion and not a new QA chain.

Canonical recovery key: `alpha.v1.proof-authority-final-fresh-qa.preflight-recovery-v2`

Claim token: `900d625669f83c0bee5186314b99931e1a1ffe22bdfdb303`

No Browser/WOF was launched. No V1/proof implementation was modified. No `product/alpha/**` file was modified. No frozen 17-case ID, expected outcome, assertion, vector, matrix, runner or adapter contract was changed. Historical PASS QA and implementation-owned regression were not rerun as oracle.

## QA-owned compatibility defect repaired

Only the authorized QA preflight compatibility line was changed by commit `4035d6eae4c6a03653fa0352ca949fdb021ce292`:

`parallel/ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE/future_fresh_qa_preflight.mjs`

The obsolete marker for `ALPHA V1 DUAL-OVERLAY PROOF-AUTHORITY HARDENING FIX V2` was replaced with the exact authoritative Recovery V5 terminal semantics:

`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING INTEGRATION FIX V4 RECOVERY V5 — AUTHORITY-V2 RUNNABLE PATH / TRUST ROOT / LIFECYCLE / MANIFEST COHERENT — READY FOR THE ONE FINAL FRESH QA`

The repair commit diff contains exactly one file with one deletion / one addition. The preflight still requires result/manifest/fixed-commit inputs, 40-hex blob pins, required manifest selections, exact blob equality, fixture-integrity flags, and exact fixed commit.

## Exact candidate / preflight pin result

Authoritative implementation candidate: `dec5ffd9b1c3d29559d3af47b200ef7b2f71e4cf`

Exact runnable fixed-tree commit: `cd19b462e31f7464669471e73b651843e5c716c9`

Authoritative `RUN_MANIFEST.json` blob: `f61abf058b997ed76a3d54e7e27ac0e017fa67a9`

The immutable GitHub tree at `cd19b462e31f7464669471e73b651843e5c716c9` was checked against every `productBlobs` / `proofToolBlobs` manifest entry selected by the repaired preflight. All selected paths exist at that exact fixed commit and their Git blob identities equal the manifest pins. Required authority-critical pins include:

- authority-v2 trust contract: `5a9a842e1dfac4fa98564ad6034eaa8439cee03a`
- proof core: `2ae605748728316f9b477bd057c19abb9da4998c`
- proof Top: `d0b8d0b833e9478c9e7ad67328d1312bf3642ad4`
- proof Worker: `e739d5b132cd8177148ff2e5e24f868dc656f971`
- authority-v2 loader: `be3c108ce76a6c9d9ada9a8a285886b70fdde692`
- player warning helper: `af7f2359514dc6f86f74fac0c47858e8a6acf107`
- enemy target-label helper: `e6e1260559f735b85ce6f69e87803369f125b2de`
- production real Worker: `b7f4506fc90b681ede059df5ad3316e665c6f15e`
- HUD: `50d944c451ac94b114e4f86441aeae8ad6b25c78`
- loader: `66aee09fc2dd009c2f295d2092f3129548605efb`
- player projection profile: `bbed0618b348961580ca805bb93e4d17525f0142`
- enemy projection profile: `8de57739818503a0e14702d2fa0bb4eba58228d2`
- HUDANCHOR loader/top/worker/gl: `8e7a72eb14556f181e4322825e98f7ac57f8eed5` / `95ae41bfb39b42deb1fee267f27da7b13a4b622c` / `12f06e40fb457963b082813607eec05e71bf7951` / `e4f91799ecc2204c68894d25056c5d6b747bfaec`
- evidence schema: `f9213012502b4a307e6cab0df23fbe9f5812f769`

Therefore the repaired preflight compatibility condition is satisfied for the exact fixed tree; later unrelated PM/docs/Collector/Training-Farm commits on `main` were not treated as floating SUT authority.

## Frozen fixture integrity / selftest

Frozen oracle files remained unchanged. Exact independently materialized hashes used for execution included:

- `fixture_catalog.json`: `e9a661a7bbb361e298628ae91307447e37307457`
- `fixture_vectors.mjs`: `776c2bac945f537202b188ebc2ff858510afc930`
- `future_fresh_qa_runner.mjs`: `3db3ca98bde29c09013dd5dc6c65ea44d04212b3`
- `fixture_selftest.mjs`: `d9f3e85da18274d33d350c1a75444bcca03be4f2`
- `CASE_MATRIX.md`: `fee897464dc478944cbbef76321386f0415add39`

Fixture-only selftest result:

`PASS — fixture schema/coverage self-check only — 17/17 — NO SUT LOADED — NO SUT VERDICT`

## Independent 17-case execution

The frozen runner was executed unchanged through a minimal QA-owned adapter against byte-exact authority-v2 contract `5a9a842e1dfac4fa98564ad6034eaa8439cee03a` and proof core `2ae605748728316f9b477bd057c19abb9da4998c`. Production projection profile snapshots were also byte-exact to their fixed-tree pins.

Final authoritative invocation:

- PASS QA-PA-001 `untrusted-signer-provenance`
- PASS QA-PA-002 `synthetic-repository-fake-live`
- PASS QA-PA-003 `exact-authority-binding`
- PASS QA-PA-004 `authority-change-revocation`
- PASS QA-PA-005 `cross-authority-aggregation`
- PASS QA-PA-006 `player-respawn-calibration`
- PASS QA-PA-007 `enemy-same-slot-replacement`
- PASS QA-PA-008 `enemy-type-offset-lifecycle`
- PASS QA-PA-009 `surface-mapping-authority`
- PASS QA-PA-010 `malformed-coercible-epoch`
- PASS QA-PA-011 `warning-sampleat-strict`
- PASS QA-PA-012 `target-strict`
- PASS QA-PA-013 `public-mutable-terminal`
- PASS QA-PA-014 `stale-replayed-transaction`
- PASS QA-PA-015 `same-authority-positive-flow`
- PASS QA-PA-016 `safety-boundary-exact`
- PASS QA-PA-017 `synthetic-no-production-activation`

Runner terminal:

`PASS — 17/17 QA-OWNED FINAL FRESH-QA AUTHORITY CASES`

During harness bring-up, one QA-adapter-only default-argument translation accidentally converted an `undefined` malformed target vector to valid `0`; it was corrected in the ephemeral QA adapter only. The SUT and frozen oracle were untouched, and only the complete post-correction 17/17 invocation above is authoritative.

## Exact safety boundary

Verified exact invariants remain:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `workerReplacement=false`

## Stop condition

Repository QA stops here. Do not open a second opinion, cross-check, V3/V4 QA, readiness audit, or closeout QA. The next permitted step is the already-prepared bounded real WOF acceptance / Owner gameplay acceptance.

**PASS — ALPHA V1 PROOF-AUTHORITY FINAL FRESH QA RECOVERY V2 — PREFLIGHT COMPATIBILITY REPAIRED / 17/17 INDEPENDENT CASES PASS — READY FOR BOUNDED REAL WOF ACCEPTANCE**
