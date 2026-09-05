#!/usr/bin/env python3
"""Resolve a PM-owned current-dispatch pointer into C2 worker RESULT truth.

The resolver is coordination-only and local-only. It never mutates the checkout,
invokes Git, or infers worker state from chat/claims/commit messages/Markdown.
Pointer/manifest identity failures are fail-closed; worker RESULT semantics are
delegated to alpha_pm_result_inbox (C2).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

import alpha_pm_result_inbox as inbox


POINTER_SCHEMA = "wof-alpha-current-dispatch-v1"
RESOLUTION_SCHEMA = "wof-alpha-current-dispatch-resolution-v1"
DEFAULT_POINTER_PATH = Path("parallel/PM/CURRENT_DISPATCH.json")
DEFAULT_REPOSITORY = "ouyong520/wof-ai-private"
MANIFEST_PREFIX = ("parallel", "PM", "DISPATCH_MANIFESTS")

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
DISPATCH_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,127}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class CurrentDispatchError(ValueError):
    """The current-dispatch pointer or its manifest identity is not trustworthy."""


@dataclass(frozen=True)
class PreviousDispatch:
    dispatch_id: str
    manifest_path: str
    manifest_authority_commit: str
    manifest_sha256: str
    revision: int


@dataclass(frozen=True)
class CurrentDispatchPointer:
    repository: str
    dispatch_id: str
    manifest_path: str
    manifest_authority_commit: str
    manifest_sha256: str
    updated_at_utc: str
    revision: int
    previous_dispatch: PreviousDispatch | None


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise CurrentDispatchError(f"{label} must be an object")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CurrentDispatchError(f"{label} must be a non-empty string")
    return value


def _require_revision(value: Any, label: str) -> int:
    if type(value) is not int or value < 1:
        raise CurrentDispatchError(f"{label} must be an integer >= 1")
    return value


def _validate_utc(value: Any, label: str) -> str:
    text = _require_string(value, label)
    if not text.endswith("Z"):
        raise CurrentDispatchError(f"{label} must use UTC Z notation")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise CurrentDispatchError(f"{label} must be valid ISO-8601 UTC") from exc
    if parsed.tzinfo != timezone.utc:
        raise CurrentDispatchError(f"{label} must be UTC")
    return text


def _validate_dispatch_id(value: Any, label: str = "dispatchId") -> str:
    text = _require_string(value, label)
    if not DISPATCH_ID_RE.fullmatch(text):
        raise CurrentDispatchError(f"{label} is malformed")
    return text


def _validate_repository(value: Any) -> str:
    text = _require_string(value, "repository")
    if not REPOSITORY_RE.fullmatch(text):
        raise CurrentDispatchError("repository must be owner/name")
    return text


def _validate_sha(value: Any, label: str) -> str:
    text = _require_string(value, label)
    if not SHA_RE.fullmatch(text):
        raise CurrentDispatchError(f"{label} must be a lowercase 40-hex Git SHA")
    return text


def _validate_sha256(value: Any, label: str) -> str:
    text = _require_string(value, label)
    if not SHA256_RE.fullmatch(text):
        raise CurrentDispatchError(f"{label} must be a lowercase 64-hex SHA-256")
    return text


def _validate_manifest_path(value: Any, dispatch_id: str, label: str = "manifestPath") -> str:
    text = _require_string(value, label)
    if "\\" in text:
        raise CurrentDispatchError(f"{label} must use repository-relative POSIX separators")
    pure = PurePosixPath(text)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise CurrentDispatchError(f"{label} must not be absolute or contain traversal")
    if pure.as_posix() != text:
        raise CurrentDispatchError(f"{label} must be canonical")
    if pure.parts[: len(MANIFEST_PREFIX)] != MANIFEST_PREFIX:
        raise CurrentDispatchError(
            f"{label} must stay under parallel/PM/DISPATCH_MANIFESTS/"
        )
    if len(pure.parts) != len(MANIFEST_PREFIX) + 1:
        raise CurrentDispatchError(f"{label} must name one manifest file directly")
    expected_name = f"{dispatch_id}.json"
    if pure.name != expected_name:
        raise CurrentDispatchError(
            f"{label} must be exact dispatch identity path ending in {expected_name}"
        )
    return text


def _parse_previous(value: Any, current_revision: int) -> PreviousDispatch | None:
    if value is None:
        return None
    previous = _require_mapping(value, "previousDispatch")
    expected = {
        "dispatchId",
        "manifestPath",
        "manifestAuthorityCommit",
        "manifestSha256",
        "revision",
    }
    missing = expected - set(previous)
    extra = set(previous) - expected
    if missing:
        raise CurrentDispatchError(
            "previousDispatch missing fields: " + ", ".join(sorted(missing))
        )
    if extra:
        raise CurrentDispatchError(
            "previousDispatch unsupported fields: " + ", ".join(sorted(extra))
        )
    dispatch_id = _validate_dispatch_id(previous["dispatchId"], "previousDispatch.dispatchId")
    revision = _require_revision(previous["revision"], "previousDispatch.revision")
    if revision >= current_revision:
        raise CurrentDispatchError("previousDispatch.revision must be less than revision")
    return PreviousDispatch(
        dispatch_id=dispatch_id,
        manifest_path=_validate_manifest_path(
            previous["manifestPath"], dispatch_id, "previousDispatch.manifestPath"
        ),
        manifest_authority_commit=_validate_sha(
            previous["manifestAuthorityCommit"],
            "previousDispatch.manifestAuthorityCommit",
        ),
        manifest_sha256=_validate_sha256(
            previous["manifestSha256"], "previousDispatch.manifestSha256"
        ),
        revision=revision,
    )


def parse_pointer_payload(payload: Any) -> CurrentDispatchPointer:
    root = _require_mapping(payload, "pointer")
    required = {
        "schema",
        "pmOwned",
        "repository",
        "dispatchId",
        "manifestPath",
        "manifestAuthorityCommit",
        "manifestSha256",
        "updatedAtUtc",
        "revision",
    }
    optional = {"previousDispatch"}
    missing = required - set(root)
    extra = set(root) - required - optional
    if missing:
        raise CurrentDispatchError(
            "pointer missing fields: " + ", ".join(sorted(missing))
        )
    if extra:
        raise CurrentDispatchError(
            "pointer unsupported fields: " + ", ".join(sorted(extra))
        )
    if root["schema"] != POINTER_SCHEMA:
        raise CurrentDispatchError(f"schema must be {POINTER_SCHEMA!r}")
    if root["pmOwned"] is not True:
        raise CurrentDispatchError("pmOwned must be true")

    repository = _validate_repository(root["repository"])
    dispatch_id = _validate_dispatch_id(root["dispatchId"])
    revision = _require_revision(root["revision"], "revision")
    pointer = CurrentDispatchPointer(
        repository=repository,
        dispatch_id=dispatch_id,
        manifest_path=_validate_manifest_path(root["manifestPath"], dispatch_id),
        manifest_authority_commit=_validate_sha(
            root["manifestAuthorityCommit"], "manifestAuthorityCommit"
        ),
        manifest_sha256=_validate_sha256(root["manifestSha256"], "manifestSha256"),
        updated_at_utc=_validate_utc(root["updatedAtUtc"], "updatedAtUtc"),
        revision=revision,
        previous_dispatch=_parse_previous(root.get("previousDispatch"), revision),
    )
    if (
        pointer.previous_dispatch is not None
        and pointer.previous_dispatch.dispatch_id == pointer.dispatch_id
    ):
        raise CurrentDispatchError("previousDispatch.dispatchId must differ from dispatchId")
    return pointer


def _within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def _resolve_pointer_path(repo_root: Path, pointer_path: Path) -> Path:
    root = repo_root.resolve()
    if not root.is_dir():
        raise CurrentDispatchError(f"repo root is not a directory: {root}")

    if pointer_path.is_absolute():
        candidate = pointer_path.resolve()
    else:
        pure = PurePosixPath(pointer_path.as_posix())
        if ".." in pure.parts or "." in pure.parts:
            raise CurrentDispatchError("pointer path must not contain traversal")
        candidate = root.joinpath(*pure.parts).resolve()
    if not _within(root, candidate):
        raise CurrentDispatchError("pointer path resolves outside repo root")
    return candidate


def load_pointer(repo_root: Path, pointer_path: Path) -> tuple[CurrentDispatchPointer, Path]:
    resolved = _resolve_pointer_path(repo_root, pointer_path)
    try:
        raw = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise CurrentDispatchError(f"cannot read current-dispatch pointer: {exc}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CurrentDispatchError(
            f"current-dispatch pointer is not valid JSON: {exc.msg}"
        ) from exc
    return parse_pointer_payload(payload), resolved


def _resolve_exact_manifest(repo_root: Path, pointer: CurrentDispatchPointer) -> Path:
    root = repo_root.resolve()
    manifest_root = root.joinpath(*MANIFEST_PREFIX).resolve()
    pure = PurePosixPath(pointer.manifest_path)
    candidate = root.joinpath(*pure.parts).resolve()
    if not _within(manifest_root, candidate):
        raise CurrentDispatchError(
            "manifestPath resolves outside parallel/PM/DISPATCH_MANIFESTS/"
        )
    try:
        data = candidate.read_bytes()
    except OSError as exc:
        raise CurrentDispatchError(f"cannot read exact manifest: {exc}") from exc
    digest = hashlib.sha256(data).hexdigest()
    if digest != pointer.manifest_sha256:
        raise CurrentDispatchError(
            "manifestSha256 mismatch: pointer target is stale or redirected"
        )
    return candidate


def _pm_action(summary: Mapping[str, Any]) -> str:
    counts = summary["counts"]
    if counts["INVALID_RESULT"]:
        return "REJECT_INVALID_RESULT"
    if counts["BLOCKED"]:
        return "REVIEW_BLOCKER"
    if counts["NOT_FINISHED"]:
        return "WAIT_FOR_EXACT_RESULT_JSON"
    if counts["SUBCOMPLETE"]:
        return "REVIEW_SUBCOMPLETE_NEXT_ACTION"
    return "CONTINUE_FROM_COMPLETE_RESULTS"


def resolve_current_dispatch(
    repo_root: Path,
    pointer_path: Path = DEFAULT_POINTER_PATH,
    *,
    slots: Sequence[int] | None = None,
    expected_repository: str = DEFAULT_REPOSITORY,
) -> dict[str, Any]:
    root = repo_root.resolve()
    pointer, resolved_pointer = load_pointer(root, pointer_path)
    if pointer.repository != expected_repository:
        raise CurrentDispatchError(
            f"repository mismatch: expected {expected_repository!r}, got {pointer.repository!r}"
        )

    resolved_manifest = _resolve_exact_manifest(root, pointer)
    try:
        manifest, c2_manifest_path = inbox.load_manifest(root, Path(pointer.manifest_path))
    except inbox.ManifestError as exc:
        raise CurrentDispatchError(f"manifest invalid: {exc}") from exc

    if manifest.dispatch_id != pointer.dispatch_id:
        raise CurrentDispatchError(
            f"dispatchId mismatch: pointer={pointer.dispatch_id!r}, manifest={manifest.dispatch_id!r}"
        )
    if manifest.authority_commit != pointer.manifest_authority_commit:
        raise CurrentDispatchError(
            "manifestAuthorityCommit mismatch: pointer target identity is stale or redirected"
        )
    if c2_manifest_path.resolve() != resolved_manifest:
        raise CurrentDispatchError("manifest path identity changed during resolution")

    try:
        inbox_summary = inbox.build_inbox_summary(
            root, Path(pointer.manifest_path), slots=slots
        )
    except inbox.ManifestError as exc:
        raise CurrentDispatchError(f"manifest/selection invalid: {exc}") from exc

    try:
        pointer_display = resolved_pointer.relative_to(root).as_posix()
    except ValueError:
        pointer_display = str(resolved_pointer)

    return {
        "schema": RESOLUTION_SCHEMA,
        "repository": pointer.repository,
        "pointerPath": pointer_display,
        "pointerRevision": pointer.revision,
        "pointerUpdatedAtUtc": pointer.updated_at_utc,
        "dispatchId": pointer.dispatch_id,
        "manifestPath": pointer.manifest_path,
        "manifestAuthorityCommit": pointer.manifest_authority_commit,
        "manifestSha256": pointer.manifest_sha256,
        "selectedSlots": inbox_summary["selectedSlots"],
        "counts": inbox_summary["counts"],
        "allResultsValid": inbox_summary["allResultsValid"],
        "allWorkersTerminal": inbox_summary["allWorkersTerminal"],
        "pmAction": _pm_action(inbox_summary),
        "workers": inbox_summary["workers"],
    }


def _error_payload(detail: str) -> dict[str, str]:
    return {
        "schema": RESOLUTION_SCHEMA,
        "error": "CURRENT_DISPATCH_INVALID",
        "detail": detail,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pointer",
        type=Path,
        nargs="?",
        default=DEFAULT_POINTER_PATH,
        help=(
            "PM-owned pointer path (default: parallel/PM/CURRENT_DISPATCH.json)"
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="local checkout root (default: current directory)",
    )
    parser.add_argument(
        "--repository",
        default=DEFAULT_REPOSITORY,
        help=f"expected repository identity (default: {DEFAULT_REPOSITORY})",
    )
    parser.add_argument(
        "--slots",
        type=int,
        nargs="+",
        help="optional C2 manifest slots, e.g. --slots 1 3",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON instead of compact one-line JSON",
    )
    args = parser.parse_args(argv)

    try:
        summary = resolve_current_dispatch(
            args.repo_root,
            args.pointer,
            slots=args.slots,
            expected_repository=args.repository,
        )
    except CurrentDispatchError as exc:
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
