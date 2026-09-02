# Training Farm R0.4.5 — Headless Background Runtime Foundation V1 Result

Date: 2026-09-02
Stage: `TRAINING_FARM_R0_4_5_HEADLESS_BACKGROUND_RUNTIME_FOUNDATION_V1`
Dedup key: `training.farm.r0.4.5.headless-background-runtime-foundation-v1`
Status: **REPOSITORY FOUNDATION COMPLETE — REAL R0.2/R0.4 OWNER PROOF STILL REQUIRED**

## Verdict

The R0.4.5 repository-side headless/background runtime foundation is complete. It adds a strict future-runtime policy authority, ROM-free background-priority primitive, explicit CPU/RAM/worker budgets, deterministic foreground/idle/pressure/manual-pause controller with hysteresis/cooldown, no-host-input/no-focus safety checks, structured ROM-free diagnostics, and exact upstream design-authority documentation.

This stage starts **zero** real multi-worker WOF sessions, imports no RL stack, does not add Reward/Search/RL semantics, does not change R0.2/R0.4 proof semantics or identities, and does not claim a real-WOF PASS.

## Exact source candidate and current-main reconciliation

Exact completed source/documentation candidate:

`e80ca16f1a72cb8845788a295e6ffc3ac4514948`

Immediately before durable RESULT creation, current `main` was re-read and was exactly that candidate.

The implementation comparison from the pre-source current main `9d75d169228f84cb2840fd61fae9ccabcd85b051` to the candidate is 5 commits ahead and contains only five added R0.4.5 files. No pre-existing `training/farm/**` source, schema, test, Stable-Retro adapter, R0.2 determinism code, or R0.4 fork code changed.

Exact candidate blobs:

- `training/farm/background_runtime.py` — `12cb776323895d894be8efe273b9039355edee41`
- `training/farm/background_runtime_policy.example.json` — `a8c0909c198a51e175ebed27ed191f0b878ed821`
- `training/farm/background_runtime_policy.schema.json` — `9256abb940d3042acbc5aef7b13fbddd43f3856c`
- `training/farm/tests/test_background_runtime.py` — `7fd3de2a46acd35b611d77861e52ff820da49198`
- `training/farm/R0_4_5_HEADLESS_BACKGROUND_RUNTIME.md` — `2221e280257289f5ab337fad1b13c432cf82c1cc`

Git blob hashes from the isolated executable candidate were compared with the GitHub candidate blobs before closeout; all five exact authorities matched.

## Implemented runtime-policy foundation

The policy explicitly and fail-closed enforces:

- normal runtime `headless=true`;
- speaker output policy `audioOutput=discard`;
- `hostKeyboardInjection=false` and `hostMouseInjection=false`;
- `focusStealing=false`;
- gameplay input authority `emulator-core-api-only`;
- foreground-friendly/background process intent;
- strict non-coercive integers/booleans/enums and exact object keys;
- future configured worker ceiling `1..10`;
- foreground/idle/pressure targets constrained by that ceiling;
- explicit CPU budget percentage and memory budget MiB;
- high/recovery CPU and RAM thresholds plus scale-up cooldown;
- deterministic canonical JSON and SHA-256 policy identity;
- an R0.4.5 stage guard fixing `maxRealEmulatorWorkersThisStage=1` while real launch, real proof, and R0.5 authorization all remain false.

The checked-in example policy identity is:

`070c95490060f4993bb3c021add1bfad01fd7226abc373e0921ab0cbcf30bccd`

The example represents a future ceiling of 10 with target 2 during foreground activity, target 8 while idle, and target 1 under high pressure. These values are policy data for future consumption, not worker-launch authorization.

## Background priority primitive

The module uses no new dependency:

- Windows: stdlib `ctypes` invokes current-process `SetPriorityClass(..., BELOW_NORMAL_PRIORITY_CLASS)`;
- Linux: stdlib `os.getpriority/os.setpriority` applies positive niceness where permitted;
- unsupported/denied priority changes produce structured status rather than fabricating success or mutating proof authority;
- no elevation, registry edit, service/daemon install, or global host setting is performed.

This follows the inspected Sample Factory design lesson that worker renice is best-effort and permission failure must not kill the runtime.

## Foreground-friendly deterministic controller

The controller is decision-only and does not start/stop processes:

- `IDLE` -> configured higher allowed target;
- `FOREGROUND_ACTIVE` -> configured lower target;
- `PRESSURE_HIGH` -> configured minimum target;
- `MANUAL_PAUSE` -> zero allowed target;
- scale-down is immediate;
- pressure recovery requires both CPU/RAM recovery thresholds;
- scale-up is held by cooldown to prevent oscillation;
- non-monotonic load samples fail closed.

Dynamic host-load acquisition remains a future adapter concern. R0.4.5 exercises only deterministic supplied/fake samples and therefore adds no heavy system-probing dependency.

## No-host-input / no-focus safety boundary

The ROM-free diagnostic AST scanner rejects known host/global input packages and focus/input authority symbols including `pyautogui`, `keyboard`, `mouse`, `pynput`, AHK bindings, `SendInput`, `keybd_event`, `mouse_event`, `SetForegroundWindow`, `SetFocus`, and `SwitchToThisWindow` in scanned Training Farm Python paths.

Repository code search before closeout found no current matches for representative prohibited authorities `SendInput`, `pyautogui`, `SetForegroundWindow`, `pynput`, or `keybd_event` outside the newly added literal guard/documentation references.

The documentation explicitly distinguishes repository policy from external runtime guarantees: internal framebuffer generation/readback remains allowed even though visible game-window presentation is not required, and a future real-runtime stage must separately validate that its selected frontend/core honors headless operation.

## Upstream reuse / inspection record

No upstream tree was vendored and no upstream license boundary was crossed. Exact inspected design authorities:

- `Farama-Foundation/Stable-Retro@67cc456c42c9d0c62a7a8df5cf48627e2fd677a0` — reused the narrow emulator/environment boundary and reconstructable runtime-state architecture concept. Existing Farm Stable-Retro `0.9.8` proof authority was deliberately **not upgraded**.
- `MatPoliquin/stable-retro-scripts@35ef1c1611a06e3c2cd91e6d548139bc395f4fa7` — reused dependency separation/configuration-driven architecture guidance; no scripts or RL framework copied.
- `DLR-RM/stable-baselines3@3246f5060eacd8bff4de575eaafbbc6e0baac376` — reused only the conceptual separation of environment/fleet orchestration; no PPO/DQN/A2C, model, replay buffer, or SB3 dependency added.
- `JesseTG/libretro.py@439454d252dc8c0076b68ca29aa82cee84dac6bd` — reused the clean frontend/core adapter-boundary concept; no alternate libretro frontend added.
- `alex-petrenko/sample-factory@1dc7f6354070a55d8e748bee68f7e0a312fb5d14` — reused the best-effort worker-priority principle; no Sample Factory runtime/RL code copied.

WOF-specific strict policy schema/hash, stage guard, resource semantics, pressure controller, safety guard, proof disclaimers, and R0.5 lock are repository-original integration code.

## Compact implementation-owned self-check

One coherent ROM-free implementation self-check was run after the module was complete. No Fresh QA was opened.

Commands/operations exercised against the exact GitHub-blob-matched candidate reconstruction:

```bash
python -m compileall -q /tmp/r045/training
PYTHONPATH=/tmp/r045 python -m unittest discover -s /tmp/r045/training/farm/tests -v
PYTHONPATH=/tmp/r045 python -m training.farm.background_runtime \
  --policy /tmp/r045/training/farm/background_runtime_policy.example.json \
  --foreground-active --cpu-percent 42 --memory-percent 33 --at-ms 1000 \
  --skip-priority-apply
PYTHONPATH=/tmp/r045 python -m training.farm.background_runtime \
  --cpu-percent 95 --memory-percent 90 --at-ms 1000
```

Observed outcomes:

- bytecode compilation: PASS;
- module-owned unit tests: **11/11 PASS**;
- valid policy parse/roundtrip/canonical SHA: PASS;
- malformed/coercible/unknown-field rejection: PASS;
- worker ceiling exact bounds 1 and 10 plus 0/11 rejection: PASS;
- manual pause -> target 0: PASS;
- deterministic foreground/idle/high-pressure transitions, pressure hysteresis and scale-up cooldown: PASS;
- Windows priority success/permission-failure behavior via safe stub: PASS;
- Linux priority behavior via safe stub: PASS;
- no-host-input guard positive/negative fixtures: PASS;
- UTF-8 path with Chinese characters, spaces, and parentheses: PASS;
- ROM-free foreground diagnostic: `PASS`, policy SHA `070c9549...bccd`, `FOREGROUND_ACTIVE`, allowed target `2`, `realWorkersStarted=0`;
- ROM-free Linux priority diagnostic: `PASS`, actual diagnostic subprocess niceness `0 -> 10`, high-pressure allowed target `1`, `realWorkersStarted=0`;
- both CLI runs: `realWofProof=false`, `r0_5Authorized=false`, `realWorkerExecutionStarted=false`.

Targeted R0.1-R0.4 compatibility check is the exact Git comparison: the implementation candidate only adds the five listed R0.4.5 files. Existing direct Stable-Retro/FBNeo adapter and deterministic frame-step/proof code are byte-for-byte untouched by this stage.

The executable environment is an isolated ROM-free reconstruction because the connected GitHub interface does not expose a mounted repository checkout. Final GitHub blob SHA verification binds the executed reconstruction to the exact committed runtime/policy/schema/test/doc contents. This is implementation evidence only, not real-WOF proof.

## Proof boundary and next legitimate gate

No ROM bytes were used, read, copied, encoded, committed, logged, or distributed by this stage. Stable-Retro is not required for the R0.4.5 diagnostic. No real WOF emulator worker fleet was executed.

R0.2 and R0.4 real proof authority is unchanged and remains Owner-local/external. Fixture or ROM-free R0.4.5 evidence cannot unlock R0.5.

R0.5 remains locked until the existing authority path is satisfied:

1. **current-source real R0.2 WOF determinism PASS** on the Owner's legal local Stable-Retro/FBNeo + external ROM environment;
2. **current-source real R0.4 fork PASS** under the existing R0.4 authority contract;
3. a separate explicit PM authorization for R0.5 or later real multi-worker execution.

## Stop condition

**COMPLETE — TRAINING FARM R0.4.5 HEADLESS BACKGROUND RUNTIME FOUNDATION V1 — REPOSITORY FOUNDATION READY; REAL R0.2/R0.4 OWNER PROOF STILL REQUIRED**
