from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Mapping

BUNDLE_SCHEMA = "wof-alpha-final-acceptance-bundle-v1"
W3_SCHEMA = "wof-render-source-qualification-v1"
P16_SCHEMA = "wof-alpha-canonical-owner-acceptance-evidence-v1"
DRAW_SCHEMA = "wof-alpha-canonical-draw-evidence-v1"
DEFAULT_CANDIDATE_REL = Path("parallel/OWNER_ONECLICK/CANDIDATES/ALPHA_V1_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE.json")
DEFAULT_W3_RUNNER_REL = Path("parallel/RENDER_AUTHORITY_V2/run_long_qualification.py")
DEFAULT_RESULTS_NAME = "WOF_RESULTS"
P16_NAME = "ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.json"
P18_NAME = "ALPHA_CANONICAL_DRAW_EVIDENCE.json"
BUNDLE_JSON_NAME = "ALPHA_FINAL_ACCEPTANCE_BUNDLE.json"
BUNDLE_MD_NAME = "ALPHA_FINAL_ACCEPTANCE_BUNDLE.md"

WAITING_W3_QUALIFICATION = "WAITING_W3_QUALIFICATION"
W3_INCONCLUSIVE = "W3_INCONCLUSIVE"
WAITING_CANONICAL_RUNTIME_EVIDENCE = "WAITING_CANONICAL_RUNTIME_EVIDENCE"
CANONICAL_RUNTIME_SUPPRESSED = "CANONICAL_RUNTIME_SUPPRESSED"
WAITING_DRAW_EVIDENCE = "WAITING_DRAW_EVIDENCE"
READY_FOR_OWNER_VISUAL_CONFIRMATION = "READY_FOR_OWNER_VISUAL_CONFIRMATION"
FAILED_EVIDENCE_MISMATCH = "FAILED_EVIDENCE_MISMATCH"


class EvidenceError(ValueError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvidenceError(f"JSON root must be an object: {path}")
    return value


def _stable_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        Path(tmp_name).unlink(missing_ok=True)


def default_results_dir() -> Path:
    return Path.home() / "Documents" / DEFAULT_RESULTS_NAME


def _require_safety(safety: Any, source: str) -> None:
    if not isinstance(safety, Mapping):
        raise EvidenceError(f"{source}: safety object missing")
    expected = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
    for key, value in expected.items():
        if safety.get(key) != value:
            raise EvidenceError(f"{source}: safety mismatch {key}={safety.get(key)!r}")
    for key in ("screenshotProductionCoordinates", "worldProjectionProductionCoordinates", "guessedAddresses"):
        if key in safety and safety.get(key) is not False:
            raise EvidenceError(f"{source}: forbidden coordinate/source safety flag {key}={safety.get(key)!r}")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_candidate_metadata(repo_root: Path, explicit: Path | None = None) -> dict[str, Any]:
    path = (explicit or (repo_root / DEFAULT_CANDIDATE_REL)).expanduser().resolve()
    if not path.is_file():
        raise EvidenceError(f"candidate metadata missing: {path}")
    value = _load_json(path)
    if value.get("schema") != "wof-owner-oneclick-package-v1":
        raise EvidenceError("candidate metadata schema mismatch")
    package_version = value.get("packageVersion")
    source_commit = value.get("sourceCommit")
    if not isinstance(package_version, str) or not package_version:
        raise EvidenceError("candidate packageVersion missing")
    if not isinstance(source_commit, str) or len(source_commit) < 12:
        raise EvidenceError("candidate sourceCommit missing")
    safety = value.get("safety")
    _require_safety(safety, "candidate")
    convergence = ((value.get("components") or {}).get("canonicalProductConvergence") or {})
    if convergence and convergence.get("alphaLivePromoted") is not False:
        raise EvidenceError("candidate unexpectedly reports alpha-live promotion")
    return {
        "sourcePath": str(path),
        "contentSha256": _sha256(path),
        "schema": value.get("schema"),
        "packageVersion": package_version,
        "sourceCommit": source_commit,
        "selectionPolicy": value.get("selectionPolicy"),
        "canonicalProductConvergence": {
            "stageId": convergence.get("stageId"),
            "initialState": convergence.get("initialState"),
            "legacySpatialFallback": convergence.get("legacySpatialFallback"),
            "alphaLivePromoted": convergence.get("alphaLivePromoted"),
        },
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "legacySpatialFallback": safety.get("legacySpatialFallback"),
        },
    }


def _resolve_w3_qualification(path: Path) -> tuple[Path, dict[str, Any]]:
    path = path.expanduser().resolve()
    value = _load_json(path)
    if value.get("schema") == "wof-w3-long-qualification-latest-v1":
        qualification = value.get("qualificationJson")
        if not isinstance(qualification, str) or not qualification:
            raise EvidenceError("W3 latest pointer qualificationJson missing")
        qpath = Path(qualification).expanduser()
        if not qpath.is_absolute():
            qpath = (path.parent / qpath).resolve()
        path = qpath
        value = _load_json(path)
    if value.get("schema") != W3_SCHEMA:
        raise EvidenceError("W3 qualification schema mismatch")
    return path, value


def read_w3_qualification(path: Path) -> dict[str, Any]:
    resolved, value = _resolve_w3_qualification(path)
    status = value.get("status")
    if status not in {"PASS", "INCONCLUSIVE", "REJECTED"}:
        raise EvidenceError(f"W3 qualification status invalid: {status!r}")
    readiness = value.get("canonicalProducerReadiness")
    if status == "PASS":
        if not isinstance(readiness, Mapping) or readiness.get("ready") is not True:
            raise EvidenceError("W3 PASS without ready canonical producer")
        renderer_source = readiness.get("rendererSource")
        if not isinstance(renderer_source, Mapping) or renderer_source.get("proven") is not True:
            raise EvidenceError("W3 PASS without explicit rendererSource.proven")
    identity = value.get("captureIdentity") if isinstance(value.get("captureIdentity"), Mapping) else {}
    return {
        "sourcePath": str(resolved),
        "schema": value.get("schema"),
        "status": status,
        "rendererAuthority": value.get("rendererAuthority"),
        "repoQualificationPolicy": value.get("repoQualificationPolicy"),
        "identity": {
            "worldSha256": identity.get("worldSha256"),
            "authorityKey": identity.get("authorityKey"),
            "runtimeEpoch": identity.get("runtimeEpoch"),
            "rendererEpoch": identity.get("rendererEpoch"),
        },
        "blockingProofEdge": value.get("blockingProofEdge"),
        "ownerAction": value.get("ownerAction"),
        "canonicalProducerReadiness": readiSÆÈ‹j◊ù~ä‹¢jZrŸﬁ≤