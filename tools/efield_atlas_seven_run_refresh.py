from pathlib import Path

p = Path('reports/EFIELD_WIN_KAWAKS_ENEMY_FIELD_ATLAS.md')
s = p.read_text(encoding='utf-8')
marker = '## Seven-capture consolidation'
if marker not in s:
    block = r'''

## Seven-capture consolidation

A direct all-run pass now covers seven independent EFIELD raw captures: EFIELD-001, 002, 003, 004, 005, 005R and 006.

### Core lifecycle totals

Across **23,400 frames / 468,000 enemy-object samples**:

- `0x00` allocation/object-header transitions: **0**.
- Physical slots `0..16` remained `0x00` for all 23,400 frames each.
- Physical slots `17..19` remained `0x01` for all 23,400 frames each.
- `0x24` current-type/type-present boundaries: **74 zero->nonzero enters + 74 nonzero->zero exits**.
- U16 BE `0x6D..0x6E` target transitions: **8**.
- All target transitions are between known player addresses P1/P2/P3: **8/8**.

The absence of any `0x00` edge is now replicated over two WinKawaks process sessions and 468k object samples. It strengthens the interpretation of `0x00` as a persistent slot-allocation / occupied-object-header layer in the observed runtime configuration, but still does not prove a general semantic ACTIVE rule because no real allocation/reuse edge has been captured.

### Target is independent of type-presence lifecycle

The eight observed target transitions are not explainable as ordinary type enter/exit events:

- six of eight retargets occurred while `0x24` type stayed exactly unchanged across the transition frame;
- the remaining two occurred with nonzero-type -> nonzero-type changes (`0x07->0x10` and `0x1B->0x09`), not zero/nonzero lifecycle edges;
- no observed target change coincided with a type-present enter or exit boundary.

Together with the earlier boundary analysis showing the target pointer remains latched across type-zero intervals, this supports treating `0x6D..0x6E` as an independently maintained WinKawaks-local player-target pointer field rather than a derivative of `0x24`.

### Exact redundant encoding: `0xC6` / `0x3E`

Do not confuse offset `0xC6` with attack-neighborhood offset `0x6C`.

Across all seven captures and **60,271 type-present samples**, the relation

`0x3E = (0x1C - 0x20 * 0xC6) mod 256`

holds for **60,271 / 60,271 samples with zero mismatches**. Only three pairs were observed:

- `C6=00 -> 3E=1C`
- `C6=01 -> 3E=FC`
- `C6=02 -> 3E=DC`

This is replicated across both WinKawaks sessions and across every observed nonzero type. `0x3E` should therefore be treated as a deterministic encoded mirror/projection of `0xC6`, not as an independent unknown field for future ranking.

### New evidence files

- `results/efield/ALL_RUN_CORE.md`
- `results/efield/NEW_SESSION_CORE.md`
- `results/efield/CROSS_SESSION_REPLICATION.md`
- `results/efield/C6_3E_ENCODING.md`

This section supersedes older temporary run-count wording in the report. No Browser/WASM equivalence or production-rule promotion is implied.
'''
    anchors = ['## Current automatic priorities', '## Current automatic decision point', '## Coverage gaps']
    positions = [s.find(a) for a in anchors if s.find(a) != -1]
    pos = min(positions) if positions else -1
    if pos == -1:
        s += block
    else:
        s = s[:pos] + block + '\n' + s[pos:]

p.write_text(s, encoding='utf-8')
