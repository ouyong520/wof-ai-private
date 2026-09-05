#!/usr/bin/env python3
"""Read-only structural Git evidence verifier for Alpha worker RESULT.json files."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from alpha_worker_result import load_result, validate_result  # noqa: E402

VERDICT_SCHEMA = "wof-alpha-result-evidence-verdict-v1"
PAPERWORK_PREFIXES = (
    "parallel/PM/DEDUP_CLAIMS/",
    "parallel/PM/STAGE_CLAIMS/",
    "parallel/PM/RESULTS/",
)
PAPERWORK_EXACT = {
    "parallel/PM/CURRENT_DISPATCH.json",
}
PAPERWORK_SUBJECT_PREFIXES = (
    "CLAIM ",
    "WORKER_RESULT ",
)


def _git(repo_root: Path, args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"git exited {proc.returncode}"
        raise RuntimeError(f"git {' '.join(args)}: {detail}")
    return proc


def _repo_root(path: str | Path) -> Path:
    root = Path(path).resolve()
    proc = _git(root, ["rev-parse", "--show-toplevel"], check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"{root} is not a Git work tree")
    return Path(proc.stdout.strip()).resolve()


def _commit_exists(repo_root: Path, sha: str) -> bool:
    return _git(repo_root, ["cat-file", "-e", f"{sha}^{{commit}}"], check=False).returncode == 0


def _commit_subject(repo_root: Path, sha: str) -> str:
    return _git(repo_root, ["show", "-s", "--format=%s", sha]).stdout.rstrip("\n")


def _commit_files(repo_root: Path, sha: str) -> list[str]:
    # -m makes merge commits expose the union of per-parent changed paths.
    proc = _git(
        repo_root,
        ["diff-tree", "--root", "-m", "--no-commit-id", "--name-only", "-r", sha],
    )
    return sorted({line.strip() for line in proc.stdout.splitlines() if line.strip()})


def _is_ancestor(repo_root: Path, older: str, newer: str) -> tuple[bool | None, str | None]:
    proc = _git(repo_root, ["merge-base", "--is-ancestor", older, newer], check=False)
    if proc.returncode == 0:
        return True, None
    if proc.returncode == 1:
        return False, None
    detail = proc.stderr.strip() or proc.stdout.strip() or f"git exited {proc.returncode}"
    return None, detail


def _is_prompt_path(path: str) -> bool:
    return path.startswith("parallel/PM/") and (
        path.endswith("_START_PROMPT.md")
        or "/DISPATCH_MANIFESTS/" in path
    )


def _is_paperwork_path(path: str) -> bool:
    return (
        path in PAPERWORK_EXACT
        or path.startswith(PAPERWORK_PREFIXES)
        or _is_prompt_path(path)
    )


def _classify_commit(subject: str, files: Sequence[str]) -> str:
    if not files:
        return "NO_MATERIAL_FILES"
    if all(_is_paperwork_path(path) for path in files):
        return "PAPERWORK_ONLY"
    if subject.startswith(PAPERWORK_SUBJECT_PREFIXES) and all(
        _is_paperwork_path(path) for path in files
    ):
        return "PAPERWORK_ONLY"
    return "IMPLEMENTATION_BEARING"


def verify_result(result_path: str | Path, repo_root: str | Path) -> dict[str, Any]:
    root = _repo_root(repo_root)
    path = Path(result_path)
    if not path.is_absolute():
        path = root / path
    data = load_result(path)
    envelope_errors = validate_result(data)

    verdict: dict[str, Any] = {
        "schema": VERDICT_SCHEMA,
        "resultPath": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "stageId": data.get("stageId") if isinstance(data, dict) else None,
        "resultState": data.get("state") if isinstance(data, dict) else None,
        "resultIntegrationReady": data.get("integrationReady") if isinstance(data, dict) else None,
        "acceptableForIntegration": False,
        "discrepancies": [],
        "verifiedImplementationCommits": [],
        "verifiedChangedFiles": [],
        "declaredChangedFiles": [],
        "materialFilesTouched": [],
        "omittedMaterialFiles": [],
        "paperworkOnlyCommits": [],
        "deeperPmInspectionRequired": False,
        "productProof": data.get("productProof") if isinstance(data, dict) else None,
        "productProofInference": "NONE",
    }

    discrepancies: list[dict[str, Any]] = verdict["discrepancies"]
    if envelope_errors:
        discrepancies.extend(
            {"code": "INVALID_RESULT_ENVELOPE", "detail": error}
            for error in envelope_errors
        )
        verdict["deeperPmInspectionRequired"] = True
        return verdict

    assert isinstance(data, dict)
    commits = list(data["implementationCommits"])
    declared_files = list(data["changedFiles"])
    verdict["declaredChangedFiles"] = declared_files

    start_commit = data["startCommit"]
    if not _commit_exists(root, start_commit):
        discrepancies.append(
            {
                "code": "START_COMMIT_MISSING",
                "startCommit": start_commit,
                "detail": "Declared startCommit does not exist in the local Git repository.",
            }
        )

    touched_union: set[str] = set()
    implementation_bearing = 0
    for sha in commits:
        if not _commit_exists(root, sha):
            discrepancies.append(
                {
                    "code": "IMPLEMENTATION_COMMIT_MISSING",
                    "commit": sha,
                    "detail": "Declared implementation commit does not exist in the local Git repository.",
                }
            )
            continue

        subject = _commit_subject(root, sha)
        files = _commit_files(root, sha)
        touched_union.update(files)
        classification = _classify_commit(subject, files)
        if classification == "IMPLEMENTATION_BEARING":
            implementation_bearing += 1
        elif classification == "PAPERWORK_ONLY":
            verdict["paperworkOnlyCommits"].append(sha)
            discrepancies.append(
                {
                    "code": "DECLARED_IMPLEMENTATION_COMMIT_IS_PAPERWORK_ONLY",
                    "commit": sha,
                    "detail": "implementationCommits must not include claim-only, result-only, manifest/prompt-only commits.",
                }
            )
        else:
            discrepancies.append(
                {
                    "code": "IMPLEMENTATION_COMMIT_HAS_NO_MATERIAL_FILES",
                    "commit": sha,
                    "detail": "Declared implementation commit exposes no materially changed paths.",
                }
            )

        ancestry: bool | None = None
        ancestry_detail: str | None = None
        if _commit_exists(root, start_commit):
            ancestry, ancestry_detail = _is_ancestor(root, start_commit, sha)
            if ancestry is False:
                discrepancies.append(
                    {
                        "code": "IMPOSSIBLE_START_ANCESTRY",
                        "commit": sha,
                        "startCommit": start_commit,
                        "detail": "Declared implementation commit is not a descendant of startCommit.",
                    }
                )
            elif ancestry is None:
                discrepancies.append(
                    {
                        "code": "ANCESTRY_UNVERIFIABLE",
                        "commit": sha,
                        "startCommit": start_commit,
                        "detail": ancestry_detail or "Git could not verify ancestry.",
                    }
                )

        verdict["verifiedImplementationCommits"].append(
            {
                "sha": sha,
                "subject": subject,
                "classification": classification,
                "changedFiles": files,
                "descendsFromStartCommit": ancestry,
            }
        )

    material_touched = sorted(path for path in touched_union if not _is_paperwork_path(path))
    verdict["materialFilesTouched"] = material_touched

    declared_set = set(declared_files)
    untouched_declared = sorted(declared_set - touched_union)
    if untouched_declared:
        discrepancies.append(
            {
                "code": "DECLARED_CHANGED_FILES_NOT_TOUCHED",
                "paths": untouched_declared,
                "detail": "Declared changedFiles paths are not touched by any declared implementation commit.",
            }
        )

    omitted_material = sorted(set(material_touched) - declared_set)
    verdict["omittedMaterialFiles"] = omitted_material
    if omitted_material:
        discrepancies.append(
            {
                "code": "MATERIAL_FILES_OMITTED_FROM_RESULT",
                "paths": omitted_material,
                "detail": "Material files touched by declared implementation commits are omitted from changedFiles.",
            }
        )

    verdict["verifiedChangedFiles"] = sorted(declared_set & touched_union)

    if data["integrationReady"] is True and not commits:
        discrepancies.append(
            {
                "code": "NO_IMPLEMENTATION_COMMITS",
                "detail": "integrationReady=true requires declared implementation commit evidence.",
            }
        )

    if data["integrationReady"] is True and implementation_bearing == 0:
        discrepancies.append(
            {
                "code": "PAPERWORK_ONLY_FALSE_GREEN",
                "commits": commits,
                "detail": "integrationReady=true but declared implementation commits contain no implementation-bearing changes.",
            }
        )

    if data["integrationReady"] is not True:
        discrepancies.append(
            {
                "code": "RESULT_NOT_INTEGRATION_READY",
                "detail": "RESULT.json itself does not declare integrationReady=true.",
            }
        )

    verdict["deeperPmInspectionRequired"] = bool(discrepancies) or bool(
        verdict["paperworkOnlyCommits"]
    )
    verdict["acceptableForIntegration"] = not discrepancies
    return verdict


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify RESULT.json implementation commits and changedFiles against local Git evidence."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify", help="verify one RESULT.json read-only")
    verify.add_argument("--result", required=True, help="repository-relative or absolute RESULT.json path")
    verify.add_argument("--repo-root", default=".", help="Git checkout root (default: current directory)")
    verify.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print the machine-readable verdict instead of one compact JSON line",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command != "verify":
        return 2
    try:
        verdict = verify_result(args.result, args.repo_root)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        verdict = {
            "schema": VERDICT_SCHEMA,
            "resultPath": args.result,
            "stageId": None,
            "acceptableForIntegration": False,
            "discrepancies": [
                {
                    "code": "VERIFIER_ERROR",
                    "detail": str(exc),
                }
            ],
            "verifiedImplementationCommits": [],
            "verifiedChangedFiles": [],
            "materialFilesTouched": [],
            "omittedMaterialFiles": [],
            "paperworkOnlyCommits": [],
            "deeperPmInspectionRequired": True,
            "productProofInference": "NONE",
        }
        print(json.dumps(verdict, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
        return 2

    print(json.dumps(verdict, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if verdict["acceptableForIntegration"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
