# Local Codex All-In-One Start Prompt

Repo authority:

`parallel/PM/OWNER_LOCAL_CODEX_ALL_IN_ONE_EXECUTION_AUTHORITY_20260907.md`

Owner intent: one long-lived local Codex thread should run the WOF program end-to-end across Alpha mainline, Unified Collector, and Training Farm / 10训. Do not split into separate product / PM / technical chat threads unless a genuinely isolated emergency makes that unavoidable.

## Start here

1. Fresh-read latest remote state, do not trust this prompt's creation-time HEAD as current truth.
2. Read and obey:
   - `AGENTS.md`
   - `PROJECT_PRODUCT_GOVERNANCE.md`
   - `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
   - `COLLECTOR_ROUTING.md`
   - `parallel/PM/OWNER_LOCAL_CODEX_ALL_IN_ONE_EXECUTION_AUTHORITY_20260907.md`
3. Fresh-read current Alpha dispatch/results/claims/progress, current Training Farm state, and the separate `ouyong520/wof-winkawaks-bridge` main/state.
4. Do not steal ACTIVE claims, reopen COMPLETE stages, or revive superseded work.
5. Use local branch/worktree execution; avoid implementation through repeated create-only remote GitHub writes.

## Repositories

Main program:

`https://github.com/ouyong520/wof-ai-private`

Unified Collector runtime:

`https://github.com/ouyong520/wof-winkawaks-bridge`

If local copies already exist, fetch/reconcile them instead of recloning blindly.

Suggested branches:

- `wof-ai-private`: `codex/local-all-in-one`
- `wof-winkawaks-bridge`: `codex/local-unified-collector`

Do not force-push shared history.

## Integrated mission

Drive all three lines in one sustained execution loop:

### A. Alpha mainline

Keep the final user-visible target in view:

```text
start game
-> 0 click / 0 manual seed
-> auto P1/P2/P3
-> visible useful HUD near correct player
-> correct X/Y orientation
-> stable follow/reacquire
-> ambiguity fail-closed
-> truthful Browser/renderer authority when promoted
```

Fresh-read the current P49/P47/P48/P43/P45/P46 authority before doing anything live.

At the authority handoff preparation point, P49 was COMPLETE and one bounded Owner diagnostic budget remained unused. Do not consume any one-shot real-game budget without fresh proof that the current authority still permits it and without explicit Owner approval for the real/manual run.

Preserve the truthful unresolved renderer-source blocker if still current:

`NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`

Do not convert diagnostic pixel/WebGL/correlation evidence into fake renderer authority.

### B. Unified Collector / 采集

Treat existing V12 as the maintained Collector product, not something to rebuild from scratch.

Expected architecture to fresh-verify:

```text
START_WOF_UNIFIED_COLLECTOR.bat
-> lifecycle
-> unified_collector_agent
-> browser-wasm / winkawaks / stable-retro-fbneo adapters
-> one tasks/queue + status/by_task + results/by_task plane
```

Collector stays read-only/no input injection.

Use it for real acquisition, data quality, long-session capture, source-aware evidence ingestion/query, and concrete missing capabilities needed by Alpha/Training.

Do not create a second Collector stack unless a real defect proves necessary.

### C. Training Farm / 10训

Treat real ten-worker end-to-end operation as a product objective that must be verified, not assumed.

Fresh-read all Training Farm authority first.

Known boundary at takeover preparation:

- source namespace is `stable-retro-fbneo`;
- R0.2 determinism / R0.4 fork / R0.4.7 Windows portable real-WOF proof tooling exist;
- Training Farm V11 source-owned exporter exists;
- Unified Collector can read up to 10 worker export records;
- the 10-worker exporter fixture is ROM-free and launches zero real emulator workers;
- exporter code itself does not launch/schedule/scale real workers.

Therefore determine from current Git whether true real 1->2->4->8->10 orchestration already exists. If not, implement the smallest reliable real orchestration path, with:

- deterministic worker identity/generation;
- clean start/stop/restart;
- per-worker Stable-Retro/FBNeo isolation;
- savestate/action experiment support;
- resource/health telemetry;
- failure isolation;
- source-owned exporter publication;
- Unified Collector ingestion;
- bounded evidence/trajectory retention;
- staged scaling 1 -> 2 -> 4 -> 8 -> 10.

Do not start at 10 if smaller scale exposes a real defect. Fix and continue automatically.

Training input automation stays inside the emulator/core API only. No OS/global keyboard, Browser, or WinKawaks input injection.

## Cross-line workflow

Use one thread and coordinate the three lines instead of pretending they are one source:

```text
Collector = observe/calibrate
Training Farm = controlled action/fork experiments
Alpha/Browser = production-context validation
```

Never assume offsets are equal across `browser-wasm`, `winkawaks`, and `stable-retro-fbneo`.

Use explicit provenance for any cross-source mapping.

If one lane waits for Owner/manual input, continue productive work in the other lanes.

## Same-machine resource rule

Do not run an important canonical WinKawaks capture at the same time as a heavy 8/10-worker Training Farm load unless measurements prove it safe.

Default:

```text
critical Collector capture
-> pause/cap heavy Training Farm
-> finish capture
-> resume Training Farm
```

Also avoid heavy farm load during timing-sensitive Alpha browser/render diagnostics.

## Environment protection

Hard constraints:

- do not delete/modify unrelated Python installations;
- do not globally change PATH/site-packages;
- do not reinstall system Python;
- use/reuse project-specific venvs;
- do not delete unrelated venv/conda/uv/pyenv environments;
- do not modify `D:\Reasonix` or unrelated projects;
- do not commit ROM/BIOS/game/savestate/emulator binaries.

For Alpha, preserve/reuse the dedicated managed interpreter when current authority still uses it:

`%LOCALAPPDATA%\WOF Alpha Current Main\venv\Scripts\python.exe`

## Working style

Do not stop after each small patch.

Run this loop continuously:

```text
fresh-read -> diagnose -> implement coherent slice -> cheap self-check
-> batched focused regression at coherent boundary
-> commit/push -> fresh-read -> continue
```

Prefer local Git commits and coherent pushes over remote file-by-file mutation.

Do not ask the Owner to choose routine next steps.

Ask only for truly manual/legal/irreversible items such as:

- legal ROM selection/path if unavailable;
- explicit real-game interaction;
- one-shot/budget-consuming live execution;
- credentials/access;
- destructive action;
- product behavior tradeoff requiring Owner choice.

Before any non-terminal stop, write durable Git progress with exact repo/branch/head, completed work, tests, remaining work, blocker and next action.

## Immediate first pass

On first run, do not start coding blindly. Produce a concise local takeover inventory from fresh Git state covering:

1. Alpha: current exact terminal/active stages, live-run budget, current highest-value product blocker;
2. Collector: current `wof-winkawaks-bridge` main, V12 health/entrypoint status, outstanding real acquisition issues;
3. Training: current real-proof/orchestration state, exact evidence for whether real 10-worker scheduling exists;
4. local machine: existing repo paths, clean/dirty state, relevant WOF venvs/runtime prerequisites, without modifying unrelated environments;
5. one integrated execution plan ordered by real dependency and user-visible value.

Then execute that plan automatically. Do not wait for a separate PM/Worker chat split.

Terminal behavior for this long-running thread is not "one stage finished". Continue until the program hits a genuinely Owner-required blocker or the major Owner goals are materially delivered.
