from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

SESSION_SCHEMA = "wof-alpha-owner-acceptance-provenance-durable-session-v1"
ROOT_SCHEMA = "wof-alpha-owner-acceptance-provenance-root-v1"
EPOCH_SCHEMA = "wof-alpha-owner-acceptance-epoch-transition-v1"
VERSION = 1
MAX_ARTIFACTS = 32
MAX_TRANSITIONS = 16

OPEN = "OPEN"
WAITING_FOR_LIVE_W3 = "WAITING_FOR_LIVE_W3"
WAITING_FOR_CANONICAL_EVIDENCE = "WAITING_FOR_CANONICAL_EVIDENCE"
WAITING_FOR_DYNAMIC_TEMPORAL_EVIDENCE = "WAITING_FOR_DYNAMIC_TEMPORAL_EVIDENCE"
READY_FOR_OWNER_VISUAL_CONFIRMATION = "READY_FOR_OWNER_VISUAL_CONFIRMATION"
WAITING_FOR_PROMOTION = "WAITING_FOR_PROMOTION"
WAITING_FOR_POST_PROMOTION_VERIFY = "WAITING_FOR_POST_PROMOTION_VERIFY"
CHAIN_COMPLETE = "CHAIN_COMPLETE"
REJECTED = "REJECTED"

STATE_RANK = {
    OPEN: 0,
    WAITING_FOR_LIVE_W3: 1,
    WAITING_FOR_CANONICAL_EVIDENCE: 2,
    WAITING_FOR_DYNAMIC_TEMPORAL_EVIDENCE: 3,
    READY_FOR_OWNER_VISUAL_CONFIRMATION: 4,
    WAITING_FOR_PROMOTION: 5,
    WAITING_FOR_POST_PROMOTION_VERIFY: 6,
    CHAIN_COMPLETE: 7,
    REJECTED: 99,
}

ORDER_GROUP = {
    "P19": 0,
    "P21": 1,
    "W3": 2,
    "P16": 2,
    "P18": 2,
    "P22": 3,
    "P24": 3,
    "P25": 3,
    "P17": 4,
    "P20_RECEIPT": 5,
    "P20_PLAN": 6,
    "P20_RESULT": 6,
    "P23": 7,
}

REQUIRED_STAGES = ("P19", "P21", "W3", "P16", "P18", "P22", "P24", "P17", "P20_RECEIPT", "P20_PLAN", "P20_RESULT", "P23")
IDENTITY_FIELDS = ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch")
SAFETY = {
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "screenshotProductionCoordinates": False,
    "worldProjectionProductionCoordinates": False,
    "guessedCoordinates": False,
    "visibleProof": "NOT_PROVEN",
    "realWofAcceptance": "NOT_RUN",
    "ownerVisualAcceptance": "NOT_RUN",
    "alphaLiveMoved": False,
}


class ProvenanceError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvenanceError(f"unreadable JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProvenanceError(f"JSON root must be an object: {path}")
    return value


def require_text(value: Any, name: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value) < minimum:
        raise ProvenanceError(f"{name} must be a string of length >= {minimum}")
    return value


def require_hex(value: Any, name: str, size: int) -> str:
    text = require_text(value, name, size)
    if len(text) != size or any(ch not in "0123456789abcdef" for ch in text):
        raise ProvenanceError(f"{name} must be exact lower-case {size}-hex")
    return text


def require_safety(value: Any, source: str) -> None:
    if not isinstance(value, Mapping):
        raise ProvenanceError(f"{source}: safety missing")
    for key, expected in (("readOnly", True), ("ramWrites", 0), ("inputInjection", False)):
        if value.get(key) != expected:
            raise ProvenanceError(f"{source}: safety mismatch {key}={value.get(key)!r}")
    for key in ("legacySpatialFallback", "screenshotProductionCoordinates", "worldProjectionProductionCoordinates", "guessedCoordinates", "guessedAddresses", "guessedRendererObjectAddress"):
        if key in value and value.get(key) is not False:
            raise ProvenanceError(f"{source}: forbidden safety flag {key}={value.get(key)!r}")


def normalize_identity(value: Any, source: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ProvenanceError(f"{source}: identity missing")
    out: dict[str, str] = {}
    for field in IDENTITY_FIELDS:
        minimum = 16 if field in ("runtimeEpoch", "rendererEpoch") else 1
        out[field] = require_text(value.get(field), f"{source}.{field}", minimum)
    require_hex(out["worldSha256"], f"{source}.worldSha256", 64)
    return out


def normalize_candidate(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ProvenanceError("root candidate missing")
    return {
        "sourceCommit": require_hex(value.get("sourceCommit"), "candidate.sourceCommit", 40),
        "packageVersion": require_text(value.get("packageVersion"), "candidate.packageVersion"),
        "candidateSha256": require_hex(value.get("candidateSha256"), "candidate.candidateSha256", 64),
        "attestationSha256": require_hex(value.get("attestationSha256"), "candidate.attestationSha256", 64),
    }


def normalize_root(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("schema") != ROOT_SCHEMA or value.get("version") != VERSION:
        raise ProvenanceError("root schema/version mismatch")
    require_safety(value.get("safety"), "root")
    root = {
        "schema": ROOT_SCHEMA,
        "version": VERSION,
        "sessionId": require_text(value.get("sessionId"), "root.sessionId", 8),
        "runNonce": require_text(value.get("runNonce"), "root.runNonce", 16),
        "p25RunNonce": value.get("p25RunNonce"),
        "candidate": normalize_candidate(value.get("candidate")),
        "initialIdentity": normalize_identity(value.get("initialIdentity"), "root.initialIdentity"),
        "p21": dict(value.get("p21")) if isinstance(value.get("p21"), Mapping) else None,
        "createdAtUtc": require_text(value.get("createdAtUtc"), "root.createdAtUtc"),
        "safety": dict(SAFETY),
        "state": OPEN,
    }
    if root["p25RunNonce"] is not None:
        root["p25RunNonce"] = require_text(root["p25RunNonce"], "root.p25RunNonce", 16)
    if root["p21"] is not None:
        if "runId" in root["p21"]:
            require_text(root["p21"].get("runId"), "root.p21.runId", 1)
        if "receiptSha256" in root["p21"]:
            require_hex(root["p21"].get("receiptSha256"), "root.p21.receiptSha256", 64)
    return root


def digest_core(session: Mapping[str, Any]) -> dict[str, Any]:
    root = dict(session["root"])
    root.pop("createdAtUtc", None)
    return {
        "schema": session["schema"],
        "version": session["version"],
        "root": root,
        "currentIdentity": session["currentIdentity"],
        "artifactLedger": session["artifactLedger"],
        "epochTransitions": session["epochTransitions"],
        "state": session["state"],
        "rejection": session.get("rejection"),
        "safety": session["safety"],
    }


def refresh_digest(session: dict[str, Any]) -> None:
    session["chainDigest"] = sha256_bytes(canonical_bytes(digest_core(session)))


def new_session(root: Mapping[str, Any]) -> dict[str, Any]:
    normalized = normalize_root(root)
    session = {
        "schema": SESSION_SCHEMA,
        "version": VERSION,
        "root": normalized,
        "currentIdentity": dict(normalized["initialIdentity"]),
        "artifactLedger": [],
        "epochTransitions": [],
        "state": OPEN,
        "terminal": False,
        "rejection": None,
        "safety": dict(SAFETY),
    }
    refresh_digest(session)
    return session


def _fsync_parent(path: Path) -> None:
    flags = getattr(os, "O_RDONLY", 0)
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    try:
        fd = os.open(str(path), flags)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def atomic_write(path: Path, payload: Mapping[str, Any], *, create_only: bool = False) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if create_only and path.exists():
        raise ProvenanceError(f"immutable session path already exists: {path}")
    if path.exists():
        existing = load_json(path)
        if existing.get("terminal") is True:
            raise ProvenanceError(f"terminal session is immutable: {path}")
    data = canonical_bytes(payload)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        _fsync_parent(path.parent)
    finally:
        temp.unlink(missing_ok=True)


def stage_map(session: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(row["stage"]): row for row in session.get("artifactLedger", []) if isinstance(row, Mapping)}


def latest_order_group(session: Mapping[str, Any]) -> int:
    rows = session.get("artifactLedger") or []
    return max((ORDER_GROUP.get(str(row.get("stage")), -1) for row in rows if isinstance(row, Mapping)), default=-1)


def expected_state(session: Mapping[str, Any]) -> str:
    stages = stage_map(session)
    if not {"P19", "P21"}.issubset(stages):
        return OPEN
    if "W3" not in stages:
        return WAITING_FOR_LIVE_W3
    if not {"P16", "P18"}.issubset(stages):
        return WAITING_FOR_CANONICAL_EVIDENCE
    if not {"P22", "P24", "P17"}.issubset(stages):
        return WAITING_FOR_DYNAMIC_TEMPORAL_EVIDENCE
    if "P20_RECEIPT" not in stages:
        return READY_FOR_OWNER_VISUAL_CONFIRMATION
    if not {"P20_PLAN", "P20_RESULT"}.issubset(stages):
        return WAITING_FOR_PROMOTION
    if "P23" not in stages:
        return WAITING_FOR_POST_PROMOTION_VERIFY
    return CHAIN_COMPLETE


def _monotonic_update(session: dict[str, Any]) -> None:
    wanted = expected_state(session)
    if STATE_RANK[wanted] < STATE_RANK[session["state"]]:
        raise ProvenanceError(f"state regression forbidden: {session['state']} -> {wanted}")
    session["state"] = wanted
    if wanted == CHAIN_COMPLETE:
        session["terminal"] = True
    refresh_digest(session)


def reject(session: dict[str, Any], *, source: str, reason: str) -> None:
    if session.get("terminal") is True:
        raise ProvenanceError("terminal session is immutable")
    if session.get("rejection") is None:
        session["rejection"] = {"firstIncompatibleArtifact": source, "reason": reason}
    session["state"] = REJECTED
    session["terminal"] = True
    refresh_digest(session)


def _candidate_bindings(session: Mapping[str, Any], bindings: Mapping[str, Any], source: str) -> None:
    candidate = session["root"]["candidate"]
    for key in ("sourceCommit", "packageVersion", "candidateSha256"):
        if bindings.get(key) != candidate[key]:
            raise ProvenanceError(f"{source}: candidate binding mismatch {key}")
    if "attestationSha256" in bindings and bindings.get("attestationSha256") != candidate["attestationSha256"]:
        raise ProvenanceError(f"{source}: candidate binding mismatch attestationSha256")


def _identity_bindings(session: Mapping[str, Any], bindings: Mapping[str, Any], source: str) -> None:
    expected = session["currentIdentity"]
    for field in IDENTITY_FIELDS:
        if bindings.get(field) != expected[field]:
            raise ProvenanceError(f"{source}: identity binding mismatch {field}")


def _artifact_identity(raw: Mapping[str, Any], stage: str) -> dict[str, Any]:
    if stage == "W3":
        ident = raw.get("captureIdentity") if isinstance(raw.get("captureIdentity"), Mapping) else {}
        return {field: ident.get(field) for field in IDENTITY_FIELDS}
    if stage == "P16":
        world = raw.get("world") if isinstance(raw.get("world"), Mapping) else {}
        runtime = raw.get("runtime") if isinstance(raw.get("runtime"), Mapping) else {}
        return {"worldSha256": world.get("sha256"), "pageTargetId": world.get("pageTargetId"), "authorityKey": runtime.get("authorityKey"), "runtimeEpoch": runtime.get("epoch"), "rendererEpoch": runtime.get("rendererEpoch")}
    if stage == "P18":
        ident = raw.get("identity") if isinstance(raw.get("identity"), Mapping) else {}
        return {field: ident.get(field) for field in IDENTITY_FIELDS}
    ident = raw.get("identity") if isinstance(raw.get("identity"), Mapping) else {}
    return {field: ident.get(field) for field in IDENTITY_FIELDS}


def _check_native_identity(session: Mapping[str, Any], raw: Mapping[str, Any], stage: str) -> None:
    ident = _artifact_identity(raw, stage)
    if all(value in (None, "") for value in ident.values()):
        return
    expected = session["currentIdentity"]
    for field in IDENTITY_FIELDS:
        if ident.get(field) not in (None, "", expected[field]):
            raise ProvenanceError(f"{stage}: native identity mismatch {field}")


def _validate_stage(session: Mapping[str, Any], stage: str, raw: Mapping[str, Any], byte_sha: str, bindings: Mapping[str, Any]) -> None:
    root = session["root"]
    candidate = root["candidate"]
    _candidate_bindings(session, bindings, stage)
    if stage not in {"P19", "P20_PLAN", "P20_RESULT"}:
        if all(field in bindings for field in IDENTITY_FIELDS):
            _identity_bindings(session, bindings, stage)
    schema = raw.get("schema")
    if stage == "P19":
        if raw.get("sourceCommit") != candidate["sourceCommit"] or raw.get("packageVersion") != candidate["packageVersion"]:
            raise ProvenanceError("P19: native candidate mismatch")
        if byte_sha != candidate["candidateSha256"]:
            raise ProvenanceError("P19: candidate byte hash mismatch")
        require_safety(raw.get("safety"), "P19")
    elif stage == "P21":
        if schema != "wof-alpha-p21-prepromotion-staging-receipt-v1" or raw.get("version") != 1:
            raise ProvenanceError("P21: schema/version mismatch")
        embedded = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
        for key in ("sourceCommit", "packageVersion", "candidateSha256"):
            if embedded.get(key) not in (None, candidate[key]):
                raise ProvenanceError(f"P21: native candidate mismatch {key}")
        if raw.get("alphaLiveMoved") is not False or raw.get("ownerVisualAcceptance") != "NOT_RUN" or raw.get("realWofAcceptance") != "NOT_RUN":
            raise ProvenanceError("P21: proof/safety boundary mismatch")
        require_safety(raw.get("safety"), "P21")
        if root.get("p21") and root["p21"].get("receiptSha256") not in (None, byte_sha):
            raise ProvenanceError("P21: root receipt SHA mismatch")
    elif stage == "W3":
        if schema != "wof-render-source-qualification-v1":
            raise ProvenanceError("W3: schema mismatch")
        _check_native_identity(session, raw, stage)
    elif stage == "P16":
        if schema != "wof-alpha-canonical-owner-acceptance-evidence-v1" or raw.get("version") != 1:
            raise ProvenanceError("P16: schema/version mismatch")
        if raw.get("visibleProof") != "NOT_PROVEN":
            raise ProvenanceError("P16: visibleProof boundary mismatch")
        require_safety(raw.get("safety"), "P16")
        _check_native_identity(session, raw, stage)
    elif stage == "P18":
        if schema != "wof-alpha-canonical-draw-evidence-v1" or raw.get("version") != 1:
            raise ProvenanceError("P18: schema/version mismatch")
        if raw.get("visibleProof") != "NOT_PROVEN":
            raise ProvenanceError("P18: visibleProof boundary mismatch")
        require_safety(raw.get("safety"), "P18")
        _check_native_identity(session, raw, stage)
        generation = bindings.get("ackGeneration")
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
            raise ProvenanceError("P18: ackGeneration binding invalid")
        if raw.get("evidenceGeneration") != generation:
            raise ProvenanceError("P18: stale generation")
        previous = 0
        rows = raw.get("acknowledgements") if isinstance(raw.get("acknowledgements"), list) else []
        for row in rows:
            if not isinstance(row, Mapping) or row.get("evidenceGeneration") != generation:
                raise ProvenanceError("P18: ACK generation mismatch")
            seq = row.get("sequence")
            if not isinstance(seq, int) or seq <= previous:
                raise ProvenanceError("P18: ACK sequence invalid")
            previous = seq
    elif stage == "P22":
        if schema != "wof-alpha-dynamic-actor-state-coverage-v1":
            raise ProvenanceError("P22: schema mismatch")
        expected_run = root.get("p25RunNonce") or root["runNonce"]
        if bindings.get("runNonce") != expected_run:
            raise ProvenanceError("P22: cross-run output")
        _check_native_identity(session, raw, stage)
    elif stage == "P24":
        if schema not in {"wof-alpha-canonical-temporal-stability-evidence-v1", "wof-alpha-canonical-temporal-observation-bundle-v1"}:
            raise ProvenanceError("P24: schema mismatch")
        expected_run = root.get("p25RunNonce") or root["runNonce"]
        if bindings.get("runNonce") != expected_run:
            raise ProvenanceError("P24: cross-run output")
        _check_native_identity(session, raw, stage)
        p18 = stage_map(session).get("P18")
        if p18 and bindings.get("ackGeneration") != p18["bindings"].get("ackGeneration"):
            raise ProvenanceError("P24: stale generation/ACK binding")
    elif stage == "P25":
        if schema != "wof-alpha-p25-final-acceptance-composite-index-v1":
            raise ProvenanceError("P25: schema mismatch")
        if root.get("p25RunNonce") is None or bindings.get("runNonce") != root["p25RunNonce"]:
            raise ProvenanceError("P25: run nonce mismatch")
        require_safety(raw.get("safety"), "P25")
    elif stage == "P17":
        if schema != "wof-alpha-final-acceptance-bundle-v1" or raw.get("version") != 1:
            raise ProvenanceError("P17: schema/version mismatch")
        if raw.get("visibleProof") != "NOT_PROVEN":
            raise ProvenanceError("P17: visibleProof boundary mismatch")
        dependencies = bindings.get("dependencyHashes")
        if not isinstance(dependencies, Mapping):
            raise ProvenanceError("P17: dependencyHashes missing")
        stages = stage_map(session)
        required = ["P19", "P21", "W3", "P16", "P18", "P22", "P24"]
        if "P25" in stages:
            required.append("P25")
        expected = {name: stages[name]["byteSha256"] for name in required}
        if dict(dependencies) != expected:
            raise ProvenanceError("P17: dependency hash mismatch")
        embedded = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
        if embedded:
            if embedded.get("sourceCommit") not in (None, candidate["sourceCommit"]) or embedded.get("packageVersion") not in (None, candidate["packageVersion"]):
                raise ProvenanceError("P17: native candidate mismatch")
            if embedded.get("contentSha256") not in (None, candidate["candidateSha256"]):
                raise ProvenanceError("P17: native candidate hash mismatch")
        _check_native_identity(session, raw, stage)
    elif stage == "P20_RECEIPT":
        if schema != "wof-alpha-owner-visual-confirmation-receipt-v1" or raw.get("version") != 1:
            raise ProvenanceError("P20 receipt: schema/version mismatch")
        if raw.get("fixtureMode") is not False or raw.get("promotionEligible") is not True:
            raise ProvenanceError("P20 receipt: fixture/non-eligible evidence cannot fill real slot")
        if raw.get("ownerVisualVerdict") != "PASS" or raw.get("ownerAnswer") != "YES" or raw.get("visualProof") != "OWNER_VISUAL_PASS":
            raise ProvenanceError("P20 receipt: real visual PASS fields missing")
        p17 = stage_map(session).get("P17")
        if p17 is None or raw.get("acceptanceBundleSha256") != p17["byteSha256"]:
            raise ProvenanceError("P20 receipt: P17 bundle hash mismatch")
        if raw.get("candidateSourceCommit") != candidate["sourceCommit"] or raw.get("candidateSha256") != candidate["candidateSha256"] or raw.get("candidateAttestationSha256") != candidate["attestationSha256"]:
            raise ProvenanceError("P20 receipt: candidate binding mismatch")
        _check_native_identity(session, raw, stage)
        require_safety(raw.get("safety"), "P20 receipt")
    elif stage == "P20_PLAN":
        if schema != "wof-alpha-live-promotion-plan-v1" or raw.get("version") != 1 or raw.get("state") != "READY":
            raise ProvenanceError("P20 plan: schema/state mismatch")
        core = raw.get("planCore") if isinstance(raw.get("planCore"), Mapping) else {}
        if raw.get("planHash") != sha256_bytes(canonical_bytes(core)):
            raise ProvenanceError("P20 plan: hash mismatch")
        receipt = stage_map(session).get("P20_RECEIPT")
        p17 = stage_map(session).get("P17")
        checks = {
            "toCandidateCommit": candidate["sourceCommit"],
            "packageVersion": candidate["packageVersion"],
            "candidateSha256": candidate["candidateSha256"],
            "candidateAttestationSha256": candidate["attestationSha256"],
            "acceptanceBundleSha256": p17["byteSha256"] if p17 else None,
            "visualReceiptSha256": receipt["byteSha256"] if receipt else None,
        }
        for key, expected in checks.items():
            if core.get(key) != expected:
                raise ProvenanceError(f"P20 plan: binding mismatch {key}")
        if core.get("fastForwardRequired") is not True or core.get("compareAndSwapExpectedOld") != core.get("fromAlphaLiveCommit"):
            raise ProvenanceError("P20 plan: CAS/fast-forward mismatch")
        require_safety(core.get("safety"), "P20 plan")
        safety = core.get("safety")
        if safety.get("forcePushAllowed") is not False or safety.get("alphaLiveMovedAtPlan") is not False:
            raise ProvenanceError("P20 plan: unsafe promotion plan")
    elif stage == "P20_RESULT":
        if schema != "wof-alpha-live-promotion-result-v1" or raw.get("version") != 1 or raw.get("state") != "PROMOTED":
            raise ProvenanceError("P20 result: schema/state mismatch")
        plan_entry = stage_map(session).get("P20_PLAN")
        if plan_entry is None:
            raise ProvenanceError("P20 result: plan missing")
        plan = load_json(Path(plan_entry["path"]))
        core = plan["planCore"]
        if raw.get("planHash") != plan.get("planHash") or raw.get("fromAlphaLiveCommit") != core.get("fromAlphaLiveCommit") or raw.get("toCandidateCommit") != core.get("toCandidateCommit"):
            raise ProvenanceError("P20 result: plan/CAS binding mismatch")
        if raw.get("forcePushUsed") is not False or raw.get("fastForwardOnly") is not True:
            raise ProvenanceError("P20 result: unsafe promotion result")
    elif stage == "P23":
        if schema not in {"wof-alpha-post-promotion-verification-v1", "wof-alpha-v1-final-close-bundle-v1", "wof-alpha-project-close-verification-v1"}:
            raise ProvenanceError("P23: schema mismatch")
        if bindings.get("promotedSessionId") != root["sessionId"]:
            raise ProvenanceError("P23: cross-session close evidence")
        result = stage_map(session).get("P20_RESULT")
        if result is None or bindings.get("promotionResultSha256") != result["byteSha256"]:
            raise ProvenanceError("P23: promotion result hash mismatch")
        if raw.get("candidateSourceCommit") not in (None, candidate["sourceCommit"]):
            raise ProvenanceError("P23: candidate mismatch")
    else:
        raise ProvenanceError(f"unsupported stage {stage}")


def bind_artifact(session: dict[str, Any], *, stage: str, path: Path, bindings: Mapping[str, Any], semantic_id: str | None = None) -> dict[str, Any]:
    if session.get("terminal") is True:
        raise ProvenanceError("terminal session is immutable")
    if stage not in ORDER_GROUP:
        reject(session, source=stage, reason=f"unsupported stage {stage}")
        raise ProvenanceError(f"unsupported stage {stage}")
    if len(session["artifactLedger"]) >= MAX_ARTIFACTS:
        reject(session, source=stage, reason="artifact ledger bound exceeded")
        raise ProvenanceError("artifact ledger bound exceeded")
    if stage in stage_map(session):
        reject(session, source=stage, reason="duplicate stage artifact")
        raise ProvenanceError(f"duplicate stage artifact: {stage}")
    group = ORDER_GROUP[stage]
    if group < latest_order_group(session):
        reject(session, source=stage, reason="artifact order regression")
        raise ProvenanceError(f"artifact order regression: {stage}")
    path = path.expanduser().resolve()
    try:
        raw = load_json(path)
        byte_sha = sha256_file(path)
        _validate_stage(session, stage, raw, byte_sha, bindings)
        entry = {
            "ordinal": len(session["artifactLedger"]) + 1,
            "stage": stage,
            "path": str(path),
            "schema": raw.get("schema"),
            "version": raw.get("version"),
            "byteSha256": byte_sha,
            "semanticId": semantic_id or f"{session['root']['sessionId']}:{stage}",
            "bindings": json.loads(json.dumps(bindings, sort_keys=True)),
        }
        semantic_core = {key: entry[key] for key in ("ordinal", "stage", "schema", "version", "semanticId", "bindings")}
        entry["semanticSha256"] = sha256_bytes(canonical_bytes(semantic_core))
        if any(existing["path"] == entry["path"] for existing in session["artifactLedger"]):
            raise ProvenanceError("artifact path re-entry")
        if any(existing["semanticId"] == entry["semanticId"] for existing in session["artifactLedger"]):
            raise ProvenanceError("semantic identity re-entry")
        session["artifactLedger"].append(entry)
        _monotonic_update(session)
        return entry
    except ProvenanceError as exc:
        if session.get("terminal") is not True:
            reject(session, source=stage, reason=str(exc))
        raise


def bind_epoch_transition(session: dict[str, Any], *, path: Path) -> dict[str, Any]:
    if session.get("terminal") is True:
        raise ProvenanceError("terminal session is immutable")
    if len(session["epochTransitions"]) >= MAX_TRANSITIONS:
        reject(session, source="EPOCH_TRANSITION", reason="transition bound exceeded")
        raise ProvenanceError("transition bound exceeded")
    if "P17" in stage_map(session):
        reject(session, source="EPOCH_TRANSITION", reason="epoch transition after P17 is forbidden")
        raise ProvenanceError("epoch transition after P17 is forbidden")
    path = path.expanduser().resolve()
    try:
        raw = load_json(path)
        if raw.get("schema") != EPOCH_SCHEMA or raw.get("version") != VERSION:
            raise ProvenanceError("epoch transition schema/version mismatch")
        sequence = raw.get("sequence")
        if sequence != len(session["epochTransitions"]) + 1:
            raise ProvenanceError("epoch transition sequence mismatch")
        before = normalize_identity(raw.get("before"), "transition.before")
        after = normalize_identity(raw.get("after"), "transition.after")
        if before != session["currentIdentity"]:
            raise ProvenanceError("epoch transition before identity does not match current authority")
        if after["worldSha256"] != before["worldSha256"] or after["pageTargetId"] != before["pageTargetId"]:
            raise ProvenanceError("unrelated World/page transition is forbidden")
        if after == before:
            raise ProvenanceError("epoch transition must change runtime/renderer authority")
        evidence = raw.get("authorityEvidenceSha256")
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 8:
            raise ProvenanceError("epoch transition authority evidence missing/unbounded")
        for index, digest in enumerate(evidence):
            require_hex(digest, f"transition.authorityEvidenceSha256[{index}]", 64)
        entry = {
            "sequence": sequence,
            "path": str(path),
            "byteSha256": sha256_file(path),
            "before": before,
            "after": after,
            "authorityEvidenceSha256": list(evidence),
        }
        transition_core = {key: entry[key] for key in ("sequence", "byteSha256", "before", "after", "authorityEvidenceSha256")}
        entry["transitionSha256"] = sha256_bytes(canonical_bytes(transition_core))
        session["epochTransitions"].append(entry)
        session["currentIdentity"] = after
        refresh_digest(session)
        return entry
    except ProvenanceError as exc:
        if session.get("terminal") is not True:
            reject(session, source="EPOCH_TRANSITION", reason=str(exc))
        raise


def verify_session(session: Mapping[str, Any]) -> dict[str, Any]:
    if session.get("schema") != SESSION_SCHEMA or session.get("version") != VERSION:
        raise ProvenanceError("session schema/version mismatch")
    require_safety(session.get("safety"), "session")
    normalize_root(session.get("root"))
    if len(session.get("artifactLedger") or []) > MAX_ARTIFACTS or len(session.get("epochTransitions") or []) > MAX_TRANSITIONS:
        raise ProvenanceError("persisted ledger bound exceeded")
    previous_group = -1
    seen_stage: set[str] = set()
    seen_path: set[str] = set()
    for entry in session.get("artifactLedger") or []:
        if not isinstance(entry, Mapping):
            raise ProvenanceError("persisted artifact row malformed")
        stage = require_text(entry.get("stage"), "persisted.stage")
        if stage in seen_stage or entry.get("path") in seen_path:
            raise ProvenanceError("persisted ledger re-entry")
        seen_stage.add(stage); seen_path.add(str(entry.get("path")))
        group = ORDER_GROUP.get(stage, -1)
        if group < previous_group:
            raise ProvenanceError("persisted artifact order regression")
        previous_group = group
        path = Path(require_text(entry.get("path"), f"{stage}.path"))
        if not path.is_file() or sha256_file(path) != entry.get("byteSha256"):
            raise ProvenanceError(f"{stage}: persisted artifact byte hash mismatch")
        raw = load_json(path)
        if raw.get("schema") != entry.get("schema"):
            raise ProvenanceError(f"{stage}: persisted artifact schema mismatch")
    for index, transition in enumerate(session.get("epochTransitions") or [], 1):
        if not isinstance(transition, Mapping) or transition.get("sequence") != index:
            raise ProvenanceError("persisted epoch transition sequence mismatch")
        path = Path(require_text(transition.get("path"), "transition.path"))
        if not path.is_file() or sha256_file(path) != transition.get("byteSha256"):
            raise ProvenanceError("persisted epoch transition byte hash mismatch")
    wanted = REJECTED if session.get("rejection") else expected_state(session)
    if session.get("state") != wanted:
        raise ProvenanceError(f"persisted state mismatch: {session.get('state')} != {wanted}")
    should_terminal = wanted in {CHAIN_COMPLETE, REJECTED}
    if session.get("terminal") is not should_terminal:
        raise ProvenanceError("persisted terminal flag mismatch")
    expected_digest = sha256_bytes(canonical_bytes(digest_core(session)))
    if session.get("chainDigest") != expected_digest:
        raise ProvenanceError("chain digest mismatch")
    return {"state": "VERIFIED", "sessionState": wanted, "terminal": should_terminal, "chainDigest": expected_digest, "artifactCount": len(session.get("artifactLedger") or []), "transitionCount": len(session.get("epochTransitions") or [])}


def verify_file(path: Path) -> dict[str, Any]:
    return verify_session(load_json(path.expanduser().resolve()))


def summary_markdown(session: Mapping[str, Any]) -> str:
    rejection = session.get("rejection") or {}
    lines = [
        "# Alpha V1 Owner Acceptance Provenance Session",
        "",
        f"- Session: `{session['root']['sessionId']}`",
        f"- Candidate: `{session['root']['candidate']['sourceCommit']}` / `{session['root']['candidate']['packageVersion']}`",
        f"- State: **{session['state']}**",
        f"- Artifacts: `{len(session['artifactLedger'])}`",
        f"- Epoch transitions: `{len(session['epochTransitions'])}`",
        f"- Chain digest: `{session['chainDigest']}`",
        "- visibleProof: `NOT_PROVEN`",
        "- realWofAcceptance: `NOT_RUN`",
        "- ownerVisualAcceptance: `NOT_RUN`",
        "- alphaLiveMoved: `false`",
    ]
    if rejection:
        lines.extend([f"- First incompatible artifact: `{rejection.get('firstIncompatibleArtifact')}`", f"- Rejection reason: `{rejection.get('reason')}`"])
    return "\n".join(lines) + "\n"


def write_summary(session_path: Path, summary_path: Path | None = None) -> Path:
    session_path = session_path.expanduser().resolve()
    session = load_json(session_path)
    verify_session(session)
    output = summary_path.expanduser().resolve() if summary_path is not None else session_path.with_suffix(".md")
    if session.get("terminal") is True and output.exists():
        raise ProvenanceError(f"terminal summary is immutable: {output}")
    data = summary_markdown(session).encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, output); _fsync_parent(output.parent)
    finally:
        temp.unlink(missing_ok=True)
    return output


def open_file(root_path: Path, session_path: Path) -> dict[str, Any]:
    session = new_session(load_json(root_path.expanduser().resolve()))
    atomic_write(session_path, session, create_only=True)
    return session


def mutate_file(session_path: Path, mutator) -> dict[str, Any]:
    session_path = session_path.expanduser().resolve()
    session = load_json(session_path)
    verify_session(session)
    if session.get("terminal") is True:
        raise ProvenanceError("terminal session is immutable")
    try:
        mutator(session)
    except ProvenanceError:
        atomic_write(session_path, session)
        raise
    atomic_write(session_path, session)
    return session


def finalize_file(session_path: Path, summary_path: Path | None = None) -> dict[str, Any]:
    session_path = session_path.expanduser().resolve()
    session = load_json(session_path)
    verify_session(session)
    if session["state"] != CHAIN_COMPLETE or session.get("terminal") is not True:
        raise ProvenanceError(f"cannot finalize incomplete session: {session['state']}")
    write_summary(session_path, summary_path)
    return session


def _parse_bindings(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProvenanceError(f"bindings JSON invalid: {exc}") from exc
    if not isinstance(value, dict):
        raise ProvenanceError("bindings JSON must be an object")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Durable P28 Alpha V1 final-acceptance provenance/session chain.")
    sub = parser.add_subparsers(dest="command", required=True)
    op = sub.add_parser("open"); op.add_argument("--root", type=Path, required=True); op.add_argument("--session", type=Path, required=True)
    bind = sub.add_parser("bind"); bind.add_argument("--session", type=Path, required=True); bind.add_argument("--stage", choices=tuple(ORDER_GROUP), required=True); bind.add_argument("--artifact", type=Path, required=True); bind.add_argument("--bindings-json", required=True); bind.add_argument("--semantic-id")
    transition = sub.add_parser("transition"); transition.add_argument("--session", type=Path, required=True); transition.add_argument("--artifact", type=Path, required=True)
    status = sub.add_parser("status"); status.add_argument("--session", type=Path, required=True)
    verify = sub.add_parser("verify"); verify.add_argument("--session", type=Path, required=True)
    finalize = sub.add_parser("finalize"); finalize.add_argument("--session", type=Path, required=True); finalize.add_argument("--summary", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "open":
            session = open_file(args.root, args.session)
            result = {"state": session["state"], "chainDigest": session["chainDigest"]}
        elif args.command == "bind":
            session = mutate_file(args.session, lambda value: bind_artifact(value, stage=args.stage, path=args.artifact, bindings=_parse_bindings(args.bindings_json), semantic_id=args.semantic_id))
            result = {"state": session["state"], "chainDigest": session["chainDigest"]}
        elif args.command == "transition":
            session = mutate_file(args.session, lambda value: bind_epoch_transition(value, path=args.artifact))
            result = {"state": session["state"], "chainDigest": session["chainDigest"]}
        elif args.command in {"status", "verify"}:
            result = verify_file(args.session)
        else:
            session = finalize_file(args.session, args.summary)
            result = {"state": session["state"], "terminal": session["terminal"], "chainDigest": session["chainDigest"]}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except ProvenanceError as exc:
        print(f"PROVENANCE_ERROR: {exc}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
