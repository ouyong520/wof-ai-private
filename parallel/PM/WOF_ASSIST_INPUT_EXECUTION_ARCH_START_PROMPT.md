# WOF Assist — Input Execution Architecture Start Prompt

stageId: `WOF_ASSIST_INPUT_EXECUTION_ARCH_V1`

Priority: **P2 strategic accelerator — spare-capacity only**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md` and re-read current HEAD. If equivalent durable result exists, return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`; if claimed, return `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.

Claim `parallel/PM/STAGE_CLAIMS/WOF_ASSIST_INPUT_EXECUTION_ARCH_V1.json`.

Purpose: prepare an adapter-neutral, user-triggered **one-click move** execution engine contract for future Beta/Assist without touching Alpha or performing autonomous gameplay.

Allowed writes only under `parallel/WOF_ASSIST_INPUT_ARCH/**` plus own claim. Do not modify `product/alpha/**`, PYLAUNCH, Recorder, Live Proof, HUD, or Owner package.

Build offline/synthetic architecture for: symbolic command steps; press/release/hold timing; cancellation; deadline/timeout; precondition checks; completion/ack signal hooks; adapter abstraction for Browser/emulator; dry-run mode; deterministic trace output; fail-closed behavior; hotkey/user-trigger boundary; no autonomous trigger. Provide mocks/fixtures and deterministic tests.

The command vocabulary may remain symbolic and must not guess game-specific move timing that the reverse lane has not proved. Define a narrow consumer contract that can later ingest `parallel/WOF_ASSIST_MOVE_REVERSE/command_model.json`.

Produce `parallel/WOF_ASSIST_INPUT_ARCH/RESULT.md`, interface/schema docs, deterministic executor prototype operating only on synthetic adapters, and tests.

Stop/park if further work requires actual game input injection or live-only command evidence.

Success: `WOF ASSIST INPUT EXECUTION ARCH READY — WAITING COMMAND MODEL / LIVE ADAPTER`.

Owner action: **NO**.