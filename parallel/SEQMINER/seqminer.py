#!/usr/bin/env python3
"""SEQMINER v3 — WinKawaks-local ordered enemy sequence miner."""
import argparse
import glob
import gzip
import json
import os
from collections import Counter, defaultdict

STRIDE = 0xE0
PLAYERS = 3
ENEMIES = 20
BLOCK = STRIDE * (PLAYERS + ENEMIES)
FLAG_MASK = 0x001C0000

FIELDS = {
    "type": (0x24, 1),
    "pulse28": (0x28, 1),
    "action2d": (0x2D, 1),
    "state2e": (0x2E, 1),
    "cursor": (0x2F, 4),
    "timer34": (0x34, 1),
    "mode35": (0x35, 1),
    "gate37": (0x37, 1),
    "timer42": (0x42, 1),
    "assoc_ptr": (0x3D, 2),
    "fine6c": (0x6C, 1),
    "target": (0x6D, 2),
    "fine70": (0x70, 1),
    "phase72": (0x72, 1),
    "coarse73": (0x73, 1),
    "coarse77": (0x77, 1),
    "flag99": (0x99, 1),
    "profile_b0": (0xB0, 1),
    "profile_b4": (0xB4, 1),
    "profile_b6": (0xB6, 1),
    "walk_b9": (0xB9, 1),
    "walk_timer_bb": (0xBB, 1),
    "assoc_c6": (0xC6, 1),
    "sync_cc": (0xCC, 1),
}

CORE = (
    "type",
    "action2d",
    "state2e",
    "logical_cursor",
    "cursor_flags",
    "mode35",
    "gate37",
    "fine6c",
    "fine70",
    "phase72",
    "coarse73",
    "coarse77",
)

CTX = (
    "target",
    "assoc_ptr",
    "assoc_c6",
    "split_ref",
    "sync_cc",
    "timer42",
    "profile_b0",
    "profile_b4",
    "profile_b6",
    "pulse28",
    "flag99",
    "walk_b9",
    "walk_timer_bb",
)


def u(buf, off, width, signed=False):
    return int.from_bytes(buf[off : off + width], "big", signed=signed)


def sgn(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def rows(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def rawblock(obj):
    if isinstance(obj, dict) and isinstance(obj.get("rawBlockHex"), str):
        try:
            buf = bytes.fromhex(obj["rawBlockHex"].strip())
            if len(buf) >= BLOCK:
                return buf[:BLOCK]
        except ValueError:
            pass

    stack = [obj]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str) and any(
                    token in key.lower() for token in ("raw", "block", "bytes", "data")
                ):
                    try:
                        buf = bytes.fromhex(value.strip())
                        if len(buf) >= BLOCK:
                            return buf[:BLOCK]
                    except ValueError:
                        pass
                elif isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(item, list):
            stack.extend(item)
    return None


def frame_id(obj, fallback):
    for key in ("sequence", "frame", "frameIndex", "frame_index", "seq", "sampleIndex"):
        if isinstance(obj, dict) and isinstance(obj.get(key), (int, float)):
            return int(obj[key])
    return fallback


def state(enemy):
    out = {name: u(enemy, off, width) for name, (off, width) in FIELDS.items()}
    out["logical_cursor"] = out["cursor"] & ~FLAG_MASK
    out["cursor_flags"] = out["cursor"] & FLAG_MASK
    out["split_ref"] = (enemy[0x6F] << 8) | enemy[0x68]
    out["x"] = u(enemy, 0x07, 4, True)
    out["y"] = u(enemy, 0x0B, 4, True)
    return out


def core(st):
    return tuple(st[name] for name in CORE)


def context(st):
    return core(st) + tuple(st[name] for name in CTX)


def guard(st):
    # B0 is deliberately excluded: retained EFIELD evidence shows genuine within-episode changes.
    return (st["type"], st["profile_b4"], st["profile_b6"])


def timer_bucket(delta):
    if delta <= 0:
        return "0"
    if delta == 1:
        return "1"
    if delta == 2:
        return "2"
    if delta <= 5:
        return "3-5"
    if delta <= 10:
        return "6-10"
    return "11+"


def hold_bucket(frames):
    if frames <= 0:
        return "0"
    if frames == 1:
        return "1"
    if frames <= 3:
        return "2-3"
    if frames <= 9:
        return "4-9"
    if frames <= 29:
        return "10-29"
    return "30+"


def reload_delta_bucket(delta):
    if delta <= 1:
        return "1"
    if delta <= 3:
        return "2-3"
    if delta <= 7:
        return "4-7"
    if delta <= 15:
        return "8-15"
    return "16+"


def new_distinct(fi, st):
    return {
        "frameStart": fi,
        "frameEnd": fi,
        "dwellFrames": 1,
        "timerStart": st["timer34"],
        "timerEnd": st["timer34"],
        "timerMin": st["timer34"],
        "timerMax": st["timer34"],
        "timer42Start": st["timer42"],
        "timer42End": st["timer42"],
        "timer42Min": st["timer42"],
        "timer42Max": st["timer42"],
        # Same-CORE reloads are retained here; cycle-level reload tracking below also
        # captures reloads that coincide with a CORE/mode transition.
        "positiveTimer34Reloads": [],
        "timer1Frames": int(st["timer34"] == 1),
        "terminalTimer1Frames": int(st["timer34"] == 1),
        **st,
    }


def extend_distinct(item, fi, st):
    item["frameEnd"] = fi
    item["dwellFrames"] = max(1, fi - item["frameStart"] + 1)
    prev34 = item["timerEnd"]
    if st["timer34"] > prev34:
        item["positiveTimer34Reloads"].append(
            {"frameOffset": fi - item["frameStart"], "from": prev34, "to": st["timer34"]}
        )
    item["timerEnd"] = st["timer34"]
    item["timerMin"] = min(item["timerMin"], st["timer34"])
    item["timerMax"] = max(item["timerMax"], st["timer34"])
    item["timer42End"] = st["timer42"]
    item["timer42Min"] = min(item["timer42Min"], st["timer42"])
    item["timer42Max"] = max(item["timer42Max"], st["timer42"])
    if st["timer34"] == 1:
        item["timer1Frames"] += 1
        item["terminalTimer1Frames"] += 1
    else:
        item["terminalTimer1Frames"] = 0


def scene_meta(obj, path):
    # Preserve all authoritative dimensions when they exist instead of silently
    # dropping room/wave after the first matching key.
    parts = []
    if isinstance(obj, dict):
        for key in ("stage", "scene", "sceneId", "room", "wave"):
            if obj.get(key) is not None:
                parts.append(f"{key}={obj[key]}")
    if parts:
        return "|".join(parts), "explicit"
    return os.path.basename(path), "capture-fallback"


def event_value(enemy, st, attack_offset, attack_width, endian):
    if not st["type"]:
        return 0
    if attack_offset is None:
        return st["coarse73"]
    if attack_offset < 0 or attack_offset + attack_width > STRIDE:
        raise ValueError("attack field outside 0xE0 enemy object")
    return int.from_bytes(
        enemy[attack_offset : attack_offset + attack_width], endian, signed=False
    )


def new_cycle(path, scene, quality, slot, fi, st):
    c = {
        "source": os.path.basename(path),
        "scene": scene,
        "sceneLabelQuality": quality,
        "slot": slot,
        "guard": guard(st),
        "type": st["type"],
        "start_frame": fi,
        "last_zero_frame": fi,
        "target_start": st["target"],
        "last_target": st["target"],
        "last_assoc_c6": st["assoc_c6"],
        "last_split_ref": st["split_ref"],
        "target_changes": [],
        "association_changes": [],
        "split_ref_changes": [],
        "timer34_reload_events": [],
        "states": [],
        # Private running fields are stripped before a resolved cycle is emitted.
        "_last_timer34": st["timer34"],
        "_last_timer42": st["timer42"],
        "_last_core": core(st),
        "_last_cursor": st["logical_cursor"],
        "_last_mode35": st["mode35"],
        "_last_phase": (
            st["fine6c"],
            st["fine70"],
            st["phase72"],
            st["coarse73"],
            st["coarse77"],
        ),
        "_timer1_run": int(st["timer34"] == 1),
    }
    return c


def track_zero_prefix_timer(cur, fi, st):
    """Track +0x34 positive loads before the future event without CORE leakage.

    This is deliberately cycle-level. Retained delayed-1B evidence shows canonical
    +0x34 positive loads can coincide with +0x35 changes, which split CORE states;
    state-local reload tracking alone would therefore miss the edge.
    """
    prev34 = cur["_last_timer34"]
    current_core = core(st)
    current_phase = (
        st["fine6c"],
        st["fine70"],
        st["phase72"],
        st["coarse73"],
        st["coarse77"],
    )
    if st["timer34"] > prev34:
        cur["timer34_reload_events"].append(
            {
                "frame": fi,
                "from": prev34,
                "to": st["timer34"],
                "sameCore": cur["_last_core"] == current_core,
                "coreFrom": cur["_last_core"],
                "coreTo": current_core,
                "cursorFrom": cur["_last_cursor"],
                "cursorTo": st["logical_cursor"],
                "cursorChanged": cur["_last_cursor"] != st["logical_cursor"],
                "mode35From": cur["_last_mode35"],
                "mode35To": st["mode35"],
                "mode35Changed": cur["_last_mode35"] != st["mode35"],
                "phaseFrom": cur["_last_phase"],
                "phaseTo": current_phase,
                "timer42From": cur["_last_timer42"],
                "timer42To": st["timer42"],
                "timer42Changed": cur["_last_timer42"] != st["timer42"],
                "timer1FramesBeforeReload": cur["_timer1_run"],
            }
        )

    cur["_timer1_run"] = cur["_timer1_run"] + 1 if st["timer34"] == 1 else 0
    cur["_last_timer34"] = st["timer34"]
    cur["_last_timer42"] = st["timer42"]
    cur["_last_core"] = current_core
    cur["_last_cursor"] = st["logical_cursor"]
    cur["_last_mode35"] = st["mode35"]
    cur["_last_phase"] = current_phase


def strip_private_cycle_state(cur):
    for key in (
        "_last_timer34",
        "_last_timer42",
        "_last_core",
        "_last_cursor",
        "_last_mode35",
        "_last_phase",
        "_timer1_run",
    ):
        cur.pop(key, None)


def mine(paths, attack_offset=None, attack_width=2, endian="big"):
    cycles = []
    ceilings = defaultdict(int)
    meta = {"frames": {}, "unresolved": Counter()}

    for path in paths:
        active = {}
        frames = 0
        capture_scene_qualities = Counter()

        for i, obj in enumerate(rows(path)):
            rb = rawblock(obj)
            if rb is None:
                continue
            fi = frame_id(obj, i)
            scene, quality = scene_meta(obj, path)
            capture_scene_qualities[quality] += 1
            frames += 1

            for slot in range(ENEMIES):
                off = (PLAYERS + slot) * STRIDE
                enemy = rb[off : off + STRIDE]
                st = state(enemy)
                ev = event_value(enemy, st, attack_offset, attack_width, endian)

                if st["type"]:
                    ceilings[st["logical_cursor"]] = max(
                        ceilings[st["logical_cursor"]], st["timer34"]
                    )

                cur = active.get(slot)
                if not st["type"]:
                    if cur and cur["states"]:
                        meta["unresolved"]["type_absent_before_event"] += 1
                    active.pop(slot, None)
                    continue

                g = guard(st)
                if cur and g != cur["guard"]:
                    if cur["states"]:
                        meta["unresolved"]["episode_guard_change_before_event"] += 1
                    active.pop(slot, None)
                    cur = None

                if ev == 0:
                    if cur is None:
                        cur = new_cycle(path, scene, quality, slot, fi, st)
                        active[slot] = cur
                    else:
                        track_zero_prefix_timer(cur, fi, st)

                    if st["target"] != cur["last_target"]:
                        cur["target_changes"].append(
                            {"frame": fi, "from": cur["last_target"], "to": st["target"]}
                        )
                        cur["last_target"] = st["target"]

                    if st["assoc_c6"] != cur["last_assoc_c6"]:
                        cur["association_changes"].append(
                            {
                                "frame": fi,
                                "from": cur["last_assoc_c6"],
                                "to": st["assoc_c6"],
                            }
                        )
                        cur["last_assoc_c6"] = st["assoc_c6"]

                    if st["split_ref"] != cur["last_split_ref"]:
                        cur["split_ref_changes"].append(
                            {
                                "frame": fi,
                                "from": cur["last_split_ref"],
                                "to": st["split_ref"],
                            }
                        )
                        cur["last_split_ref"] = st["split_ref"]

                    if not cur["states"] or core(cur["states"][-1]) != core(st):
                        cur["states"].append(new_distinct(fi, st))
                    else:
                        extend_distinct(cur["states"][-1], fi, st)
                    cur["last_zero_frame"] = fi

                else:
                    if cur and cur["states"]:
                        cur["active_frame"] = fi
                        cur["eventual_attack"] = ev
                        cur["target_end"] = st["target"]

                        if st["target"] != cur["last_target"]:
                            cur["target_changes"].append(
                                {
                                    "frame": fi,
                                    "from": cur["last_target"],
                                    "to": st["target"],
                                    "atEventEdge": True,
                                }
                            )
                            cur["last_target"] = st["target"]

                        cur["target_stable"] = not cur["target_changes"]
                        cur["active_state"] = st
                        strip_private_cycle_state(cur)
                        cycles.append(cur)
                    active.pop(slot, None)

        meta["frames"][os.path.basename(path)] = frames
        for quality, count in capture_scene_qualities.items():
            meta.setdefault("sceneLabelQualityFrames", Counter())[quality] += count
        meta["unresolved"]["open_at_eof"] += sum(
            1 for c in active.values() if c["states"]
        )

    # Record-relative timer normalization and cross-CORE reload normalization.
    for c in cycles:
        for st in c["states"]:
            ceiling = ceilings[st["logical_cursor"]]
            st["timerCeiling"] = ceiling
            for src, dst in (
                ("timerStart", "timerStartBucket"),
                ("timerEnd", "timerEndBucket"),
                ("timerMin", "timerMinBucket"),
                ("timerMax", "timerMaxBucket"),
            ):
                st[dst] = timer_bucket(max(0, ceiling - st[src]))
            st["terminalTimer1Bucket"] = hold_bucket(st["terminalTimer1Frames"])

        for reload in c["timer34_reload_events"]:
            from_ceiling = ceilings[reload["cursorFrom"]]
            to_ceiling = ceilings[reload["cursorTo"]]
            reload["delta"] = reload["to"] - reload["from"]
            reload["deltaBucket"] = reload_delta_bucket(reload["delta"])
            reload["fromBucket"] = timer_bucket(
                max(0, from_ceiling - reload["from"])
            )
            reload["toBucket"] = timer_bucket(max(0, to_ceiling - reload["to"]))
            reload["timer1HoldBucketBeforeReload"] = hold_bucket(
                reload["timer1FramesBeforeReload"]
            )

    all_reloads = [r for c in cycles for r in c["timer34_reload_events"]]
    meta["timer34ReloadAudit"] = {
        "zeroPrefixPositiveReloadEvents": len(all_reloads),
        "sameCore": sum(r["sameCore"] for r in all_reloads),
        "crossCore": sum(not r["sameCore"] for r in all_reloads),
        "cursorChanged": sum(r["cursorChanged"] for r in all_reloads),
        "mode35Changed": sum(r["mode35Changed"] for r in all_reloads),
        "timer42Changed": sum(r["timer42Changed"] for r in all_reloads),
    }
    meta["unresolved"] = dict(meta["unresolved"])
    meta["sceneLabelQualityFrames"] = dict(
        meta.get("sceneLabelQualityFrames", {})
    )
    return cycles, meta


def exact_state(st):
    reloads = tuple(
        (r["frameOffset"], r["from"], r["to"])
        for r in st["positiveTimer34Reloads"]
    )
    return core(st) + (
        st["timerStart"],
        st["timerEnd"],
        st["timerMin"],
        st["timerMax"],
        st["terminalTimer1Frames"],
        reloads,
        st["timer42Start"],
        st["timer42End"],
    )


def norm_state(st):
    first = (
        st["positiveTimer34Reloads"][0]["frameOffset"]
        if st["positiveTimer34Reloads"]
        else -1
    )
    return core(st) + (
        st["timerStartBucket"],
        st["timerEndBucket"],
        st["timerMinBucket"],
        st["timerMaxBucket"],
        st["terminalTimer1Bucket"],
        len(st["positiveTimer34Reloads"]),
        first,
    )


def reload_exact(reload):
    return (
        tuple(reload["coreFrom"]),
        tuple(reload["coreTo"]),
        reload["from"],
        reload["to"],
        reload["timer1FramesBeforeReload"],
        reload["timer42From"],
        reload["timer42To"],
    )


def reload_norm(reload):
    return (
        tuple(reload["coreFrom"]),
        tuple(reload["coreTo"]),
        reload["fromBucket"],
        reload["toBucket"],
        reload["deltaBucket"],
        reload["timer1HoldBucketBeforeReload"],
        reload["mode35Changed"],
        reload["cursorChanged"],
        reload["timer42Changed"],
    )


def features(c):
    core_states = [core(x) for x in c["states"]]
    context_states = [context(x) for x in c["states"]]
    exact_states = [exact_state(x) for x in c["states"]]
    norm_states = [norm_state(x) for x in c["states"]]

    def tail(seq, n):
        return [tuple(seq[-n:])] if len(seq) >= n else []

    reloads = c.get("timer34_reload_events", [])
    cross_core_reloads = [r for r in reloads if not r["sameCore"]]

    return {
        "final": [core_states[-1]],
        "final_context": [context_states[-1]],
        "final_timer_exact": [exact_states[-1]],
        "final_timer_norm": [norm_states[-1]],
        "tail2": tail(core_states, 2),
        "tail3": tail(core_states, 3),
        "tail2_context": tail(context_states, 2),
        "tail3_context": tail(context_states, 3),
        "tail2_timer_exact": tail(exact_states, 2),
        "tail3_timer_exact": tail(exact_states, 3),
        "tail2_timer_norm": tail(norm_states, 2),
        "tail3_timer_norm": tail(norm_states, 3),
        "pair": [
            tuple(core_states[i : i + 2]) for i in range(len(core_states) - 1)
        ],
        "triple": [
            tuple(core_states[i : i + 3]) for i in range(len(core_states) - 2)
        ],
        "pair_timer_exact": [
            tuple(exact_states[i : i + 2]) for i in range(len(exact_states) - 1)
        ],
        "triple_timer_exact": [
            tuple(exact_states[i : i + 3])
            for i in range(len(exact_states) - 2)
        ],
        "pair_timer_norm": [
            tuple(norm_states[i : i + 2]) for i in range(len(norm_states) - 1)
        ],
        "triple_timer_norm": [
            tuple(norm_states[i : i + 3])
            for i in range(len(norm_states) - 2)
        ],
        # These are prefix-only features. Event-edge state is never included.
        "timer34_reload_exact": [reload_exact(r) for r in reloads],
        "timer34_reload_norm": [reload_norm(r) for r in reloads],
        "cross_core_reload_exact": [reload_exact(r) for r in cross_core_reloads],
        "cross_core_reload_norm": [reload_norm(r) for r in cross_core_reloads],
    }


def branchpoints(cycles):
    # Confidence is cycle-based. Repeated loop visits to the same anchor in one
    # cycle remain visible in raw_occurrence_distribution but count only once
    # toward attack_distribution and successor/context support.
    attacks = defaultdict(Counter)
    raw_occurrences = defaultdict(Counter)
    nxt = defaultdict(lambda: defaultdict(Counter))
    prv = defaultdict(lambda: defaultdict(Counter))
    timers = defaultdict(lambda: defaultdict(Counter))

    for c in cycles:
        attack = str(c["eventual_attack"])
        seq = [core(x) for x in c["states"]]
        indices = defaultdict(list)
        for i, value in enumerate(seq):
            indices[sgn(value)].append(i)

        for anchor, positions in indices.items():
            attacks[anchor][attack] += 1
            raw_occurrences[anchor][attack] += len(positions)

            next_values = set()
            prev_values = set()
            timer_values = set()
            for i in positions:
                next_values.add(
                    sgn(seq[i + 1]) if i + 1 < len(seq) else "<EVENT_NEXT>"
                )
                prev_values.add(sgn(seq[i - 1]) if i else "<CYCLE_START>")
                st = c["states"][i]
                timer_values.add(
                    sgn(
                        (
                            st["timerStart"],
                            st["timerEnd"],
                            st["timerMax"],
                            st["terminalTimer1Frames"],
                            st["positiveTimer34Reloads"],
                        )
                    )
                )

            for value in next_values:
                nxt[anchor][attack][value] += 1
            for value in prev_values:
                prv[anchor][attack][value] += 1
            for value in timer_values:
                timers[anchor][attack][value] += 1

    out = []
    for anchor, dist in attacks.items():
        if len(dist) < 2:
            continue
        sets = {attack: set(nxt[anchor][attack]) for attack in dist}
        union = set().union(*sets.values())
        common = set.intersection(*sets.values()) if sets else set()
        out.append(
            {
                "anchor": anchor,
                "attack_distribution": dict(dist),
                "raw_occurrence_distribution": dict(raw_occurrences[anchor]),
                "cycles_with_anchor": sum(dist.values()),
                "raw_occurrences": sum(raw_occurrences[anchor].values()),
                "next_by_attack": {
                    attack: dict(values.most_common(20))
                    for attack, values in nxt[anchor].items()
                },
                "prev_by_attack": {
                    attack: dict(values.most_common(20))
                    for attack, values in prv[anchor].items()
                },
                "timer_profile_by_attack": {
                    attack: dict(values.most_common(20))
                    for attack, values in timers[anchor].items()
                },
                "has_post_anchor_divergence": bool(union - common),
            }
        )

    out.sort(
        key=lambda x: (
            x["has_post_anchor_divergence"],
            len(x["attack_distribution"]),
            x["cycles_with_anchor"],
        ),
        reverse=True,
    )
    return out[:300]


def summarize(cycles, meta, mode):
    by_attack = defaultdict(list)
    counts = defaultdict(lambda: defaultdict(Counter))
    srcs = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    explicit_scenes = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    fallback_scenes = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    targets = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    stable = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
    finals = defaultdict(set)

    for c in cycles:
        attack = str(c["eventual_attack"])
        by_attack[attack].append(c)
        finals[sgn(core(c["states"][-1]))].add(attack)

        for kind, values in features(c).items():
            # Support unit is one resolved future-event cycle, never raw occurrence count.
            for value in {sgn(v) for v in values}:
                counts[kind][value][attack] += 1
                srcs[kind][value][attack].add(c["source"])
                if c["sceneLabelQuality"] == "explicit":
                    explicit_scenes[kind][value][attack].add(c["scene"])
                else:
                    fallback_scenes[kind][value][attack].add(c["scene"])
                targets[kind][value][attack].add(c["target_start"])
                stable[kind][value][attack][
                    "stable" if c["target_stable"] else "changed"
                ] += 1

    candidates = []
    for kind, mapping in counts.items():
        for value, dist in mapping.items():
            total = sum(dist.values())
            if total < 2:
                continue
            winner, support = max(dist.items(), key=lambda item: item[1])
            purity = support / total
            source_count = len(srcs[kind][value][winner])
            explicit_scene_count = len(explicit_scenes[kind][value][winner])
            fallback_scene_count = len(fallback_scenes[kind][value][winner])
            target_count = len(targets[kind][value][winner])
            stable_fraction = (
                stable[kind][value][winner]["stable"] / support if support else 0
            )

            evidence = "same_cycle_evidence" if support >= 2 else "discovery_correlation"
            if (
                mode != "phase73-structural-proxy"
                and purity == 1
                and support >= 3
                and source_count >= 2
            ):
                evidence = "potentially_prospectively_testable_candidate"

            score = (
                purity
                * (1 + min(support, 20) / 20)
                * (1 + min(source_count, 3) / 6)
                * (1 + min(target_count, 3) / 9)
                * (0.85 + 0.15 * stable_fraction)
            )
            candidates.append(
                {
                    "kind": kind,
                    "signature": value,
                    "winner_attack": winner,
                    "attack_distribution": dict(dist),
                    "support": support,
                    "total_cycles_with_signature": total,
                    "purity": round(purity, 6),
                    "source_count": source_count,
                    "explicit_scene_count": explicit_scene_count,
                    "capture_fallback_scene_count": fallback_scene_count,
                    "target_count": target_count,
                    "winner_target_stable_fraction": round(stable_fraction, 6),
                    "score": round(score, 6),
                    "evidence_class": evidence,
                }
            )

    candidates.sort(
        key=lambda x: (
            x["evidence_class"] == "potentially_prospectively_testable_candidate",
            x["purity"],
            x["support"],
            x["source_count"],
            x["target_count"],
            x["score"],
        ),
        reverse=True,
    )

    return {
        "version": "seqminer-generated-v3",
        "mode": mode,
        "evidenceNamespace": "WinKawaks-local-discovery-only",
        "productionPromotion": False,
        "supportUnit": "unique_resolved_cycle",
        "semanticGuard": (
            "phase73 mode is structural proxy only; explicit mode requires a "
            "separately proven WinKawaks-local attack field"
        ),
        "total_cycles": len(cycles),
        "meta": meta,
        "attacks": {
            attack: {
                "cycles": len(items),
                "sources": sorted({c["source"] for c in items}),
                "explicitScenes": sorted(
                    {
                        c["scene"]
                        for c in items
                        if c["sceneLabelQuality"] == "explicit"
                    }
                ),
                "captureFallbackLabels": sorted(
                    {
                        c["scene"]
                        for c in items
                        if c["sceneLabelQuality"] != "explicit"
                    }
                ),
                "targets": sorted({c["target_start"] for c in items}),
                "targetStableCycles": sum(c["target_stable"] for c in items),
            }
            for attack, items in by_attack.items()
        },
        "ambiguous_final_states": [
            {"signature": signature, "attacks": sorted(attacks)}
            for signature, attacks in finals.items()
            if len(attacks) > 1
        ],
        "ambiguous_state_branchpoints": branchpoints(cycles),
        "ranked_candidates": candidates[:500],
    }


def write(outdir, cycles, summary):
    os.makedirs(outdir, exist_ok=True)

    with open(
        os.path.join(outdir, "CYCLES.generated.jsonl"), "w", encoding="utf-8"
    ) as f:
        for cycle in cycles:
            f.write(json.dumps(cycle, ensure_ascii=False) + "\n")

    for name, obj in (
        ("CANDIDATES.generated.json", summary),
        (
            "BRANCHPOINTS.generated.json",
            summary["ambiguous_state_branchpoints"],
        ),
    ):
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)

    lines = [
        "# SEQMINER generated sequence atlas",
        "",
        f"- version: `{summary['version']}`",
        f"- mode: `{summary['mode']}`",
        f"- support unit: `{summary['supportUnit']}`",
        f"- cycles: **{summary['total_cycles']}**",
        f"- zero-prefix +0x34 reload audit: `{summary['meta'].get('timer34ReloadAudit', {})}`",
        "",
    ]
    for attack, data in summary["attacks"].items():
        lines += [
            f"## Event `{attack}`",
            f"- cycles: {data['cycles']}",
            f"- sources: {data['sources']}",
            f"- explicit scenes: {data['explicitScenes']}",
            f"- targets: {data['targets']}",
            "",
        ]

    lines += ["## Top candidates", ""]
    for candidate in summary["ranked_candidates"][:75]:
        lines.append(
            f"- `{candidate['kind']}` -> `{candidate['winner_attack']}` "
            f"{candidate['support']}/{candidate['total_cycles_with_signature']} "
            f"purity {candidate['purity']:.3f}; sources {candidate['source_count']}; "
            f"explicit-scenes {candidate['explicit_scene_count']}; "
            f"targets {candidate['target_count']} — `{candidate['evidence_class']}`"
        )
    with open(
        os.path.join(outdir, "SEQUENCE_ATLAS.generated.md"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(lines) + "\n")

    lines = ["# SEQMINER generated ambiguous branchpoints", ""]
    for branch in summary["ambiguous_state_branchpoints"][:75]:
        lines += [
            f"## `{branch['anchor']}`",
            f"- cycle attack support: `{branch['attack_distribution']}`",
            f"- raw repeated occurrences: `{branch['raw_occurrence_distribution']}`",
            f"- post-anchor divergence: `{branch['has_post_anchor_divergence']}`",
            f"- next: `{branch['next_by_attack']}`",
            "",
        ]
    with open(
        os.path.join(outdir, "ATTACK_BRANCHES.generated.md"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--captures", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--attack-offset", type=lambda value: int(value, 0))
    parser.add_argument("--attack-width", type=int, default=2)
    parser.add_argument(
        "--attack-endian", choices=("big", "little", "be", "le"), default="be"
    )
    args = parser.parse_args()

    paths = sorted(
        glob.glob(os.path.join(args.captures, "*.jsonl"))
        + glob.glob(os.path.join(args.captures, "*.jsonl.gz"))
    )
    endian = "big" if args.attack_endian in ("big", "be") else "little"

    cycles, meta = mine(paths, args.attack_offset, args.attack_width, endian)
    mode = (
        "phase73-structural-proxy"
        if args.attack_offset is None
        else f"explicit-attack-offset-{hex(args.attack_offset)}"
    )
    summary = summarize(cycles, meta, mode)
    write(args.output, cycles, summary)

    print(
        json.dumps(
            {
                "version": summary["version"],
                "mode": mode,
                "files": len(paths),
                "cycles": len(cycles),
                "ambiguousBranchpoints": len(
                    summary["ambiguous_state_branchpoints"]
                ),
                "candidates": len(summary["ranked_candidates"]),
                "zeroPrefixTimer34ReloadAudit": meta["timer34ReloadAudit"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
