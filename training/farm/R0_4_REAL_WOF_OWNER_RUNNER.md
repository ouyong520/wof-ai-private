# Training Farm R0.4 Real-WOF Proof Owner Runner

This package is the Windows-first Owner entry point for the remaining real Training Farm authority gate. It orchestrates the existing R0.2 determinism CLI and existing R0.4 deterministic fork CLI; it does not reimplement their emulator logic and does not implement R0.5.

## One Owner command

From a Windows checkout of the repository:

```cmd
training\farm\run_real_wof_proof.cmd
```

The wrapper changes to the repository root and prefers `py -3`, then `python`. The Python implementation underneath is:

```text
python -m training.farm.real_wof_proof_owner_runner
```

Linux invocation is supported for development/runtime parity, but Windows is the primary Owner path.

## Required local prerequisites

The runner fails closed before real execution unless all of these are true:

- source namespace is exactly `stable-retro-fbneo`;
- platform is Windows or Linux;
- Python is within the current Training Farm supported range;
- `stable-retro==0.9.8` is installed and FBNeo capability probes pass;
- `WOF_ROM_PATH` is set to an absolute, readable `.zip` file outside this repository;
- that ROM can be SHA-256 hashed in place;
- current R0.2/R0.4 CLIs, schemas, and the bounded fork plan are present;
- the local evidence directory is writable and outside the repository.

The runner never downloads ROMs, BIOS files, emulator binaries, or game assets. It never copies ROM bytes, savestate bytes, raw RAM dumps, BIOS/core binaries, or copyrighted assets into Git.

## What it runs

1. Current-source R0.2 real determinism using `determinism_actions.example.json`, exactly 8 frames and 3 repetitions.
2. It validates the resulting JSON against the repository schema surface and strict R0.2 semantic proof consumer. Required authority includes `PASS / DETERMINISM_MATCH`, `REAL_WOF`, `realWofProof=true`, complete checkpoints, strict real Stable-Retro/FBNeo identity, current Farm candidate identity, and the exact preflight ROM SHA-256.
3. Only after that exact R0.2 proof validates, it runs current-source R0.4 with `real_wof_fork_smoke.plan.json` and passes the exact R0.2 JSON path to the existing R0.4 proof gate.
4. It validates R0.4 as `PASS / FORK_SET_DETERMINISTIC`, `REAL_WOF_FORK`, `realWofProof=true`, with the exact fork plan, accepted exact R0.2 run/runtime identity, current ROM/Farm identity, complete branches, repeated deterministic outcomes, and no resume reuse.

Fixture/synthetic PASS is never accepted as the real gate.

## Evidence location

By default evidence is written outside the repository:

- Windows: `%LOCALAPPDATA%\WofTrainingFarm\real-proof\<UTC-run-id>\`
- Linux: `$XDG_STATE_HOME/WofTrainingFarm/real-proof/<UTC-run-id>/`, or `~/.local/state/...` when `XDG_STATE_HOME` is unset.

Each invocation creates a new unique directory and never merges with earlier runs or another ROM/source identity.

Compact files are:

```text
r0_2_real_determinism.json
r0_4_real_fork_smoke.json       # only when R0.2 passed and R0.4 ran
summary.json
summary.txt
```

A custom evidence root may be supplied with `--evidence-root`, but repository-internal paths are rejected.

## Final states

The console and summary report one unambiguous outcome:

```text
PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE
WAITING_PREREQUISITE — <exact missing local prerequisite>
BLOCKED — R0.2 REAL DETERMINISM — <exact failure>
BLOCKED — R0.4 REAL FORK SMOKE — <exact failure>
```

A fixture result, malformed/coercible JSON, stale Farm candidate, wrong ROM, wrong proof scope, partial fork, non-deterministic branch, source drift, or proof identity mismatch cannot become PASS.

## Source drift protection

The runner records a hash over the current R0.2/R0.4 source/schema/plan surface before execution and recomputes it before/after each proof stage. If those files change during the Owner run, the run blocks rather than combining evidence from different candidates. The R0.2 runtime identity is also required to equal the current Farm source identity.

## Scope boundary

This package does not establish WOF semantic memory addresses, Reward, search policy, best-branch selection, beam/MCTS/A*, PPO/SB3/RL, multi-worker orchestration, safe-route advice, Browser/Alpha authority, or WinKawaks authority.

After a legitimate real PASS, PM may consume that durable local evidence as the real R0.2 determinism gate and real R0.4 fork smoke authority for the next separately authorized Training Farm stage. A repository fixture PASS alone cannot authorize R0.5.
