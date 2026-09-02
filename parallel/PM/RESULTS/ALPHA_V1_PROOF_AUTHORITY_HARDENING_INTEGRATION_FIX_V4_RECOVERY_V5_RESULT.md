# Alpha V1 Proof-Authority Hardening Integration Fix V4 Recovery V5 — RESULT

`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING INTEGRATION FIX V4 RECOVERY V5 — AUTHORITY-V2 RUNNABLE PATH / TRUST ROOT / LIFECYCLE / MANIFEST COHERENT — READY FOR THE ONE FINAL FRESH QA`

## Scope / authority

This was the PM-authorized stale-worker recovery for Integration Fix V4. Recovery V5 used its own canonical dedup key and token. The historical V4 ACTIVE canonical/stage claim was intentionally left untouched.

Recovery V5 did **not** run Final Fresh QA, Browser/WOF, historical PASS QA, second-opinion/cross-check, or supportive recovery regression. It did **not** modify `product/alpha/**`, danger rules, target semantics, Transport, Recorder, PYLAUNCH, OneClick, input/AI, or production profiles.

## Coherent authority-v2 candidate

Implementation candidate commit:

`dec5ffd9b1c3d29559d3af47b200ef7b2f71e4cf`

Manifest repin commit:

`cd19b462e31f7464669471e73b651843e5c716c9`

Manifest blob:

`f61abf058b997ed76a3d54e7e27ac0e017fa67a9`

Exact critical pins:

- authority-v2 external trust contract: `5a9a842e1dfac4fa98564ad6034eaa8439cee03a`
- proof core: `2ae605748728316f9b477bd057c19abb9da4998c`
- Top observer: `d0b8d0b833e9478c9e7ad67328d1312bf3642ad4`
- Worker observer: `e739d5b132cd8177148ff2e5e24f868dc656f971`
- authority-v2 loader: `be3c108ce76a6c9d9ada9a8a285886b70fdde692`
- implementation-owned authority-v2 regression: `f93abb13c59053df4b76df1085fb27e188abf314`
- HUDANCHOR loader/top/worker/gl remain exactly `8e7a72eb14556f181e4322825e98f7ac57f8eed5` / `95ae41bfb39b42deb1fee267f27da7b13a4b622c` / `12f06e40fb457963b082813607eec05e71bf7951` / `e4f91799ecc2204c68894d25056c5d6b747bfaec`
- live-proof evidence schema remains `f9213012502b4a307e6cab0df23fbe9f5812f769`

All manifest-selected `product/alpha/**` blobs were read-only checked against current `main` and remained unchanged.

## Implementation-owned authority-v2 regression

Only the implementation-owned regression was run:

`node parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/proof_authority_regression.mjs`

Final exact result on the exact pinned candidate blobs:

`PASS — 11 / 11 authority-v2 implementation regression`

Covered implementation assertions:

1. trusted-root mismatch rejects a witness signed by a different self-generated key;
2. workerGeneration/runtimeEpoch/pairGeneration/pairNonce authority change revokes old capability/challenge state;
3. normal same-authority retarget remains scoreable only inside one lifecycle;
4. same-slot replacement lifecycle cannot be scored as retarget continuity;
5. cross-epoch drawing-buffer mapping and coercible epoch fail closed;
6. `warningSampleAt` requires primitive finite number and target7E requires primitive exact type/value;
7. player respawn and enemy lifecycle replacement invalidate old calibration/profile authority;
8. signed authority-gap transaction is fresh, same-authority and one-shot; stale/replay is rejected;
9. public mutable/serialized state cannot force terminal `IMPLEMENTATION_READY`;
10. runnable Top/Worker/loader/contract sources use authority-v2 and contain no Worker self-key generation/self-authentication path;
11. authority-v2 contract rejects coercible authority and stale/mutable trust roots.

## Recovery-local closeout fixes discovered by the owned regression

Two proof-local issues had to be corrected before closeout; neither touched production code.

- The expanded implementation regression had a deterministic destructuring typo in its second test (`liveSession()` returns `{s,...}` while the test destructured `{x:s,...}`). This was corrected in commit `6375d8d8be81526500b28b7c9cee6580bee9487a`.
- The regression then exposed a real strict-authority defect: `proof_core` used JSON stringify/parse as its event clone boundary, which could launder boxed/coercible values (for example a boxed epoch) into primitive values before private authority scoring. The proof-local clone boundary now preserves primitive exactness, rejects non-plain wrappers, and public event copies are separated from the private scoring event. Final correction is in candidate commit `dec5ffd9b1c3d29559d3af47b200ef7b2f71e4cf`.

The full 11/11 regression was rerun from the beginning only after those two corrections.

## Authority-v2 closeout assertions

| Requirement | Result | Durable implementation fact |
| --- | --- | --- |
| Independent trusted signer/root | PASS | Top consumes an independently provisioned immutable trust root; Worker consumes an independently provisioned immutable signer provider. Worker does not call `generateKey()` or authenticate a key it just announced. |
| External trust candidate binding | PASS | trust root and signer provider are candidate-commit pinned and freshness bounded; loader requires the role-appropriate rooted provider before loading the observer. |
| proofSession / workerGeneration / runtimeEpoch / pairGeneration / pairNonce | PASS | live witness/capability and gap witness are bound to the exact authority tuple; any authority change invalidates prior capability/evidence, and worker-generation change also requires a fresh signer pin/challenge. |
| Cross-authority aggregation | PASS | private scoring accepts events only under the current exact authority and phase pairing requires the same authority tuple/surface mapping; old/cross authority events cannot compose terminal success. |
| Player respawn | PASS | player calibration/profile is lifecycle-id + lifecycle-generation bound and is cleared/rejected when current player lifecycle changes. |
| Enemy replacement / same-slot continuity | PASS | lifecycle authority carries generation + token; continuity resets on replacement and retarget scoring requires monotonically continuous samples in the same lifecycle. |
| Enemy type-offset lifecycle isolation | PASS | enemy calibration requires one unique current stable lifecycle for the type and exact lifecycle-generation-slot match; replacement or ambiguity fails closed. |
| Drawing-buffer/surface mapping authority | PASS | runtime/projection/drawing-buffer/drawing-buffer-projection epochs must be strict and equal; anchored scoring also requires the actual surface mapping key to equal the expected current mapping key. |
| Strict epoch / warningSampleAt / target | PASS | epochs are strict primitive hex strings; `warningSampleAt` is primitive finite and ordered before the spatial sample; target7E is primitive finite integer exact 0/4/8 with label/target consistency. |
| Stale/replay transaction evidence | PASS | signed gap witness is time bounded, same-authority, one-shot by transaction id, and requires both player fixed fallback and enemy suppression evidence from the matching transaction window. |
| Private terminal state | PASS | authoritative scoring state/capability metadata remains private via WeakMap/WeakSet; public/serialized copies cannot mutate the private terminal gate into `IMPLEMENTATION_READY`. |
| Safety | PASS | exact accepted runtime safety is `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`; any deviation fails the safety boundary. |
| Manifest | PASS | `RUN_MANIFEST.json` is now authority-v2 schema and pins the exact coherent candidate plus all current critical blobs. |

## Boundary statement

Recovery V5 establishes only repository-side implementation readiness for the **one final independent Fresh QA**. It does not itself provide that Fresh QA verdict and does not claim Browser/WOF live acceptance.

`READY FOR THE ONE FINAL FRESH QA`
