# Training Farm R0.4.5 — Headless Background Runtime Foundation V1

## PM authority / dedup

- stageId: `TRAINING_FARM_R0_4_5_HEADLESS_BACKGROUND_RUNTIME_FOUNDATION_V1`
- dedupProtocol: `v2`
- dedupKey: `training.farm.r0.4.5.headless-background-runtime-foundation-v1`
- dedupMode: `exclusive`
- canonical claim path: `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.5.headless-background-runtime-foundation-v1.json`
- stage claim path: `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_5_HEADLESS_BACKGROUND_RUNTIME_FOUNDATION_V1.json`

Canonical dedup v2 is mandatory. Before any mutation, re-read current `main`, this prompt, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/TESTING_CADENCE_POLICY.md`, current R0.2/R0.4 durable RESULTs, and search for equivalent claims/results/prompts. If equivalent work is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`. If validly claimed, stop `ALREADY CLAIMED — SAFE TO CLOSE`. Do not steal stale claims; only PM-authorized recovery may supersede them.

## Context

Training Farm R0.1-R0.4 repository implementation is already substantially complete. R0.2 real-WOF determinism and R0.4 real fork smoke still require Owner-local Stable-Retro/FBNeo execution with an external legally held ROM. Owner-local environment setup is proceeding independently.

This stage exists so repository development does not idle while local proof prerequisites are being prepared. It is **pre-R0.5 infrastructure**, not R0.5 itself.

Owner's long-term requirement for “10训” is strict:

- background execution while Owner keeps using the Windows foreground normally;
- headless: no game windows in normal training;
- muted: no audible game output;
- no focus stealing;
- no OS/global keyboard or mouse injection;
- no `SendInput`, AutoHotkey gameplay control, key-window switching, or foreground window automation;
- all gameplay actions through emulator/core API only;
- foreground-friendly CPU/RAM behavior with explicit resource budgets;
- future 2/4/8/10 worker scaling must be able to reduce load rather than simply saturate the machine.

## Hard scope boundary

This task MAY implement repository-side background/headless/runtime-policy foundations that can be fully tested ROM-free.

This task MUST NOT:

- claim or fabricate a real R0.2/R0.4 PASS;
- modify proof semantics to make local proof easier;
- change `realWofProof`, proof-scope, runtime/ROM/source identity acceptance, determinism, or fork authority;
- start R0.5 Reward/Search semantics;
- run or orchestrate 2+ real WOF emulator workers;
- add PPO/DQN/A2C or any RL algorithm;
- guess WOF semantic RAM addresses;
- implement teacher/safe-path policy;
- download, vendor, copy, commit, encode, split, or distribute ROM/BIOS/game assets;
- modify `product/alpha/**`, Alpha release/proof, Transport, Recorder, PYLAUNCH, WinKawaks Collector.

A fixture/fake-backend check never unlocks R0.5.

## Upstream reuse rule

Before implementing generic infrastructure, inspect maintained upstreams and reuse design/API patterns where appropriate instead of re-inventing them:

- `Farama-Foundation/Stable-Retro`
- `MatPoliquin/stable-retro-scripts`
- `DLR-RM/stable-baselines3`
- `JesseTG/libretro.py`
- `alex-petrenko/sample-factory`

Do not vendor large upstream trees. Record exact upstream project/commit/version references used as design authority. Preserve license boundaries. Prefer small adapters around maintained dependencies over copied frameworks.

## Required implementation

### 1. Strict Training Farm runtime policy contract

Create a narrow runtime-policy module under `training/farm/**` plus structured schema/example as appropriate.

The policy must make these invariants explicit and fail closed:

- `headless = true` for normal Training Farm execution;
- `audioOutput = disabled/discard` for normal Training Farm execution;
- `hostKeyboardInjection = false`;
- `hostMouseInjection = false`;
- `focusStealing = false`;
- gameplay input authority is emulator/core API only;
- foreground-friendly/background process intent is explicit;
- resource budget values use strict non-coercive types/ranges;
- future worker ceiling is representable up to 10, but **this stage must not execute more than one real emulator worker**;
- malformed/coercible/unknown policy fields are rejected;
- serialized policy has a deterministic canonical identity/hash for future worker/fleet binding.

Do not make this policy part of existing R0.2/R0.4 proof identity unless absolutely required; avoid invalidating completed proof implementation candidates. Prefer a separate future-runtime policy authority.

### 2. Background process priority primitive

Implement a small cross-platform best-effort primitive for the current process and/or future worker child process launch:

- Windows: background/below-normal process priority using supported stdlib/Win32 calls; no elevation, registry mutation, service installation, or global system setting;
- Linux: best-effort positive niceness where permitted;
- failure to lower priority must be observable in structured status but must not silently mutate proof authority.

No daemon/service installation in this stage.

### 3. Resource budget foundation

Implement strict resource budget data structures/configuration for future scaling. At minimum represent:

- configured worker ceiling (1..10);
- foreground-active worker target;
- idle worker target;
- process priority intent;
- CPU budget percentage;
- memory budget MiB or equivalent explicit bound;
- overload/backoff thresholds and hysteresis primitives if implemented;
- pause/resume state representation.

This stage may implement policy evaluation and fake/fixture scheduling decisions, but MUST NOT start 2+ real WOF emulator workers.

If dynamic system-load probing would require a new dependency, prefer a clean optional adapter interface and deterministic fake probe tests rather than adding a heavy dependency without necessity.

### 4. Headless/no-host-input safety guard

Add module-owned checks that make accidental regressions obvious. Examples:

- static or runtime guard ensuring Training Farm gameplay paths do not import/use known host-input primitives (`SendInput`, pyautogui, AutoHotkey integrations, global keyboard/mouse packages) as gameplay authority;
- ensure background foundation does not create a visible game window or request focus;
- document that internal framebuffer generation/readback is allowed while display/window presentation is not required;
- audio data may be discarded; no speaker output required.

Do not overclaim that an external library can never create a window; distinguish repository policy/adapter guarantees from future real-runtime validation.

### 5. Foreground-friendly controller primitive

Implement a deterministic controller/state machine that can later map system-load state to an allowed worker target, for example:

- `IDLE` -> higher allowed target;
- `FOREGROUND_ACTIVE` -> lower target;
- `PRESSURE_HIGH` -> minimum target or pause;
- explicit manual pause -> zero new work;
- recovery uses hysteresis/cooldown so it does not oscillate rapidly.

For this stage, exercise it only with deterministic fake load samples. No real multi-worker WOF execution.

The long-term intended policy is roughly:

- Owner active: 2-4 workers when later authorized;
- machine idle: 8-10 workers when later authorized;
- high CPU/RAM pressure: reduce workers or pause;

but do not hard-code unsafe assumptions. Make limits configurable and strict.

### 6. CLI / diagnostics

Provide an obvious ROM-free CLI or diagnostic command that prints structured JSON showing:

- effective runtime policy;
- background-priority application result;
- resource budget;
- controller decision for supplied/fake load state;
- confirmation that no real WOF proof or R0.5 authorization is being claimed.

It must be safe to run without ROM and without Stable-Retro.

### 7. Documentation

Document:

- normal 10训 operation is headless/muted/background;
- Owner may keep Chrome/ChatGPT/Codex/VS Code/office apps in foreground;
- no host keyboard/mouse gameplay automation;
- why framebuffer computation may still exist internally despite “no screen”;
- how this foundation will later be consumed by 2/4/8/10 workers;
- exact boundary that real R0.2/R0.4 proof is still external/Owner-gated and R0.5 remains locked.

Also record any upstream projects/commits inspected and exactly what was reused as architecture/API guidance versus what remains original WOF-specific code.

## Integration constraints

- Preserve the existing direct Stable-Retro/FBNeo adapter and deterministic frame-step semantics.
- Do not introduce window focus or host input dependencies.
- Do not change current R0.2/R0.4 schemas/results merely to integrate this module.
- Do not make local filesystem path `F:\三国\三国10训` a repository-global hard-coded path. Local workspace paths belong to local bootstrap/config, not portable source authority.
- Windows Chinese/space/parentheses paths must remain safe wherever this module accepts local paths.
- No ROM bytes in tests, fixtures, RESULT, package, Git, or logs.

## Implementation-owned self-check

After the coherent module is complete, run one compact implementation self-check rather than QA-per-patch. Cover at least:

- strict valid policy parse/roundtrip/hash;
- malformed/coercible/unknown-field rejection;
- worker ceiling bounds including 1 and 10;
- manual pause behavior;
- deterministic fake controller transitions including hysteresis/backoff;
- Windows priority primitive behavior via safe mock/stub when not on Windows;
- Linux niceness behavior via safe mock/stub when not on Linux;
- no host input/window-focus authority in the module;
- ROM-free CLI structured output;
- existing R0.1-R0.4 implementation tests or targeted compatibility checks sufficient to show no material regression to proof code.

Do not call fixture evidence real WOF proof.

## Durable RESULT and closeout

Write a durable RESULT under an appropriate `parallel/TRAINING_FARM_R0_4_5_HEADLESS_BACKGROUND_RUNTIME_FOUNDATION_V1/RESULT.md` path containing:

- exact source candidate and current-main reconciliation;
- exact files/blobs changed;
- upstream reuse/inspection record;
- self-check commands and observed outcomes;
- explicit statement that no real-WOF proof was claimed;
- explicit statement that R0.5 remains locked pending current-source real R0.2 + R0.4 PASS;
- exact next legitimate gate.

Then token-verify and close both canonical and stage claims to COMPLETE. Do not stop at ACTIVE/LOCKED/WAITING if repository implementation is actually done.

## Stop condition

Only:

- `COMPLETE — TRAINING FARM R0.4.5 HEADLESS BACKGROUND RUNTIME FOUNDATION V1 — REPOSITORY FOUNDATION READY; REAL R0.2/R0.4 OWNER PROOF STILL REQUIRED`
- precise irreducible `BLOCKED — <exact external/repository blocker>`
- canonical duplicate stop.
