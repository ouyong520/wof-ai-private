from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

STATUS_RING_SCHEMA = "wof-alpha-p25-runtime-status-ring-v1"
MAX_SNAPSHOTS = 512


def _atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(data)
        os.replace(tmp, path)
    finally:
        try:
            Path(tmp).unlink(missing_ok=True)
        except OSError:
            pass


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--candidate-root", type=Path, required=True)
    p.add_argument("--status-ring", type=Path, required=True)
    args, rest = p.parse_known_args()
    return args, rest


def main() -> int:
    args, candidate_args = parse_args()
    root = args.candidate_root.expanduser().resolve()
    entry = root / "parallel" / "PYLAUNCH" / "render_authority_measurement_entry.py"
    pylaunch = root / "parallel" / "PYLAUNCH"
    if not entry.is_file():
        raise RuntimeError(f"exact candidate runtime entry missing: {entry}")
    sys.path.insert(0, str(pylaunch))
    spec = importlib.util.spec_from_file_location("p25_exact_candidate_runtime_entry", entry)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load exact candidate runtime entry")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    Base = module.MeasurementPublisher
    ring = {"schema": STATUS_RING_SCHEMA, "version": 1, "runNonce": os.environ.get("WOF_ALPHA_P25_RUN_NONCE"), "snapshots": [], "truncated": False}

    class TeePublisher(Base):
        def publish(self, state: str, **payload: Any) -> None:
            super().publish(state, **payload)
            snapshot = self.store.get().snapshot()
            row = {"publisherSequence": len(ring["snapshots"]), "measurementState": state, "snapshot": snapshot, "payload": payload}
            ring["snapshots"].append(row)
            if len(ring["snapshots"]) > MAX_SNAPSHOTS:
                del ring["snapshots"][0]
                ring["truncated"] = True
            _atomic(args.status_ring, ring)

    module.MeasurementPublisher = TeePublisher
    old_argv = sys.argv
    sys.argv = [str(entry), *candidate_args]
    try:
        return int(module.main() or 0)
    finally:
        sys.argv = old_argv
        _atomic(args.status_ring, ring)


if __name__ == "__main__":
    raise SystemExit(main())
