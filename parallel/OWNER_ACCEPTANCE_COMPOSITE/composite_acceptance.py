from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import secrets
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

RUN_SCHEMA = "wof-alpha-p25-final-acceptance-composite-run-v1"
INDEX_SCHEMA = "wof-alpha-p25-final-acceptance-composite-index-v1"
STATUS_RING_SCHEMA = "wof-alpha-p25-runtime-status-ring-v1"
CANONICAL_SCHEMA = "wof-alpha-canonical-runtime-coordinator-v1"
P24_OBSERVATION_SCHEMA = "wof-alpha-canonical-temporal-observation-v1"
P24_BUNDLE_SCHEMA = "wof-alpha-canonical-temporal-observation-bundle-v1"
WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
RUN_JSON = "ALPHA_FINAL_ACCEPTANCE_COMPOSITE_RUN.json"
INDEX_JSON = "ALPHA_FINAL_ACCEPTANCE_COMPOSITE_INDEX.json"
INDEX_MD = "ALPHA_FINAL_ACCEPTANCE_COMPOSITE_INDEX.md"
STATUS_RING = "P25_RUNTIME_STATUS_RING.json"
MAX_TEMPORAL_OBSERVATIONS = 4096
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False,
          "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False,
          "guessedAddresses": False, "alphaLiveMoved": False}


class CompositeError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(data)
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(ch in "0123456789abcdef" for ch in value.lower())


def normalize_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    source, package = candidate.get("sourceCommit"), candidate.get("packageVersion")
    candidate_sha = candidate.get("candidateSha256") or candidate.get("contentSha256")
    attestation_sha = candidate.get("attestationSha256")
    if not _is_sha(source) or not isinstance(package, str) or not package:
        raise CompositeError("exact P19 candidate identity missing/invalid")
    if any(not isinstance(v, str) or len(v) != 64 for v in (candidate_sha, attestation_sha)):
        raise CompositeError("exact P19 candidate/attestation SHA-256 missing/invalid")
    return {"sourceCommit": source.lower(), "packageVersion": package,
            "candidateSha256": candidate_sha.lower(), "attestationSha256": attestation_sha.lower()}


def new_run_record(candidate: Mapping[str, Any], *, run_nonce: str | None = None) -> dict[str, Any]:
    nonce = run_nonce or secrets.token_hex(24)
    if not isinstance(nonce, str) or len(nonce) < 32:
        raise CompositeError("run nonce must represent at least 128 bits")
    return {"schema": RUN_SCHEMA, "version": 1, "runNonce": nonce, "startedAtUtc": utc_now(), "endedAtUtc": None,
            "candidate": normalize_candidate(candidate), "p21": {"runId": None, "receiptSha256": None},
            "observedAuthority": None, "identityTransitions": [],
            "canonicalFeed": {"state": "UNOBSERVED", "schema": CANONICAL_SCHEMA},
            "capture": {"statusSnapshotsSeen": 0, "canonicalCyclesAccepted": 0, "duplicateSnapshotsRejected": 0,
                        "outOfOrderSnapshotsRejected": 0, "malformedSnapshotsRejected": 0,
                        "temporalObservationCount": 0, "statusRingTruncated": False},
            "evidence": {}, "state": "CAPTURING", "reason": None, "realWofAcceptance": "NOT_RUN",
            "ownerVisualAcceptance": "NOT_RUN", "visibleProof": "NOT_PROVEN", "alphaLiveMoved": False,
            "safety": dict(SAFETY)}


def _canonical_candidates(entry: Mapping[str, Any]) -> list[Any]:
    snap = entry.get("snapshot") if isinstance(entry.get("snapshot"), Mapping) else entry
    payload = entry.get("payload") if isinstance(entry.get("payload"), Mapping) else {}
    out: list[Any] = [snap, payload]
    roots = [snap.get("alpha_status") if isinstance(snap, Mapping) else None,
             snap.get("alphaStatus") if isinstance(snap, Mapping) else None,
             payload.get("alphaStatus"), payload.get("alpha_status")]
    for root in roots:
        if isinstance(root, Mapping):
            out.extend([root, root.get("canonicalOverlay"), root.get("canonicalRuntime"), root.get("canonicalCoordinator")])
    out.extend([payload.get("canonicalOverlay"), payload.get("canonicalRuntime"), payload.get("canonicalCoordinator")])
    return out


def extract_canonical_status(entry: Mapping[str, Any]) -> dict[str, Any] | None:
    for value in _canonical_candidates(entry):
        if isinstance(value, Mapping) and value.get("schema") == CANONICAL_SCHEMA:
            return json.loads(json.dumps(value))
    return None


def _safe_canonical(status: Mapping[str, Any]) -> None:
    if status.get("readOnly") is not True or status.get("ramWrites") != 0 or status.get("inputInjection") is not False:
        raise CompositeError("canonical status violates read-only safety boundary")
    if status.get("legacySpatialFallback") is not False or status.get("worldSha256") != WORLD_SHA256:
        raise CompositeError("canonical status authority mismatch")


def identity_of(status: Mapping[str, Any]) -> dict[str, str]:
    keys = ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch")
    values = {k: status.get(k) for k in keys}
    if any(not isinstance(v, str) or not v for v in values.values()):
        raise CompositeError("canonical exact identity incomplete")
    return {k: str(v) for k, v in values.items()}


def _payload(status: Mapping[str, Any]) -> Mapping[str, Any] | None:
    bridge = status.get("bridge")
    value = bridge.get("lastPayload") if isinstance(bridge, Mapping) else None
    return value if isinstance(value, Mapping) else None


def _payload_order(payload: Mapping[str, Any]) -> tuple[int | None, tuple[float, ...]]:
    seq = payload.get("sequence") if isinstance(payload.get("sequence"), int) else None
    samples = tuple(float(r["sampleAt"]) for r in payload.get("records") or []
                    if isinstance(r, Mapping) and isinstance(r.get("sampleAt"), (int, float)) and math.isfinite(float(r["sampleAt"])))
    return seq, samples


def _geometry(anchor: Mapping[str, Any]) -> dict[str, Any]:
    point, bounds = anchor.get("anchor"), anchor.get("bodyBounds")
    if not isinstance(point, Mapping) or not isinstance(bounds, Mapping):
        raise CompositeError("READY P10 anchor missing canonical geometry")
    return {"coordinateAuthority": "canonical-render-object-only", "nativeWidth": anchor.get("nativeWidth"),
            "nativeHeight": anchor.get("nativeHeight"), "anchor": dict(point), "bodyBounds": dict(bounds)}


def temporal_observations_from_status(status: Mapping[str, Any], *, first_sample_seq: int) -> list[dict[str, Any]]:
    _safe_canonical(status); ident = identity_of(status); payload = _payload(status)
    if payload is None:
        return []
    rows = payload.get("records")
    if not isinstance(rows, list):
        raise CompositeError("P10 records malformed")
    transport_seq = payload.get("sequence") if isinstance(payload.get("sequence"), int) else None
    out = []
    for idx, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise CompositeError("P10 record malformed")
        actor, generation, sample_at = row.get("actor"), row.get("generation"), row.get("sampleAt")
        if not isinstance(actor, str) or not actor or not isinstance(generation, int) or generation < 0:
            raise CompositeError("P10 actor/generation missing")
        if not isinstance(sample_at, (int, float)) or not math.isfinite(float(sample_at)) or float(sample_at) < 0:
            raise CompositeError("P10 sampleAt invalid")
        for key in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch"):
            if row.get(key) != ident[key]:
                raise CompositeError(f"P10 {key} mismatch")
        anchor = row.get("canonicalAnchor")
        if not isinstance(anchor, Mapping) or anchor.get("schema") != "wof-render-object-anchor-v1":
            raise CompositeError("P10 canonical anchor missing")
        state = anchor.get("state")
        if state not in {"READY", "SUPPRESSED"}:
            raise CompositeError("P10 anchor state invalid")
        if state == "SUPPRESSED" and (isinstance(anchor.get("anchor"), Mapping) or isinstance(anchor.get("bodyBounds"), Mapping)):
            raise CompositeError("SUPPRESSED record carried coordinates")
        out.append({"schema": P24_OBSERVATION_SCHEMA, "sampleSeq": first_sample_seq + idx,
                    "frameSeq": transport_seq if transport_seq is not None else first_sample_seq + idx,
                    "observedAt": float(sample_at), **ident, "actor": actor, "generation": generation, "state": state,
                    "reason": None if state == "READY" else str(anchor.get("reason") or "SUPPRESSED"),
                    "actorPresence": "UNKNOWN", "transportSequence": transport_seq, "canonicalSampleAt": float(sample_at),
                    "canonicalGeometry": _geometry(anchor) if state == "READY" else None, "drawAcknowledgements": [],
                    "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False}})
    return out


@dataclass
class CaptureAccumulator:
    run_record: dict[str, Any]
    p22_recorder: Any
    observations: list[dict[str, Any]] = field(default_factory=list)
    last_order_by_identity: dict[tuple[str, ...], tuple[int | None, tuple[float, ...]]] = field(default_factory=dict)
    seen_signatures: set[str] = field(default_factory=set)

    def consume(self, entry: Mapping[str, Any]) -> bool:
        cap = self.run_record["capture"]; cap["statusSnapshotsSeen"] += 1
        status = extract_canonical_status(entry)
        if status is None:
            return False
        try:
            _safe_canonical(status); ident = identity_of(status); payload = _payload(status)
            if payload is None:
                return False
            key = tuple(ident[k] for k in ("worldSha256", "pageTargetId", "authorityKey", "runtimeEpoch", "rendererEpoch"))
            order = _payload_order(payload)
            signature = hashlib.sha256(json.dumps({"identity": key, "order": order, "records": payload.get("records")},
                                                    sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()
            if signature in self.seen_signatures:
                cap["duplicateSnapshotsRejected"] += 1; return False
            previous = self.last_order_by_identity.get(key)
            if previous is not None:
                prev_seq, prev_samples = previous; seq, samples = order
                if (prev_seq is not None and seq is not None and seq < prev_seq) or (prev_seq == seq and samples and prev_samples and min(samples) < min(prev_samples)):
                    cap["outOfOrderSnapshotsRejected"] += 1; return False
            prior = self.run_record.get("observedAuthority")
            if prior is None:
                self.run_record["observedAuthority"] = ident
            elif prior != ident:
                self.run_record["identityTransitions"].append({"atUtc": utc_now(), "from": prior, "to": ident})
                self.run_record["observedAuthority"] = ident
            self.p22_recorder.record_cycle(status)
            obs = temporal_observations_from_status(status, first_sample_seq=len(self.observations))
            if len(self.observations) + len(obs) > MAX_TEMPORAL_OBSERVATIONS:
                raise CompositeError("P24 observation bound exceeded")
            self.observations.extend(obs); self.seen_signatures.add(signature); self.last_order_by_identity[key] = order
            cap["canonicalCyclesAccepted"] += 1; cap["temporalObservationCount"] = len(self.observations)
            return True
        except Exception:
            cap["malformedSnapshotsRejected"] += 1
            raise


def evidence_ref(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": sha256_file(path)}


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise CompositeError(f"JSON root is not object: {path}")
    return value


def _find(root: Path, name: str) -> Path | None:
    direct = root / name
    if direct.is_file():
        return direct
    hits = sorted(p for p in root.rglob(name) if p.is_file())
    return hits[-1] if hits else None


def validate_receipt_candidate(receipt: Mapping[str, Any], exact: Mapping[str, Any]) -> None:
    candidate = receipt.get("candidate")
    if not isinstance(candidate, Mapping) or normalize_candidate(candidate) != normalize_candidate(exact):
        raise CompositeError("P21 receipt exact candidate mismatch")
    if receipt.get("alphaLiveMoved") is not False:
        raise CompositeError("P21 receipt reports alpha-live movement")


def validate_p17_candidate(bundle: Mapping[str, Any], exact: Mapping[str, Any]) -> None:
    candidate = bundle.get("candidate"); wanted = normalize_candidate(exact)
    if not isinstance(candidate, Mapping):
        raise CompositeError("P17 candidate missing")
    digest = candidate.get("candidateSha256") or candidate.get("contentSha256") or candidate.get("sha256")
    if candidate.get("sourceCommit") != wanted["sourceCommit"] or candidate.get("packageVersion") != wanted["packageVersion"] or digest != wanted["candidateSha256"]:
        raise CompositeError("P17 exact candidate mismatch")


def render_index_markdown(index: Mapping[str, Any]) -> str:
    lines = ["# Alpha V1 P25 Final Acceptance Composite Evidence Index", "", f"State: **{index.get('state')}**",
             f"Run nonce: `{index.get('runNonce')}`", "", "## Evidence", ""]
    for name, row in sorted((index.get("evidence") or {}).items()):
        if isinstance(row, Mapping):
            lines.append(f"- **{name}**: `{row.get('path')}` sha256=`{row.get('sha256')}` state=`{row.get('state')}`")
    lines += ["", "## Boundary", "", "- One run nonce binds P19/P21/W3/P16/P18/P22/P24/P17.",
              "- Only P10 READY/SUPPRESSED coordinates are consumed; SUPPRESSED never carries coordinates.",
              "- Page/runtime/renderer replacement is explicit; no cross-session merge or guessed identity.",
              "- Maximum automatic state is READY_FOR_OWNER_VISUAL_CONFIRMATION; P20 remains Owner gate.",
              "- realWofAcceptance=NOT_RUN; ownerVisualAcceptance=NOT_RUN; visibleProof=NOT_PROVEN; alphaLiveMoved=false.", ""]
    return "\n".join(lines)


def _load_modules(repo_root: Path):
    for path in (repo_root / "parallel" / "OWNER_STAGING", repo_root / "parallel" / "OWNER_ACCEPTANCE_STATE", repo_root / "parallel" / "TEMPORAL_ACCEPTANCE"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    return (importlib.import_module("p21_candidate"), importlib.import_module("exact_candidate_staging_acceptance"),
            importlib.import_module("dynamic_actor_state_coverage"), importlib.import_module("temporal_acceptance"))


@contextmanager
def p21_runtime_override(p21: Any, builder: Any, *, run_nonce: str, ring_path: Path):
    original = p21.build_runtime_command; old_nonce = os.environ.get("WOF_ALPHA_P25_RUN_NONCE"); old_ring = os.environ.get("WOF_ALPHA_P25_STATUS_RING")
    p21.build_runtime_command = builder; os.environ["WOF_ALPHA_P25_RUN_NONCE"] = run_nonce; os.environ["WOF_ALPHA_P25_STATUS_RING"] = str(ring_path)
    try:
        yield
    finally:
        p21.build_runtime_command = original
        if old_nonce is None: os.environ.pop("WOF_ALPHA_P25_RUN_NONCE", None)
        else: os.environ["WOF_ALPHA_P25_RUN_NONCE"] = old_nonce
        if old_ring is None: os.environ.pop("WOF_ALPHA_P25_STATUS_RING", None)
        else: os.environ["WOF_ALPHA_P25_STATUS_RING"] = old_ring


def run_composite(*, repo_root: Path, output_root: Path, staging_root: Path, permanent_repo: Path | None,
                  python_exe: str, browser: str, host: str, port: int, evidence_timeout: float,
                  stop_permanent_runtime: bool, pointer_path: Path | None = None) -> tuple[dict[str, Any], int]:
    repo_root = repo_root.expanduser().resolve(); output_root = output_root.expanduser().resolve(); output_root.mkdir(parents=True, exist_ok=True)
    p21_candidate, p21, p22, p24 = _load_modules(repo_root); candidate = p21_candidate.resolve_p19_candidate(repo_root, pointer_path)
    run = new_run_record(candidate); atomic_json(output_root / RUN_JSON, run); ring_path = output_root / STATUS_RING
    tee_path = Path(__file__).with_name("p25_runtime_tee.py").resolve()
    def builder(py: str, checkout: Path, owner_results: Path, selected_browser: str = "chrome") -> list[str]:
        return [py, str(tee_path), "--candidate-root", str(checkout), "--status-ring", str(ring_path), "--root", str(checkout),
                "--output-root", str(owner_results), "--browser", selected_browser]
    atomic_json(ring_path, {"schema": STATUS_RING_SCHEMA, "version": 1, "runNonce": run["runNonce"], "snapshots": [], "truncated": False})
    with p21_runtime_override(p21, builder, run_nonce=str(run["runNonce"]), ring_path=ring_path):
        receipt, p21_rc = p21.run_staged_acceptance(repo_root=repo_root, pointer_path=pointer_path, staging_root=staging_root,
            output_root=output_root / "p21", permanent_repo=permanent_repo, python_exe=python_exe, browser=browser,
            host=host, port=port, evidence_timeout=evidence_timeout, stop_permanent_runtime=stop_permanent_runtime)
    validate_receipt_candidate(receipt, candidate)
    receipt_path = output_root / "p21" / "ALPHA_P21_STAGING_RECEIPT.json"
    if not receipt_path.is_file(): raise CompositeError("P21 receipt file missing")
    run["p21"] = {"runId": ((receipt.get("staging") or {}).get("runId")), "receiptSha256": sha256_file(receipt_path)}
    recorder = p22.DynamicActorStateCoverageRecorder(candidate); accumulator = CaptureAccumulator(run, recorder)
    ring = _read_json(ring_path)
    if ring.get("schema") != STATUS_RING_SCHEMA or not isinstance(ring.get("snapshots"), list) or ring.get("runNonce") != run["runNonce"]:
        raise CompositeError("P25 status ring schema/run nonce mismatch")
    run["capture"]["statusRingTruncated"] = ring.get("truncated") is True
    for entry in ring["snapshots"]:
        if isinstance(entry, Mapping): accumulator.consume(entry)
    run["canonicalFeed"]["state"] = ("OBSERVED_MAINTAINED_P10_COORDINATOR" if run["capture"]["canonicalCyclesAccepted"] > 0
                                           else "NOT_EXPOSED_BY_STAGED_RUNTIME_STATUS" if run["capture"]["statusSnapshotsSeen"] > 0
                                           else "NO_STAGED_RUNTIME_STATUS")
    p22_report = recorder.build_report(generated_at_utc=utc_now()); p22_json, _ = p22.atomic_write_outputs(output_root / "p22", p22_report)
    p16 = _find(output_root / "p21", "ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.STAGED.json")
    p18 = _find(output_root / "p21", "ALPHA_CANONICAL_DRAW_EVIDENCE.STAGED.json")
    source: dict[str, Any] = {}
    if p16: source["p16"] = _read_json(p16)
    if p18: source["p18Snapshots"] = [_read_json(p18)]
    p24_report = p24.analyze_bundle({"schema": P24_BUNDLE_SCHEMA, "observations": accumulator.observations, "sourceEvidence": source})
    p24_json, _ = p24.write_report(p24_report, output_root / "p24")
    p17 = _find(output_root / "p21", "ALPHA_FINAL_ACCEPTANCE_BUNDLE.json")
    if p17 is None: raise CompositeError("P17 final bundle missing")
    p17_bundle = _read_json(p17); validate_p17_candidate(p17_bundle, candidate)
    evidence = {"P21": {**evidence_ref(receipt_path), "state": receipt.get("state")},
                "P22": {**evidence_ref(Path(p22_json)), "state": ((p22_report.get("coreAcceptance") or {}).get("state"))},
                "P24": {**evidence_ref(Path(p24_json)), "state": ((p24_report.get("aggregate") or {}).get("classification"))},
                "P17": {**evidence_ref(p17), "state": p17_bundle.get("automaticDecision") or p17_bundle.get("state")},
                "STATUS_RING": {**evidence_ref(ring_path), "state": "CAPTURED"}}
    w3 = _find(output_root / "p21", "LATEST_W3_RENDER_SOURCE_QUALIFICATION.json")
    for label, path in (("P16", p16), ("P18", p18), ("W3", w3)):
        if path:
            raw = _read_json(path); evidence[label] = {**evidence_ref(path), "state": raw.get("state") or raw.get("status") or raw.get("evidenceState")}
    p21_state = str(receipt.get("state") or ""); p17_state = str(p17_bundle.get("automaticDecision") or p17_bundle.get("state") or "")
    p24_state = str((p24_report.get("aggregate") or {}).get("classification") or "")
    if p21_rc != 0: final_state, reason = "P21_NOT_READY", f"P21 exited {p21_rc}: {p21_state}"
    elif run["capture"]["statusRingTruncated"]: final_state, reason = "INCOMPLETE_COMPOSITE_EVIDENCE", "bounded status ring truncated"
    elif run["capture"]["canonicalCyclesAccepted"] <= 0: final_state, reason = "INCOMPLETE_COMPOSITE_EVIDENCE", "no maintained canonical P10 cycles observed"
    elif p21_state != "READY_FOR_OWNER_VISUAL_CONFIRMATION" or p17_state != "READY_FOR_OWNER_VISUAL_CONFIRMATION": final_state, reason = "P17_NOT_READY", f"P21={p21_state} P17={p17_state}"
    elif p24_state in {"STALE_OR_MISMATCH", "UNPROVEN"}: final_state, reason = "INCOMPLETE_COMPOSITE_EVIDENCE", f"P24={p24_state}"
    else: final_state, reason = "READY_FOR_OWNER_VISUAL_CONFIRMATION", None
    run.update({"endedAtUtc": utc_now(), "state": final_state, "reason": reason, "evidence": evidence}); atomic_json(output_root / RUN_JSON, run)
    evidence["P25_RUN"] = {**evidence_ref(output_root / RUN_JSON), "state": final_state}
    index = {"schema": INDEX_SCHEMA, "version": 1, "runNonce": run["runNonce"], "candidate": normalize_candidate(candidate),
             "state": final_state, "reason": reason, "canonicalFeed": run["canonicalFeed"], "capture": run["capture"],
             "identityTransitions": run["identityTransitions"], "evidence": evidence, "realWofAcceptance": "NOT_RUN",
             "ownerVisualAcceptance": "NOT_RUN", "visibleProof": "NOT_PROVEN", "alphaLiveMoved": False,
             "safety": dict(SAFETY), "generatedAtUtc": utc_now()}
    atomic_json(output_root / INDEX_JSON, index); (output_root / INDEX_MD).write_text(render_index_markdown(index), encoding="utf-8", newline="\n")
    return index, 0 if final_state == "READY_FOR_OWNER_VISUAL_CONFIRMATION" else 2


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Alpha V1 P25 exact-candidate composite staged acceptance")
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2]); p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--staging-root", type=Path); p.add_argument("--permanent-repo", type=Path); p.add_argument("--python", dest="python_exe")
    p.add_argument("--browser", default="chrome"); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=9223)
    p.add_argument("--evidence-timeout", type=float, default=90.0); p.add_argument("--stop-permanent-runtime", action="store_true"); p.add_argument("--pointer-path", type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args(); repo = args.repo_root.expanduser().resolve(); _, p21, _, _ = _load_modules(repo)
    staging = args.staging_root or p21.default_staging_root(); permanent = args.permanent_repo if args.permanent_repo is not None else p21.default_permanent_repo()
    python_exe = args.python_exe or p21.resolve_python(None)
    try:
        index, rc = run_composite(repo_root=repo, output_root=args.output_root, staging_root=staging, permanent_repo=permanent,
            python_exe=python_exe, browser=args.browser, host=args.host, port=args.port, evidence_timeout=args.evidence_timeout,
            stop_permanent_runtime=args.stop_permanent_runtime, pointer_path=args.pointer_path)
        print(json.dumps({"state": index["state"], "index": str(args.output_root / INDEX_JSON), "runNonce": index["runNonce"]}, ensure_ascii=False, indent=2)); return rc
    except Exception as exc:
        print(json.dumps({"state": "BLOCKED", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2)); return 3


if __name__ == "__main__":
    raise SystemExit(main())
