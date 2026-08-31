from pathlib import Path

p = Path('reports/EFIELD_WIN_KAWAKS_ENEMY_FIELD_ATLAS.md')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '| `0x2F..0x32` | **U32 BE candidate** | 178 values, 5540 changes; `+0x0A` exactly 3006 times; repeated `-0x32` loops and `+0x4000A`/bank-like steps | **script/animation record pointer / progression address candidate** |',
    '| `0x2F..0x32` | **flagged U32 BE cursor candidate** | masking `0x001C0000` collapses many raw flag jumps into logical `+0x0A`; 4323/5539 logical pointer changes are `+0x0A`; repeated logical `-0x32` loops remain | **10-byte script/animation record cursor with embedded flag bits candidate** |',
)
s = s.replace(
    '| `0x34` | **U8** | 43 values; 31,920 changes; pointer-stable changes are overwhelmingly `-1/-2`; at pointer changes it reloads upward 4967 times | **script/animation duration or frame-countdown candidate** |',
    '| `0x34` | **U8** | pointer-stable changes overwhelmingly `-1/-2`; before logical `+0x0A` cursor steps, `0x34<=2` in 4206/4323 = 97.29% and `<=1` in 75.99%; then usually reloads upward | **current 10-byte record countdown/dwell timer candidate** |',
)
s = s.replace(
    '| `0x65` | U8 | changes at all original retarget events but many unrelated changes | retarget-associated trigger/substate, not identity |',
    '| `0x65` | U8 | seven-run retarget pass: exact same-frame on 6/8; any change within +/-3 frames on 7/8; 401 total changes | optional retarget-associated trigger/substate, not identity and not universal |',
)

if '| `0x99` | U8 |' not in s:
    needle = '| `0x81` | historical reference | no current semantic promotion | unknown/reference only |\n'
    row = '| `0x99` | U8 | binary `00/FF`; only 17 total changes across seven captures; 5/8 retargets changed it same-frame; no lagged misses and no deterministic target-side or horizontal-velocity mapping | sparse internal mode/flag candidate enriched at some retargets; **not target identity and not simple facing/target-side** |\n'
    if needle in s:
        s = s.replace(needle, needle + row)

queued = '''### EFIELD-007-passive-proximity-association-60s60 — queued

Purpose: expand the sparse same-type `C6` proximity-association switch sample, measure proximity hysteresis/crossings, preserve separation from live target `0x6D..0x6E`, and replicate the script-pointer/countdown model. No operator gate is required.'''
failed = '''### EFIELD-007-passive-proximity-association-60s60 — FAILED PRE-CAPTURE

- no raw capture was produced
- failure occurred during fresh immutable CPS RAM discovery before sampling
- Collector error: `Fresh immutable CPS RAM discovery is not uniquely qualified`
- read-only contract remained intact; no game-memory write occurred
- do not auto-retry this exact collection while discovery remains ambiguous; continue offline analysis until runtime discovery is uniquely qualified again'''
if queued in s:
    s = s.replace(queued, failed)

marker = '## Script-record executor: `0x2F..0x32` + `0x34`'
if marker not in s:
    block = r'''

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
'''
    anchor = '## High-value evidence outputs'
    pos = s.find(anchor)
    if pos == -1:
        s += block
    else:
        s = s[:pos] + block + '\n' + s[pos:]

p.write_text(s, encoding='utf-8')
