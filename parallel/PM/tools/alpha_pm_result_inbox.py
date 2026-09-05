#!/usr/bin/env python3
"""Read an immutable Alpha dispatch manifest and summarize worker RESULT.json files.

This helper is intentionally local-only: it performs no network access, never
invokes Git, and never mutates the checkout. Manifest errors fail closed.
Malformed/inconsistent worker results are reported as INVALID_RESULT.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


MANIFEST_SCHEMA = "wof-alpha-dispatch-manifest-v1"
INBOX_SCHEMA = "wof-alpha-pm-result-inbox-v1"
RESULT_PROTOCOL = "wof-alpha-worker-result-v1"

TERMINAL_STATES = {"SUBCOMPLETE", "COMPLETE", "BLOCKED"}
TEST_RESULTS = {"PASS", "FAIL", "NOT_RUN"}
PRODUCT_PROOF_STATES = {"PROVEN", "NOT_PROVEN", "NOT_APPLICABLE"}
PROOF_CLASSIFICATIONS = {
    "IMPLEMENTATION_PROOF",
    "MACHINE_DRAW_PROOF",
    "OWNER_VISUAL_PROOF",
    "NOT_PROVEN",
    "NOT_APPLICABLE",
}
PROVEN_CLASSIFICATIONS = {
    "IMPLEMENTATION_PROOF",
    "MACHINE_DRAW_PROOF",
    "OWNER_VISUAL_PROOF",
}
BLOCKER_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")

STAGE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,127}$")
DISPATCH_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,127}$")
DEDUP_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,95}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ManifestError(ValueError):
    """The dispatch manifest is unsafe, malformed, or internally inconsistent."""


class ResultError(ValueError):
    """A worker result exists but cannot be trusted as a valid terminal result."""


@dataclass(frozen=True)
class WorkerSpec:
    slot: int
    stage_id: str
    prompt_path: str
    dedup_key: str
    result_protocol: str
    result_json_path: str
    result_md_path: str
    terminal_commit_prefix: str


@dataclass(frozen=True)
class DispatchManifest:
    dispatch_id: str
    created_at_utc: str
    authority_commit: str
    workers: tuple[WorkerSpec, ...]


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(f"{label} must be an object")
    return value


def _require_result_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ResultError(f"{label} must be an object")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{label} must be a non-empty string")
    return value


def _require_result_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResultError(f"{label} must be a non-empty string")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise ResultError(f"{label} must be a boolean")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ResultError(f"{label} must be an array")
    items: list[str] = []
    for index, item in enumerate(value):
        items.append(_require_result_string(item, f"{label}[{index}]"))
    return items


def _canonical_repo_path(
    value: Any,
    label: str,
    *,
    required_prefix: tuple[str, ...] | None = None,
    suffix: str | None = None,
) -> str:
    path = _require_string(value, label)
    if "\\" in path:
        raise ManifestError(f"{label} must use repository-relative POSIX separators")
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts:
        raise ManifestError(f"{label} must not be absolute or contain path traversal")
    normalized = pure.as_posix()
    if normalized != path or "." in pure.parts:
        raise ManifestError(f"{label} must be a canonical repository-relative path")
    if required_prefix is not None and pure.parts[: len(required_prefix)] != required_prefix:
        prefix = "/".join(required_prefix) + "/"
        raise ManifestError(f"{label} must stay under {prefix}")
    if suffix is not None and not path.endswith(suffix):
        raise ManifestError(f"{label} must end with {suffix}")
    return path


def _validate_created_at_utc(value: Any) -> str:
    text = _require_string(value, "createdAtUtc")
    if not text.endswith("Z"):
        raise ManifestError("createdAtUtc must use UTC Z notation")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ManifestError("createdAtUtc must be valid ISO-8601 UTC") from exc
    if parsed.tzinfo != timezone.utc:
        raise ManifestError("createdAtUtc must be UTC")
    return text


def _parse_worker_basic(value: Any, index: int) -> WorkerSpec:
    worker = _require_mapping(value, f"workers[{index}]")
    expected_keys = {
        "slot",
        "stageId",
        "promptPath",
        "dedupKey",
        "resultProtocol",
        "resultJsonPath",
        "resultMdPath",
        "terminalCommitPrefix",
    }
    missing = expected_keys - set(worker)
    extra = set(worker) - expected_keys
    if missing:
        raise ManifestError(f"workers[{index}] missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise ManifestError(f"workers[{index}] unsupported fields: {', '.join(sorted(extra))}")

    slot = worker["slot"]
    if type(slot) is not int or slot < 1 or slot > 99:
        raise ManifestError(f"workers[{index}].slot must be an integer from 1 to 99")

    stage_id = _require_string(worker["stageId"], f"workers[{index}].stageId")
    if not STAGE_ID_RE.fullmatch(stage_id):
        raise ManifestError(f"workers[{index}].stageId is malformed")

    prompt_path = _canonical_repo_path(
        worker["promptPath"],
        f"workers[{index}].promptPath",
        required_prefix=("parallel", "PM"),
        suffix=".md",
    )

    dedup_key = _require_string(worker["dedupKey"], f"workers[{index}].dedupKey")
    if not DEDUP_KEY_RE.fullmatch(dedup_key):
        raise ManifestError(f"workers[{index}].dedupKey is malformed")

    result_protocol = _require_string(
        worker["resultProtocol"], f"workers[{index}].resultProtocol"
    )
    if result_protocol != RESULT_PROTOCOL:
        raise ManifestError(
            f"workers[{index}].resultProtocol must be {RESULT_PROTOCOL!r}"
        )

    result_json_path = _canonical_repo_path(
        worker["resultJsonPath"],
        f"workers[{index}].resultJsonPath",
        required_prefix=("parallel", "PM", "RESULTS"),
        suffix=".json",
    )
    result_md_path = _canonical_repo_path(
        worker["resultMdPath"],
        f"workers[{index}].resultMdPath",
        required_prefix=("parallel", "PM", "RESULTS"),
        suffix=".md",
    )
    terminal_prefix = _require_string(
        worker["terminalCommitPrefix"], f"workers[{index}].terminalCommitPrefix"
    )

    return WorkerSpec(
        slot=slot,
        stage_id=stage_id,
        prompt_path=prompt_path,
        dedup_key=dedup_key,
        result_protocol=result_protocol,
        result_json_path=result_json_path,
        result_md_path=result_md_path,
        terminal_commit_prefix=terminal_prefix,
    )


def parse_manifest_payload(payload: Any) -> DispatchManifest:
    root = _require_mapping(payload, "manifest")
    expected_keys = {
        "schema",
        "dispatchId",
        "createdAtUtc",
        "authorityCommit",
        "immutable",
        "workers",
    }
    missing = expected_keys - set(root)
    extra = set(root) - expected_keys
    if missing:
        raise ManifestError(f"manifest missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise ManifestError(f"manifest unsupported fields: {', '.join(sorted(extra))}")

    if root["schema"] != MANIFEST_SCHEMA:
        raise ManifestError(f"schema must be {MANIFEST_SCHEMA!r}")

    dispatch_id = _require_string(root["dispatchId"], "dispatchId")
    if not DISPATCH_ID_RE.fullmatch(dispatch_id):
        raise ManifestError("dispatchId is malformed")

    created_at_utc = _validate_created_at_utc(root["createdAtUtc"])

    authority_commit = _require_string(root["authorityCommit"], "authorityCommit")
    if not SHA_RE.fullmatch(authority_commit):
        raise ManifestError("authorityCommit must be a full 40-character lowercase Git SHA")

    if root["immutable"] is not True:
        raise ManifestError("immutable must be true")

    raw_workers = root["workers"]
    if not isinstance(raw_workers, list) or not raw_workers:
        raise ManifestError("workers must be a non-empty array")

    workers = [_parse_worker_basic(item, index) for index, item in enumerate(raw_workers)]

    def reject_duplicate(values: Iterable[Any], label: str) -> None:
        seen: set[Any] = set()
        for value in values:
            if value in seen:
                raise ManifestError(f"duplicate {label}: {value}")
            seen.add(value)

    reject_duplicate((w.slot for w in workers), "slot")
    reject_duplicate((w.stage_id for w in workers), "stageId")
    reject_duplicate((w.result_json_path for w in workers), "resultJsonPath")
    reject_duplicate((w.result_md_path for w in workers), "resultMdPath")

    for worker in workers:
        expected_json = f"parallel/PM/RESULTS/{worker.stage_id}_RESULT.json"
        expected_md = f"parallel/PM/RESULTS/{worker.stage_id}_RESULT.md"
        expected_prefix = f"WORKER_RESULT {worker.stage_id}"
        if worker.result_json_path != expected_json:
            raise ManifestError(
                f"{worker.stage_id} resultJsonPath must be deterministic: {expected_json}"
            )
        if worker.result_md_path != expected_md:
            raise ManifestError(
                f"{worker.stage_id} resultMdPath must be deterministic: {expected_md}"
            )
        if worker.terminal_commit_prefix != expected_prefix:
            raise ManifestError(
                f"{worker.stage_id} terminalCommitPrefix must be {expected_prefix!r}"
            )

    workers.sort(key=lambda item: item.slot)
    return DispatchManifest(
        dispatch_id=dispatch_id,
        created_at_utc=created_at_utc,
        authority_commit=authority_commit,
        workers=tuple(workers),
    )


def _within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def _resolve_manifest_path(repo_root: Path, manifest_path: Path) -> Path:
    root = repo_root.resolve()
    candidate = manifest_path if manifest_path.is_absolute() else root / manifest_path
    resolved = candidate.resolve()
    if not _within(root, resolved):
        raise ManifestError("manifest path resolves outside repo root")
    return resolved


def _resolve_result_path(repo_root: Path, repo_relative: str) -> Path:
    # Lexical validation already happened while parsing the manifest; resolve again
    # so a symlink cannot escape the intended RESULTS directory.
    root = repo_root.resolve()
    results_root = (root / "parallel" / "PM" / "RESULTS").resolve()
    pure = PurePosixPath(repo_relative)
    candidate = root.joinpath(*pure.parts).resolve()
    if not _within(results_root, candidate):
        raise ManifestError(
            f"declared result path resolves outside parallel/PM/RESULTS/: {repo_relative}"
        )
    return candidate


def load_manifest(repo_root: Path, manifest_path: Path) -> tuple[DispatchManifest, Path]:
    root = repo_root.resolve()
    if not root.is_dir():
        raise ManifestError(f"repo root is not a directory: {root}")
    resolved_manifest = _resolve_manifest_path(root, manifest_path)
    try:
        payload = json.loads(resolved_manifest.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ManifestError(f"cannot read manifest: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest is not valid JSON: {exc.msg}") from exc
    manifest = parse_manifest_payload(payload)

    # Resolve every declared result path before reading any result. This makes
    # traversal/symlink escapes a manifest-level fail-closed condition.
    for worker in manifest.workers:
        _resolve_result_path(root, worker.result_json_path)
        _resolve_result_path(root, worker.result_md_path)
    return manifest, resolved_manifest


def _nullable_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _require_result_string(value, label)


def _validate_tests(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ResultError("tests must be an array")
    tests: list[dict[str, str]] = []
    for index, raw_test in enumerate(value):
        test = _require_result_mapping(raw_test, f"tests[{index}]")
        for key in ("name", "result", "detail"):
            if key not in test:
                raise ResultError(f"tests[{index}] missing field: {key}")
        name = _require_result_string(test["name"], f"tests[{index}].name")
        result = _require_result_string(test["result"], f"tests[{index}].result")
        detail = _require_result_string(test["detail"], f"tests[{index}].detail")
        if result not in TEST_RESULTS:
            raise ResultError(
                f"tests[{index}].result must be PASS, FAIL, or NOT_RUN"
            )
        tests.append({"name": name, "result": result, "detail": detail})
    return tests


def _validate_product_proof(value: Any) -> dict[str, str]:
    proof = _require_result_mapping(value, "productProof")
    for key in ("status", "classification", "detail"):
        if key not in proof:
            raise ResultError(f"productProof missing field: {key}")
    status = _require_result_string(proof["status"], "productProof.status")
    classification = _require_result_string(
        proof["classification"], "productProof.classification"
    )
    detail = _require_result_string(proof["detail"], "productProof.detail")
    if status not in PRODUCT_PROOF_STATES:
        raise ResultError(
            "productProof.status must be PROVEN, NOT_PROVEN, or NOT_APPLICABLE"
        )
    if classification not in PROOF_CLASSIFICATIONS:
        raise ResultError("productProof.classification is unsupported")
    if status == "PROVEN" and classification not in PROVEN_CLASSIFICATIONS:
        raise ResultError(
            "PROVEN productProof requires IMPLEMENTATION_PROOF, "
            "MACHINE_DRAW_PROOF, or OWNER_VISUAL_PROOF classification"
        )
    if status == "NOT_PROVEN" and classification != "NOT_PROVEN":
        raise ResultError(
            "NOT_PROVEN productProof requires NOT_PROVEN classification"
        )
    if status == "NOT_APPLICABLE" and classification != "NOT_APPLICABLE":
        raise ResultError(
            "NOT_APPLICABLE productProof requires NOT_APPLICABLE classification"
        )
    return {
        "status": status,
        "classification": classification,
        "detail": detail,
    }


def _validate_owner_gate(value: Any) -> dict[str, Any]:
    gate = _require_result_mapping(value, "ownerGate")
    for key in ("required", "question", "reason"):
        if key not in gate:
            raise ResultError(f"ownerGate missing field: {key}")
    required = _require_bool(gate["required"], "ownerGate.required")
    question = _nullable_string(gate["question"], "ownerGate.question")
    reason = _nullable_string(gate["reason"], "ownerGate.reason")
    if required:
        if question is None or reason is None:
            raise ResultError(
                "ownerGate.question and ownerGate.reason must be set when required is true"
            )
    elif question is not None or reason is not None:
        raise ResultError(
            "ownerGate.question and ownerGate.reason must be null when required is false"
        )
    return {"required": required, "question": question, "reason": reason}


def _validate_blocker(value: Any, state: str) -> dict[str, Any] | None:
    if value is None:
        if state == "BLOCKED":
            raise ResultError("BLOCKED result requires blocker object")
        return None
    if state != "BLOCKED":
        raise ResultError("blocker must be null unless state is BLOCKED")
    blocker = _require_result_mapping(value, "blocker")
    required_fields = (
        "code",
        "detail",
        "ownerRequired",
        "pmRequired",
        "recoveryAllowedByWorker",
    )
    for key in required_fields:
        if key not in blocker:
            raise ResultError(f"blocker missing field: {key}")
    code = _require_result_string(blocker["code"], "blocker.code")
    if not BLOCKER_CODE_RE.fullmatch(code):
        raise ResultError("blocker.code must match ^[A-Z][A-Z0-9_]{2,127}$")
    return {
        "code": code,
        "detail": _require_result_string(blocker["detail"], "blocker.detail"),
        "ownerRequired": _require_bool(
            blocker["ownerRequired"], "blocker.ownerRequired"
        ),
        "pmRequired": _require_bool(blocker["pmRequired"], "blocker.pmRequired"),
        "recoveryAllowedByWorker": _require_bool(
            blocker["recoveryAllowedByWorker"], "blocker.recoveryAllowedByWorker"
        ),
    }


def _validate_safety(value: Any) -> dict[str, Any]:
    safety = _require_result_mapping(value, "safety")
    for key in ("readOnly", "ramWrites", "inputInjection"):
        if key not in safety:
            raise ResultError(f"safety missing field: {key}")
    read_only = _require_bool(safety["readOnly"], "safety.readOnly")
    ram_writes = safety["ramWrites"]
    if type(ram_writes) is not int or ram_writes < 0:
        raise ResultError("safety.ramWrites must be a non-negative integer")
    input_injection = _require_bool(
        safety["inputInjection"], "safety.inputInjection"
    )
    return {
        "readOnly": read_only,
        "ramWrites": ram_writes,
        "inputInjection": input_injection,
    }


def validate_result_payload(payload: Any, worker: WorkerSpec) -> dict[str, Any]:
    result = _require_result_mapping(payload, "result")
    required = (
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
    for key in required:
        if key not in result:
            raise ResultError(f"result missing field: {key}")

    if result["schema"] != worker.result_protocol:
        raise ResultError(
            f"unsupported result protocol: expected {worker.result_protocol!r}"
        )
    if result["stageId"] != worker.stage_id:
        raise ResultError(
            f"stageId mismatch: expected {worker.stage_id!r}, got {result['stageId']!r}"
        )
    if result["dedupKey"] != worker.dedup_key:
        raise ResultError(
            f"dedupKey mismatch: expected {worker.dedup_key!r}, got {result['dedupKey']!r}"
        )

    claim_token = _require_result_string(result["claimToken"], "claimToken")
    if not 8 <= len(claim_token) <= 256:
        raise ResultError("claimToken must be 8..256 characters")
    state = _require_result_string(result["state"], "state")
    if state not in TERMINAL_STATES:
        raise ResultError(
            "unsupported result state: expected SUBCOMPLETE, COMPLETE, or BLOCKED"
        )

    verdict = _require_result_string(result["verdict"], "verdict")
    start_commit = _require_result_string(result["startCommit"], "startCommit")
    if not SHA_RE.fullmatch(start_commit):
        raise ResultError("startCommit must be a lowercase 40-hex Git SHA")
    implementation_commits = _require_string_list(
        result["implementationCommits"], "implementationCommits"
    )
    if len(set(implementation_commits)) != len(implementation_commits):
        raise ResultError("implementationCommits must not contain duplicates")
    for commit in implementation_commits:
        if not SHA_RE.fullmatch(commit):
            raise ResultError(
                "implementationCommits entries must be lowercase 40-hex Git SHAs"
            )
    integration_ready = _require_bool(result["integrationReady"], "integrationReady")
    changed_files = _require_string_list(result["changedFiles"], "changedFiles")
    if len(set(changed_files)) != len(changed_files):
        raise ResultError("changedFiles must not contain duplicates")
    tests = _validate_tests(result["tests"])
    product_proof = _validate_product_proof(result["productProof"])
    owner_gate = _validate_owner_gate(result["ownerGate"])
    blocker = _validate_blocker(result["blocker"], state)
    next_action = _require_result_string(result["nextAction"], "nextAction")
    evidence_paths = _require_string_list(result["evidencePaths"], "evidencePaths")
    if len(set(evidence_paths)) != len(evidence_paths):
        raise ResultError("evidencePaths must not contain duplicates")
    safety = _validate_safety(result["safety"])

    if state == "COMPLETE":
        if not implementation_commits:
            raise ResultError("COMPLETE requires at least one implementation commit")
        if not changed_files:
            raise ResultError("COMPLETE requires at least one materially changed file")
        if not tests:
            raise ResultError("COMPLETE requires terminal test evidence")
        test_results = [item["result"] for item in tests]
        if "FAIL" in test_results:
            raise ResultError("COMPLETE cannot contain FAIL test evidence")
        if "PASS" not in test_results:
            raise ResultError("COMPLETE requires at least one PASS test")
        if not evidence_paths:
            raise ResultError("COMPLETE requires at least one evidence path")
        if integration_ready is not True:
            raise ResultError("COMPLETE requires integrationReady=true")
        if owner_gate["required"] is True:
            raise ResultError("COMPLETE cannot leave an Owner gate open")
        if product_proof["status"] == "NOT_PROVEN":
            raise ResultError("COMPLETE cannot use productProof.status=NOT_PROVEN")
        if blocker is not None:
            raise ResultError("COMPLETE requires blocker=null")

    return {
        "schema": worker.result_protocol,
        "stageId": worker.stage_id,
        "dedupKey": worker.dedup_key,
        "claimToken": claim_token,
        "state": state,
        "verdict": verdict,
        "startCommit": start_commit,
        "implementationCommits": implementation_commits,
        "integrationReady": integration_ready,
        "changedFiles": changed_files,
        "tests": tests,
        "productProof": product_proof,
        "ownerGate": owner_gate,
        "blocker": blocker,
        "nextAction": next_action,
        "evidencePaths": evidence_paths,
        "safety": safety,
    }


def _tests_summary(tests: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    counts = {key: 0 for key in ("PASS", "FAIL", "NOT_RUN")}
    items: list[dict[str, str]] = []
    for test in tests:
        result = test["result"]
        counts[result] += 1
        items.append(
            {"name": test["name"], "result": result, "detail": test["detail"]}
        )
    return {
        "total": len(tests),
        "PASS": counts["PASS"],
        "FAIL": counts["FAIL"],
        "NOT_RUN": counts["NOT_RUN"],
        "items": items,
    }


def _base_worker_summary(worker: WorkerSpec, state: str) -> dict[str, Any]:
    return {
        "slot": worker.slot,
        "stageId": worker.stage_id,
        "state": state,
        "verdict": None,
        "integrationReady": False,
        "implementationCommits": [],
        "changedFiles": [],
        "tests": {
            "total": 0,
            "PASS": 0,
            "FAIL": 0,
            "NOT_RUN": 0,
            "items": [],
        },
        "productProof": {"status": None},
        "ownerGate": {"required": False, "question": None},
        "blocker": None,
        "nextAction": None,
        "resultJsonPath": worker.result_json_path,
        "resultMdPath": worker.result_md_path,
    }


def _not_finished_summary(worker: WorkerSpec) -> dict[str, Any]:
    summary = _base_worker_summary(worker, "NOT_FINISHED")
    summary["nextAction"] = (
        f"Wait for terminal result JSON at {worker.result_json_path}; do not infer from chat."
    )
    return summary


def _invalid_result_summary(worker: WorkerSpec, error: str) -> dict[str, Any]:
    summary = _base_worker_summary(worker, "INVALID_RESULT")
    summary["blocker"] = {
        "code": "INVALID_RESULT",
        "ownerRequired": False,
        "pmRequired": True,
    }
    summary["nextAction"] = (
        "PM must reject this result and route repair under the worker/result authority."
    )
    summary["validationErrors"] = [error]
    return summary


def _terminal_summary(worker: WorkerSpec, result: Mapping[str, Any]) -> dict[str, Any]:
    blocker = result["blocker"]
    summary = _base_worker_summary(worker, result["state"])
    summary.update(
        {
            "verdict": result["verdict"],
            "integrationReady": result["integrationReady"],
            "implementationCommits": list(result["implementationCommits"]),
            "changedFiles": list(result["changedFiles"]),
            "tests": _tests_summary(result["tests"]),
            "productProof": {
                "status": result["productProof"]["status"],
                "detail": result["productProof"]["detail"],
            },
            "ownerGate": {
                "required": result["ownerGate"]["required"],
                "question": result["ownerGate"]["question"],
            },
            "blocker": (
                None
                if blocker is None
                else {
                    "code": blocker["code"],
                    "ownerRequired": blocker["ownerRequired"],
                    "pmRequired": blocker["pmRequired"],
                }
            ),
            "nextAction": result["nextAction"],
        }
    )
    return summary


def _read_worker_result(repo_root: Path, worker: WorkerSpec) -> dict[str, Any]:
    path = _resolve_result_path(repo_root, worker.result_json_path)
    if not path.exists():
        return _not_finished_summary(worker)
    if not path.is_file():
        return _invalid_result_summary(worker, "declared result JSON is not a regular file")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return _invalid_result_summary(worker, f"cannot read result JSON: {exc}")
    except json.JSONDecodeError as exc:
        return _invalid_result_summary(
            worker, f"result JSON is malformed: {exc.msg}"
        )
    try:
        result = validate_result_payload(payload, worker)
    except ResultError as exc:
        return _invalid_result_summary(worker, str(exc))
    return _terminal_summary(worker, result)


def build_inbox_summary(
    repo_root: Path,
    manifest_path: Path,
    *,
    slots: Sequence[int] | None = None,
) -> dict[str, Any]:
    root = repo_root.resolve()
    manifest, resolved_manifest = load_manifest(root, manifest_path)

    selected_workers = list(manifest.workers)
    if slots is not None:
        if not slots:
            raise ManifestError("slots selection must not be empty")
        if any(type(slot) is not int or slot < 1 for slot in slots):
            raise ManifestError("slots must be positive integers")
        if len(set(slots)) != len(slots):
            raise ManifestError("slots selection contains duplicates")
        available = {worker.slot for worker in manifest.workers}
        missing = sorted(set(slots) - available)
        if missing:
            raise ManifestError(
                "requested slot(s) not declared by manifest: "
                + ", ".join(str(item) for item in missing)
            )
        selected = set(slots)
        selected_workers = [w for w in manifest.workers if w.slot in selected]

    worker_summaries = [_read_worker_result(root, worker) for worker in selected_workers]
    state_order = (
        "COMPLETE",
        "SUBCOMPLETE",
        "BLOCKED",
        "NOT_FINISHED",
        "INVALID_RESULT",
    )
    counts = {state: 0 for state in state_order}
    for summary in worker_summaries:
        counts[summary["state"]] += 1

    try:
        manifest_display = resolved_manifest.relative_to(root).as_posix()
    except ValueError:
        manifest_display = str(resolved_manifest)

    return {
        "schema": INBOX_SCHEMA,
        "dispatchId": manifest.dispatch_id,
        "authorityCommit": manifest.authority_commit,
        "manifestPath": manifest_display,
        "selectedSlots": [worker.slot for worker in selected_workers],
        "counts": counts,
        "allResultsValid": counts["INVALID_RESULT"] == 0,
        "allWorkersTerminal": (
            counts["NOT_FINISHED"] == 0 and counts["INVALID_RESULT"] == 0
        ),
        "workers": worker_summaries,
    }


def _error_payload(detail: str) -> dict[str, str]:
    return {
        "schema": INBOX_SCHEMA,
        "error": "MANIFEST_INVALID",
        "detail": detail,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="immutable dispatch manifest path")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="local checkout root (default: current directory)",
    )
    parser.add_argument(
        "--slots",
        type=int,
        nargs="+",
        help="optional manifest slot numbers, e.g. --slots 1 3",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON instead of the default compact one-line form",
    )
    args = parser.parse_args(argv)

    try:
        summary = build_inbox_summary(
            args.repo_root, args.manifest, slots=args.slots
        )
    except ManifestError as exc:
        print(
            json.dumps(
                _error_payload(str(exc)),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2

    if args.pretty:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))

    return 1 if summary["counts"]["INVALID_RESULT"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
