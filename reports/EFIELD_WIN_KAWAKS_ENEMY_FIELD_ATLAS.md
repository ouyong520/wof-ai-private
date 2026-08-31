# WinKawaks Enemy Field Atlas (EFIELD)

Research line: `EFIELD-` only. This report is a **WinKawaks-local discovery atlas**. It is not a Browser/WASM offset contract and does not promote or modify any production rule.

## Scope / invariants

- enemy pool: `0xFFC0BC`
- stride: `0xE0`
- enemy slots: `20`
- Collector raw block: P1 + P2 + P3 + 20 enemies, `23 * 0xE0 = 5152` bytes/frame
- read-only only; no game-memory writes
- do not modify or advance `WOF-045`
- do not modify T16/T18/T20/T23/T24/D867/D881 production-shadow rules
- WinKawaks offsets remain namespace-local unless separately re-proven elsewhere
- raw Collector frames are normalized CPS byte-lane captures

## Current corpus

Seven valid EFIELD raw captures are now in the corpus:

- `EFIELD-001-baseline-30s60`
- `EFIELD-002-natural-diversity-60s60`
- `EFIELD-003-passive-retarget-60s60`
- `EFIELD-004-passive-lifecycle-retarget-60s60`
- `EFIELD-005-cross-session-target-60s60`
- `EFIELD-005R-cross-session-target-60s60`
- `EFIELD-006-cross-session-lifecycle-target-60s60`

Combined coverage:

- frames: **23,400**
- enemy-object samples: **468,000**
- WinKawaks process sessions represented: **2**
- `0x24` type-present enter/exit boundaries: **74 / 74**
- `0x00` transitions: **0**
- live target `0x6D..0x6E` transitions: **8**
- known-player live retargets: **8/8**
- game-memory writes: **0**

The first malformed version of EFIELD-005 was rejected by Collector schema validation. The same task ID was later corrected to the valid `parameters` shape and successfully executed; its final task status/result is PASS. EFIELD-005R also executed successfully and remains a separate valid raw capture.

## Current field atlas

| Offset | Width | Current evidence | Current WinKawaks-local interpretation |
|---|---:|---|---|
| `0x00` | U8 | 23,400 frames; slots17..19 always `1`, slots0..16 always `0`; **0 transitions** while `0x24` has 74/74 lifecycle edges | persistent physical-slot/object-header marker candidate; **not current enemy-presence ACTIVE** |
| `0x07..0x0A` | s32 candidate | dynamic coordinate anchor used successfully for velocity and proximity conditioning | X coordinate / geometry candidate |
| `0x0B..0x0E` | s32 candidate | dynamic coordinate anchor used for 2D geometry conditioning | Y coordinate / geometry candidate |
| `0x19` | U8 | slow binary `00/FF`; mostly episode-stable but not immutable | slowly-changing instance/type/variant property candidate |
| `0x23` | U8 | zero high byte in legacy type wrapper | padding/high byte next to type |
| `0x24` | **U8** | 31 observed values; **74 enter + 74 exit** zero/nonzero edges | **current type / type-present lifecycle anchor** |
| `0x28` | U8 | sparse; retarget-associated but far more changes than true retargets | sparse transition/pulse state; not target identity |
| `0x2D` | U8 | broad action/reset dynamics | action/reset-state candidate |
| `0x2E` | U8 | broad state dynamics | broad action/state candidate |
| `0x2F..0x32` | **flagged U32 BE cursor candidate** | masking `0x001C0000` collapses many raw flag jumps into logical `+0x0A`; 4323/5539 logical pointer changes are `+0x0A`; repeated logical `-0x32` loops remain | **10-byte script/animation record cursor with embedded flag bits candidate** |
| `0x34` | **U8** | pointer-stable changes overwhelmingly `-1/-2`; before logical `+0x0A` cursor steps, `0x34<=2` in 4206/4323 = 97.29% and `<=1` in 75.99%; then usually reloads upward | **current 10-byte record countdown/dwell timer candidate** |
| `0x37` | **U8** | values `00/80/02`; 1528 changes, heavily attack-associated; `0x38` is constant `0x84` | attack-associated gate/flag/substate; **not supported as a U16 timer** |
| `0x3D..0x3E` | **U16 BE** | values exactly `BE1C/BEFC/BFDC`; deterministic relation with `0xC6` | **player-association/proximity pointer candidate**, separate from live target |
| `0x65` | U8 | seven-run retarget pass: exact same-frame on 6/8; any change within +/-3 frames on 7/8; 401 total changes | optional retarget-associated trigger/substate, not identity and not universal |
| `0x68` | U8 | strong player-reference relation; near retargets often reaches destination low byte before or at live commit | player-reference mirror/association byte candidate |
| `0x6C` | **U8** | fine state deterministically projects to coarse `0x73` in current corpus | **fine attack substate/phase candidate** |
| `0x6D..0x6E` | **U16 BE** | only P1 `BE1C`, P2 `BEFC`, P3 `BFDC`; 8 changes and all 8 are true known-player retargets | **strong live/materialized player-target pointer candidate** |
| `0x6F` | U8 | strong player-reference relation and retarget lead/commit association | player-reference high-byte mirror/association candidate |
| `0x70` | U8 | fine state deterministically projects to `0x77` | fine attack/body state candidate |
| `0x71..0x72` | structure candidate | dynamic attack/body neighborhood; `0x72` highly attack-coupled | body/animation state structure; final width still unresolved |
| `0x73` | **U8** | values mainly `00/0A/0B/1B/1E`; following `0x74` is zero | **coarse attack state/family anchor** |
| `0x74` | U8 | constant zero in current type-present corpus | padding/zero neighbor to `0x73` |
| `0x77` | U8 | deterministic coarse projection of `0x70` | attack-neighborhood coarse state candidate |
| `0x81` | historical reference | no current semantic promotion | unknown/reference only |
| `0x99` | U8 | binary `00/FF`; only 17 total changes across seven captures; 5/8 retargets changed it same-frame; no lagged misses and no deterministic target-side or horizontal-velocity mapping | sparse internal mode/flag candidate enriched at some retargets; **not target identity and not simple facing/target-side** |
| `0x9C` | U8 | high-frequency state; strong +1-frame relation with `0x04` | pipelined/high-frequency state candidate |
| `0xA2` | U8 | X payload equality peaks with a +1-frame relation | one-frame-delayed/latched X-coordinate mirror/history candidate |
| `0xB0` | U8 | mostly episode-stable but changes at some replacements | slowly-changing instance/profile property candidate |
| `0xB4` | **U8** | **1604/1604** type episodes constant, zero within-episode changes; binary domain | **instance-initialized coarse profile/variant metadata candidate** |
| `0xB6` | **U8** | **1604/1604** type episodes constant, zero within-episode changes; 34-value domain; changes on 9/11 same-type replacement boundaries | **strong instance/profile/variant initialization code candidate** |
| `0xB9` | U8 | almost static without horizontal motion; strong cyclic changes on horizontal/diagonal movement | **horizontal locomotion / walk-phase counter candidate** |
| `0xBB` | U8 | movement changes overwhelmingly decrement; absent on stationary/pure-vertical transitions | **horizontal movement countdown / step-timer candidate** |
| `0xC6` | **U8** | only `00/01/02`; exact mapping to P1/P2/P3 association pointer; 87.02% nearest-X agreement, but only 2/11 same-type switches have an old-nearer -> new-nearer crossing within the same-type +/-600f window and 3/11 switch while the old association is still closer | **horizontal-proximity-associated physical-player link/bookkeeping index candidate**; not a simple nearest-player threshold and not a direct future target selector |

## Lifecycle: `0x00` is not current ACTIVE

Across all 23,400 frames:

- slots `0..16`: `0x00 == 0` throughout
- slots `17..19`: `0x00 == 1` throughout
- total `0x00` transitions: **0**
- `0x24` zero->nonzero: **74**
- `0x24` nonzero->zero: **74**

Therefore the corpus contains repeated enemy lifecycle/type-presence transitions without any `0x00` transition. Current model:

1. `0x00` = persistent physical-slot/object-header layer in the observed runtime configuration.
2. `0x24` = faster current type/type-present lifecycle layer.

No semantic production ACTIVE rule is promoted from this WinKawaks evidence.

## Live target layer: `0x6D..0x6E`

Observed U16 BE values are exactly:

- P1 `0xBE1C`
- P2 `0xBEFC`
- P3 `0xBFDC`

Across seven captures:

- total live-target transitions: **8**
- known-player retargets: **8**
- precision among observed target changes: **8/8 = 1.0**
- six retargets occurred while `0x24` type stayed unchanged
- the other two were nonzero-type -> nonzero-type changes, not lifecycle zero/nonzero boundaries
- no target transition coincided with an ordinary type-present enter/exit edge

Target values can remain latched through `0x24 == 0`, so target lifetime is not the same as type-present lifetime.

## Separate player-association / proximity layer: `0xC6` + `0x3D..0x3E`

`0xC6` and `0x3D..0x3E` form an exact three-player encoding:

- `C6=00 -> 0x3D..0x3E = 0xBE1C` = P1
- `C6=01 -> 0x3D..0x3E = 0xBEFC` = P2
- `C6=02 -> 0x3D..0x3E = 0xBFDC` = P3

Across **60,271 type-present samples**:

- exact `0x3D..0x3E == live 0x6D..0x6E`: only **18,753/60,271 = 31.11%**
- both fields nevertheless always belong to the known P1/P2/P3 set in this corpus
- `C6` agrees with the **nearest-X player** on **52,445/60,271 = 87.02%**
- live target agrees with nearest-X on only **18,519/60,271 = 30.73%**
- `C6` agrees with nearest Manhattan(X,Y) player on 70.25%

This strongly separates the layers:

- `0xC6` / `0x3D..0x3E`: spatial/proximity association candidate
- `0x6D..0x6E`: live/materialized target pointer candidate

### C6 is not a simple intended-target predictor

There are 11 same-type `C6` changes in the seven-run corpus. Only **1/11** was followed within 240 frames by the live target committing to the newly selected player. Therefore the earlier “future intended target selector” hypothesis is rejected as a general model.

Geometry conditioning instead shows:

- 8/11 switches moved from a player that was not nearest-X to one that was nearest-X on the switch frame
- 3/11 switched away from the instantaneous nearest-X player
- global nearest-X agreement rises only slightly from 87.02% at `t` to 87.38% at `t+15`; there is no sharp fixed lead/lag
- many switches occur after the new player has already been closer for multiple frames, while a few counterexamples show a switch before or without a local nearest crossing

Best current label: **sticky/hysteretic horizontal proximity association**, not per-frame `argmin(distance)` and not direct target identity.

## Script / animation executor candidate: `0x2F..0x32` + `0x34`

The old generic labels around `0x2F` and `0x33` are refined substantially.

### Pointer/progression field

U32 BE at `0x2F..0x32`:

- unique values: **178**
- changes: **5540**
- exact delta `+0x0A`: **3006**
- exact `-0x0A`: 24
- repeated `-0x32` loop/reset transitions
- repeated `+0x4000A` and paired bank-like return jumps
- examples include `0x02008BE0 -> 0x02008BEA -> 0x02008BF4 -> ...`

Byte `0x2F` alone is constant `0x02` in the current type-present corpus; the semantic candidate is the **whole U32 structure**, not byte `0x2F` by itself.

### Countdown/reload field

`0x34` U8:

- 43 values
- 31,920 changes
- when pointer is stable but countdown changes, dominant deltas are `-1` and `-2`
- at pointer changes, `0x34` changes 5203 times and moves upward/reloads **4967** times

Current model is a strong **record pointer + duration/countdown** executor candidate. It is consistent with an animation/script progression mechanism, but the exact ROM/program semantics remain discovery-only.

### `0x37` correction

`0x37` is not supported as the old U16 timer hypothesis:

- U8 values: `00`, `80`, `02`
- 1528 changes
- `0x38` is constant `0x84`
- changes are strongly attack-associated

Treat `0x37` as an attack-associated flag/gate/substate until further evidence.

## Attack hierarchy / phase topology

Current structural relations:

- H(`0x73 | 0x6C`) = `0` in the analyzed corpus: each fine `0x6C` state maps to one coarse `0x73` family.
- H(`0x77 | 0x70`) = `0`: each fine `0x70` state maps to one `0x77` coarse state.
- `0x72 -> 0x73` is near-deterministic but not perfect.

Representative mappings:

- `6C=E0 -> 73=0A`
- `6C=40/48/50/58 -> 73=1B`
- `6C=90 -> 73=0B`
- `6C=70/78 -> 73=1E`
- `70=A0 -> 77=0C`
- `70=80/10/58/28 -> 77=0B`
- `70=D8 -> 77=14`
- `70=F8 -> 77=0A`

Phase-boundary analysis separates structural states:

- `90,00,88,0B,00`: **94.83% interior**; strongest long-dwell interior candidate
- `E0,A0,D8,0A,0C`: **84.21% interior**; dominant core/loop state
- `40,00,E8,1B,00`: common bridge/core state
- `50,00,18,1B,00` and `58,00,30,1B,00`: more boundary-enriched
- `78,78,78,1E,0B` and `70,70,70,1E,0B`: no interior samples in the phase-boundary corpus; rare boundary/termination candidates

These are structural labels only. They do not yet claim visual onset/hit/recovery semantics.

## Movement subsystem

Velocity-conditioned evidence strongly separates locomotion fields from attack fields.

### `0xB9`

- nearly static when X is stationary
- approximately 45% change rate on pure horizontal movement in the analyzed pass
- approximately 77–99% change rate on diagonal movement
- left/right share recurring chains such as `04->03->02->01->04`

Current interpretation: **horizontal locomotion/walk-phase counter**, not direction bit.

### `0xBB`

- no changes in stationary/pure-vertical samples in the velocity pass
- changes only when a horizontal component is present
- among changes, roughly 86–94% are `-1`

Current interpretation: **horizontal movement countdown / step timer**.

### `0xA2`

X payload equality peaks at a +1-frame relation (`0x08[t] == 0xA2[t+1]` about 97.8% in the original lag pass), supporting a delayed/latched X-coordinate mirror/history interpretation.

## Instance/profile metadata

Episodes are contiguous same-nonzero-`0x24` type segments in a physical slot.

Across **1604 episodes**:

- `0xB4`: **1604/1604 constant**, zero within-episode changes
- `0xB6`: **1604/1604 constant**, zero within-episode changes
- `0xB6`: 34-value domain in the seven-run episode pass

Across **1583 consecutive episode boundaries**:

- same-type replacement boundaries: 11
- `B6` changed on **9/11** same-type replacements
- `B4` changed on 3/11 same-type replacements

This strongly rejects “type constant” and supports initialization-time instance/profile semantics for B6. Earlier factorization also found low individual type/slot/run purity and high simultaneous uniqueness without strict uniqueness, so B6 is better described as **instance/profile/variant code** than unique ID.

Additional deterministic/co-change structure:

- `0xC6 <-> 0x3E` is exact in the current corpus and now has player-association semantics rather than generic metadata semantics.
- `0xC6` and `0x3E` should not be treated as independent unknowns.
- `0xB6` almost determines coarse binary `0xB4`; B4 behaves like a coarse projection of a richer profile code.

## Run ledger

### EFIELD-001-baseline-30s60 — PASS
- 1800 frames
- ~59.984 Hz
- distinct raw frames 1448/1800 = 80.44%
- type enter/exit 7/6
- target transitions 0
- read/frame errors 0/0

### EFIELD-002-natural-diversity-60s60 — PASS
- 3600 frames
- ~59.993 Hz
- distinct 2848/3600 = 79.11%
- type enter/exit 3/4
- target retargets 3/3

### EFIELD-003-passive-retarget-60s60 — PASS
- 3600 frames
- ~60 Hz
- distinct 2817/3600 = 78.25%
- type enter/exit 11/11
- target retargets 3/3
- includes first natural P2 target observation

### EFIELD-004-passive-lifecycle-retarget-60s60 — PASS
- 3600 frames
- ~59.990 Hz
- distinct 2480/3600 = 68.89%
- fresh/new WinKawaks process session
- type enter/exit 5/5
- two simultaneous known-player retargets at frame 2961

### EFIELD-005-cross-session-target-60s60 — PASS after corrected schema
- initial malformed task attempt failed validation before capture
- corrected task blob later executed successfully under the same task ID
- 3600 frames @ 59.993 Hz
- distinct 3376/3600 = **93.78%**
- type enter/exit 17/16
- target transitions 0; target stayed P1 in the observed active slots

### EFIELD-005R-cross-session-target-60s60 — PASS
- 3600 frames @ 59.994 Hz
- distinct 3356/3600 = **93.22%**
- type enter/exit 16/17
- target transitions 0; target stayed P1 in the observed active slots

### EFIELD-006-cross-session-lifecycle-target-60s60 — PASS
- 3600 frames @ 59.993 Hz
- distinct 1841/3600 = **51.14%**
- type enter/exit 15/15
- target transitions 0
- read/frame errors 0/0

### EFIELD-007-passive-proximity-association-60s60 — FAILED PRE-CAPTURE

- no raw capture was produced
- failure occurred during fresh immutable CPS RAM discovery before sampling
- Collector error: `Fresh immutable CPS RAM discovery is not uniquely qualified`
- read-only contract remained intact; no game-memory write occurred
- do not auto-retry this exact collection while discovery remains ambiguous; continue offline analysis until runtime discovery is uniquely qualified again





## C6 switch timing: proximity-associated, not a simple nearest threshold

A +/-600-frame analysis of all 11 same-type `0xC6` switches tests whether the association simply flips when another player's X distance becomes smaller.

Results:

- only **2/11** switches have a clean old-nearer -> new-nearer crossing inside the same-type search window;
- those two switches occur **9 frames** and **533 frames** after the nearest such crossing;
- the other **9/11** switches have no such crossing within the contiguous same-type +/-600-frame window;
- at the actual switch frame, the new association player is X-nearer in **8/11** cases, but the old association player is still X-nearer in **3/11** cases;
- filtering players by player-object `0x00 != 0` does not improve the overall geometry agreement (87.02% -> 86.20%), and the association can point at a physical player slot whose player `0x00` header is zero.

Therefore the geometry relation is real but should not be described as a deterministic nearest-player selector or a simple fixed hysteresis threshold. The safer current interpretation is a **horizontal-proximity-associated physical-player link/bookkeeping state with coarse/sticky update behavior**. Its exact update trigger remains unresolved.

Evidence: `results/efield/PLAYER_ASSOC_GEOMETRY.md`, `results/efield/PROXIMITY_HYSTERESIS.md`, `results/efield/C6_VALID_PLAYER_GEOMETRY.md`, `results/efield/C6_SWITCH_LATENCY.md`.

## Script-record executor: `0x2F..0x32` + `0x34`

Seven-capture pointer/countdown analysis substantially strengthens the executor model.

The raw U32 field at `0x2F..0x32` contains address-like progression plus flag-like bits in the `0x30` byte. Masking `0x001C0000` removes the observed `04/08/10/18`-class embedded bits and turns many apparent large jumps into ordinary sequential steps:

- raw `+0x0A`: 3006
- raw `+0x4000A`: 762
- raw `-0x3FFF6`: 488
- after masking, logical `+0x0A`: **4323/5539 = 78.05% of logical pointer changes**
- logical `-0x32`: 352; this is exactly `-50`, consistent with a five-record backward loop if the record stride is 10 bytes

The countdown relation is equally strong:

- on logical `+0x0A` steps, previous `0x34 <= 1`: **3285/4323 = 75.99%**
- previous `0x34 <= 2`: **4206/4323 = 97.29%**
- previous `0x34 <= 3`: **98.64%**
- when the logical pointer remains stable and `0x34` changes, the dominant deltas are `-1` (19,928) and `-2` (6,372)
- after a sequential pointer step, `0x34` usually reloads to a larger duration value

Current structural model:

1. `0x2F..0x32` = **logical 10-byte script/animation-record cursor plus embedded flag bits**.
2. `0x34` = **current record dwell/countdown timer**.
3. logical `+0x0A` = sequential record advance.
4. logical negative/sparse non-`+0x0A` deltas = loop/branch/script-switch candidates.

This remains a dynamic structural interpretation. It does not yet identify record opcode semantics or claim Browser/WASM address equivalence.

Evidence: `results/efield/NEXT_POINTER.md`, `results/efield/TIMER_SEMANTICS.md`, `results/efield/ATTACK_TIMERS.md`, `results/efield/POINTER_RECORD_MASK.md`.

## High-value evidence outputs

- `results/efield/summary.json`
- `results/efield/RUN_FOCUS.md`
- `results/efield/ALL_RUN_CORE.md`
- `results/efield/NEW_SESSION_CORE.md`
- `results/efield/CROSS_SESSION_REPLICATION.md`
- `results/efield/FULL_EPISODE_STABILITY.md`
- `results/efield/INSTANCE_BUNDLE.md`
- `results/efield/METADATA_FACTORIZATION.md`
- `results/efield/PROFILE_TUPLES.md`
- `results/efield/PHASE_BOUNDARIES.md`
- `results/efield/VELOCITY_PHASE.md`
- `results/efield/TIMER_SEMANTICS.md`
- `results/efield/ATTACK_TIMER_PHASE.md`
- `results/efield/NEXT_POINTER.md`
- `results/efield/TARGET_LAYERS.md`
- `results/efield/RETARGET_LEAD.md`
- `results/efield/SELECTOR_PRECISION.md`
- `results/efield/PLAYER_ASSOC_GEOMETRY.md`
- `results/efield/PROXIMITY_HYSTERESIS.md`

## Current priorities

1. Expand same-type `C6` switch coverage when Collector discovery becomes uniquely qualified; current 11-switch evidence rejects a simple nearest-X threshold/hysteresis model.
2. Determine whether `0x3D..0x3E` / `C6` is specifically nearest-X association, navigation focus, collision/player-link state, or another spatial player-reference layer.
3. Decode the `0x2F..0x32` + `0x34` executor more deeply: record size, loop/branch structure, and relation to `0x6C/70/72/73/77` attack phases.
4. Convert structural attack phase families into stronger onset/core/termination semantics without assuming visual meaning not present in raw evidence.
5. Continue B6/profile factorization against type, spawn, stage, slot and player-association context.
6. Keep opportunistically watching for a real `0x00` allocation/reuse edge, but do not treat passive failure to observe one as a blocker for other field mapping.

No Browser/WASM offset equivalence, WOF-045 progression, production-shadow modification, or game-memory write is implied by this atlas.
