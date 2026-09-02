# Alpha V1 Dual-Overlay Proof-Authority Fix — Independent Cross-check V2 Result

## Verdict

**BLOCKED — ALPHA V1 DUAL-OVERLAY PROOF-AUTHORITY FIX INDEPENDENT CROSS-CHECK V2 — self-signed live-witness public key is not pinned to the real Worker, so repository JavaScript can mint the internal live capability and serialize synthetic evidence as `IMPLEMENTATION_READY`.**

## Scope / independence

- Repository-only cross-check. Browser/WOF was not launched.
- Production / implementation files were not modified.
- The implementation regression, Fresh QA fixture, and Fresh QA verdict were not used as proof.
- Audited current-head implementation snapshot: `6bed94ed5a21bbbfc95afbb1b281fc5b590aa77e`.
- Canonical independent-validation slot: `second-opinion-v2` under group `alpha.v1.dual-overlay.proof-authority-fix-v1`.

## Deterministic blocker A — unpinned self-signed live witness

Current `proof_core.js` accepts a live witness as follows:

1. Top creates a random `proofSessionId` and challenge nonce using `Session.beginLiveWitness()`.
2. `Session.acceptLiveWitness(w)` checks only that the challenge/session fields match, that `w.authority` is syntactically valid, and that an ECDSA signature verifies.
3. The verification key is **`w.publicKey` supplied by the same untrusted witness message**.
4. There is no pinned Worker public-key fingerprint, no attested key derivation from the formal adapter tuple, and no independent comparison of that public key to the Worker that produced current snapshots.
5. On successful verification, `acceptLiveWitness()` creates a `capBrand` capability and sets `browserWofActuallyRun=true` / `liveWorkerWitnessVerified=true`.

The BroadcastChannel challenge is observable by repository JavaScript running in the same execution environment. A synthetic repository script can therefore:

- observe or obtain `{proofSessionId, nonce}`;
- generate its own P-256 ECDSA key pair;
- fabricate any syntactically valid authority tuple (`session`, `runtimeEpoch`, `pairGeneration`, `pairNonce`, fixed launcher SHA, matching `channel`);
- sign `WOF_ALPHA_DUAL_LIVE_V1|...` with its own private key;
- supply its own public key in the witness object;
- have `acceptLiveWitness()` verify the self-issued signature and mint the branded capability.

No real Worker private key or live Browser/WOF execution is required by that acceptance equation. This defeats the primary fix objective: repository/synthetic evidence can still obtain the internal live capability.

### Why the branded `WeakSet` is not sufficient

The `WeakSet` prevents a plain JSON object from masquerading directly as the capability, but the only minting gate for a new branded object is the self-signed witness flow above. Because the signer identity is not independently trusted, the capability brand roots to signature self-consistency rather than real-Worker provenance.

## Deterministic blocker B — accepted capability is not bound to later event authority

Even when the first witness is assumed honest, `Session` stores the accepted authority tuple privately but later phase scoring does not require event authority tuples to equal that accepted authority.

- `authorityTuple(event)` validates internal equality of runtime / projection / drawing-buffer epochs and mapping key.
- `markWindow()` requires player/enemy events in a joint phase to have equal event tuples.
- Neither path compares the event tuple's runtime epoch to the authority stored by `acceptLiveWitness()`.
- `hasLiveWitness()` remains true for the lifetime of the Session; there is no Worker-generation/runtime-epoch/pair-nonce revocation or expiry hook.
- Top's `bound` flag similarly remains true after it is set and is not invalidated on a changed Worker binding tuple.

Therefore an old live capability can continue authorizing scoring after a Worker/runtime/pair authority change, as long as the new surface events are internally epoch-consistent. This permits cross-generation/cross-runtime evidence aggregation inside one terminal proof session.

## Deterministic blocker C — player calibration is not bound to the current player lifecycle at bind time

Top records `body.lifecycleId` and `body.headLifecycleId` at calibration time. `playerProfile()` verifies that those two stored values equal each other, but it does not compare either value to the **current** P1 lifecycle from the Worker snapshot when `bind()` is later executed.

Consequences:

- a P1 respawn/replacement may correctly advance Worker lifecycle generation;
- the old `body` calibration object remains stored;
- a later `bind()` can still pass `playerProfile()` because the two old lifecycle fields remain equal to each other;
- the emitted player projection profile does not carry an active lifecycle binding that would revoke it on subsequent respawn.

Thus old head/body calibration can survive player lifecycle replacement.

## Additional attack-matrix findings

| Attack | Cross-check result |
|---|---|
| repository/synthetic JSON/event stream forges live capability | **BYPASS — BLOCKER A** |
| witness replay across proof session | direct nonce/session replay is rejected, but signer provenance itself is forgeable |
| Worker generation / runtime epoch / pair nonce replay | **BYPASS — BLOCKER B** |
| malformed/partial witness | ordinary missing fields fail closed; does not repair unpinned signer root |
| player epoch A + enemy epoch B in one joint `markWindow` call | rejected by `sameAuthorityTuple`; however final proof can aggregate different accepted epochs across time because no global witnessed-authority binding exists |
| same-slot replacement masquerading as retarget | **not authority-safe**: Worker lifecycle identity is heuristic (present/type/time/coordinate discontinuity); a same-type, close-position replacement with no sampled absent frame can retain generation and then satisfy retarget continuity |
| player respawn preserves calibration | **BYPASS — BLOCKER C** |
| enemy type offset survives occupant replacement | profile is emitted as type-global `enemyHeadOffsetsByType`; after rooted bind there is no per-current-occupant lifecycle binding in the profile, so replacement does not itself revoke the type offset |
| stale stop/reinstall without exact transaction witness | official `acceptAuthorityGapWitness()` checks proof session, exact authority text, signature, request/transaction IDs, timing and one-use transaction IDs; however a forged root signer from Blocker A can also mint the required signed transaction witness |
| old drawing-buffer/mapping + fresh evidence | proof event stores both `mappingKey` and `surfaceMappingKey`, but `authorityTuple()` validates only `mappingKey`; it does not require the helper-produced surface mapping key to equal the current drawing-buffer mapping authority |
| malformed/coercible `warningSampleAt` | production player helper is strict; proof-core `sample()` is not: invalid values fall back to the secondary timestamp or `Date.now()`, and `warningSampleAtRaw` is not part of authority tuple/verdict |
| malformed/coercible target | current production enemy helper is strict and `enemyEvents()` only recognizes primitive integer 0/4/8; direct synthetic Session events are not semantically revalidated by `verdict()` |
| malformed/coercible epoch | helper conversion is mostly strict, but `authorityTuple()` uses `String(...)` before the 32-hex test, so direct synthetic event objects can provide coercible epoch values |
| terminal serialization upgrades synthetic evidence | **BYPASS**: `terminal()` always emits the real-live evidence class and `shape()` performs structural checks only; it does not independently re-attest provenance or reject a synthetic boundary |
| RUN_MANIFEST stale blob | no post-fix selected implementation-file drift was seen in `e604274... -> 6bed94e...`; current fetched core/top/worker/dual-loader/player-helper/enemy-helper blob SHAs match `RUN_MANIFEST.json`. The manifest check therefore does not cause this BLOCKED verdict |
| readOnly / RAM writes / gameplay input injection | **boundary retained in inspected proof path**: proof Worker reads HEAP through read helpers; no RAM write/input-injection path was found; production real Worker declares `readOnly:true`, `ramWrites:0`, `inputInjection:false` |

## Minimal false-proof construction

The decisive construction does not require a Browser/WOF run:

1. Instantiate the exported proof `Session`.
2. Call `beginLiveWitness()` to obtain its challenge.
3. Generate an attacker-owned ECDSA P-256 key pair.
4. Create a syntactically valid authority tuple and sign the exact live-witness text with the attacker private key.
5. Call `acceptLiveWitness()` with the attacker public key and signature. The method accepts and mints a branded capability because it verifies against the supplied public key.
6. The Session's scoring/state objects (`bind`, `phases`, `authority`, `visual`) are public mutable objects, while `terminal()` / `verdict()` do not independently reconstruct provenance from a trusted Worker transcript.
7. Synthetic state can therefore be serialized with the real-live evidence class and can reach the `IMPLEMENTATION_READY` terminal label after the public state gates are populated.

This construction is sufficient to stop the stage as BLOCKED; the secondary lifecycle/epoch/mapping findings above strengthen the blocker but are not required for the verdict.

## Required repair direction

A successor fix needs a non-self-authenticating root of trust and end-to-end authority binding. At minimum:

- Top must verify the live witness against a Worker key/identity that the witness message itself cannot choose (or against another non-forgeable channel rooted in the current formal adapter authority).
- The accepted live witness must bind one exact Worker generation + runtime epoch + pair generation + pair nonce, and all later counted event/phase tuples must equal that authority or force re-challenge/rebind.
- Player calibration and enemy type calibration must be revoked/reproved on relevant lifecycle replacement.
- `surfaceMappingKey` must be cross-checked against current mapping authority where a surface anchor is scored.
- Proof-core timestamps/epochs must remain primitive/strict at the scoring boundary; malformed values must not be replaced with fresh timestamps.
- Terminal verdict must be recomputable from immutable/privately-held attested state rather than public mutable scoring objects.

## Stop condition

`BLOCKED — ALPHA V1 DUAL-OVERLAY PROOF-AUTHORITY FIX INDEPENDENT CROSS-CHECK V2 — self-signed live-witness public key is not pinned to the real Worker, allowing repository JS to mint live capability and serialize synthetic IMPLEMENTATION_READY.`
