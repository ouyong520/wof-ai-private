# Training Farm R0.4.5 — Headless Background Runtime Foundation

Status: repository runtime-policy foundation only. This stage does **not** authorize R0.5 and does not claim a real-WOF proof.

## Intended 10训 operating mode

Future authorized Training Farm worker fleets consume a policy whose normal mode is headless, muted/discard-audio, background-friendly and no-focus. Gameplay input authority remains the emulator/core API only. Repository Training Farm code must not use host/global keyboard or mouse injection, `SendInput`, AutoHotkey gameplay control, focus switching, or foreground-window automation as gameplay authority.

The Owner is expected to keep Chrome, ChatGPT, Codex, VS Code, office applications, and other normal foreground work open while future training runs in the background. The controller therefore treats foreground activity and CPU/RAM pressure as explicit reasons to reduce the allowed future worker target rather than saturating the host.

“Headless” means no game-window presentation is required for normal training. It does not mean the emulator core stops producing pixels internally: framebuffer generation/readback may still be needed for observations, debugging contracts, or future model inputs. Audio data may likewise exist internally but normal Training Farm speaker output is discarded.

## Runtime policy authority

`background_runtime.py` owns a separate future-runtime policy authority. It is deliberately not mixed into the already-completed R0.2/R0.4 proof identities.

The policy is strict and fail-closed:

- `headless = true`;
- `audioOutput = discard`;
- host keyboard/mouse injection and focus stealing are false;
- `gameplayInputAuthority = emulator-core-api-only`;
- worker ceiling is a strict integer `1..10`;
- resource values reject booleans, strings, floats, unknown fields, and other coercible forms;
- configured foreground/idle/pressure targets must remain inside the worker ceiling;
- recovery thresholds must be below their pressure-high thresholds;
- the canonical JSON form is sorted and compact, producing a deterministic SHA-256 policy identity;
- the R0.4.5 `stageGuard` fixes `maxRealEmulatorWorkersThisStage = 1` and keeps real worker launch, real-WOF proof, and R0.5 authorization false.

The checked-in example uses a future ceiling of 10, target 2 while the Owner is active, target 8 while idle, and target 1 under high pressure. These are configurable policy examples, not permission to launch those workers. R0.4.5 never starts a real emulator worker fleet.

## Foreground-friendly controller

`ForegroundFriendlyController` consumes deterministic load samples and returns a decision only:

- `IDLE` -> configured idle target;
- `FOREGROUND_ACTIVE` -> configured foreground target;
- `PRESSURE_HIGH` -> configured minimum/pressure target;
- `MANUAL_PAUSE` -> zero new work.

Pressure entry and any scale-down are immediate. Recovery requires CPU and memory to fall below separate recovery thresholds, and scale-up is held by a configurable cooldown. This provides hysteresis and avoids rapid oscillation. The controller itself never creates, terminates, or signals a process.

Dynamic host-load acquisition is intentionally left behind a future adapter boundary. This stage needs no `psutil` or other new dependency; fake deterministic samples exercise the policy.

## Background priority primitive

The runtime foundation exposes a best-effort current-process priority reduction:

- Windows: stdlib `ctypes` -> `SetPriorityClass(..., BELOW_NORMAL_PRIORITY_CLASS)`;
- Linux: stdlib `os.getpriority/os.setpriority` -> positive niceness where permitted;
- unsupported or denied operations are returned as structured status and do not mutate R0.2/R0.4 proof authority.

No elevation, registry edits, service/daemon installation, or global system configuration is used.

## No-host-input / no-focus guard

The ROM-free diagnostic AST-scans Training Farm Python paths for known host-input imports (`pyautogui`, `keyboard`, `mouse`, `pynput`, AHK bindings) and known host/focus authority symbols such as `SendInput`, `SetForegroundWindow`, and `SetFocus`.

This is a repository guarantee for scanned adapter/gameplay paths, not a claim that an arbitrary third-party emulator can never create a window. Future real-runtime validation must separately verify that its selected frontend/core configuration honors the policy.

## ROM-free diagnostic

No ROM and no Stable-Retro installation are required:

```bash
python -m training.farm.background_runtime \
  --policy training/farm/background_runtime_policy.example.json \
  --foreground-active \
  --cpu-percent 42 \
  --memory-percent 33 \
  --at-ms 1000
```

For a read-only priority demonstration:

```bash
python -m training.farm.background_runtime --skip-priority-apply
```

The JSON output includes the effective policy and SHA-256, priority application result, resource budget, supplied load sample, controller state/allowed target, safety-guard result, and explicit `realWofProof=false`, `r0_5Authorized=false`, `realWorkerExecutionStarted=false` fields.

Paths are normal `pathlib`/UTF-8 paths; Chinese characters, spaces, and parentheses are not special-cased or hard-coded.

## Upstream architecture/design inspection

No upstream source tree is vendored. R0.4.5 records small architecture patterns only:

| Project | Exact inspected authority | Reused guidance | Not imported into this stage |
| --- | --- | --- | --- |
| Farama Stable-Retro | `Farama-Foundation/Stable-Retro@67cc456c42c9d0c62a7a8df5cf48627e2fd677a0` | keep emulator/core behind a narrow environment/backend boundary; keep live emulator resources out of portable orchestration state | no Stable-Retro upgrade; repository R0.1-R0.4 remains pinned to its existing `0.9.8` authority |
| stable-retro-scripts | `MatPoliquin/stable-retro-scripts@35ef1c1611a06e3c2cd91e6d548139bc395f4fa7` | keep emulator/training dependencies separable and configuration-driven rather than vendor a second framework | no scripts tree or RL stack copied |
| Stable-Baselines3 | `DLR-RM/stable-baselines3@3246f5060eacd8bff4de575eaafbbc6e0baac376` | environment/fleet orchestration is a separate layer from the environment itself | no PPO/DQN/A2C, model, replay buffer, or SB3 dependency |
| libretro.py | `JesseTG/libretro.py@439454d252dc8c0076b68ca29aa82cee84dac6bd` | maintain a clean frontend/core callback/adapter boundary suitable for headless automation | no alternate libretro frontend is introduced |
| Sample Factory | `alex-petrenko/sample-factory@1dc7f6354070a55d8e748bee68f7e0a312fb5d14` | worker niceness/renice is best-effort; permission failure must be observable without killing the worker | no Sample Factory worker runtime or RL code is copied |

The WOF-specific strict policy schema/hash, stage guard, resource-budget semantics, pressure state machine, safety scan, and proof/R0.5 disclaimers are original repository integration code.

## Future 2/4/8/10 consumption boundary

A later explicitly authorized fleet layer may bind a worker/fleet generation to the policy SHA and ask the controller for an allowed target. It should separately own process launch, load probing, graceful drain/pause, and per-worker Stable-Retro lifecycle. R0.4.5 provides those decision contracts only and starts zero real multi-worker WOF sessions.

The current legal gate is unchanged:

1. obtain a **current-source real R0.2 WOF determinism PASS** on the Owner's legal local Stable-Retro/FBNeo + external ROM environment;
2. obtain the required **current-source real R0.4 fork PASS** under its existing authority contract;
3. only then may PM explicitly authorize R0.5 or a later real multi-worker stage.

Fixture/ROM-free R0.4.5 diagnostics never unlock R0.5.
