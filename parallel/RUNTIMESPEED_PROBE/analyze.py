from __future__ import annotations

import argparse
import gzip
import json
import math
import statistics
import struct
from dataclasses import dataclass
from pathlib import Path

VERSION = "wof-runtime-speed-analyzer-v1"
RESULT_SCHEMA = "wof-runtime-speed-result-v1"
CAPTURE_SCHEMA = "wof-runtime-speed-capture-v1"
MAGIC = b"WOFSPC1\n"
RAM_SIZE = 0x10000
TIME_SIZE = 8
RECORD_SIZE = TIME_SIZE + RAM_SIZE
NOMINAL_CPS1_HZ = 8_000_000 / (512 * 262)
DEFAULT_LOCAL = Path("parallel/RUNTIMESPEED_PROBE/out/local_speed_capture.wofsp.gz")
DEFAULT_RESULT = Path("parallel/RUNTIMESPEED_PROBE/out/runtime_speed_result.json")


@dataclass
class Capture:
    path: Path
    header: dict
    payload: bytes
    count: int
    times: list[float]

    @property
    def runtime(self) -> str:
        return str(self.header.get("runtime") or "unknown")

    @property
    def span_ms(self) -> float:
        return self.times[-1] - self.times[0] if len(self.times) >= 2 else 0.0

    @property
    def achieved_hz(self) -> float:
        return (self.count - 1) / (self.span_ms / 1000.0) if self.count >= 2 and self.span_ms > 0 else 0.0

    def frame(self, index: int) -> memoryview:
        off = index * RECORD_SIZE + TIME_SIZE
        return memoryview(self.payload)[off : off + RAM_SIZE]

    def value(self, frame: memoryview, address: int, width: int) -> int:
        if width == 1:
            return frame[address]
        return (frame[address] << 8) | frame[address + 1]


def _open_binary(path: Path):
    if path.name.lower().endswith(".gz"):
        return gzip.open(path, "rb")
    return path.open("rb")


def load_capture(path: Path) -> Capture:
    with _open_binary(path) as f:
        magic = f.read(len(MAGIC))
        if magic != MAGIC:
            raise RuntimeError(f"{path}: bad capture magic")
        raw_len = f.read(4)
        if len(raw_len) != 4:
            raise RuntimeError(f"{path}: truncated capture header length")
        header_len = struct.unpack("<I", raw_len)[0]
        if header_len <= 0 or header_len > 1_000_000:
            raise RuntimeError(f"{path}: unreasonable capture header length {header_len}")
        header = json.loads(f.read(header_len).decode("utf-8"))
        payload = f.read()
    if header.get("schemaVersion") != CAPTURE_SCHEMA:
        raise RuntimeError(f"{path}: unsupported schema {header.get('schemaVersion')!r}")
    if header.get("readOnly") is not True or header.get("writesGameMemory") is not False or header.get("inputInjection") is not False:
        raise RuntimeError(f"{path}: capture does not assert read-only/no-input contract")
    ram = header.get("ram") or {}
    if ram.get("bytesPerSample") != RAM_SIZE or ram.get("normalized") is not True:
        raise RuntimeError(f"{path}: expected normalized 64 KiB CPS RAM samples")
    if len(payload) % RECORD_SIZE:
        raise RuntimeError(f"{path}: record payload size is not an exact multiple of {RECORD_SIZE}")
    count = len(payload) // RECORD_SIZE
    if count < 20:
        raise RuntimeError(f"{path}: too few records ({count})")
    times = [struct.unpack_from("<d", payload, i * RECORD_SIZE)[0] for i in range(count)]
    if not all(math.isfinite(x) for x in times):
        raise RuntimeError(f"{path}: non-finite timestamp")
    if not all(times[i] > times[i - 1] for i in range(1, len(times))):
        raise RuntimeError(f"{path}: timestamps are not strictly monotonic")
    return Capture(path=path, header=header, payload=payload, count=count, times=times)


def _coarse_indices(cap: Capture, target: int = 220) -> list[int]:
    step = max(1, (cap.count - 1) // max(2, target - 1))
    idx = list(range(0, cap.count, step))
    if idx[-1] != cap.count - 1:
        idx.append(cap.count - 1)
    return idx


def _candidate_scan(cap: Capture, width: int, keep: int = 320) -> tuple[list[dict], list[dict]]:
    idx = _coarse_indices(cap)
    frames = [cap.frame(i) for i in idx]
    times = [cap.times[i] for i in idx]
    avg_dt = (times[-1] - times[0]) / max(1, len(times) - 1)
    max_jump = max(4, min(96, int(math.ceil(avg_dt / 8.0)) + 3))
    modulus = 256 if width == 1 else 65536
    end = RAM_SIZE if width == 1 else RAM_SIZE - 1
    min_changes = max(8, int(len(frames) * 0.12))
    monotonic: list[dict] = []
    periodic: list[dict] = []

    for address in range(end):
        first = frames[0]
        prev = first[address] if width == 1 else (first[address] << 8) | first[address + 1]
        changes = pos_ok = neg_ok = pos_unit = neg_unit = 0
        for frame in frames[1:]:
            cur = frame[address] if width == 1 else (frame[address] << 8) | frame[address + 1]
            if cur != prev:
                changes += 1
                fd = (cur - prev) % modulus
                bd = (prev - cur) % modulus
                if 0 < fd <= max_jump:
                    pos_ok += 1
                    if fd == 1:
                        pos_unit += 1
                if 0 < bd <= max_jump:
                    neg_ok += 1
                    if bd == 1:
                        neg_unit += 1
            prev = cur
        if changes < min_changes:
            continue
        pos_frac = pos_ok / changes
        neg_frac = neg_ok / changes
        best_frac = max(pos_frac, neg_frac)
        if best_frac >= 0.965:
            direction = 1 if pos_frac >= neg_frac else -1
            unit_frac = (pos_unit if direction == 1 else neg_unit) / max(1, changes)
            score = best_frac * (0.65 + 0.35 * min(1.0, changes / max(1, len(frames) * 0.55))) * (0.85 + 0.15 * unit_frac)
            monotonic.append({"address": address, "width": width, "direction": direction, "coarseScore": score, "coarseChanges": changes})
        else:
            periodic.append({"address": address, "width": width, "coarseScore": changes / max(1, len(frames) - 1), "coarseChanges": changes})

    monotonic.sort(key=lambda x: (x["coarseScore"], x["coarseChanges"]), reverse=True)
    periodic.sort(key=lambda x: (x["coarseScore"], x["coarseChanges"]), reverse=True)
    return monotonic[:keep], periodic[:keep]


def _counter_metric(cap: Capture, address: int, width: int, direction: int) -> dict:
    modulus = 256 if width == 1 else 65536
    prev = cap.value(cap.frame(0), address, width)
    prev_t = cap.times[0]
    changes = accepted = unit = violations = 0
    cumulative = 0
    first_event_t = last_event_t = None
    first_cum = last_cum = None
    per_step_intervals: list[float] = []
    last_event_time = None

    for i in range(1, cap.count):
        cur = cap.value(cap.frame(i), address, width)
        t = cap.times[i]
        if cur != prev:
            changes += 1
            delta = ((cur - prev) if direction == 1 else (prev - cur)) % modulus
            dt = max(0.0, t - prev_t)
            max_allowed = max(3, min(96, int(math.ceil(dt / 7.0)) + 3))
            if 0 < delta <= max_allowed:
                accepted += 1
                cumulative += delta
                if delta == 1:
                    unit += 1
                if first_event_t is None:
                    first_event_t = t
                    first_cum = cumulative
                if last_event_time is not None:
                    per_step_intervals.append((t - last_event_time) / max(1, delta))
                last_event_time = t
                last_event_t = t
                last_cum = cumulative
            else:
                violations += 1
        prev = cur
        prev_t = t

    monotonic_fraction = accepted / changes if changes else 0.0
    unit_fraction = unit / accepted if accepted else 0.0
    coverage = rate = 0.0
    if first_event_t is not None and last_event_t is not None and last_event_t > first_event_t and first_cum is not None and last_cum is not None:
        active_span = last_event_t - first_event_t
        coverage = active_span / max(1e-9, cap.span_ms)
        rate = (last_cum - first_cum) / (active_span / 1000.0)
    if per_step_intervals:
        mean_i = statistics.mean(per_step_intervals)
        cv = statistics.pstdev(per_step_intervals) / mean_i if len(per_step_intervals) > 1 and mean_i > 0 else 0.0
        median_i = statistics.median(per_step_intervals)
    else:
        cv = 99.0
        median_i = None
    regularity = 1.0 / (1.0 + cv)
    density = min(1.0, accepted / 40.0)
    quality = 0.45 * monotonic_fraction + 0.25 * min(1.0, coverage) + 0.20 * regularity + 0.10 * density
    stable = bool(changes >= 20 and accepted >= 20 and monotonic_fraction >= 0.985 and coverage >= 0.65 and rate >= 0.2 and quality >= 0.72)
    return {
        "address": address,
        "cpsAddress": f"0x{0xFF0000 + address:06X}",
        "width": width,
        "direction": "+" if direction == 1 else "-",
        "changes": changes,
        "acceptedChanges": accepted,
        "violations": violations,
        "monotonicFraction": round(monotonic_fraction, 6),
        "unitStepFraction": round(unit_fraction, 6),
        "coverage": round(coverage, 6),
        "rateHz": round(rate, 9),
        "medianStepIntervalMs": round(median_i, 6) if median_i is not None else None,
        "stepIntervalCv": round(cv, 6) if math.isfinite(cv) else None,
        "qualityScore": round(quality, 6),
        "stable": stable,
    }


def _periodic_metric(cap: Capture, address: int, width: int) -> dict:
    prev = cap.value(cap.frame(0), address, width)
    event_times: list[float] = []
    distinct = {prev}
    overflow_domain = False
    for i in range(1, cap.count):
        cur = cap.value(cap.frame(i), address, width)
        if len(distinct) < 65:
            distinct.add(cur)
        else:
            overflow_domain = True
        if cur != prev:
            event_times.append(cap.times[i])
        prev = cur
    changes = len(event_times)
    if changes >= 2:
        active_span = event_times[-1] - event_times[0]
        rate = (changes - 1) / (active_span / 1000.0) if active_span > 0 else 0.0
        coverage = active_span / max(1e-9, cap.span_ms)
        intervals = [event_times[i] - event_times[i - 1] for i in range(1, len(event_times))]
        mean_i = statistics.mean(intervals) if intervals else 0.0
        cv = statistics.pstdev(intervals) / mean_i if len(intervals) > 1 and mean_i > 0 else 0.0
        median_i = statistics.median(intervals) if intervals else None
    else:
        rate = coverage = 0.0
        cv = 99.0
        median_i = None
    domain_size = 65 if overflow_domain else len(distinct)
    domain_score = 1.0 if domain_size <= 16 else (0.8 if domain_size <= 32 else 0.55)
    regularity = 1.0 / (1.0 + cv)
    density = min(1.0, changes / 50.0)
    quality = 0.35 * min(1.0, coverage) + 0.40 * regularity + 0.15 * density + 0.10 * domain_score
    stable = bool(changes >= 30 and coverage >= 0.65 and rate >= 0.2 and cv <= 0.55 and quality >= 0.62)
    return {
        "address": address,
        "cpsAddress": f"0x{0xFF0000 + address:06X}",
        "width": width,
        "changes": changes,
        "coverage": round(coverage, 6),
        "changeRateHz": round(rate, 9),
        "medianChangeIntervalMs": round(median_i, 6) if median_i is not None else None,
        "changeIntervalCv": round(cv, 6) if math.isfinite(cv) else None,
        "domainSizeCapped65": domain_size,
        "qualityScore": round(quality, 6),
        "stable": stable,
    }


def analyze_capture(cap: Capture) -> dict:
    mono_coarse: list[dict] = []
    periodic_coarse: list[dict] = []
    for width in (1, 2):
        m, p = _candidate_scan(cap, width)
        mono_coarse.extend(m)
        periodic_coarse.extend(p)
    counters = []
    for c in mono_coarse:
        metric = _counter_metric(cap, c["address"], c["width"], c["direction"])
        metric["coarseScore"] = round(c["coarseScore"], 6)
        if metric["stable"]:
            counters.append(metric)
    counters.sort(key=lambda x: (x["qualityScore"], x["coverage"], x["changes"]), reverse=True)

    periodic = []
    seen = set()
    for c in periodic_coarse[:480]:
        key = (c["address"], c["width"])
        if key in seen:
            continue
        seen.add(key)
        metric = _periodic_metric(cap, c["address"], c["width"])
        metric["coarseScore"] = round(c["coarseScore"], 6)
        if metric["stable"]:
            periodic.append(metric)
    periodic.sort(key=lambda x: (x["qualityScore"], x["coverage"], x["changes"]), reverse=True)

    return {
        "runtime": cap.runtime,
        "path": cap.path.as_posix(),
        "sampleCount": cap.count,
        "spanMs": round(cap.span_ms, 6),
        "achievedHz": round(cap.achieved_hz, 6),
        "headerAchievedHz": cap.header.get("achievedHz"),
        "counterCandidates": counters[:160],
        "periodicCandidates": periodic[:160],
    }


def _weighted_median(values: list[tuple[float, float]]) -> float:
    if not values:
        raise ValueError("weighted median of empty input")
    ordered = sorted(values, key=lambda x: x[0])
    total = sum(max(0.0, w) for _, w in ordered)
    if total <= 0:
        return statistics.median(v for v, _ in ordered)
    acc = 0.0
    for v, w in ordered:
        acc += max(0.0, w)
        if acc >= total / 2:
            return v
    return ordered[-1][0]


def _pair_counters(local: dict, browser: dict) -> tuple[str, list[dict]]:
    lmap = {(x["address"], x["width"], x["direction"]): x for x in local["counterCandidates"]}
    bmap = {(x["address"], x["width"], x["direction"]): x for x in browser["counterCandidates"]}
    pairs = []
    for key in sorted(lmap.keys() & bmap.keys()):
        l, b = lmap[key], bmap[key]
        if b["rateHz"] <= 0:
            continue
        ratio = l["rateHz"] / b["rateHz"]
        if not (0.4 <= ratio <= 2.5):
            continue
        weight = min(l["qualityScore"], b["qualityScore"]) * (0.75 + 0.25 * min(1.0, min(l["rateHz"], b["rateHz"]) / 5.0))
        pairs.append({"kind": "monotonic-counter", "key": key, "local": l, "browser": b, "ratio": ratio, "weight": weight})
    if pairs:
        return "monotonic-counter", pairs

    lmap2 = {(x["address"], x["width"]): x for x in local["periodicCandidates"]}
    bmap2 = {(x["address"], x["width"]): x for x in browser["periodicCandidates"]}
    for key in sorted(lmap2.keys() & bmap2.keys()):
        l, b = lmap2[key], bmap2[key]
        if b["changeRateHz"] <= 0:
            continue
        ratio = l["changeRateHz"] / b["changeRateHz"]
        if not (0.4 <= ratio <= 2.5):
            continue
        weight = min(l["qualityScore"], b["qualityScore"]) * 0.75
        pairs.append({"kind": "periodic-heartbeat", "key": key, "local": l, "browser": b, "ratio": ratio, "weight": weight})
    return "periodic-heartbeat", pairs


def _near_nominal(rate: float, tolerance: float = 0.025) -> bool:
    return rate > 0 and abs(rate / NOMINAL_CPS1_HZ - 1.0) <= tolerance


def build_result(local: dict, browser: dict) -> dict:
    mode, pairs = _pair_counters(local, browser)
    if not pairs:
        return {
            "schemaVersion": RESULT_SCHEMA,
            "analyzerVersion": VERSION,
            "verdict": "INCONCLUSIVE_NO_COMMON_HEARTBEAT",
            "confidence": "LOW",
            "measurementMode": "none",
            "winkawaks": {"sampleCount": local["sampleCount"], "captureHz": local["achievedHz"], "spanMs": local["spanMs"]},
            "browser": {"sampleCount": browser["sampleCount"], "captureHz": browser["achievedHz"], "spanMs": browser["spanMs"]},
            "speedRatio": None,
            "reason": "No stable same-address monotonic U8/U16 counter and no stable same-address periodic fallback heartbeat were found in the paired full-RAM captures.",
            "readOnly": True,
            "writesGameMemory": False,
            "inputInjection": False,
        }

    ratio0 = _weighted_median([(p["ratio"], p["weight"]) for p in pairs])
    cluster = [p for p in pairs if abs(p["ratio"] / ratio0 - 1.0) <= 0.02]
    if not cluster:
        cluster = pairs
    ratio = _weighted_median([(p["ratio"], p["weight"]) for p in cluster])
    deviations = [abs(p["ratio"] / ratio - 1.0) for p in cluster]
    spread = statistics.median(deviations) if deviations else 1.0

    def rate_of(p: dict, side: str) -> float:
        x = p[side]
        return x["rateHz"] if p["kind"] == "monotonic-counter" else x["changeRateHz"]

    def primary_score(p: dict) -> float:
        lr, br = rate_of(p, "local"), rate_of(p, "browser")
        nominal_bonus = 0.35 if (_near_nominal(lr, 0.08) or _near_nominal(br, 0.08)) else 0.0
        closeness = max(0.0, 1.0 - abs(p["ratio"] / ratio - 1.0) / 0.02)
        return p["weight"] * (1.0 + nominal_bonus) * (0.8 + 0.2 * closeness)

    primary = max(cluster, key=primary_score)
    local_rate = rate_of(primary, "local")
    browser_rate = rate_of(primary, "browser")
    primary_ratio = local_rate / browser_rate if browser_rate > 0 else ratio

    sample_quality = local["achievedHz"] >= 80 and browser["achievedHz"] >= 80 and local["spanMs"] >= 12000 and browser["spanMs"] >= 12000
    if mode == "monotonic-counter" and len(cluster) >= 2 and spread <= 0.0075 and sample_quality:
        confidence = "HIGH"
    elif len(cluster) >= 1 and spread <= 0.02 and local["spanMs"] >= 10000 and browser["spanMs"] >= 10000:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    local_nominal = _near_nominal(local_rate)
    browser_nominal = _near_nominal(browser_rate)
    ratio_delta = abs(ratio - 1.0)
    plan_direction_conflict = False
    if confidence == "LOW":
        verdict = "INCONCLUSIVE_MEASUREMENT_QUALITY"
    elif ratio_delta <= 0.015:
        verdict = "SAME_SIMULATION_SPEED_DIFFERENT_FEEL"
    elif 0.015 < ratio_delta < 0.03:
        verdict = "INCONCLUSIVE_1_5_TO_3_PERCENT"
    elif ratio >= 1.03:
        if browser_nominal and not local_nominal:
            verdict = "WINKAWAKS_FASTER"
        elif local_nominal and not browser_nominal:
            verdict = "BROWSER_SLOWER"
        else:
            verdict = "WINKAWAKS_FASTER_THAN_BROWSER_NOMINAL_ATTRIBUTION_UNPROVEN"
    else:
        plan_direction_conflict = True
        if browser_nominal and not local_nominal:
            verdict = "WINKAWAKS_SLOWER"
        elif local_nominal and not browser_nominal:
            verdict = "BROWSER_FASTER"
        else:
            verdict = "BROWSER_FASTER_THAN_WINKAWAKS_NOMINAL_ATTRIBUTION_UNPROVEN"

    evidence = []
    for p in sorted(cluster, key=primary_score, reverse=True)[:8]:
        l, b = p["local"], p["browser"]
        evidence.append({
            "kind": p["kind"],
            "cpsAddress": l["cpsAddress"],
            "width": l["width"],
            "direction": l.get("direction"),
            "winkawaksRateHz": round(rate_of(p, "local"), 6),
            "browserRateHz": round(rate_of(p, "browser"), 6),
            "speedRatio": round(p["ratio"], 9),
            "winkawaksQuality": l["qualityScore"],
            "browserQuality": b["qualityScore"],
        })

    return {
        "schemaVersion": RESULT_SCHEMA,
        "analyzerVersion": VERSION,
        "verdict": verdict,
        "confidence": confidence,
        "measurementMode": mode,
        "primaryHeartbeat": {
            "cpsAddress": primary["local"]["cpsAddress"],
            "width": primary["local"]["width"],
            "direction": primary["local"].get("direction"),
            "winkawaksRateHz": round(local_rate, 6),
            "browserRateHz": round(browser_rate, 6),
            "primaryPairRatio": round(primary_ratio, 9),
        },
        "speedRatio": round(ratio, 9),
        "ratioDeltaPct": round((ratio - 1.0) * 100.0, 6),
        "ratioConsensus": {
            "commonCandidateCount": len(pairs),
            "agreeingCandidateCount": len(cluster),
            "medianRelativeSpreadPct": round(spread * 100.0, 6),
        },
        "winkawaks": {
            "sampleCount": local["sampleCount"],
            "captureHz": local["achievedHz"],
            "spanMs": local["spanMs"],
            "primaryRateHz": round(local_rate, 6),
            "nearNominal59_6374": local_nominal,
        },
        "browser": {
            "sampleCount": browser["sampleCount"],
            "captureHz": browser["achievedHz"],
            "spanMs": browser["spanMs"],
            "primaryRateHz": round(browser_rate, 6),
            "nearNominal59_6374": browser_nominal,
        },
        "nominalCps1Hz": round(NOMINAL_CPS1_HZ, 6),
        "nominalReferenceApplicable": bool(local_nominal or browser_nominal),
        "planDirectionConflict": plan_direction_conflict,
        "evidence": evidence,
        "readOnly": True,
        "writesGameMemory": False,
        "inputInjection": False,
    }


def _find_browser_capture(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_file():
            raise FileNotFoundError(p)
        return p
    candidates: list[Path] = []
    roots = [Path.home() / "Downloads", Path("parallel/RUNTIMESPEED_PROBE/out"), Path.cwd()]
    patterns = ["wof_browser_speed_capture*.wofsp.gz", "wof_browser_speed_capture*.wofsp", "browser_speed_capture*.wofsp.gz", "browser_speed_capture*.wofsp"]
    for root in roots:
        if not root.exists():
            continue
        for pattern in patterns:
            candidates.extend(root.glob(pattern))
    if not candidates:
        raise FileNotFoundError("Browser capture not found in Downloads or probe out/")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare paired WOF WinKawaks/Browser full-RAM speed captures")
    parser.add_argument("--local", default=DEFAULT_LOCAL.as_posix())
    parser.add_argument("--browser", default=None)
    parser.add_argument("--out", default=DEFAULT_RESULT.as_posix())
    args = parser.parse_args()
    try:
        local_cap = load_capture(Path(args.local))
        if local_cap.runtime != "winkawaks":
            raise RuntimeError(f"Local capture runtime is {local_cap.runtime!r}, expected 'winkawaks'")
        local_analysis = analyze_capture(local_cap)
        del local_cap

        browser_path = _find_browser_capture(args.browser)
        browser_cap = load_capture(browser_path)
        if browser_cap.runtime != "browser":
            raise RuntimeError(f"Browser capture runtime is {browser_cap.runtime!r}, expected 'browser'")
        browser_analysis = analyze_capture(browser_cap)
        del browser_cap

        result = build_result(local_analysis, browser_analysis)
        result["captures"] = {"winkawaks": Path(args.local).as_posix(), "browser": browser_path.as_posix()}
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not str(result["verdict"]).startswith("INCONCLUSIVE") else 20
    except Exception as exc:
        result = {
            "schemaVersion": RESULT_SCHEMA,
            "analyzerVersion": VERSION,
            "verdict": "INCONCLUSIVE_TOOL_ERROR",
            "confidence": "LOW",
            "error": f"{type(exc).__name__}: {exc}",
            "readOnly": True,
            "writesGameMemory": False,
            "inputInjection": False,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 30


if __name__ == "__main__":
    raise SystemExit(main())