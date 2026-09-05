from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import refresh_manifest as refresh

SCHEMA = "wof-alpha-final-canonical-candidate-attestation-v1"
VERSION = 1
POINTER_SCHEMA = "wof-alpha-latest-final-canonical-candidate-v1"
BUILDER_REL = "parallel/OWNER_ONECLICK/final_canonical_candidate.py"
DEFAULT_OUTPUT_REL = Path("parallel/OWNER_ONECLICK/CANDIDATES/FINAL_CANONICAL")
DEFAULT_POINTER_REL = Path("parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json")

P15_RESULT = "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE_RESULT.json"
P16_RESULT = "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE_RESULT.json"
P17_RESULT = "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P17_OWNER_FINAL_ACCEPTANCE_ORCHESTRATOR_RESULT.json"
P18_RESULT = "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P18_MAINTAINED_HUD_CANONICAL_DRAW_ACKNOWLEDGEMENT_RESULT.json"
W3_RESULT = "parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2_RESULT.json"

STAGES: tuple[tuple[str, str, str, str], ...] = (
    ("P15", "ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE", "alpha.v1.product-takeover.canonical-product-convergence-package-candidate-v1", P15_RESULT),
    ("P16", "ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE", "alpha.v1.product-takeover.owner-canonical-status-acceptance-evidence-v1", P16_RESULT),
    ("P17", "ALPHA_V1_PRODUCT_TAKEOVER_P17_OWNER_FINAL_ACCEPTANCE_ORCHESTRATOR", "alpha.v1.product-takeover.owner-final-acceptance-orchestrator-v1", P17_RESULT),
    ("P18", "ALPHA_V1_PRODUCT_TAKEOVER_P18_MAINTAINED_HUD_CANONICAL_DRAW_ACKNOWLEDGEMENT", "alpha.v1.product-takeover.maintained-hud-canonical-draw-acknowledgement-v1", P18_RESULT),
)

P16_RUNTIME_PATHS = (
    "parallel/PYLAUNCH/wof_launcher/canonical_owner_status.py",
    "parallel/PYLAUNCH/wof_launcher/canonical_acceptance_evidence.py",
    "parallel/PYLAUNCH/wof_launcher/state.py",
    "parallel/PYLAUNCH/wof_launcher/tray.py",
)
P17_RUNTIME_PATHS = (
    "parallel/OWNER_ACCEPTANCE/final_acceptance_orchestrator.py",
    "parallel/OWNER_ACCEPTANCE/WOF_ALPHA_FINAL_ACCEPTANCE.cmd",
)
P18_RUNTIME_PATHS = (
    "product/alpha/wof_alpha_hud.js",
    "parallel/PYLAUNCH/wof_launcher/canonical_draw_evidence.py",
)
W3_ACCEPTANCE_PATHS = (
    "parallel/RENDER_AUTHORITY_V2/run_long_qualification.py",
    "parallel/RENDER_AUTHORITY_V2/qualification_analyzer.py",
    "parallel/RENDER_AUTHORITY_V2/measurement_runner.py",
)


class CandidateError(RuntimeError):
    pass


def _run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(["git", *args], cwd=root, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and cp.returncode:
        raise CandidateError(cp.stderr.strip() or cp.stdout.strip() or f"git {' '.join(args)} failed")
    return cp


def _resolve_commit(root: Path, source: str) -> str:
    commit = _run_git(root, "rev-parse", f"{source}^{{commit}}").stdout.strip().lower()
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise CandidateError(f"invalid source commit: {source!r}")
    return commit


def _git_show_bytes(root: Path, commit: str, path: str) -> bytes:
    cp = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if cp.returncode:
        raise FileNotFoundError(path)
    return cp.stdout


def _try_git_json(root: Path, commit: str, path: str) -> dict[str, Any] | None:
    try:
        raw = _git_show_bytes(root, commit, path)
    except FileNotFoundError:
        return None
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except Exception as exc:
        raise CandidateError(f"invalid JSON at source commit: {path}") from exc
    if not isinstance(value, dict):
        raise CandidateError(f"JSON root is not an object: {path}")
    return value


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    try:
        tmp.write_bytes(data)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def _assert_safety(value: Any, source: str) -> None:
    if not isinstance(value, Mapping):
        raise CandidateError(f"{source}: safety object missing")
    for key, wanted in {"readOnly": True, "ramWrites": 0, "inputInjection": False}.items():
        if value.get(key) != wanted:
            raise CandidateError(f"{source}: safety mismatch {key}={value.get(key)!r}")
    for key in ("legacySpatialFallback", "screenshotProductionCoordinates", "worldProjectionProductionCoordinates", "guessedAddresses", "alphaLiveMoved"):
        if key in value and value.get(key) is not False:
            raise CandidateError(f"{source}: forbidden safety flag {key}={value.get(key)!r}")


def _walk_proof_fields(value: Any, where: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            here = f"{where}.{key}"
            if key in {"visibleProof", "ownerVisualAcceptance"} and child not in (None, "NOT_PROVEN", "NOT_RUN"):
                raise CandidateError(f"unsupported visual proof claim at {here}: {child!r}")
            if key == "realWofAcceptance" and child not in (None, "NOT_RUN"):
                raise CandidateError(f"unsupported real-WOF acceptance claim at {here}: {child!r}")
            _walk_proof_fields(child, here)
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            _walk_proof_fields(child, f"{where}[{idx}]")


def _validate_result(label: str, expected_stage: str, expected_dedup: str, raw: dict[str, Any], *, p18_wait: bool = False) -> tuple[bool, str | None]:
    if raw.get("schema") != "wof-alpha-worker-result-v1":
        raise CandidateError(f"{label}: result schema mismatch")
    if raw.get("stageId") != expected_stage:
        raise CandidateError(f"{label}: stageId mismatch")
    if raw.get("dedupKey") != expected_dedup:
        raise CandidateError(f"{label}: dedupKey mismatch")
    _assert_safety(raw.get("safety"), label)
    _walk_proof_fields(raw, label)
    if raw.get("state") != "COMPLETE" or raw.get("integrationReady") is not True:
        if p18_wait:
            return False, f"P18 is {raw.get('state')!r}/integrationReady={raw.get('integrationReady')!r}"
        raise CandidateError(f"{label}: terminal COMPLETE/integrationReady=true required")
    commits = raw.get("implementationCommits")
    if not isinstance(commits, list) or not commits:
        raise CandidateError(f"{label}: implementationCommits missing")
    for commit in commits:
        if not isinstance(commit, str) or len(commit) != 40:
            raise CandidateError(f"{label}: invalid implementation commit {commit!r}")
    return True, None


def _stage_results(root: Path, source: str) -> tuple[dict[str, dict[str, Any]], dict[str, Any] | None]:
    results: dict[str, dict[str, Any]] = {}
    for label, stage, dedup, path in STAGES:
        raw = _try_git_json(root, source, path)
        if raw is None:
            if label == "P18":
                return results, {"state": "WAITING_FOR_P18", "reason": "P18 result is missing at the exact source commit", "resultPath": path}
            raise CandidateError(f"{label}: required result missing at exact source commit: {path}")
        ready, reason = _validate_result(label, stage, dedup, raw, p18_wait=(label == "P18"))
        if not ready:
            return results, {"state": "WAITING_FOR_P18", "reason": reason, "resultPath": path}
        results[label] = raw
    return results, None


def _assert_ancestors(root: Path, source: str, results: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for label in ("P15", "P16", "P17", "P18"):
        for commit in results[label].get("implementationCommits") or []:
            cp = _run_git(root, "merge-base", "--is-ancestor", commit, source, check=False)
            if cp.returncode != 0:
                raise CandidateError(f"{label}: implementation commit is not an ancestor of source: {commit}")
            rows.append({"stage": label, "commit": commit, "isAncestor": True})
    return rows


def _blob_at(root: Path, source: str, path: str) -> str:
    try:
        return refresh._blob_at(root, source, path)
    except Exception as exc:
        raise CandidateError(f"required candidate file missing or not a blob: {path}") from exc


def _observe_alpha_live(root: Path) -> str | None:
    for ref in ("refs/remotes/origin/alpha-live", "refs/heads/alpha-live"):
        cp = _run_git(root, "rev-parse", "--verify", f"{ref}^{{commit}}", check=False)
        if cp.returncode == 0:
            value = cp.stdout.strip().lower()
            if len(value) == 40:
                return value
    return None


def _w3_summary(root: Path, source: str) -> dict[str, Any]:
    raw = _try_git_json(root, source, W3_RESULT)
    if raw is None:
        return {"resultPath": W3_RESULT, "resultState": "MISSING", "liveQualification": "NOT_RUN", "integrationReady": False}
    _assert_safety(raw.get("safety"), "W3")
    _walk_proof_fields(raw, "W3")
    proof = raw.get("productProof") if isinstance(raw.get("productProof"), Mapping) else {}
    classification = proof.get("classification")
    status = proof.get("status")
    if classification == "INCONCLUSIVE" or status == "LIVE_EVIDENCE_REQUIRED" or raw.get("state") == "SUBCOMPLETE":
        live = "INCONCLUSIVE"
    elif raw.get("state") == "COMPLETE" and classification in {"PASS", "PROVEN"}:
        live = "PASS"
    else:
        live = "NOT_RUN"
    return {"resultPath": W3_RESULT, "resultState": raw.get("state"), "integrationReady": raw.get("integrationReady") is True, "liveQualification": live, "classification": classification, "proofStatus": status, "blocker": raw.get("blocker")}


def _result_pin(root: Path, source: str, label: str, result: Mapping[str, Any]) -> dict[str, Any]:
    spec = next(row for row in STAGES if row[0] == label)
    path = spec[3]
    return {"stageId": result.get("stageId"), "dedupKey": result.get("dedupKey"), "state": result.get("state"), "integrationReady": result.get("integrationReady"), "resultPath": path, "resultGitBlobSha": _blob_at(root, source, path), "implementationCommits": list(result.get("implementationCommits") or [])}


def critical_paths() -> tuple[str, ...]:
    return tuple(dict.fromkeys((*refresh.CANONICAL_STACK_PATHS, *P16_RUNTIME_PATHS, *P17_RUNTIME_PATHS, *P18_RUNTIME_PATHS, *W3_ACCEPTANCE_PATHS)))


def _extend_manifest(root: Path, source: str, base: dict[str, Any], results: Mapping[str, Mapping[str, Any]], ancestry: list[dict[str, Any]], w3: Mapping[str, Any]) -> dict[str, Any]:
    manifest = json.loads(json.dumps(base))
    if manifest.get("schema") != refresh.SCHEMA or manifest.get("sourceCommit") != source:
        raise CandidateError("refresh_manifest returned unexpected schema/source")
    _assert_safety(manifest.get("safety"), "base candidate")
    if (manifest.get("safety") or {}).get("legacySpatialFallback") is not False:
        raise CandidateError("base candidate must explicitly disable legacySpatialFallback")
    components = manifest.get("components")
    if not isinstance(components, dict):
        raise CandidateError("base candidate components missing")
    canonical = components.get("canonicalProductConvergence")
    if not isinstance(canonical, dict) or canonical.get("legacySpatialFallback") is not False:
        raise CandidateError("P15 canonical convergence safety metadata missing")
    if canonical.get("alphaLivePromoted") is not False:
        raise CandidateError("P15 canonical candidate unexpectedly reports alpha-live promotion")

    file_map: dict[str, str] = {}
    for row in manifest.get("files") or []:
        if not isinstance(row, Mapping) or not isinstance(row.get("path"), str) or not isinstance(row.get("gitBlobSha"), str):
            raise CandidateError("base manifest file row malformed")
        file_map[str(row["path"])] = str(row["gitBlobSha"]).lower()
    for path in critical_paths():
        file_map[path] = _blob_at(root, source, path)
    manifest["files"] = [{"path": path, "gitBlobSha": file_map[path]} for path in sorted(file_map)]
    pins = {label: _result_pin(root, source, label, results[label]) for label in ("P15", "P16", "P17", "P18")}
    blobs = {path: file_map[path] for path in critical_paths()}
    components["finalCanonicalRelease"] = {
        "schema": SCHEMA,
        "version": VERSION,
        "stageId": "ALPHA_V1_PRODUCT_TAKEOVER_P19_FINAL_CANONICAL_CANDIDATE_REBUILD_ATTESTATION",
        "sourceCommit": source,
        "baseSelectionPolicy": manifest.get("selectionPolicy"),
        "resultPins": pins,
        "implementationAncestry": ancestry,
        "criticalRuntimeBlobs": blobs,
        "acceptanceEntrypoint": "parallel/OWNER_ACCEPTANCE/WOF_ALPHA_FINAL_ACCEPTANCE.cmd",
        "w3Qualification": dict(w3),
        "ownerVisualAcceptance": "NOT_RUN",
        "realWofAcceptance": "NOT_RUN",
        "alphaLivePromoted": False,
        "legacySpatialFallback": False,
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False},
    }
    manifest["generator"] = BUILDER_REL
    manifest["safety"]["legacySpatialFallback"] = False
    refresh.verify_publishable_manifest(manifest)
    return manifest


def verify_manifest_blobs(root: Path, manifest: Mapping[str, Any]) -> None:
    source = manifest.get("sourceCommit")
    if not isinstance(source, str) or len(source) != 40:
        raise CandidateError("candidate sourceCommit invalid")
    seen: set[str] = set()
    for row in manifest.get("files") or []:
        if not isinstance(row, Mapping):
            raise CandidateError("candidate file row malformed")
        path, expected = row.get("path"), row.get("gitBlobSha")
        if not isinstance(path, str) or not isinstance(expected, str):
            raise CandidateError("candidate file row missing path/blob")
        if path in seen:
            raise CandidateError(f"duplicate candidate file path: {path}")
        seen.add(path)
        actual = _blob_at(root, source, path)
        if actual != expected.lower():
            raise CandidateError(f"blob mismatch for {path}: expected {expected}, actual {actual}")
    missing = set(critical_paths()) - seen
    if missing:
        raise CandidateError("candidate missing critical runtime files: " + ", ".join(sorted(missing)))


def _attestation(root: Path, source: str, candidate_rel: str, candidate: Mapping[str, Any], candidate_sha: str, results: Mapping[str, Mapping[str, Any]], ancestry: list[dict[str, Any]], w3: Mapping[str, Any], alpha_previous: str | None, alpha_current: str | None) -> dict[str, Any]:
    final = ((candidate.get("components") or {}).get("finalCanonicalRelease") or {})
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "sourceCommit": source,
        "packageVersion": candidate.get("packageVersion"),
        "candidatePath": candidate_rel,
        "candidateSha256": candidate_sha,
        "selectedFileCount": len(candidate.get("files") or []),
        "stageResults": {label: _result_pin(root, source, label, results[label]) for label in ("P15", "P16", "P17", "P18")},
        "implementationAncestry": ancestry,
        "criticalRuntimeBlobs": dict(final.get("criticalRuntimeBlobs") or {}),
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False},
        "w3LiveQualification": w3.get("liveQualification"),
        "w3ResultState": w3.get("resultState"),
        "ownerVisualAcceptance": "NOT_RUN",
        "realWofAcceptance": "NOT_RUN",
        "alphaLivePromoted": False,
        "alphaLiveObservedPrevious": alpha_previous,
        "alphaLiveObservedCurrent": alpha_current,
        "attestedAtUtc": candidate.get("generatedAtUtc"),
    }


def build(root: Path, source: str, output_dir: Path | None = None, pointer_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    source_commit = _resolve_commit(root, source)
    results, wait = _stage_results(root, source_commit)
    if wait is not None:
        return {**wait, "sourceCommit": source_commit, "emitted": False}
    ancestry = _assert_ancestors(root, source_commit, results)
    w3 = _w3_summary(root, source_commit)
    alpha_before = _observe_alpha_live(root)
    base = refresh.generate_manifest(root, source_commit, canonical_candidate=True)
    candidate = _extend_manifest(root, source_commit, base, results, ancestry, w3)
    verify_manifest_blobs(root, candidate)

    out_dir = (output_dir or root / DEFAULT_OUTPUT_REL).resolve()
    pointer = (pointer_path or root / DEFAULT_POINTER_REL).resolve()
    short = source_commit[:12]
    candidate_path = out_dir / f"ALPHA_V1_FINAL_CANONICAL_CANDIDATE_{short}.json"
    attestation_path = out_dir / f"ALPHA_V1_FINAL_CANONICAL_CANDIDATE_{short}.attestation.json"
    candidate_rel = candidate_path.relative_to(root).as_posix()
    attestation_rel = attestation_path.relative_to(root).as_posix()
    candidate_bytes = _json_bytes(candidate)
    candidate_sha = _sha256_bytes(candidate_bytes)
    p15 = results["P15"]
    alpha_previous = p15.get("alphaLiveCommitObserved") if isinstance(p15.get("alphaLiveCommitObserved"), str) else None
    attestation = _attestation(root, source_commit, candidate_rel, candidate, candidate_sha, results, ancestry, w3, alpha_previous, alpha_before)
    attestation_bytes = _json_bytes(attestation)
    attestation_sha = _sha256_bytes(attestation_bytes)
    alpha_after = _observe_alpha_live(root)
    if alpha_before != alpha_after:
        raise CandidateError(f"alpha-live moved during candidate build: before={alpha_before}, after={alpha_after}")
    pointer_value = {
        "schema": POINTER_SCHEMA,
        "version": VERSION,
        "state": "READY",
        "sourceCommit": source_commit,
        "packageVersion": candidate.get("packageVersion"),
        "candidatePath": candidate_rel,
        "candidateSha256": candidate_sha,
        "attestationPath": attestation_rel,
        "attestationSha256": attestation_sha,
        "selectedFileCount": len(candidate.get("files") or []),
        "stageStates": {label: "COMPLETE" for label in ("P15", "P16", "P17", "P18")},
        "w3LiveQualification": w3.get("liveQualification"),
        "ownerVisualAcceptance": "NOT_RUN",
        "alphaLivePromoted": False,
    }
    _atomic_write(candidate_path, candidate_bytes)
    _atomic_write(attestation_path, attestation_bytes)
    _atomic_write(pointer, _json_bytes(pointer_value))
    return {"state": "READY", "emitted": True, "sourceCommit": source_commit, "packageVersion": candidate.get("packageVersion"), "candidatePath": candidate_rel, "candidateSha256": candidate_sha, "attestationPath": attestation_rel, "attestationSha256": attestation_sha, "pointerPath": pointer.relative_to(root).as_posix(), "selectedFileCount": len(candidate.get("files") or []), "w3LiveQualification": w3.get("liveQualification"), "alphaLiveObserved": alpha_before, "alphaLivePromoted": False}


def verify(root: Path, pointer_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    pointer = (pointer_path or root / DEFAULT_POINTER_REL).resolve()
    if not pointer.is_file():
        raise CandidateError(f"latest final candidate pointer missing: {pointer}")
    p = json.loads(pointer.read_text(encoding="utf-8-sig"))
    if not isinstance(p, dict) or p.get("schema") != POINTER_SCHEMA or p.get("state") != "READY":
        raise CandidateError("latest final candidate pointer is invalid/not READY")
    candidate_path = root / str(p.get("candidatePath"))
    attestation_path = root / str(p.get("attestationPath"))
    if not candidate_path.is_file() or not attestation_path.is_file():
        raise CandidateError("candidate or attestation referenced by latest pointer is missing")
    candidate_sha, attestation_sha = _sha256_file(candidate_path), _sha256_file(attestation_path)
    if candidate_sha != p.get("candidateSha256"):
        raise CandidateError("latest pointer candidate SHA256 mismatch")
    if attestation_sha != p.get("attestationSha256"):
        raise CandidateError("latest pointer attestation SHA256 mismatch")
    candidate = json.loads(candidate_path.read_text(encoding="utf-8-sig"))
    attestation = json.loads(attestation_path.read_text(encoding="utf-8-sig"))
    if candidate.get("sourceCommit") != p.get("sourceCommit") or attestation.get("sourceCommit") != p.get("sourceCommit"):
        raise CandidateError("candidate/attestation source commit mismatch")
    if attestation.get("candidateSha256") != candidate_sha or attestation.get("candidatePath") != p.get("candidatePath"):
        raise CandidateError("attestation does not bind exact candidate")
    if attestation.get("ownerVisualAcceptance") != "NOT_RUN" or attestation.get("alphaLivePromoted") is not False:
        raise CandidateError("attestation contains unsupported release/visual claim")
    _assert_safety(candidate.get("safety"), "candidate")
    _assert_safety(attestation.get("safety"), "attestation")
    verify_manifest_blobs(root, candidate)
    return {"state": "VERIFIED", "sourceCommit": p.get("sourceCommit"), "packageVersion": p.get("packageVersion"), "candidatePath": p.get("candidatePath"), "candidateSha256": candidate_sha, "attestationPath": p.get("attestationPath"), "attestationSha256": attestation_sha, "selectedFileCount": p.get("selectedFileCount"), "w3LiveQualification": p.get("w3LiveQualification"), "alphaLivePromoted": False}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and attest the exact Alpha V1 final canonical package candidate")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--source", default="HEAD")
    b.add_argument("--output-dir", type=Path)
    b.add_argument("--pointer", type=Path)
    v = sub.add_parser("verify")
    v.add_argument("--pointer", type=Path)
    bv = sub.add_parser("build-verify")
    bv.add_argument("--source", default="HEAD")
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
            if result.get("emitted"):
                result = {"build": result, "verify": verify(args.root, args.pointer)}
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        if isinstance(result, dict) and result.get("state") == "WAITING_FOR_P18":
            return 4
        return 0
    except CandidateError as exc:
        print(json.dumps({"state": "FAILED", "error": str(exc)}, ensure_ascii=False, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
