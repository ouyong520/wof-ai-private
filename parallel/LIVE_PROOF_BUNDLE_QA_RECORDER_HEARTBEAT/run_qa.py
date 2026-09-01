from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QA_DIR = Path(__file__).resolve().parent

CASES = (
    ("fresh-adversarial", QA_DIR, "test_recorder_authority_heartbeat_adversarial.py"),
    ("heartbeat-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_recorder_authority_heartbeat.py"),
    ("live-proof-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_unified_live_proof.py"),
    ("preflight-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_unified_preflight.py"),
    ("previous-freshness-qa", ROOT / "parallel" / "LIVE_PROOF_BUNDLE_QA_FRESHNESS", "test_freshness_adversarial.py"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> int:
    rows = []
    for name, cwd, entrypoint in CASES:
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "-v", entrypoint],
            cwd=str(cwd),
            text=True,
            capture_output=True,
            check=False,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        print(f"\n===== {name} =====")
        print(output.rstrip())
        rows.append({
            "name": name,
            "cwd": str(cwd.relative_to(ROOT)),
            "entrypoint": entrypoint,
            "returnCode": proc.returncode,
            "result": "PASS" if proc.returncode == 0 else "FAIL",
            "outputTail": output[-8000:],
        })

    summary = {
        "schema": "wof-recorder-authority-heartbeat-fresh-qa-run-v1",
        "updatedAtUtc": utc_now(),
        "ownerBrowserWofRequired": False,
        "result": "PASS" if all(row["returnCode"] == 0 for row in rows) else "FAIL",
        "cases": rows,
    }
    out = QA_DIR / "RUN_RESULT.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nsummary: {out}")
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
