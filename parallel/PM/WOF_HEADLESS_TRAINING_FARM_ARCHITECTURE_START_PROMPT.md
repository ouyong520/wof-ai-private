# WOF Headless Training Farm — Architecture / Feasibility V1

stageId: `WOF_HEADLESS_TRAINING_FARM_ARCHITECTURE_V1`
dedupProtocol: `v2`
dedupKey: `wof.headless-training-farm.architecture-feasibility-v1`
dedupMode: `exclusive`

Priority: **Future Near-Zero mainline architecture, parallel-safe with Alpha closeout**

## Purpose

Define an implementation-ready local background training architecture for WOF that can eventually run 10 isolated emulator workers on the Owner's Windows machine, fork the same savestate into multiple branches, inject independent per-instance frame-level input, read WOF RAM state, score damage/survival outcomes, and generate state -> action -> result data for near-zero-damage route learning.

This stage is architecture/preflight only. It must not modify Alpha product behavior and must not turn into a broad emulator-rewrite project.

Owner target machine for sizing: AMD Ryzen 7 5800H, 32 GB RAM.

## Start / canonical dedup v2

Before substantive work, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current claims/recent commits, and relevant current architecture/contracts including at minimum:

- `parallel/WOF_ASSIST_INPUT_ARCH/RESULT.md` and any current input-execution successor/result;
- `WINKAWAKS_SINGLE_OPERATOR_SWEEP_GUIDE.md`;
- `COLLECTOR_ROUTING.md`;
- `PARALLEL_RESEARCH.md`;
- `parallel/BASECAP/README.md` and `parallel/BASECAP/BASE_CAPTURE_CATALOG.md` as useful for known WOF state semantics;
- current Alpha worker/rules/state schema only as read-only semantic references, not as a write target;
- in `ouyong520/wof-winkawaks-bridge`, `docs/COLLECTOR_V1_CONTRACT.md` and relevant collector/session ownership facts.

Use current public upstream documentation/source for emulator candidates when materially needed; do not rely on stale chat assumptions. If equivalent architecture/feasibility work is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/wof.headless-training-farm.architecture-feasibility-v1.json`

with a fresh unpredictable `claimToken`. Re-read current `main` and exact canonical claim and verify ownership, then create:

`parallel/PM/STAGE_CLAIMS/WOF_HEADLESS_TRAINING_FARM_ARCHITECTURE_V1.json`

Any ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Required architecture work

Produce an implementation-ready decision and contract, not a vague survey.

### 1. Emulator/core selection

Evaluate realistic existing candidates for CPS1/WOF headless/scriptable training, with primary attention to an FBNeo/libretro-style embedded core versus MAME Lua/headless or another demonstrably better fit. Establish from current upstream facts:

- CPS1/WOF compatibility;
- deterministic frame stepping/control;
- savestate save/load support and expected determinism boundaries;
- programmatic per-frame input without Windows foreground focus;
- RAM/memory inspection/access capability;
- headless/no-video/no-audio operation or equivalent low-overhead mode;
- multi-process isolation feasibility;
- licensing/distribution implications for our host code;
- whether one process per emulator/core instance is the safest V0 architecture.

Choose one primary V0.1 implementation target and one fallback. Do not propose writing a CPS1 emulator from scratch unless current facts prove existing cores cannot satisfy the contract.

### 2. Minimal headless host contract

Freeze a minimal API such as:

- `reset()`;
- `step(action, frames)`;
- `read_state()`;
- `save_state()`;
- `load_state()`;
- `score_transition()` / reward observation;
- health/diagnostic/worker-id lifecycle operations.

Define exact frame/input semantics, ownership, process boundaries, error/fail-closed behavior and deterministic replay expectations.

### 3. 10-worker fleet model

Design a Windows-local fleet for the 5800H/32GB target:

- independent process/core state per worker;
- no desktop focus dependency;
- video/audio disabled or minimized;
- CPU affinity/priority strategy that leaves the Owner machine usable;
- worker crash isolation and restart;
- per-worker save-state namespace;
- central coordinator with bounded fan-out/fan-in;
- staged benchmark gates at 1 -> 2 -> 4 -> 8 -> 10 workers rather than assuming 10 works.

Define objective benchmark metrics: simulated frames/sec, real-time multiplier, CPU %, memory/worker, aggregate memory, thermals/throttling signals where observable, state save/load latency, fork turnaround, deterministic replay mismatches and desktop responsiveness budget.

### 4. WOF RAM observation bridge

Define how to map the new emulator's CPS1 address space/RAM into existing WOF semantic knowledge without assuming WinKawaks host addresses transfer directly. At minimum plan proof for:

- P1/P2/P3 live identity, position and HP;
- enemy slots/identity/type/position;
- current target semantics where available;
- current attack/action/animation state fields as raw/high-value observation even when their human semantic names are not yet known;
- lifecycle/death/replacement;
- camera/boundary fields if available/needed for policy observation.

Specify a cross-emulator semantic calibration method using controlled identical scenes/savestates and invariants, not guessed address translation.

### 5. Savestate fork-search primitive

Define the first technical milestone exactly:

`one WOF state -> save -> clone/load across N workers -> try N independent action sequences -> advance fixed frames -> score -> select best result`

The V0 milestone must work before PPO/RL. Define deterministic branch identity, RNG/state concerns, action-duration encoding, horizon choices and replay artifact format.

### 6. Reward / outcome V0

Define a minimal robust score based primarily on observable results rather than requiring every attack to be reverse-engineered first. Include at least:

- HP loss as large negative;
- death as terminal/severe negative;
- known grab/knockdown/bad-state signals if reliably observable;
- survival/safe separation or reachable safety as secondary signal;
- anti-degenerate progress/timeout terms so the agent cannot maximize score by permanently refusing to advance.

Retain enemy attack/action memory fields as strong observations/features and diagnostics; do not require exhaustive T18-style manual rule coverage before training can begin.

### 7. Training-data contract

Specify a compact durable trajectory/branch record containing state fingerprint/observation, action sequence, horizon, before/after HP/state, enemy context, raw action/attack fields where available, score, worker/core/version, savestate hash/id and deterministic replay metadata.

This should support later search-teacher -> supervised policy distillation, with RL optional later rather than mandatory in V0.

### 8. Security / legal / repository boundaries

- No ROM, BIOS, copyrighted game assets or emulator binaries should be committed to this private application repository unless licensing explicitly permits it and PM separately approves.
- Keep the architecture compatible with user-supplied legally obtained game content/core installation.
- Do not touch `product/alpha/**` in this stage.
- Do not change current Collector's read-only/single-owner contract merely to simulate multi-instance training; the training farm is a separate lane.
- Do not weaken current Assist explicit-user-trigger safety boundaries in production; future autonomous emulator training is a controlled local research environment and must be isolated from live public gameplay adapters.

## Deliverables

Write only under a dedicated lane such as:

`parallel/WOF_HEADLESS_TRAINING_FARM_ARCHITECTURE/**`

plus this stage/canonical claim updates.

At minimum deliver:

- `RESULT.md` with the chosen primary/fallback emulator/core and rationale;
- implementation-ready `ARCHITECTURE.md`;
- `HEADLESS_HOST_CONTRACT.md`;
- `FLEET_BENCHMARK_PLAN.md` for the 5800H/32GB machine;
- `WOF_RAM_MAPPING_PLAN.md`;
- `SAVESTATE_FORK_SEARCH_V0.md`;
- machine-readable observation/action/result schema if useful;
- exact smallest next implementation stage with proposed stageId/dedupKey/write boundary.

No actual 10-instance local benchmark is required in this repository-only architecture stage unless a compatible runtime is already available to the worker. Do not fabricate performance numbers.

## Stop

PASS:

`PASS — WOF HEADLESS TRAINING FARM ARCHITECTURE V1 — IMPLEMENTATION-READY 10-WORKER FORK-SEARCH CONTRACT DEFINED`

BLOCKED:

`BLOCKED — WOF HEADLESS TRAINING FARM ARCHITECTURE V1 — <precise missing fact or incompatible dependency>`

Owner action: **NO** for this architecture stage.
