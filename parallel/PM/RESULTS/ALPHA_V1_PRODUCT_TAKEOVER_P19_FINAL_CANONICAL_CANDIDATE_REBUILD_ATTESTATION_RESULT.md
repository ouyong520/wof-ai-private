# Alpha V1 P19 — Final Canonical Candidate Rebuild + Attestation

State: **COMPLETE**  
Integration ready: **true**

## Outcome

P19 rebuilt one exact final canonical package candidate only after P18 was terminal `COMPLETE` / `integrationReady=true`. The final candidate is tied to immutable source commit `0752796369f1687435a1b1647e66ea0b5ab07688`, pins P15/P16/P17/P18 durable results and implementation ancestry, verifies every selected Git blob, emits a deterministic attestation, and publishes a stable latest pointer for later P21/P20 consumption.

W3 is truthfully retained as `INCONCLUSIVE`; `ownerVisualAcceptance=NOT_RUN` and `realWofAcceptance=NOT_RUN`. `alpha-live` was not moved.

## Changes

- Added `parallel/OWNER_ONECLICK/final_canonical_candidate.py` for exact-source rebuild, fail-closed P18 dependency handling, result/ancestry/blob validation, deterministic candidate/attestation generation, stable pointer publication, and verification.
- Added `parallel/OWNER_ONECLICK/WOF_ALPHA_BUILD_FINAL_CANONICAL_CANDIDATE.cmd` as the Windows-friendly build+verify entrypoint.
- Added focused deterministic tests and `.github/workflows/alpha-p19-final-canonical-candidate.yml` so the repository itself can rebuild from the exact checked-out commit and commit only the generated candidate artifacts.
- Emitted package version `2026.09.05.0752796369f1` with 90 selected files.
- Candidate: `parallel/OWNER_ONECLICK/CANDIDATES/FINAL_CANONICAL/ALPHA_V1_FINAL_CANONICAL_CANDIDATE_0752796369f1.json`, SHA256 `d7835982ef3210b605c0f90b25e859bf013c7d16be541f7f09f6ba7d4410a150`, Git blob `a1f2be25ff3a0e23f32aeba6509903d7def573b1`.
- Attestation: `parallel/OWNER_ONECLICK/CANDIDATES/FINAL_CANONICAL/ALPHA_V1_FINAL_CANONICAL_CANDIDATE_0752796369f1.attestation.json`, SHA256 `6d6796fa5b447150f160d0d06351119a77cf9f3af86bddc52539de738f6828bd`, Git blob `c4be0374fdbc096afcad69ee41a5fbd21723be32`.
- Stable pointer: `parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json`, Git blob `765c83064b2b4b4787d277897f3704d85a9f2c2d`.

## Tests

Focused workflow run `33955965163` passed Python 3.12 compile plus four P19 fixtures: P18-missing does not emit or mutate latest pointer; fixed-source rebuild is deterministic; non-ancestor implementation commits are rejected; mutated blob pins are rejected.

The same run performed the real repository build+verify on exact source `0752796369f1687435a1b1647e66ea0b5ab07688`: all 11 P15-P18 implementation commits were verified as ancestors, all 90 selected files were verified against exact Git blobs, and 23 critical P15/P16/P17/P18/W3 runtime/acceptance blobs were attested.

An independent post-build branch read confirmed `alpha-live=d664618403b1ae83f6880ca4d3833202c299415f`, unchanged from the before/after values recorded in the attestation.

No broad QA and no real WOF were run.

## Integration

The stable latest pointer is `READY` and records P15/P16/P17/P18 as `COMPLETE`. It binds the exact candidate source/package/hash to the exact attestation hash, so P21 can resolve and stage this immutable candidate rather than moving `main` or `alpha-live`.

P19 deliberately adds P17 acceptance runtime and the W3 qualification runner dependencies to the candidate blob set because those files are required by the later exact-candidate acceptance path and were not all part of the older P15 package selection.

## Owner Action

Do not promote `alpha-live` from P19. Use the later exact-candidate staging/acceptance path, run the bounded W3 normal-play qualification, and answer the later single Owner visual-confirmation question only when P17/P21/P20 request it.

W3 remains `SUBCOMPLETE / INCONCLUSIVE / LIVE_EVIDENCE_REQUIRED`; a repository package, P18 draw acknowledgement, or successful staging launch must not be treated as visible PASS.

## Recommended Next

P21 should consume `parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json`, stage source commit `0752796369f1687435a1b1647e66ea0b5ab07688` without changing `alpha-live`, and keep P17/W3/P16/P18 evidence bound to this candidate. P20 promotion remains gated on the later real Owner visual receipt.
