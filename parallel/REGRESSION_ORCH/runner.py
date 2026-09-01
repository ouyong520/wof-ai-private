from __future__ import annotations

from pathlib import Path

import orchestrator as core


_CORE_DISCOVER_CANDIDATES = core.discover_candidates
IGNORED_PARTS = {
    ".venv",
    "venv",
    "env",
    "site-packages",
    "node_modules",
    "__pycache__",
    ".git",
}


def is_generated_or_dependency_path(path: str | Path) -> bool:
    parts = {part.lower() for part in Path(path).parts}
    return bool(parts & IGNORED_PARTS)


def discover_candidates(root: Path) -> list[str]:
    return [
        path
        for path in _CORE_DISCOVER_CANDIDATES(root)
        if not is_generated_or_dependency_path(path)
    ]


def install_safe_discovery() -> None:
    core.discover_candidates = discover_candidates


def main() -> int:
    install_safe_discovery()
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
