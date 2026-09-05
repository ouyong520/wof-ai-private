from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

SESSION_SCHEMA = "wof-alpha-owner-acceptance-provenance-session-v1"
MANIFEST_SCHEMA = "wof-alpha-owner-acceptance-provenance-manifest-v1"
VERSION = 1

STAGES = ("P19", "P21", "W3", "P16", "P18", "P22", "P24", "P17", "P20_RECEIPT", "P20_PLAN", "P20_RESULT", "P23")
TRANSITIONS = (
    ("PRECHECK", "RENDERER_QUALIFIED", ("P19", "P21", "W3", "P16", "P18")),
    ("RENDERER_QUALIFIED", "OWNER_READY", ("P22", "P24", "P17")),
    ("OWNER_READY", "OWNER_RECEIPT", ("P20_RECEIPT",)),
    ("OWNER_RECEIPT", "OWNER_DECISION", ("P20_PLAN", "P20_RESULT")),
    ("OWNER_DECISION", "CLOSED", ("P23",)),
)

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

IDENTITY_FIELDS = ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch")


class ProvenanceError(ValueError):
    pass


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


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvenanceError(f"unreadable JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProvenanceError(f"JSON root must be an object: {path}")
    return value


def _require_string(value: Any, name: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value) < minimum:
        raise ProvenanceError(f"{name} must be a non-empty string")
    return value


def _require_hex(value: Any, name: str, size: int) -> str:
    text = _require_string(value, name, size)
    if len(text) != size or any(ch not in "0123456789abcdef" for ch in text):
        raise ProvenanceError(f"{name} must be exact lower-case {size}-hex")
    return text


def _strict_safety(value: Any, source: str) -> None:
    if not isinstance(value, Mapping):
        raise ProvenanceError(f"{source}: safety missing")
    for key, expected in SAFETY.items():
        if key in value and value.get(key) != expected:
            raise ProvenanceError(f"{source}: safety mismatch {key}={value.get(key)!r}")
    for key, expected in (("readOnly", True), ("ramWrites", 0), ("inputInjection", False)):
        if value.get(key) != expected:
            raise ProvenanceError(f"{source}: safety mismatch {key}={value.get(key)!r}")


def _normalize_root(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ProvenanceError("manifest sessionRoot missing")
    candidate = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
    identity = raw.get("identity") if isinstance(raw.get("identity"), Mapping) else {}
    root = {
        "sessionId": _require_string(raw.get("sessionId"), "sessionRoot.sessionId", 8),
        "p21SessionId": _require_string(raw.get("p21SessionId"), "sessionRoot.p21SessionId", 8),
        "p21RunToken": _require_string(raw.get("p21RunToken"), "sessionRoot.p21RunToken", 8),
        "candidate": {
            "sourceCommit": _require_hex(candidate.get("sourceCommit"), "candidate.sourceCommit", 40),
            "packageVersion": _require_string(candidate.get("packageVersion"), "candidate.packageVersion"),
            "candidateSha256": _require_hex(candidate.get("candidateSha256"), "candidate.candidateSha256", 64),
            "attestationSha256": _require_hex(candidate.get("attestationSha256"), "candidate.attestationSha256", 64),
        },
        "identity": {},
        "ackGeneration": raw.get("ackGeneration"),
        "p22RunId": _require_string(raw.get("p22RunId"), "sessionRoot.p22RunId", 8),
        "p24RunId": _require_string(raw.get("p24RunId"), "sessionRoot.p24RunId", 8),
    }
    for field in IDENTITY_FIELDS:
        minimum = 16 if field in ("runtimeEpoch", "rendererEpoch") else 1
        root["identity"][field] = _require_string(identity.get(field), f"identity.{field}", minimum)
    _require_hex(root["identity"]["worldSha256"], "identity.worldSha256", 64)
    generation = root["ackGeneration"]
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
        raise ProvenanceError("sessionRoot.ackGeneration must be an integer >= 1")
    if root["p22RunId"] != root["sessionId"]:
        raise ProvenanceError("P22 cross-run binding mismatch")
    if root["p24RunId"] != root["sessionId"]:
        raise ProvenanceError("P24 cross-run binding mismatch")
    return root


def _binding_core(root: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "sessionId": root["sessionId"],
        "p21SessionId": root["p21SessionId"],
        "p21RunToken": root["p21RunToken"],
        "sourceCommit": root["candidate"]["sourceCommit"],
        "packageVersion": root["candidate"]["packageVersion"],
        "candidateSha256": root["candidate"]["candidateSha256"],
        "worldSha256": root["identity"]["worldSha256"],
        "pageTargetId": root["identity"]["pageTargetId"],
        "authorityKey": root["identity"]["authorityKey"],
        "runtimeEpoch": root["identity"]["runtimeEpoch"],
        "rendererEpoch": root["identity"]["rendererEpoch"],
        "ackGeneration": root["ackGeneration"],
    }


def _validate_bindings(stage: str, bindings: Any, root: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(bindings, Mapping):
        raise ProvenanceError(f"{stage}: bindings missing")
    expected = _binding_core(root)
    required = set(expected)
    if stage == "P19":
        required = {"sourceCommit", "packageVersion", "candidateSha256"}
    elif stage == "P21":
        required = {"sessionId", "p21SessionId", "p21RunToken", "sourceCommit", "packageVersion", "candidateSha256", *IDENTITY_FIELDS}
    elif stage in {"W3", "P16"}:
        required = {"sessionId", "sourceCommit", "packageVersion", *IDENTITY_FIELDS}
    elif stage == "P18":
        required = {"sessionId", "sourceCommit", "packageVersion", *IDENTITY_FIELDS, "ackGeneration"}
    elif stage == "P22":
        required = {"sessionId", "p22RunId", "runtimeEpoch", "rendererEpoch", "worldSha256", "authorityKey", "pageTargetId"}
        expected = {**expected, "p22RunId": root["p22RunId"]}
    elif stage == "P24":
        required = {"sessionId", "p24RunId", "runtimeEpoch", "rendererEpoch", "worldSha256", "authorityKey", "pageTargetId", "ackGeneration"}
        expected = {**expected, "p24RunId": root["p24RunId"]}
    elif stage == "P17":
        required = {"sessionId", "sourceCommit", "packageVersion", "candidateSha256", *IDENTITY_FIELDS, "ackGeneration"}
    elif stage.startswith("P20_") or stage == "P23":
        required = {"sessionId", "sourceCommit", "packageVersion", "candidateSha256"}
    clean: dict[str, Any] = {}
    for key in sorted(required):
        if key not in bindings:
            raise ProvenanceError(f"{stage}: required binding missing: {key}")
        value = bindings.get(key)
        if key in expected and value != expected[key]:
            raise ProvenanceError(f"{stage}: binding mismatch {key}")
        clean[key] = value
    for key, value in bindings.items():
        if key not in clean:
            clean[key] = value
    return dict(sorted(clean.items()))


def _validate_artifact_semantics(stage: str, raw: Mapping[str, Any], bindings: Mapping[str, Any], root: Mapping[str, Any], byte_sha: str) -> None:
    schema = raw.get("schema")
    if stage == "P19":
        if raw.get("sourceCommit") != root["candidate"]["sourceCommit"] or raw.get("packageVersion") != root["candidate"]["packageVersion"]:
            raise ProvenanceError("P19 candidate identity mismatch")
        if byte_sha != root["candidate"]["candidateSha256"]:
            raise ProvenanceError("P19 candidate byte hash mismatch")
        _strict_safety(raw.get("safety"), "P19")
    elif stage == "P21":
        if schema != "wof-alpha-p21-prepromotion-staging-receipt-v1" or raw.get("version") != 1:
            raise ProvenanceError("P21 receipt schema/version mismatch")
        candidate = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
        for key, expected in (("sourceCommit", root["candidate"]["sourceCommit"]), ("packageVersion", root["candidate"]["packageVersion"]), ("candidateSha256", root["candidate"]["candidateSha256"])):
            if candidate.get(key) not in (None, expected):
                raise ProvenanceError(f"P21 candidate mismatch {key}")
        if raw.get("alphaLiveMoved") is not False or raw.get("ownerVisualAcceptance") != "NOT_RUN" or raw.get("realWofAcceptance") != "NOT_RUN":
            raise ProvenanceError("P21 safety/proof boundary mismatch")
        _strict_safety(raw.get("safety"), "P21")
    elif stage == "P16":
        if schema != "wof-alpha-canonical-owner-acceptance-evidence-v1" or raw.get("version") != 1:
            raise ProvenanceError("P16 schema/version mismatch")
        world = raw.get("world") if isinstance(raw.get("world"), Mapping) else {}
        runtime = raw.get("runtime") if isinstance(raw.get("runtime"), Mapping) else {}
        checks = {
            "worldSha256": world.get("sha256"), "pageTargetId": world.get("pageTargetId"),
            "authorityKey": runtime.get("authorityKey"), "runtimeEpoch": runtime.get("epoch"), "rendererEpoch": runtime.get("rendererEpoch"),
        }
        if world.get("accepted") is not True or any(checks[k] != root["identity"][k] for k in IDENTITY_FIELDS):
            raise ProvenanceError("P16 exact identity mismatch")
        if raw.get("visibleProof") != "NOT_PROVEN":
            raise ProvenanceError("P16 visibleProof boundary mismatch")
        _strict_safety(raw.get("safety"), "P16")
    elif stage == "P18":
        if schema != "wof-alpha-canonical-draw-evidence-v1" or raw.get("version") != 1:
            raise ProvenanceError("P18 schema/version mismatch")
        ident = raw.get("identity") if isinstance(raw.get("identity"), Mapping) else {}
        if any(ident.get(k) != root["identity"][k] for k in IDENTITY_FIELDS):
            raise ProvenanceError("P18 exact identity mismatch")
        if raw.get("evidenceGeneration") != root["ackGeneration"]:
            raise ProvenanceError("P18 evidence generation mismatch")
        rows = raw.get("acknowledgements") if isinstance(raw.get("acknowledgements"), list) else []
        previous = 0
        for row in rows:
            if not isinstance(row, Mapping) or row.get("evidenceGeneration") != root["ackGeneration"]:
                raise ProvenanceError("P18 acknowledgement generation mismatch")
            sequence = row.get("sequence")
            if not isinstance(sequence, int) or sequence <= previous:
                raise ProvenanceError("P18 acknowledgement sequence mismatch")
            previous = sequence
        if raw.get("visibleProof") != "NOT_PROVEN":
            raise ProvenanceError("P18 visibleProof boundary mismatch")
        _strict_safety(raw.get("safety"), "P18")
    elif stage == "W3":
        if schema != "wof-render-source-qualification-v1":
            raise ProvenanceError("W3 schema mismatch")
        ident = raw.get("captureIdentity") if isinstance(raw.get("captureIdentity"), Mapping) else {}
        for key in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch"):
            if ident.get(key) != root["identity"][key]:
                raise ProvenanceError(f"W3 identity mismatch {key}")
    elif stage == "P24":
        if schema not in {"wof-alpha-canonical-temporal-stability-evidence-v1", "wof-alpha-canonical-temporal-observation-bundle-v1"}:
            raise ProvenanceError("P24 schema mismatch")
        if bindings.get("ackGeneration") != root["ackGeneration"]:
            raise ProvenanceError("P24 ACK generation mismatch")
    elif stage == "P22":
        if schema != "wof-alpha-dynamic-actor-state-coverage-v1":
            raise ProvenanceError("P22 schema mismatch")
    elif stage == "P17":
        if schema != "wof-alpha-final-acceptance-bundle-v1":
            raise ProvenanceError("P17 schema mismatch")
        if raw.get("visibleProof") != "NOT_PROVEN":
            raise ProvenanceError("P17 visibleProof boundary mismatch")
    elif stage == "P20_RECEIPT":
        if schema != "wof-alpha-owner-visual-confirmation-receipt-v1":
            raise ProvenanceError("P20 receipt schema mismatch")
    elif stage == "P20_PLAN":
        if schema != "wof-alpha-live-promotion-plan-v1":
            raise ProvenanceError("P20 plan schema mismatch")
    elif stage == "P20_RESULT":
        if schema != "wof-alpha-live-promotion-result-v1":
            raise ProvenanceError("P20 result schema mismatch")
    elif stage == "P23":
        if schema not in {"wof-alpha-post-promotion-verification-v1", "wof-alpha-v1-final-close-bundle-v1", "wof-alpha-project-close-verification-v1"}:
            raise ProvenanceError("P23 close schema mismatch")


def _artifact_entry(stage: str, spec: Mapping[str, Any], root: Mapping[str, Any], base_dir: Path) -> dict[str, Any]:
    rel = _require_string(spec.get("path"), f"{stage}.path")
    path = Path(rel).expanduser()
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    if not path.is_file():
        raise ProvenanceError(f"{stage}: artifact missing: {path}")
    data = path.read_bytes()
    raw = _load_json(path)
    expected_schema = _require_string(spec.get("schema"), f"{stage}.schema")
    if raw.get("schema") != expected_schema:
        raise ProvenanceError(f"{stage}: declared schema disagrees with bytes")
    bindings = _validate_bindings(stage, spec.get("bindings"), root)
    byte_sha = sha256_bytes(data)
    _validate_artifact_semantics(stage, raw, bindings, root, byte_sha)
    semantic = {
        "stage": stage,
        "schema": expected_schema,
        "version": raw.get("version"),
        "semanticId": _require_string(spec.get("semanticId"), f"{stage}.semanticId"),
        "bindings": bindings,
    }
    return {
        "stage": stage,
        "sourceClass": _require_string(spec.get("sourceClass"), f"{stage}.sourceClass"),
        "path": str(path),
        "schema": expected_schema,
        "version": raw.get("version"),
        "byteSha256": byte_sha,
        "semanticId": semantic["semanticId"],
        "semanticSha256": sha256_bytes(canonical_bytes(semantic)),
        "bindings": bindings,
    }


def _ledger(manifest: Mapping[str, Any], root: Mapping[str, Any], base_dir: Path) -> list[dict[str, Any]]:
    specs = manifest.get("artifacts")
    if not isinstance(specs, list):
        raise ProvenanceError("manifest artifacts must be a list")
    by_stage: dict[str, dict[str, Any]] = {}
    semantic_ids: dict[str, tuple[str, str]] = {}
    paths: dict[str, tuple[str, str]] = {}
    for spec in specs:
        if not isinstance(spec, Mapping):
            raise ProvenanceError("artifact spec must be an object")
        stage = _require_string(spec.get("stage"), "artifact.stage")
        if stage not in STAGES:
            raise ProvenanceError(f"unsupported artifact stage: {stage}")
        entry = _artifact_entry(stage, spec, root, base_dir)
        if stage in by_stage:
            if by_stage[stage]["byteSha256"] != entry["byteSha256"]:
                raise ProvenanceError(f"{stage}: duplicate stage bytes disagree")
            raise ProvenanceError(f"{stage}: duplicate stage artifact is forbidden")
        prior = paths.get(entry["path"])
        if prior is not None:
            raise ProvenanceError(f"artifact path re-entry is forbidden: {entry['path']} already belongs to {prior[0]}")
        paths[entry["path"]] = (stage, entry["byteSha256"])
        semantic_id = entry["semanticId"]
        semantic_key = entry["semanticSha256"]
        if semantic_id in semantic_ids and semantic_ids[semantic_id] != (stage, semantic_key):
            raise ProvenanceError(f"semantic identity conflict: {semantic_id}")
        semantic_ids[semantic_id] = (stage, semantic_key)
        by_stage[stage] = entry
    missing = [stage for stage in STAGES if stage not in by_stage]
    if missing:
        raise ProvenanceError(f"missing required artifacts: {', '.join(missing)}")
    return [by_stage[stage] for stage in STAGES]


def _stage_hashes(ledger: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    return {str(entry["stage"]): str(entry["byteSha256"]) for entry in ledger}


def _validate_dependencies(manifest: Mapping[str, Any], ledger: Sequence[Mapping[str, Any]], root: Mapping[str, Any]) -> dict[str, Any]:
    deps = manifest.get("dependencies")
    if not isinstance(deps, Mapping):
        raise ProvenanceError("manifest dependencies missing")
    hashes = _stage_hashes(ledger)
    p17 = deps.get("p17") if isinstance(deps.get("p17"), Mapping) else {}
    expected_p17 = {stage: hashes[stage] for stage in ("P19", "P21", "W3", "P16", "P18", "P22", "P24")}
    if p17.get("artifactHashes") != expected_p17:
        raise ProvenanceError("P17 dependency hash mismatch")
    p17_hash = hashes["P17"]
    receipt = deps.get("p20Receipt") if isinstance(deps.get("p20Receipt"), Mapping) else {}
    if receipt.get("p17Sha256") != p17_hash or receipt.get("sessionId") != root["sessionId"]:
        raise ProvenanceError("P20 receipt binding mismatch")
    plan = deps.get("p20Plan") if isinstance(deps.get("p20Plan"), Mapping) else {}
    if plan.get("receiptSha256") != hashes["P20_RECEIPT"] or plan.get("p17Sha256") != p17_hash or plan.get("sessionId") != root["sessionId"]:
        raise ProvenanceError("P20 plan binding mismatch")
    result = deps.get("p20Result") if isinstance(deps.get("p20Result"), Mapping) else {}
    if result.get("planSha256") != hashes["P20_PLAN"] or result.get("receiptSha256") != hashes["P20_RECEIPT"] or result.get("sessionId") != root["sessionId"]:
        raise ProvenanceError("P20 result binding mismatch")
    p23 = deps.get("p23") if isinstance(deps.get("p23"), Mapping) else {}
    if p23.get("promotionResultSha256") != hashes["P20_RESULT"] or p23.get("promotedSessionId") != root["sessionId"]:
        raise ProvenanceError("P23 promoted-session binding mismatch")
    return {
        "p17ArtifactHashes": expected_p17,
        "p20ReceiptP17Sha256": p17_hash,
        "p20PlanReceiptSha256": hashes["P20_RECEIPT"],
        "p20ResultPlanSha256": hashes["P20_PLAN"],
        "p23PromotionResultSha256": hashes["P20_RESULT"],
    }


def _transition_log(ledger: Sequence[Mapping[str, Any]], root: Mapping[str, Any]) -> list[dict[str, Any]]:
    hashes = _stage_hashes(ledger)
    epoch_binding = {
        "runtimeEpoch": root["identity"]["runtimeEpoch"],
        "rendererEpoch": root["identity"]["rendererEpoch"],
        "ackGeneration": root["ackGeneration"],
    }
    out: list[dict[str, Any]] = []
    for previous, current, evidence_stages in TRANSITIONS:
        evidence = {stage: hashes[stage] for stage in evidence_stages}
        core = {"from": previous, "to": current, "evidence": evidence, "epochBinding": epoch_binding}
        out.append({**core, "transitionSha256": sha256_bytes(canonical_bytes(core))})
    return out


def _digest_core(session: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": session["schema"],
        "version": session["version"],
        "terminal": session["terminal"],
        "state": session["state"],
        "sessionRoot": session["sessionRoot"],
        "artifactLedger": session["artifactLedger"],
        "dependencies": session["dependencies"],
        "epochTransitions": session["epochTransitions"],
        "safety": session["safety"],
    }


def build_session(manifest: Mapping[str, Any], *, manifest_dir: Path) -> dict[str, Any]:
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("version") != VERSION:
        raise ProvenanceError("manifest schema/version mismatch")
    _strict_safety(manifest.get("safety"), "manifest")
    root = _normalize_root(manifest.get("sessionRoot"))
    ledger = _ledger(manifest, root, manifest_dir)
    dependencies = _validate_dependencies(manifest, ledger, root)
    session: dict[str, Any] = {
        "schema": SESSION_SCHEMA,
        "version": VERSION,
        "terminal": True,
        "state": "CLOSED",
        "sessionRoot": root,
        "artifactLedger": ledger,
        "dependencies": dependencies,
        "epochTransitions": _transition_log(ledger, root),
        "safety": dict(SAFETY),
    }
    session["chainDigest"] = sha256_bytes(canonical_bytes(_digest_core(session)))
    return session


def _fsync_parent(path: Path) -> None:
    if not hasattr(os, "fsync"):
        return
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


def atomic_persist(path: Path, payload: Mapping[str, Any], *, refuse_existing_terminal: bool = True) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = _load_json(path)
        if refuse_existing_terminal and existing.get("terminal") is True:
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
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass


def create_from_manifest(manifest_path: Path, output_path: Path) -> dict[str, Any]:
    manifest_path = manifest_path.expanduser().resolve()
    manifest = _load_json(manifest_path)
    session = build_session(manifest, manifest_dir=manifest_path.parent)
    atomic_persist(output_path, session, refuse_existing_terminal=True)
    return session


def verify_session(path: Path) -> dict[str, Any]:
    path = path.expanduser().resolve()
    session = _load_json(path)
    if session.get("schema") != SESSION_SCHEMA or session.get("version") != VERSION:
        raise ProvenanceError("session schema/version mismatch")
    if session.get("terminal") is not True or session.get("state") != "CLOSED":
        raise ProvenanceError("only terminal CLOSED sessions are verifiable")
    _strict_safety(session.get("safety"), "session")
    root = _normalize_root(session.get("sessionRoot"))
    ledger = session.get("artifactLedger")
    if not isinstance(ledger, list) or [entry.get("stage") for entry in ledger if isinstance(entry, Mapping)] != list(STAGES):
        raise ProvenanceError("artifact ledger order/stage set mismatch")
    seen_semantic: dict[str, str] = {}
    seen_path: dict[str, str] = {}
    for entry in ledger:
        if not isinstance(entry, Mapping):
            raise ProvenanceError("artifact ledger row malformed")
        stage = str(entry.get("stage"))
        path_value = _require_string(entry.get("path"), f"{stage}.path")
        artifact_path = Path(path_value)
        if not artifact_path.is_file():
            raise ProvenanceError(f"{stage}: persisted artifact missing: {artifact_path}")
        byte_sha = sha256_file(artifact_path)
        if byte_sha != entry.get("byteSha256"):
            raise ProvenanceError(f"{stage}: persisted artifact byte hash mismatch")
        raw = _load_json(artifact_path)
        if raw.get("schema") != entry.get("schema"):
            raise ProvenanceError(f"{stage}: persisted artifact schema mismatch")
        bindings = _validate_bindings(stage, entry.get("bindings"), root)
        semantic = {"stage": stage, "schema": entry.get("schema"), "version": raw.get("version"), "semanticId": entry.get("semanticId"), "bindings": bindings}
        if sha256_bytes(canonical_bytes(semantic)) != entry.get("semanticSha256"):
            raise ProvenanceError(f"{stage}: semantic hash mismatch")
        _validate_artifact_semantics(stage, raw, bindings, root, byte_sha)
        prior_path = seen_path.get(path_value)
        if prior_path is not None and prior_path != byte_sha:
            raise ProvenanceError(f"persisted path conflict: {path_value}")
        seen_path[path_value] = byte_sha
        semantic_id = _require_string(entry.get("semanticId"), f"{stage}.semanticId")
        prior_semantic = seen_semantic.get(semantic_id)
        if prior_semantic is not None and prior_semantic != entry.get("semanticSha256"):
            raise ProvenanceError(f"persisted semantic identity conflict: {semantic_id}")
        seen_semantic[semantic_id] = str(entry.get("semanticSha256"))
    hashes = _stage_hashes(ledger)
    stored = session.get("dependencies") if isinstance(session.get("dependencies"), Mapping) else {}
    expected_stored = {
        "p17ArtifactHashes": {stage: hashes[stage] for stage in ("P19", "P21", "W3", "P16", "P18", "P22", "P24")},
        "p20ReceiptP17Sha256": hashes["P17"],
        "p20PlanReceiptSha256": hashes["P20_RECEIPT"],
        "p20ResultPlanSha256": hashes["P20_PLAN"],
        "p23PromotionResultSha256": hashes["P20_RESULT"],
    }
    if dict(stored) != expected_stored:
        raise ProvenanceError("persisted dependency summary mismatch")
    expected_transitions = _transition_log(ledger, root)
    if session.get("epochTransitions") != expected_transitions:
        raise ProvenanceError("persisted epoch transition mismatch")
    expected_digest = sha256_bytes(canonical_bytes(_digest_core(session)))
    if session.get("chainDigest") != expected_digest:
        raise ProvenanceError("chain digest mismatch")
    return {
        "state": "VERIFIED",
        "sessionId": root["sessionId"],
        "artifactCount": len(ledger),
        "chainDigest": expected_digest,
        "terminal": True,
        "visibleProof": "NOT_PROVEN",
        "realWofAcceptance": "NOT_RUN",
        "ownerVisualAcceptance": "NOT_RUN",
        "alphaLiveMoved": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build or verify an immutable Alpha V1 Owner acceptance provenance session.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Create one terminal immutable provenance session from a manifest and exact artifact bytes.")
    build.add_argument("--manifest", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)
    verify = sub.add_parser("verify", help="Verify-only reload; never mutates the session or source artifacts.")
    verify.add_argument("--session", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "build":
            value = create_from_manifest(args.manifest, args.output)
            print(json.dumps({"state": value["state"], "sessionId": value["sessionRoot"]["sessionId"], "chainDigest": value["chainDigest"]}, sort_keys=True))
        else:
            print(json.dumps(verify_session(args.session), sort_keys=True))
        return 0
    except ProvenanceError as exc:
        print(f"PROVENANCE_ERROR: {exc}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
