from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import p47_bounded_owner_diagnostic_readiness_gate as core


def evaluate(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    artifact = core.evaluate(snapshot)
    requested = snapshot.get("requestedRunBudget", 1)
    if requested != 1:
        blockers = list(artifact.get("blockerCodes") or [])
        if "RUN_BUDGET_NOT_EXACTLY_ONE" not in blockers:
            blockers.append("RUN_BUDGET_NOT_EXACTLY_ONE")
        artifact["blockerCodes"] = blockers
        artifact["checks"]["runBudget.requestedExactlyOne"] = False
        artifact["decision"] = core.BLOCKED
        artifact["runBudget"] = 0
    else:
        artifact["checks"]["runBudget.requestedExactlyOne"] = True
        artifact["runBudget"] = 1 if artifact.get("decision") == core.READY else 0
    artifact["requestedRunBudget"] = requested
    return artifact


def collect(repo_root: Path) -> dict[str, Any]:
    snapshot = core.collect(repo_root)
    snapshot["requestedRunBudget"] = 1
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        artifact = evaluate(collect(args.repo_root))
    except Exception as exc:
        artifact = {
            "schema": "wof-alpha-p47-bounded-owner-diagnostic-readiness-v1",
            "decision": core.BLOCKED,
            "runBudget": 0,
            "requestedRunBudget": 1,
            "blockerCodes": ["READINESS_INPUT_UNAVAILABLE_OR_INVALID"],
            "error": f"{type(exc).__name__}: {exc}",
            "terminalAuthority": "RESULT_AND_CLOSED_CLAIMS_ONLY_PROGRESS_IGNORED",
        }
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if artifact.get("decision") == core.READY else 2


if __name__ == "__main__":
    raise SystemExit(main())
