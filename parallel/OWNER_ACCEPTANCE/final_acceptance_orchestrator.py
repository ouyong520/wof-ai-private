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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def default_results_dir() -> Path:
    return Path.home() / "Documents" / "WOF_RESULTS"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvidenceError(f"JSON root must be an object: {path}")
    return value


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safety(value: Any, source: str) -> None:
    if not isinstance(value, Mapping):
        raise EvidenceError(f"{source}: safety missing")
    for key, expected in (("readOnly", True), ("ramWrites", 0), ("inputInjection", False)):
        if value.get(key) != expected:
            raise EvidenceError(f"{source}: safety mismatch {key}={value.get(key)!r}")
    for key in ("screenshotProductionCoordinates", "worldProjectionProductionCoordinates", "guessedAddresses"):
        if key in value and value.get(key) is not False:
            raise EvidenceError(f"{source}: forbidden safety flag {key}")


def read_candidate_metadata(repo_root: Path, explicit: Path | None = None) -> dict[str, Any]:
    path = (explicit or repo_root / DEFAULT_CANDIDATE_REL).expanduser().resolve()
    if not path.is_file():
        raise EvidenceError(f"candidate metadata missing: {path}")
    raw = _load(path)
    if raw.get("schema") != "wof-owner-oneclick-package-v1":
        raise EvidenceError("candidate metadata schema mismatch")
    if not isinstance(raw.get("packageVersion"), str) or not raw["packageVersion"]:
        raise EvidenceError("candidate packageVersion missing")
    if not isinstance(raw.get("sourceCommit"), str) or len(raw["sourceCommit"]) < 12:
        raise EvidenceError("candidate sourceCommit missing")
    _safety(raw.get("safety"), "candidate")
    convergence = ((raw.get("components") or {}).get("canonicalProductConvergence") or {})
    if convergence and convergence.get("alphaLivePromoted") is not False:
        raise EvidenceError("candidate unexpectedly reports alpha-live promotion")
    return {
        "sourcePath": str(path),
        "contentSha256": _sha256(path),
        "schema": raw.get("schema"),
        "packageVersion": raw.get("packageVersion"),
        "sourceCommit": raw.get("sourceCommit"),
        "selectionPolicy": raw.get("selectionPolicy"),
        "canonicalProductConvergence": {
            "stageId": convergence.get("stageId"),
            "initialState": convergence.get("initialState"),
            "legacySpatialFallback": convergence.get("legacySpatialFallback"),
            "alphaLivePromoted": convergence.get("alphaLivePromoted"),
        },
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
    }


def _resolve_w3(path: Path) -> tuple[Path, dict[str, Any]]:
    path = path.expanduser().resolve()
    raw = _load(path)
    if raw.get("schema") == "wof-w3-long-qualification-latest-v1":
        q = raw.get("qualificationJson")
        if not isinstance(q, str) or not q:
            raise EvidenceError("W3 latest pointer qualificationJson missing")
        qpath = Path(q).expanduser()
        path = qpath if qpath.is_absolute() else (path.parent / qpath).resolve()
        raw = _load(path)
    if raw.get("schema") != W3_SCHEMA:
        raise EvidenceError("W3 qualification schema mismatch")
    return path, raw


def read_w3_qualification(path: Path) -> dict[str, Any]:
    path, raw = _resolve_w3(path)
    status = raw.get("status")
    if status not in {"PASS", "INCONCLUSIVE", "REJECTED"}:
        raise EvidenceError(f"W3 qualification status invalid: {status!r}")
    ready = raw.get("canonicalProducerReadiness")
    if status == "PASS":
        source = ready.get("rendererSource") if isinstance(ready, Mapping) else None
        if not isinstance(ready, Mapping) or ready.get("ready") is not True or not isinstance(source, Mapping) or source.get("proven") is not True:
            raise EvidenceError("W3 PASS lacks explicit ready/proven renderer source")
    ident = raw.get("captureIdentity") if isinstance(raw.get("captureIdentity"), Mapping) else {}
    return {
        "sourcePath": str(path),
        "schema": raw.get("schema"),
        "status": status,
        "repoQualificationPolicy": raw.get("repoQualificationPolicy"),
        "identity": {k: ident.get(k) for k in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch")},
        "blockingProofEdge": raw.get("blockingProofEdge"),
        "ownerAction": raw.get("ownerAction"),
        "canonicalProducerReadiness": ready,
    }


def invoke_w3(repo_root: Path, output_root: Path) -> Path:
    runner = (repo_root / DEFAULT_W3_RUNNER_REL).resolve()
    if not runner.is_file():
        raise EvidenceError(f"W3 runner missing: {runner}")
    output_root = output_root.expanduser().resolve()
    cmd = [sys.executable, str(runner), "--root", str(repo_root.resolve()), "--output-root", str(output_root)]
    rc = subprocess.run(cmd, cwd=repo_root, check=False).returncode
    if rc:
        raise EvidenceError(f"W3 bounded qualification failed with exit code {rc}")
    latest = output_root / "LATEST_W3_RENDER_SOURCE_QUALIFICATION.json"
    if not latest.is_file():
        raise EvidenceError(f"W3 latest qualification pointer missing: {latest}")
    return latest


def read_p16(path: Path) -> dict[str, Any]:
    path = path.expanduser().resolve()
    raw = _load(path)
    if raw.get("schema") != P16_SCHEMA or raw.get("version") != 1:
        raise EvidenceError("P16 schema/version mismatch")
    if raw.get("visibleProof") != "NOT_PROVEN":
        raise EvidenceError("P16 visibleProof must be NOT_PROVEN")
    _safety(raw.get("safety"), "P16")
    world = raw.get("world") if isinstance(raw.get("world"), Mapping) else {}
    runtime = raw.get("runtime") if isinstance(raw.get("runtime"), Mapping) else {}
    canonical = raw.get("canonical") if isinstance(raw.get("canonical"), Mapping) else {}
    if world.get("accepted") is not True:
        raise EvidenceError("P16 exact World is not accepted")
    for k in ("sha256", "pageTargetId", "workerTargetId"):
        if not isinstance(world.get(k), str) or not world.get(k):
            raise EvidenceError(f"P16 world identity missing: {k}")
    for k in ("epoch", "authorityKey", "rendererEpoch"):
        if not isinstance(runtime.get(k), str) or not runtime.get(k):
            raise EvidenceError(f"P16 runtime identity missing: {k}")
    return {
        "sourcePath": str(path),
        "schema": raw.get("schema"),
        "generatedAtUtc": raw.get("generatedAtUtc"),
        "packageVersion": raw.get("packageVersion"),
        "canonicalState": canonical.get("state"),
        "canonicalReason": canonical.get("reason"),
        "hudCanonicalStatus": raw.get("hudCanonicalStatus"),
        "identity": {
            "worldSha256": world.get("sha256"),
            "pageTargetId": world.get("pageTargetId"),
            "workerTargetId": world.get("workerTargetId"),
            "authorityKey": runtime.get("authorityKey"),
            "runtimeEpoch": runtime.get("epoch"),
            "rendererEpoch": runtime.get("rendererEpoch"),
            "rendererAuthority": runtime.get("rendererAuthority"),
        },
        "visibleProof": "NOT_PROVEN",
    }


def read_p18(path: Path) -> dict[str, Any]:
    path = path.expanduser().resolve()
    raw = _load(path)
    if raw.get("schema") != DRAW_SCHEMA or raw.get("version") != 1:
        raise EvidenceError("P18 draw evidence schema/version mismatch")
    if raw.get("visibleProof") != "NOT_PROVEN":
        raise EvidenceError("P18 visibleProof must be NOT_PROVEN")
    _safety(raw.get("safety"), "P18")
    state = raw.get("evidenceState") or raw.get("state")
    if state not in {"NO_CANONICAL_DRAW", "CANONICAL_DRAW_ACKNOWLEDGED", "STALE_OR_MISMATCH", "HUD_API_MISSING"}:
        raise EvidenceError(f"P18 evidence state invalid: {state!r}")
    entries = raw.get("entries") or raw.get("acknowledgements") or []
    if not isinstance(entries, list) or len(entries) > 256:
        raise EvidenceError("P18 acknowledgement rows malformed or unbounded")
    ident = raw.get("identity") if isinstance(raw.get("identity"), Mapping) else {}
    runtime = raw.get("runtime") if isinstance(raw.get("runtime"), Mapping) else {}
    page = raw.get("pageTarget") if isinstance(raw.get("pageTarget"), Mapping) else {}
    identity = {
        "worldSha256": ident.get("worldSha256") or raw.get("worldSha256"),
        "pageTargetId": ident.get("pageTargetId") or page.get("id") or raw.get("pageTargetId"),
        "authorityKey": ident.get("authorityKey") or runtime.get("authorityKey") or raw.get("authorityKey"),
        "runtimeEpoch": ident.get("runtimeEpoch") or runtime.get("epoch") or raw.get("runtimeEpoch"),
        "rendererEpoch": ident.get("rendererEpoch") or runtime.get("rendererEpoch") or raw.get("rendererEpoch"),
        "rendererAuthority": ident.get("rendererAuthority") or runtime.get("rendererAuthority") or raw.get("rendererAuthority"),
    }
    return {
        "sourcePath": str(path),
        "schema": raw.get("schema"),
        "collectedAtUtc": raw.get("collectedAtUtc") or raw.get("collectedAt"),
        "packageVersion": raw.get("packageVersion"),
        "sourceCommit": raw.get("sourceCommit"),
        "evidenceState": state,
        "identity": identity,
        "entries": entries,
        "visibleProof": "NOT_PROVEN",
    }


def _identity_mismatches(candidate: Mapping[str, Any], summaries: list[tuple[str, Mapping[str, Any]]]) -> list[str]:
    out: list[str] = []
    fields = ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch", "rendererAuthority")
    seen: dict[str, tuple[str, Any]] = {}
    for name, summary in summaries:
        for field in fields:
            value = summary.get(field)
            if value in (None, ""):
                continue
            if field in seen and seen[field][1] != value:
                out.append(f"{field} mismatch: {seen[field][0]}={seen[field][1]!r}, {name}={value!r}")
            else:
                seen[field] = (name, value)
        p = summary.get("packageVersion")
        if p and candidate.get("packageVersion") and p != candidate.get("packageVersion"):
            out.append(f"packageVersion mismatch: candidate={candidate.get('packageVersion')!r}, {name}={p!r}")
        c = summary.get("sourceCommit")
        if c and candidate.get("sourceCommit") and c != candidate.get("sourceCommit"):
            out.append(f"sourceCommit mismatch: candidate={candidate.get('sourceCommit')!r}, {name}={c!r}")
    return sorted(set(out))


@dataclass(frozen=True)
class Inputs:
    candidate: dict[str, Any] | None
    w3: dict[str, Any] | None
    p16: dict[str, Any] | None
    p18: dict[str, Any] | None
    errors: tuple[str, ...] = ()


def _consistency(inputs: Inputs) -> list[str]:
    if not inputs.candidate:
        return []
    sources = []
    for name, item in (("W3", inputs.w3), ("P16", inputs.p16), ("P18", inputs.p18)):
        if item:
            sources.append((name, {**(item.get("identity") or {}), "packageVersion": item.get("packageVersion"), "sourceCommit": item.get("sourceCommit")}))
    return _identity_mismatches(inputs.candidate, sources)


def decide(inputs: Inputs) -> tuple[str, list[str]]:
    if inputs.errors or inputs.candidate is None:
        return FAILED_EVIDENCE_MISMATCH, list(inputs.errors) or ["candidate metadata unavailable"]
    if inputs.w3 is None:
        return WAITING_W3_QUALIFICATION, ["W3 qualification evidence is not available"]
    if inputs.w3.get("status") == "INCONCLUSIVE":
        return W3_INCONCLUSIVE, ["W3 renderer/object causal proof is inconclusive"]
    if inputs.w3.get("status") != "PASS":
        return FAILED_EVIDENCE_MISMATCH, [f"W3 qualification rejected: {inputs.w3.get('status')}"]
    if inputs.p16 is None:
        return WAITING_CANONICAL_RUNTIME_EVIDENCE, ["P16 canonical runtime evidence is not available"]
    if inputs.p16.get("canonicalState") != "HUD_INGEST_ACCEPTED":
        return CANONICAL_RUNTIME_SUPPRESSED, [f"P16 canonical runtime state is {inputs.p16.get('canonicalState')!r}"]
    mismatch = _consistency(Inputs(inputs.candidate, inputs.w3, inputs.p16, None))
    if mismatch:
        return FAILED_EVIDENCE_MISMATCH, mismatch
    if inputs.p18 is None:
        return WAITING_DRAW_EVIDENCE, ["P18 maintained draw evidence is not available"]
    if inputs.p18.get("evidenceState") == "STALE_OR_MISMATCH":
        return FAILED_EVIDENCE_MISMATCH, ["P18 explicitly reports stale or mismatched evidence"]
    if inputs.p18.get("evidenceState") != "CANONICAL_DRAW_ACKNOWLEDGED":
        return WAITING_DRAW_EVIDENCE, [f"P18 draw evidence state is {inputs.p18.get('evidenceState')!r}"]
    mismatch = _consistency(inputs)
    if mismatch:
        return FAILED_EVIDENCE_MISMATCH, mismatch
    return READY_FOR_OWNER_VISUAL_CONFIRMATION, [
        "W3 renderer/object source qualification explicitly passed",
        "P16 canonical runtime reached HUD_INGEST_ACCEPTED",
        "P18 maintained draw primitive acknowledgement is present",
        "Owner screen confirmation is still required",
    ]


def build_bundle(inputs: Inputs, *, generated_at_utc: str | None = None) -> dict[str, Any]:
    decision, reasons = decide(inputs)
    mismatches = _consistency(inputs)
    return {
        "schema": BUNDLE_SCHEMA,
        "version": 1,
        "generatedAtUtc": generated_at_utc or _now(),
        "candidate": inputs.candidate,
        "w3Qualification": inputs.w3,
        "p16CanonicalRuntime": inputs.p16,
        "p18DrawEvidence": inputs.p18,
        "identityConsistency": {"consistent": not mismatches, "mismatches": mismatches},
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "screenshotProductionCoordinates": False,
            "worldProjectionProductionCoordinates": False,
            "guessedRendererObjectAddress": False,
            "alphaLiveMoved": False,
        },
        "automaticDecision": decision,
        "decisionReasons": reasons,
        "visibleProof": "NOT_PROVEN",
        "ownerVisualConfirmationRequired": True,
    }


def render_markdown(bundle: Mapping[str, Any]) -> str:
    c, w, p, d = (bundle.get(k) or {} for k in ("candidate", "w3Qualification", "p16CanonicalRuntime", "p18DrawEvidence"))
    lines = [
        "# Alpha Final Acceptance Bundle", "",
        f"- Generated: `{bundle.get('generatedAtUtc')}`",
        f"- Automatic decision: **{bundle.get('automaticDecision')}**",
        f"- Visible proof: **{bundle.get('visibleProof')}**",
        f"- Candidate: `{c.get('packageVersion') or 'N/A'}` @ `{c.get('sourceCommit') or 'N/A'}`",
        f"- W3: `{w.get('status') or 'MISSING'}`",
        f"- P16 canonical runtime: `{p.get('canonicalState') or 'MISSING'}`",
        f"- P18 draw evidence: `{d.get('evidenceState') or 'MISSING'}`", "", "## Decision reasons", "",
    ]
    lines.extend(f"- {x}" for x in bundle.get("decisionReasons") or [])
    lines.extend(["", "## Owner gate", "", "Automatic evidence never emits final PASS. READY_FOR_OWNER_VISUAL_CONFIRMATION still requires the Owner to confirm the overlay follows the intended actors on screen.", ""])
    return "\n".join(lines)


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def write_bundle(bundle: Mapping[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir = output_dir.expanduser().resolve()
    jp, mp = output_dir / BUNDLE_JSON_NAME, output_dir / BUNDLE_MD_NAME
    _atomic_write(jp, (json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
    _atomic_write(mp, render_markdown(bundle).encode())
    return jp, mp


def collect_inputs(*, repo_root: Path, candidate_path: Path | None, w3_path: Path | None, p16_path: Path, p18_path: Path) -> Inputs:
    errors: list[str] = []
    candidate = w3 = p16 = p18 = None
    for name, exists, reader in (
        ("candidate", True, lambda: read_candidate_metadata(repo_root, candidate_path)),
        ("W3", w3_path is not None, lambda: read_w3_qualification(w3_path)),
        ("P16", p16_path.is_file(), lambda: read_p16(p16_path)),
        ("P18", p18_path.is_file(), lambda: read_p18(p18_path)),
    ):
        if not exists:
            continue
        try:
            value = reader()
            if name == "candidate": candidate = value
            elif name == "W3": w3 = value
            elif name == "P16": p16 = value
            else: p18 = value
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{name}: {exc}")
    return Inputs(candidate, w3, p16, p18, tuple(errors))


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve()
    parser = argparse.ArgumentParser(description="Alpha V1 bounded final Owner acceptance orchestrator")
    parser.add_argument("--repo-root", type=Path, default=here.parents[2])
    parser.add_argument("--output-dir", type=Path, default=default_results_dir())
    parser.add_argument("--candidate-metadata", type=Path)
    parser.add_argument("--w3-qualification", type=Path)
    parser.add_argument("--invoke-w3", action="store_true")
    parser.add_argument("--w3-output-root", type=Path)
    parser.add_argument("--p16-evidence", type=Path)
    parser.add_argument("--p18-evidence", type=Path)
    args = parser.parse_args(argv)
    if args.invoke_w3 and args.w3_qualification:
        parser.error("--invoke-w3 and --w3-qualification are mutually exclusive")
    repo, out = args.repo_root.expanduser().resolve(), args.output_dir.expanduser().resolve()
    w3_path, errors = args.w3_qualification, []
    if args.invoke_w3:
        try:
            root = args.w3_output_root or Path(os.environ.get("LOCALAPPDATA", str(out))) / "WOF_ALPHA_RENDER_AUTHORITY"
            w3_path = invoke_w3(repo, root)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    inputs = collect_inputs(
        repo_root=repo,
        candidate_path=args.candidate_metadata,
        w3_path=w3_path,
        p16_path=(args.p16_evidence or default_results_dir() / P16_NAME).expanduser().resolve(),
        p18_path=(args.p18_evidence or default_results_dir() / P18_NAME).expanduser().resolve(),
    )
    if errors:
        inputs = Inputs(inputs.candidate, inputs.w3, inputs.p16, inputs.p18, inputs.errors + tuple(errors))
    bundle = build_bundle(inputs)
    jp, mp = write_bundle(bundle, out)
    print(f"decision={bundle['automaticDecision']}")
    print(f"visibleProof={bundle['visibleProof']}")
    print(f"bundleJson={jp}")
    print(f"bundleMarkdown={mp}")
    if bundle["automaticDecision"] == READY_FOR_OWNER_VISUAL_CONFIRMATION:
        print("请保持 WOF 正常游玩，并在屏幕上确认提示是否稳定跟随正确人物；自动证据不会替你判定最终 PASS。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
