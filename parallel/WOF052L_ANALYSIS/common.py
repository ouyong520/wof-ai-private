from __future__ import annotations

import hashlib
import json
import os
import re
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "wof-052l-analysis-v1"
RECORDER_SCHEMA = "wof-052l-recorder-v1"
FLEET_SCHEMA = "wof-052l-fleet-supervisor-v1"
CANDIDATE_SIG = "S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736"
TARGET_ATTACKS = ("A4704", "A4712")
WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
DEFAULT_MIN_PER_OUTCOME = 2
DEFAULT_MIN_SEQUENCE_SUPPORT = 2
DEFAULT_WATCH_INTERVAL = 5.0

FEATURE_ORDER = [
    "exact_tail3", "exact_tail2", "tm_tail3", "tm_tail2",
    "exact_triple", "exact_pair", "tm_triple", "tm_pair",
    "exact_final", "tm_final",
]
FEATURE_LABEL_ZH = {
    "exact_final": "exact 最终状态",
    "exact_tail2": "exact tail2",
    "exact_tail3": "exact tail3",
    "tm_final": "TM* 最终状态",
    "tm_tail2": "TM* tail2",
    "tm_tail3": "TM* tail3",
    "exact_pair": "exact 有序 pair",
    "exact_triple": "exact 有序 triple",
    "tm_pair": "TM* 有序 pair",
    "tm_triple": "TM* 有序 triple",
}


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_attack(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text.startswith("A"):
        text = text[1:]
    try:
        return f"A{int(text)}"
    except ValueError:
        return f"A{text}" if text else "AUNKNOWN"


def family_signature(sig: str) -> str:
    return re.sub(r"\|TM[^|]*", "|TM*", str(sig or ""))


def top_counter(counter: Counter[str], n: int = 80) -> list[dict[str, Any]]:
    return [
        {"key": key, "count": int(count)}
        for key, count in sorted(counter.items(), key=lambda item: (-int(item[1]), item[0]))[:n]
    ]


def stats(values: Iterable[float]) -> dict[str, Any]:
    vals = [float(v) for v in values]
    if not vals:
        return {"count": 0, "min": None, "median": None, "max": None}
    return {
        "count": len(vals),
        "min": min(vals),
        "median": statistics.median(vals),
        "max": max(vals),
    }


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def trace_fingerprint(trace: dict[str, Any]) -> str:
    core = {
        "roomId": trace.get("roomId"),
        "id": trace.get("id"),
        "atEpoch": trace.get("atEpoch"),
        "slot": trace.get("slot"),
        "type": trace.get("type"),
        "activeAttack": trace.get("activeAttack"),
        "cycleDurationMs": trace.get("cycleDurationMs"),
        "candidateFirstLeadMs": trace.get("candidateFirstLeadMs"),
        "candidateLastLeadMs": trace.get("candidateLastLeadMs"),
        "candidateStateIndexes": trace.get("candidateStateIndexes"),
        "targetStart7E": trace.get("targetStart7E"),
        "targetAtActive7E": trace.get("targetAtActive7E"),
        "sideStart": trace.get("sideStart"),
        "sideAtActive": trace.get("sideAtActive"),
        "retargets": trace.get("retargets"),
        "states": trace.get("states"),
    }
    raw = json.dumps(core, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def feature_chain(trace: dict[str, Any]) -> tuple[list[str], list[str]]:
    states = trace.get("states")
    exact_all = [
        str(row.get("signature"))
        for row in states
        if isinstance(row, dict) and row.get("signature")
    ] if isinstance(states, list) else []
    indexes = trace.get("candidateStateIndexes") or []
    start = None
    for idx in indexes if isinstance(indexes, list) else []:
        try:
            idx_i = int(idx)
        except (TypeError, ValueError):
            continue
        if 0 <= idx_i < len(exact_all):
            start = idx_i if start is None else min(start, idx_i)
    if start is None:
        try:
            start = exact_all.index(CANDIDATE_SIG)
        except ValueError:
            return [], []
    exact = exact_all[start:]
    family: list[str] = []
    for sig in exact:
        fam = family_signature(sig)
        if not family or family[-1] != fam:
            family.append(fam)
    return exact, family


def add_chain_features(bucket: dict[str, Counter[str]], exact: list[str], family: list[str]) -> None:
    if exact:
        bucket["exact_final"][exact[-1]] += 1
        if len(exact) >= 2:
            bucket["exact_tail2"][" -> ".join(exact[-2:])] += 1
        if len(exact) >= 3:
            bucket["exact_tail3"][" -> ".join(exact[-3:])] += 1
        for pattern in {f"{exact[i-1]} -> {exact[i]}" for i in range(1, len(exact))}:
            bucket["exact_pair"][pattern] += 1
        for pattern in {f"{exact[i-2]} -> {exact[i-1]} -> {exact[i]}" for i in range(2, len(exact))}:
            bucket["exact_triple"][pattern] += 1
    if family:
        bucket["tm_final"][family[-1]] += 1
        if len(family) >= 2:
            bucket["tm_tail2"][" -> ".join(family[-2:])] += 1
        if len(family) >= 3:
            bucket["tm_tail3"][" -> ".join(family[-3:])] += 1
        for pattern in {f"{family[i-1]} -> {family[i]}" for i in range(1, len(family))}:
            bucket["tm_pair"][pattern] += 1
        for pattern in {f"{family[i-2]} -> {family[i-1]} -> {family[i]}" for i in range(2, len(family))}:
            bucket["tm_triple"][pattern] += 1


class Dataset:
    def __init__(self) -> None:
        self.inputs: list[dict[str, Any]] = []
        self.traces: list[dict[str, Any]] = []
        self._trace_seen: set[str] = set()
        self.t23_traces: list[dict[str, Any]] = []
        self._t23_seen: set[str] = set()
        self.type_samples: Counter[str] = Counter()
        self.attack_frequency: Counter[str] = Counter()
        self.target_samples: Counter[str] = Counter()
        self.scene_sets: Counter[str] = Counter()
        self.rare_edges: Counter[str] = Counter()
        self.player_hist = [0, 0, 0, 0]
        self.counts: Counter[str] = Counter()
        self.room_ids: set[str] = set()
        self.identity_shas: set[str] = set()
        self.safety_violations: list[str] = []
        self.notes: list[str] = []

    def add_trace(self, trace: dict[str, Any], source: str, run_id: Any = None, fleet_id: Any = None) -> None:
        row = dict(trace)
        if run_id is not None:
            row.setdefault("_runId", run_id)
        if fleet_id is not None:
            row.setdefault("_fleetInstanceId", fleet_id)
        row.setdefault("_source", source)
        fp = trace_fingerprint(row)
        if fp in self._trace_seen:
            return
        self._trace_seen.add(fp)
        self.traces.append(row)
        if row.get("roomId"):
            self.room_ids.add(str(row.get("roomId")))

    def add_t23_trace(self, trace: dict[str, Any], source: str, run_id: Any = None) -> None:
        row = dict(trace)
        row.setdefault("_source", source)
        if run_id is not None:
            row.setdefault("_runId", run_id)
        fp = trace_fingerprint(row)
        if fp in self._t23_seen:
            return
        self._t23_seen.add(fp)
        self.t23_traces.append(row)

    def check_safety(self, payload: dict[str, Any], source: str) -> None:
        safety = payload.get("safety")
        if not isinstance(safety, dict):
            return
        if safety.get("readOnly") is not True:
            self.safety_violations.append(f"{source}: readOnly != true")
        if safe_int(safety.get("ramWrites"), -1) != 0:
            self.safety_violations.append(f"{source}: ramWrites != 0")
        if safety.get("inputInjection") not in (False, None):
            self.safety_violations.append(f"{source}: inputInjection != false")
