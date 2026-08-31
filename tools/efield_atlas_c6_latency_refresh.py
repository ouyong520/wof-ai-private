from pathlib import Path

p = Path('reports/EFIELD_WIN_KAWAKS_ENEMY_FIELD_ATLAS.md')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '| `0xC6` | **U8** | only `00/01/02`; exact mapping to P1/P2/P3 association pointer; 87.02% agreement with nearest-X player; only 1/11 same-type C6 changes committed to live target within 240 frames | **sticky/hysteretic horizontal proximity player-association index candidate**, not a direct future target selector |',
    '| `0xC6` | **U8** | only `00/01/02`; exact mapping to P1/P2/P3 association pointer; 87.02% nearest-X agreement, but only 2/11 same-type switches have an old-nearer -> new-nearer crossing within the same-type +/-600f window and 3/11 switch while the old association is still closer | **horizontal-proximity-associated physical-player link/bookkeeping index candidate**; not a simple nearest-player threshold and not a direct future target selector |',
)

marker = '## C6 switch timing: proximity-associated, not a simple nearest threshold'
if marker not in s:
    block = r'''

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
'''
    anchor = '## Script-record executor: `0x2F..0x32` + `0x34`'
    pos = s.find(anchor)
    if pos == -1:
        anchor = '## High-value evidence outputs'
        pos = s.find(anchor)
    if pos == -1:
        s += block
    else:
        s = s[:pos] + block + '\n' + s[pos:]

# Update priority wording if the old proximity-threshold language is still present.
s = s.replace(
    '1. Expand same-type `C6` switch coverage and test a quantitative proximity/hysteresis threshold model.',
    '1. Expand same-type `C6` switch coverage when Collector discovery becomes uniquely qualified; current 11-switch evidence rejects a simple nearest-X threshold/hysteresis model.',
)

p.write_text(s, encoding='utf-8')
