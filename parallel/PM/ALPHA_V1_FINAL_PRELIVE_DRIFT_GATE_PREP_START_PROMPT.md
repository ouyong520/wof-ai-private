# Alpha V1 Final Pre-Live Narrow Drift Gate Prep

stageId: `ALPHA_V1_FINAL_PRELIVE_DRIFT_GATE_PREP`
dedupProtocol: `v2`
dedupKey: `alpha.v1.final-prelive-drift-gate-prep`
dedupMode: `exclusive`

Priority: **P0 release-path acceleration / pre-live gate preparation**

Repository: `ouyong520/wof-ai-private`

## Context

Current-head readiness reconciliation has already determined:

- Owner OneClick V4 immutable candidate is CLOSED/current;
- Formal / Recorder / PYLAUNCH / player-head / enemy-head repository QA gates are already CLOSED;
- Proof-Authority Hardening Fix V2 is the only substantive pre-live implementation blocker;
- after Hardening V2 closes, exactly one final independent Fresh QA must PASS;
- after that PASS, only a **narrow no-drift / no-new-blocker recheck** is required before `START BOUNDED REAL WOF ACCEPTANCE`.

This task prepares that narrow final gate now. It must not authorize live testing before its prerequisites actually exist.

## Goal

Create/reconcile the smallest deterministic repository-side pre-live checker and procedure that can be run immediately after the one final Hardening V2 Fresh QA PASS.

The checker must answer only:

`AUTHORIZED FOR START BOUNDED REAL WOF ACCEPTANCE` or `WAITING/BLOCKED` with the precise failing gate.

It must not rerun already-PASS QA suites.

## Required checks

1. Proof-Authority Hardening Fix V2 canonical/stage/result is terminal COMPLETE.
2. Exactly one current final Hardening V2 Fresh QA result exists for the exact hardened proof-tooling blobs and is PASS.
3. OneClick V4 candidate/manifest remains the intended immutable acceptance candidate.
4. Every package-selected runtime blob still matches the V4 manifest pin, or equivalently no post-freeze selected-runtime drift exists.
5. No new ACTIVE P0/P1 implementation owner controls a package-selected runtime blob or mandatory live-proof authority.
6. Historical stale ACTIVE claims already superseded by durable successor authority are not treated as blockers.
7. No new mandatory proof-authority blocker was opened after the final Fresh QA.
8. Hardening/Fresh-QA proof-only files must not force OneClick regeneration unless a package-selected runtime blob actually changed.
9. The bounded Owner Flow V2 remains COMPLETE and available.
10. Safety/release boundary remains read-only; this prep/checker must not start Browser/WOF or mutate production.

## Implementation / deliverable

Prefer reusing existing acceptance/preflight utilities under `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/**` or other current gate selectors rather than creating a parallel gate system.

Produce:

- a small deterministic checker or exact command sequence;
- machine-readable PASS/WAITING/BLOCKED output if existing conventions support it;
- a concise result/README explaining each checked authority source;
- explicit fail-closed behavior for missing/malformed/ambiguous result or claim state;
- no current live-authorization verdict if Hardening/Fresh-QA prerequisites are not yet terminal.

If an equivalent narrow checker already exists and is current, document/reuse it instead of duplicating implementation.

## Scope

Repository-only preparation.
Do not modify `product/alpha/**`.
Do not modify proof implementation.
Do not modify danger rules, target semantics, Transport, PYLAUNCH, Recorder, OneClick runtime, input/AI.
Do not start Browser/WOF.
Do not rerun Formal, Recorder, PYLAUNCH, player-head, enemy-head, 5h endurance, or OneClick QA merely for repetition.
Do not create the final Hardening Fresh-QA claim.
Do not authorize live acceptance before Hardening COMPLETE + final Fresh QA PASS actually exist.

## Success

`COMPLETE — ALPHA V1 FINAL PRE-LIVE NARROW DRIFT GATE PREP — ONE-SHOT POST-QA AUTHORIZATION CHECK READY`

## Failure

`BLOCKED — ALPHA V1 FINAL PRE-LIVE NARROW DRIFT GATE PREP — <precise missing authority/checker capability>`

Strict canonical dedup v2. Stop duplicate-safe if equivalent work is already COMPLETE or ACTIVE.