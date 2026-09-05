from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence

RECEIPT_SCHEMA = "wof-alpha-owner-visual-confirmation-receipt-v1"
PLAN_SCHEMA = "wof-alpha-live-promotion-plan-v1"
PROMOTION_RESULT_SCHEMA = "wof-alpha-live-promotion-result-v1"
P17_BUNDLE_SCHEMA = "wof-alpha-final-acceptance-bundle-v1"
P17_READY = "READY_FOR_OWNER_VISUAL_CONFIRMATION"

VISUAL_READY = "READY_TO_ASK"
VISUAL_WAITING = "WAITING"
VISUAL_REJECTED = "REJECTED"

REQUIRED_W1_FILES = (
    "WOF_ALPHA_TEST.cmd",
    "parallel/PYLAUNCH/owner_live_retest_loop.ps1",
    "parallel/PYLAUNCH/render_authority_measurement_entry.py",
    "parallel/PYLAUNCH/requirements.txt",
)

DEFAULT_POINTERS = (
    Path("parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json"),
    Path("parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE_POINTER.json"),
    Path("parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANDIDATE.json"),
)

OWNER_QUESTION = "游戏里的提示是否稳定跟随正确的人物/怪物？请输入 YES 或 NO："


class GateError(RuntimeError):
    pass


class WaitingError(GateError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def default_results_dir() -> Path:
    return Path.home() / "Documents" / "WOF_RESULTS"


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WaitingError(f"missing evidence: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"unreadable JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GateError(f"JSON root must be an object: {path}")
    return value


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _strict_safety(value: Any, source: str, *, require_alpha_unmoved: bool = False) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise GateError(f"{source}: safety missing")
    expected = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
    for key, wanted in expected.items():
        if value.get(key) != wanted:
            raise GateError(f"{source}: weakened safety {key}={value.get(key)!r}")
    forbidden_truthy = (
        "screenshotProductionCoordinates",
        "worldProjectionProductionCoordinates",
        "guessedAddresses",
        "guessedRendererObjectAddress",
        "legacySpatialFallback",
    )
    for key in forbidden_truthy:
        if key in value and value.get(key) is not False:
            raise GateError(f"{source}: forbidden safety flag {key}={value.get(key)!r}")
    if require_alpha_unmoved and value.get("alphaLiveMoved") is not False:
        raise GateError(f"{source}: alphaLiveMoved must be false")
    return dict(value)


def _first(mapping: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return None


def _nested(mapping: Mapping[str, Any], *keys: str) -> Mapping[str, Any]:
    cur: Any = mapping
    for key in keys:
        if not isinstance(cur, Mapping):
            return {}
        cur = cur.get(key)
    return cur if isinstance(cur, Mapping) else {}


def _norm_rel(value: str) -> str:
    return value.replace("\\", "/").removeprefix("./")


def _repo_rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _resolve_path(value: str, *, repo_root: Path, pointer_parent: Path | None = None) -> Path:
    p = Path(value).expanduser()
    if p.is_absolute():
        return p.resolve()
    repo_path = (repo_root / p).resolve()
    if repo_path.exists() or pointer_parent is None:
        return repo_path
    return (pointer_parent / p).resolve()


def resolve_candidate_attestation(
    repo_root: Path,
    *,
    candidate_path: Path | None = None,
    attestation_path: Path | None = None,
    pointer_path: Path | None = None,
) -> tuple[Path, Path]:
    repo_root = repo_root.resolve()
    if candidate_path or attestation_path:
        if not candidate_path or not attestation_path:
            raise WaitingError("candidate and attestation must be supplied together")
        c, a = candidate_path.expanduser().resolve(), attestation_path.expanduser().resolve()
        if not c.is_file() or not a.is_file():
            raise WaitingError("final candidate or attestation is not available yet")
        return c, a

    pointers = (pointer_path.expanduser().resolve(),) if pointer_path else tuple(repo_root / p for p in DEFAULT_POINTERS)
    for pointer in pointers:
        if not pointer.is_file():
            continue
        raw = _load(pointer)
        if raw.get("packageVersion") and raw.get("sourceCommit"):
            att = _first(raw, ("attestationPath", "finalAttestationPath"))
            if isinstance(att, str):
                return pointer.resolve(), _resolve_path(att, repo_root=repo_root, pointer_parent=pointer.parent)
        candidate = _first(raw, ("candidatePath", "finalCandidatePath", "manifestPath", "candidateManifestPath"))
        attestation = _first(raw, ("attestationPath", "finalAttestationPath"))
        nested = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
        if not candidate:
            candidate = _first(nested, ("path", "manifestPath"))
        if not attestation:
            attested = raw.get("attestation") if isinstance(raw.get("attestation"), Mapping) else {}
            attestation = _first(attested, ("path",))
        if isinstance(candidate, str) and isinstance(attestation, str):
            c = _resolve_path(candidate, repo_root=repo_root, pointer_parent=pointer.parent)
            a = _resolve_path(attestation, repo_root=repo_root, pointer_parent=pointer.parent)
            if c.is_file() and a.is_file():
                return c, a
    raise WaitingError("P19 final candidate latest pointer/attestation is not available yet")


def read_candidate(repo_root: Path, path: Path) -> dict[str, Any]:
    raw = _load(path)
    package = raw.get("packageVersion")
    commit = raw.get("sourceCommit")
    if not isinstance(package, str) or not package:
        raise GateError("candidate packageVersion missing")
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdefABCDEF" for c in commit):
        raise GateError("candidate sourceCommit must be an exact 40-hex commit")
    _strict_safety(raw.get("safety"), "candidate")
    convergence = _nested(raw, "components", "canonicalProductConvergence")
    if convergence and convergence.get("alphaLivePromoted") is not False:
        raise GateError("candidate claims alpha-live was already promoted")
    if convergence and convergence.get("legacySpatialFallback") not in (None, False, "disabled", "DISABLED"):
        raise GateError("candidate enables legacy spatial fallback")
    return {
        "path": path.resolve(),
        "repoPath": _repo_rel(repo_root, path),
        "sha256": _sha256_file(path),
        "schema": raw.get("schema"),
        "packageVersion": package,
        "sourceCommit": commit.lower(),
        "raw": raw,
    }


def _attestation_candidate_fields(raw: Mapping[str, Any]) -> tuple[Any, Any]:
    candidate = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
    path = _first(raw, ("candidateManifestPath", "candidatePath", "manifestPath")) or _first(candidate, ("manifestPath", "path"))
    sha = _first(raw, ("candidateManifestSha256", "candidateSha256", "manifestSha256")) or _first(candidate, ("manifestSha256", "sha256", "contentSha256"))
    return path, sha


def read_attestation(repo_root: Path, path: Path, candidate: Mapping[str, Any]) -> dict[str, Any]:
    raw = _load(path)
    if not isinstance(raw.get("schema"), str) or not raw.get("schema"):
        raise GateError("attestation schema missing")
    if raw.get("version") not in (1, "1", None):
        raise GateError(f"unsupported attestation version: {raw.get('version')!r}")
    source_commit = _first(raw, ("sourceCommit", "candidateSourceCommit"))
    package_version = _first(raw, ("packageVersion", "candidatePackageVersion"))
    if source_commit != candidate["sourceCommit"]:
        raise GateError("attestation sourceCommit disagrees with candidate")
    if package_version != candidate["packageVersion"]:
        raise GateError("attestation packageVersion disagrees with candidate")
    att_path, att_sha = _attestation_candidate_fields(raw)
    if not isinstance(att_sha, str) or att_sha.lower() != candidate["sha256"]:
        raise GateError("attestation candidate SHA-256 disagrees with candidate bytes")
    if not isinstance(att_path, str):
        raise GateError("attestation candidate manifest path missing")
    expected_rel = _norm_rel(candidate["repoPath"])
    given = _norm_rel(att_path)
    if Path(given).is_absolute():
        given = _repo_rel(repo_root, Path(given))
    if given != expected_rel:
        raise GateError(f"attestation candidate path mismatch: {given!r} != {expected_rel!r}")
    _strict_safety(raw.get("safety"), "attestation")
    if _first(raw, ("alphaLivePromoted", "alphaLiveMoved")) not in (False, None):
        raise GateError("attestation claims alpha-live movement")
    visual = _first(raw, ("ownerVisualAcceptance", "ownerVisualVerdict", "visibleProof"))
    if visual not in (None, "NOT_RUN", "NOT_PROVEN"):
        raise GateError(f"attestation contains unsupported pre-Owner visual claim: {visual!r}")
    return {
        "path": path.resolve(),
        "repoPath": _repo_rel(repo_root, path),
        "sha256": _sha256_file(path),
        "schema": raw.get("schema"),
        "sourceCommit": source_commit,
        "packageVersion": package_version,
        "w3LiveQualification": _first(raw, ("w3LiveQualification", "w3Qualification")),
        "previousAlphaLiveCommit": _first(raw, ("previousAlphaLiveCommit", "previousObservedAlphaLiveCommit")),
        "currentAlphaLiveCommit": _first(raw, ("currentAlphaLiveCommit", "observedAlphaLiveCommit")),
        "raw": raw,
    }


def _identity_from_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    p16 = bundle.get("p16CanonicalRuntime") if isinstance(bundle.get("p16CanonicalRuntime"), Mapping) else {}
    p18 = bundle.get("p18DrawEvidence") if isinstance(bundle.get("p18DrawEvidence"), Mapping) else {}
    w3 = bundle.get("w3Qualification") if isinstance(bundle.get("w3Qualification"), Mapping) else {}
    p16i = p16.get("identity") if isinstance(p16.get("identity"), Mapping) else {}
    p18i = p18.get("identity") if isinstance(p18.get("identity"), Mapping) else {}
    w3i = w3.get("identity") if isinstance(w3.get("identity"), Mapping) else {}
    fields = ("worldSha256", "pageTargetId", "workerTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch", "rendererAuthority")
    out: dict[str, Any] = {}
    for field in fields:
        seen = [(name, src.get(field)) for name, src in (("P16", p16i), ("P18", p18i), ("W3", w3i)) if src.get(field) not in (None, "")]
        if seen:
            first = seen[0][1]
            if any(value != first for _, value in seen[1:]):
                raise GateError(f"bundle identity mismatch for {field}: {seen!r}")
            out[field] = first
    for required in ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch"):
        if not isinstance(out.get(required), str) or not out[required]:
            raise GateError(f"bundle exact identity missing {required}")
    return out


def inspect_bundle(path: Path, candidate: Mapping[str, Any]) -> tuple[str, list[str], dict[str, Any] | None]:
    try:
        raw = _load(path)
    except WaitingError as exc:
        return VISUAL_WAITING, [str(exc)], None
    except GateError as exc:
        return VISUAL_REJECTED, [str(exc)], None
    try:
        if raw.get("schema") != P17_BUNDLE_SCHEMA or raw.get("version") != 1:
            raise GateError("P17 acceptance bundle schema/version mismatch")
        decision = raw.get("automaticDecision")
        if decision != P17_READY:
            waiting_states = {
                "WAITING_W3_QUALIFICATION", "W3_INCONCLUSIVE", "WAITING_CANONICAL_RUNTIME_EVIDENCE",
                "CANONICAL_RUNTIME_SUPPRESSED", "WAITING_DRAW_EVIDENCE",
            }
            if decision in waiting_states:
                return VISUAL_WAITING, [f"P17 automatic decision is {decision}"], raw
            raise GateError(f"P17 automatic decision is not owner-visual-ready: {decision!r}")
        if raw.get("visibleProof") != "NOT_PROVEN" or raw.get("ownerVisualConfirmationRequired") is not True:
            raise GateError("P17 bundle must stop at NOT_PROVEN and require Owner visual confirmation")
        consistency = raw.get("identityConsistency") if isinstance(raw.get("identityConsistency"), Mapping) else {}
        if consistency.get("consistent") is not True or consistency.get("mismatches") not in ([], (), None):
            raise GateError("P17 identityConsistency is not exact/clean")
        _strict_safety(raw.get("safety"), "P17 bundle", require_alpha_unmoved=True)
        embedded = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
        if embedded.get("sourceCommit") != candidate["sourceCommit"] or embedded.get("packageVersion") != candidate["packageVersion"]:
            raise GateError("P17 bundle candidate identity disagrees with P19 candidate")
        if embedded.get("contentSha256") != candidate["sha256"]:
            raise GateError("P17 bundle candidate hash disagrees with P19 candidate bytes")
        w3 = raw.get("w3Qualification") if isinstance(raw.get("w3Qualification"), Mapping) else {}
        ready = w3.get("canonicalProducerReadiness") if isinstance(w3.get("canonicalProducerReadiness"), Mapping) else {}
        renderer = ready.get("rendererSource") if isinstance(ready.get("rendererSource"), Mapping) else {}
        if w3.get("status") != "PASS" or ready.get("ready") is not True or renderer.get("proven") is not True:
            raise GateError("P17 bundle lacks explicit W3 PASS + proven renderer source")
        p16 = raw.get("p16CanonicalRuntime") if isinstance(raw.get("p16CanonicalRuntime"), Mapping) else {}
        if p16.get("canonicalState") != "HUD_INGEST_ACCEPTED" or p16.get("visibleProof") != "NOT_PROVEN":
            raise GateError("P16 evidence is not exact HUD_INGEST_ACCEPTED/NOT_PROVEN")
        p18 = raw.get("p18DrawEvidence") if isinstance(raw.get("p18DrawEvidence"), Mapping) else {}
        if p18.get("evidenceState") != "CANONICAL_DRAW_ACKNOWLEDGED" or p18.get("visibleProof") != "NOT_PROVEN":
            raise GateError("P18 draw evidence is not exact CANONICAL_DRAW_ACKNOWLEDGED/NOT_PROVEN")
        identity = _identity_from_bundle(raw)
        return VISUAL_READY, [], {"raw": raw, "identity": identity, "sha256": _sha256_file(path), "path": path.resolve()}
    except GateError as exc:
        return VISUAL_REJECTED, [str(exc)], raw


def visual_preflight(repo_root: Path, candidate_path: Path, attestation_path: Path, bundle_path: Path) -> dict[str, Any]:
    try:
        candidate = read_candidate(repo_root, candidate_path)
        attestation = read_attestation(repo_root, attestation_path, candidate)
    except WaitingError as exc:
        return {"state": VISUAL_WAITING, "reasons": [str(exc)]}
    except GateError as exc:
        return {"state": VISUAL_REJECTED, "reasons": [str(exc)]}
    state, reasons, bundle = inspect_bundle(bundle_path, candidate)
    if state != VISUAL_READY or bundle is None:
        return {"state": state, "reasons": reasons, "candidate": candidate, "attestation": attestation}
    return {"state": VISUAL_READY, "reasons": [], "candidate": candidate, "attestation": attestation, "bundle": bundle}


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def _create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise GateError(f"immutable artifact already exists: {path}") from exc
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def _receipt_markdown(receipt: Mapping[str, Any]) -> str:
    return (
        "# Alpha Owner Visual Confirmation\n\n"
        f"- Verdict: **{receipt.get('ownerVisualVerdict')}**\n"
        f"- Candidate: `{receipt.get('packageVersion')}` @ `{receipt.get('candidateSourceCommit')}`\n"
        f"- Recorded: `{receipt.get('recordedAtUtc')}`\n"
        f"- Fixture mode: `{receipt.get('fixtureMode')}`\n\n"
        "This receipt records only the Owner's explicit visual YES/NO answer. It does not bypass candidate, ancestry, CAS, or safety gates.\n"
    )


def record_visual_receipt(
    preflight: Mapping[str, Any],
    *,
    answer: str,
    output_dir: Path,
    recorded_at_utc: str | None = None,
    fixture_mode: bool = False,
) -> tuple[dict[str, Any], Path]:
    if preflight.get("state") != VISUAL_READY:
        raise GateError("visual receipt cannot be created before READY_TO_ASK")
    normalized = answer.strip().upper()
    if normalized not in {"YES", "NO"}:
        raise GateError("Owner answer must be exactly YES or NO")
    candidate = preflight["candidate"]
    attestation = preflight["attestation"]
    bundle = preflight["bundle"]
    verdict = "PASS" if normalized == "YES" else "FAIL"
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "version": 1,
        "recordedAtUtc": recorded_at_utc or _now(),
        "question": OWNER_QUESTION.removesuffix("："),
        "ownerAnswer": normalized,
        "ownerVisualVerdict": verdict,
        "fixtureMode": bool(fixture_mode),
        "promotionEligible": verdict == "PASS" and not fixture_mode,
        "candidateSourceCommit": candidate["sourceCommit"],
        "packageVersion": candidate["packageVersion"],
        "candidateSha256": candidate["sha256"],
        "candidateAttestationSha256": attestation["sha256"],
        "acceptanceBundleSha256": bundle["sha256"],
        "identity": bundle["identity"],
        "visualProof": "FIXTURE_ONLY" if fixture_mode else ("OWNER_VISUAL_PASS" if verdict == "PASS" else "OWNER_VISUAL_FAIL"),
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "alphaLiveMoved": False,
            "forcePushAllowed": False,
        },
    }
    stem = f"ALPHA_OWNER_VISUAL_CONFIRMATION_{bundle['sha256'][:12]}_{candidate['sha256'][:12]}"
    jp = output_dir.expanduser().resolve() / f"{stem}.json"
    mp = jp.with_suffix(".md")
    if jp.exists():
        existing = _load(jp)
        immutable_keys = ("candidateSourceCommit", "packageVersion", "candidateSha256", "candidateAttestationSha256", "acceptanceBundleSha256", "ownerVisualVerdict", "fixtureMode")
        if all(existing.get(k) == receipt.get(k) for k in immutable_keys):
            return existing, jp
        raise GateError("an immutable visual receipt already exists for this candidate/bundle combination; it cannot be overwritten")
    _create_only(jp, (json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    try:
        _create_only(mp, _receipt_markdown(receipt).encode("utf-8"))
    except Exception:
        jp.unlink(missing_ok=True)
        raise
    return receipt, jp


def write_gate_status(output_dir: Path, state: str, reasons: Sequence[str]) -> Path:
    payload = {
        "schema": "wof-alpha-owner-visual-gate-status-v1",
        "version": 1,
        "generatedAtUtc": _now(),
        "state": state,
        "ownerVisualVerdict": "NOT_ASKED",
        "questionAsked": False,
        "reasons": list(reasons),
        "alphaLiveMoved": False,
    }
    path = output_dir.expanduser().resolve() / "ALPHA_OWNER_VISUAL_GATE_STATUS.json"
    _atomic_write(path, (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return path


def read_receipt(path: Path, *, candidate: Mapping[str, Any], attestation: Mapping[str, Any], bundle: Mapping[str, Any]) -> dict[str, Any]:
    raw = _load(path)
    if raw.get("schema") != RECEIPT_SCHEMA or raw.get("version") != 1:
        raise GateError("visual receipt schema/version mismatch")
    if raw.get("fixtureMode") is not False or raw.get("promotionEligible") is not True:
        raise GateError("fixture/non-eligible visual receipt can never authorize promotion")
    if raw.get("ownerVisualVerdict") != "PASS" or raw.get("ownerAnswer") != "YES" or raw.get("visualProof") != "OWNER_VISUAL_PASS":
        raise GateError("Owner visual verdict is not explicit real PASS")
    checks = {
        "candidateSourceCommit": candidate["sourceCommit"],
        "packageVersion": candidate["packageVersion"],
        "candidateSha256": candidate["sha256"],
        "candidateAttestationSha256": attestation["sha256"],
        "acceptanceBundleSha256": bundle["sha256"],
    }
    for key, wanted in checks.items():
        if raw.get(key) != wanted:
            raise GateError(f"receipt mismatch for {key}")
    if raw.get("identity") != bundle["identity"]:
        raise GateError("receipt identity disagrees with acceptance bundle")
    _strict_safety(raw.get("safety"), "visual receipt", require_alpha_unmoved=True)
    if raw["safety"].get("forcePushAllowed") is not False:
        raise GateError("visual receipt weakens no-force policy")
    return {"raw": raw, "path": path.resolve(), "sha256": _sha256_file(path)}


def _git(repo_root: Path, args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(["git", "-C", str(repo_root), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and cp.returncode:
        raise GateError(f"git {' '.join(args)} failed: {cp.stderr.strip() or cp.stdout.strip()}")
    return cp


def _git_dir(git_dir: Path, args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(["git", "--git-dir", str(git_dir), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and cp.returncode:
        raise GateError(f"git --git-dir {git_dir} {' '.join(args)} failed: {cp.stderr.strip() or cp.stdout.strip()}")
    return cp


def observe_remote_ref(repo_root: Path, remote: str, branch: str) -> str:
    cp = _git(repo_root, ["ls-remote", "--heads", remote, f"refs/heads/{branch}"], check=False)
    if cp.returncode:
        raise WaitingError(f"cannot observe {remote}/{branch}: {cp.stderr.strip()}")
    rows = [line.split() for line in cp.stdout.splitlines() if line.strip()]
    if len(rows) != 1 or len(rows[0]) < 2:
        raise WaitingError(f"remote branch {remote}/{branch} missing or ambiguous")
    sha = rows[0][0].lower()
    if len(sha) != 40:
        raise GateError("remote alpha-live returned a non-exact commit")
    return sha


def _commit_exists(repo_root: Path, commit: str) -> None:
    cp = _git(repo_root, ["cat-file", "-e", f"{commit}^{{commit}}"], check=False)
    if cp.returncode:
        raise WaitingError(f"commit {commit} is not present in the local repository")


def _is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    cp = _git(repo_root, ["merge-base", "--is-ancestor", ancestor, descendant], check=False)
    if cp.returncode == 0:
        return True
    if cp.returncode == 1:
        return False
    raise GateError(f"cannot evaluate commit ancestry: {cp.stderr.strip()}")


def validate_w1_files(repo_root: Path, commit: str) -> None:
    missing = []
    for path in REQUIRED_W1_FILES:
        cp = _git(repo_root, ["cat-file", "-e", f"{commit}:{path}"], check=False)
        if cp.returncode:
            missing.append(path)
    if missing:
        raise GateError(f"candidate target is missing W1 permanent release files: {', '.join(missing)}")


def _attestation_visual_claim(attestation: Mapping[str, Any]) -> Any:
    raw = attestation["raw"]
    return _first(raw, ("ownerVisualAcceptance", "ownerVisualVerdict", "visibleProof"))


def build_promotion_plan(
    repo_root: Path,
    *,
    candidate_path: Path,
    attestation_path: Path,
    bundle_path: Path,
    receipt_path: Path,
    remote: str,
    live_branch: str = "alpha-live",
    prepared_at_utc: str | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    candidate = read_candidate(repo_root, candidate_path)
    attestation = read_attestation(repo_root, attestation_path, candidate)
    state, reasons, bundle = inspect_bundle(bundle_path, candidate)
    if state != VISUAL_READY or bundle is None:
        raise GateError(f"acceptance bundle cannot authorize promotion: {state}: {'; '.join(reasons)}")
    receipt = read_receipt(receipt_path, candidate=candidate, attestation=attestation, bundle=bundle)
    if _attestation_visual_claim(attestation) not in (None, "NOT_RUN", "NOT_PROVEN"):
        raise GateError("candidate attestation contains an unsupported visual PASS claim")
    from_commit = observe_remote_ref(repo_root, remote, live_branch)
    to_commit = candidate["sourceCommit"]
    _commit_exists(repo_root, from_commit)
    _commit_exists(repo_root, to_commit)
    if not _is_ancestor(repo_root, from_commit, to_commit):
        raise GateError("candidate is not a fast-forward descendant of current alpha-live")
    validate_w1_files(repo_root, to_commit)
    core = {
        "fromAlphaLiveCommit": from_commit,
        "toCandidateCommit": to_commit,
        "packageVersion": candidate["packageVersion"],
        "candidateSha256": candidate["sha256"],
        "candidateAttestationSha256": attestation["sha256"],
        "acceptanceBundleSha256": bundle["sha256"],
        "visualReceiptSha256": receipt["sha256"],
        "identity": bundle["identity"],
        "rollback": {
            "previousCommit": from_commit,
            "preserveW1LastKnownGoodBehavior": True,
        },
        "fastForwardRequired": True,
        "compareAndSwapExpectedOld": from_commit,
        "requiredW1Files": list(REQUIRED_W1_FILES),
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "screenshotProductionCoordinates": False,
            "worldProjectionProductionCoordinates": False,
            "guessedAddresses": False,
            "forcePushAllowed": False,
            "alphaLiveMovedAtPlan": False,
        },
    }
    plan_hash = _canonical_sha256(core)
    return {
        "schema": PLAN_SCHEMA,
        "version": 1,
        "state": "READY",
        "preparedAtUtc": prepared_at_utc or _now(),
        "planCore": core,
        "planHashAlgorithm": "sha256(canonical-json(planCore))",
        "planHash": plan_hash,
        "artifactPaths": {
            "candidate": str(candidate_path.resolve()),
            "attestation": str(attestation_path.resolve()),
            "acceptanceBundle": str(bundle_path.resolve()),
            "visualReceipt": str(receipt_path.resolve()),
        },
        "remote": remote,
        "liveBranch": live_branch,
        "applyDefault": "DRY_RUN",
    }


def write_plan(plan: Mapping[str, Any], output_dir: Path) -> Path:
    if plan.get("state") != "READY" or not isinstance(plan.get("planHash"), str):
        raise GateError("only READY promotion plans can be written")
    path = output_dir.expanduser().resolve() / f"ALPHA_LIVE_PROMOTION_PLAN_{plan['planHash'][:16]}.json"
    data = (json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() == data:
            return path
        raise GateError(f"promotion plan path collision: {path}")
    _create_only(path, data)
    return path


def _validate_plan_document(plan: Mapping[str, Any], confirm_hash: str) -> tuple[Mapping[str, Any], str]:
    if plan.get("schema") != PLAN_SCHEMA or plan.get("version") != 1 or plan.get("state") != "READY":
        raise GateError("promotion plan schema/state mismatch")
    core = plan.get("planCore")
    if not isinstance(core, Mapping):
        raise GateError("promotion plan core missing")
    expected = _canonical_sha256(core)
    if plan.get("planHash") != expected:
        raise GateError("promotion plan hash does not match its core")
    if confirm_hash != expected:
        raise GateError("explicit confirmation token does not equal exact promotion plan hash")
    safety = core.get("safety") if isinstance(core.get("safety"), Mapping) else {}
    _strict_safety(safety, "promotion plan")
    if safety.get("forcePushAllowed") is not False or safety.get("alphaLiveMovedAtPlan") is not False:
        raise GateError("promotion plan weakens no-force/unmoved safety")
    if core.get("fastForwardRequired") is not True or core.get("compareAndSwapExpectedOld") != core.get("fromAlphaLiveCommit"):
        raise GateError("promotion plan CAS/fast-forward contract invalid")
    if tuple(core.get("requiredW1Files") or ()) != REQUIRED_W1_FILES:
        raise GateError("promotion plan W1 required-file contract changed")
    return core, expected


def _validate_plan_artifacts(plan: Mapping[str, Any], core: Mapping[str, Any]) -> None:
    paths = plan.get("artifactPaths") if isinstance(plan.get("artifactPaths"), Mapping) else {}
    expected = {
        "candidate": core.get("candidateSha256"),
        "attestation": core.get("candidateAttestationSha256"),
        "acceptanceBundle": core.get("acceptanceBundleSha256"),
        "visualReceipt": core.get("visualReceiptSha256"),
    }
    for key, wanted in expected.items():
        value = paths.get(key)
        if not isinstance(value, str):
            raise GateError(f"promotion plan artifact path missing: {key}")
        path = Path(value).expanduser().resolve()
        if not path.is_file() or _sha256_file(path) != wanted:
            raise GateError(f"promotion plan artifact changed or missing: {key}")


def _assert_no_force_push_args(args: Sequence[str]) -> None:
    for arg in args:
        if arg.startswith("--force") or arg.startswith("+") or ":+" in arg:
            raise GateError("force-style git push arguments are forbidden")


def _local_bare_path(remote: str) -> Path | None:
    p = Path(remote).expanduser()
    if not p.is_dir():
        return None
    cp = subprocess.run(["git", "--git-dir", str(p), "rev-parse", "--is-bare-repository"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return p.resolve() if cp.returncode == 0 and cp.stdout.strip() == "true" else None


def apply_promotion_plan(
    repo_root: Path,
    *,
    plan_path: Path,
    confirm_plan_hash: str,
    execute: bool = False,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    plan = _load(plan_path)
    core, plan_hash = _validate_plan_document(plan, confirm_plan_hash)
    _validate_plan_artifacts(plan, core)
    remote = plan.get("remote")
    branch = plan.get("liveBranch")
    if not isinstance(remote, str) or not remote or not isinstance(branch, str) or not branch:
        raise GateError("promotion plan remote/liveBranch missing")
    current = observe_remote_ref(repo_root, remote, branch)
    expected_old = core["fromAlphaLiveCommit"]
    target = core["toCandidateCommit"]
    if current != expected_old:
        raise GateError(f"CAS rejection: alpha-live changed from planned {expected_old} to {current}")
    _commit_exists(repo_root, target)
    if not _is_ancestor(repo_root, expected_old, target):
        raise GateError("apply rejected: target is no longer a valid fast-forward descendant")
    validate_w1_files(repo_root, target)
    if not execute:
        return {"state": "DRY_RUN_READY", "planHash": plan_hash, "alphaLiveMoved": False, "currentAlphaLiveCommit": current}

    local_bare = _local_bare_path(remote)
    if local_bare is not None:
        _git_dir(local_bare, ["fetch", "--quiet", str(repo_root), target])
        cp = _git_dir(local_bare, ["update-ref", f"refs/heads/{branch}", target, expected_old], check=False)
        if cp.returncode:
            raise GateError(f"local bare CAS update failed: {cp.stderr.strip() or cp.stdout.strip()}")
    else:
        args = ["push", "--porcelain", remote, f"{target}:refs/heads/{branch}"]
        _assert_no_force_push_args(args)
        cp = _git(repo_root, args, check=False)
        if cp.returncode:
            raise GateError(f"non-force alpha-live push failed: {cp.stderr.strip() or cp.stdout.strip()}")
    confirmed = observe_remote_ref(repo_root, remote, branch)
    if confirmed != target:
        raise GateError(f"promotion ref movement could not be confirmed: observed {confirmed}")
    result = {
        "schema": PROMOTION_RESULT_SCHEMA,
        "version": 1,
        "state": "PROMOTED",
        "promotedAtUtc": _now(),
        "planHash": plan_hash,
        "fromAlphaLiveCommit": expected_old,
        "toCandidateCommit": target,
        "alphaLiveMoved": True,
        "forcePushUsed": False,
        "fastForwardOnly": True,
    }
    if output_dir is not None:
        out = output_dir.expanduser().resolve() / f"ALPHA_LIVE_PROMOTION_RESULT_{plan_hash[:16]}.json"
        _create_only(out, (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        result["resultPath"] = str(out)
    return result


def _invoke_p17(repo_root: Path, output_dir: Path, candidate_path: Path, w3_qualification: Path | None) -> Path:
    orchestrator = repo_root / "parallel/OWNER_ACCEPTANCE/final_acceptance_orchestrator.py"
    if not orchestrator.is_file():
        raise WaitingError(f"P17 orchestrator missing: {orchestrator}")
    cmd = [
        sys.executable, str(orchestrator), "--repo-root", str(repo_root), "--output-dir", str(output_dir),
        "--candidate-metadata", str(candidate_path),
        "--p16-evidence", str(output_dir / "ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.json"),
        "--p18-evidence", str(output_dir / "ALPHA_CANONICAL_DRAW_EVIDENCE.json"),
    ]
    if w3_qualification:
        cmd += ["--w3-qualification", str(w3_qualification)]
    else:
        cmd += ["--invoke-w3"]
    cp = subprocess.run(cmd, cwd=repo_root, text=True, check=False)
    if cp.returncode:
        raise WaitingError(f"P17 final acceptance flow exited {cp.returncode}")
    bundle = output_dir / "ALPHA_FINAL_ACCEPTANCE_BUNDLE.json"
    if not bundle.is_file():
        raise WaitingError("P17 did not produce the final acceptance bundle")
    return bundle


def _confirm_command(args: argparse.Namespace) -> int:
    repo = args.repo_root.expanduser().resolve()
    out = args.output_dir.expanduser().resolve()
    try:
        candidate_path, attestation_path = resolve_candidate_attestation(repo, candidate_path=args.candidate, attestation_path=args.attestation, pointer_path=args.candidate_pointer)
        bundle_path = args.bundle.expanduser().resolve()
        preflight = visual_preflight(repo, candidate_path, attestation_path, bundle_path)
        if preflight["state"] != VISUAL_READY:
            status = write_gate_status(out, preflight["state"], preflight.get("reasons") or [])
            print(f"visualGate={preflight['state']}")
            print(f"questionAsked=false")
            print(f"statusArtifact={status}")
            return 2
        if args.fixture_mode:
            if args.fixture_answer not in {"YES", "NO"}:
                raise GateError("--fixture-mode requires --fixture-answer YES or NO")
            answer = args.fixture_answer
        else:
            if args.fixture_answer:
                raise GateError("fixture answer is forbidden outside --fixture-mode")
            answer = input(OWNER_QUESTION)
        receipt, path = record_visual_receipt(preflight, answer=answer, output_dir=out, fixture_mode=args.fixture_mode)
        print(f"visualGate={VISUAL_READY}")
        print(f"ownerVisualVerdict={receipt['ownerVisualVerdict']}")
        print(f"promotionEligible={str(receipt['promotionEligible']).lower()}")
        print(f"receipt={path}")
        return 0 if receipt["ownerVisualVerdict"] == "PASS" else 3
    except WaitingError as exc:
        status = write_gate_status(out, VISUAL_WAITING, [str(exc)])
        print(f"visualGate={VISUAL_WAITING}\nquestionAsked=false\nstatusArtifact={status}")
        return 2
    except GateError as exc:
        status = write_gate_status(out, VISUAL_REJECTED, [str(exc)])
        print(f"visualGate={VISUAL_REJECTED}\nquestionAsked=false\nstatusArtifact={status}", file=sys.stderr)
        return 4


def _plan_command(args: argparse.Namespace) -> int:
    repo = args.repo_root.expanduser().resolve()
    try:
        candidate, attestation = resolve_candidate_attestation(repo, candidate_path=args.candidate, attestation_path=args.attestation, pointer_path=args.candidate_pointer)
        plan = build_promotion_plan(
            repo,
            candidate_path=candidate,
            attestation_path=attestation,
            bundle_path=args.bundle.expanduser().resolve(),
            receipt_path=args.receipt.expanduser().resolve(),
            remote=args.remote,
            live_branch=args.live_branch,
        )
        path = write_plan(plan, args.output_dir)
        print(f"promotionPlan=READY\nplanHash={plan['planHash']}\nplan={path}\nalphaLiveMoved=false")
        return 0
    except GateError as exc:
        print(f"promotionPlan=REJECTED\nreason={exc}\nalphaLiveMoved=false", file=sys.stderr)
        return 4


def _apply_command(args: argparse.Namespace) -> int:
    try:
        result = apply_promotion_plan(
            args.repo_root.expanduser().resolve(),
            plan_path=args.plan.expanduser().resolve(),
            confirm_plan_hash=args.confirm_plan_hash,
            execute=args.execute,
            output_dir=args.output_dir if args.execute else None,
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except GateError as exc:
        print(f"apply=REJECTED\nreason={exc}\nalphaLiveMoved=false", file=sys.stderr)
        return 4


def _run_command(args: argparse.Namespace) -> int:
    repo = args.repo_root.expanduser().resolve()
    out = args.output_dir.expanduser().resolve()
    try:
        candidate, attestation = resolve_candidate_attestation(repo, candidate_path=args.candidate, attestation_path=args.attestation, pointer_path=args.candidate_pointer)
        bundle = args.bundle.expanduser().resolve() if args.bundle else _invoke_p17(repo, out, candidate, args.w3_qualification)
        preflight = visual_preflight(repo, candidate, attestation, bundle)
        if preflight["state"] != VISUAL_READY:
            status = write_gate_status(out, preflight["state"], preflight.get("reasons") or [])
            print(f"finalGate={preflight['state']}\nquestionAsked=false\nstatusArtifact={status}\nalphaLiveMoved=false")
            return 2
        answer = input(OWNER_QUESTION)
        receipt, receipt_path = record_visual_receipt(preflight, answer=answer, output_dir=out, fixture_mode=False)
        if receipt["ownerVisualVerdict"] != "PASS":
            print(f"ownerVisualVerdict=FAIL\nreceipt={receipt_path}\npromotionPlan=BLOCKED\nalphaLiveMoved=false")
            return 3
        plan = build_promotion_plan(
            repo,
            candidate_path=candidate,
            attestation_path=attestation,
            bundle_path=bundle,
            receipt_path=receipt_path,
            remote=args.remote,
            live_branch=args.live_branch,
        )
        plan_path = write_plan(plan, out)
        print(f"ownerVisualVerdict=PASS\nreceipt={receipt_path}\npromotionPlan=READY\nplanHash={plan['planHash']}\nplan={plan_path}\nalphaLiveMoved=false")
        print("真实发布未执行；仅 PM 后续使用 apply --execute 且提供完全一致的 planHash 才会进入发布路径。")
        return 0
    except WaitingError as exc:
        status = write_gate_status(out, VISUAL_WAITING, [str(exc)])
        print(f"finalGate={VISUAL_WAITING}\nquestionAsked=false\nstatusArtifact={status}\nalphaLiveMoved=false")
        return 2
    except GateError as exc:
        status = write_gate_status(out, VISUAL_REJECTED, [str(exc)])
        print(f"finalGate={VISUAL_REJECTED}\nquestionAsked=false\nstatusArtifact={status}\nalphaLiveMoved=false", file=sys.stderr)
        return 4


def build_parser() -> argparse.ArgumentParser:
    here = Path(__file__).resolve()
    default_repo = here.parents[2]
    parser = argparse.ArgumentParser(description="Alpha V1 Owner visual confirmation + fail-closed alpha-live promotion gate")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser, *, bundle: bool = True) -> None:
        p.add_argument("--repo-root", type=Path, default=default_repo)
        p.add_argument("--candidate", type=Path)
        p.add_argument("--attestation", type=Path)
        p.add_argument("--candidate-pointer", type=Path)
        if bundle:
            p.add_argument("--bundle", type=Path, default=default_results_dir() / "ALPHA_FINAL_ACCEPTANCE_BUNDLE.json")
        p.add_argument("--output-dir", type=Path, default=default_results_dir())

    confirm = sub.add_parser("confirm", help="validate automatic evidence and ask/record the single Owner visual YES/NO")
    common(confirm)
    confirm.add_argument("--fixture-mode", action="store_true", help="tests only; receipts are permanently promotion-ineligible")
    confirm.add_argument("--fixture-answer", choices=("YES", "NO"))
    confirm.set_defaults(func=_confirm_command)

    plan = sub.add_parser("plan", help="build a deterministic fail-closed promotion plan; never moves alpha-live")
    common(plan)
    plan.add_argument("--receipt", type=Path, required=True)
    plan.add_argument("--remote", default="origin")
    plan.add_argument("--live-branch", default="alpha-live")
    plan.set_defaults(func=_plan_command)

    apply = sub.add_parser("apply", help="verify or explicitly execute an existing promotion plan")
    apply.add_argument("--repo-root", type=Path, default=default_repo)
    apply.add_argument("--plan", type=Path, required=True)
    apply.add_argument("--confirm-plan-hash", required=True)
    apply.add_argument("--execute", action="store_true", help="without this flag apply is dry-run only")
    apply.add_argument("--output-dir", type=Path, default=default_results_dir())
    apply.set_defaults(func=_apply_command)

    run = sub.add_parser("run", help="one command: P17 -> single Owner YES/NO -> promotion plan; never promotes")
    common(run, bundle=False)
    run.add_argument("--bundle", type=Path, help="reuse an existing P17 bundle instead of invoking P17")
    run.add_argument("--w3-qualification", type=Path, help="explicit bounded W3 result; otherwise P17 invokes W3")
    run.add_argument("--remote", default="origin")
    run.add_argument("--live-branch", default="alpha-live")
    run.set_defaults(func=_run_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
