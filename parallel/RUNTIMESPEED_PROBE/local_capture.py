from __future__ import annotations

import argparse
import gzip
import json
import os
import struct
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

VERSION = "wof-runtime-speed-local-capture-v1"
CAPTURE_SCHEMA = "wof-runtime-speed-capture-v1"
MAGIC = b"WOFSPC1\n"
RAM_SIZE = 0x10000
DEFAULT_SECONDS = 15.0
DEFAULT_HZ = 120.0
MAX_SECONDS = 30.0
MAX_HZ = 160.0
DEFAULT_OUT = Path("parallel/RUNTIMESPEED_PROBE/out/local_speed_capture.wofsp.gz")
RECORD = struct.Struct("<d")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bridge_root(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    env = os.environ.get("WOF_WINKAWAKS_BRIDGE")
    if env:
        candidates.append(Path(env))
    here = Path(__file__).resolve()
    if len(here.parents) >= 4:
        candidates.append(here.parents[3] / "wof-winkawaks-bridge")
    candidates.extend([Path.cwd() / "wof-winkawaks-bridge", Path.cwd().parent / "wof-winkawaks-bridge"])
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except Exception:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if (resolved / "bridge" / "session_discovery.py").is_file() and (resolved / "bridge" / "memory.py").is_file():
            return resolved
    searched = ", ".join(str(x) for x in candidates)
    raise RuntimeError("Cannot locate wof-winkawaks-bridge. Keep it beside wof-ai-private or pass --bridge-root. " + f"Searched: {searched}")


def _normalize_host_block(raw: bytes, xor_mask: int) -> bytes:
    if len(raw) != RAM_SIZE:
        raise RuntimeError(f"RAM block length {len(raw)} != {RAM_SIZE}")
    if xor_mask == 0:
        return raw
    src = raw
    out = bytearray(RAM_SIZE)
    if xor_mask == 1:
        out[0::2] = src[1::2]
        out[1::2] = src[0::2]
    elif xor_mask == 2:
        out[0::4] = src[2::4]
        out[1::4] = src[3::4]
        out[2::4] = src[0::4]
        out[3::4] = src[1::4]
    elif xor_mask == 3:
        out[0::4] = src[3::4]
        out[1::4] = src[2::4]
        out[2::4] = src[1::4]
        out[3::4] = src[0::4]
    else:
        raise RuntimeError(f"Unsupported mapping XOR mask: {xor_mask}")
    return bytes(out)


def _write_capture(temp_path: Path, out_path: Path, header: dict, sample_count: int, xor_mask: int) -> None:
    header_bytes = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with temp_path.open("rb") as src, gzip.open(out_path, "wb", compresslevel=6) as dst:
        dst.write(MAGIC)
        dst.write(struct.pack("<I", len(header_bytes)))
        dst.write(header_bytes)
        for _ in range(sample_count):
            ts = src.read(RECORD.size)
            raw = src.read(RAM_SIZE)
            if len(ts) != RECORD.size or len(raw) != RAM_SIZE:
                raise RuntimeError("Temporary capture truncated during finalization")
            dst.write(ts)
            dst.write(_normalize_host_block(raw, xor_mask))
        if src.read(1):
            raise RuntimeError("Temporary capture contains trailing bytes")


def capture(seconds: float, hz: float, out_path: Path, bridge_root: Path) -> dict:
    if not (0 < seconds <= MAX_SECONDS):
        raise ValueError(f"seconds must be >0 and <= {MAX_SECONDS}")
    if not (0 < hz <= MAX_HZ):
        raise ValueError(f"hz must be >0 and <= {MAX_HZ}")

    sys.path.insert(0, str(bridge_root))
    from bridge.cps_ram import CPS_RAM_START, MAPPING_XOR_MASK
    from bridge.memory import ProcessReader
    from bridge.process import find_winkawaks
    from bridge.session_discovery import discover_fresh_immutable

    proc = find_winkawaks()
    if proc is None:
        raise RuntimeError("WinKawaks process not found")

    requested_started_utc = _utc_now()
    sample_times: list[float] = []
    read_errors = 0
    temp_path: Path | None = None
    discovery: dict | None = None
    selected: dict | None = None

    try:
        with ProcessReader(proc.pid) as reader:
            discovery = discover_fresh_immutable(reader)
            selected = discovery.get("selected")
            if not (discovery.get("candidateUnique") and selected):
                raise RuntimeError("Fresh immutable CPS RAM discovery is not uniquely qualified")

            ram_base = int(str(selected["ramBase"]), 16)
            mapping = str(selected["mapping"])
            if mapping not in MAPPING_XOR_MASK:
                raise RuntimeError(f"Unsupported discovered mapping: {mapping}")
            xor_mask = int(MAPPING_XOR_MASK[mapping])

            fd, tmp_name = tempfile.mkstemp(prefix="wof_speed_local_", suffix=".raw")
            os.close(fd)
            temp_path = Path(tmp_name)
            interval = 1.0 / hz
            start = time.perf_counter()
            sequence = 0
            with temp_path.open("wb", buffering=1024 * 1024) as tmp:
                while True:
                    now = time.perf_counter()
                    if sequence > 0 and now - start >= seconds:
                        break
                    try:
                        raw = reader.read(ram_base, RAM_SIZE)
                    except Exception:
                        read_errors += 1
                        raise
                    if len(raw) != RAM_SIZE:
                        read_errors += 1
                        raise RuntimeError(f"ReadProcessMemory returned {len(raw)} bytes, expected {RAM_SIZE}")
                    captured = time.perf_counter()
                    elapsed_ms = (captured - start) * 1000.0
                    tmp.write(RECORD.pack(elapsed_ms))
                    tmp.write(raw)
                    sample_times.append(elapsed_ms)
                    sequence += 1
                    deadline = start + sequence * interval
                    sleep_for = deadline - time.perf_counter()
                    if sleep_for > 0:
                        time.sleep(sleep_for)

        if len(sample_times) < 2:
            raise RuntimeError("Too few samples captured")
        duration_ms = sample_times[-1] - sample_times[0]
        achieved_hz = (len(sample_times) - 1) / (duration_ms / 1000.0) if duration_ms > 0 else 0.0
        intervals = [sample_times[i] - sample_times[i - 1] for i in range(1, len(sample_times))]
        intervals_sorted = sorted(intervals)
        p95 = intervals_sorted[min(len(intervals_sorted) - 1, int(0.95 * (len(intervals_sorted) - 1)))] if intervals_sorted else None

        assert selected is not None and discovery is not None and temp_path is not None
        mapping = str(selected["mapping"])
        xor_mask = int(MAPPING_XOR_MASK[mapping])
        header = {
            "schemaVersion": CAPTURE_SCHEMA,
            "captureToolVersion": VERSION,
            "runtime": "winkawaks",
            "readOnly": True,
            "writesGameMemory": False,
            "inputInjection": False,
            "timestampClock": "time.perf_counter",
            "timestampUnit": "milliseconds-from-capture-start",
            "requestedSeconds": seconds,
            "targetHz": hz,
            "sampleCount": len(sample_times),
            "measuredSpanMs": round(duration_ms, 6),
            "achievedHz": round(achieved_hz, 6),
            "captureStartedAtUtc": requested_started_utc,
            "captureFinishedAtUtc": _utc_now(),
            "ram": {
                "logicalStart": f"0x{CPS_RAM_START:06X}",
                "bytesPerSample": RAM_SIZE,
                "normalized": True,
                "normalization": f"hostOffset=logicalOffset^{xor_mask}",
                "sourceRamBase": str(selected["ramBase"]),
                "sourceMapping": mapping,
            },
            "session": {
                "pid": int(proc.pid),
                "exeName": proc.exe_name,
                "freshDiscoveryMethod": discovery.get("method"),
                "candidateUnique": bool(discovery.get("candidateUnique")),
                "cachedRamBaseUsedAsDiscoveryInput": False,
            },
            "captureQuality": {
                "readErrors": read_errors,
                "monotonicTimestamps": all(sample_times[i] > sample_times[i - 1] for i in range(1, len(sample_times))),
                "intervalP95Ms": round(p95, 6) if p95 is not None else None,
            },
        }
        _write_capture(temp_path, out_path, header, len(sample_times), xor_mask)
        return {
            "ok": True,
            "runtime": "winkawaks",
            "capturePath": out_path.as_posix(),
            "sampleCount": len(sample_times),
            "measuredSpanMs": round(duration_ms, 3),
            "achievedHz": round(achieved_hz, 3),
            "mapping": mapping,
            "readOnly": True,
            "writesGameMemory": False,
            "inputInjection": False,
        }
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only 15 s full-CPS-RAM WinKawaks speed capture")
    parser.add_argument("--seconds", type=float, default=DEFAULT_SECONDS)
    parser.add_argument("--hz", type=float, default=DEFAULT_HZ)
    parser.add_argument("--out", default=DEFAULT_OUT.as_posix())
    parser.add_argument("--bridge-root", default=None)
    args = parser.parse_args()
    try:
        root = _bridge_root(args.bridge_root)
        result = capture(args.seconds, args.hz, Path(args.out), root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        result = {
            "ok": False,
            "runtime": "winkawaks",
            "error": f"{type(exc).__name__}: {exc}",
            "readOnly": True,
            "writesGameMemory": False,
            "inputInjection": False,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 30


if __name__ == "__main__":
    raise SystemExit(main())