#!/usr/bin/env python3
"""Build deterministic, fail-closed Alpha PM -> Worker dispatch packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

import alpha_worker_dispatch_contract as dispatch_contract

SPEC_SCHEMA = "wof-alpha-dispatch-spec-v1"
MANIFEST_SCHEMA = "wof-alpha-dispatch-manifest-v1"
RESULT_PROTOCOL = "wof-alpha-worker-result-v1"
FEEDBACK_PROTOCOL_PATH = "parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md"
DISPATCH_CONTRACT_PATH = "parallel/PM/ALPHA_PM_DISPATCH_CONTRACT_V1.md"
MANIFEST_ROOT = "parallel/PM/DISPATCH_MANIFESTS"
STAGE_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")
DEDUP_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,95}$")
INDEPENDENT_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,47}$")
DISPATCH_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,127}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
CREATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

TOP_LEVEL_FIELDS = {
    "schema",
    "dispatchId",
    "createdAtUtc",
    "authorityPath",
    "authorityCommit",
    "manifestPath",
    "workers",
}
WORKER_FIELDS = {
    "stageId",
    "dedupKey",
    "dedupProtocol",
    "dedupMode",
    "promptPath",
    "mission",
    "instructions",
    "resultProtocol",
    "resultJsonPath",
    "resultMdPath",
    "terminalCommitPrefix",
    "independentValidationGroup",
    "independentValidationKey",
}


class DispatchSpecError(ValueError):
    """Raised when a dispatch spec or generated package fails closed."""

    def __init__(self, errors: Sequence[str]):
        self.errors = sorted(set(str(error) for error in errors))
        super().__init__("; ".join(self.errors))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _is_safe_repo_path(value: Any, *, prefix: str, suffix: str) -> bool:
    if not isinstance(value, str) or not value.startswith(prefix) or not value.endswith(suffix):
        return False
    if "\\" in value or value.startswith("/"):
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and "." not in parts and ".." not in parts


def _expected_manifest_path(dispatch_id: str) -> str:
    return f"{MANIFEST_ROOT}/{dispatch_id}.json"


def _expected_prompt_path(stage_id: str) -> str:
    return f"parallel/PM/{stage_id}_START_PROMPT.md"


def _text(value: Any, where: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}: must be a non-empty string")
        return ""
    return value.strip()


def normalize_spec(spec: Any) -> dict[str, Any]:
    """Normalize compact input while rejecting ambiguity and contract drift."""
    if not isinstance(spec, dict):
        raise DispatchSpecError(["$spec: must be a JSON object"])

    errors: list[str] = []
    for key in sorted(set(spec) - TOP_LEVEL_FIELDS):
        errors.append(f"$spec.{key}: unexpected field")

    if spec.get("schema") != SPEC_SCHEMA:
        errors.append(f"$spec.schema: must equal {SPEC_SCHEMA!r}")

    dispatch_id = _text(spec.get("dispatchId"), "$spec.dispatchId", errors)
    if dispatch_id and not DISPATCH_ID_RE.fullmatch(dispatch_id):
        errors.append("$spec.dispatchId: malformed dispatchId")

    created_at = _text(spec.get("createdAtUtc"), "$spec.createdAtUtc", errors)
    if created_at and not CREATED_RE.fullmatch(created_at):
        errors.append("$spec.createdAtUtc: must be UTC YYYY-MM-DDTHH:MM:SSZ")

    authority_path = _text(spec.get("authorityPath"), "$spec.authorityPath", errors)
    if authority_path and not _is_safe_repo_path(authority_path, prefix="parallel/PM/", suffix=".md"):
        errors.append("$spec.authorityPath: must be traversal-free parallel/PM/*.md")

    authority_commit = _text(spec.get("authorityCommit"), "$spec.authorityCommit", errors)
    if authority_commit and not COMMIT_RE.fullmatch(authority_commit):
        errors.append("$spec.authorityCommit: must be lowercase 40-hex")

    expected_manifest = _expected_manifest_path(dispatch_id) if dispatch_id else ""
    declared_manifest = spec.get("manifestPath")
    manifest_path = expected_manifest if declared_manifest is None else declared_manifest
    if manifest_path and not _is_safe_repo_path(manifest_path, prefix=MANIFEST_ROOT + "/", suffix=".json"):
        errors.append(f"$spec.manifestPath: must be traversal-free under {MANIFEST_ROOT}/")
    if expected_manifest and manifest_path != expected_manifest:
        errors.append(f"$spec.manifestPath: expected {expected_manifest!r}, got {manifest_path!r}")

    workers = spec.get("workers")
    if not isinstance(workers, list):
        errors.append("$spec.workers: must be an array")
        workers = []
    if not 1 <= len(workers) <= 3:
        errors.append("$spec.workers: worker count must be 1, 2, or 3")

    normalized_workers: list[dict[str, Any]] = []
    seen_stage: dict[str, int] = {}
    seen_dedup: dict[str, int] = {}
    seen_prompt: dict[str, int] = {}
    seen_result_json: dict[str, int] = {}
    seen_result_md: dict[str, int] = {}

    for index, raw in enumerate(workers):
        where = f"$spec.workers[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{where}: must be an object")
            continue
        for key in sorted(set(raw) - WORKER_FIELDS):
            errors.append(f"{where}.{key}: unexpected field")

        stage_id = _text(raw.get("stageId"), f"{where}.stageId", errors)
        if stage_id and not STAGE_RE.fullmatch(stage_id):
            errors.append(f"{where}.stageId: malformed stageId")

        dedup_key = _text(raw.get("dedupKey"), f"{where}.dedupKey", errors)
        if dedup_key and not DEDUP_RE.fullmatch(dedup_key):
            errors.append(f"{where}.dedupKey: malformed dedupKey")

        dedup_protocol = raw.get("dedupProtocol", "v2")
        if dedup_protocol != "v2":
            errors.append(f"{where}.dedupProtocol: must equal 'v2'")

        dedup_mode = raw.get("dedupMode", "exclusive")
        if dedup_mode not in {"exclusive", "independent-validation"}:
            errors.append(f"{where}.dedupMode: unsupported value")

        iv_group = raw.get("independentValidationGroup")
        iv_key = raw.get("independentValidationKey")
        if dedup_mode == "independent-validation":
            for field, value in (("independentValidationGroup", iv_group), ("independentValidationKey", iv_key)):
                if not isinstance(value, str) or not INDEPENDENT_RE.fullmatch(value):
                    errors.append(f"{where}.{field}: required and malformed for independent-validation")
        elif iv_group is not None or iv_key is not None:
            errors.append(f"{where}: independent-validation fields require dedupMode='independent-validation'")

        expected_prompt = _expected_prompt_path(stage_id) if stage_id else ""
        prompt_path = raw.get("promptPath", expected_prompt)
        if prompt_path and not _is_safe_repo_path(prompt_path, prefix="parallel/PM/", suffix=".md"):
            errors.append(f"{where}.promptPath: must be traversal-free parallel/PM/*.md")

        mission = _text(raw.get("mission"), f"{where}.mission", errors)
        instructions = raw.get("instructions", [])
        if not isinstance(instructions, list) or any(not isinstance(item, str) or not item.strip() for item in instructions):
            errors.append(f"{where}.instructions: must be an array of non-empty strings")
            instructions = []
        else:
            instructions = [item.strip() for item in instructions]

        try:
            result_fields = dispatch_contract.result_contract(stage_id)
        except (TypeError, ValueError):
            result_fields = {
                "resultJsonPath": "",
                "resultMdPath": "",
                "terminalCommitPrefix": "",
            }

        declared_result_protocol = raw.get("resultProtocol", RESULT_PROTOCOL)
        if declared_result_protocol != RESULT_PROTOCOL:
            errors.append(f"{where}.resultProtocol: must equal {RESULT_PROTOCOL!r}")
        for field, expected in result_fields.items():
            if field in raw and raw.get(field) != expected:
                errors.append(f"{where}.{field}: expected {expected!r}, got {raw.get(field)!r}")

        for value, seen, field in (
            (stage_id, seen_stage, "stageId"),
            (dedup_key, seen_dedup, "dedupKey"),
            (prompt_path, seen_prompt, "promptPath"),
            (result_fields["resultJsonPath"], seen_result_json, "resultJsonPath"),
            (result_fields["resultMdPath"], seen_result_md, "resultMdPath"),
        ):
            if value:
                if value in seen:
                    errors.append(f"{where}.{field}: duplicate value also used by workers[{seen[value]}]")
                else:
                    seen[value] = index

        normalized_workers.append(
            {
                "slot": index + 1,
                "stageId": stage_id,
                "dedupKey": dedup_key,
                "dedupProtocol": "v2",
                "dedupMode": dedup_mode,
                "promptPath": prompt_path,
                "mission": mission,
                "instructions": instructions,
                "independentValidationGroup": iv_group,
                "independentValidationKey": iv_key,
                "resultProtocol": RESULT_PROTOCOL,
                **result_fields,
            }
        )

    if errors:
        raise DispatchSpecError(errors)
    return {
        "schema": SPEC_SCHEMA,
        "dispatchId": dispatch_id,
        "createdAtUtc": created_at,
        "authorityPath": authority_path,
        "authorityCommit": authority_commit,
        "manifestPath": manifest_path,
        "workers": normalized_workers,
    }


def _prompt_text(spec: Mapping[str, Any], worker: Mapping[str, Any]) -> str:
    header = [
        f"stageId: `{worker['stageId']}`",
        "dedupProtocol: `v2`",
        f"dedupKey: `{worker['dedupKey']}`",
        f"dedupMode: `{worker['dedupMode']}`",
    ]
    if worker["dedupMode"] == "independent-validation":
        header.extend(
            [
                f"independentValidationGroup: `{worker['independentValidationGroup']}`",
                f"independentValidationKey: `{worker['independentValidationKey']}`",
            ]
        )
    header.extend(
        [
            f"resultProtocol: `{worker['resultProtocol']}`",
            f"resultJsonPath: `{worker['resultJsonPath']}`",
            f"resultMdPath: `{worker['resultMdPath']}`",
            f"terminalCommitPrefix: `{worker['terminalCommitPrefix']}`",
            f"dispatchManifestPath: `{spec['manifestPath']}`",
        ]
    )
    body = [
        "",
        f"# {worker['stageId']} — {worker['mission']}",
        "",
        "Repository: `ouyong520/wof-ai-private`",
        "",
        "Read latest `main` first. This generated prompt and the immutable dispatch manifest are PM handoff authority; do not mutate either after dispatch.",
        "",
        "## Dispatch authority",
        "",
        f"- authorityPath: `{spec['authorityPath']}`",
        f"- authorityCommit: `{spec['authorityCommit']}`",
        f"- dispatch contract: `{DISPATCH_CONTRACT_PATH}`",
        f"- immutable manifest: `{spec['manifestPath']}`",
        "",
        "Execute only the authorized worker mission below. Worker progress/terminal state belongs in this stage's RESULT files, never in a shared mutable dispatch manifest/dashboard.",
        "",
        "## Mission",
        "",
        worker["mission"],
    ]
    if worker["instructions"]:
        body.extend(["", "## Worker instructions", ""])
        body.extend(f"- {item}" for item in worker["instructions"])
    body.extend(
        [
            "",
            "## Dedup and dispatch gate",
            "",
            "Apply `parallel/PM/STAGE_DEDUP_GUARD.md` fail-closed: latest-main preflight, create-only canonical claim, exact claimToken re-read, create-only stage claim, exact claimToken re-read, then execute.",
            "",
            "Before execution, the PM dispatch package must pass the existing C2/C3 dispatch validators. Do not repair or reinterpret manifest/prompt conflicts in the worker thread.",
            "",
            "## Terminal reporting",
            "",
            f"Terminal reporting must follow `{FEEDBACK_PROTOCOL_PATH}` using the exact RESULT paths declared above.",
            "",
            "The RESULT JSON/Markdown are per-stage mutable worker terminal artifacts. The prompt and dispatch manifest remain immutable PM handoff artifacts.",
            "",
            f"Final result commit must begin `{worker['terminalCommitPrefix']} <STATE>` where `<STATE>` is COMPLETE, SUBCOMPLETE, or BLOCKED.",
            "",
            "Chat returns only `COMPLETE`, `SUBCOMPLETE`, or `BLOCKED: <precise reason>`.",
            "",
        ]
    )
    return "\n".join(header + body)


def render_package(spec: Any, *, repo_root: Path | None = None) -> dict[str, Any]:
    normalized = normalize_spec(spec)
    errors: list[str] = []
    if repo_root is not None:
        authority_file = repo_root / PurePosixPath(normalized["authorityPath"])
        if not authority_file.is_file():
            errors.append(f"$spec.authorityPath: file does not exist under repo root: {normalized['authorityPath']!r}")

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "dispatchId": normalized["dispatchId"],
        "createdAtUtc": normalized["createdAtUtc"],
        "authorityCommit": normalized["authorityCommit"],
        "immutable": True,
        "workers": [
            {
                "slot": worker["slot"],
                "stageId": worker["stageId"],
                "promptPath": worker["promptPath"],
                "dedupKey": worker["dedupKey"],
                "resultProtocol": worker["resultProtocol"],
                "resultJsonPath": worker["resultJsonPath"],
                "resultMdPath": worker["resultMdPath"],
                "terminalCommitPrefix": worker["terminalCommitPrefix"],
            }
            for worker in normalized["workers"]
        ],
    }
    errors.extend(dispatch_contract.validate_manifest_data(manifest))

    prompts: dict[str, str] = {}
    result_paths: list[dict[str, str]] = []
    chat_handoffs: list[str] = []
    for index, worker in enumerate(normalized["workers"]):
        prompt = _prompt_text(normalized, worker)
        prompts[worker["promptPath"]] = prompt
        errors.extend(
            dispatch_contract.validate_entry_against_prompt(
                manifest["workers"][index],
                prompt,
                index=index,
                manifest_path=normalized["manifestPath"],
            )
        )
        result_paths.append(
            {
                "stageId": worker["stageId"],
                "resultJsonPath": worker["resultJsonPath"],
                "resultMdPath": worker["resultMdPath"],
            }
        )
        chat_handoffs.append(
            "\n".join(
                [
                    f"负责 {worker['mission']}。",
                    "",
                    "引用：",
                    worker["promptPath"],
                    normalized["manifestPath"],
                    "",
                    "按 Git authority 执行。完成后必须写入 Git 指定 RESULT 文件；聊天只回 COMPLETE / SUBCOMPLETE / 精确 BLOCKED。",
                ]
            )
        )

    if errors:
        raise DispatchSpecError(errors)
    return {
        "schema": "wof-alpha-dispatch-package-render-v1",
        "manifestPath": normalized["manifestPath"],
        "manifest": manifest,
        "prompts": prompts,
        "resultPaths": result_paths,
        "chatHandoffs": chat_handoffs,
    }


def _target(root: Path, repo_relative: str) -> Path:
    root_resolved = root.resolve()
    target = (root / PurePosixPath(repo_relative)).resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise DispatchSpecError([f"output path escapes root: {repo_relative!r}"]) from exc
    return target


def write_package(package: Mapping[str, Any], *, output_root: Path) -> list[str]:
    targets: list[tuple[str, str]] = []
    for prompt_path, prompt_text in package["prompts"].items():
        targets.append((prompt_path, prompt_text))
    targets.append((package["manifestPath"], canonical_json(package["manifest"])))

    existing = [path for path, _ in targets if _target(output_root, path).exists()]
    if existing:
        raise DispatchSpecError([f"output target already exists: {path}" for path in existing])

    written: list[str] = []
    for repo_path, content in targets:
        target = _target(output_root, repo_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
        except FileExistsError as exc:
            raise DispatchSpecError([f"output target raced into existence: {repo_path}"]) from exc
        written.append(repo_path)
    return written


def load_spec(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "render", "build"):
        cmd = sub.add_parser(name)
        cmd.add_argument("spec", type=Path)
        cmd.add_argument("--repo-root", type=Path, default=Path("."))
        if name == "build":
            cmd.add_argument("--output-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        spec = load_spec(args.spec)
        package = render_package(spec, repo_root=args.repo_root)
        if args.command == "validate":
            payload = {"ok": True, "dispatchId": package["manifest"]["dispatchId"], "workerCount": len(package["manifest"]["workers"])}
        elif args.command == "render":
            payload = {"ok": True, "package": package}
        else:
            written = write_package(package, output_root=args.output_root)
            payload = {"ok": True, "written": written, "resultPaths": package["resultPaths"]}
        print(canonical_json(payload), end="")
        return 0
    except (DispatchSpecError, OSError, json.JSONDecodeError) as exc:
        errors = exc.errors if isinstance(exc, DispatchSpecError) else [str(exc)]
        print(canonical_json({"ok": False, "errors": errors}), end="")
        return 2


if __name__ == "__main__":
    sys.exit(main())
