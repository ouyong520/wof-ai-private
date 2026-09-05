#!/usr/bin/env python3
"""Plan and verify PM-owned CURRENT_DISPATCH transitions without writing the live pointer.

C7 intentionally keeps the live pointer PM/coordinator-owned.  This tool validates
an immutable C2/C3 dispatch manifest, validates any existing pointer through C5,
derives the next revision/history entry, renders exact deterministic pointer bytes,
and emits byte-hash guards a PM can check immediately before/after its own write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

import alpha_pm_current_dispatch as current
import alpha_pm_result_inbox as inbox
import alpha_worker_dispatch_contract as contract


PLAN_SCHEMA = "wof-alpha-current-dispatch-activation-plan-v1"
VERIFY_SCHEMA = "wof-alpha-current-dispatch-activation-verification-v1"
GUARD_SCHEMA = "wof-alpha-current-dispatch-write-guard-v1"
DEFAULT_POINTER_PATH = Path("parallel/PM/CURRENT_DISPATCH.json")
DEFAULT_REPOSITORY = current.DEFAULT_REPOSITORY
MANIFEST_PREFIX = ("parallel", "PM", "DISPATCH_MANIFESTS")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ActivationError(ValueError):
    """The requested current-dispatch transition is unsafe or inconsistent."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _deterministic_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_utc_text(value: str) -> str:
    if not value.endswith("Z"):
        raise ActivationError("--at-utc must use UTC Z notation")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ActivationError("--at-utc must be valid ISO-8601 UTC") from exc
    if parsed.tzinfo != timezone.utc:
        raise ActivationError("--at-utc must be UTC")
    return value


def _repo_root(path: Path) -> Path:
    root = path.resolve()
    if not root.is_dir():
        raise ActivationError(f"repo root is not a directory: {root}")
    return root


def _within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def _repo_relative_manifest(root: Path, manifest_arg: Path) -> tuple[str, Path]:
    if manifest_arg.is_absolute():
        resolved = manifest_arg.resolve()
    else:
        pure_arg = PurePosixPath(manifest_arg.as_posix())
        if pure_arg.is_absolute() or ".." in pure_arg.parts or "." in pure_arg.parts:
            raise ActivationError("manifest path must be canonical and traversal-free")
        resolved = root.joinpath(*pure_arg.parts).resolve()
    try:
        rel = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ActivationError("manifest path resolves outside repo root") from exc
    pure = PurePosixPath(rel)
    if pure.parts[: len(MANIFEST_PREFIX)] != MANIFEST_PREFIX:
        raise ActivationError("manifest must stay under parallel/PM/DISPATCH_MANIFESTS/")
    if len(pure.parts) != len(MANIFEST_PREFIX) + 1:
        raise ActivationError("manifest must be a direct child of parallel/PM/DISPATCH_MANIFESTS/")
    return rel, resolved


def _resolve_pointer_path(root: Path, pointer_arg: Path) -> Path:
    if pointer_arg.is_absolute():
        resolved = pointer_arg.resolve()
    else:
        pure = PurePosixPath(pointer_arg.as_posix())
        if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
            raise ActivationError("pointer path must be canonical and traversal-free")
        resolved = root.joinpath(*pure.parts).resolve()
    if not _within(root, resolved):
        raise ActivationError("pointer path resolves outside repo root")
    return resolved


def _pointer_display(root: Path, resolved: Path) -> str:
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return str(resolved)


def _load_target_manifest(root: Path, manifest_arg: Path) -> tuple[inbox.DispatchManifest, str, Path, bytes]:
    manifest_rel, manifest_file = _repo_relative_manifest(root, manifest_arg)
    try:
        raw = manifest_file.read_bytes()
    except OSError as exc:
        raise ActivationError(f"cannot read target manifest: {exc}") from exc
    try:
        manifest, c2_path = inbox.load_manifest(root, Path(manifest_rel))
    except inbox.ManifestError as exc:
        raise ActivationError(f"target manifest failed C2 validation: {exc}") from exc
    c3_errors = contract.validate_dispatch(manifest_file, root)
    if c3_errors:
        raise ActivationError("target manifest failed C3 validation: " + " | ".join(c3_errors))
    if c2_path.resolve() != manifest_file:
        raise ActivationError("target manifest path identity changed during validation")
    expected_rel = f"parallel/PM/DISPATCH_MANIFESTS/{manifest.dispatch_id}.json"
    if manifest_rel != expected_rel:
        raise ActivationError(
            f"manifest path/dispatchId mismatch: expected {expected_rel!r}, got {manifest_rel!r}"
        )
    return manifest, manifest_rel, manifest_file, raw


def _snapshot(pointer: current.CurrentDispatchPointer) -> dict[str, Any]:
    return {
        "dispatchId": pointer.dispatch_id,
        "manifestPath": pointer.manifest_path,
        "manifestAuthorityCommit": pointer.manifest_authority_commit,
        "manifestSha256": pointer.manifest_sha256,
        "revision": pointer.revision,
    }


def _load_and_validate_current(
    root: Path,
    pointer_arg: Path,
    repository: str,
) -> tuple[current.CurrentDispatchPointer | None, Path, bytes | None]:
    pointer_file = _resolve_pointer_path(root, pointer_arg)
    if not pointer_file.exists():
        return None, pointer_file, None
    if not pointer_file.is_file():
        raise ActivationError(f"current pointer is not a regular file: {pointer_file}")
    try:
        raw = pointer_file.read_bytes()
    except OSError as exc:
        raise ActivationError(f"cannot read current pointer bytes: {exc}") from exc
    try:
        current.resolve_current_dispatch(
            root,
            Path(_pointer_display(root, pointer_file)),
            expected_repository=repository,
        )
        pointer, reread_path = current.load_pointer(root, Path(_pointer_display(root, pointer_file)))
    except current.CurrentDispatchError as exc:
        raise ActivationError(f"current pointer failed C5 validation: {exc}") from exc
    if reread_path.resolve() != pointer_file:
        raise ActivationError("current pointer path identity changed during validation")
    try:
        after = pointer_file.read_bytes()
    except OSError as exc:
        raise ActivationError(f"cannot re-read current pointer after C5 validation: {exc}") from exc
    if after != raw:
        raise ActivationError("current pointer changed during validation; re-plan from latest state")
    return pointer, pointer_file, raw


def build_plan(
    *,
    repo_root: Path,
    manifest_path: Path,
    pointer_path: Path = DEFAULT_POINTER_PATH,
    repository: str = DEFAULT_REPOSITORY,
    at_utc: str | None = None,
    revision: int | None = None,
    expected_authority_commit: str | None = None,
    expected_current_sha256: str | None = None,
    expect_current_absent: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    manifest, manifest_rel, _, manifest_raw = _load_target_manifest(root, manifest_path)
    if expected_authority_commit is not None:
        if not SHA_RE.fullmatch(expected_authority_commit):
            raise ActivationError("--expected-authority-commit must be a lowercase 40-hex Git SHA")
        if manifest.authority_commit != expected_authority_commit:
            raise ActivationError(
                "target authority mismatch: "
                f"expected {expected_authority_commit}, manifest has {manifest.authority_commit}"
            )

    old, pointer_file, old_raw = _load_and_validate_current(root, pointer_path, repository)
    actual_old_sha = _sha256(old_raw) if old_raw is not None else None
    if expect_current_absent and old is not None:
        raise ActivationError("current pointer exists but --expect-current-absent was requested")
    if expected_current_sha256 is not None:
        if not SHA256_RE.fullmatch(expected_current_sha256):
            raise ActivationError("--expected-current-sha256 must be lowercase 64-hex SHA-256")
        if actual_old_sha != expected_current_sha256:
            raise ActivationError(
                "stale current-pointer guard: expected old SHA-256 does not match current bytes"
            )

    if old is None:
        operation = "create"
        next_revision = 1
        previous = None
    else:
        operation = "update"
        if old.dispatch_id == manifest.dispatch_id:
            raise ActivationError(
                "target dispatch is already current; activation requires a new immutable dispatchId"
            )
        next_revision = old.revision + 1
        previous = _snapshot(old)

    if revision is not None:
        if type(revision) is not int or revision < 1:
            raise ActivationError("--revision must be an integer >= 1")
        if revision != next_revision:
            raise ActivationError(
                f"revision regression/non-monotonic request: exact next revision is {next_revision}, got {revision}"
            )

    timestamp = _validate_utc_text(at_utc) if at_utc is not None else _utc_now_text()
    pointer_payload: dict[str, Any] = {
        "schema": current.POINTER_SCHEMA,
        "pmOwned": True,
        "repository": repository,
        "dispatchId": manifest.dispatch_id,
        "manifestPath": manifest_rel,
        "manifestAuthorityCommit": manifest.authority_commit,
        "manifestSha256": _sha256(manifest_raw),
        "updatedAtUtc": timestamp,
        "revision": next_revision,
        "previousDispatch": previous,
    }
    try:
        parsed = current.parse_pointer_payload(pointer_payload)
    except current.CurrentDispatchError as exc:
        raise ActivationError(f"planned pointer failed C5 pointer validation: {exc}") from exc
    if parsed.revision != next_revision:
        raise ActivationError("planned pointer revision changed during validation")

    pointer_bytes = _deterministic_json_bytes(pointer_payload)
    pointer_sha = _sha256(pointer_bytes)
    pointer_display = _pointer_display(root, pointer_file)
    return {
        "schema": PLAN_SCHEMA,
        "ok": True,
        "operation": operation,
        "repository": repository,
        "pointerPath": pointer_display,
        "target": {
            "dispatchId": manifest.dispatch_id,
            "manifestPath": manifest_rel,
            "manifestAuthorityCommit": manifest.authority_commit,
            "manifestSha256": pointer_payload["manifestSha256"],
        },
        "transition": {
            "revision": next_revision,
            "previousDispatch": previous,
        },
        "writeGuard": {
            "expectedOldState": "ABSENT" if old_raw is None else "PRESENT",
            "expectedOldSha256": actual_old_sha,
            "expectedOldGitBlobSha1": _git_blob_sha1(old_raw) if old_raw is not None else None,
        },
        "plannedPointerSha256": pointer_sha,
        "plannedPointerGitBlobSha1": _git_blob_sha1(pointer_bytes),
        "plannedPointerJson": pointer_payload,
        "plannedPointerText": pointer_bytes.decode("utf-8"),
    }


def check_guard(
    *,
    repo_root: Path,
    pointer_path: Path = DEFAULT_POINTER_PATH,
    expected_old_sha256: str | None,
    expect_absent: bool,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    pointer_file = _resolve_pointer_path(root, pointer_path)
    if expect_absent == (expected_old_sha256 is not None):
        raise ActivationError("guard requires exactly one of --expect-absent or --expected-old-sha256")
    try:
        raw = pointer_file.read_bytes()
    except FileNotFoundError:
        raw = None
    except OSError as exc:
        raise ActivationError(f"cannot read guarded pointer: {exc}") from exc
    actual = _sha256(raw) if raw is not None else None
    if expect_absent:
        if raw is not None:
            raise ActivationError("concurrent pointer change: expected pointer to remain absent")
    else:
        assert expected_old_sha256 is not None
        if not SHA256_RE.fullmatch(expected_old_sha256):
            raise ActivationError("--expected-old-sha256 must be lowercase 64-hex SHA-256")
        if actual != expected_old_sha256:
            raise ActivationError("concurrent pointer change: old pointer SHA-256 no longer matches plan")
    return {
        "schema": GUARD_SCHEMA,
        "ok": True,
        "pointerPath": _pointer_display(root, pointer_file),
        "actualSha256": actual,
    }


def verify_activation(
    *,
    repo_root: Path,
    pointer_path: Path = DEFAULT_POINTER_PATH,
    repository: str = DEFAULT_REPOSITORY,
    expected_pointer_sha256: str | None = None,
    expected_dispatch_id: str | None = None,
    expected_revision: int | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    pointer_file = _resolve_pointer_path(root, pointer_path)
    try:
        raw = pointer_file.read_bytes()
    except OSError as exc:
        raise ActivationError(f"cannot read PM-written pointer: {exc}") from exc
    actual_sha = _sha256(raw)
    if expected_pointer_sha256 is not None:
        if not SHA256_RE.fullmatch(expected_pointer_sha256):
            raise ActivationError("--expected-pointer-sha256 must be lowercase 64-hex SHA-256")
        if actual_sha != expected_pointer_sha256:
            raise ActivationError("PM-written pointer bytes do not match planned pointer SHA-256")
    try:
        summary = current.resolve_current_dispatch(
            root,
            Path(_pointer_display(root, pointer_file)),
            expected_repository=repository,
        )
        pointer, _ = current.load_pointer(root, Path(_pointer_display(root, pointer_file)))
    except current.CurrentDispatchError as exc:
        raise ActivationError(f"PM-written pointer failed C5 resolution: {exc}") from exc
    if expected_dispatch_id is not None and pointer.dispatch_id != expected_dispatch_id:
        raise ActivationError(
            f"dispatchId mismatch after activation: expected {expected_dispatch_id!r}, got {pointer.dispatch_id!r}"
        )
    if expected_revision is not None:
        if type(expected_revision) is not int or expected_revision < 1:
            raise ActivationError("--expected-revision must be an integer >= 1")
        if pointer.revision != expected_revision:
            raise ActivationError(
                f"revision mismatch after activation: expected {expected_revision}, got {pointer.revision}"
            )
    return {
        "schema": VERIFY_SCHEMA,
        "ok": True,
        "pointerPath": _pointer_display(root, pointer_file),
        "pointerSha256": actual_sha,
        "dispatchId": pointer.dispatch_id,
        "revision": pointer.revision,
        "manifestPath": pointer.manifest_path,
        "manifestAuthorityCommit": pointer.manifest_authority_commit,
        "manifestSha256": pointer.manifest_sha256,
        "c5PmAction": summary["pmAction"],
        "c5AllResultsValid": summary["allResultsValid"],
    }


def _error_payload(kind: str, detail: str) -> dict[str, Any]:
    return {"schema": kind, "ok": False, "error": "ACTIVATION_REJECTED", "detail": detail}


def _print(payload: Mapping[str, Any], pretty: bool) -> None:
    if pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="validate target/current state and render exact next pointer")
    plan.add_argument("--manifest", type=Path, required=True)
    plan.add_argument("--repo-root", type=Path, default=Path("."))
    plan.add_argument("--pointer", type=Path, default=DEFAULT_POINTER_PATH)
    plan.add_argument("--repository", default=DEFAULT_REPOSITORY)
    plan.add_argument("--at-utc", help="deterministic UTC timestamp override for planning/tests")
    plan.add_argument("--revision", type=int, help="optional exact-next revision assertion")
    plan.add_argument("--expected-authority-commit")
    group = plan.add_mutually_exclusive_group()
    group.add_argument("--expected-current-sha256")
    group.add_argument("--expect-current-absent", action="store_true")
    plan.add_argument("--pretty", action="store_true")

    guard = sub.add_parser("guard", help="fail if current pointer bytes changed since planning")
    guard.add_argument("--repo-root", type=Path, default=Path("."))
    guard.add_argument("--pointer", type=Path, default=DEFAULT_POINTER_PATH)
    g = guard.add_mutually_exclusive_group(required=True)
    g.add_argument("--expected-old-sha256")
    g.add_argument("--expect-absent", action="store_true")
    guard.add_argument("--pretty", action="store_true")

    verify = sub.add_parser("verify", help="verify PM-written pointer bytes and resolve through C5")
    verify.add_argument("--repo-root", type=Path, default=Path("."))
    verify.add_argument("--pointer", type=Path, default=DEFAULT_POINTER_PATH)
    verify.add_argument("--repository", default=DEFAULT_REPOSITORY)
    verify.add_argument("--expected-pointer-sha256")
    verify.add_argument("--expected-dispatch-id")
    verify.add_argument("--expected-revision", type=int)
    verify.add_argument("--pretty", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    kind = {
        "plan": PLAN_SCHEMA,
        "guard": GUARD_SCHEMA,
        "verify": VERIFY_SCHEMA,
    }[args.command]
    try:
        if args.command == "plan":
            payload = build_plan(
                repo_root=args.repo_root,
                manifest_path=args.manifest,
                pointer_path=args.pointer,
                repository=args.repository,
                at_utc=args.at_utc,
                revision=args.revision,
                expected_authority_commit=args.expected_authority_commit,
                expected_current_sha256=args.expected_current_sha256,
                expect_current_absent=args.expect_current_absent,
            )
        elif args.command == "guard":
            payload = check_guard(
                repo_root=args.repo_root,
                pointer_path=args.pointer,
                expected_old_sha256=args.expected_old_sha256,
                expect_absent=args.expect_absent,
            )
        else:
            payload = verify_activation(
                repo_root=args.repo_root,
                pointer_path=args.pointer,
                repository=args.repository,
                expected_pointer_sha256=args.expected_pointer_sha256,
                expected_dispatch_id=args.expected_dispatch_id,
                expected_revision=args.expected_revision,
            )
    except (ActivationError, inbox.ManifestError, current.CurrentDispatchError) as exc:
        _print(_error_payload(kind, str(exc)), getattr(args, "pretty", False))
        return 2
    _print(payload, getattr(args, "pretty", False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
