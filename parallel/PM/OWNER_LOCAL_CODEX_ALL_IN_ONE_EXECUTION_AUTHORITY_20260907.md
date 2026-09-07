# Owner Local Codex All-In-One Execution Authority — 2026-09-07

Status: **OWNER AUTHORIZED**

Prepared from `wof-ai-private` main:

`d4c204f38fcf60efeb269a60b36be318d8d08bdf`

This document records an explicit Owner cross-line authorization under `AGENTS.md` / `PROJECT_PRODUCT_GOVERNANCE.md`.

## 1. Owner operating decision

The Owner no longer wants the WOF program split into many short-lived product / PM / technical / Worker chat threads.

The new preferred operating model is:

```text
ONE long-lived local Codex thread
= product prioritization
+ technical diagnosis
+ code implementation
+ local tests
+ local runtime diagnosis
+ Git commit/push
+ durable progress/handoff
+ next-step selection
```

The same local Codex thread is explicitly authorized to work across all three WOF product lines:

1. Alpha mainline product;
2. Unified Collector / data acquisition;
3. Training Farm / 10训.

This is an **execution/orchestration unification**, not a semantic/source-authority merge.

Do not create separate chats merely because work crosses Alpha / Collector / Training boundaries. Prefer one sustained local execution loop until a real Owner/manual blocker is reached.

## 2. Product/source boundaries remain strict

The following namespaces remain distinct:

```text
browser-wasm
winkawaks
stable-retro-fbneo
```

Do not silently copy numeric addresses/offsets, runtime identity, causal authority, timing assumptions or input permission from one namespace into another.

Cross-line evidence may be correlated only with explicit provenance.

The preferred high-level loop is:

```text
Collector observation / calibration
-> Training Farm controlled action experiments
-> candidate interpretation / policy / rule
-> Alpha / Browser real-product validation
```

But each source keeps its own authority.

## 3. Safety boundaries

### Alpha / Browser

Keep existing production safety and acceptance rules. Do not weaken proof criteria just to make UI appear.

Current Alpha safety remains:

```text
readOnly=true
ramWrites=0
inputInjection=false
```

Do not promote or move alpha-live unless the exact existing guarded promotion authority allows it.

### Unified Collector

Collector remains observation-only:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

Collector is not an autoplay engine and must not choose gameplay actions.

### Training Farm / 10训

Programmatic gameplay actions are allowed only inside the isolated Stable-Retro / FBNeo Training Farm environment and only through its existing emulator/core action boundary.

Do not use OS/global keyboard injection, Browser input automation, WinKawaks input automation, SendInput, focus automation or similar cross-runtime shortcuts.

Do not commit ROMs, BIOS, copyrighted game assets, savestates, emulator cores or third-party binaries.

## 4. Current Alpha mainline truth

Current main dispatch at the preparation point is revision 34:

`ALPHA_V1_GSTYPHOON_MAPPING_OWNER_WINDOWS_ONE_RUN_HANDOFF_V1`

P49 is terminal COMPLETE.

Exact P49 terminal authority:

- result stage: `ALPHA_V1_PRODUCT_TAKEOVER_P49_OWNER_WINDOWS_ONE_RUN_HANDOFF_BRIDGE`
- testedCommit: `fad9780dc7a542027ba622e2b010a63b2f085eee`
- current main containing terminal result: `d4c204f38fcf60efeb269a60b36be318d8d08bdf`
- P47 readiness: `READY_FOR_ONE_BOUNDED_OWNER_DIAGNOSTIC`
- remaining one-run budget: `1`
- P49 worker did **not** run real WOF
- P49 worker did **not** consume the remaining run budget
- promotion not performed
- alpha-live not moved

The exact P49 one-run handoff entrypoint is:

`parallel/OWNER_DIAGNOSTIC/WOF_ALPHA_P49_OWNER_WINDOWS_ONE_RUN_HANDOFF.cmd`

The managed Alpha interpreter remains:

`%LOCALAPPDATA%\WOF Alpha Current Main\venv\Scripts\python.exe`

Do not delete, reinstall, upgrade, downgrade or repurpose unrelated/global Python environments.

Important unresolved Alpha authority truth remains:

`NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`

P40 is still a truthful BLOCKED authority boundary. P43/P45/P46 diagnostic tooling improves observability/correlation; it must not be re-labeled as a direct renderer proof unless a later real source mapping truly satisfies the existing contract.

Alpha product goal remains Owner-facing reality:

```text
start game
-> zero click / zero manual seed
-> automatically acquire P1/P2/P3
-> visible useful HUD near the correct player
-> stable follow / reacquire
-> no Y inversion
-> fail closed on ambiguity
-> later upgrade diagnostic correlation to truthful renderer authority
```

Do not let internal proof machinery indefinitely prevent useful diagnostic visibility; keep diagnostic vs production authority labels explicit.

## 5. Current Unified Collector truth

Repository:

`ouyong520/wof-winkawaks-bridge`

At this authority preparation, current Collector main is:

`d693b0f0e471b937f9ab07b3d8c56c5b5ac81249`

Unified Collector V12 terminal integration is already COMPLETE.

The terminal maintained architecture is one Collector product:

```text
START_WOF_UNIFIED_COLLECTOR.bat
  -> bridge.collector_lifecycle
     -> bridge.unified_collector_agent
        -> browser-wasm adapter
        -> winkawaks adapter
        -> stable-retro-fbneo adapter
```

There is one Git control/result plane:

```text
tasks/queue
status/by_task
results/by_task
```

Do not build a second queue, catalog, warehouse, planner, analysis engine or source-specific Collector service unless a concrete defect proves the current terminal architecture insufficient.

Collector development should now be driven by real operational needs, data-quality defects, missing acquisition capability, or integration requirements from the mainline / Training Farm — not by version-number churn.

## 6. Current Training Farm / 10训 truth

Training Farm lives in:

`training/farm/**`

Source namespace:

`stable-retro-fbneo`

Existing real-WOF proof path includes R0.2 determinism, R0.4 fork proof, Windows bootstrap / Owner runner, and the R0.4.7 portable real-WOF proof bundle.

R0.4.7 packaging itself does **not** prove real WOF; real proof remains Owner-local.

Unified Collector V11 added a source-owned Training Farm read-only exporter. It can expose evidence from already-running Training Farm workers and Unified Collector may select up to 10 worker records.

However this must not be misread as proof that real ten-worker emulator orchestration is already complete:

- `training.farm.collector_export` does not launch/schedule/scale workers;
- the existing ten-worker exporter validation is ROM-free fixture evidence;
- the fixture performs zero real worker launches;
- real 10训 orchestration/runtime capability must be fresh-read from Git and implemented/proven if absent.

Therefore the local Codex takeover should treat **real 10训 end-to-end runtime** as a concrete product objective, not as already-delivered merely because a 10-worker exporter fixture exists.

Target Training Farm direction:

```text
legal local WOF ROM
-> deterministic Stable-Retro/FBNeo worker runtime
-> 1 -> 2 -> 4 -> 8 -> 10 controlled worker scale
-> isolated savestate/action experiments
-> per-worker identity / generation / resource telemetry
-> source-owned read-only exporter
-> Unified Collector ingestion/query
-> durable trajectory / branch evidence
-> mainline research consumption
```

Do not jump directly to 10 workers if 1/2/4 scaling exposes determinism, resource, lifecycle or identity defects. Fix the real bottleneck and continue automatically.

## 7. One-thread local execution rules

The local Codex thread should operate continuously:

```text
fresh-read Git
-> inspect durable state / claims / results
-> choose highest-value real blocker
-> implement coherent fix/feature
-> cheap local self-check while coding
-> run one focused/batched regression at coherent boundary
-> commit
-> push
-> fresh-read pushed state
-> continue
```

Do not stop after every small patch to ask the Owner what to do next.

Do not open a new chat or a new micro-stage simply because a task crosses a product boundary.

Do not create multiple artificial Workers just to fill capacity.

The same Codex thread may alternate between Alpha, Collector and 10训 according to dependency and machine availability.

## 8. Git / branch discipline

GitHub remains durable authority.

Before any mutation:

1. `git fetch --all --prune`;
2. fresh-read latest `origin/main` for each relevant repo;
3. inspect current claims / RESULT / PROGRESS / recent equivalent commits;
4. do not steal an ACTIVE claim;
5. do not reopen a COMPLETE stage;
6. do not revive superseded work;
7. reconcile any local uncommitted work before changing branches.

Prefer a long-lived local Codex work branch / worktree per repository over direct concurrent edits to remote `main`.

For `wof-ai-private`, a suggested branch name is:

`codex/local-all-in-one`

For `wof-winkawaks-bridge`, a suggested branch name is:

`codex/local-unified-collector`

Commit and push coherent milestones. Avoid many create-only remote GitHub writes while implementation is still in flux.

Do not force-push or rewrite shared history unless the Owner explicitly requests it.

## 9. Durable progress without chat fragmentation

One long Codex thread does not mean chat-only state.

Before any non-terminal stop, context reset, reboot, or handoff, write a concise durable checkpoint in Git containing:

- exact repo/head/branch;
- current objective;
- completed implementation;
- tests actually run;
- remaining work;
- exact blocker if any;
- local runtime state that matters;
- next command/action.

For pre-existing stage claims, continue to respect their exact claim token / RESULT / PROGRESS semantics.

For new all-in-one local work, do not manufacture dozens of tiny claims. Use coherent stage boundaries and durable Git checkpoints only when they materially help dedup, recovery or acceptance.

## 10. Same-machine scheduling rule

Collector and Training Farm may be developed in parallel conceptually, but physical runtime contention must be scheduled.

Default rule:

```text
critical/canonical WinKawaks Collector capture
-> pause or cap heavy 8/10-worker Training Farm load
-> finish capture
-> resume Training Farm
```

Repository-only coding/tests may proceed in parallel if they do not materially load the same machine.

Alpha browser diagnostics should also avoid competing with heavy 10训 workloads when browser timing/render capture quality matters.

## 11. Environment protection

The Owner has other Python projects on the same machine.

Hard rule:

- do not delete or alter unrelated Python installations;
- do not globally reinstall Python;
- do not change global PATH merely to make WOF work;
- do not globally mutate site-packages;
- prefer project-specific venvs;
- reuse existing WOF-specific environments when valid;
- do not delete unrelated venv/conda/uv/pyenv environments;
- do not modify `D:\Reasonix` or unrelated projects.

If a dependency/environment repair is needed, contain it inside the relevant WOF project environment.

## 12. Owner interaction policy

The Owner should not be used as the routine debugger or task router.

Codex should continue automatically through safe code inspection, local tests, Git history, fixture diagnosis, runtime logs and bounded local experiments.

Ask the Owner only when one of these is truly required:

- legal local ROM selection/path not already available;
- explicit real-game/manual interaction;
- a one-shot/budget-consuming live run;
- destructive or irreversible action;
- product-direction tradeoff that changes user-visible behavior;
- credentials/secrets/access unavailable to Codex;
- hardware/OS operation that cannot be safely automated.

When asking, state exactly what the Owner must do and why.

## 13. Priority policy

The all-in-one Codex thread should optimize for **usable product progress**, not internal stage count.

Default priority:

1. preserve/fix Alpha Owner-visible zero-click product path and consume real live feedback intelligently;
2. make real 10训 runtime genuinely operational and scalable rather than fixture-only;
3. use Unified Collector V12 as the common read-only evidence plane and extend it only for concrete missing capability;
4. feed Collector/Training findings back into Alpha only through explicit source-aware calibration and Browser validation.

If one line is waiting on Owner/manual input, continue useful independent work in the other lines instead of stopping the whole thread.

## 14. Success definition

This takeover is successful when one sustained local Codex thread can keep the whole WOF program moving without repeated short-chat handoffs, while preserving strict source/safety authority.

Desired end state:

```text
Unified Collector operational
+ real 10-worker Training Farm operational
+ reusable evidence/trajectory flow operational
+ Alpha mainline visibly useful and zero-click
+ Browser/renderer authority upgraded truthfully where needed
+ Git remains clean durable authority
+ Owner only handles genuinely manual/live decisions
```

Do not declare success merely because repository tests pass. Owner-facing runtime reality and real local Training Farm/Collector operation remain the final practical checks.
