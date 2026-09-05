#!/usr/bin/env python3
"""Validate and locate WOF Alpha worker RESULT envelopes.

Stdlib-only so future workers and PM checks can run it without installing packages.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_ID = "wof-alpha-worker-result-v1"
STATES = ("SUBCOMPLETE", "COMPLETE", "BLOCKED")
TEST_RESULTS = ("PASS", "FAIL", "NOT_RUN")
PRODUCT_STATUSES = ("PROVEN", "NOT_PROVEN", "NOT_APPLICABLE")
PROOF_CLASSIFICATIONS = (
    "IMPLEMENTATION_PROOF",
    "MACHINE_DRAW_PROOF",
    "OWNER_VISUAL_PROOF",
    "NOT_PROVEN",
    "NOT_APPLICABLE",
)
PROVEN_CLASSIFICATIONS = (
    "IMPLEMENTATION_PROOF",
    "MACHINE_DRAW_PROOF",
    "OWNER_VISUAL_PROOF",
)
STAGE_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")
DEDUP_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,95}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BLOCKER_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")
RESULT_ROOT = "parallel/PM/RESULTS"

REQUIRED_TOP_LEVEL = (
    "schema",
    "stageId",
    "dedupKey",
    "claimToken",
    "state",
    "verdict",
    "startCommit",
    "implementationCommits",
    "integrationReady",
    "changedFiles",
    "tests",
    "productProof",
    "ownerGate",
    "blocker",
    "nextAction",
    "evidencePaths",
    "safety",
)


def result_paths(stage_id: str) -> dict[str, str]:
    """Return deterministic terminal RESULT paths for a valid stageId."""
    errors = _validate_stage_id(stage_id)
    if errors:
        raise ValueError(errors[0])
    stem = f"{RESULT_ROOT}/{stage_id}_RESULT"
    return {"json": f"{stem}.json", "md": f"{stem}.md"}


def verify_result_paths(stage_id: str, json_path: str, md_path: str) -> list[str]:
    """Return concise mismatches for supplied result paths."""
    try:
        expected = result_paths(stage_id)
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    if json_path != expected["json"]:
        errors.append(f"$.resultJsonPath: expected {expected['json']!r}, got {json_path!r}")
    if md_path != expected["md"]:
        errors.append(f"$.resultMdPath: expected {expected['md']!r}, got {md_path!r}")
    return errors


def _is_string(value: Any) -> bool:
    return isinstance(value, str)


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_stage_id(stage_id: Any) -> list[str]:
    if not _is_string(stage_id) or not STAGE_RE.fullmatch(stage_id):
        return ["$.stageId: must match ^[A-Z][A-Z0-9_]{2,127}$"]
    return []


def _require_keys(obj: Mapping[str, Any], keys: Iterable[str], where: str) -> list[str]:
    return [f"{where}.{key}: missing required field" for key in keys if key not in obj]


def _validate_string(value: Any, where: str, *, nonempty: bool = True) -> list[str]:
    if not _is_string(value):
        return [f"{where}: must be a string"]
    if nonempty and not value.strip():
        return [f"{where}: must be non-empty"]
    return []


def _validate_string_list(
    value: Any,
    where: str,
    *,
    sha: bool = False,
    unique: bool = True,
) -> list[str]:
    if not isinstance(value, list):
        return [f"{where}: must be an array"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        path = f"{where}[{index}]"
        if not _is_string(item) or not item.strip():
            errors.append(f"{path}: must be a non-empty string")
            continue
        if sha and not SHA_RE.fullmatch(item):
            errors.append(f"{path}: must be a lowercase 40-hex commit SHA")
        if unique:
            if item in seen:
                errors.append(f"{path}: duplicate value {item!r}")
            seen.add(item)
    return errors


def _validate_tests(value: Any) -> list[str]:
    if not isinstance(value, list):
        return ["$.tests: must be an array"]
    errors: list[str] = []
    for index, item in enumerate(value):
        where = f"$.tests[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: must be an object")
            continue
        errors.extend(_require_keys(item, ("name", "result", "detail"), where))
        if "name" in item:
            errors.extend(_validate_string(item["name"], f"{where}.name"))
        if "result" in item and item["result"] not in TEST_RESULTS:
            errors.append(
                f"{where}.result: unsupported value {item['result']!r}; "
                f"expected {'|'.join(TEST_RESULTS)}"
            )
        if "detail" in item:
            errors.extend(_validate_string(item["detail"], f"{where}.detail"))
    return errors


def _validate_product_proof(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["$.productProof: must be an object"]
    errors = _require_keys(value, ("status", "classification", "detail"), "$.productProof")
    status = value.get("status")
    classification = value.get("classification")
    if "status" in value and status not in PRODUCT_STATUSES:
        errors.append(
            f"$.productProof.status: unsupported value {status!r}; "
            f"expected {'|'.join(PRODUCT_STATUSES)}"
        )
    if "classification" in value and classification not in PROOF_CLASSIFICATIONS:
        errors.append(
            f"$.productProof.classification: unsupported value {classification!r}"
        )
    if "detail" in value:
        errors.extend(_validate_string(value["detail"], "$.productProof.detail"))

    if status == "PROVEN" and classification not in PROVEN_CLASSIFICATIONS:
        errors.append(
            "$.productProof.classification: PROVEN requires explicit "
            "IMPLEMENTATION_PROOF, MACHINE_DRAW_PROOF, or OWNER_VISUAL_PROOF"
        )
    if status == "NOT_PROVEN" and classification != "NOT_PROVEN":
        errors.append(
            "$.productProof.classification: NOT_PROVEN status requires NOT_PROVEN classification"
        )
    if status == "NOT_APPLICABLE" and classification != "NOT_APPLICABLE":
        errors.append(
            "$.productProof.classification: NOT_APPLICABLE status requires "
            "NOT_APPLICABLE classification"
        )
    return errors


def _validate_owner_gate(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["$.ownerGate: must be an object"]
    errors = _require_keys(value, ("required", "question", "reason"), "$.ownerGate")
    required = value.get("required")
    if "required" in value and not _is_bool(required):
        errors.append("$.ownerGate.required: must be boolean")
    for key in ("question", "reason"):
        if key not in value:
            continue
        item = value[key]
        if item is not None and (not _is_string(item) or not item.strip()):
            errors.append(f"$.ownerGate.{key}: must be null or a non-empty string")
    if required is True:
        for key in ("question", "reason"):
            item = value.get(key)
            if not _is_string(item) or not item.strip():
                errors.append(
                    f"$.ownerGate.{key}: required Owner gate needs a non-empty string"
                )
    elif required is False:
        for key in ("question", "reason"):
            if value.get(key) is not None:
                errors.append(f"$.ownerGate.{key}: must be null when required=false")
    return errors


def _validate_blocker(value: Any, state: Any, owner_gate: Any) -> list[str]:
    if state == "BLOCKED":
        if not isinstance(value, dict):
            return ["$.blocker: BLOCKED requires a blocker object"]
    else:
        if value is not None:
            return ["$.blocker: must be null unless state=BLOCKED"]
        return []

    assert isinstance(value, dict)
    errors = _require_keys(
        value,
        ("code", "detail", "ownerRequired", "pmRequired", "recoveryAllowedByWorker"),
        "$.blocker",
    )
    code = value.get("code")
    if "code" in value and (not _is_string(code) or not BLOCKER_CODE_RE.fullmatch(code)):
        errors.append("$.blocker.code: must match ^[A-Z][A-Z0-9_]{2,127}$")
    if "detail" in value:
        errors.extend(_validate_string(value["detail"], "$.blocker.detail"))
    for key in ("ownerRequired", "pmRequired", "recoveryAllowedByWorker"):
        if key in value and not _is_bool(value[key]):
            errors.append(f"$.blocker.{key}: must be boolean")
    if value.get("ownerRequired") is True:
        if not isinstance(owner_gate, dict) or owner_gate.get("required") is not True:
            errors.append(
                "$.ownerGate.required: must be true when blocker.ownerRequired=true"
            )
    return errors


def _validate_safety(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["$.safety: must be an object"]
    errors = _require_keys(value, ("readOnly", "ramWrites", "inputInjection"), "$.safety")
    if "readOnly" in value and not _is_bool(value["readOnly"]):
        errors.append("$.safety.readOnly: must be boolean")
    if "ramWrites" in value and (not _is_int(value["ramWrites"]) or value["ramWrites"] < 0):
        errors.append("$.safety.ramWrites: must be a non-negative integer")
    if "inputInjection" in value and not _is_bool(value["inputInjection"]):
        errors.append("$.safety.inputInjection: must be boolean")
    return errors


def validate_result(data: Any) -> list[str]:
    """Validate a parsed RESULT object and return stable, concise errors."""
    if not isinstance(data, dict):
        return ["$: result must be a JSON object"]

    errors = _require_keys(data, REQUIRED_TOP_LEVEL, "$")
    if "schema" in data and data["schema"] != SCHEMA_ID:
        errors.append(f"$.schema: expected {SCHEMA_ID!r}")

    if "stageId" in data:
        errors.extend(_validate_stage_id(data["stageId"]))
    if "dedupKey" in data:
        key = data["dedupKey"]
        if not _is_string(key) or not DEDUP_RE.fullmatch(key):
            errors.append("$.dedupKey: must match ^[a-z0-9][a-z0-9.-]{2,95}$")
    if "claimToken" in data:
        token = data["claimToken"]
        if not _is_string(token) or not (8 <= len(token) <= 256):
            errors.append("$.claimToken: must be a string of length 8..256")
    state = data.get("state")
    if "state" in data and state not in STATES:
        errors.append(
            f"$.state: unsupported value {state!r}; expected {'|'.join(STATES)}"
        )
    if "verdict" in data:
        errors.extend(_validate_string(data["verdict"], "$.verdict"))
    if "startCommit" in data:
        commit = data["startCommit"]
        if not _is_string(commit) or not SHA_RE.fullmatch(commit):
            errors.append("$.startCommit: must be a lowercase 40-hex commit SHA")
    if "implementationCommits" in data:
        errors.extend(
            _validate_string_list(
                data["implementationCommits"], "$.implementationCommits", sha=True
            )
        )
    if "integrationReady" in data and not _is_bool(data["integrationReady"]):
        errors.append("$.integrationReady: must be boolean")
    if "changedFiles" in data:
        errors.extend(_validate_string_list(data["changedFiles"], "$.changedFiles"))
    if "tests" in data:
        errors.extend(_validate_tests(data["tests"]))
    if "productProof" in data:
        errors.extend(_validate_product_proof(data["productProof"]))
    if "ownerGate" in data:
        errors.extend(_validate_owner_gate(data["ownerGate"]))
    if "nextAction" in data:
        errors.extend(_validate_string(data["nextAction"], "$.nextAction"))
    if "evidencePaths" in data:
        errors.extend(_validate_string_list(data["evidencePaths"], "$.evidencePaths"))
    if "safety" in data:
        errors.extend(_validate_safety(data["safety"]))

    if "blocker" in data and "state" in data:
        errors.extend(_validate_blocker(data["blocker"], state, data.get("ownerGate")))

    if state == "COMPLETE":
        implementation_commits = data.get("implementationCommits")
        if isinstance(implementation_commits, list) and not implementation_commits:
            errors.append("$.implementationCommits: COMPLETE requires at least one implementation commit")
        changed_files = data.get("changedFiles")
        if isinstance(changed_files, list) and not changed_files:
            errors.append("$.changedFiles: COMPLETE requires at least one materially changed file")
        tests = data.get("tests")
        if isinstance(tests, list):
            if not tests:
                errors.append("$.tests: COMPLETE requires terminal test evidence")
            else:
                results = [item.get("result") for item in tests if isinstance(item, dict)]
                if "FAIL" in results:
                    errors.append("$.tests: COMPLETE cannot contain FAIL")
                if "PASS" not in results:
                    errors.append("$.tests: COMPLETE requires at least one PASS")
        evidence_paths = data.get("evidencePaths")
        if isinstance(evidence_paths, list) and not evidence_paths:
            errors.append("$.evidencePaths: COMPLETE requires at least one evidence path")
        if data.get("integrationReady") is not True:
            errors.append("$.integrationReady: COMPLETE requires true")
        owner_gate = data.get("ownerGate")
        if isinstance(owner_gate, dict) and owner_gate.get("required") is True:
            errors.append("$.ownerGate.required: COMPLETE cannot leave an Owner gate open")
        product_proof = data.get("productProof")
        if isinstance(product_proof, dict) and product_proof.get("status") == "NOT_PROVEN":
            errors.append("$.productProof.status: COMPLETE cannot claim NOT_PROVEN product proof")
        if data.get("blocker") is not None:
            errors.append("$.blocker: COMPLETE requires null")

    return errors


def load_result(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _print_errors(errors: Sequence[str]) -> None:
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        data = load_result(args.path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR $: cannot read valid JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate_result(data)
    if args.expect_stage is not None:
        if not isinstance(data, dict) or data.get("stageId") != args.expect_stage:
            errors.append(
                f"$.stageId: expected command stageId {args.expect_stage!r}, "
                f"got {data.get('stageId') if isinstance(data, dict) else None!r}"
            )
    if errors:
        _print_errors(errors)
        return 1
    print(f"VALID {data['stageId']} {data['state']}")
    return 0


def _cmd_paths(args: argparse.Namespace) -> int:
    try:
        paths = result_paths(args.stage_id)
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    print(json.dumps(paths, separators=(",", ":"), sort_keys=True))
    return 0


def _cmd_verify_paths(args: argparse.Namespace) -> int:
    errors = verify_result_paths(args.stage_id, args.json_path, args.md_path)
    if errors:
        _print_errors(errors)
        return 1
    print(f"VALID_PATHS {args.stage_id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate a worker RESULT JSON")
    validate.add_argument("path")
    validate.add_argument("--expect-stage", dest="expect_stage")
    validate.set_defaults(func=_cmd_validate)

    paths = sub.add_parser("paths", help="derive deterministic RESULT paths")
    paths.add_argument("stage_id")
    paths.set_defaults(func=_cmd_paths)

    verify = sub.add_parser("verify-paths", help="verify deterministic RESULT paths")
    verify.add_argument("stage_id")
    verify.add_argument("json_path")
    verify.add_argument("md_path")
    verify.set_defaults(func=_cmd_verify_paths)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
