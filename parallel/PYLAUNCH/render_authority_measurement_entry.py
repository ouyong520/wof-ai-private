from __future__ import annotations

import runpy
from pathlib import Path


def main() -> int:
    runner = Path(__file__).resolve().parents[1] / "RENDER_AUTHORITY_V2" / "measurement_runner.py"
    if not runner.is_file():
        raise SystemExit("render authority V2 measurement runner missing")
    ns = runpy.run_path(str(runner), run_name="__main__")
    return int(ns.get("__return_code__", 0) or 0)


if __name__ == "__main__":
    main()
