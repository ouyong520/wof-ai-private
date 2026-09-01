#!/usr/bin/env python3
import argparse, gzip, json, os, glob
from collections import Counter, defaultdict

STRIDE = 0xE0
PLAYER_COUNT = 3
ENEMY_COUNT = 20
BLOCK = STRIDE * (PLAYER_COUNT + ENEMY_COUNT)
CURSOR_FLAG_MASK = 0x001C0000

FIELDS = {
    'type': (0x24, 1),
    'action2d': (0x2D, 1),
    'state2e': (0x2E, 1),
    'cursor': (0x2F, 4),
    'timer34': (0x34, 1),
    'mode35': (0x35, 1),
    'gate37': (0x37, 1),
    'assoc_ptr': (0x3D, 2),
    'fine6c': (0x6C, 1),
    'target': (0x6D, 2),
    'fine70': (0x70, 1),
    'phase72': (0x72, 1),
    'coarse73': (0x73, 1),
    'coarse77': (0x77, 1),
    'profile_b0': (0xB0, 1),
    'profile_b4': (0xB4, 1),
    'profile_b6': (0xB6, 1),
    'walk_b9': (0xB9, 1),
    'walk_timer_bb': (0xBB, 1),
    'assoc_c6': (0xC6, 1),
    'x_raw': (0x07, 4),
    'y_raw': (0x0B, 4),
}


def be(buf, off, width, signed=False):
    return int.from_bytes(buf[off:off + width], 'big', signed=signed)


def logical_cursor(v):
    return v & ~CURSOR_FLAG_MASK


def load_lines(path):
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def find_raw_blob(obj):
    # Collector v1 uses rawBlockHex. Recursive fallback keeps older compatible streams usable.
    if isinstance(obj, dict) and isinstance(obj.get('rawBlockHex'), str):
        s = obj['rawBlockHex'].strip()
        try:
            b = bytes.fromhex(s)
            if len(b) >= BLOCK:
                return b[:BLOCK]
        except ValueError:
            pass
    stack = [obj]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            for k, v in x.items():
                lk = k.lower()
                if isinstance(v, str) and ('raw' in lk or 'block' in lk or 'bytes' in lk or 'data' in lk):
                    s = v.strip()
                    try:
                        if len(s) >= BLOCK * 2 and all(c in '0123456789abcdefABCDEF' for c in s[:min(len(s), 200)]):
                            b = bytes.fromhex(s)
                            if len(b) >= BLOCK:
                                return b[:BLOCK]
                    except ValueError:
                        pass
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(x, list):
            stack.extend(x)
    return None


def frame_index(obj, fallback):
    for k in ('sequence', 'frame', 'frameIndex', 'frame_index', 'seq', 'sampleIndex'):
        if isinstance(obj, dict) and isinstance(obj.get(k), (int, float)):
            return int(obj[k])
    return fallback


def scene_id(obj, path):
    for k in ('scene', 'sceneId', 'room', 'stage', 'taskId', 'task_id', 'captureId'):
        if isinstance(obj, dict) and obj.get(k) is not None:
            return str(obj[k])
    return os.path.basename(path)


def state_from_enemy(e):
    d = {name: be(e, off, width) for name, (off, width) in FIELDS.items()}
    d['x'] = be(e, 0x07, 4, signed=True)
    d['y'] = be(e, 0x0B, 4, signed=True)
    d['logical_cursor'] = logical_cursor(d['cursor'])
    d['cursor_flags'] = d['cursor'] & CURSOR_FLAG_MASK
    return d


def identity_key(s):
    # Stable episode context known from retained EFIELD evidence.
    return (s['type'], s['profile_b6'], s['profile_b0'], s['profile_b4'])


def base_key(s):
    names = [
        'type', 'action2d', 'state2e', 'logical_cursor', 'cursor_flags',
        'mode35', 'gate37', 'fine6c', 'fine70', 'phase72', 'coarse73',
        'coarse77', 'target', 'assoc_ptr', 'assoc_c6', 'profile_b0',
        'profile_b4', 'profile_b6', 'walk_b9', 'walk_timer_bb'
    ]
    return tuple(s[n] for n in names)


def exact_key(s):
    return base_key(s) + (s['timer34'],)


def timer_bucket(delta):
    if delta <= 0:
        return '0'
    if delta == 1:
        return '1'
    if delta == 2:
        return '2'
    if delta <= 5:
        return '3-5'
    if delta <= 10:
        return '6-10'
    return '11+'


def sig(value):
    # JSON encoding avoids collisions between nested pair/triple tuples.
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False)


def close_distinct_state(cur, frame_end):
    if cur and cur['states']:
        st = cur['states'][-1]
        st['frameEnd'] = frame_end
        st['dwellFrames'] = max(1, frame_end - st['frameStart'] + 1)


def mine(paths, attack_offset=None, attack_width=2, attack_endian='big'):
    records = []
    ceilings = defaultdict(int)
    cycles = []
    source_counts = Counter()

    for path in paths:
        frame_count = 0
        for i, obj in enumerate(load_lines(path)):
            raw = find_raw_blob(obj)
            if raw is None or len(raw) < BLOCK:
                continue
            fi = frame_index(obj, i)
            sc = scene_id(obj, path)
            for slot in range(ENEMY_COUNT):
                off = (PLAYER_COUNT + slot) * STRIDE
                e = raw[off:off + STRIDE]
                s = state_from_enemy(e)
                if s['type'] == 0:
                    records.append((path, sc, fi, slot, None, s))
                    continue
                if attack_offset is None:
                    attack = s['coarse73']
                else:
                    attack = int.from_bytes(
                        e[attack_offset:attack_offset + attack_width],
                        attack_endian,
                        signed=False,
                    )
                ceilings[s['logical_cursor']] = max(ceilings[s['logical_cursor']], s['timer34'])
                records.append((path, sc, fi, slot, attack, s))
            frame_count += 1
        source_counts[os.path.basename(path)] = frame_count

    records.sort(key=lambda x: (x[0], x[2], x[3]))
    by_slot = {}

    for path, sc, fi, slot, attack, s in records:
        slot_key = (path, slot)
        cur = by_slot.get(slot_key)
        ident = identity_key(s) if s['type'] else None

        # Type/profile identity changes terminate the old zero-cycle rather than allowing slot reuse to leak across instances.
        if cur is not None and ident != cur['identity']:
            close_distinct_state(cur, cur['last_frame'])
            by_slot.pop(slot_key, None)
            cur = None

        if s['type'] == 0:
            continue

        if attack == 0:
            if cur is None:
                cur = {
                    'source': os.path.basename(path),
                    'scene': sc,
                    'slot': slot,
                    'identity': ident,
                    'type': s['type'],
                    'target_start': s['target'],
                    'target_changes': [],
                    'states': [],
                    'start_frame': fi,
                    'last_frame': fi,
                }
                by_slot[slot_key] = cur
            if s['target'] != cur['target_start'] and (not cur['target_changes'] or cur['target_changes'][-1]['target'] != s['target']):
                cur['target_changes'].append({'frame': fi, 'target': s['target']})
            cur['last_frame'] = fi
            bk = base_key(s)
            if not cur['states'] or base_key(cur['states'][-1]) != bk:
                close_distinct_state(cur, fi - 1)
                cur['states'].append({'frameStart': fi, 'frameEnd': fi, 'dwellFrames': 1, **s})
            else:
                close_distinct_state(cur, fi)
        else:
            if cur and cur['states']:
                close_distinct_state(cur, max(cur['last_frame'], fi - 1))
                cur['active_frame'] = fi
                cur['eventual_attack'] = attack
                cur['target_end'] = s['target']
                cur['target_stable'] = (cur['target_start'] == s['target'] and not cur['target_changes'])
                cur['active_state'] = s
                cycles.append(cur)
            by_slot.pop(slot_key, None)

    for c in cycles:
        for st in c['states']:
            st['timer_ceiling'] = ceilings[st['logical_cursor']]
            st['timer_delta'] = max(0, st['timer_ceiling'] - st['timer34'])
            st['timer_bucket'] = timer_bucket(st['timer_delta'])
    return cycles, source_counts


def summarize(cycles):
    out = {
        'total_cycles': len(cycles),
        'attacks': {},
        'ambiguous_final_states': [],
        'ranked_candidates': [],
    }
    by_attack = defaultdict(list)
    final_attack_sets = defaultdict(set)
    feature_counts = defaultdict(lambda: defaultdict(Counter))
    feature_sources = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    feature_scenes = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    feature_targets = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

    for c in cycles:
        a = str(c['eventual_attack'])
        by_attack[a].append(c)
        exact = [exact_key(s) for s in c['states']]
        base = [base_key(s) for s in c['states']]
        norm = [base_key(s) + (s['timer_bucket'],) for s in c['states']]
        features = {
            'final': [base[-1]],
            'final_exact': [exact[-1]],
            'final_norm': [norm[-1]],
            'tail2': [tuple(base[-2:])] if len(base) >= 2 else [],
            'tail3': [tuple(base[-3:])] if len(base) >= 3 else [],
            'tail2_exact': [tuple(exact[-2:])] if len(exact) >= 2 else [],
            'tail3_exact': [tuple(exact[-3:])] if len(exact) >= 3 else [],
            'tail2_norm': [tuple(norm[-2:])] if len(norm) >= 2 else [],
            'tail3_norm': [tuple(norm[-3:])] if len(norm) >= 3 else [],
            'pair': [tuple(base[i:i + 2]) for i in range(len(base) - 1)],
            'triple': [tuple(base[i:i + 3]) for i in range(len(base) - 2)],
            'pair_exact': [tuple(exact[i:i + 2]) for i in range(len(exact) - 1)],
            'triple_exact': [tuple(exact[i:i + 3]) for i in range(len(exact) - 2)],
            'pair_norm': [tuple(norm[i:i + 2]) for i in range(len(norm) - 1)],
            'triple_norm': [tuple(norm[i:i + 3]) for i in range(len(norm) - 2)],
        }
        final_attack_sets[sig(base[-1])].add(a)
        for kind, vals in features.items():
            for v in {sig(v) for v in vals}:
                feature_counts[kind][v][a] += 1
                feature_sources[kind][v][a].add(c['source'])
                feature_scenes[kind][v][a].add(c['scene'])
                feature_targets[kind][v][a].add(c['target_start'])

    out['attacks'] = {
        a: {
            'cycles': len(cs),
            'sources': sorted({c['source'] for c in cs}),
            'scenes': sorted({c['scene'] for c in cs}),
            'targets': sorted({c['target_start'] for c in cs}),
        }
        for a, cs in by_attack.items()
    }
    out['ambiguous_final_states'] = [
        {'signature': k, 'attacks': sorted(v)}
        for k, v in final_attack_sets.items()
        if len(v) > 1
    ]

    candidates = []
    for kind, mp in feature_counts.items():
        for v, ac in mp.items():
            total = sum(ac.values())
            winner, n = max(ac.items(), key=lambda kv: kv[1])
            purity = n / total
            src = len(feature_sources[kind][v][winner])
            scenes = len(feature_scenes[kind][v][winner])
            targets = len(feature_targets[kind][v][winner])
            if total < 2:
                continue
            score = (
                purity
                * (1 + min(total, 20) / 20)
                * (1 + min(src, 3) / 6)
                * (1 + min(scenes, 3) / 6)
                * (1 + min(targets, 3) / 9)
            )
            evidence = 'same_cycle_evidence' if n >= 2 else 'discovery_correlation'
            if purity == 1 and n >= 3 and src >= 2 and scenes >= 2:
                evidence = 'potentially_prospectively_testable_candidate'
            candidates.append({
                'kind': kind,
                'signature': v,
                'winner_attack': winner,
                'support': n,
                'total_occurrences': total,
                'purity': round(purity, 6),
                'source_count': src,
                'scene_count': scenes,
                'target_count': targets,
                'score': round(score, 6),
                'evidence_class': evidence,
            })

    candidates.sort(
        key=lambda x: (
            x['evidence_class'] == 'potentially_prospectively_testable_candidate',
            x['purity'], x['support'], x['source_count'], x['scene_count'],
            x['target_count'], x['score'],
        ),
        reverse=True,
    )
    out['ranked_candidates'] = candidates[:200]
    return out


def write_outputs(outdir, cycles, summary, source_counts, mode):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'CANDIDATES.generated.json'), 'w', encoding='utf-8') as f:
        json.dump(
            {'mode': mode, 'source_frame_counts': dict(source_counts), 'summary': summary},
            f, indent=2, ensure_ascii=False,
        )
    with open(os.path.join(outdir, 'CYCLES.generated.jsonl'), 'w', encoding='utf-8') as f:
        for c in cycles:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')

    lines = [
        '# SEQMINER generated sequence atlas', '',
        f'- mode: `{mode}`',
        f'- resolved cycles: **{len(cycles)}**', '',
    ]
    for a, d in summary['attacks'].items():
        lines += [
            f'## Eventual attack/proxy `{a}`',
            f"- cycles: {d['cycles']}",
            f"- sources: {', '.join(d['sources']) or '(none)'}",
            f"- scenes: {', '.join(d['scenes']) or '(none)'}",
            f"- targets: {d['targets']}", '',
        ]
    lines += ['## Ambiguous final states', '']
    for x in summary['ambiguous_final_states'][:50]:
        lines.append(f"- attacks {x['attacks']}: `{x['signature']}`")
    lines += ['', '## Top candidates', '']
    for c in summary['ranked_candidates'][:50]:
        lines.append(
            f"- `{c['kind']}` -> `{c['winner_attack']}` support {c['support']}/{c['total_occurrences']} "
            f"purity {c['purity']:.3f}, sources {c['source_count']}, scenes {c['scene_count']}, "
            f"targets {c['target_count']} — `{c['evidence_class']}`"
        )
    with open(os.path.join(outdir, 'SEQUENCE_ATLAS.generated.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--captures', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--attack-offset', type=lambda x: int(x, 0))
    ap.add_argument('--attack-width', type=int, default=2)
    ap.add_argument('--attack-endian', choices=['big', 'little', 'be', 'le'], default='be')
    args = ap.parse_args()

    paths = sorted(
        glob.glob(os.path.join(args.captures, '*.jsonl'))
        + glob.glob(os.path.join(args.captures, '*.jsonl.gz'))
    )
    endian = 'big' if args.attack_endian in ('big', 'be') else 'little'
    cycles, src = mine(paths, args.attack_offset, args.attack_width, endian)
    summary = summarize(cycles)
    mode = (
        'phase73-structural-proxy'
        if args.attack_offset is None
        else f'explicit-attack-offset-{hex(args.attack_offset)}'
    )
    write_outputs(args.output, cycles, summary, src, mode)
    print(json.dumps({
        'mode': mode,
        'files': len(paths),
        'cycles': len(cycles),
        'attacks': summary['attacks'],
    }, indent=2))
