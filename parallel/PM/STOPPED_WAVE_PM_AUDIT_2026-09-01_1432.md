# PM Audit — Five Stopped Stages

Date: 2026-09-01

## Reviewed stopped stages

### 1. PYLAUNCH_PARENTFRAME_AUTHORITY_FIX_V1
PM classification: `ACCEPTED_DEV — FRESH QA REQUIRED`
- production `Page.getFrameTree` mapping now reaches direct Worker `parentFrameId` authority;
- fix reports targeted 5/5 + compatibility/safety 16/16;
- no Owner run required;
- next: `PYLAUNCH_PARENTFRAME_AUTHORITY_QA_V1`.

### 2. PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_P0_FIX_V1
PM classification: `ACCEPTED_DEV — FRESH QA REQUIRED`
- positive-duration live-topology audit gap removed;
- exact pair reproof required before prospective drain/ingest;
- cleanup payload no longer bypasses topology authority;
- next: `PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_QA_V1`.

### 3. UNIFIED_LIVE_PROOF_FRESHNESS_FIX_V1
PM classification: `ACCEPTED_DEV — FRESH QA REQUIRED`
- malformed/partial child health, stale PYLAUNCH PASS, stale Recorder admission, and generation advance gates addressed;
- implementation reports 43 combined tests PASS;
- next: `UNIFIED_LIVE_PROOF_FRESHNESS_QA_V1`.

### 4. WOF052L_RECORDER_HARDENING_QA_V1
PM classification: `NEEDS_FRESH_FIX — P0/P1`
Fresh independent QA found:
- P0: live/live shared-Worker topology transition can remain invisible until next audit and allow evidence polling;
- P1: recreated Worker can inherit cached World identity authority keyed only by targetId.
Next: `WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_FIX_V1`.
Long capture remains NOT AUTHORIZED.

### 5. HUDANCHOR_PLAYER_PROJECTION_REVERSE_V1
PM classification: `ACCEPTED_COMPLETE — WAITING BOUNDED LIVE PROOF`
- useful offline reverse-engineering exhausted without guessing;
- native raster, player structure, XYZ reader, drawing-buffer mapping, resize/DPR/staleness policy are closed as candidate/runtime contract;
- remaining exact camera/bias/Y-Z model/clearance require one bounded live Browser proof;
- do not start broader reverse engineering;
- current `HUDANCHOR_ONECLICK_BROWSER_PROOF_AUTOMATION_V1` remains active and owns reduction of that Owner step.

## Current still-active lanes at audit time
- `HUDANCHOR_ONECLICK_BROWSER_PROOF_AUTOMATION_V1`
- `ALPHA_TRANSPORT_REAL_ADAPTER_PREP_V1`
- `REGRESSION_ORCH_DISCOVERY_V2_GUARD_V1`
- `OWNER_ONECLICK_WORKFLOW_DYNAMIC_MANIFEST_FIX_V1`

## Five replacement slots
1. P0 `WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_FIX_V1`
2. P0 `PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_QA_V1`
3. P1 `PYLAUNCH_PARENTFRAME_AUTHORITY_QA_V1`
4. P1 `UNIFIED_LIVE_PROOF_FRESHNESS_QA_V1`
5. P1 `ALPHA_TRANSPORT_REFERENCE_QA_V1`

All five are repository-side and non-conflicting by primary write scope.

## Owner action
`NO` for real WOF/Windows testing.
