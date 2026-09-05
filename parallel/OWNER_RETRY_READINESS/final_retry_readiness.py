from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Protocol

READY = "READY_FOR_ONE_BOUNDED_OWNER_RETRY"
BLOCKED = "BLOCKED"
SCHEMA = "wof-alpha-final-retry-readiness-v1"
DEFAULT_CANDIDATE_PROVENANCE = (
    "parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json"
)
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class StageRequirement:
    stage_id: str
    dedup_key: str
    accepted_terminal_states: tuple[str, ...] = ("COMPLETE",)

    @property
    def result_path(self) -> str:
        return f"parallel/PM/RESULTS/{self.stage_id}_RESULT.json"

    @property
    def canonical_claim_path(self) -> str:
        return f"parallel/PM/DEDUP_CLAIMS/{self.dedup_key}.json"

    @property
    def stage_claim_path(self) -> str:
        return f"parallel/PM/STAGE_CLAIMS/{self.stage_id}.json"


DEFAULT_REQUIREMENTS: tuple[StageRequirement, ...] = (
    StageRequirement(
        "ALPHA_V1_PRODUCT_TAKEOVER_P29_W3_LIVE_EVIDENCE_CONTRACT_REPAIR",
        "alpha.v1.product-takeover.w3-live-evidence-contract-repair-v1",
    ),
    StageRequirement(
        "ALPHA_V1_PRODUCT_TAKEOVER_P30_P16_P9_BINDING_AND_STAGING_READINESS_REPAIR",
        "alpha.v1.product-takeover.p16-p9-binding-staging-readiness-repair-v1",
    ),
    StageRequirement(
        "ALPHA_V1_PRODUCT_TAKEOVER_P31_WOF_PAGE_ASSOCIATION_AMBIGUITY_REPAIR",
        "alpha.v1.product-takeover.wof-page-association-ambiguity-repair-v1",
    ),
    StageRequirement(
        "ALPHA_V1_PRODUCT_TAKEOVER_P32_NATIVE_PLAYER_MARKER_RENDERER_ANCHOR_QUALIFICATION",
        "alpha.v1.product-takeover.native-player-marker-renderer-anchor-qualification-v1",
    ),
)


class GitProbeProtocol(Protocol):
    def commit_exists(self, sha: str) -> bool: ...
    def is_ancestor(self, ancestor: str, descendant: str) -> bool: ...


class GitProbe:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.repo_root), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def commit_exists(self, sha: str) -> bool:
        if not _SHA40_RE.fullmatch(sha):
            return False
        return self._run("cat-file", "-e", f"{sha}^{{commit}}").returncode == 0

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        if not (_SHA40_RE.fullmatch(ancestor) and _SHA40_RE.fullmatch(descendant)):
            return False
        return (
            self._run("merge-base", "--is-ancestor", ancestor, descendant).returncode
            == 0
        )


def _block(
    blockers: list[dict[str, Any]],
    code: str,
    detail: str,
    *,
    stage_id: str | None = None,
    path: str | None = None,
) -> None:
    item: dict[str, Any] = {"code": code, "detail": detail}
    if stage_id is not None:
        item["stageId"] = stage_id
    if path is not None:
        item["path"] = path
    blockers.append(item)


def _safe_repo_path(repo_root: Path, relative_path: str) -> Path | None:
    try:
        posix = PurePosixPath(relative_path)
    except (TypeError, ValueError):
        return None
    if not relative_path or posix.is_absolute() or ".." in posix.parts:
        return None
    candidate = repo_root.joinpath(*posix.parts)
    try:
        candidate.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return None
    return candidate


def _load_json(
    repo_root: Path,
    relative_path: str,
    blockers: list[dict[str, Any]],
    *,
    missing_code: str,
    invalid_code: str,
    stage_id: str | None = None,
) -> tuple[dict[str, Any] | None, bytes | None]:
    path = _safe_repo_path(repo_root, relative_path)
    if path is None:
        _block(
            blockers,
            invalid_code,
            f"Unsafe or invalid repository-relative JSON path: {relative_path!r}.",
            stage_id=stage_id,
            path=relative_path,
        )
        return None, None
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        _block(
            blockers,
            missing_code,
            f"Required authority file is missing: {relative_path}.",
            stage_id=stage_id,
            path=relative_path,
        )
        return None, None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _block(
            blockers,
            invalid_code,
            f"Required JSON is not valid UTF-8 JSON: {relative_path}: {exc}.",
            stage_id=stage_id,
            path=relative_path,
        )
        return None, raw
    if not isinstance(value, dict):
        _block(
            blockers,
            invalid_code,
            f"Required JSON root must be an object: {relative_path}.",
            stage_id=stage_id,
            path=relative_path,
        )
        return None, raw
    return value, raw


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _true_movement_paths(value: Any, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key in sorted(value):
            child = value[key]
            child_prefix = f"{prefix}.{key}"
            if (
                key in {"alphaLiveMoved", "alphaLivePromoted", "promotionPerformed"}
                and child is True
            ):
                found.append(child_prefix)
            found.extend(_true_movement_paths(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_true_movement_paths(child, f"{prefix}[{index}]"))
    return found


def _claim_points_to_result(claim: Mapping[str, Any], expected: str) -> bool:
    return claim.get("resultJsonPath") == expected or claim.get("resultPath") == expected


def _validate_stage(
    repo_root: Path,
    requirement: StageRequirement,
    blockers: list[dict[str, Any]],
) -> tuple[dict[str, Any], str | None]:
    before = len(blockers)
    stage: dict[str, Any] = {
        "stageId": requirement.stage_id,
        "dedupKey": requirement.dedup_key,
        "acceptedTerminalStates": list(requirement.accepted_terminal_states),
        "resultPath": requirement.result_path,
        "terminalState": None,
        "claimState": None,
        "stageClaimState": None,
        "claimToken": None,
        "testedCommit": None,
        "integrationReady": None,
        "terminalBlocker": None,
        "productProof": None,
        "accepted": False,
    }

    result, _ = _load_json(
        repo_root,
        requirement.result_path,
        blockers,
        missing_code="MISSING_TERMINAL_RESULT",
        invalid_code="INVALID_TERMINAL_RESULT",
        stage_id=requirement.stage_id,
    )
    canonical, _ = _load_json(
        repo_root,
        requirement.canonical_claim_path,
        blockers,
        missing_code="MISSING_CANONICAL_CLAIM",
        invalid_code="INVALID_CANONICAL_CLAIM",
        stage_id=requirement.stage_id,
    )
    stage_claim, _ = _load_json(
        repo_root,
        requirement.stage_claim_path,
        blockers,
        missing_code="MISSING_STAGE_CLAIM",
        invalid_code="INVALID_STAGE_CLAIM",
        stage_id=requirement.stage_id,
    )

    if result is not None:
        stage["terminalState"] = result.get("state")
        stage["claimToken"] = result.get("claimToken")
        stage["testedCommit"] = result.get("testedCommit")
        stage["integrationReady"] = result.get("integrationReady")
        stage["terminalBlocker"] = result.get("blocker")
        stage["productProof"] = result.get("productProof")

        if result.get("stageId") != requirement.stage_id:
            _block(
                blockers,
                "RESULT_STAGE_ID_MISMATCH",
                "Terminal RESULT stageId does not match the required stage.",
                stage_id=requirement.stage_id,
                path=requirement.result_path,
            )
        if result.get("dedupKey") != requirement.dedup_key:
            _block(
                blockers,
                "RESULT_DEDUP_KEY_MISMATCH",
                "Terminal RESULT dedupKey does not match the required logical claim.",
                stage_id=requirement.stage_id,
                path=requirement.result_path,
            )
        if result.get("state") not in requirement.accepted_terminal_states:
            _block(
                blockers,
                "UPSTREAM_TERMINAL_STATE_NOT_ACCEPTED",
                (
                    f"Required stage terminal state is {result.get('state')!r}; "
                    f"accepted states are {requirement.accepted_terminal_states!r}."
                ),
                stage_id=requirement.stage_id,
                path=requirement.result_path,
            )
        if result.get("integrationReady") is not True:
            _block(
                blockers,
                "UPSTREAM_NOT_INTEGRATION_READY",
                "Required terminal RESULT must explicitly set integrationReady=true.",
                stage_id=requirement.stage_id,
                path=requirement.result_path,
            )
        tested_commit = result.get("testedCommit")
        if not isinstance(tested_commit, str) or not _SHA40_RE.fullmatch(tested_commit):
            _block(
                blockers,
                "MISSING_OR_INVALID_TESTED_COMMIT",
                "Required terminal RESULT must carry one exact 40-hex testedCommit.",
                stage_id=requirement.stage_id,
                path=requirement.result_path,
            )
        movement = _true_movement_paths(result)
        if movement:
            _block(
                blockers,
                "ALPHA_LIVE_MOVED_BEFORE_RETRY",
                f"Terminal RESULT reports forbidden movement at: {', '.join(movement)}.",
                stage_id=requirement.stage_id,
                path=requirement.result_path,
            )

    if canonical is not None:
        stage["claimState"] = canonical.get("state")
        if canonical.get("stageId") != requirement.stage_id:
            _block(
                blockers,
                "CANONICAL_CLAIM_STAGE_ID_MISMATCH",
                "Canonical claim stageId does not match the required stage.",
                stage_id=requirement.stage_id,
                path=requirement.canonical_claim_path,
            )
        if canonical.get("dedupKey") != requirement.dedup_key:
            _block(
                blockers,
                "CANONICAL_CLAIM_DEDUP_KEY_MISMATCH",
                "Canonical claim dedupKey does not match the required logical claim.",
                stage_id=requirement.stage_id,
                path=requirement.canonical_claim_path,
            )

    if stage_claim is not None:
        stage["stageClaimState"] = stage_claim.get("state")
        if stage_claim.get("stageId") != requirement.stage_id:
            _block(
                blockers,
                "STAGE_CLAIM_STAGE_ID_MISMATCH",
                "Stage claim stageId does not match the required stage.",
                stage_id=requirement.stage_id,
                path=requirement.stage_claim_path,
            )
        if stage_claim.get("dedupKey") != requirement.dedup_key:
            _block(
                blockers,
                "STAGE_CLAIM_DEDUP_KEY_MISMATCH",
                "Stage claim dedupKey does not match the required logical claim.",
                stage_id=requirement.stage_id,
                path=requirement.stage_claim_path,
            )
        if stage_claim.get("canonicalClaimPath") != requirement.canonical_claim_path:
            _block(
                blockers,
                "STAGE_CLAIM_CANONICAL_PATH_MISMATCH",
                "Stage claim does not point to the exact canonical claim path.",
                stage_id=requirement.stage_id,
                path=requirement.stage_claim_path,
            )

    if result is not None and canonical is not None and stage_claim is not None:
        tokens = (
            result.get("claimToken"),
            canonical.get("claimToken"),
            stage_claim.get("claimToken"),
        )
        if (
            not all(isinstance(token, str) and token for token in tokens)
            or len(set(tokens)) != 1
        ):
            _block(
                blockers,
                "CLAIM_TOKEN_MISMATCH",
                "Terminal RESULT, canonical claim, and stage claim must carry one exact matching claimToken.",
                stage_id=requirement.stage_id,
            )

        terminal_state = result.get("state")
        if (
            canonical.get("state") != terminal_state
            or stage_claim.get("state") != terminal_state
        ):
            _block(
                blockers,
                "CLAIM_STATE_MISMATCH",
                "Canonical/stage claim states must exactly match the terminal RESULT state.",
                stage_id=requirement.stage_id,
            )
        if terminal_state in requirement.accepted_terminal_states and (
            canonical.get("state") not in requirement.accepted_terminal_states
            or stage_claim.get("state") not in requirement.accepted_terminal_states
        ):
            _block(
                blockers,
                "CLAIM_NOT_CLOSED_IN_ACCEPTED_STATE",
                "Accepted terminal RESULT requires both claims closed in the same accepted terminal state.",
                stage_id=requirement.stage_id,
            )

        tested = result.get("testedCommit")
        if (
            canonical.get("testedCommit") != tested
            or stage_claim.get("testedCommit") != tested
        ):
            _block(
                blockers,
                "TESTED_COMMIT_MISMATCH",
                "Terminal RESULT and both claims must carry the exact same testedCommit.",
                stage_id=requirement.stage_id,
            )

        if not _claim_points_to_result(canonical, requirement.result_path):
            _block(
                blockers,
                "CANONICAL_CLAIM_RESULT_PATH_MISMATCH",
                "Canonical claim does not point to the exact terminal RESULT JSON.",
                stage_id=requirement.stage_id,
                path=requirement.canonical_claim_path,
            )
        if not _claim_points_to_result(stage_claim, requirement.result_path):
            _block(
                blockers,
                "STAGE_CLAIM_RESULT_PATH_MISMATCH",
                "Stage claim does not point to the exact terminal RESULT JSON.",
                stage_id=requirement.stage_id,
                path=requirement.stage_claim_path,
            )

        movement = _true_movement_paths(canonical) + _true_movement_paths(stage_claim)
        if movement:
            _block(
                blockers,
                "ALPHA_LIVE_MOVED_BEFORE_RETRY",
                f"Claim authority reports forbidden movement at: {', '.join(movement)}.",
                stage_id=requirement.stage_id,
            )

    stage["accepted"] = len(blockers) == before
    tested_commit = stage["testedCommit"]
    return stage, tested_commit if isinstance(tested_commit, str) else None


def _validate_candidate(
    repo_root: Path,
    provenance_path: str,
    requirements: tuple[StageRequirement, ...],
    tested_commits: Mapping[str, str],
    blockers: list[dict[str, Any]],
    git_probe: GitProbeProtocol,
) -> dict[str, Any]:
    candidate_evidence: dict[str, Any] = {
        "provenancePath": provenance_path,
        "sourceCommit": None,
        "packageVersion": None,
        "candidatePath": None,
        "candidateSha256": None,
        "manifestPath": None,
        "manifestSha256": None,
        "requiredTestedCommits": None,
    }

    provenance, _ = _load_json(
        repo_root,
        provenance_path,
        blockers,
        missing_code="MISSING_FINAL_CANDIDATE_PROVENANCE",
        invalid_code="INVALID_FINAL_CANDIDATE_PROVENANCE",
    )
    if provenance is None:
        return candidate_evidence

    source_commit = provenance.get("sourceCommit")
    package_version = provenance.get("packageVersion")
    candidate_path = provenance.get("candidatePath")
    candidate_sha = provenance.get("candidateSha256")
    manifest_path = provenance.get("manifestPath")
    manifest_sha = provenance.get("manifestSha256")
    required_map = provenance.get("requiredTestedCommits")

    candidate_evidence.update(
        {
            "sourceCommit": source_commit,
            "packageVersion": package_version,
            "candidatePath": candidate_path,
            "candidateSha256": candidate_sha,
            "manifestPath": manifest_path,
            "manifestSha256": manifest_sha,
            "requiredTestedCommits": required_map,
        }
    )

    movement = _true_movement_paths(provenance)
    if movement:
        _block(
            blockers,
            "ALPHA_LIVE_MOVED_BEFORE_RETRY",
            f"Candidate provenance reports forbidden movement at: {', '.join(movement)}.",
            path=provenance_path,
        )

    if not isinstance(source_commit, str) or not _SHA40_RE.fullmatch(source_commit):
        _block(
            blockers,
            "INVALID_SOURCE_COMMIT",
            "Final candidate provenance must carry one exact 40-hex sourceCommit.",
            path=provenance_path,
        )
    elif not git_probe.commit_exists(source_commit):
        _block(
            blockers,
            "SOURCE_COMMIT_NOT_FOUND",
            f"Final candidate sourceCommit is not a valid repository commit: {source_commit}.",
            path=provenance_path,
        )

    if not isinstance(package_version, str) or not package_version:
        _block(
            blockers,
            "MISSING_PACKAGE_VERSION",
            "Final candidate provenance must carry a non-empty packageVersion.",
            path=provenance_path,
        )
    if not isinstance(candidate_path, str) or not candidate_path:
        _block(
            blockers,
            "MISSING_CANDIDATE_PATH",
            "Final candidate provenance must carry candidatePath.",
            path=provenance_path,
        )
    if not isinstance(candidate_sha, str) or not _SHA256_RE.fullmatch(candidate_sha):
        _block(
            blockers,
            "MISSING_OR_INVALID_CANDIDATE_SHA256",
            "Final candidate provenance must carry exact lowercase candidateSha256.",
            path=provenance_path,
        )
    if not isinstance(manifest_path, str) or not manifest_path:
        _block(
            blockers,
            "MISSING_MANIFEST_PATH",
            "Final candidate provenance must carry manifestPath for exact readback.",
            path=provenance_path,
        )
    if not isinstance(manifest_sha, str) or not _SHA256_RE.fullmatch(manifest_sha):
        _block(
            blockers,
            "MISSING_OR_INVALID_MANIFEST_SHA256",
            "Final candidate provenance must carry exact lowercase manifestSha256.",
            path=provenance_path,
        )

    expected_stage_ids = [requirement.stage_id for requirement in requirements]
    if not isinstance(required_map, dict):
        _block(
            blockers,
            "MISSING_REQUIRED_TESTED_COMMITS_PROVENANCE",
            "Final candidate provenance must carry requiredTestedCommits keyed by required stageId.",
            path=provenance_path,
        )
    else:
        if set(required_map) != set(expected_stage_ids):
            _block(
                blockers,
                "REQUIRED_TESTED_COMMITS_SET_MISMATCH",
                "Candidate requiredTestedCommits keys must exactly match the required repair stages.",
                path=provenance_path,
            )
        for stage_id in expected_stage_ids:
            terminal_tested = tested_commits.get(stage_id)
            if terminal_tested is not None and required_map.get(stage_id) != terminal_tested:
                _block(
                    blockers,
                    "CANDIDATE_REQUIRED_TESTED_COMMIT_MISMATCH",
                    (
                        "Candidate provenance does not pin the exact terminal testedCommit "
                        f"for {stage_id}."
                    ),
                    stage_id=stage_id,
                    path=provenance_path,
                )

    candidate: dict[str, Any] | None = None
    if isinstance(candidate_path, str) and candidate_path:
        candidate, candidate_raw = _load_json(
            repo_root,
            candidate_path,
            blockers,
            missing_code="MISSING_CANDIDATE_PAYLOAD",
            invalid_code="INVALID_CANDIDATE_PAYLOAD",
        )
        if candidate_raw is not None and isinstance(candidate_sha, str):
            actual = _sha256(candidate_raw)
            candidate_evidence["candidateActualSha256"] = actual
            if actual != candidate_sha:
                _block(
                    blockers,
                    "CANDIDATE_SHA256_MISMATCH",
                    f"Candidate SHA-256 readback mismatch: expected {candidate_sha}, got {actual}.",
                    path=candidate_path,
                )

    manifest: dict[str, Any] | None = None
    if isinstance(manifest_path, str) and manifest_path:
        manifest, manifest_raw = _load_json(
            repo_root,
            manifest_path,
            blockers,
            missing_code="MISSING_MANIFEST_PAYLOAD",
            invalid_code="INVALID_MANIFEST_PAYLOAD",
        )
        if manifest_raw is not None and isinstance(manifest_sha, str):
            actual = _sha256(manifest_raw)
            candidate_evidence["manifestActualSha256"] = actual
            if actual != manifest_sha:
                _block(
                    blockers,
                    "MANIFEST_SHA256_MISMATCH",
                    f"Manifest SHA-256 readback mismatch: expected {manifest_sha}, got {actual}.",
                    path=manifest_path,
                )

    for label, payload, payload_path in (
        ("candidate", candidate, candidate_path),
        ("manifest", manifest, manifest_path),
    ):
        if payload is None:
            continue
        if payload.get("sourceCommit") != source_commit:
            _block(
                blockers,
                f"{label.upper()}_SOURCE_COMMIT_MISMATCH",
                f"{label} sourceCommit does not exactly match provenance sourceCommit.",
                path=payload_path if isinstance(payload_path, str) else None,
            )
        if payload.get("packageVersion") != package_version:
            _block(
                blockers,
                f"{label.upper()}_PACKAGE_VERSION_MISMATCH",
                f"{label} packageVersion does not exactly match provenance packageVersion.",
                path=payload_path if isinstance(payload_path, str) else None,
            )
        movement = _true_movement_paths(payload)
        if movement:
            _block(
                blockers,
                "ALPHA_LIVE_MOVED_BEFORE_RETRY",
                f"{label} reports forbidden movement at: {', '.join(movement)}.",
                path=payload_path if isinstance(payload_path, str) else None,
            )

    if (
        isinstance(source_commit, str)
        and _SHA40_RE.fullmatch(source_commit)
        and git_probe.commit_exists(source_commit)
    ):
        for requirement in requirements:
            tested = tested_commits.get(requirement.stage_id)
            if tested is None or not _SHA40_RE.fullmatch(tested):
                continue
            if not git_probe.commit_exists(tested):
                _block(
                    blockers,
                    "TESTED_COMMIT_NOT_FOUND",
                    f"Required testedCommit is not a valid repository commit: {tested}.",
                    stage_id=requirement.stage_id,
                )
                continue
            if not git_probe.is_ancestor(tested, source_commit):
                _block(
                    blockers,
                    "SOURCE_COMMIT_MISSING_REQUIRED_TESTED_COMMIT",
                    (
                        f"sourceCommit {source_commit} does not contain required "
                        f"testedCommit {tested}."
                    ),
                    stage_id=requirement.stage_id,
                    path=provenance_path,
                )

    return candidate_evidence


def evaluate_readiness(
    repo_root: Path | str,
    *,
    candidate_provenance_path: str = DEFAULT_CANDIDATE_PROVENANCE,
    requirements: Iterable[StageRequirement] = DEFAULT_REQUIREMENTS,
    git_probe: GitProbeProtocol | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    ordered_requirements = tuple(requirements)
    blockers: list[dict[str, Any]] = []
    stages: dict[str, Any] = {}
    tested_commits: dict[str, str] = {}

    for requirement in ordered_requirements:
        stage, tested_commit = _validate_stage(root, requirement, blockers)
        stages[requirement.stage_id] = stage
        if tested_commit is not None:
            tested_commits[requirement.stage_id] = tested_commit

    probe = git_probe if git_probe is not None else GitProbe(root)
    candidate = _validate_candidate(
        root,
        candidate_provenance_path,
        ordered_requirements,
        tested_commits,
        blockers,
        probe,
    )

    ready = not blockers
    return {
        "schema": SCHEMA,
        "state": READY if ready else BLOCKED,
        "readyForOneBoundedOwnerRetry": ready,
        "ownerRetryBudget": 1 if ready else 0,
        "promotionAuthorized": False,
        "alphaLiveMoveAuthorized": False,
        "realGameRunPerformed": False,
        "candidate": candidate,
        "stages": stages,
        "blockerCount": len(blockers),
        "blockers": blockers,
    }


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail-closed Alpha V1 repo-side gate for exactly one bounded Owner retry. "
            "This command never runs WOF and never promotes alpha-live."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=_default_repo_root())
    parser.add_argument(
        "--candidate-provenance",
        default=DEFAULT_CANDIDATE_PROVENANCE,
        help="Repository-relative final candidate provenance JSON.",
    )
    args = parser.parse_args(argv)
    result = evaluate_readiness(
        args.repo_root,
        candidate_provenance_path=args.candidate_provenance,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["readyForOneBoundedOwnerRetry"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
