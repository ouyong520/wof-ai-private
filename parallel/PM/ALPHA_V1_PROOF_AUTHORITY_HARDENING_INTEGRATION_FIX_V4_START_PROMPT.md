# Alpha V1 Proof-Authority Hardening Integration Fix V4

stageId: `ALPHA_V1_PROOF_AUTHORITY_HARDENING_INTEGRATION_FIX_V4`
dedupProtocol: `v2`
dedupKey: `alpha.v1.proof-authority-hardening-integration-fix-v4`
dedupMode: `exclusive`

Priority: **P0 narrow implementation fix**

Repository: `ouyong520/wof-ai-private`

## PM authorization / predecessor

Recovery V3 closeout is durably BLOCKED by:

`parallel/PM/RESULTS/ALPHA_V1_PROOF_AUTHORITY_HARDENING_FIX_V2_RECOVERY_V3_CLOSEOUT_RESULT.md`

The predecessor landed hardened core commit:

`296a48881137048beb5083b83b2cc11cd404a23d`

but the runnable proof path remains split between hardened core authority-v2 and old Top/Worker authority-v1 integration.

This stage is PM-authorized successor implementation work. Do not overwrite/delete/reuse predecessor claims or tokens.

## Goal

Complete the runnable proof-authority integration so the current proof Top / Worker / loader / regression / manifest all use the same hardened authority-v2 contract and the proof path has a non-self-authenticating trusted signer/authority root.

This is implementation, not Fresh QA.

## Required fixes

1. **Trusted signer / authority-root provenance**
   - remove the runnable self-authentication path where Worker can mint its own key and have Top trust that same witness-provided key;
   - wire an independently trusted proof/live signer fingerprint or authority root into the proof path;
   - fail closed if the trusted root is absent, malformed, stale, mismatched, or originates only from the same witness being authenticated;
   - do not simply pin the Worker's own announced fingerprint.

2. **Top authority-v2 integration**
   - pin trusted signer/root before challenge issuance;
   - call exact `observeAuthority(...)` with proof session + workerGeneration + runtime epoch + pair generation + pair nonce authority;
   - revoke/regenerate challenge/capability after authority changes;
   - wire `observeRuntimeSafety(...)`;
   - wire `observeLifecycles(...)`;
   - wire `confirmProfileBinding(...)`;
   - carry exact accepted authority into event/scoring context;
   - provide current player lifecycle / enemy lifecycle / authority inputs required by hardened profile construction.

3. **Worker authority-v2 contract**
   - publish strict primitive positive `workerGeneration`;
   - sign/verify V2 witness/gap texts using the expanded exact authority tuple;
   - ensure runtime epoch / pair generation / pair nonce / worker generation transitions revoke old proof authority;
   - reject malformed/coercible authority fields.

4. **Enemy same-slot replacement continuity**
   - close the same-slot / same-type / near-position replacement hole without relying solely on absence/type/timeout/large-position heuristic;
   - establish an authority/lifecycle continuity token or equivalent fail-closed mechanism sufficient to prevent replacement from inheriting old retarget/calibration authority;
   - if continuity cannot be proved, invalidate old lifecycle/calibration rather than guessing continuity.

5. **Lifecycle / calibration binding**
   - player respawn/replacement invalidates old player calibration;
   - enemy calibration/type offset cannot cross lifecycle;
   - same-authority normal retarget within one proven lifecycle remains valid.

6. **Surface / drawing-buffer mapping authority**
   - current Top event path must carry exact current authority and mapping key expected by hardened core;
   - stale or cross-epoch mapping must fail closed.

7. **Implementation-owned regression**
   - update current implementation regression to authority-v2 behavior;
   - cover trusted-root rejection, workerGeneration binding, authority change revocation, lifecycle invalidation, same-slot replacement fail-closed, mapping authority, strict primitive timestamp/epoch/target, replay rejection, mutable-state false terminal prevention, and valid same-authority retarget/live flow;
   - this regression is supportive implementation evidence only and must not consume the one Final Fresh QA.

8. **RUN_MANIFEST**
   - only after runnable Top/Worker/core/regression form one coherent fixed candidate, repin `RUN_MANIFEST.json` to exact current authority-critical blobs and implementation commit;
   - do not certify an incomplete candidate.

9. **Safety boundaries**
   - exact required safety remains:
     `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`;
   - no Browser/WOF launch.

## Scope

Allowed:

- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**`
- proof-local tests/regression/manifest
- PM/result/claim metadata for this stage

Forbidden:

- `product/alpha/**`
- danger rules
- target semantics
- Transport
- PYLAUNCH
- Recorder
- OneClick runtime
- input/AI
- Browser/WOF
- Final Fresh QA fixture modifications

Do not rerun Formal / Recorder / PYLAUNCH / player-head / enemy-head / 5h / OneClick QA.

## Completion requirement

Do not claim completion from hardened `proof_core.js` alone.

Completion requires one coherent runnable authority-v2 candidate across core + Top + Worker + loader as applicable + implementation regression + final RUN_MANIFEST, with a durable RESULT identifying exact blobs/commit.

Success:

`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING INTEGRATION FIX V4 — RUNNABLE AUTHORITY-V2 TOP/WORKER/TRUST ROOT/LIFECYCLE/MANIFEST INTEGRATED — READY FOR THE ONE FINAL FRESH QA`

Failure:

`BLOCKED — ALPHA V1 PROOF-AUTHORITY HARDENING INTEGRATION FIX V4 — <precise blocker>`

Strict canonical dedup v2. Stop duplicate-safe if equivalent successor integration work is already COMPLETE or ACTIVE.
