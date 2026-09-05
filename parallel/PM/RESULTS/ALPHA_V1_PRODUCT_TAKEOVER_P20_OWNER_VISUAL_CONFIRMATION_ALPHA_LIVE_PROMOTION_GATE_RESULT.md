# Alpha V1 P20 — Owner Visual Confirmation + Alpha-Live Promotion Gate

## Outcome

**COMPLETE / integration-ready.** P20 now implements the final human/release boundary without moving the real `alpha-live` ref. The implementation asks exactly one real Owner YES/NO question only after the final automatic evidence gate is ready, binds the answer to the exact final candidate/attestation/P17 bundle, produces a deterministic promotion plan, and leaves actual release behind a separate explicit PM apply action.

No real Owner visual PASS was claimed in this task. No screenshot, P18 draw acknowledgement, fixture, or module-load signal can synthesize PASS.

## Changes

- Added `parallel/OWNER_RELEASE/owner_release_gate.py` with four bounded commands:
  - `confirm`: candidate/attestation/P17 evidence gate + single Owner YES/NO receipt.
  - `plan`: deterministic, hash-bound alpha-live promotion plan only.
  - `apply`: dry-run by default; explicit apply requires `--execute` plus the exact `--confirm-plan-hash`.
  - `run`: P17 -> one Owner question -> receipt -> plan, and always stops before real promotion.
- Added `parallel/OWNER_RELEASE/WOF_ALPHA_FINAL_RELEASE_GATE.cmd` as the Windows one-command Owner entry point. It contains no `--execute` path.
- Added focused tests and a concise release-contract README.
- P20 auto-discovers P19's stable `parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json` contract and accepts its `candidatePath` / `attestationPath` outputs.

Implementation commits:

- `d3a5310a155a22e35cc8291fe77e70acfc6377e0`
- `a0747e543ea7f563c070ccb63a3c09c42c722fc0`
- `cc508079e3d6722b7a4c9aed46d11b31b9c16b01`
- `1071f4f5386ce1ef741a65bee3a0c98b5fd0efd5`

## Visual Receipt Contract

The question is:

`游戏里的提示是否稳定跟随正确的人物/怪物？请输入 YES 或 NO`

The question is asked only if all of these are exact and consistent:

- P19 final candidate + attestation are present and hash-bound.
- P17 is exactly `READY_FOR_OWNER_VISUAL_CONFIRMATION`.
- W3 is `PASS` with proven renderer source.
- P16 is `HUD_INGEST_ACCEPTED` with `visibleProof=NOT_PROVEN`.
- P18 is `CANONICAL_DRAW_ACKNOWLEDGED` with `visibleProof=NOT_PROVEN`.
- World/page/authority/runtime/renderer identities agree.
- Read-only/no-input/no-fallback safety remains unchanged.

`YES` writes a bounded immutable-style PASS receipt for the exact candidate/bundle combination; it does **not** promote. `NO` writes FAIL and that receipt cannot be overwritten into PASS. Missing, inconclusive, stale, or mismatched evidence emits WAITING/REJECTED with `questionAsked=false`.

Test-only fixture answers are marked `promotionEligible=false`, so a fixture PASS cannot authorize a plan.

## Promotion Gate

A READY plan binds:

- `fromAlphaLiveCommit`
- `toCandidateCommit`
- package version
- candidate SHA-256
- P19 attestation SHA-256
- P17 bundle SHA-256
- P20 visual receipt SHA-256
- exact runtime/renderer identity
- rollback previous commit metadata
- W1 permanent release-file requirements
- fast-forward/CAS/no-force/safety invariants

The deterministic plan hash is `sha256(canonical-json(planCore))`; timestamps and local artifact paths do not alter that core hash.

Apply re-hashes every bound artifact, immediately re-reads `alpha-live`, rejects any stale `fromAlphaLiveCommit`, re-checks ancestry and W1 files, and refuses force-style push arguments. A promotion result is written only after the ref is confirmed at the target.

For local bare-repo testing, exact-old `git update-ref <new> <old>` provides atomic CAS after explicit fast-forward validation. A real remote remains normal non-force push only; no force, force-with-lease, or `+refspec` path exists.

## Tests

Focused checks passed:

- Python `py_compile`: PASS.
- `python -m unittest -v test_owner_release_gate.py`: **5 passed**.
- PASS / FAIL / WAITING receipt fixtures: PASS.
- Fixture PASS promotion rejection: PASS.
- Candidate / bundle / receipt mismatch rejection: PASS.
- Deterministic plan-hash fixture: PASS.
- Required W1 release-file validation: PASS.
- Local bare-repo fast-forward apply: PASS.
- Stale alpha-live CAS rejection: PASS.
- Non-fast-forward rejection: PASS.
- No-force argument enforcement: PASS.
- P19 stable-pointer discovery fixture: PASS.
- Final CMD wrapper static contract: PASS; wrapper does not invoke `--execute`.

No broad QA, real WOF run, or real alpha-live apply was performed.

## Integration

The existing W1 permanent channel remains the release mechanism. P20 validates the same permanent updater release files before a plan can be READY:

- `WOF_ALPHA_TEST.cmd`
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`
- `parallel/PYLAUNCH/render_authority_measurement_entry.py`
- `parallel/PYLAUNCH/requirements.txt`

The real `alpha-live` ref was observed as `d664618403b1ae83f6880ca4d3833202c299415f` before implementation and again after implementation. It was not moved by P20.

## Safety

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- screenshot production coordinates disabled
- world-projection production coordinates disabled
- guessed renderer/object addresses disabled
- legacy spatial fallback disabled
- force push forbidden
- P18 ownership untouched
- W3 ownership untouched
- `alphaLiveMoved=false`
- real Owner visual verdict: `NOT_RUN`
- visible proof remains `NOT_PROVEN` until the Owner actually answers the final question from real WOF observation

## Owner / PM Action

After P19 emits/verifies the final candidate pointer and the P17 one-command flow can reach `READY_FOR_OWNER_VISUAL_CONFIRMATION`, run:

`parallel\OWNER_RELEASE\WOF_ALPHA_FINAL_RELEASE_GATE.cmd`

If the question appears, answer only from real WOF observation with `YES` or `NO`. A YES produces the receipt and plan but still does not move `alpha-live`.

Only after reviewing those exact artifacts should PM separately invoke the explicit apply path with `--execute` and the exact plan hash. That later apply action was intentionally not executed by P20.
