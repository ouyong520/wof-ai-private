from pathlib import Path

p = Path('reports/EFIELD_WIN_KAWAKS_ENEMY_FIELD_ATLAS.md')
s = p.read_text(encoding='utf-8')
marker = '## EFIELD-005R consolidation'
if marker not in s:
    block = '''

## EFIELD-005R consolidation

### Run ledger

`EFIELD-005-cross-session-target-60s60` was rejected by Collector schema validation before execution because the capture parameters were at the wrong JSON level. No game capture or memory operation occurred for that rejected task.

`EFIELD-005R-cross-session-target-60s60` then ran successfully using the validated Collector v1 `parameters` shape:

- PASS; 3600 frames @ 59.994Hz
- distinct raw frames: 3356/3600 = **93.22%**
- read/frame-size errors: 0/0
- same second WinKawaks session as run4: PID `30144`, RAM base `0x8E1FDFC`, mapping `xor3`
- raw `captures/EFIELD-005R-cross-session-target-60s60.jsonl.gz`
- `0x00` allocation transitions: **0**
- `0x24` type-present enter/exit: **16 / 17**
- U16 BE `0x6D..0x6E` target transitions: **0**
- slots17..19 carried P1 `0xBE1C` throughout the run when examining target values; high global frame diversity did not produce a retarget event

### Five-run cumulative allocation evidence

Across EFIELD-001..005R there are now **16200 frames / 324000 enemy-object samples** across two WinKawaks sessions. The `0x00` allocation/header byte still has **zero observed transitions**: slots0..16 remain 0 and slots17..19 remain 1 in every captured frame. This strengthens its interpretation as a persistent allocation/object-header layer in the observed runtime configuration, while also showing that passive normal-play sampling is inefficient for obtaining an actual allocation/reuse edge.

### Target evidence after run5

Run5 contributed no new target changes, so the dynamic target sample remains **8/8 known P1/P2/P3 retargets** from EFIELD-002..004. The important negative result is that run5 had 93.22% distinct raw frames yet zero retargets. Raw-frame diversity is therefore not a proxy for target-transition coverage.

### Cross-session semantic replication

`results/efield/CROSS_SESSION_REPLICATION.md` re-tested key semantics in EFIELD-004 and EFIELD-005R, the newer WinKawaks session:

- `0x6C -> 0x73` remained deterministic in both runs: zero ambiguous fine-state mappings.
- `0x70 -> 0x77` remained deterministic in both runs: zero ambiguous fine-state mappings.
- `0xB9` remained almost static on stationary/pure-vertical transitions and changed strongly when a horizontal component was present, replicating the horizontal locomotion/walk-phase interpretation.
- `0xBB` remained almost absent from stationary/pure-vertical changes; on horizontal/diagonal changes its updates were overwhelmingly `-1`, replicating the horizontal countdown/step-timer interpretation.
- `0xC6/0x3E` showed only the three pairs `00/1C`, `01/FC`, `02/DC` in both new-session runs, motivating an explicit exact-encoding test across the full five-run corpus.

### Automatic decision after run5

Do not blindly queue another generic 60-second burst. Five passive runs have produced no `0x00` allocation transition, and run5 showed that very high raw diversity does not guarantee retarget coverage. Continue offline semantic decomposition and cross-session replication first. A future staged allocation/reuse capture should only be requested if allocation semantics become the highest-value unresolved blocker; it remains separate from Browser/WASM production evidence.
'''
    anchors = ['## Current priorities', '## Current automatic priorities', '## Coverage gaps']
    pos = next((s.find(a) for a in anchors if s.find(a) != -1), -1)
    if pos == -1:
        s += block
    else:
        s = s[:pos] + block + '\n' + s[pos:]

p.write_text(s, encoding='utf-8')
