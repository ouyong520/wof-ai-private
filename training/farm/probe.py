"""Dependency/environment and optional one-instance WOF runtime probe."""

from __future__ import annotations

import argparse
import hashlib
import json

from .adapter import CoreAction, TrainingFarmAdapter, TrainingFarmError
from .stable_retro_backend import StableRetroFbneoBackend, dependency_probe


def one_instance_probe() -> dict[str, object]:
    backend = StableRetroFbneoBackend()
    with TrainingFarmAdapter(backend) as adapter:
        reset_ram = adapter.reset()
        state = adapter.save_state()
        adapter.step(CoreAction(player=0, pressed=()))
        stepped_ram = adapter.read_ram()
        adapter.load_state(state)
        restored_ram = adapter.read_ram()
        if restored_ram != reset_ram:
            raise RuntimeError("RAM mismatch after save/load restore")
        return {
            "status": "PASS",
            "ram_bytes": len(reset_ram),
            "state_bytes": len(state),
            "reset_ram_sha256": hashlib.sha256(reset_ram).hexdigest(),
            "stepped_ram_changed": stepped_ram != reset_ram,
            "restored_ram_matches": True,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runtime",
        action="store_true",
        help="run the explicit one-instance WOF probe; requires WOF_ROM_PATH",
    )
    args = parser.parse_args()

    report = dependency_probe()
    output: dict[str, object] = {"environment": report.to_dict()}

    if args.runtime:
        if not report.runtime_ready:
            output["runtime"] = {
                "status": "SKIP",
                "reason": report.detail,
            }
            print(json.dumps(output, indent=2, sort_keys=True))
            return 2
        try:
            output["runtime"] = one_instance_probe()
        except TrainingFarmError as exc:
            output["runtime"] = {"status": "FAIL", "reason": str(exc)}
            print(json.dumps(output, indent=2, sort_keys=True))
            return 1

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
