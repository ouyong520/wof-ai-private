# Alpha V1 P33 — Post-Repair Final Candidate Rebuild Preparation Result

State: **COMPLETE**

Tested implementation commit: `c8c61112efbccdef5794ee68cd27767eacb72e96`  
Tested tree: `70329cbceffa8b17bfc88fc753b28648f4cbf6fc`

## Verdict

P33 completed the repository-side post-repair final-candidate rebuild mechanism. A rebuild now fails closed unless the caller supplies one explicit full source commit SHA whose Git ancestry contains all PM-accepted repair tested commits: P29 `c02f7e108e73665f22eb950573622acb6f452732`, P30 `90094a656ab311f18b0a758716dc97c3f8df092d`, and P31 `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731`.

P32 remains terminal `BLOCKED`, `integrationReady=false`, tested commit `bd75c3b5f7fd20fe004fae21142a0fa19942e076`, and is explicitly excluded from the P33 accepted-repair set.

The historical P19 source `0752796369f1687435a1b1647e66ea0b5ab07688` and legacy latest-pointer shape are rejected as stale post-repair provenance.

## Mechanism completed

- Requires one exact 40-hex source commit; symbolic `HEAD` and abbreviated SHAs are rejected.
- Requires true Git ancestor containment for exact P29/P30/P31 tested commits.
- Re-reads terminal RESULT authority at the selected exact source before build.
- Preserves truthful P32 `BLOCKED` authority while excluding P32 from `requiredTestedCommits`.
- Builds through a temporary/staged pointer first; canonical pointer publication occurs only after verification.
- Binds and re-reads exact `sourceCommit`, `packageVersion`, candidate SHA-256, attestation SHA-256, rebuild manifest path/SHA-256, and required tested-commit map.
- Emits deterministic rebuild metadata for fixed inputs.
- Rejects stale pre-repair pointer/provenance that lacks the P33 manifest and exact required tested-commit map.
- Restores the prior pointer if post-publication verification fails.
- Windows entrypoint no longer defaults to `HEAD`; the exact source SHA is required as an argument.
- The previous P19 workflow no longer has contents-write permission or automatically publishes candidate bytes on ordinary `main` pushes; it is now a read-only rebuild-contract verification gate.

## Exact candidate proof

Fresh readback from tested commit `c8c61112efbccdef5794ee68cd27767eacb72e96` matched all implementation blobs:

- `parallel/OWNER_ONECLICK/post_repair_final_candidate_rebuild.py` → `77eab756a65b3ee1e2bae21f6f73e98400d87b8a`
- `parallel/OWNER_ONECLICK/test_post_repair_final_candidate_rebuild.py` → `f179dd0d8a6ed743948f586636d4f045594a7053`
- `parallel/OWNER_ONECLICK/WOF_ALPHA_BUILD_FINAL_CANONICAL_CANDIDATE.cmd` → `1855a97cc5bef3a842be992ff0ea259582a70188`
- `.github/workflows/alpha-p19-final-canonical-candidate.yml` → `59a6700aa0f7e20bb66dea89c34b002b096f913b`

GitHub Actions run `33977914719`, job `101337774061`, completed `success` on that exact implementation commit. Python compile passed. Focused deterministic regression passed **14/14** tests: 10 P33 post-repair cases plus the 4 existing P19 final-candidate integrity cases. The workflow also passed `git diff --exit-code -- parallel/OWNER_ONECLICK/CANDIDATES`, proving the contract check did not generate or alter repository candidate artifacts.

## Scope boundary

P33 did **not** rebuild or claim completion of a new final integrated package. P35 owns integration lineage; P36 owns renderer source trace; P34 owns retry readiness. P33 does not weaken or reinterpret those authorities.

No real WOF run, Owner retry, visual acceptance, promotion, or alpha-live movement was performed. `readOnly=true`, `ramWrites=0`, `inputInjection=false` remain unchanged.

## Next action

PM may use the separately owned terminal P35 integration lineage as an exact source input to this P33 mechanism when a fresh integrated candidate rebuild is authorized. P34 readiness and P36 renderer-source authority remain separate fail-closed gates. P33 itself authorizes neither Owner retry nor promotion.
