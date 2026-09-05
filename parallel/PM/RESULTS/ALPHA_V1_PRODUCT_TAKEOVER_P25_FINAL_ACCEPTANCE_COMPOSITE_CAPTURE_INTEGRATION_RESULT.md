# Alpha V1 P25 Final Acceptance Composite Capture Integration — RESULT

## 1. Verdict

**COMPLETE — integrationReady=true.**

The existing P25 composite capture integration was not rewritten in this continuation. Its five owned files on current `main` are byte-identical to durable tested candidate `d56d9b69aa682f5f49eeff8fe367ee68097f3c0f`. Terminal P27 resolved the former `P21_STAGED_RUNTIME_CANONICAL_FEED_NOT_EXPOSED` / `NOT_EXPOSED_BY_STAGED_RUNTIME_STATUS` structural seam, and deterministic committed readback confirms the supported P21/P27/P25 path now carries same-session maintained P10 `wof-alpha-canonical-runtime-coordinator-v1` status into P25.

This is implementation/integration proof only. It is not real-WOF or Owner-visible proof.

## 2. Implementation and tested bytes

P25 implementation commits remain:

- `d6a0817bda6e0856ae71f1215d72dd0f6d6a7340`
- `f20e4f9ae38e40124d23012ef40cf8048689bb93`
- `0a1e99b247b3405186dabcc32b95462248a77ac3`
- `95204c04bf7d48d78cdd1924c11fb7fdfa64bc54`
- `d56d9b69aa682f5f49eeff8fe367ee68097f3c0f` — durable tested candidate

Current P25-owned blob readback exactly matches that tested candidate:

- `parallel/OWNER_ACCEPTANCE_COMPOSITE/README.md` → `25d9c7010c0b85284b1a6f18cad94b0749df3f09`
- `parallel/OWNER_ACCEPTANCE_COMPOSITE/WOF_ALPHA_FINAL_COMPOSITE_ACCEPTANCE.cmd` → `12dc1062e6929facd6e70353731e1bddcbd7dd8b`
- `parallel/OWNER_ACCEPTANCE_COMPOSITE/composite_acceptance.py` → `d6ce58cb3252e174d48de9b20cbcf17978fff8e2`
- `parallel/OWNER_ACCEPTANCE_COMPOSITE/p25_runtime_tee.py` → `a43179ce5d691a9a6a41a2e08b5513ca66761ae8`
- `parallel/OWNER_ACCEPTANCE_COMPOSITE/test_composite_acceptance.py` → `b44c194276f0213b9c0508d2fadd80e9292cf854`

No P25 implementation byte changed during this continuation.

## 3. Post-P27 deterministic revalidation

Terminal P27 is `COMPLETE`, `integrationReady=true`, terminal commit `33f0621ca39c144e6d21a685ca608cd9d1fd1e6f`.

Committed call-chain readback establishes:

1. P25 supplies its existing tee builder through `p21_runtime_override(...)`.
2. P21 calls `_wrap_staged_runtime_command(...)` **after** `build_runtime_command(...)` returns, so the P25 builder override cannot bypass P27.
3. P27 installs its interposer on the exact-candidate `MeasurementPublisher` before delegating to the P25 tee script.
4. P27 accepts only validated output from the maintained exact-candidate P10 `CanonicalRuntimeCoordinator`; it publishes that status as `canonicalCoordinator` and `alpha_status.canonicalOverlay` while keeping W3/V3 measurement separate.
5. P25 `TeePublisher.publish(...)` calls `super().publish(...)` first, then snapshots the same store into the run-nonce-bound status ring.
6. P25 `extract_canonical_status(...)` consumes the maintained canonical surfaces only when the schema is `wof-alpha-canonical-runtime-coordinator-v1`, after which existing safety, exact identity, duplicate/out-of-order and SUPPRESSED/no-coordinate checks remain fail-closed.

Therefore the old `NOT_EXPOSED_BY_STAGED_RUNTIME_STATUS` result is no longer a structural failure of the supported staged path. Current renderer-source qualification may still legitimately be unproven, and P10 may emit coordinate-free `SUPPRESSED/RENDERER_SOURCE_UNPROVEN`; P25 does not upgrade that to visible or coordinate proof.

## 4. Checks and proof boundary

- Python compile: **PASS** on durable tested P25 candidate; current owned blobs are identical.
- Focused composite acceptance fixtures: **PASS**, 11 fixtures on the same tested bytes.
- Forbidden source scan: **PASS** on the same tested bytes.
- Post-P27 supported staged-path committed readback: **PASS**.
- Real WOF acceptance: **NOT_RUN**.
- Owner visual acceptance: **NOT_RUN**.
- `visibleProof=NOT_PROVEN`.

No P22/P24/W3/Owner visual evidence was manufactured. No live dynamic/temporal coverage is claimed by this terminal closeout.

## 5. Ownership and safety

Continuation changed no P25 implementation and did not modify P27/P21/P22/P24/W3/P20/P23 ownership or permanent W1/update paths.

Safety remains:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no legacy spatial fallback
- no screenshot/world-projection production coordinates
- no guessed address/coordinates
- `realWofAcceptance=NOT_RUN`
- `ownerVisualAcceptance=NOT_RUN`
- `visibleProof=NOT_PROVEN`
- `alphaLiveMoved=false`

## 6. Terminal next action

Close the original P25 canonical and stage claims using exact token `1a8e410f279e1450057986f7e8212959`, then set P25 PROGRESS to `TERMINAL/100` only after those claim updates are durable. After P25 is terminal, PM may advance the existing final live acceptance Owner gate; this P25 result itself does not run or claim real WOF/Owner visual acceptance.
