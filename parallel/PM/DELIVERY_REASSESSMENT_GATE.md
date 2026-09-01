# PM Delivery Reassessment Gate

Status: AUTHORITATIVE PM PROCESS RULE

## Why this exists

A worker saying `PASS`, `READY`, or `COMPLETE` is not itself project progress.
Every delivered artifact must be judged by whether it actually shortens the path to the product north star:

**WOF Future Danger AI actually useful in real gameplay.**

The PM must not operate as a task dispatcher that merely replaces one finished task with another.
The PM must continuously think, re-plan, and converge the project.

## Mandatory gate after EVERY completed / blocked delivery

Before issuing the next task, PM must re-read current GitHub default-branch state and explicitly reassess:

1. **Authoritative classification**
   - `ACCEPTED_COMPLETE`
   - `ACCEPTED_WAITING_GATE`
   - `NEEDS_FRESH_FIX`
   - `SUPERSEDED`
   - `NO_DURABLE_RESULT`

2. **Actual project leverage**
   - What bottleneck did this close?
   - What repeated cost did it remove?
   - Did it reduce Owner/manual Browser work?
   - Did it improve Alpha/Beta/Safe Path readiness, or only produce an artifact?

3. **Critical-path impact**
   - What downstream stage is newly unlocked?
   - Did any previously queued task become stale, redundant, unsafe, or lower priority?
   - Did a new P0/P1 blocker appear?
   - Does the mainline ordering need to change?

4. **Release-readiness impact**
   - Reassess distance to the next real product gate (Alpha first, then Beta, then Safe Path).
   - Do not mechanically increase a percentage because a task finished.
   - Progress only increases when a meaningful release blocker, integration dependency, evidence gap, or Owner burden is actually reduced.
   - If a fresh QA exposes a blocker, readiness may stay flat or temporarily decrease even though useful work was completed.

5. **Convergence / anti-scope-creep**
   - Is more work on this lane still decision-changing?
   - If only real evidence can advance it, park it and batch with the next unavoidable Owner run.
   - If enough is known for the current stage, stop researching and consume the result downstream.
   - Accelerators must make the existing route shorter, not make the project larger.

6. **Next-task decision**
   Only after the above reassessment may PM:
   - create a fresh fix stage;
   - create a fresh independent QA stage;
   - promote an integration stage;
   - park/supersede a lane;
   - change priority;
   - or intentionally leave a slot unused if no durable non-conflicting task is justified.

## Required PM behavior on user progress checks

When the user says `继续`, `检查进度`, or reports that workers stopped:

1. re-read latest commits + stage claims/results;
2. audit each newly stopped delivery independently;
3. classify it using this gate;
4. update the critical path and priorities;
5. only then fill available worker slots.

Do not merely count completed tasks.
Do not treat worker `PASS/READY` as authoritative.
Do not keep a task alive just to consume concurrency.

## Product-experience priority note

Player-head warning HUD is now P1 product-experience mainline because the player's visual focus is on the controlled character and nearby threats, not a fixed screen corner. Fixed HUD remains a fail-safe fallback, not the desired primary presentation.

This P1 priority must still not override a true P0 safety/authority blocker, but it should consume non-conflicting capacity aggressively until it reaches real Browser proof + integration + fresh QA closure.

## Owner rule

Owner action remains `NO` unless repository-side analysis, regression, QA, automation, integration prep, and preflight can no longer advance the decision.
