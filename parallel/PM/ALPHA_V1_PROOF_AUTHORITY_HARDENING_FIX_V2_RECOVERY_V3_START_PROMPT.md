# Alpha V1 Proof-Authority Hardening Fix V2 Recovery V3

stageId: `ALPHA_V1_PROOF_AUTHORITY_HARDENING_FIX_V2_RECOVERY_V3`
dedupProtocol: `v2`
dedupKey: `alpha.v1.proof-authority-hardening-fix-v2-recovery-v3`
dedupMode: `exclusive`

Priority: **P0 recovery — sole pre-live blocker**

Repository: `ouyong520/wof-ai-private`

## PM recovery authorization

The original Proof-Authority Hardening Fix V2 worker is no longer running, but its original canonical claim remains ACTIVE. This Recovery V3 is explicitly authorized to resume the unfinished logical work without overwriting, deleting, reusing, stealing, or mutating the original canonical/stage claim.

The old claim remains historical evidence. Recovery V3 must use its own new canonical dedup key and claim token.

## Goal

Re-read current `main`, the original Hardening V2 prompt, Cross-check V2 BLOCKED result, original ACTIVE claim, all proof-tooling files, and any durable partial implementation evidence. Resume only the unfinished Hardening V2 implementation and close it COMPLETE or BLOCKED.

Do not repeat already-completed PM prep work. In particular, the independent Final Fresh-QA fixture prep is already COMPLETE and must not be rerun by this implementation recovery.

## Required hardening scope

Close the existing proof-authority defects, including:

- trusted live witness / signer provenance rooted outside repository-controlled self-assertion;
- exact binding to proof session, Worker generation, runtime epoch, pair generation and pair nonce;
- capability revocation when any authority component changes;
- lifecycle-bound player calibration and respawn invalidation;
- lifecycle-safe enemy same-slot continuity / replacement handling;
- enemy calibration/type-offset lifecycle isolation;
- surface/drawing-buffer mapping authority binding;
- strict primitive validation for epoch, warningSampleAt and target where proof scoring consumes them;
- stale/replayed transaction evidence rejection;
- terminal IMPLEMENTATION_READY not forceable through public mutable/serialized state;
- cross-authority evidence cannot aggregate into terminal success;
- valid same-authority retarget/live flow still works;
- safety boundaries stay exact: readOnly=true, ramWrites=0, inputInjection=false, workerReplacement=false;
- repin RUN_MANIFEST and all authority-critical blobs.

## Scope boundaries

Modify only proof-tooling-local files under:
`parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**`
plus recovery RESULT/claims/regression evidence required by this recovery.

Do NOT modify:
- `product/alpha/**`;
- danger rules;
- raw target semantics;
- Transport authority;
- gameplay input/AI;
- PYLAUNCH / Recorder / Owner OneClick runtime;
- RAM-write policy.

Do not start Browser/WOF.

## Regression expectation

Implementation-owned regression is required for the repaired paths, but it is supportive evidence only. Do not consume or alter the independent 17-case Final Fresh-QA oracle as implementation authority.

## Completion

Success:
`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING FIX V2 RECOVERY V3 — ORIGINAL STOPPED WORK RECOVERED / FALSE-PROOF AUTHORITY PATHS CLOSED — READY FOR THE ONE FINAL FRESH QA`

Failure:
`BLOCKED — ALPHA V1 PROOF-AUTHORITY HARDENING FIX V2 RECOVERY V3 — <precise blocker>`

On COMPLETE, publish exact fixed commit/blob pins and leave the original Hardening V2 ACTIVE claim untouched as historical stale residue. The next and only QA step is the already-prepared single Final Fresh Independent QA.

Strict canonical dedup v2. If equivalent PM-authorized recovery is already ACTIVE or COMPLETE, duplicate-stop.