from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "parallel" / "LIVE_PROOF_BUNDLE"
QA = ROOT / "parallel" / "LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY"

SUITES = (
    (QA, "test_recorder_inflight_atomicity_fresh_qa.py"),
    (ROOT / "parallel" / "LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2", "test_recorder_generation_inflight_race.py"),
    (BUNDLE, "test_recorder_inflight_generation_atomicity.py"),
    (BUNDLE, "test_recorder_authority_generation.py"),
    (BUNDLE, "test_recorder_authority_heartbeat.py"),
    (BUNDLE, "test_unified_live_proof.py"),
    (BUNDLE, "test_unified_preflight.py"),
)


def run() -> int:
    env = dict(os.environ)
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    total = 0
    for cwd, entrypoint in SUITES:
        cmd = [sys.executable, "-m", "unittest", "-v", entrypoint]
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        print(f"\n=== {cwd.relative_to(ROOT)}/{entrypoint} ===")
        print(output.rstrip())
        matches = re.findall(r"Ran\s+(\d+)\s+tests?", output)
        count = int(matches[-1]) if matches else 0
        if proc.returncode != 0 or count <= 0:
            print(f"BLOCKED: suite failed or ran zero tests (rc={proc.returncode}, tests={count})")
            return proc.returncode or 1
        total += count
    print(f"\nPASS: {len(SUITES)} suites / {total} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
