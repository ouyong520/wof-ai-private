from pathlib import Path

p = Path('reports/EFIELD_WIN_KAWAKS_ENEMY_FIELD_ATLAS.md')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '### EFIELD-004-passive-lifecycle-retarget-60s60 — QUEUED',
    '### EFIELD-004-passive-lifecycle-retarget-60s60 — PASS',
)
old = '''- 60s @ 60Hz natural gameplay
- raw upload yes
- operator gate no
- primary: seek real slot-allocation/reuse edges
- secondary: additional retarget and attack/movement replication
- currently serialized behind independent GEO-0005, which remains `WAITING_FOR_OPERATOR`; EFIELD does not modify the GEO task'''
new = '''- 3600 frames @ 59.990Hz; distinct 2480/3600 = 68.89%
- read/frame errors 0/0; raw uploaded successfully
- fresh WinKawaks session PID `30144`, RAM base `0x8E1FDFC`, mapping `xor3`
- `0x00` allocation transitions: `0`; slots0..16 remained 0 and slots17..19 remained 1 for all 3600 frames
- `0x24` type-present edges: 5 enter + 5 exit
- U16 BE `0x6D..0x6E` target transitions: 2; both are known-player retargets
- run4 retargets: slot17 P3->P1 and slot18 P2->P1 at frame 2961
- raw `captures/EFIELD-004-passive-lifecycle-retarget-60s60.jsonl.gz`'''
if old in s:
    s = s.replace(old, new)

marker = '## Cross-session consolidation after EFIELD-004'
if marker not in s:
    block = '''

## Cross-session consolidation after EFIELD-004

EFIELD-004 ran in a fresh WinKawaks process/session, so it is useful as an independent replication rather than only more frames from the original process.

### Allocation/object-header layer

Across EFIELD-001..004 (`12600` frames / `252000` enemy-object samples), `0x00` still produced **zero transitions**. In run4, as in the earlier corpus, slots0..16 stayed `00` and slots17..19 stayed `01` for every frame. The `0x00` field is therefore strengthened as a persistent slot-allocation / occupied-object-header layer in the observed runtime configuration, but an actual allocation/reuse transition is still not captured. `0x24` continues to represent a faster current-type/type-present layer inside those preallocated objects.

### Target pointer across sessions

Run4 added two true U16 target changes, both known P1/P2/P3 retargets. Combined dynamic target evidence is now **8/8 known-player retargets** across EFIELD-002..004 and across two WinKawaks sessions. This strengthens `0x6D..0x6E` as the WinKawaks-local U16 BE target pointer candidate.

A separate lifecycle pass over runs1..3 found 21 type-enter and 21 type-exit boundaries. The target pointer was unchanged across **21/21 enters and 21/21 exits** and can remain a known P1/P2/P3 value while `0x24 == 0`. Target lifetime is therefore not identical to current type-present lifetime; stale/latched target values survive type-zero intervals.

### Coarse attack phase topology

For joint state `(0x6C,0x70,0x72,0x73,0x77)`, boundary enrichment separates stable interior states from rare boundary-like states without assigning visual attack semantics:

- `90,00,88,0B,00`: 94.83% interior; strongest long-dwell interior state in the boundary analysis.
- `E0,A0,D8,0A,0C`: 84.21% interior and 216 episodes consisted solely of this state; a dominant core/loop state.
- `40,00,E8,1B,00`: 67.48% interior but common at zero/nonzero crossings; transitional/core-bridge family.
- `50,00,18,1B,00` and `58,00,30,1B,00`: substantially more boundary-enriched than the dominant core states.
- `78,78,78,1E,0B` and `70,70,70,1E,0B`: zero interior samples in this corpus and strongly end-boundary enriched; rare boundary-state candidates.

These labels are structural (`interior`, `bridge`, `boundary`) only; they do not claim visual onset/hit/recovery semantics.

### Horizontal locomotion phase fields

Signed coordinate-delta conditioning substantially refines the movement interpretation:

- `0xB9` changes almost never when X is stationary (7/15497 stationary transitions; 1/1157 pure-up; 0/1048 pure-down), but changes on ~45% of pure horizontal transitions and ~77–99% of diagonal transitions. Left/right use nearly the same chains (`04->03->02->01->04`, plus higher cycles). `0xB9` is therefore best described as a **horizontal locomotion / walk-phase counter**, not a direction bit.
- `0xBB` does not change in the stationary or pure-vertical samples and changes only during transitions with a horizontal component. Of those changes, roughly 86–94% are `-1`. It is therefore best described as a **horizontal movement countdown / step timer**.

### Instance/profile metadata

Episode factorization and replacement-boundary analysis refine `0xB4`/`0xB6`:

- `0xB6` is constant in 266/266 original type episodes but has low type purity (`0.327`), low slot purity (`0.320`) and multiple values even for repeated same-type/same-slot/same-run episodes. It is not a type constant or slot constant.
- Across frames containing >=2 type-present enemies, simultaneous `0xB6` values were all unique in 8259/8315 frames (99.33%), but collisions exist, so `0xB6` is **not a strict unique ID**. It behaves more like an instance/profile/variant code.
- `0xB4` is also episode-stable but can differ on same-type replacements; it is not a deterministic facing or spawn-side bit. Initial relative-side correlation is only partial.
- Episode-level entropy shows `B6` almost determines `B4` (`H(B4|B6)=0.1004`), suggesting `B4` is a coarse binary projection of a finer `B6` profile/instance class.
- `0xC6` and `0x3E` form an exact deterministic episode-level pair in the current metadata bundle and are worth treating as a linked static-property representation rather than independent unknowns.

### New/updated offline evidence

- `results/efield/PHASE_BOUNDARIES.md`
- `results/efield/VELOCITY_PHASE.md`
- `results/efield/METADATA_FACTORIZATION.md`
- `results/efield/SPAWN_METADATA.md`
- `results/efield/PROFILE_TUPLES.md`
- `results/efield/INSTANCE_BUNDLE.md`
- `results/efield/TARGET_LIFECYCLE.md`
- `results/efield/RUN4_CORE.md`

### Next passive run

`EFIELD-005R-cross-session-target-60s60` is queued with no operator gate. `EFIELD-005-cross-session-target-60s60` was rejected by schema validation before execution because its capture parameters were placed at the wrong JSON level; no game capture or memory operation occurred for the rejected task. EFIELD-005R uses the validated Collector v1 `parameters` shape. Its main purpose is to expand the exact target-pointer sample beyond eight retargets and replicate the type/attack/movement atlas in the new session, while still watching opportunistically for a rare real `0x00` allocation/reuse edge.
'''
    anchors = ['## Current automatic priorities', '## Current automatic decision point', '## Coverage gaps']
    pos = next((s.find(a) for a in anchors if s.find(a) != -1), -1)
    if pos == -1:
        s += block
    else:
        s = s[:pos] + block + '\n' + s[pos:]

p.write_text(s, encoding='utf-8')
