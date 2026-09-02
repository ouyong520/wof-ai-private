from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QA_DIR = Path(__file__).resolve().parent

# Stop on first deterministic blocker. The remaining cases are the mandatory
# regressions to execute only if the fresh generation-boundary attack is green.
CASES = (
    ("fresh-generation-boundary", QA_DIR, "test_recorder_authority_generation_adversarial.py"),
    ("existing-recorder-heartbeat-independent-qa", ROOT / "parallel" / "LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT", "run_qa.py"),
    ("implementation-generation-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_recorder_authority_generation.py"),
    ("unified-live-proof-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_unified_live_proof.py"),
    ("unified-preflight-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_unified_preflight.py"),
    ("previous-freshness-qa", ROOT / "parallel" / "LIVE_PROOF_BUNDLE_QA_FRESHNESS", "test_freshness_adversarial.py"),
    ("previous-failclosed-qa", ROOT / "parallel" / "LIVE_PROOF_BUNDLE_QA_FAILCLOSED", "test_failclosed_adversarial.py"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def command_for(cwd: Path, entrypoint: str) -> list[str]:
    if entrypoint == "run_qa.py":
        return [sys.executable, entrypoint]
    return [sys.executable, "-m", "unittest", "-v", entrypoint]


def main() -> int:
    rows = []
    blocked = False
    for name, cwd, entrypoint in CASES:
        if blocked:
            rows.append({
                "name": name,
                "cwd": str(cwd.relative_to(ROOT)),
                "entrypoint": entrypoint,
                "result": "NOT_RUN_STOP_ON_BLOCKER",
            })
            continue
        proc = subprocess.run(
            command_for(cwd, entrypoint),
            cwd=str(cwd),
            text=True,
            capture_output=True,
            check=False,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        print(f"\n===== {name} =====")
        print(output.rstrip())
        row = {
            "name": name,
            "cwd": str(cwd.relative_to(ROOT)),
            "entrypoint": entrypoint,
            "returnCode": proc.returncode,
            "result": "PASS" if proc.returncode == 0 else "FAIL",
            "outputTail": output[-12000:],
        }
        rows.append(row)
        if proc.returncode != 0:
            blocked = True

    summary = {
        "schema": "wof-recorder-authority-generation-fresh-qa-run-v1",
        "updatedAtUtc": utc_now(),
        "ownerBrowserWofRequired": False,
        "result": "BLOCKED" if blocked else "PASS",
        "stopOnFirstBlocker": True,
        "cases": rows,
    }
    out = QA_DIR / "RUN_RESULT.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nsummary: {out}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
