# BASECAP Operator-Gate Timing Note

Updated: 2026-09-01

## Finding

Collector v1 operator readiness and capture start are not the same instant.

`READY_WOF_TASK.bat` writes `runtime/OPERATOR_READY.json` immediately, but `bridge.collector_service` checks the queue on its poll loop. The delivered default is `DEFAULT_POLL_SECONDS = 10.0`.

Therefore an instruction of the form:

```text
READY accepted -> immediately perform a short action
```

is not timing-safe for a short action capture. The operator may complete the action before Collector has entered the formal `RUNNING` capture window.

This is a control-plane timing/UX limitation, not a raw-frame integrity failure. Collector PASS still proves mechanical capture health only.

## BASECAP rule

For future BASECAP operator-gated captures that require a short action after READY and cannot be labeled from an already-retained raw:

1. keep Collector v1 unchanged;
2. use a sufficiently long capture window (30 s default for short action scenes);
3. after exact `Operator ready accepted for task: <taskId>`, require 12 s of no input;
4. only then perform the requested action sequence;
5. keep the action sequence short enough to fit comfortably inside the remaining window;
6. retain P2/P3 and all unrelated controls as specified by the task.

The 12-second delay is chosen because the delivered Collector poll period is 10 seconds. It ensures the service has had at least one poll opportunity to observe the matching ready token and enter the capture window.

## Affected capture

`BASECAP-B12-facing-minimal-8s60-20260901-0518Z` completed mechanically with PASS and retained raw, but its task instructed the operator to act immediately after READY. Because the readiness-to-run delay can be up to one poll interval, BASECAP does not treat that raw as a canonical B12 facing baseline.

It is retained historically and must not be overwritten or reused as a canonical operator-timed B12 scene.

A new unique retry task uses the delayed protocol:

`BASECAP-B12R-facing-delayed-30s60-20260901-0527Z`

## Scope

This note changes only BASECAP acquisition protocol. It does not modify frozen Collector v1 and does not authorize game-memory writes, automatic keypresses, or Browser/WASM promotion.
