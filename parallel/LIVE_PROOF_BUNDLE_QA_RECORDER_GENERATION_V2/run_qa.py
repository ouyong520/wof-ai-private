from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QA_DIR = Path(__file__).resolve().parent

CASES = (
    ("fresh-inflight-rollover-race", QA_DIR, "test_recorder_generation_inflight_race.py"),
    ("implementation-generation-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_recorder_authority_generation.py"),
    ("implementation-heartbeat-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_recorder_authority_heartbeat.py"),
    ("unified-live-proof-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_unified_live_proof.py"),
    ("freshness-independent-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE_QA_FRESHNESS", "test_freshness_adversarial.py"),
    ("failclosed-independent-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE_QA_FAILCLOSED", "test_failclosed_adversarial.py"),
    ("unified-preflight-regression", ROOT / "parallel" / "LIVE_PROOF_BUNDLE", "test_unified_preflight.py"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> int:
    rows: list[dict[str, object]] = []
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
            "outputTail": output[-12000:],
        })
        blocked = proc.returncode != 0

    result = {
        "schema": "wof-recorder-authority-generation-fresh-qa-v2-run-v1",
        "updatedAtUtc": utc_now(),
        "ownerBrowserWofRequired": False,
        "stopOnFirstBlocker": True,
        "result": "BLOCKED" if blocked else "PASS",
        "cases": rows,
    }
    out = QA_DIR / "RUN_RESULT.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nsummary: {out}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
