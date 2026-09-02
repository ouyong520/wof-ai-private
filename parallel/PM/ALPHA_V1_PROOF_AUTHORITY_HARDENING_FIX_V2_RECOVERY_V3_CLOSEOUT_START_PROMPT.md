# Alpha V1 Proof-Authority Hardening Fix V2 Recovery V3 Closeout

stageId: `ALPHA_V1_PROOF_AUTHORITY_HARDENING_FIX_V2_RECOVERY_V3_CLOSEOUT`
dedupProtocol: `v2`
dedupKey: `alpha.v1.proof-authority-hardening-fix-v2-recovery-v3-closeout`
dedupMode: `exclusive`

Priority: **P0 release-path closeout**

Repository: `ouyong520/wof-ai-private`

## PM authorization

The Recovery V3 worker has stopped after landing Hardening implementation work, while the Recovery V3 canonical claim is still ACTIVE and no durable terminal RESULT/COMPLETE record is present. This is an explicitly PM-authorized closeout/recovery task. Preserve the old Recovery V3 claim as historical evidence; do not overwrite, delete, steal, or reuse its token.

## Goal

Re-read current `main` and determine whether the already-landed Hardening V2 Recovery V3 implementation is actually complete against its own required scope. This is **not another independent QA round** and must not create a new Fresh-QA verdict.

If the implementation and its implementation-owned regression/evidence are complete, write the durable Recovery V3 successor RESULT and close this closeout claim as COMPLETE, with exact fixed commit/blob pins and the statement that the SUT is ready for the **one final independent Fresh QA**.

If a required Hardening item is still missing, either finish only that missing proof-local implementation item within the original scope or emit a precise BLOCKED result. Do not expand scope.

## Read first

- `parallel/PM/ALPHA_V1_PROOF_AUTHORITY_HARDENING_FIX_V2_RECOVERY_V3_START_PROMPT.md`
- original Hardening V2 prompt
- Cross-check V2 BLOCKED result
- Recovery V3 canonical/stage claims
- latest Hardening implementation commits, including `296a48881137048beb5083b83b2cc11cd404a23d`
- proof-tooling `RUN_MANIFEST.json`
- current implementation-owned regression/evidence
- Final Fresh-QA fixture prep RESULT, but do **not** run it as a Fresh-QA verdict

## Required closeout assertions

Confirm the landed implementation covers the original Hardening V2 scope:

1. trusted/private live signer or authority-root provenance;
2. proofSession + Worker generation + runtime epoch + pair generation + pair nonce binding;
3. capability revocation/reset on authority change;
4. player lifecycle/respawn calibration invalidation;
5. enemy same-slot replacement continuity;
6. enemy type/head-offset lifecycle isolation;
7. current surface/drawing-buffer mapping authority binding;
8. strict primitive finite timestamp/epoch/target validation;
9. stale/replayed transaction rejection;
10. cross-authority evidence cannot aggregate terminal success;
11. public mutable/serialized state cannot force `IMPLEMENTATION_READY`;
12. valid same-authority/same-lifecycle retarget/live flow remains supported;
13. safety remains `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`;
14. `RUN_MANIFEST.json` and every authority-critical blob are repinned to the final fixed implementation.

## No extra test loop

Do not run Formal, Recorder, PYLAUNCH, player-head, enemy-label, OneClick, 5h endurance, Browser/WOF, second-opinion, cross-check, or any new independent QA.

Implementation-owned regression may be run only as needed to prove the Recovery implementation itself is internally complete. The already-prepared 17-case Final Fresh-QA fixture remains reserved for the single future independent Fresh QA after this closeout.

## Success

`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING FIX V2 RECOVERY V3 CLOSEOUT — HARDENED BLOBS PINNED / READY FOR THE ONE FINAL FRESH QA`

The RESULT must include exact final commit/blob pins and clearly identify any historical stale ACTIVE claims as superseded rather than mutating them.

## Failure

`BLOCKED — ALPHA V1 PROOF-AUTHORITY HARDENING FIX V2 RECOVERY V3 CLOSEOUT — <precise missing implementation authority>`

Strict canonical dedup v2. Continue until COMPLETE / BLOCKED / duplicate stop.
