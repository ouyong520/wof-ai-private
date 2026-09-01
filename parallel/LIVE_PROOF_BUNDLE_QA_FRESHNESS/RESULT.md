# Unified Live Proof Freshness — Fresh Independent QA Result

Date: 2026-09-01
Stage: `UNIFIED_LIVE_PROOF_FRESHNESS_QA_V1`

## Verdict

**BLOCKED — UNIFIED LIVE PROOF FRESHNESS QA — P1 arbitrary Recorder stdout can refresh stale admission authority**

`你现在需要操作：NO`

No Owner Windows/WOF run was requested or used.

This QA wrote only under `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/**` plus the mandatory stage claim. The implementation under `parallel/LIVE_PROOF_BUNDLE/**`, PYLAUNCH, Recorder, Fleet, Prospective, and Alpha was not modified.

## Target re-read

Fresh QA re-read the current default-branch implementation and dependencies. The blocker is against:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
  - blob `ce2e9f970f1a9e70493eb0d06b04431ea4870aa1`
- `parallel/PYLAUNCH/wof_launcher/proof.py`
  - blob `7cddae420b08bba627b05f2164083289569e5f5a`
- `parallel/PYLAUNCH/wof_launcher/state.py`
  - blob `7f00e9a2e948f86c30a99cab04809d726b60c95d`
- `parallel/WOF052L_RECORDER/fleet_recorder.py`
  - blob `9398ef1569815439e6c141890f069674a30dca0f`

Fresh independent fixture:

- `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/test_freshness_adversarial.py`
- fixture blob `bb13a3577facc7160c8b26a306a8fee789282857`
- fixture commit `b145a6b0db4899cc3e10820a5456dd34895acbbb`

Machine-readable result:

- `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.json`

## Fresh vectors built

The new fixture does not copy the old fail-closed QA timestamps/process mappings. It builds current-time fixtures for:

1. empty/malformed/inconsistent process-health mappings;
2. live-but-hung recent PYLAUNCH PASS where Recorder/process generations move but the PYLAUNCH generation does not;
3. the second Owner generation gate after simulated confirmation;
4. stale/missing/malformed/future PYLAUNCH timestamps;
5. valid carriage-return Recorder supervisor heartbeat parsing;
6. arbitrary carriage-return text after a stale Recorder admission;
7. `longCaptureAutoStarted=false`;
8. read-only/RAM/input/Worker-replacement safety invariants.

The malformed health and hung recent-PASS paths are fail-closed in the current source. The fresh QA blocker is a different Recorder-authority boundary.

## P1 blocker — arbitrary stdout renews stale Recorder admission

Current `RecorderEvidence.feed()` refreshes Recorder output freshness for **every non-empty stdout fragment** before classifying what that fragment means:

- increments `output_generation`;
- updates `last_output_utc`;
- resets `_last_output_monotonic` to now;
- only afterward checks whether the text is an admission marker or fatal marker.

`RecorderEvidence.current_healthy` is then simply:

`admitted and not fatal and current_fresh`

The carriage-return-aware `reader()` forwards every `\r`/`\n` delimited non-empty fragment to `RecorderEvidence.feed()`.

Therefore the following fresh adversarial sequence reanimates old authority:

1. establish one valid Recorder admission;
2. age `_last_output_monotonic` beyond `RECORDER_FRESHNESS_SECONDS` so the admission is correctly `STALE` / `current_healthy=false`;
3. send `arbitrary stale diagnostic text\r` through the CR-aware reader;
4. that text is not a trusted supervisor heartbeat, not a new admission, and not a fatal marker;
5. nevertheless `feed()` advances output generation and resets freshness;
6. the old `admitted=true` state remains unchanged, so `current_healthy` becomes true again.

A source-exact isolated reproduction of the current `RecorderEvidence.feed` + `reader` logic produced:

```text
before: current_healthy=False, output_generation=1
after arbitrary CR text: current_healthy=True, output_generation=2
```

This is not only a synthetic parsing concern. The real Fleet Recorder supervisor emits a periodic carriage-return status line independently of whether the historical admission itself has been freshly re-proven. The unified proof currently has no semantic distinction between that intended heartbeat and unrelated stdout; both renew the same Recorder success freshness generation.

## Release impact

With otherwise current and safe evidence:

- Fleet browser/page/Worker indicator valid;
- current PYLAUNCH PASS with fresh `lastUpdateUtc`;
- complete current live process health;
- no blocker;
- Owner playability `CONFIRMED`;

an old Recorder admission can be refreshed by arbitrary stdout and once again satisfy both `safety_ok()` and `automated_ready()` through `recorder.current_healthy`.

That can restore:

- `overallResult=PASS`;
- `tenRoomLongCaptureReady=true`.

This violates freshness QA requirement 6:

> carriage-return heartbeat handling works without accepting arbitrary stale text as new authority.

Because this false authority can admit the next long-capture gate, severity is **P1**.

## Required fix direction

Keep CR-aware reading, but separate **trusted Recorder authority heartbeat** from generic stdout diagnostics.

At minimum:

1. only a semantically recognized current supervisor heartbeat or a fresh admission should advance the Recorder authority-heartbeat generation;
2. arbitrary stdout must remain diagnostic-only and must not reset success freshness;
3. `current_healthy` must depend on the trusted heartbeat/admission generation, not generic output generation;
4. add regression coverage proving arbitrary `\r` text cannot revive a stale admission while the real supervisor heartbeat still can;
5. keep fatal/revocation, historical evidence, double Owner generation gates, Chinese UX, `longCaptureAutoStarted=false`, and all safety invariants unchanged.

A fresh fix stage is required, followed by a new independent QA stage.

## Stop condition

**BLOCKED — UNIFIED LIVE PROOF FRESHNESS QA — P1 arbitrary Recorder stdout can refresh stale admission authority**

`你现在需要操作：NO`
