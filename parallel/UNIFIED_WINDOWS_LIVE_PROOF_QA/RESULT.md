# WOF Unified Windows Live Proof — Fresh Independent QA Result

Date: 2026-09-01

## Verdict

**BLOCKED — P1 fail-closed aggregation can return PASS with a retained fatal/blocker**

Fresh fix stage is required. This QA did **not** modify `parallel/LIVE_PROOF_BUNDLE/**`, PYLAUNCH, Browser Fleet, Recorder, or `product/alpha/**`.

## Precise blocker

The unified live-proof aggregator does not make blockers/fatal Recorder state part of the final PASS predicate.

Current code path in `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`:

1. `RecorderEvidence.feed()` leaves `admitted=True` after a later fatal line and separately sets `fatal=True`.
2. `automated_ready()` requires `recorder.admitted`, but does **not** require `recorder.fatal == False`.
3. The live loop correctly appends a blocker when Recorder emits a fatal marker such as `已安全拒绝采集`.
4. `build_status()` computes:

   `live_pass = auto_ready and playability == "CONFIRMED"`

   and checks `if live_pass:` **before** `elif blockers:`.
5. Therefore a retained blocker does not prevent `overallResult="PASS"` or `tenRoomLongCaptureReady=true` once automated readiness remains true and the owner answers Y.
6. The loop also enters the owner Y/N branch on `automatedChecksReady` before its later `if blockers:` branch, so an already-fatal run can still ask the owner for playability confirmation.

This violates the start-prompt requirements:

- any child failure must make the total result fail closed while preserving other evidence;
- the owner playability question may appear only after all automatic items have passed;
- a failed Recorder Discovery V2 state must not be converted into readiness for 10-room long capture.

## Deterministic reproduction vector

The following state is sufficient to expose the defect without a real browser:

```text
Fleet: PASS / cheap-indicator-only / safety PASS
PYLAUNCH: authoritative PASS / World 921031 PASS
Recorder: admitted=True
Recorder: fatal=True after later "已安全拒绝采集"
blockers: ["Recorder 准入失败: ..."]
owner playability: CONFIRMED
```

Expected:

```json
{
  "overallResult": "BLOCKED",
  "tenRoomLongCaptureReady": false
}
```

Current aggregation logic can produce:

```json
{
  "overallResult": "PASS",
  "tenRoomLongCaptureReady": true
}
```

while the blocker is still retained in `live.blockers`.

## Related fail-closed risk found during the same inspection

The child-process exit guards are also conditional on stale success state:

- PYLAUNCH exit is only turned into a blocker when `automatedPass` is false.
- Recorder exit is only turned into a blocker when `admitted` is false.

So an unexpected child exit after previously reaching PASS/admission can leave stale positive evidence eligible for the final PASS path. Fresh fix QA should include post-PASS child-exit vectors as well.

## Other required invariants inspected before stop

These were present in the current repository and are **not** the blocker:

- Browser Fleet manifest explicitly marks Worker status `cheap-indicator-only` and World identity non-authoritative.
- PYLAUNCH Discovery V2 performs an exact World 921031 CPU-logical SHA-256 gate against `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.
- Recorder Discovery V2 independently checks its exact World SHA-256 before admission.
- unified proof uses one owner entry and does not require Git/DevTools/Worker Console/pasted JavaScript in the normal flow.
- long capture is not auto-started by the bundle.
- owner-facing primary flow is Simplified Chinese.

These positive findings cannot override the P1 fail-closed defect.

## Fresh-fix acceptance criteria

A fresh fix stage must prove at minimum:

1. Any non-empty fatal blocker makes final PASS impossible.
2. `RecorderEvidence.fatal == True` makes Recorder automatic admission not-ready/failed even if it had previously admitted.
3. The Y/N playability prompt cannot be reached after any blocker/fatal state exists.
4. An unexpected PYLAUNCH or Recorder child exit after prior PASS/admission fails closed rather than trusting stale positive evidence.
5. Regression vectors cover fatal-after-admission, blocker + owner Y, PYLAUNCH-exit-after-PASS, and Recorder-exit-after-admission.
6. Positive evidence from unaffected lanes remains preserved in the final blocked JSON.

## Stop condition

**BLOCKED — P1 fail-closed aggregation can return PASS with a retained fatal/blocker**
