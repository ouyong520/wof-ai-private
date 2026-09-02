# Alpha V1 Final Pre-Live Narrow Drift Gate

This is the one-shot repository-side authorization check to run **only after** Proof-Authority Hardening Fix V2 is expected to be terminal and the single Final Fresh QA is expected to have PASSed.

It does not launch Browser/WOF, does not execute Formal/Recorder/PYLAUNCH/player-head/enemy-head/5h/OneClick QA suites, and does not mutate production or proof implementation.

## Command

```text
python parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/final_prelive_drift_gate.py
```

Optional machine-readable form:

```text
python parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/final_prelive_drift_gate.py --json
```

Default stdout is exactly one of:

```text
AUTHORIZED FOR START BOUNDED REAL WOF ACCEPTANCE
```

or:

```text
WAITING/BLOCKED — <precise failing authority>
```

Non-authorized exit code is `3`.

## Authority checked

### 1. Hardening V2 terminal authority

Canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.v1.anchored-overlays.proof-authority-hardening-fix-v2.json`

Stage claim:

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_ANCHORED_OVERLAYS_PROOF_AUTHORITY_HARDENING_FIX_V2.json`

Both must be `COMPLETE`, agree on token/result authority, and the durable result must contain the exact Hardening V2 terminal COMPLETE marker.

The post-fix `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/RUN_MANIFEST.json` must expose a valid `implementationCommit`. Every recursive `{path, sha}` authority pin in that manifest is checked against the exact fixed Git tree and against current HEAD. The check includes, at minimum, RUN_MANIFEST itself, proof core/Top/Worker/loader, production real Worker, player warning helper, enemy target-label helper, evidence schema, and any new authority-root/attestation/lifecycle/mapping blobs added by Hardening V2.

Any post-fixed authority-critical blob drift blocks authorization.

### 2. Exactly one Final Fresh QA

The checker discovers canonical claims whose dedup key contains all of:

- `proof-authority`
- `hardening-v2`
- `final-fresh-qa`

and excludes fixture/prep claims.

Exactly one such canonical authority may exist. It and its stage claim must be terminal `COMPLETE`, with a durable result on current history.

The result must record:

- PASS;
- Hardening V2 Final Fresh QA identity;
- frozen independent fixture coverage `17/17`;
- the exact hardened `implementationCommit`;
- every hardened authority pin SHA from the post-fix RUN_MANIFEST, including the RUN_MANIFEST blob itself.

Therefore a generic text PASS, a QA run on floating `main`, or a PASS against different hardened blobs cannot authorize live acceptance.

### 3. Owner OneClick V4 immutable candidate / selected-runtime drift

Authority:

- `parallel/OWNER_ONECLICK/RESULT.md`
- `parallel/OWNER_ONECLICK/package_manifest.json`
- current `parallel/OWNER_ONECLICK/refresh_manifest.py` selector

The result must retain the exact V4 PASS marker. Manifest schema/policy/safety must remain:

```json
{
  "schema": "wof-owner-oneclick-package-v1",
  "selectionPolicy": "owner-oneclick-runtime-v2",
  "safety": {
    "readOnly": true,
    "ramWrites": 0,
    "inputInjection": false
  }
}
```

The checker asks the current deterministic selector which runtime files are package-selected at current HEAD, then requires the selected path set and every selected Git blob SHA to equal the frozen V4 manifest.

This is intentionally narrow: proof-only Hardening/Fresh-QA files outside the package selector do **not** force OneClick regeneration. Only a real selected-runtime path/set/blob change blocks.

### 4. New ACTIVE P0/P1 release implementation owner

OneClick V4 is the durable historical baseline. ACTIVE canonical claims whose generation is at/before the V4 immutable source commit are not mechanically reopened; V4 already reconciled the historical/stale ACTIVE state, including successor authority.

For claims opened after the V4 baseline, the checker reads their PM start prompt. A new ACTIVE P0/P1 release implementation/fix/integration/hardening/refresh owner in Alpha V1 / OneClick / Transport / PYLAUNCH / Recorder / Live Proof / Browser Fleet / proof-authority domains blocks.

QA/audit/cross-check/review/reconciliation/readiness/prep/fixture/Owner-Flow work is not misclassified as a runtime implementation owner merely because its claim is ACTIVE.

Hardening V2 itself is never exempted by historical-baseline logic: it is an explicit prerequisite checked first and must be terminal COMPLETE.

### 5. No new mandatory proof-authority blocker after Final Fresh QA

After the Final Fresh QA result commit, any newly opened canonical `BLOCKED` proof-authority/live-proof-authority claim blocks. A newly opened ACTIVE P0/P1 proof-authority implementation owner also blocks.

The exact hardened authority pins are simultaneously rechecked at current HEAD, so post-QA proof implementation drift cannot hide behind claim state.

### 6. Owner Flow V2

`ALPHA_V1_BOUNDED_LIVE_ACCEPTANCE_OWNER_FLOW_V2` must remain terminal COMPLETE, its durable result must retain the exact COMPLETE marker, and the Owner procedure artifact must still exist.

## Historical stale ACTIVE handling

Historical ACTIVE is not treated as an error by itself. The narrow gate uses the durable OneClick V4 baseline plus explicit current successor/result authority rather than reopening every old claim. This prevents old interrupted Formal/QA/package bookkeeping from falsely blocking the final authorization while still detecting **new** post-freeze release implementation ownership and post-QA proof-authority blockers.

## Current expected disposition during prep

Until Hardening V2 is actually terminal COMPLETE, this checker must fail immediately with a `WAITING/BLOCKED` Hardening reason. No live authorization may be emitted before Hardening COMPLETE + exactly one exact-blob Final Fresh QA PASS.
