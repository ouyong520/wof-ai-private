"""Strict runtime/ROM/source identity for Training Farm deterministic replay."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from pathlib import Path

from .adapter import RuntimeCapabilityError, TrainingFarmAdapter
from .stable_retro_backend import (
    PINNED_STABLE_RETRO,
    configured_rom_path,
    installed_stable_retro_version,
)

SOURCE_NAMESPACE = "stable-retro-fbneo"
RUNTIME_IDENTITY_SCHEMA = "wof-training-farm-runtime-identity-v1"
_REAL_KIND = "real-wof"
_FIXTURE_KIND = "fixture"
_SOURCE_FILES = (
    "__init__.py",
    "adapter.py",
    "fake_backend.py",
    "stable_retro_backend.py",
    "identity.py",
    "determinism.py",
    "determinism.schema.json",
)

_REQUIRED_KEYS = {
    "schema",
    "sourceNamespace",
    "runtimeKind",
    "pinnedStableRetroVersion",
    "stableRetroVersion",
    "osSystem",
    "osRelease",
    "machine",
    "pythonImplementation",
    "pythonVersion",
    "pythonExecutable",
    "processId",
    "romIdentityKind",
    "romSha256",
    "farmCandidateSha256",
    "farmSourceFiles",
    "backend",
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        raise RuntimeCapabilityError(
            f"failed to hash identity file {path}: {type(exc).__name__}: {exc}"
        ) from exc
    return digest.hexdigest()


def farm_source_identity() -> tuple[str, dict[str, str]]:
    base = Path(__file__).resolve().parent
    files: dict[str, str] = {}
    for name in _SOURCE_FILES:
        path = base / name
        if not path.is_file():
            raise RuntimeCapabilityError(f"Farm source identity file is missing: {name}")
        files[name] = sha256_file(path)
    payload = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload), files


def _validate_sha256(value: object, field: str) -> str:
    if type(value) is not str or len(value) != 64:
        raise RuntimeCapabilityError(f"{field} must be a 64-character SHA-256 hex string")
    if any(ch not in "0123456789abcdef" for ch in value):
        raise RuntimeCapabilityError(f"{field} must contain lowercase SHA-256 hex")
    return value


def _validate_backend(value: object) -> dict[str, object]:
    if type(value) is not dict or not value:
        raise RuntimeCapabilityError("backend identity must be a non-empty dict")
    normalized: dict[str, object] = {}
    for key, item in value.items():
        if type(key) is not str or not key:
            raise RuntimeCapabilityError("backend identity keys must be non-empty strings")
        if type(item) not in (str, int, bool):
            raise RuntimeCapabilityError(
                f"backend identity value {key} must be strict str/int/bool"
            )
        if type(item) is int and item < 0:
            raise RuntimeCapabilityError(
                f"backend identity integer {key} must be non-negative"
            )
        normalized[key] = item
    for required in ("backendName", "coreName"):
        if type(normalized.get(required)) is not str or not normalized[required]:
            raise RuntimeCapabilityError(f"backend identity requires non-empty {required}")
    return normalized


def validate_runtime_identity(
    identity: object, *, require_real_rom: bool
) -> dict[str, object]:
    if type(identity) is not dict:
        raise RuntimeCapabilityError("runtime identity must be a dict")
    if set(identity) != _REQUIRED_KEYS:
        missing = sorted(_REQUIRED_KEYS - set(identity))
        extra = sorted(set(identity) - _REQUIRED_KEYS)
        raise RuntimeCapabilityError(
            f"runtime identity key mismatch: missing={missing} extra={extra}"
        )

    string_fields = (
        "schema",
        "sourceNamespace",
        "runtimeKind",
        "pinnedStableRetroVersion",
        "stableRetroVersion",
        "osSystem",
        "osRelease",
        "machine",
        "pythonImplementation",
        "pythonVersion",
        "pythonExecutable",
        "romIdentityKind",
    )
    for field in string_fields:
        if type(identity[field]) is not str or not identity[field]:
            raise RuntimeCapabilityError(f"runtime identity field {field} must be a string")

    if (
        isinstance(identity["processId"], bool)
        or not isinstance(identity["processId"], int)
        or identity["processId"] <= 0
    ):
        raise RuntimeCapabilityError(
            "runtime identity processId must be a positive integer"
        )

    if identity["schema"] != RUNTIME_IDENTITY_SCHEMA:
        raise RuntimeCapabilityError("runtime identity schema mismatch")
    if identity["sourceNamespace"] != SOURCE_NAMESPACE:
        raise RuntimeCapabilityError("runtime identity sourceNamespace mismatch")
    if identity["pinnedStableRetroVersion"] != PINNED_STABLE_RETRO:
        raise RuntimeCapabilityError("runtime identity pinned Stable-Retro version mismatch")
    if identity["runtimeKind"] not in (_REAL_KIND, _FIXTURE_KIND):
        raise RuntimeCapabilityError("runtime identity runtimeKind is invalid")

    _validate_sha256(identity["romSha256"], "romSha256")
    _validate_sha256(identity["farmCandidateSha256"], "farmCandidateSha256")

    files = identity["farmSourceFiles"]
    if type(files) is not dict or set(files) != set(_SOURCE_FILES):
        raise RuntimeCapabilityError("runtime identity farmSourceFiles is incomplete")
    for name, value in files.items():
        if type(name) is not str:
            raise RuntimeCapabilityError("runtime identity source file names must be strings")
        _validate_sha256(value, f"farmSourceFiles[{name}]")

    _validate_backend(identity["backend"])

    if require_real_rom:
        if identity["runtimeKind"] != _REAL_KIND:
            raise RuntimeCapabilityError("real determinism proof requires runtimeKind=real-wof")
        if identity["romIdentityKind"] != "sha256-external-rom":
            raise RuntimeCapabilityError("real determinism proof requires external ROM SHA-256")
        if identity["stableRetroVersion"] != PINNED_STABLE_RETRO:
            raise RuntimeCapabilityError("real determinism proof requires pinned Stable-Retro")
        backend = identity["backend"]
        assert isinstance(backend, dict)
        if backend.get("coreName") != "FBNeo":
            raise RuntimeCapabilityError("real determinism proof requires FBNeo core identity")
    else:
        if identity["runtimeKind"] != _FIXTURE_KIND:
            raise RuntimeCapabilityError("fixture identity requires runtimeKind=fixture")
        if identity["romIdentityKind"] != "fixture-marker":
            raise RuntimeCapabilityError("fixture identity requires fixture ROM marker")

    return dict(identity)


def runtime_identity_sha256(identity: object, *, require_real_rom: bool) -> str:
    validated = validate_runtime_identity(identity, require_real_rom=require_real_rom)
    payload = json.dumps(validated, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def _base_identity(
    adapter: TrainingFarmAdapter,
    *,
    runtime_kind: str,
    stable_retro_version: str,
    rom_identity_kind: str,
    rom_sha256: str,
) -> dict[str, object]:
    candidate_sha, source_files = farm_source_identity()
    return {
        "schema": RUNTIME_IDENTITY_SCHEMA,
        "sourceNamespace": SOURCE_NAMESPACE,
        "runtimeKind": runtime_kind,
        "pinnedStableRetroVersion": PINNED_STABLE_RETRO,
        "stableRetroVersion": stable_retro_version,
        "osSystem": platform.system(),
        "osRelease": platform.release(),
        "machine": platform.machine() or "unknown",
        "pythonImplementation": platform.python_implementation(),
        "pythonVersion": platform.python_version(),
        "pythonExecutable": str(Path(sys.executable).resolve()),
        "processId": os.getpid(),
        "romIdentityKind": rom_identity_kind,
        "romSha256": rom_sha256,
        "farmCandidateSha256": candidate_sha,
        "farmSourceFiles": source_files,
        "backend": adapter.runtime_identity_components(),
    }


def build_real_runtime_identity(
    adapter: TrainingFarmAdapter,
    rom_path: str | Path | None = None,
) -> dict[str, object]:
    rom = configured_rom_path(rom_path)
    if rom is None or not rom.is_absolute() or not rom.is_file():
        raise RuntimeCapabilityError("real runtime identity requires an existing absolute ROM path")
    version = installed_stable_retro_version()
    if type(version) is not str or not version:
        raise RuntimeCapabilityError("real runtime identity requires observed Stable-Retro version")
    identity = _base_identity(
        adapter,
        runtime_kind=_REAL_KIND,
        stable_retro_version=version,
        rom_identity_kind="sha256-external-rom",
        rom_sha256=sha256_file(rom),
    )
    return validate_runtime_identity(identity, require_real_rom=True)


def build_fixture_runtime_identity(adapter: TrainingFarmAdapter) -> dict[str, object]:
    identity = _base_identity(
        adapter,
        runtime_kind=_FIXTURE_KIND,
        stable_retro_version="not-applicable-fixture",
        rom_identity_kind="fixture-marker",
        rom_sha256=_sha256_bytes(b"training-farm-r0.2-fixture-no-rom"),
    )
    return validate_runtime_identity(identity, require_real_rom=False)


def identities_match_exactly(
    left: object, right: object, *, require_real_rom: bool
) -> bool:
    left_valid = validate_runtime_identity(left, require_real_rom=require_real_rom)
    right_valid = validate_runtime_identity(right, require_real_rom=require_real_rom)
    return left_valid == right_valid
