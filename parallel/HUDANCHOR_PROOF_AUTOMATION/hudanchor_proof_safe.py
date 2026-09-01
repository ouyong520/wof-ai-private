from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import hudanchor_proof as engine
from proof_policy import evaluate_trace


def _candidate_payload(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    for key in ("projectionModel", "projectionCandidate", "candidate"):
        if isinstance(data.get(key), dict):
            return data[key]
    return data


def load_projection_reference(path: str | None) -> dict[str, Any] | None:
    if path:
        try:
            return _candidate_payload(json.loads(Path(path).expanduser().read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return None

    root = engine._repo_root() / "parallel/HUDANCHOR_REVERSE"
    preferred = [root / "PROJECTION_MODEL.json", root / "PROJECTION_CANDIDATE.json", root / "RESULT.json"]
    candidates = preferred + sorted(root.glob("*.json")) if root.is_dir() else preferred
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            payload = _candidate_payload(json.loads(candidate.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
        if isinstance(payload, dict):
            return payload
    return None


def main(argv=None) -> int:
    # The engine calls module globals for both reference loading and evaluation.
    # Replace both with the strict fail-closed policy before entering live CDP.
    engine._load_reference = load_projection_reference
    engine.evaluate_trace = evaluate_trace
    return engine.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
