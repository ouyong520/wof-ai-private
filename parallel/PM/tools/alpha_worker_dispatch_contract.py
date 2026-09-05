#!/usr/bin/env python3
"""Validate Alpha PM -> Worker dispatch communication contracts.

The validator is intentionally stdlib-only and fails closed. It validates the
Git authority prompt metadata, immutable dispatch manifests, deterministic
RESULT paths, per-worker uniqueness, and prompt/manifest membership.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

RESULT_PROTOCOL = "wof-alpha-worker-result-v1"
MANIFEST_SCHEMA = "wof-alpha-dispatch-manifest-v1"
MANIFEST_SCHEMAS = {MANIFEST_SCHEMA, "wof-alpha-dispatch-manifest-v1-draft"}
RESULT_ROOT = "parallel/PM/RESULTS"
MANIFEST_ROOT = "parallel/PM/DISPATCH_MANIFESTS"
FEEDBACK_PROTOCOL_PATH = "parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md"
STAGE_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")
DEDUP_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,95}$")
INDEPENDENT_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,47}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
DISPATCH_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,127}$")
FINAL_TOP_LEVEL_FIELDS = {"schema", "dispatchId", "createdAtUtc", "authorityCommit", "immutable", "workers"}

PROMPT_REQUIRED = (
    "stageId",
    "dedupProtocol",
    "dedupKey",
    "dedupMode",
    "resultProtocol",
    "resultJsonPath",
    "resultMdPath",
    "terminalCommitPrefix",
)

MANIFEST_WORKER_REQUIRED = (
    "stageId",
    "promptPath",
    "dedupKey",
    "resultProtocol",
    "resultJsonPath",
    "resultMdPath",
    "terminalCommitPrefix",
)
FINAL_WORKER_FIELDS = {"slot", *MANIFEST_WORKER_REQUIRED}


def result_contract(stage_id: str) -> dict[str, str]:
    if not isinstance(stage_id, str) or not STAGE_RE.fullmatch(stage_id):
        raise ValueError("stageId must match ^[A-Z][A-Z0-9_]{2,127}$")
    stem = f"{RESULT_ROOT}/{stage_id}_RESULT"
    return {
        "resultJsonPath": f"{stem}.json",
        "resultMdPath": f"{stem}.md",
        "terminalCommitPrefix": f"WORKER_RESULT {stage_id}",
    }


def _require(obj: Mapping[str, Any], fields: Sequence[str], where: str) -> list[str]:
    return [f"{where}.{field}: missing required field" for field in fields if field not in obj]


def _string(value: Any, where: str) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"{where}: must be a non-empty string"]
    return []


def _valid_pm_md_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("parallel/PM/") or not value.endswith(".md"):
        return False
    if "\\" in value:
        return False
    return ".." not in Path(value).parts


def parse_prompt_metadata(text: str) -> dict[str, str]:
    """Parse the contiguous key/value metadata header at the top of a prompt."""
    metadata: dict[str, str] = {}
    started = False
    for raw in text.lstrip("\ufeff").splitlines():
        line = raw.strip()
        if not line:
            if started:
                break
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*)", line)
        if not match:
            break
        started = True
        key, value = match.group(1), match.group(2).strip()
        if value.startswith("`") and value.endswith("`") and len(value) >= 2:
            value = value[1:-1]
        metadata[key] = value
    return metadata


def validate_prompt_text(
    text: str,
    *,
    prompt_path: str | None = None,
    manifest_path: str | None = None,
) -> list[str]:
    metadata = parse_prompt_metadata(text)
    errors = _require(metadata, PROMPT_REQUIRED, "$prompt")

    stage_id = metadata.get("stageId")
    if stage_id is not None and not STAGE_RE.fullmatch(stage_id):
        errors.append("$prompt.stageId: must match ^[A-Z][A-Z0-9_]{2,127}$")

    if metadata.get("dedupProtocol") != "v2":
        errors.append("$prompt.dedupProtocol: must equal 'v2'")
    dedup_key = metadata.get("dedupKey")
    if dedup_key is not None and not DEDUP_RE.fullmatch(dedup_key):
        errors.append("$prompt.dedupKey: must match [a-z0-9][a-z0-9.-]{2,95}")

    dedup_mode = metadata.get("dedupMode")
    if dedup_mode not in {"exclusive", "independent-validation"}:
        errors.append("$prompt.dedupMode: must equal 'exclusive' or 'independent-validation'")
    if dedup_mode == "independent-validation":
        for field in ("independentValidationGroup", "independentValidationKey"):
            value = metadata.get(field)
            if value is None:
                errors.append(f"$prompt.{field}: missing required field for independent-validation")
            elif not INDEPENDENT_RE.fullmatch(value):
                errors.append(f"$prompt.{field}: malformed independent-validation value")

    if metadata.get("resultProtocol") != RESULT_PROTOCOL:
        errors.append(f"$prompt.resultProtocol: must equal {RESULT_PROTOCOL!r}")

    if stage_id and STAGE_RE.fullmatch(stage_id):
        expected = result_contract(stage_id)
        for field, value in expected.items():
            if metadata.get(field) != value:
                errors.append(f"$prompt.{field}: expected {value!r}, got {metadata.get(field)!r}")

    dispatch_manifest = metadata.get("dispatchManifestPath")
    if dispatch_manifest is not None:
        if not dispatch_manifest.startswith(MANIFEST_ROOT + "/") or not dispatch_manifest.endswith(".json"):
            errors.append(
                f"$prompt.dispatchManifestPath: must be an immutable manifest under {MANIFEST_ROOT}/"
            )
        if manifest_path is not None and dispatch_manifest != manifest_path:
            errors.append(
                f"$prompt.dispatchManifestPath: expected current manifest {manifest_path!r}, got {dispatch_manifest!r}"
            )

    if FEEDBACK_PROTOCOL_PATH not in text:
        errors.append("$prompt.terminalReporting: must require " + FEEDBACK_PROTOCOL_PATH)

    if prompt_path is not None:
        if not _valid_pm_md_path(prompt_path):
            errors.append("$promptPath: must be a traversal-free repository-relative parallel/PM/*.md path")

    return sorted(set(errors))


def _validate_worker_entry(entry: Any, index: int) -> list[str]:
    where = f"$manifest.workers[{index}]"
    if not isinstance(entry, dict):
        return [f"{where}: must be an object"]
    errors = _require(entry, MANIFEST_WORKER_REQUIRED, where)
    stage_id = entry.get("stageId")
    if stage_id is not None and (not isinstance(stage_id, str) or not STAGE_RE.fullmatch(stage_id)):
        errors.append(f"{where}.stageId: malformed stageId")
    prompt_path = entry.get("promptPath")
    if prompt_path is not None:
        if not _valid_pm_md_path(prompt_path):
            errors.append(f"{where}.promptPath: must be a traversal-free repository-relative parallel/PM/*.md path")
    dedup_key = entry.get("dedupKey")
    if dedup_key is not None and (not isinstance(dedup_key, str) or not DEDUP_RE.fullmatch(dedup_key)):
        errors.append(f"{where}.dedupKey: malformed dedupKey")
    if entry.get("resultProtocol") != RESULT_PROTOCOL:
        errors.append(f"{where}.resultProtocol: must equal {RESULT_PROTOCOL!r}")
    if stage_id and isinstance(stage_id, str) and STAGE_RE.fullmatch(stage_id):
        expected = result_contract(stage_id)
        for field, value in expected.items():
            if entry.get(field) != value:
                errors.append(f"{where}.{field}: expected {value!r}, got {entry.get(field)!r}")
    if "dedupProtocol" in entry and entry.get("dedupProtocol") != "v2":
        errors.append(f"{where}.dedupProtocol: must equal 'v2' when present")
    if "dedupMode" in entry and entry.get("dedupMode") not in {"exclusive", "independent-validation"}:
        errors.append(f"{where}.dedupMode: unsupported value")
    return errors


def _status_dashboard_paths(obj: Mapping[str, Any]) -> list[tuple[str, str]]:
    paths: list[tuple[str, str]] = []
    for key, value in obj.items():
        lowered = key.lower()
        if ("status" in lowered or "dashboard" in lowered) and isinstance(value, str) and value.strip():
            paths.append((key, value))
    return paths


def validate_manifest_data(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["$manifest: must be a JSON object"]
    errors: list[str] = []
    schema = data.get("schema")
    base_required = ("schema", "dispatchId", "immutable", "workers")
    final_required = ("createdAtUtc", "authorityCommit") if schema == MANIFEST_SCHEMA else ()
    for field in (*base_required, *final_required):
        if field not in data:
            errors.append(f"$manifest.{field}: missing required field")

    if schema not in MANIFEST_SCHEMAS:
        errors.append(
            f"$manifest.schema: expected {MANIFEST_SCHEMA!r} (or bootstrap draft), got {data.get('schema')!r}"
        )
    errors.extend(_string(data.get("dispatchId"), "$manifest.dispatchId") if "dispatchId" in data else [])
    if "dispatchId" in data and isinstance(data.get("dispatchId"), str) and not DISPATCH_ID_RE.fullmatch(data["dispatchId"]):
        errors.append("$manifest.dispatchId: must match ^[A-Z0-9][A-Z0-9_.-]{2,127}$")
    if schema == MANIFEST_SCHEMA:
        for key in sorted(set(data) - FINAL_TOP_LEVEL_FIELDS):
            errors.append(f"$manifest.{key}: unexpected field in final C2 manifest contract")
    repo = data.get("repository")
    if repo is not None and (not isinstance(repo, str) or not REPO_RE.fullmatch(repo)):
        errors.append("$manifest.repository: must be owner/name")
    authority_path = data.get("authorityPath")
    if authority_path is not None and not _valid_pm_md_path(authority_path):
        errors.append("$manifest.authorityPath: must be a traversal-free repository-relative parallel/PM/*.md path")
    if schema == MANIFEST_SCHEMA:
        created = data.get("createdAtUtc")
        if created is not None and (not isinstance(created, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", created)):
            errors.append("$manifest.createdAtUtc: must be UTC YYYY-MM-DDTHH:MM:SSZ")
        authority_commit = data.get("authorityCommit")
        if authority_commit is not None and (
            not isinstance(authority_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", authority_commit)
        ):
            errors.append("$manifest.authorityCommit: must be a lowercase 40-hex commit SHA")
    if data.get("immutable") is not True:
        errors.append("$manifest.immutable: must be true")

    workers = data.get("workers")
    if not isinstance(workers, list):
        errors.append("$manifest.workers: must be an array")
        return sorted(set(errors))
    if not 1 <= len(workers) <= 3:
        errors.append("$manifest.workers: worker count must be 1, 2, or 3")

    seen_slot: dict[int, int] = {}
    seen_stage: dict[str, int] = {}
    seen_prompt: dict[str, int] = {}
    seen_result_json: dict[str, int] = {}
    seen_result_md: dict[str, int] = {}
    mutable_paths: dict[str, tuple[int, str]] = {}

    for index, entry in enumerate(workers):
        errors.extend(_validate_worker_entry(entry, index))
        if not isinstance(entry, dict):
            continue
        if schema == MANIFEST_SCHEMA:
            for key in sorted(set(entry) - FINAL_WORKER_FIELDS):
                errors.append(f"$manifest.workers[{index}].{key}: unexpected field in final C2 manifest contract")
            slot = entry.get("slot")
            if not isinstance(slot, int) or isinstance(slot, bool) or not 1 <= slot <= 99:
                errors.append(f"$manifest.workers[{index}].slot: final manifest requires integer slot 1..99")
            elif slot in seen_slot:
                errors.append(f"$manifest.workers[{index}].slot: duplicate slot; also used by worker {seen_slot[slot]}")
            else:
                seen_slot[slot] = index
        for field, seen, code in (
            ("stageId", seen_stage, "duplicate stageId"),
            ("promptPath", seen_prompt, "duplicate promptPath"),
            ("resultJsonPath", seen_result_json, "duplicate RESULT.json path"),
            ("resultMdPath", seen_result_md, "duplicate RESULT.md path"),
        ):
            value = entry.get(field)
            if isinstance(value, str):
                if value in seen:
                    errors.append(
                        f"$manifest.workers[{index}].{field}: {code}; also used by worker {seen[value]}"
                    )
                else:
                    seen[value] = index
        for key, path in _status_dashboard_paths(entry):
            if path in mutable_paths:
                prev_index, prev_key = mutable_paths[path]
                errors.append(
                    f"$manifest.workers[{index}].{key}: shared mutable worker status/dashboard path {path!r}; "
                    f"also used by workers[{prev_index}].{prev_key}"
                )
            else:
                mutable_paths[path] = (index, key)

    if schema == MANIFEST_SCHEMA and len(workers) in (1, 2, 3) and set(seen_slot) != set(range(1, len(workers) + 1)):
        errors.append(f"$manifest.workers: slots must be exactly 1..{len(workers)} for PM shorthand")

    for key, path in _status_dashboard_paths(data):
        if key not in {"status", "schema"}:
            errors.append(
                f"$manifest.{key}: global mutable status/dashboard path {path!r} is forbidden; use per-stage RESULT files"
            )

    return sorted(set(errors))


def validate_entry_against_prompt(
    entry: Mapping[str, Any],
    prompt_text: str,
    *,
    index: int,
    manifest_path: str,
) -> list[str]:
    prompt_path = entry.get("promptPath")
    metadata = parse_prompt_metadata(prompt_text)
    errors = validate_prompt_text(
        prompt_text,
        prompt_path=prompt_path if isinstance(prompt_path, str) else None,
        manifest_path=manifest_path,
    )
    where = f"$manifest.workers[{index}]"
    for field in (
        "stageId",
        "dedupKey",
        "resultProtocol",
        "resultJsonPath",
        "resultMdPath",
        "terminalCommitPrefix",
    ):
        if metadata.get(field) != entry.get(field):
            errors.append(
                f"{where}.{field}: manifest/prompt mismatch; manifest={entry.get(field)!r}, prompt={metadata.get(field)!r}"
            )
    return sorted(set(errors))


def repo_relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def validate_dispatch(manifest_path: Path, repo_root: Path) -> list[str]:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"$manifest: cannot read valid JSON: {exc}"]
    errors = validate_manifest_data(data)
    try:
        manifest_rel = repo_relative(manifest_path, repo_root)
    except ValueError:
        errors.append("$manifestPath: manifest must be inside repo root")
        return sorted(set(errors))

    workers = data.get("workers") if isinstance(data, dict) else None
    if not isinstance(workers, list):
        return sorted(set(errors))
    for index, entry in enumerate(workers):
        if not isinstance(entry, dict):
            continue
        prompt_path = entry.get("promptPath")
        if not isinstance(prompt_path, str):
            continue
        prompt_file = repo_root / prompt_path
        try:
            prompt_text = prompt_file.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"$manifest.workers[{index}].promptPath: cannot read {prompt_path!r}: {exc}")
            continue
        errors.extend(
            validate_entry_against_prompt(
                entry,
                prompt_text,
                index=index,
                manifest_path=manifest_rel,
            )
        )
    return sorted(set(errors))


def _report(kind: str, errors: Sequence[str], **extra: Any) -> int:
    payload = {"schema": "wof-alpha-dispatch-contract-validation-v1", "kind": kind, "ok": not errors}
    payload.update(extra)
    payload["errors"] = list(errors)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prompt = sub.add_parser("validate-prompt")
    prompt.add_argument("path", type=Path)
    manifest = sub.add_parser("validate-manifest")
    manifest.add_argument("path", type=Path)
    dispatch = sub.add_parser("validate-dispatch")
    dispatch.add_argument("manifest", type=Path)
    dispatch.add_argument("--repo-root", type=Path, default=Path("."))
    derive = sub.add_parser("derive")
    derive.add_argument("stage_id")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "derive":
        try:
            contract = result_contract(args.stage_id)
        except ValueError as exc:
            return _report("derive", [str(exc)], stageId=args.stage_id)
        return _report("derive", [], stageId=args.stage_id, contract=contract)
    if args.command == "validate-prompt":
        try:
            text = args.path.read_text(encoding="utf-8")
        except OSError as exc:
            return _report("prompt", [f"cannot read prompt: {exc}"])
        return _report("prompt", validate_prompt_text(text), path=str(args.path))
    if args.command == "validate-manifest":
        try:
            data = json.loads(args.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return _report("manifest", [f"cannot read valid JSON: {exc}"])
        workers = data.get("workers") if isinstance(data, dict) else None
        return _report(
            "manifest",
            validate_manifest_data(data),
            path=str(args.path),
            workerCount=len(workers) if isinstance(workers, list) else None,
        )
    errors = validate_dispatch(args.manifest, args.repo_root)
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        workers = data.get("workers") if isinstance(data, dict) else None
    except Exception:
        workers = None
    return _report(
        "dispatch",
        errors,
        path=str(args.manifest),
        workerCount=len(workers) if isinstance(workers, list) else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
