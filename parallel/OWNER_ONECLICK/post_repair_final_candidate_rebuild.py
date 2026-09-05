from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import final_canonical_candidate as final

SCHEMA = "wof-alpha-post-repair-final-candidate-rebuild-v1"
VERSION = 1
HISTORICAL_P19_SOURCE_COMMIT = "0752796369f1687435a1b1647e66ea0b5ab07688"
DEFAULT_OUTPUT_REL = final.DEFAULT_OUTPUT_REL
DEFAULT_POINTER_REL = final.DEFAULT_POINTER_REL
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class RepairRequirement:
    stage_id: str
    dedup_key: str
    tested_commit: str
    result_path: str


REQUIRED_ACCEPTED_REPAIRS: tuple[RepairRequirement, ...] = (
    RepairRequirement(
        "ALPHA_V1_PRODUCT_TAKEOVER_P29_W3_LIVE_EVIDENCE_CONTRACT_REPAIR",
        "alpha.v1.product-takeover.w3-live-evidence-contract-repair-v1",
        "c02f7e108e73665f22eb950573622acb6f452732",
        "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P29_W3_LIVE_EVIDENCE_CONTRACT_REPAIR_RESULT.json",
    ),
    RepairRequirement(
        "ALPHA_V1_PRODUCT_TAKEOVER_P30_P16_P9_BINDING_AND_STAGING_READINESS_REPAIR",
        "alpha.v1.product-takeover.p16-p9-binding-staging-readiness-repair-v1",
        "90094a656ab311f18b0a758716dc97c3f8df092d",
        "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P30_P16_P9_BINDING_AND_STAGING_READINESS_REPAIR_RESULT.json",
    ),
    RepairRequirement(
        "ALPHA_V1_PRODUCT_TAKEOVER_P31_WOF_PAGE_ASSOCIATION_AMBIGUITY_REPAIR",
        "alpha.v1.product-takeover.wof-page-association-ambiguity-repair-v1",
        "423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731",
        "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P31_WOF_PAGE_ASSOCIATION_AMBIGUITY_REPAIR_RESULT.json",
    ),
)

P32_BLOCKED = RepairRequirement(
    "ALPHA_V1_PRODUCT_TAKEOVER_P32_NATIVE_PLAYER_MARKER_RENDERER_ANCHOR_QUALIFICATION",
    "alpha.v1.product-takeover.native-player-marker-renderer-anchor-qualification-v1",
    "bd75c3b5f7fd20fe004fae21142a0fa19942e076",
    "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P32_NATIVE_PLAYER_MARKER_RENDERER_ANCHOR_QUALIFICATION_RESULT.json",
)


class RebuildError(final.CandidateError):
    pass


def _assert_no_true_movement(value: Any, where: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            here = f"{where}.{key}"
            if key in {"alphaLiveMoved", "alphaLivePromoted", "promotionPerformed"} and child is True:
                raise RebuildError(f"forbidden alpha-live/promotion movement at {here}")
            _assert_no_true_movement(child, here)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_true_movement(child, f"{where}[{index}]")


def _resolve_exact_source(root: Path, source: str) -> str:
    normalized = source.strip().lower()
    if not _SHA40_RE.fullmatch(normalized):
        raise RebuildError("EXACT_SOURCE_COMMIT_REQUIRED: --source must be one full 40-hex commit SHA")
    try:
        resolved = final._resolve_commit(root, normalized)
    except final.CandidateError as exc:
        raise RebuildError(f"SOURCE_COMMIT_NOT_FOUND: {normalized}") from exc
    if resolved != normalized:
        raise RebuildError(f"SOURCE_COMMIT_READBACK_MISMATCH: requested {normalized}, resolved {resolved}")
    return normalized


def _assert_not_historical_source(source_commit: str) -> None:
    if source_commit == HISTORICAL_P19_SOURCE_COMMIT:
        raise RebuildError(
            "STALE_P19_SOURCE_COMMIT_REJECTED: historical P19 source predates required accepted repairs"
        )


def _source_json(root: Path, source_commit: str, path: str, label: str) -> dict[str, Any]:
    try:
        value = final._try_git_json(root, source_commit, path)
    except final.CandidateError as exc:
        raise RebuildError(f"{label}: invalid authority JSON at exact source: {path}") from exc
    if value is None:
        raise RebuildError(f"{label}: required terminal RESULT missing at exact source: {path}")
    return value


def _validate_required_authority(
    root: Path,
    source_commit: str,
    requirement: RepairRequirement,
) -> dict[str, Any]:
    raw = _source_json(root, source_commit, requirement.result_path, requirement.stage_id)
    if raw.get("schema") != "wof-alpha-worker-result-v1":
        raise RebuildError(f"{requirement.stage_id}: result schema mismatch")
    if raw.get("stageId") != requirement.stage_id:
        raise RebuildError(f"{requirement.stage_id}: result stageId mismatch")
    if raw.get("dedupKey") != requirement.dedup_key:
        raise RebuildError(f"{requirement.stage_id}: result dedupKey mismatch")
    if raw.get("state") != "COMPLETE" or raw.get("integrationReady") is not True:
        raise RebuildError(
            f"{requirement.stage_id}: PM-accepted terminal COMPLETE/integrationReady=true required"
        )
    if raw.get("testedCommit") != requirement.tested_commit:
        raise RebuildError(f"{requirement.stage_id}: exact testedCommit mismatch")
    final._assert_safety(raw.get("safety"), requirement.stage_id)
    _assert_no_true_movement(raw, requirement.stage_id)
    return {
        "stageId": requirement.stage_id,
        "dedupKey": requirement.dedup_key,
        "testedCommit": requirement.tested_commit,
        "resultPath": requirement.result_path,
        "resultGitBlobSha": final._blob_at(root, source_commit, requirement.result_path),
        "pmAccepted": True,
        "terminalState": "COMPLETE",
        "integrationReady": True,
    }


def _validate_p32_blocked_not_required(root: Path, source_commit: str) -> dict[str, Any]:
    raw = _source_json(root, source_commit, P32_BLOCKED.result_path, "P32")
    if raw.get("schema") != "wof-alpha-worker-result-v1":
        raise RebuildError("P32: result schema mismatch")
    if raw.get("stageId") != P32_BLOCKED.stage_id or raw.get("dedupKey") != P32_BLOCKED.dedup_key:
        raise RebuildError("P32: terminal authority identity mismatch")
    if raw.get("testedCommit") != P32_BLOCKED.tested_commit:
        raise RebuildError("P32: testedCommit mismatch")
    if raw.get("state") != "BLOCKED" or raw.get("integrationReady") is not False:
        raise RebuildError("P32: terminal BLOCKED/integrationReady=false authority must remain truthful")
    final._assert_safety(raw.get("safety"), "P32")
    _assert_no_true_movement(raw, "P32")
    return {
        "stageId": P32_BLOCKED.stage_id,
        "dedupKey": P32_BLOCKED.dedup_key,
        "testedCommit": P32_BLOCKED.tested_commit,
        "resultPath": P32_BLOCKED.result_path,
        "resultGitBlobSha": final._blob_at(root, source_commit, P32_BLOCKED.result_path),
        "terminalState": "BLOCKED",
        "integrationReady": False,
        "required": False,
        "reason": "P32 is terminal BLOCKED and is not a PM-accepted repair candidate for P33.",
    }


def _assert_required_containment(root: Path, source_commit: str) -> list[dict[str, Any]]:
    _assert_not_historical_source(source_commit)
    rows: list[dict[str, Any]] = []
    for requirement in REQUIRED_ACCEPTED_REPAIRS:
        try:
            resolved = final._resolve_commit(root, requirement.tested_commit)
        except final.CandidateError as exc:
            raise RebuildError(
                f"REQUIRED_TESTED_COMMIT_NOT_FOUND: {requirement.stage_id} {requirement.tested_commit}"
            ) from exc
        if resolved != requirement.tested_commit:
            raise RebuildError(
                f"REQUIRED_TESTED_COMMIT_READBACK_MISMATCH: {requirement.stage_id}"
            )
        cp = final._run_git(
            root,
            "merge-base",
            "--is-ancestor",
            requirement.tested_commit,
            source_commit,
            check=False,
        )
        if cp.returncode != 0:
            raise RebuildError(
                "SOURCE_COMMIT_MISSING_REQUIRED_TESTED_COMMIT: "
                f"{source_commit} does not contain {requirement.stage_id} "
                f"{requirement.tested_commit}"
            )
        rows.append(
            {
                "stageId": requirement.stage_id,
                "testedCommit": requirement.tested_commit,
                "isAncestor": True,
            }
        )
    return rows


def _required_map() -> dict[str, str]:
    return {item.stage_id: item.tested_commit for item in REQUIRED_ACCEPTED_REPAIRS}


def _safe_local_path(root: Path, relative_path: str, label: str) -> Path:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise RebuildError(f"{label}: unsafe path outside repository: {relative_path!r}") from exc
    return candidate


def _read_json_file(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise RebuildError(f"{label}: missing file {path}") from exc
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except Exception as exc:
        raise RebuildError(f"{label}: invalid UTF-8 JSON {path}") from exc
    if not isinstance(value, dict):
        raise RebuildError(f"{label}: JSON root must be an object")
    return value


def _read_base_binding(
    root: Path,
    pointer_path: Path,
    source_commit: str,
    *,
    build_result: Mapping[str, Any] | None = None,
    verify_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    pointer = _read_json_file(pointer_path, "base pointer")
    if pointer.get("schema") != final.POINTER_SCHEMA or pointer.get("state") != "READY":
        raise RebuildError("base final-candidate pointer schema/state mismatch")
    if pointer.get("sourceCommit") != source_commit:
        raise RebuildError("base pointer sourceCommit mismatch")
    package_version = pointer.get("packageVersion")
    if not isinstance(package_version, str) or not package_version:
        raise RebuildError("base pointer packageVersion missing")

    candidate_rel = pointer.get("candidatePath")
    attestation_rel = pointer.get("attestationPath")
    if not isinstance(candidate_rel, str) or not isinstance(attestation_rel, str):
        raise RebuildError("base pointer candidate/attestation path missing")
    candidate_path = _safe_local_path(root, candidate_rel, "candidate")
    attestation_path = _safe_local_path(root, attestation_rel, "attestation")
    candidate_sha = final._sha256_file(candidate_path)
    attestation_sha = final._sha256_file(attestation_path)
    if candidate_sha != pointer.get("candidateSha256"):
        raise RebuildError("candidate SHA256 readback mismatch")
    if attestation_sha != pointer.get("attestationSha256"):
        raise RebuildError("attestation SHA256 readback mismatch")

    candidate = _read_json_file(candidate_path, "candidate")
    attestation = _read_json_file(attestation_path, "attestation")
    for label, payload in (("candidate", candidate), ("attestation", attestation)):
        if payload.get("sourceCommit") != source_commit:
            raise RebuildError(f"{label} sourceCommit exact readback mismatch")
        if payload.get("packageVersion") != package_version:
            raise RebuildError(f"{label} packageVersion exact readback mismatch")
        _assert_no_true_movement(payload, label)
    if attestation.get("candidatePath") != candidate_rel:
        raise RebuildError("attestation candidatePath mismatch")
    if attestation.get("candidateSha256") != candidate_sha:
        raise RebuildError("attestation candidateSha256 mismatch")
    final._assert_safety(candidate.get("safety"), "candidate")
    final._assert_safety(attestation.get("safety"), "attestation")
    _assert_no_true_movement(pointer, "pointer")

    if build_result is not None:
        for key, expected in {
            "sourceCommit": source_commit,
            "packageVersion": package_version,
            "candidatePath": candidate_rel,
            "candidateSha256": candidate_sha,
            "attestationPath": attestation_rel,
            "attestationSha256": attestation_sha,
        }.items():
            if build_result.get(key) != expected:
                raise RebuildError(f"base build result readback mismatch for {key}")
    if verify_result is not None:
        for key, expected in {
            "sourceCommit": source_commit,
            "packageVersion": package_version,
            "candidatePath": candidate_rel,
            "candidateSha256": candidate_sha,
            "attestationPath": attestation_rel,
            "attestationSha256": attestation_sha,
        }.items():
            if verify_result.get(key) != expected:
                raise RebuildError(f"base verify result readback mismatch for {key}")

    return {
        "pointer": pointer,
        "sourceCommit": source_commit,
        "packageVersion": package_version,
        "candidatePath": candidate_rel,
        "candidateSha256": candidate_sha,
        "attestationPath": attestation_rel,
        "attestationSha256": attestation_sha,
        "candidateGeneratedAtUtc": candidate.get("generatedAtUtc"),
    }


def _rebuild_manifest(
    binding: Mapping[str, Any],
    authority_rows: list[dict[str, Any]],
    containment_rows: list[dict[str, Any]],
    p32_row: Mapping[str, Any],
) -> dict[str, Any]:
    by_stage = {row["stageId"]: row for row in containment_rows}
    accepted: list[dict[str, Any]] = []
    for row in authority_rows:
        merged = dict(row)
        merged["isAncestor"] = bool(by_stage.get(row["stageId"], {}).get("isAncestor"))
        accepted.append(merged)
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "state": "REBUILD_CONTRACT_VERIFIED",
        "sourceCommit": binding["sourceCommit"],
        "packageVersion": binding["packageVersion"],
        "candidatePath": binding["candidatePath"],
        "candidateSha256": binding["candidateSha256"],
        "attestationPath": binding["attestationPath"],
        "attestationSha256": binding["attestationSha256"],
        "requiredTestedCommits": _required_map(),
        "requiredAcceptedRepairs": accepted,
        "excludedBlockedRepairs": [dict(p32_row)],
        "historicalP19Candidate": {
            "sourceCommit": HISTORICAL_P19_SOURCE_COMMIT,
            "acceptedAsPostRepairSource": False,
        },
        "deterministicInputs": {
            "sourceCommit": binding["sourceCommit"],
            "packageVersion": binding["packageVersion"],
            "candidateSha256": binding["candidateSha256"],
            "attestationSha256": binding["attestationSha256"],
            "requiredTestedCommits": _required_map(),
        },
        "candidateGeneratedAtUtc": binding.get("candidateGeneratedAtUtc"),
        "ownerVisualAcceptance": "NOT_RUN",
        "realWofAcceptance": "NOT_RUN",
        "alphaLiveMoved": False,
        "alphaLivePromoted": False,
        "promotionPerformed": False,
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "legacySpatialFallback": False,
            "screenshotProductionCoordinates": False,
            "worldProjectionProductionCoordinates": False,
            "guessedAddresses": False,
            "alphaLiveMoved": False,
        },
    }


def _restore_pointer(pointer: Path, previous: bytes | None) -> None:
    if previous is None:
        pointer.unlink(missing_ok=True)
    else:
        final._atomic_write(pointer, previous)


def _validate_manifest_binding(
    root: Path,
    pointer: Mapping[str, Any],
    manifest: Mapping[str, Any],
    manifest_raw: bytes,
    authority_rows: list[dict[str, Any]],
    containment_rows: list[dict[str, Any]],
    p32_row: Mapping[str, Any],
) -> None:
    manifest_sha = final._sha256_bytes(manifest_raw)
    if pointer.get("manifestSha256") != manifest_sha:
        raise RebuildError("manifest SHA256 exact readback mismatch")
    required = _required_map()
    if pointer.get("requiredTestedCommits") != required:
        raise RebuildError("requiredTestedCommits exact set/value mismatch")
    for key in ("sourceCommit", "packageVersion", "candidatePath", "candidateSha256"):
        if manifest.get(key) != pointer.get(key):
            raise RebuildError(f"manifest {key} exact readback mismatch")
    if manifest.get("schema") != SCHEMA or manifest.get("state") != "REBUILD_CONTRACT_VERIFIED":
        raise RebuildError("post-repair rebuild manifest schema/state mismatch")
    if manifest.get("requiredTestedCommits") != required:
        raise RebuildError("manifest requiredTestedCommits mismatch")
    expected_manifest = _rebuild_manifest(
        {
            "sourceCommit": pointer["sourceCommit"],
            "packageVersion": pointer["packageVersion"],
            "candidatePath": pointer["candidatePath"],
            "candidateSha256": pointer["candidateSha256"],
            "attestationPath": pointer["attestationPath"],
            "attestationSha256": pointer["attestationSha256"],
            "candidateGeneratedAtUtc": manifest.get("candidateGeneratedAtUtc"),
        },
        authority_rows,
        containment_rows,
        p32_row,
    )
    if final._json_bytes(manifest) != final._json_bytes(expected_manifest):
        raise RebuildError("deterministic rebuild manifest content mismatch")
    _assert_no_true_movement(manifest, "manifest")


def verify(root: Path, pointer_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    pointer_path = (pointer_path or root / DEFAULT_POINTER_REL).resolve()
    pointer = _read_json_file(pointer_path, "post-repair pointer")
    manifest_rel = pointer.get("manifestPath")
    manifest_sha = pointer.get("manifestSha256")
    required_map = pointer.get("requiredTestedCommits")
    if not isinstance(manifest_rel, str) or not manifest_rel:
        raise RebuildError("STALE_PRE_REPAIR_POINTER_REJECTED: manifestPath missing")
    if not isinstance(manifest_sha, str) or not _SHA256_RE.fullmatch(manifest_sha):
        raise RebuildError("STALE_PRE_REPAIR_POINTER_REJECTED: manifestSha256 missing/invalid")
    if required_map != _required_map():
        raise RebuildError("STALE_PRE_REPAIR_POINTER_REJECTED: requiredTestedCommits mismatch")

    source_commit = _resolve_exact_source(root, str(pointer.get("sourceCommit") or ""))
    _assert_not_historical_source(source_commit)
    authority_rows = [
        _validate_required_authority(root, source_commit, requirement)
        for requirement in REQUIRED_ACCEPTED_REPAIRS
    ]
    p32_row = _validate_p32_blocked_not_required(root, source_commit)
    containment_rows = _assert_required_containment(root, source_commit)

    alpha_before = final._observe_alpha_live(root)
    base_verify = final.verify(root, pointer_path)
    binding = _read_base_binding(
        root,
        pointer_path,
        source_commit,
        verify_result=base_verify,
    )
    manifest_path = _safe_local_path(root, manifest_rel, "rebuild manifest")
    try:
        manifest_raw = manifest_path.read_bytes()
    except FileNotFoundError as exc:
        raise RebuildError("post-repair rebuild manifest missing") from exc
    manifest = _read_json_file(manifest_path, "rebuild manifest")
    _validate_manifest_binding(
        root,
        pointer,
        manifest,
        manifest_raw,
        authority_rows,
        containment_rows,
        p32_row,
    )
    if binding["packageVersion"] != pointer.get("packageVersion"):
        raise RebuildError("packageVersion exact readback mismatch")
    alpha_after = final._observe_alpha_live(root)
    if alpha_before != alpha_after:
        raise RebuildError(
            f"alpha-live moved during post-repair verify: before={alpha_before}, after={alpha_after}"
        )
    return {
        "state": "VERIFIED",
        "rebuildContractState": "REBUILD_CONTRACT_VERIFIED",
        "sourceCommit": source_commit,
        "packageVersion": binding["packageVersion"],
        "candidatePath": binding["candidatePath"],
        "candidateSha256": binding["candidateSha256"],
        "manifestPath": manifest_rel,
        "manifestSha256": manifest_sha,
        "requiredTestedCommits": _required_map(),
        "p32Required": False,
        "alphaLivePromoted": False,
        "promotionPerformed": False,
    }


def build(
    root: Path,
    source: str,
    output_dir: Path | None = None,
    pointer_path: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    source_commit = _resolve_exact_source(root, source)
    _assert_not_historical_source(source_commit)
    authority_rows = [
        _validate_required_authority(root, source_commit, requirement)
        for requirement in REQUIRED_ACCEPTED_REPAIRS
    ]
    p32_row = _validate_p32_blocked_not_required(root, source_commit)
    containment_rows = _assert_required_containment(root, source_commit)

    out_dir = (output_dir or root / DEFAULT_OUTPUT_REL).resolve()
    pointer = (pointer_path or root / DEFAULT_POINTER_REL).resolve()
    previous_pointer = pointer.read_bytes() if pointer.is_file() else None
    staged_pointer = pointer.with_name(f".{pointer.name}.p33-{os.getpid()}.tmp")
    staged_pointer.unlink(missing_ok=True)
    alpha_before = final._observe_alpha_live(root)
    try:
        base = final.build(root, source_commit, out_dir, staged_pointer)
        if not base.get("emitted"):
            return {
                **dict(base),
                "rebuildContractState": "NOT_EMITTED",
                "requiredTestedCommits": _required_map(),
                "p32Required": False,
            }
        base_verified = final.verify(root, staged_pointer)
        binding = _read_base_binding(
            root,
            staged_pointer,
            source_commit,
            build_result=base,
            verify_result=base_verified,
        )
        manifest = _rebuild_manifest(binding, authority_rows, containment_rows, p32_row)
        manifest_bytes = final._json_bytes(manifest)
        manifest_sha = final._sha256_bytes(manifest_bytes)
        manifest_path = out_dir / f"ALPHA_V1_POST_REPAIR_REBUILD_{source_commit[:12]}.manifest.json"
        manifest_rel = manifest_path.relative_to(root).as_posix()
        final._atomic_write(manifest_path, manifest_bytes)

        pointer_value = dict(binding["pointer"])
        pointer_value.update(
            {
                "manifestPath": manifest_rel,
                "manifestSha256": manifest_sha,
                "requiredTestedCommits": _required_map(),
                "postRepairRebuildSchema": SCHEMA,
                "postRepairRebuildVersion": VERSION,
                "postRepairRebuildState": "REBUILD_CONTRACT_VERIFIED",
                "p32Required": False,
                "alphaLiveMoved": False,
                "alphaLivePromoted": False,
                "promotionPerformed": False,
            }
        )
        pointer_bytes = final._json_bytes(pointer_value)
        final._atomic_write(staged_pointer, pointer_bytes)
        prepublish = verify(root, staged_pointer)
        if final._observe_alpha_live(root) != alpha_before:
            raise RebuildError("alpha-live moved before post-repair pointer publication")

        final._atomic_write(pointer, pointer_bytes)
        try:
            readback = verify(root, pointer)
            if readback != prepublish:
                raise RebuildError("published pointer verification readback mismatch")
            if pointer.read_bytes() != pointer_bytes:
                raise RebuildError("published pointer bytes differ from deterministic pointer bytes")
            if manifest_path.read_bytes() != manifest_bytes:
                raise RebuildError("published rebuild manifest bytes differ from deterministic bytes")
            if final._observe_alpha_live(root) != alpha_before:
                raise RebuildError("alpha-live moved during post-repair pointer publication")
        except Exception:
            _restore_pointer(pointer, previous_pointer)
            raise
        return {
            **readback,
            "emitted": True,
            "rebuildManifestDeterministic": True,
            "alphaLiveObserved": alpha_before,
        }
    finally:
        staged_pointer.unlink(missing_ok=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Fail-closed post-repair Alpha final-candidate rebuild wrapper. "
            "Requires one exact source commit containing all PM-accepted P29/P30/P31 tested commits."
        )
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--source", required=True)
    b.add_argument("--output-dir", type=Path)
    b.add_argument("--pointer", type=Path)
    v = sub.add_parser("verify")
    v.add_argument("--pointer", type=Path)
    bv = sub.add_parser("build-verify")
    bv.add_argument("--source", required=True)
    bv.add_argument("--output-dir", type=Path)
    bv.add_argument("--pointer", type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "build":
            result = build(args.root, args.source, args.output_dir, args.pointer)
        elif args.command == "verify":
            result = verify(args.root, args.pointer)
        else:
            result = build(args.root, args.source, args.output_dir, args.pointer)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        if isinstance(result, dict) and result.get("state") == "WAITING_FOR_P18":
            return 4
        return 0
    except (RebuildError, final.CandidateError) as exc:
        print(
            json.dumps({"state": "FAILED", "error": str(exc)}, ensure_ascii=False, indent=2, sort_keys=True),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
