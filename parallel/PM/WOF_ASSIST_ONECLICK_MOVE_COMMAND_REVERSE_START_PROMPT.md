# WOF Assist — One-Click Move Command Reverse Longrun Start Prompt

stageId: `WOF_ASSIST_ONECLICK_MOVE_COMMAND_REVERSE_V1`

Priority: **P2 strategic accelerator — spare-capacity only**

## Dedup / claim

Before work, follow `parallel/PM/STAGE_DEDUP_GUARD.md` and re-read current HEAD.

If equivalent durable result already exists, return:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If claimed/executing, return:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise atomically claim:
`parallel/PM/STAGE_CLAIMS/WOF_ASSIST_ONECLICK_MOVE_COMMAND_REVERSE_V1.json`

## Why this exists

Alpha release remains higher priority. This lane exists only to consume spare concurrency without competing with Alpha. Its purpose is to reduce future Beta/Assist engineering time by reverse-engineering the minimum command/state model needed for a deterministic **user-triggered one-click move** feature.

This is **not** an autoplay lane and must not expand into combat AI or automatic enemy response.

## First downstream consumer

Future `WOF Assist / one-click move` executor and Safe Path action planner.

## Hard write boundary

Allowed writes only under:
- `parallel/WOF_ASSIST_MOVE_REVERSE/**`
- own stage claim

Do not modify:
- `product/alpha/**`
- `parallel/PYLAUNCH/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/WOF052L_RECORDER/**`
- HUD implementation/proof lanes
- current Owner One-Click package

## Work

Use repository evidence, disassembly/reverse artifacts, ROM/state documentation, emulator knowledge already present in repo, and deterministic offline tooling where possible.

Determine only the minimum reusable model required for one-click move execution:
1. player input command grammar / direction + button sequence representation;
2. timing windows or ordering constraints visible from code/evidence;
3. player-state preconditions that make a command admissible or impossible;
4. command start / acceptance / completion / recovery signals if inferable offline;
5. representative move families sufficient to prove the model, not a full movelist atlas;
6. uncertainty/confidence and exactly what remains live-only.

Produce:
- `parallel/WOF_ASSIST_MOVE_REVERSE/RESULT.md`
- `parallel/WOF_ASSIST_MOVE_REVERSE/command_model.json`
- `parallel/WOF_ASSIST_MOVE_REVERSE/STATE_MODEL.md`
- deterministic parser/replay tests if justified
- a minimal next-evidence request if offline proof reaches its limit

## Longrun rule

This may run for hours if there is real non-redundant reverse work. Do not use sleep or artificial loops to manufacture duration. Re-read current HEAD periodically; if Alpha needs the same scarce scope, stop/park immediately.

## Maximum breadth

Do not reverse the whole game and do not catalog every move. Stop once the command/state abstraction is sufficient for a representative deterministic executor contract or once the next useful fact requires real gameplay evidence.

## Kill / park conditions

Stop or park when:
- additional findings no longer change the future executor contract;
- only descriptive movelist expansion remains;
- evidence becomes live-only;
- work drifts into autoplay, combat strategy, or unrelated game internals;
- a P0/P1 mainline task needs the resource/scope.

## Success stop condition

`WOF ASSIST ONE-CLICK MOVE COMMAND MODEL READY — READY FOR EXECUTOR PROTOTYPE`

Or one precise blocker / minimum live-evidence request.

Owner action: **NO** unless the final result proves a bounded live-only fact is unavoidable.