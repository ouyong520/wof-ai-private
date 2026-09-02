# Alpha V1 Proof-Authority Hardening Fix V2 Recovery V3 Closeout Result

## Verdict

**BLOCKED — ALPHA V1 PROOF-AUTHORITY HARDENING FIX V2 RECOVERY V3 CLOSEOUT — hardened `proof_core.js` was landed, but current Top/Worker/regression/manifest remain on the pre-Hardening authority-v1 contract and no non-self-authenticating live-signer root is wired into the runnable proof path.**

This is a Recovery V3 closeout finding, not a Final Fresh-QA verdict. No Browser/WOF, Formal, Recorder, PYLAUNCH, player-head, enemy-label, OneClick, endurance, second-opinion, cross-check, or prepared Final Fresh-QA fixture was run.

## Current-main / implementation pin

Closeout re-read current `main` after canonical ownership. The last semantic Hardening implementation commit is:

- `296a48881137048beb5083b83b2cc11cd404a23d` — `Alpha proof: harden private authority root and scoring`

The only commits after it at closeout inspection were PM closeout metadata (`607cc05e48d8166e368300ecb6076280de3d11c3`, `6e41cb6cd7e88e89ddac25486780bdf2861e7b19`, `429cc791954d50f6ad40ab1fcbbde5f65b4c865f`). No later proof implementation change was present.

Current authority-critical proof blobs inspected:

- `proof_core.js`: `03eb65d431996fd054683104940300d40db0e60e`
- `wof_alpha_v1_dual_live_proof_top.js`: `e0e686cafc3463ce6041d83c5e0fe1030f7eb444`
- `wof_alpha_v1_dual_live_proof_worker.js`: `2b75092fee63cecafb51e108aa2af8b3d83cc696`
- `wof_alpha_v1_dual_live_proof.js`: `e71a802c8d150cf727345c51c4786512a82abb97`
- `proof_authority_regression.mjs`: `e3697ab88cb36922e717b7a85044e0bfca72a444`
- `RUN_MANIFEST.json`: `aed5740697cdeecb55aa3736faff98ddd08033c9`

## What `296a488...` did complete in the core

The landed core contains substantial Hardening V2 work:

- exact authority tuple includes proof session binding plus `workerGeneration`, runtime epoch, pair generation and pair nonce;
- signer fingerprint pin support and private branded capability metadata;
- capability revocation / private evidence reset on authority change;
- strict primitive finite epoch/sample/target scoring boundaries;
- current player lifecycle binding and enemy lifecycle/type/slot isolation in profile construction;
- drawing-buffer mapping authority plus exact surface mapping-key comparison;
- one-use, signed, time-bounded authority-gap transaction acceptance;
- cross-authority events excluded from private scoring;
- terminal verdict recomputed from private state rather than public mutable scoring copies;
- exact safety gate requires `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`;
- same-authority/same-lifecycle retarget scorer remains represented in the hardened core.

Those are implementation changes, not an independent QA verdict.

## Blocking integration defects

### 1. Trusted signer provenance is not runnable and the old self-signed root remains in Worker

The current Worker still generates its own fresh P-256 key pair inside the proof script and sends the matching public key in the same witness message. It therefore remains self-authenticating unless an independently trusted fingerprint/root is supplied from outside that witness path.

The hardened core correctly refuses to create a challenge until `pinTrustedSigner(...)` and `observeAuthority(...)` establish such authority. But current Top never supplies that trusted root.

A proof-local rewrite that merely accepts the Worker's own announced fingerprint would reproduce the Cross-check V2 blocker and is not an acceptable closeout repair. The repository currently exposes no already-authoritative private signer/attestation primitive that this proof-local Top/Worker pair can consume without changing the external authority root.

### 2. Top is incompatible with the hardened core contract

Current Top calls `s.beginLiveWitness()` immediately after constructing `Session`. Under `296a488...`, that call requires both a valid trusted signer pin and an observed exact authority, so the current runnable path fails closed before a live challenge can be created.

Current Top also does not wire the new mandatory core operations/inputs into the live path:

- no trusted signer pin setup;
- no exact `observeAuthority(...)` lifecycle;
- no authority-change challenge/capability regeneration;
- no `observeRuntimeSafety(...)` feed;
- no `observeLifecycles(...)` invalidation feed;
- no `confirmProfileBinding(...)` call;
- event context does not carry the exact accepted authority;
- profile construction does not provide the required current lifecycle/current enemy/authority inputs.

Consequently the hardened private-state terminal path cannot reach a legitimate positive terminal state through current Top.

### 3. Worker is incompatible with authority V2

Current Worker authority still contains only:

`session / runtimeEpoch / pairGeneration / pairNonce / launcherIdentitySha / channel`

It does not publish the hardened core's required `workerGeneration` field. It also still signs `WOF_ALPHA_DUAL_LIVE_V1` / `WOF_ALPHA_DUAL_GAP_V1`, while the hardened core verifies `..._V2` texts containing the expanded authority tuple.

Thus current Worker witnesses cannot satisfy current core even aside from the signer-root problem.

### 4. Same-slot replacement continuity is still only the old heuristic in Worker

The current Worker lifecycle generation advances on absence, type change, timeout, or large coordinate discontinuity. A same-slot, same-type, near-position replacement with no sampled absent frame can therefore retain the old generation. The hardened core can consume stronger continuity fields, but current Worker does not establish a non-heuristic replacement continuity token/authority sufficient to close this original requirement.

### 5. Implementation-owned regression/evidence is stale for the hardened contract

`proof_authority_regression.mjs` remains the earlier authority-v1 regression. It does not exercise the new trusted-pin/observed-authority/worker-generation contract and its event fixtures omit current authority/mapping requirements needed by the hardened private scorer. It therefore cannot serve as current implementation-owned regression evidence for Recovery V3 completion.

No new regression loop was started after this deterministic incompatibility was established.

### 6. `RUN_MANIFEST.json` is stale and cannot be truthfully repinned as a final fixed manifest

Current manifest still declares:

- schema `...proof-authority-fix-v1`;
- `implementationCommit` = `e6042741486ed6aae215e282c2f700fd84167811`;
- `dualCore` = `6fa5b5178dd0dedcad2afe7e53c6cdda98c8a701`.

Current hardened `proof_core.js` is blob `03eb65d431996fd054683104940300d40db0e60e`, so the manifest is already stale against current SUT. Because Top/Worker/regression are not yet a complete fixed candidate, repinning the manifest now would incorrectly certify an incomplete authority generation; it is intentionally left unchanged.

## Required closeout assertion matrix

| Requirement | Closeout status |
|---|---|
| 1. trusted/private live signer or authority-root provenance | **BLOCKED** — no non-self-authenticating root wired into runnable Top/Worker |
| 2. proofSession + Worker generation + runtime epoch + pair generation + pair nonce | **BLOCKED integration** — core models it; Worker omits `workerGeneration` and uses V1 signed text |
| 3. capability revocation/reset on authority change | core implemented; **not wired by Top** |
| 4. player respawn/calibration invalidation | core implemented; **not wired by Top lifecycle feed/binding** |
| 5. enemy same-slot replacement continuity | **BLOCKED** — Worker still uses old heuristic continuity |
| 6. enemy type/head-offset lifecycle isolation | core implemented; **not wired by current Top profile inputs** |
| 7. surface/drawing-buffer mapping authority | core implemented; current live events lack complete authority integration |
| 8. strict primitive finite timestamp/epoch/target | core implemented |
| 9. stale/replayed transaction rejection | core implemented; Worker remains V1 witness contract |
| 10. cross-authority evidence cannot aggregate | core private scorer implemented; positive live path not integrated |
| 11. public mutable/serialized state cannot force `IMPLEMENTATION_READY` | core private terminal state implemented |
| 12. valid same-authority retarget/live flow supported | core scorer exists; **current Top/Worker cannot satisfy its authority contract** |
| 13. exact safety invariants | core gate exists; **Top never supplies safety observation** |
| 14. final manifest/authority-critical blob repin | **BLOCKED** — no complete fixed candidate exists to pin |

## Final Fresh-QA fixture handling

The prepared Final Fresh-QA fixture result at `df752acd3849cb23980856ee47324f2beab853ab` was read only as required. Its 17-case oracle remains reserved and was not executed against this SUT. This closeout does not consume the one final Fresh-QA slot.

## Claim preservation / supersession semantics

Historical ACTIVE claims are preserved unchanged as abandonment residue, including:

- original Hardening V2 canonical claim `alpha.v1.anchored-overlays.proof-authority-hardening-fix-v2`;
- Recovery V3 canonical/stage claim with token `9a22f4c1e05363ff07a8d105da2c5a37035a18ea4a6f6262`.

This closeout does not overwrite, delete, reuse, or claim ownership of those tokens. They are historical residue; this successor closeout result is the durable current status for the stopped Recovery V3 attempt.

## Stop condition

**BLOCKED — ALPHA V1 PROOF-AUTHORITY HARDENING FIX V2 RECOVERY V3 CLOSEOUT — trusted signer provenance plus Top/Worker authority-v2 integration and current implementation regression/manifest are incomplete.**

`READY FOR THE ONE FINAL FRESH QA` is **not** authorized by this closeout state.
