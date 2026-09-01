from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import Dataset, FLEET_SCHEMA, RECORDER_SCHEMA, load_json, safe_int


def discover_json(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for raw in paths:
        p = Path(raw).expanduser().resolve()
        candidates = [p] if p.is_file() else sorted(p.rglob("*.json")) if p.is_dir() else []
        for candidate in candidates:
            if candidate.name.lower().endswith(".checkpoint.json"):
                continue
            key = str(candidate).lower()
            if key in seen:
                continue
            seen.add(key)
            found.append(candidate)
    return found


def payload_kind(payload: dict[str, Any]) -> str:
    if payload.get("schema") == FLEET_SCHEMA:
        return "fleet"
    if payload.get("schema") == RECORDER_SCHEMA and isinstance(payload.get("t18CandidateEvidence"), list):
        return "merged"
    if payload.get("schema") == RECORDER_SCHEMA and isinstance(payload.get("t18"), dict):
        return "room"
    return "unknown"


def map_from_top(rows: Any) -> Counter[str]:
    c: Counter[str] = Counter()
    if not isinstance(rows, list):
        return c
    for row in rows:
        if isinstance(row, dict) and row.get("key") is not None:
            c[str(row["key"])] += safe_int(row.get("count"))
    return c


def merge_int_map(counter: Counter[str], mapping: Any) -> None:
    if isinstance(mapping, dict):
        for key, value in mapping.items():
            counter[str(key)] += safe_int(value)


def choose_primary_payloads(files: list[Path]) -> tuple[list[tuple[Path, dict[str, Any], str]], list[str]]:
    loaded: list[tuple[Path, dict[str, Any], str]] = []
    warnings: list[str] = []
    for path in files:
        payload = load_json(path)
        if payload is None:
            continue
        kind = payload_kind(payload)
        if kind != "unknown":
            loaded.append((path, payload, kind))

    merged_by_run: dict[str, tuple[Path, dict[str, Any], str]] = {}
    rooms_by_run: dict[str, list[tuple[Path, dict[str, Any], str]]] = defaultdict(list)
    fleets: list[tuple[Path, dict[str, Any], str]] = []
    for item in loaded:
        path, payload, kind = item
        run_id = str(payload.get("runId") or "")
        if kind == "merged" and run_id:
            old = merged_by_run.get(run_id)
            if old is None or path.stat().st_mtime >= old[0].stat().st_mtime:
                merged_by_run[run_id] = item
        elif kind == "room" and run_id:
            rooms_by_run[run_id].append(item)
        elif kind == "fleet":
            fleets.append(item)

    selected: list[tuple[Path, dict[str, Any], str]] = list(merged_by_run.values())
    for run_id, rooms in rooms_by_run.items():
        if run_id not in merged_by_run:
            selected.extend(rooms)

    for fleet_item in fleets:
        _, fleet_payload, _ = fleet_item
        child_ids = {
            str(row.get("runId"))
            for row in (fleet_payload.get("childRuns") or [])
            if isinstance(row, dict) and row.get("runId")
        }
        if child_ids and child_ids.issubset(set(merged_by_run)):
            continue
        if child_ids:
            # Fleet totals/evidence already contain every child. If Fleet must be used because
            # one or more child merged files are absent, do not also aggregate the available
            # child merged/room files or counts and T18 evidence would be doubled.
            selected = [
                item for item in selected
                if str(item[1].get("runId") or "") not in child_ids
            ]
        selected.append(fleet_item)
        missing = sorted(child_ids - set(merged_by_run))
        if missing:
            warnings.append("Fleet 总合并文件引用的部分子合并文件不在输入中，已使用 Fleet 内嵌证据补足：" + ", ".join(missing))

    if not selected and loaded:
        selected = loaded
    selected.sort(key=lambda row: str(row[0]).lower())
    return selected, warnings


def ingest_payload(dataset: Dataset, path: Path, payload: dict[str, Any], kind: str) -> None:
    source = str(path)
    run_id = payload.get("runId")
    dataset.inputs.append({"path": source, "kind": kind, "runId": run_id, "status": payload.get("status")})
    dataset.check_safety(payload, source)

    if kind == "room":
        identity = payload.get("identity") or {}
        if isinstance(identity, dict) and identity.get("sha256"):
            dataset.identity_shas.add(str(identity["sha256"]))
        if payload.get("roomId"):
            dataset.room_ids.add(str(payload["roomId"]))
        diag = payload.get("diagnostics") or {}
        if isinstance(diag, dict):
            dataset.counts["enemySamples"] += safe_int(diag.get("enemySamples"))
            dataset.counts["activeEdges"] += safe_int(diag.get("activeEdges"))
            d18, d23 = diag.get("t18") or {}, diag.get("t23") or {}
            if isinstance(d18, dict):
                dataset.counts["t18Samples"] += safe_int(d18.get("samples"))
                dataset.counts["t18Cycles"] += safe_int(d18.get("resolvedCycles"))
                dataset.counts["t18CandidateCycles"] += safe_int(d18.get("candidateCycles"))
                dataset.counts["t18CandidateSamples"] += safe_int(d18.get("candidateSamples"))
            if isinstance(d23, dict):
                dataset.counts["t23Samples"] += safe_int(d23.get("samples"))
                dataset.counts["t23Cycles"] += safe_int(d23.get("resolvedCycles"))
            merge_int_map(dataset.type_samples, diag.get("typeSamples"))
            merge_int_map(dataset.attack_frequency, diag.get("activeAttackFrequency"))
            merge_int_map(dataset.target_samples, diag.get("targetSamples"))
            merge_int_map(dataset.scene_sets, diag.get("sceneTypeSets"))
            merge_int_map(dataset.rare_edges, diag.get("rareDescriptorAttack"))
            ph = diag.get("playerCountHist") or []
            if isinstance(ph, list):
                for i in range(min(4, len(ph))):
                    dataset.player_hist[i] += safe_int(ph[i])
        room_id = payload.get("roomId")
        t18 = payload.get("t18") or {}
        for tr in (t18.get("candidateTraces") or []) if isinstance(t18, dict) else []:
            if isinstance(tr, dict):
                dataset.add_trace({**tr, "roomId": room_id}, source, run_id)
        t23 = payload.get("t23") or {}
        for tr in (t23.get("traces") or []) if isinstance(t23, dict) else []:
            if isinstance(tr, dict):
                dataset.add_t23_trace({**tr, "roomId": room_id}, source, run_id)
        rare_map = diag.get("rareDescriptorAttack") if isinstance(diag, dict) else None
        if not isinstance(rare_map, dict) or not rare_map:
            for edge in payload.get("rareDescriptorAttackEdges") or []:
                if isinstance(edge, dict):
                    dataset.rare_edges[f"T{edge.get('type')}|{edge.get('preActiveSignature')}->A{edge.get('attack')}"] += 1
        return

    counts = payload.get("counts") or {}
    if isinstance(counts, dict):
        for key, value in counts.items():
            if isinstance(value, (int, float)) and key not in {"liveRooms", "completedRooms"}:
                dataset.counts[str(key)] += safe_int(value)
    coverage = payload.get("coverage") or {}
    if isinstance(coverage, dict):
        dataset.type_samples.update(map_from_top(coverage.get("enemyTypeSamplesTop")))
        dataset.attack_frequency.update(map_from_top(coverage.get("activeAttackFrequencyTop")))
        dataset.scene_sets.update(map_from_top(coverage.get("sceneTypeSetTop")))
        merge_int_map(dataset.target_samples, coverage.get("targetSamples"))
        ph = coverage.get("playerCountHist") or []
        if isinstance(ph, list):
            for i in range(min(4, len(ph))):
                dataset.player_hist[i] += safe_int(ph[i])
    for room in payload.get("rooms") or []:
        if isinstance(room, dict):
            if room.get("roomId"):
                dataset.room_ids.add(str(room["roomId"]))
            if room.get("identitySha256"):
                dataset.identity_shas.add(str(room["identitySha256"]))
    for tr in payload.get("t18CandidateEvidence") or []:
        if isinstance(tr, dict):
            dataset.add_trace(tr, source, run_id, tr.get("fleetInstanceId"))
    if kind == "merged":
        t23_summary = payload.get("t23SequenceSummary") or {}
        if isinstance(t23_summary, dict):
            dataset.counts["t23SummaryCycles"] += safe_int(t23_summary.get("totalCycles"))
    else:
        dataset.notes.append("Fleet 总合并文件只内嵌 T18 候选证据；完整 T23 / 稀有 descriptor+attack 细节需要子合并文件才能统计。")


def ingest_room_supplement(dataset: Dataset, path: Path, payload: dict[str, Any]) -> None:
    source = str(path)
    run_id = payload.get("runId")
    room_id = payload.get("roomId")
    t23 = payload.get("t23") or {}
    for tr in (t23.get("traces") or []) if isinstance(t23, dict) else []:
        if isinstance(tr, dict):
            dataset.add_t23_trace({**tr, "roomId": room_id}, source, run_id)
    diag = payload.get("diagnostics") or {}
    rare_map = diag.get("rareDescriptorAttack") if isinstance(diag, dict) else None
    if isinstance(rare_map, dict) and rare_map:
        merge_int_map(dataset.rare_edges, rare_map)
    else:
        for edge in payload.get("rareDescriptorAttackEdges") or []:
            if isinstance(edge, dict):
                dataset.rare_edges[f"T{edge.get('type')}|{edge.get('preActiveSignature')}->A{edge.get('attack')}"] += 1


def build_dataset(paths: list[str]) -> Dataset:
    files = discover_json(paths)
    selected, warnings = choose_primary_payloads(files)
    dataset = Dataset()
    dataset.notes.extend(warnings)
    selected_paths = {str(path).lower() for path, _, _ in selected}
    covered_runs = {
        str(payload.get("runId")) for _, payload, kind in selected
        if kind == "merged" and payload.get("runId")
    }
    for _, payload, kind in selected:
        if kind == "fleet":
            covered_runs.update(
                str(row.get("runId"))
                for row in (payload.get("childRuns") or [])
                if isinstance(row, dict) and row.get("runId")
            )
    for path, payload, kind in selected:
        ingest_payload(dataset, path, payload, kind)
    for path in files:
        if str(path).lower() in selected_paths:
            continue
        payload = load_json(path)
        if payload and payload_kind(payload) == "room" and str(payload.get("runId") or "") in covered_runs:
            ingest_room_supplement(dataset, path, payload)
    if not selected:
        dataset.notes.append("没有找到可识别的 WOF-052L per-room / merged / fleet merged JSON。")
    return dataset


def input_signature(paths: list[str]) -> tuple[tuple[str, int, int], ...]:
    rows: list[tuple[str, int, int]] = []
    for path in discover_json(paths):
        payload = load_json(path)
        if not payload or payload_kind(payload) == "unknown":
            continue
        try:
            st = path.stat()
        except OSError:
            continue
        rows.append((str(path), st.st_mtime_ns, st.st_size))
    return tuple(rows)
