# PM True Long-Run Execution Policy

Date: 2026-09-01

## Why this exists

A task must not be labeled `5h+`, `long soak`, or `longrun` merely because its matrix/corpus is large. The first three such stages ended in ~6–13 minutes: two correctly stopped on P1 blockers and one converged after bounded replay. Those results were useful, but they did not satisfy the owner's request for genuine multi-hour background work.

## Authoritative rule

A future stage may be called a **true 5h+ long-run** only when all of the following are true:

1. It launches or owns a durable executor whose intended wall-clock runtime is at least 5 hours when no stop-worthy blocker occurs (for example CI/soak/replay/fuzz/endurance infrastructure that continues without an interactive chat remaining open).
2. The executor records periodic durable checkpoints/heartbeats and the exact SUT/input snapshot.
3. The task has enough independent work to keep producing decision-changing evidence for that duration; do not pad time with sleeps or repeated identical checks.
4. Current P0/P1 implementation gates that would invalidate the run are already closed, or the runner is intentionally designed to consume moving current-head snapshots safely.
5. Write ownership does not conflict with active fixes.
6. It names a downstream consumer and a convergence/kill condition.

## Early-stop rule

A true long-run may still end before 5 hours if it discovers a precise P0/P1 blocker or reaches a proof that further execution cannot change the decision. That is a valid early stop, but PM must report that the intended 5h+ soak did **not** complete.

## Forbidden

- Calling a bounded static audit a `5h+` task without a long-lived executor.
- Calling a 10-minute exhaustive permutation pass a `5h+` task merely because the check count is large.
- Sleeping/waiting only to satisfy elapsed time.
- Continuing on an invalidated SUT merely to reach five hours.
- Re-running the same saturated corpus after the decision is already unchanged.

## PM delivery reassessment

After every long-run submission, PM must classify separately:

- intended duration;
- actual elapsed executor duration;
- whether a P0/P1 early stop occurred;
- useful artifact/evidence produced;
- actual critical-path acceleration;
- whether V2/restart is justified.

A stage that does not launch a durable multi-hour executor must be described as `bounded audit`, `bounded replay`, `stress matrix`, or similar — not `5h+ long-run`.
