from pathlib import Path

p = Path('reports/EFIELD_WIN_KAWAKS_ENEMY_FIELD_ATLAS.md')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '| `0x2F..0x32` | **flagged U32 BE cursor candidate** | masking `0x001C0000` collapses many raw flag jumps into logical `+0x0A`; 4323/5539 logical pointer changes are `+0x0A`; repeated logical `-0x32` loops remain | **10-byte script/animation record cursor with embedded flag bits candidate** |',
    '| `0x2F..0x32` | **flagged U32 BE cursor candidate** | 4323/5539 logical changes are `+0x0A`; sequential destination logical record predicts full `(6C,70,72,73,77)` phase tuple with **99.9769%** modal purity; raw embedded flags raise steady-state cursor->phase purity from 96.31% to 97.30% | **10-byte script/animation record cursor with phase-modifier flag bits** |',
)

marker = '## Logical record identity drives attack phase'
if marker not in s:
    block = r'''

## Logical record identity drives attack phase

The executor model is now supported not only by pointer stride/countdown behavior but by direct state-output concentration.

Across **60,271 type-present samples** and 174 masked logical cursor values:

- weighted modal purity of full `(0x6C,0x70,0x72,0x73,0x77)` phase tuple given logical cursor: **96.3117%**;
- weighted conditional entropy `H(phaseTuple | logicalCursor)`: only **0.0936 bits**;
- weighted coarse `0x73` purity given logical cursor: **96.3133%**;
- most populated logical cursor values map to exactly one phase tuple with 100% observed purity.

The strongest causal-looking transition evidence comes from sequential record execution:

- logical `+0x0A` destination events: **4323**;
- destination logical record -> post-arrival full phase tuple modal purity: **99.9769%**.

This strongly supports a record-driven phase machine: the logical record cursor nearly determines the attack/animation state tuple reached after the cursor advances.

### Embedded cursor flag bits are phase modifiers

Keeping the `0x001C0000` flag-like bits increases steady-state phase-tuple purity:

- masked logical cursor: **96.3117%**;
- raw cursor / logical+flag: **97.2955%**;
- raw cursor + enemy type: **97.4499%**.

Specific flag classes are structurally informative:

- `0x080000`: 4963 samples, **100%** `E0,A0,D8,0A,0C`;
- `0x140000`: only the rare `0x73=1E` boundary family (`78,78,78,1E,0B` / `70,70,70,1E,0B`);
- at ambiguous logical cursors `0x02008BD6` and `0x02005E9A`, flag `0x100000` maps **100%** to `E0,00,38,0A,00` in the current corpus.

Therefore the masked value is useful for recovering the underlying 10-byte record address, while the removed bits should be retained as meaningful **record/phase modifier flags**, not discarded as noise.

### `0x34` reload is context-dependent

On the same 4323 sequential `+0x0A` arrivals:

- destination logical cursor predicts the reloaded `0x34` value with only **75.6650%** modal purity;
- retaining raw flag bits does not improve that value;
- conditioning on destination logical cursor + enemy type raises reload purity to **80.3840%**;
- conditioning on phase tuple does not materially improve it.

Thus record identity strongly determines phase, but record dwell duration is not a fixed per-record constant. Current evidence favors a **record + enemy/context dependent duration** model.

Evidence: `results/efield/POINTER_PHASE_MAPPING.md`, `results/efield/POINTER_FLAG_SEMANTICS.md`, `results/efield/POINTER_RECORD_MASK.md`.
'''
    anchor = '## High-value evidence outputs'
    pos = s.find(anchor)
    if pos == -1:
        s += block
    else:
        s = s[:pos] + block + '\n' + s[pos:]

# Ensure high-value output list mentions the new reports.
needle = '- `results/efield/NEXT_POINTER.md`\n'
addition = '- `results/efield/POINTER_RECORD_MASK.md`\n- `results/efield/POINTER_PHASE_MAPPING.md`\n- `results/efield/POINTER_FLAG_SEMANTICS.md`\n'
if needle in s and 'results/efield/POINTER_PHASE_MAPPING.md' not in s:
    s = s.replace(needle, needle + addition)

p.write_text(s, encoding='utf-8')
