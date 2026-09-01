# WOF-052L Recorder Live Topology Identity Fix — RESULT

Stage: `WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_FIX_V1`

Status: READY

Start commit: `9d50c16a5e65ba1b7c914d2e6da497b78f12b417`

Implementation commit: `23ba3177a399f7975ad99b0191f98b1061db67e6`

Verification workflow commit: `e71e12294c5f3692ee8a9296003bff423bc6865d`

Verification workflow: `.github/workflows/wof052l-recorder-live-topology-identity.yml`

Verification run: `33522460226` (`windows-regression`, Windows Server 2025, Python 3.11.9)

## Fixes

### P0 — live topology revalidation evidence gap

Fixed fail-closed on the production Recorder path.

- Every discovery epoch that may admit or continue live evidence forces a fresh scan of already-live pages instead of trusting the old 10-second live-page skip window.
- `poll_rooms(now)` is evidence-gated by a proof token from that exact discovery epoch; a poll between proof epochs does not collect live evidence.
- Current topology must freshly prove a unique `(workerTargetId, pageTargetId)` pair for each live room.
- Cross-page shared-worker ambiguity, missing proof, probe failure, or discovery exception causes affected live rooms to finalize before any subsequent evidence poll.
- Reproof failure uses `live-topology-reproof-failed` and does not silently defer untrusted evidence.

### P1 — stale identity cache authority across runtime recreation

Fixed fail-closed on the production discovery path.

- `targetId` remains only an index and is no longer sufficient authority for exact World identity reuse.
- Exact World cache authority is bound to the current CDP session/runtime lifecycle.
- A recreated/re-attached runtime reusing the same `targetId` clears stale authority and must run the exact World proof again.
- Wrong-World replacement is rejected.
- Correct replacement may be readmitted only after its own fresh exact-World proof.
- The same live CDP session may reuse its own proven identity cache.

## Changed files

- `parallel/WOF052L_RECORDER/discovery_v2_sync.py`
- `parallel/WOF052L_RECORDER/discovery_v2_sync_base.py`
- `parallel/WOF052L_RECORDER/hardening_v2.py`
- `parallel/WOF052L_RECORDER/hardening_v2_base.py`
- `parallel/WOF052L_RECORDER/test_live_topology_identity_fix.py`
- `.github/workflows/wof052l-recorder-live-topology-identity.yml`

The `*_base.py` files preserve the previous complete implementations exactly while the public modules add the narrow lifecycle/topology authority guards. This avoids broad behavioral churn in unrelated Recorder code.

## Regression evidence

GitHub Actions run `33522460226` completed successfully.

- Compile production + compatibility + regression files: PASS.
- Existing Discovery V2 regression: 3/3 PASS.
- Existing fleet regression: 21/21 PASS.
- New live topology / identity fix regression: 7/7 PASS.
- Independent QA adversarial suite: 3/3 PASS.
- Total executed tests in this verification run: 34/34 PASS.

## New adversarial coverage

1. Reused `targetId`, new runtime, wrong World: fresh reprobe occurs and replacement is rejected.
2. Reused `targetId`, correct recreated runtime: fresh proof is required before support/readmission.
3. Same live CDP session: its own exact-World authority may be reused.
4. Two already-live pages transition to a shared Worker inside the old 10-second window: affected live rooms finalize before evidence poll.
5. Two distinct Workers/pages remain independent and live.
6. Live topology reproof failure finalizes instead of deferring evidence under stale authority.
7. Polling between discovery proof epochs collects no live evidence.

The independent QA adversarial cases for explicit endpoint drift, mid-capture live/live shared Worker ambiguity, and reused-target stale identity authority all pass against the fixed production modules.

## Preserved invariants

- Explicit endpoint guard remains fail-closed; no cross-port silent fallover was introduced.
- Normal distinct-worker room isolation remains intact.
- Existing Chinese owner UX remains intact; new live-topology failure announcement is Simplified Chinese with technical reason retained.
- Existing room lifecycle/accounting and 10-room fleet behavior remain in the preserved base implementation; fleet regression is 21/21 PASS.
- No `product/alpha/**` changes.
- No game RAM writes or input injection added.

## Risks / blockers

No repository-side blocker remains for this stage.

The fix is deliberately fail-closed: if fresh live topology cannot be reproven, evidence collection stops for the affected room rather than accepting stale ownership. This can reduce capture continuity during transient CDP/probe failures, but it preserves evidence identity correctness as required.

Independent QA may proceed.

LIVE TOPOLOGY IDENTITY FIX READY
