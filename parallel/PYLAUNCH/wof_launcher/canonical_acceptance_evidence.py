from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from .canonical_owner_status import normalize_owner_status

SCHEMA = "wof-alpha-canonical-owner-acceptance-evidence-v1"
OUTPUT_NAME = "ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.json"
TIMELINE_LIMIT = 32


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def default_results_dir() -> Path:
    return Path.home() / "Documents" / "WOF_RESULTS"


def default_evidence_path() -> Path:
    return default_results_dir() / OUTPUT_NAME


def _canonical_timeline(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw = snapshot.get("significant_events")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for event in raw:
        if not isinstance(event, Mapping) or event.get("kind") != "canonical-state-transition":
            continue
        out.append({
            key: event.get(key)
            for key in (
                "atUtc",
                "canonicalState",
                "reason",
                "previousState",
                "previousReason",
                "packageVersion",
                "runtimeEpoch",
                "authorityKey",
                "rendererEpoch",
                "rendererAuthority",
                "pageTargetId",
                "workerTargetId",
                "worldSha256",
            )
            if event.get(key) is not None
        })
    return out[-TIMELINE_LIMIT:]


def build_acceptance_evidence(
    status: Mapping[str, Any] | Any,
    *,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    if hasattr(status, "snapshot") and callable(status.snapshot):
        status = status.snapshot()
    if not isinstance(status, Mapping):
        raise TypeError("status must be a mapping or expose snapshot()")

    normalized = status.get("canonical_owner_status")
    if not isinstance(normalized, Mapping):
        normalized = normalize_owner_status(status)
    else:
        normalized = dict(normalized)

    return {
        "schema": SCHEMA,
        "version": 1,
        "generatedAtUtc": generated_at_utc or _utc_now(),
        "packageVersion": normalized.get("packageVersion") or status.get("alpha_package_version"),
        "world": {
            "accepted": status.get("world_921031") is True,
            "sha256": status.get("identity_sha256"),
            "pageTargetId": status.get("page_target_id"),
            "pageUrl": status.get("page_url"),
            "workerTargetId": status.get("worker_target_id"),
            "workerUrl": status.get("worker_url"),
        },
        "runtime": {
            "epoch": normalized.get("runtimeEpoch") or status.get("alpha_runtime_epoch"),
            "authorityKey": normalized.get("authorityKey"),
            "rendererEpoch": normalized.get("rendererEpoch"),
            "rendererAuthority": normalized.get("rendererAuthority"),
        },
        "canonical": {
            "state": normalized.get("state"),
            "reason": normalized.get("reason"),
            "labelZh": normalized.get("labelZh"),
            "humanZh": normalized.get("humanZh"),
        },
        "canonicalTransitionTimeline": _canonical_timeline(status),
        "safety": {
            "readOnly": status.get("read_only") is True,
            "ramWrites": status.get("ram_writes"),
            "inputInjection": status.get("input_injection") is True,
        },
        "hudCanonicalStatus": normalized.get("hudCanonicalStatus"),
        # P16 is deliberately incapable of promoting runtime/module/fixture evidence
        # into a human-visible product claim. A later dedicated Owner gate owns that.
        "visibleProof": "NOT_PROVEN",
    }


def write_acceptance_evidence(
    status: Mapping[str, Any] | Any,
    output_path: Path | None = None,
) -> Path:
    path = Path(output_path) if output_path is not None else default_evidence_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_acceptance_evidence(status)
    fd, temp_name = tempfile.mkstemp(prefix=".ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        try:
            Path(temp_name).unlink(missing_ok=True)
        except OSError:
            pass
    return path
