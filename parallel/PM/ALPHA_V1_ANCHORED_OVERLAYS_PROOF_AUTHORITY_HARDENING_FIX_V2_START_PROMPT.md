# Alpha V1 Dual-Overlay Proof-Authority Hardening Fix V2

stageId: `ALPHA_V1_ANCHORED_OVERLAYS_PROOF_AUTHORITY_HARDENING_FIX_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.anchored-overlays.proof-authority-hardening-fix-v2`
dedupMode: `exclusive`

Priority: **P0 proof-integrity implementation fix**

Repository: `ouyong520/wof-ai-private`

## Trigger

Independent Cross-check V2 is durably BLOCKED at commit `eb12405f1d9ee5cfb3054c169daa6f8670503a01`.

Primary blocker:

`self-signed live-witness public key is not pinned to the real Worker, allowing repository JavaScript to mint live capability and serialize synthetic IMPLEMENTATION_READY`.

Secondary authority leaks found by the same cross-check must be addressed in this same narrow proof-local fix because they share the same proof-authority root:

- accepted live capability not bound/revoked on exact Worker/runtime/pair authority changes;
- player calibration can survive player lifecycle replacement;
- same-slot same-type close-position replacement can retain heuristic occupant generation;
- enemy type calibration can survive replacement without explicit authority rules;
- surfaceMappingKey is not cross-checked against current mapping authority;
- proof-core timestamp/epoch coercion or fallback can create fresh-looking authority;
- terminal verdict depends on public mutable state rather than immutable/private attested state.

## Scope

Modify only proof tooling under:

`parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**`

plus this stage RESULT/claims/regressions.

Do not modify:

- `product/alpha/**`;
- danger rules;
- raw target semantics;
- Transport authority;
- gameplay input/AI;
- PYLAUNCH/Recorder/Owner OneClick;
- RAM-write policy.

Do not start Browser/WOF.

## Required repair

1. Replace the self-authenticating witness root. A witness must not be able to choose the verification key that authenticates itself. Root live authority in an identity/key/channel that repository/synthetic JavaScript cannot independently mint, and bind that root to the exact current formal adapter/Worker authority.
2. Bind the accepted live authority to one exact proofSession + Worker generation + runtime epoch + pair generation + pair nonce (+ any required launcher/channel identity). Any later counted event/phase with a different authority must fail closed and require a fresh challenge/rebind.
3. Revoke/reset live capability and bound profile state on Worker/runtime/pair authority change.
4. Player head/body calibration must be valid only for the current player lifecycle at bind/use time; respawn/replacement invalidates old calibration.
5. Enemy retarget scoring must require lifecycle-safe same-occupant continuity. Same-slot same-type close-position replacement must not be silently treated as retarget if continuity cannot be proved.
6. Define and enforce safe enemy type-offset lifecycle rules. If type-global reuse cannot be proven safe, fail closed/reprove rather than carrying authority across replacement.
7. Require surface mapping authority used by the helper/draw event to equal the current drawing-buffer/mapping authority when an anchored event is counted.
8. At proof scoring boundaries, timestamps/epochs/target values must use strict primitive validation. Invalid `warningSampleAt` or epoch must not fall back to another timestamp or `Date.now()` to become fresh-looking evidence.
9. Terminal `IMPLEMENTATION_READY` must be recomputed from private/immutable attested state. Public mutable objects, serialized fixtures, candidate payloads or direct Session property mutation must not be sufficient to upgrade evidence.
10. Preserve read-only boundaries: `ramWrites=0`, `inputInjection=false`, no Worker replacement, no Blob rewrite, no production profile activation from repository/synthetic evidence.
11. Repin `RUN_MANIFEST.json` to exact fixed blobs.

## Required deterministic regression

Add independent-style regression cases proving at least:

- attacker-owned P-256 key cannot self-sign into live authority;
- forged/synthetic repository Session cannot mint the live capability;
- old capability is revoked on Worker/runtime/pair change;
- cross-authority phases cannot aggregate across time into one terminal PASS;
- respawn between calibration and bind/use invalidates calibration;
- same-slot same-type close replacement is not counted as retarget unless continuity is proven;
- stale enemy calibration does not survive an unsafe lifecycle replacement;
- stale/old `surfaceMappingKey` fails closed;
- malformed/coercible timestamp/epoch does not become fresh authority;
- public state mutation cannot force `IMPLEMENTATION_READY`;
- normal valid same-occupant retarget and valid live-authority flow still work;
- all safety flags remain exact.

Implementation selftests are supportive only for the later independent QA, but this fix must leave deterministic repository regression evidence.

## Dedup

Strict canonical dedup v2. Re-read current `main`, the Cross-check V2 BLOCKED result, relevant claims and current proof blobs before claiming. If an equivalent current fix already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`; if already claimed, stop duplicate-safe.

## Success

`COMPLETE — ALPHA V1 DUAL-OVERLAY PROOF-AUTHORITY HARDENING FIX V2 — LIVE ROOT / AUTHORITY REVOCATION / LIFECYCLE / TERMINAL FALSE-PROOF PATHS CLOSED — READY FOR ONE FRESH QA`

## Failure

`BLOCKED — ALPHA V1 DUAL-OVERLAY PROOF-AUTHORITY HARDENING FIX V2 — <precise blocker>`
