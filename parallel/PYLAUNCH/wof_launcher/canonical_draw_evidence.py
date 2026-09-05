from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

HUD_EVIDENCE_SCHEMA = "wof-alpha-maintained-hud-canonical-draw-evidence-v1"
HUD_EVIDENCE_VERSION = "wof-alpha-maintained-hud-canonical-draw-acknowledgement-v1"
COLLECTOR_SCHEMA = "wof-alpha-canonical-draw-evidence-snapshot-v1"
COLLECTOR_VERSION = "wof-alpha-canonical-draw-evidence-collector-v1"
DEFAULT_OUTPUT_PATH = Path.home() / "Documents" / "WOF_RESULTS" / "ALPHA_CANONICAL_DRAW_EVIDENCE.json"
MAX_ACKNOWLEDGEMENTS = 128
ALLOWED_STATES = frozenset({
    "NO_CANONICAL_DRAW",
    "CANONICAL_DRAW_ACKNOWLEDGED",
    "STALE_OR_MISMATCH",
    "HUD_API_MISSING",
})
ALLOWED_KINDS = frozenset({"enemy-target-label", "player-danger-warning"})
WORLD_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
SAFETY = {
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "legacySpatialFallback": False,
    "screenshotAuthority": False,
    "worldProjectionAuthority": False,
    "positionAuthority": False,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _normalize_authority(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("expected authority must be an object")
    authority_key = value.get("authorityKey")
    runtime_epoch = value.get("runtimeEpoch")
    renderer_epoch = value.get("rendererEpoch")
    world_sha = value.get("worldSha256")
    if not isinstance(authority_key, str) or not authority_key:
        raise ValueError("authorityKey is required")
    if not isinstance(runtime_epoch, str) or len(runtime_epoch) < 16:
        raise ValueError("runtimeEpoch must be an exact non-empty epoch")
    if not isinstance(renderer_epoch, str) or len(renderer_epoch) < 16:
        raise ValueError("rendererEpoch must be an exact non-empty epoch")
    if world_sha is not None and (not isinstance(world_sha, str) or WORLD_SHA_RE.fullmatch(world_sha) is None):
        raise ValueError("worldSha256 must be a lower-case sha256 when present")
    return {
        "authorityKey": authority_key,
        "runtimeEpoch": runtime_epoch,
        "rendererEpoch": renderer_epoch,
        "worldSha256": world_sha,
    }


def _same_authority(observed: Any, expected: Mapping[str, Any]) -> bool:
    if not isinstance(observed, Mapping):
        return False
    return all(observed.get(key) == expected.get(key) for key in ("authorityKey", "runtimeEpoch", "rendererEpoch", "worldSha256"))


def _find_page_target(client: Any, page_target_id: str) -> dict[str, Any] | None:
    result = client.request("Target.getTargets")
    infos = result.get("targetInfos") if isinstance(result, Mapping) else None
    if not isinstance(infos, list):
        return None
    for row in infos:
        if isinstance(row, Mapping) and row.get("targetId") == page_target_id:
            return dict(row)
    return None


def _base_snapshot(
    *,
    state: str,
    reason: str | None,
    page_target_id: str,
    page_target: Mapping[str, Any] | None,
    expected_authority: Mapping[str, Any],
    observed_authority: Mapping[str, Any] | None = None,
    acknowledgements: list[dict[str, Any]] | None = None,
    evidence_generation: int | None = None,
) -> dict[str, Any]:
    if state not in ALLOWED_STATES:
        raise ValueError(f"unsupported evidence state: {state}")
    rows = acknowledgements or []
    return {
        "schema": COLLECTOR_SCHEMA,
        "version": COLLECTOR_VERSION,
        "evidenceState": state,
        "reason": reason,
        "collectedAt": _utc_now(),
        "pageTarget": {
            "targetId": page_target_id,
            "type": page_target.get("type") if isinstance(page_target, Mapping) else None,
            "url": page_target.get("url") if isinstance(page_target, Mapping) else None,
        },
        "authority": dict(expected_authority) if state in {"NO_CANONICAL_DRAW", "CANONICAL_DRAW_ACKNOWLEDGED"} else None,
        "expectedAuthority": dict(expected_authority),
        "observedAuthority": dict(observed_authority) if isinstance(observed_authority, Mapping) else None,
        "evidenceGeneration": evidence_generation,
        "acknowledgementCount": len(rows),
        "acknowledgements": copy.deepcopy(rows),
        "safety": dict(SAFETY),
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "visibleProof": "NOT_PROVEN",
    }


def _validate_hud_snapshot(remote: Any, expected_authority: Mapping[str, Any]) -> tuple[str | None, list[dict[str, Any]], int | None, Mapping[str, Any] | None]:
    if not isinstance(remote, Mapping):
        return "HUD_EVIDENCE_MALFORMED", [], None, None
    observed = remote.get("authority") if isinstance(remote.get("authority"), Mapping) else None
    if remote.get("schema") != HUD_EVIDENCE_SCHEMA or remote.get("version") != HUD_EVIDENCE_VERSION:
        return "HUD_EVIDENCE_SCHEMA_MISMATCH", [], None, observed
    if remote.get("visibleProof") != "NOT_PROVEN":
        return "VISIBLE_PROOF_BOUNDARY_INVALID", [], None, observed
    if remote.get("readOnly") is not True or remote.get("ramWrites") != 0 or remote.get("inputInjection") is not False:
        return "HUD_EVIDENCE_SAFETY_MISMATCH", [], None, observed
    safety = remote.get("safety")
    if not isinstance(safety, Mapping) or any(safety.get(key) != value for key, value in SAFETY.items()):
        return "HUD_EVIDENCE_SAFETY_MISMATCH", [], None, observed
    if remote.get("bound") is not True or not _same_authority(observed, expected_authority):
        return "AUTHORITY_RUNTIME_RENDERER_MISMATCH", [], None, observed
    generation = remote.get("evidenceGeneration")
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
        return "EVIDENCE_GENERATION_INVALID", [], None, observed
    max_entries = remote.get("maxEntries")
    entries = remote.get("entries")
    if not isinstance(max_entries, int) or isinstance(max_entries, bool) or not 1 <= max_entries <= MAX_ACKNOWLEDGEMENTS:
        return "LEDGER_BOUND_INVALID", [], generation, observed
    if not isinstance(entries, list) or len(entries) > max_entries or remote.get("entryCount") != len(entries):
        return "LEDGER_SHAPE_INVALID", [], generation, observed
    previous_sequence = -1
    clean: list[dict[str, Any]] = []
    for row in entries:
        if not isinstance(row, Mapping):
            return "ACKNOWLEDGEMENT_ROW_INVALID", [], generation, observed
        sequence = row.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= previous_sequence:
            return "ACKNOWLEDGEMENT_SEQUENCE_INVALID", [], generation, observed
        previous_sequence = sequence
        if row.get("evidenceGeneration") != generation or row.get("kind") not in ALLOWED_KINDS or row.get("completed") is not True:
            return "ACKNOWLEDGEMENT_IDENTITY_INVALID", [], generation, observed
        if row.get("visibleProof") != "NOT_PROVEN" or row.get("screenshotAuthority") is not False or row.get("worldProjectionAuthority") is not False:
            return "ACKNOWLEDGEMENT_PROOF_BOUNDARY_INVALID", [], generation, observed
        if row.get("coordinateAuthority") != "canonical-render-object-only" or not _same_authority(row.get("authority"), expected_authority):
            return "ACKNOWLEDGEMENT_AUTHORITY_MISMATCH", [], generation, observed
        native_x, native_y = row.get("nativeX"), row.get("nativeY")
        if not _finite_number(native_x) or not _finite_number(native_y) or not (0 <= float(native_x) < 384) or not (0 <= float(native_y) < 224):
            return "ACKNOWLEDGEMENT_NATIVE_COORDINATE_INVALID", [], generation, observed
        rect = row.get("drawRectDb")
        if not isinstance(rect, Mapping) or not all(_finite_number(rect.get(key)) for key in ("x", "y", "width", "height")):
            return "ACKNOWLEDGEMENT_DRAW_RECT_INVALID", [], generation, observed
        if float(rect["width"]) <= 0 or float(rect["height"]) <= 0:
            return "ACKNOWLEDGEMENT_DRAW_RECT_INVALID", [], generation, observed
        clean.append(copy.deepcopy(dict(row)))
    state = remote.get("evidenceState")
    if entries and state != "CANONICAL_DRAW_ACKNOWLEDGED":
        return "HUD_EVIDENCE_STATE_MISMATCH", [], generation, observed
    if not entries and state != "NO_CANONICAL_DRAW":
        return "HUD_EVIDENCE_STATE_MISMATCH", [], generation, observed
    return None, clean, generation, observed


def atomic_write_snapshot(path: str | os.PathLike[str], payload: Mapping[str, Any]) -> Path:
    output = Path(path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, output)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return output


def collect_canonical_draw_evidence(
    client: Any,
    *,
    page_target_id: str,
    expected_authority: Mapping[str, Any],
    expected_page_url: str | None = None,
    output_path: str | os.PathLike[str] = DEFAULT_OUTPUT_PATH,
) -> dict[str, Any]:
    if not isinstance(page_target_id, str) or not page_target_id:
        raise ValueError("explicit accepted page target id is required")
    expected = _normalize_authority(expected_authority)
    target = _find_page_target(client, page_target_id)
    if target is None or target.get("type") != "page":
        snapshot = _base_snapshot(state="STALE_OR_MISMATCH", reason="PAGE_TARGET_MISSING_OR_NOT_PAGE", page_target_id=page_target_id, page_target=target, expected_authority=expected)
        atomic_write_snapshot(output_path, snapshot)
        return snapshot
    if expected_page_url is not None and target.get("url") != expected_page_url:
        snapshot = _base_snapshot(state="STALE_OR_MISMATCH", reason="PAGE_TARGET_URL_MISMATCH", page_target_id=page_target_id, page_target=target, expected_authority=expected)
        atomic_write_snapshot(output_path, snapshot)
        return snapshot

    session = None
    try:
        session = client.attach(page_target_id)
        session.request("Runtime.enable")
        remote = session.evaluate(
            "(()=>{const h=window.WOFALPHAHUD;if(!h||typeof h.canonicalDrawEvidence!=='function')return {__wofP18:'HUD_API_MISSING'};return h.canonicalDrawEvidence();})()",
            timeout=5.0,
        )
    except Exception as exc:
        snapshot = _base_snapshot(state="STALE_OR_MISMATCH", reason=f"CDP_READ_FAILED:{type(exc).__name__}", page_target_id=page_target_id, page_target=target, expected_authority=expected)
        atomic_write_snapshot(output_path, snapshot)
        return snapshot
    finally:
        if session is not None:
            try:
                session.close()
            except Exception:
                pass

    if isinstance(remote, Mapping) and remote.get("__wofP18") == "HUD_API_MISSING":
        snapshot = _base_snapshot(state="HUD_API_MISSING", reason="HUD_CANONICAL_DRAW_EVIDENCE_API_MISSING", page_target_id=page_target_id, page_target=target, expected_authority=expected)
        atomic_write_snapshot(output_path, snapshot)
        return snapshot

    error, acknowledgements, generation, observed = _validate_hud_snapshot(remote, expected)
    if error is not None:
        snapshot = _base_snapshot(state="STALE_OR_MISMATCH", reason=error, page_target_id=page_target_id, page_target=target, expected_authority=expected, observed_authority=observed, evidence_generation=generation)
        atomic_write_snapshot(output_path, snapshot)
        return snapshot

    state = "CANONICAL_DRAW_ACKNOWLEDGED" if acknowledgements else "NO_CANONICAL_DRAW"
    snapshot = _base_snapshot(state=state, reason=None if acknowledgements else str(remote.get("reason") or "NO_CANONICAL_DRAW"), page_target_id=page_target_id, page_target=target, expected_authority=expected, observed_authority=observed, acknowledgements=acknowledgements, evidence_generation=generation)
    atomic_write_snapshot(output_path, snapshot)
    return snapshot


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect bounded maintained-HUD canonical draw acknowledgement evidence over read-only CDP.")
    parser.add_argument("--browser-websocket-url", required=True)
    parser.add_argument("--page-target-id", required=True)
    parser.add_argument("--page-url")
    parser.add_argument("--authority-key", required=True)
    parser.add_argument("--runtime-epoch", required=True)
    parser.add_argument("--renderer-epoch", required=True)
    parser.add_argument("--world-sha256")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    from .cdp import CdpClient

    client = CdpClient(args.browser_websocket_url)
    client.connect()
    try:
        snapshot = collect_canonical_draw_evidence(
            client,
            page_target_id=args.page_target_id,
            expected_page_url=args.page_url,
            expected_authority={
                "authorityKey": args.authority_key,
                "runtimeEpoch": args.runtime_epoch,
                "rendererEpoch": args.renderer_epoch,
                "worldSha256": args.world_sha256,
            },
            output_path=args.output,
        )
    finally:
        client.close()
    print(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if snapshot["evidenceState"] in {"NO_CANONICAL_DRAW", "CANONICAL_DRAW_ACKNOWLEDGED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())