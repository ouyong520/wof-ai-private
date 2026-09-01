# WOF Unified Windows Live Proof Fail-Closed — Fresh Independent QA Result

Date: 2026-09-01
Stage: `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_QA_V1`

## Verdict

**BLOCKED — UNIFIED LIVE PROOF FAIL-CLOSED QA — P1 stale/unknown child success can still become PASS**

`你现在需要操作：NO`

This is a fresh independent QA result. Per the QA boundary, no file under `parallel/LIVE_PROOF_BUNDLE/**`, PYLAUNCH, Fleet, Recorder, Prospective, or Alpha was modified.

## Target re-read

QA re-read the current default-branch target and tested against these blobs:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`: `b3098a586dae8a1d3070e6667c536ea011911e6b`
- `parallel/LIVE_PROOF_BUNDLE/test_unified_live_proof.py`: `05b739158d4147ac5d87a16520f75be5497c6028`
- `parallel/PYLAUNCH/wof_launcher/proof.py`: `7cddae420b08bba627b05f2164083289569e5f5a`
- `parallel/PYLAUNCH/wof_launcher/monitor.py`: `5ee0ce9a84988d7841799d907ebdfe2a3e68ea56`
- `parallel/PYLAUNCH/wof_launcher/state.py`: `7f00e9a2e948f86c30a99cab04809d726b60c95d`

Independent adversarial fixture added:

- `parallel/LIVE_PROOF_BUNDLE_QA_FAILCLOSED/test_failclosed_adversarial.py`

Machine-readable result:

- `parallel/LIVE_PROOF_BUNDLE_QA_FAILCLOSED/RESULT.json`

## P1-1 — unknown/partial child health is classified healthy

`normalize_process_health()` currently defines `healthKnown` only as `process_state is not None` and defaults missing `launcherRequired` / `recorderRequired` fields to `False`.

Independent adversarial evaluation of the current logic produced:

```json
{
  "input": {},
  "healthKnown": true,
  "launcherRequired": false,
  "recorderRequired": false,
  "launcherLive": null,
  "recorderLive": null,
  "healthy": true
}
```

With otherwise clean Fleet + authoritative PYLAUNCH PASS + Recorder admission + Owner `CONFIRMED`, that state is sufficient for:

```json
{
  "overallResult": "PASS",
  "tenRoomLongCaptureReady": true
}
```

The same problem exists for partial mappings that prove only one child, e.g. `{"launcherRequired": true}` or `{"recorderRequired": true}`.

This violates QA requirement 5: **child health unknown =>不可 PASS**. Unified proof must require structurally complete current health for both required child processes; absence of a required child field cannot be interpreted as “not required”.

## P1-2 — stale PYLAUNCH PASS has no freshness gate

PYLAUNCH proof JSON already carries `lastUpdateUtc`. `StatusStore.update()` refreshes that timestamp and the monitor publishes proof snapshots as it polls.

Unified proof currently copies PYLAUNCH result/check/safety fields but does not consume `lastUpdateUtc`, age, heartbeat, generation, or any other freshness signal. Process health only checks whether `poll()` reports the process has exited.

Independent adversarial evaluation used an otherwise-valid PASS proof with:

```json
{
  "lastUpdateUtc": "2000-01-01T00:00:00+00:00",
  "launcherExitCode": null,
  "recorderExitCode": null
}
```

Current aggregation still produced:

```json
{
  "overallResult": "PASS",
  "tenRoomLongCaptureReady": true
}
```

Therefore a live-but-hung PYLAUNCH child can leave a previous PASS JSON with current authority indefinitely. The final Owner-answer re-check cannot detect that regression because it re-reads the same stale positive JSON and only treats process exit as unhealthy.

This violates requirements 6 and 10, and prevents requirement 7 from being robust across the PYLAUNCH lane:

- stale positive JSON/history must not restore current authority;
- recovery must require new current evidence/generation;
- a child/regression during Owner answering must fail closed at final re-check.

## 16-vector independent matrix

| # | QA vector | Result | Independent finding |
|---|---|---|---|
| 1 | Recorder admission then fatal revokes authority | PASS | Fatal clears current admission and produces blocker. |
| 2 | blocker + simulated Owner Y remains blocked | PASS | Sticky blocker dominates PASS. |
| 3 | PYLAUNCH exit-after-PASS | PASS | Exit code creates blocker and removes readiness. |
| 4 | Recorder exit-after-admission | PASS | Exit code creates blocker and removes readiness. |
| 5 | child health unknown cannot PASS | **FAIL / P1** | Empty/partial process mapping is classified healthy. |
| 6 | stale positive JSON/history cannot recover authority | **FAIL / P1** | Recorder history is separated, but PYLAUNCH stale PASS has no freshness gate. |
| 7 | recovery requires new generation/current evidence | **FAIL / P1 coupling** | Recorder generation is correct; PYLAUNCH has no freshness/generation requirement at unified gate. |
| 8 | sticky blocker cannot be erased by later positive | PASS | Existing blocker keeps same run blocked. |
| 9 | blocker/fatal => ownerPromptEligible=false | PASS | Aggregation gates prompt on blocker-free automatic readiness. |
| 10 | Owner-answer regression gets final fail-closed re-check | **FAIL / P1** | Exit/fatal regression is rechecked, but live-but-hung stale PYLAUNCH PASS remains accepted. |
| 11 | blocked JSON retains positive history + diagnostics | PASS | Positive unaffected lanes and Recorder history remain present. |
| 12 | clean current lanes + Owner CONFIRMED may PASS | PASS | Clean complete fixture reaches PASS and does not auto-start long capture. |
| 13 | repository/CI PASS cannot substitute live PASS | PASS | Repository result is separate; absent live evidence remains non-PASS. |
| 14 | RAM/input/Worker-replacement safety violation not ready | PASS for covered current safety fields | RAM-write and Fleet Worker-replacement violations fail readiness. |
| 15 | `longCaptureAutoStarted=false` always | PASS | Remains false including clean PASS fixture. |
| 16 | owner-facing modified path Simplified Chinese | PASS | Main prompts, errors, summaries, and final action text remain Simplified Chinese; technical component labels remain identifiers only. |

## Why this is release-blocking

The stage exists specifically to prove that stale child success cannot become PASS. The current implementation closes fatal/exit cases but still equates “process has not exited” with “current evidence is healthy”, and it accepts malformed/partial health metadata as known health.

That means the Unified Windows Live Proof can produce a false `PASS` / `tenRoomLongCaptureReady=true` without current authoritative child evidence. This is a P1 because it can incorrectly admit the next long-capture gate.

## Required fresh fix direction

A fresh fix thread should, at minimum:

1. make process-health completeness fail closed: both PYLAUNCH and Recorder required/live facts must be explicitly present and current before `healthy=true`;
2. consume PYLAUNCH `lastUpdateUtc` or a stronger monotonic heartbeat/generation and reject stale PASS while the child remains alive;
3. apply freshness again immediately before the Owner prompt and after the Owner answer;
4. add equivalent freshness/current-generation semantics for every child success that can authorize PASS;
5. preserve historical positive evidence only as diagnostics, never as readiness authority.

After that fix, a **new independent QA stage** must rerun the adversarial fixture. This QA thread must not patch the implementation.

## Stop condition

**BLOCKED — UNIFIED LIVE PROOF FAIL-CLOSED QA — P1 stale/unknown child success can still become PASS**

`你现在需要操作：NO`
