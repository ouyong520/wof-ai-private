from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

POINTER_SCHEMA = "wof-alpha-latest-final-canonical-candidate-v1"
ATTESTATION_SCHEMA = "wof-alpha-final-canonical-candidate-attestation-v1"
CANDIDATE_SCHEMA = "wof-owner-oneclick-package-v1"
POINTER_REL = Path("parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json")
WAITING_FOR_P19 = "WAITING_FOR_P19"
SUPPORTED_W3 = frozenset({"NOT_RUN", "INCONCLUSIVE", "PASS"})
REQUIRED_STAGES = ("P15", "P16", "P17", "P18")
HEX = frozenset("0123456789abcdef")


class StagingError(RuntimeError):
    pass


class WaitingForP19(StagingError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise StagingError(f"JSON root must be an object: {path}")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(
        ["git", *args], cwd=root, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if check and cp.returncode:
        raise StagingError(cp.stderr.strip() or cp.stdout.strip() or f"git {' '.join(args)} failed")
    return cp


def is_hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(ch in HEX for ch in value.lower())


def safe_repo_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise StagingError(f"{label} missing")
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        raise StagingError(f"{label} is not a bounded repository-relative path")
    resolved = (root / rel).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise StagingError(f"{label} escapes repository root") from exc
    return resolved


def assert_safety(value: Any, source: str) -> None:
    if not isinstance(value, Mapping):
        raise StagingError(f"{source}: safety object missing")
    for key, wanted in (("readOnly", True), ("ramWrites", 0), ("inputInjection", False)):
        if value.get(key) != wanted:
            raise StagingError(f"{source}: safety mismatch {key}={value.get(key)!r}")
    for key in (
        "legacySpatialFallback", "screenshotProductionCoordinates",
        "worldProjectionProductionCoordinates", "guessedAddresses", "alphaLiveMoved",
    ):
        if key in value and value.get(key) is not False:
            raise StagingError(f"{source}: forbidden safety flag {key}={value.get(key)!r}")


def git_blob(root: Path, commit: str, rel_path: str) -> str:
    value = run_git(root, "rev-parse", f"{commit}:{rel_path}").stdout.strip().lower()
    if not is_hex(value, 40):
        raise StagingError(f"invalid git blob for {rel_path}")
    return value


def verify_stage_map(value: Any, source: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(value, Mapping):
        raise StagingError(f"{source}: stage map missing")
    out: dict[str, Mapping[str, Any]] = {}
    for label in REQUIRED_STAGES:
        row = value.get(label)
        if not isinstance(row, Mapping):
            raise StagingError(f"{source}: {label} pin missing")
        if row.get("state") != "COMPLETE" or row.get("integrationReady") is not True:
            raise StagingError(f"{source}: {label} is not COMPLETE/integration-ready")
        commits = row.get("implementationCommits")
        if not isinstance(commits, list) or not commits or any(not is_hex(c, 40) for c in commits):
            raise StagingError(f"{source}: {label} implementation commits missing/invalid")
        out[label] = row
    return out


def resolve_p19_candidate(repo_root: Path, pointer_path: Path | None = None) -> dict[str, Any]:
    root = repo_root.expanduser().resolve()
    pointer = (pointer_path or root / POINTER_REL).expanduser().resolve()
    if not pointer.is_file():
        raise WaitingForP19(f"P19 latest final candidate pointer missing: {pointer}")
    p = load_json(pointer)
    if p.get("schema") != POINTER_SCHEMA or p.get("version") != 1 or p.get("state") != "READY":
        raise WaitingForP19("P19 latest final candidate pointer is not READY")
    source = str(p.get("sourceCommit") or "").lower()
    package = p.get("packageVersion")
    if not is_hex(source, 40):
        raise StagingError("P19 pointer sourceCommit invalid")
    if not isinstance(package, str) or not package:
        raise StagingError("P19 pointer packageVersion missing")
    states = p.get("stageStates")
    if not isinstance(states, Mapping) or any(states.get(k) != "COMPLETE" for k in REQUIRED_STAGES):
        raise WaitingForP19("P19 pointer does not pin COMPLETE P15/P16/P17/P18")
    if p.get("ownerVisualAcceptance") != "NOT_RUN" or p.get("alphaLivePromoted") is not False:
        raise StagingError("P19 pointer contains unsupported visual/promotion claim")
    w3 = p.get("w3LiveQualification")
    if w3 not in SUPPORTED_W3:
        raise StagingError(f"P19 pointer W3 state invalid: {w3!r}")

    candidate_path = safe_repo_path(root, p.get("candidatePath"), "candidatePath")
    attestation_path = safe_repo_path(root, p.get("attestationPath"), "attestationPath")
    if not candidate_path.is_file() or not attestation_path.is_file():
        raise WaitingForP19("P19 candidate/attestation referenced by pointer is missing")
    candidate_sha, attestation_sha = sha256_file(candidate_path), sha256_file(attestation_path)
    if candidate_sha != p.get("candidateSha256"):
        raise StagingError("P19 candidate SHA-256 mismatch")
    if attestation_sha != p.get("attestationSha256"):
        raise StagingError("P19 attestation SHA-256 mismatch")

    candidate, att = load_json(candidate_path), load_json(attestation_path)
    if candidate.get("schema") != CANDIDATE_SCHEMA:
        raise StagingError("final candidate schema mismatch")
    if candidate.get("sourceCommit") != source or candidate.get("packageVersion") != package:
        raise StagingError("candidate identity disagrees with P19 pointer")
    assert_safety(candidate.get("safety"), "candidate")
    if att.get("schema") != ATTESTATION_SCHEMA or att.get("version") != 1:
        raise StagingError("P19 attestation schema/version mismatch")
    if att.get("sourceCommit") != source or att.get("packageVersion") != package:
        raise StagingError("attestation identity disagrees with P19 pointer")
    if att.get("candidatePath") != p.get("candidatePath") or att.get("candidateSha256") != candidate_sha:
        raise StagingError("attestation does not bind exact P19 candidate")
    if att.get("ownerVisualAcceptance") != "NOT_RUN" or att.get("realWofAcceptance") != "NOT_RUN" or att.get("alphaLivePromoted") is not False:
        raise StagingError("attestation contains unsupported visual/runtime/promotion claim")
    if att.get("w3LiveQualification") != w3:
        raise StagingError("pointer/attestation W3 state mismatch")
    assert_safety(att.get("safety"), "attestation")

    final = ((candidate.get("components") or {}).get("finalCanonicalRelease") or {})
    if not isinstance(final, Mapping) or final.get("sourceCommit") != source:
        raise StagingError("candidate finalCanonicalRelease identity missing/mismatched")
    if final.get("ownerVisualAcceptance") != "NOT_RUN" or final.get("realWofAcceptance") != "NOT_RUN" or final.get("alphaLivePromoted") is not False:
        raise StagingError("candidate final release metadata contains unsupported proof/promotion claim")
    if final.get("legacySpatialFallback") is not False:
        raise StagingError("candidate does not explicitly disable legacy spatial fallback")
    assert_safety(final.get("safety"), "candidate final release")

    pins, att_results = verify_stage_map(final.get("resultPins"), "candidate final release"), verify_stage_map(att.get("stageResults"), "attestation")
    for label in REQUIRED_STAGES:
        if list(pins[label].get("implementationCommits") or []) != list(att_results[label].get("implementationCommits") or []):
            raise StagingError(f"{label} candidate/attestation implementation commit mismatch")

    ancestry = att.get("implementationAncestry")
    if not isinstance(ancestry, list):
        raise StagingError("attestation implementationAncestry missing")
    proven: set[tuple[str, str]] = set()
    for row in ancestry:
        if not isinstance(row, Mapping) or row.get("isAncestor") is not True:
            raise StagingError("attestation contains unproved implementation ancestry")
        stage, commit = row.get("stage"), row.get("commit")
        if stage not in REQUIRED_STAGES or not is_hex(commit, 40):
            raise StagingError("attestation ancestry row malformed")
        proven.add((str(stage), str(commit)))
    for label in REQUIRED_STAGES:
        for commit in att_results[label].get("implementationCommits") or []:
            if (label, commit) not in proven:
                raise StagingError(f"attestation omits ancestry proof for {label} {commit}")
            if run_git(root, "merge-base", "--is-ancestor", commit, source, check=False).returncode != 0:
                raise StagingError(f"local Git ancestry rejects attested {label} commit {commit}")

    critical, final_critical = att.get("criticalRuntimeBlobs"), final.get("criticalRuntimeBlobs")
    if not isinstance(critical, Mapping) or not critical or not isinstance(final_critical, Mapping):
        raise StagingError("critical runtime blob attestation missing")
    candidate_files = {
        row.get("path"): str(row.get("gitBlobSha") or "").lower()
        for row in (candidate.get("files") or [])
        if isinstance(row, Mapping) and isinstance(row.get("path"), str)
    }
    verified: dict[str, str] = {}
    for path, expected_value in critical.items():
        if not isinstance(path, str) or not is_hex(expected_value, 40):
            raise StagingError("critical runtime blob row malformed")
        expected = str(expected_value).lower()
        if final_critical.get(path) != expected or candidate_files.get(path) != expected:
            raise StagingError(f"critical blob pin disagrees across candidate/attestation: {path}")
        actual = git_blob(root, source, path)
        if actual != expected:
            raise StagingError(f"critical runtime blob mismatch: {path}")
        verified[path] = actual

    return {
        "state": "READY", "pointerPath": str(pointer), "sourceCommit": source,
        "packageVersion": package, "candidatePath": str(candidate_path),
        "candidateRelPath": str(p.get("candidatePath")), "candidateSha256": candidate_sha,
        "attestationPath": str(attestation_path), "attestationRelPath": str(p.get("attestationPath")),
        "attestationSha256": attestation_sha, "selectedFileCount": p.get("selectedFileCount"),
        "w3LiveQualification": w3, "criticalRuntimeBlobs": verified,
        "implementationAncestryCount": len(proven), "ownerVisualAcceptance": "NOT_RUN",
        "alphaLivePromoted": False,
    }


def observe_git_state(repo: Path) -> dict[str, Any]:
    root = repo.expanduser().resolve()
    if run_git(root, "rev-parse", "--git-dir", check=False).returncode != 0:
        raise StagingError(f"not a git repository: {root}")
    def rev(ref: str) -> str | None:
        cp = run_git(root, "rev-parse", "--verify", f"{ref}^{{commit}}", check=False)
        value = cp.stdout.strip().lower() if cp.returncode == 0 else ""
        return value if is_hex(value, 40) else None
    branch_cp = run_git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    return {
        "repo": str(root), "head": rev("HEAD"),
        "branch": branch_cp.stdout.strip() if branch_cp.returncode == 0 else None,
        "alphaLiveLocal": rev("refs/heads/alpha-live"),
        "alphaLiveRemote": rev("refs/remotes/origin/alpha-live"),
        "statusPorcelain": run_git(root, "status", "--porcelain").stdout.splitlines(),
    }


def compare_git_state(before: Mapping[str, Any], after: Mapping[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("head", "branch", "alphaLiveLocal", "alphaLiveRemote", "statusPorcelain"):
        if before.get(key) != after.get(key):
            out.append(f"{key}: before={before.get(key)!r}, after={after.get(key)!r}")
    return out


def ensure_candidate_commit(repo_root: Path, source_commit: str) -> bool:
    if run_git(repo_root, "cat-file", "-e", f"{source_commit}^{{commit}}", check=False).returncode == 0:
        return False
    cp = run_git(repo_root, "fetch", "--no-tags", "origin", source_commit, check=False)
    if cp.returncode != 0:
        raise StagingError(f"cannot fetch exact P19 candidate commit {source_commit}: {cp.stderr.strip()}")
    run_git(repo_root, "cat-file", "-e", f"{source_commit}^{{commit}}")
    return True
