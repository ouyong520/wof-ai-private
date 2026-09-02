# WOF Training Farm — Open-Source Baseline Decision

Updated: 2026-09-02
Status: **AUTHORITATIVE INTERNAL R&D BASELINE**

## 1. Decision

For the WOF headless multi-instance training / reverse-discovery farm, do **not** build an emulator or generic RL environment from scratch.

Preferred stack:

- **Stable-Retro** — primary Python/Gymnasium training environment and host layer.
- **FBNeo / FinalBurn Neo** — primary CPS1/WOF emulation core.
- **MAME** — reverse-engineering, RAM inspection and independent cross-check tool; not the default training runtime.
- **RetroArch/libretro** — API/reference/fallback host path only; do not make RetroArch itself the first Training Farm implementation target.
- **OpenAI Gym Retro** — historical reference only; do not use as the new primary dependency.

Implementation strategy:

`Stable-Retro + FBNeo -> thin WOF Adapter -> WOF RAM/state decoder -> savestate fork/search -> 1/2/4/8/10 workers`

Do not fork Stable-Retro or FBNeo by default. Start by consuming them as dependencies. Fork/patch only if a proven blocker exists in RAM exposure, deterministic save/load, headless execution, worker isolation, or performance.

## 2. Why this baseline

The reusable generic capabilities already exist in the selected open-source stack:

- emulator lifecycle;
- CPS1/WOF execution;
- frame stepping / action stepping;
- input injection through emulator APIs rather than global keyboard focus;
- RAM access;
- state serialization / unserialization;
- Gymnasium-style environment API;
- multiprocessing/vectorized-environment patterns;
- deterministic replay tooling.

The WOF project should spend engineering effort on game-specific value rather than recreating those layers.

Project-owned work should focus on:

- WOF memory map / state schema;
- P1/P2/P3 and enemy object decoding;
- target / HP / position / lifecycle / action-state observations;
- scenario capture and replay;
- same-state fork search;
- outcome scoring;
- multi-worker orchestration;
- automatic RAM-differential / reverse-discovery experiments;
- later teacher policy / distilled Assist policy.

## 3. Project evaluation

### Stable-Retro

Role: **primary Training Farm framework**.

Why reuse:

- Python/Gymnasium-facing emulator environment;
- exposes emulator RAM;
- supports state get/set through emulator serialization;
- provides frame/action stepping;
- already contains FBNeo arcade-core integration;
- suitable foundation for multiprocessing/vectorized workers.

Deployment expectation: **low-to-medium difficulty** compared with writing a custom libretro host.

Decision: **use directly first; extend with a WOF Adapter outside the dependency**.

Upstream: `https://github.com/Farama-Foundation/Stable-Retro`

### FinalBurn Neo / FBNeo

Role: **primary CPS1/WOF emulation core**.

Why reuse:

- mature CPS1 emulation;
- WOF family support belongs in the FBNeo driver ecosystem;
- input, frame execution and save-state machinery already exist;
- suitable libretro core for a headless training host.

Deployment expectation: **medium difficulty** if built directly; easier when consumed through Stable-Retro.

Decision: **use as the core; patch only when a concrete Training Farm blocker is proven**.

Upstream: `https://github.com/finalburnneo/FBNeo`

### MAME

Role: **research instrument / independent verifier**.

Why reuse:

- CPS1/WOF driver support;
- strong debugger and Lua automation facilities;
- address-space and memory inspection;
- useful for cheat-style scanning, RAM experiments and independent confirmation of semantics found under WinKawaks/FBNeo.

Deployment expectation: **medium difficulty**.

Decision: **use alongside the main farm for reverse engineering and cross-checks; do not make it the initial 10-worker training base**.

Upstream: `https://github.com/mamedev/mame`

### RetroArch / libretro

Role: **API reference and fallback custom-host path**.

Decision: do not start by building on the RetroArch application. If Stable-Retro later blocks required control, write a small project-owned headless libretro host around the FBNeo core rather than adopting a large frontend stack.

Upstream: `https://github.com/libretro/RetroArch`

### OpenAI Gym Retro

Role: **historical reference only**.

Decision: do not anchor the new project to its old Python/version assumptions. Stable-Retro is the preferred successor path.

## 4. Product / license boundary

Training infrastructure is an **internal R&D accelerator**, not the shipped Alpha/V1 product itself.

Keep the architecture separated:

`FBNeo / Stable-Retro / MAME research and training -> datasets / validated rules / policy artifacts -> project-owned live Assist runtime`

Do not assume emulator-core licensing is equivalent to Stable-Retro's framework license. Before commercial distribution of any emulator-derived binary/component, perform a separate license review.

The preferred product architecture does not require shipping FBNeo/MAME with the player-facing Assist.

## 5. Simplest MVP

The first MVP is **not PPO/DQN/neural-network training**.

Goal:

> Prove that one WOF dangerous state can be restored repeatedly, multiple actions can be tried from the exact same state, and the system can automatically identify a no-damage / safer action.

Required MVP API:

```text
reset()
step(action)
read_state()
save_state()
load_state()
score_outcome()
```

Minimal flow:

```text
load WOF through Stable-Retro + FBNeo
        ↓
read known RAM fields
        ↓
capture one dangerous savestate
        ↓
restore the same state for every trial
        ↓
try 9 actions
↖ ↑ ↗ / ← HOLD → / ↙ ↓ ↘
        ↓
run ~30 frames per trial
        ↓
read HP + position + enemy/target/action state
        ↓
score each result
        ↓
return best action
```

Initial scoring can remain deliberately simple:

- death: very large penalty;
- HP loss: very large penalty;
- no HP loss: strong reward;
- safer resulting spacing/position: secondary reward;
- useful forward stage progress: small reward;
- avoid rewarding hiding/stalling as the long-term objective.

Example MVP result:

```json
{
  "scene": "danger_001",
  "bestAction": "DOWN_LEFT",
  "hpLoss": 0,
  "frames": 30
}
```

## 6. Scaling order

Do not begin with ten workers.

Required progression:

`1 -> 2 -> 4 -> 8 -> 10`

At each step measure:

- deterministic save/load consistency;
- simulated frames per wall-clock second;
- CPU and memory consumption;
- per-worker isolation;
- input isolation;
- RAM observation consistency;
- crash/desync rate.

Only move to the next worker count when the previous level is stable.

## 7. Reverse-discovery role

The same farm should also become an automated WOF RAM discovery platform.

Use controlled savestate experiments to correlate unknown RAM fields with known events such as:

- player movement;
- enemy movement;
- target changes;
- attack/action transitions;
- damage / hitstun / knockdown;
- grab/release;
- spawn/despawn/replacement;
- camera/stage progression.

Long-term output should be a machine-validated **product-relevant WOF RAM map**, not merely a collection of online cheat addresses.

External/online addresses are candidate hints only; current ROM/runtime experiments remain the authority before a field is used by production or training.

## 8. Stop / escalation rule

Stay on the Stable-Retro + FBNeo baseline unless evidence proves one of these blockers:

1. required CPS1 RAM cannot be exposed reliably;
2. save/load state is not deterministic enough for same-state branching;
3. worker processes cannot be isolated safely;
4. headless throughput is inadequate on the target PC;
5. required frame/input control cannot be expressed;
6. an upstream license constraint conflicts with the intended use.

If a blocker appears, first consider a narrow FBNeo/Stable-Retro patch. Only then consider a project-owned minimal libretro headless host.

## 9. Relationship to product roadmap

This decision implements the Training Farm R&D lane described in `parallel/PM/PRODUCT_VERSION_ROADMAP.md`.

It does not change the current V1.0.0 release gates and must not displace legitimate V1 P0/P1 release work.
