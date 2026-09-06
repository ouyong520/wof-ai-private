from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from typing import Any, Mapping, Sequence

RECEIPT_SCHEMA = "wof-alpha-bounded-zero-click-live-diagnostic-receipt-v2"
P36_RAW_DISCOVERY_SCHEMA = "wof-p43-p36-source-discovery-raw-v1"
P42_SCHEMA = "wof-gstyphoon-renderer-correlation-probe-v1"
P37_CLASSIFICATION = "UNVERIFIED_AUTO_BASELINE"
P16_SCHEMA = "wof-alpha-canonical-owner-acceptance-evidence-v1"
P17_SCHEMA = "wof-alpha-final-acceptance-bundle-v1"
P36_WORKER_REL = "parallel/RENDER_AUTHORITY_V2/native_marker_renderer_submit_source_trace_worker.js"
EXPECTED_WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
P17_READY = "READY_FOR_OWNER_VISUAL_CONFIRMATION"
P17_BLOCKED = {
    "WAITING_W3_QUALIFICATION",
    "W3_INCONCLUSIVE",
    "WAITING_CANONICAL_RUNTIME_EVIDENCE",
    "CANONICAL_RUNTIME_SUPPRESSED",
    "WAITING_DRAW_EVIDENCE",
}
P17_FAILED = {"FAILED_EVIDENCE_MISMATCH"}
SAFETY = {
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "alphaLiveMoved": False,
    "zeroClick": True,
    "manualSeedRequired": False,
}
MAX_CONSOLE_EVENTS = 512
MAX_LOG_BYTES = 8 * 1024 * 1024


class DiagnosticError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def is_hex(value: Any, size: int) -> bool:
    return isinstance(value, str) and len(value) == size and all(ch in "0123456789abcdef" for ch in value.lower())


def require_hex(value: Any, name: str, size: int) -> str:
    if not is_hex(value, size):
        raise DiagnosticError(f"{name} must be exact {size}-hex")
    return str(value).lower()


def load_json_bytes(data: bytes, source: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8-sig"))
    except Exception as exc:
        raise DiagnosticError(f"{source}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise DiagnosticError(f"{source}: JSON root must be an object")
    return value


class GitReader:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.expanduser().resolve()

    def _run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        cp = subprocess.run(
            ["git", *args], cwd=self.repo_root, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False,
        )
        if check and cp.returncode:
            err = cp.stderr.decode("utf-8", "replace").strip()
            out = cp.stdout.decode("utf-8", "replace").strip()
            raise DiagnosticError(err or out or f"git {' '.join(args)} failed")
        return cp

    def commit_exists(self, commit: str) -> bool:
        return self._run("cat-file", "-e", f"{commit}^{{commit}}", check=False).returncode == 0

    def read_blob(self, commit: str, rel_path: str) -> bytes:
        if Path(rel_path).is_absolute() or ".." in Path(rel_path).parts:
            raise DiagnosticError(f"unbounded repository path: {rel_path}")
        return self._run("show", f"{commit}:{rel_path}").stdout

    def tree(self, commit: str) -> str:
        value = self._run("rev-parse", f"{commit}^{{tree}}").stdout.decode().strip().lower()
        return require_hex(value, "tree", 40)

    def rev(self, ref: str) -> str | None:
        cp = self._run("rev-parse", "--verify", f"{ref}^{{commit}}", check=False)
        if cp.returncode:
            return None
        value = cp.stdout.decode().strip().lower()
        return value if is_hex(value, 40) else None

    def head(self) -> str:
        value = self._run("rev-parse", "HEAD").stdout.decode().strip().lower()
        return require_hex(value, "HEAD", 40)

    def status(self) -> list[str]:
        return self._run("status", "--porcelain").stdout.decode("utf-8", "replace").splitlines()


def artifact_record(rel_path: str, data: bytes) -> dict[str, Any]:
    raw = load_json_bytes(data, rel_path)
    return {
        "path": rel_path,
        "schema": raw.get("schema"),
        "sha256": sha256_bytes(data),
        "gitBlobSha": git_blob_sha(data),
        "size": len(data),
        "raw": raw,
    }


def _same_identity(raw: Mapping[str, Any], source_commit: str, package: str, label: str) -> None:
    if raw.get("sourceCommit") not in (None, source_commit):
        raise DiagnosticError(f"{label}: sourceCommit mismatch")
    if raw.get("packageVersion") not in (None, package):
        raise DiagnosticError(f"{label}: packageVersion mismatch")


def verify_candidate_binding(
    git: GitReader, *, metadata_commit: str, source_commit: str,
    pointer_path: str, provenance_path: str,
) -> dict[str, Any]:
    metadata_commit = require_hex(metadata_commit, "metadataCommit", 40)
    source_commit = require_hex(source_commit, "sourceCommit", 40)
    if not git.commit_exists(metadata_commit):
        raise DiagnosticError("exact metadataCommit is not present locally; no implicit HEAD/fetch fallback")
    if not git.commit_exists(source_commit):
        raise DiagnosticError("exact sourceCommit is not present locally; no implicit HEAD/fetch fallback")

    pointer = artifact_record(pointer_path, git.read_blob(metadata_commit, pointer_path))
    provenance = artifact_record(provenance_path, git.read_blob(metadata_commit, provenance_path))
    p = pointer["raw"]
    prov = provenance["raw"]
    if p.get("schema") != "wof-alpha-latest-final-canonical-candidate-v1" or p.get("version") != 1 or p.get("state") != "READY":
        raise DiagnosticError("candidate pointer is not exact READY v1")
    if p.get("sourceCommit") != source_commit:
        raise DiagnosticError("explicit sourceCommit disagrees with pointer")
    package = p.get("packageVersion")
    if not isinstance(package, str) or not package:
        raise DiagnosticError("pointer packageVersion missing")
    for flag in ("alphaLiveMoved", "alphaLivePromoted", "promotionPerformed"):
        if flag in p and p.get(flag) is not False:
            raise DiagnosticError(f"pointer unsafe promotion state: {flag}")
    if prov.get("sourceCommit") != source_commit or prov.get("packageVersion") != package:
        raise DiagnosticError("provenance identity disagrees with explicit source/package")
    if prov.get("alphaLiveMoved") is not False or prov.get("promotionPerformed") is not False:
        raise DiagnosticError("provenance unsafe promotion/alpha-live state")
    if prov.get("pointerPath") != pointer_path or prov.get("pointerSha256") != pointer["sha256"]:
        raise DiagnosticError("provenance does not bind exact pointer bytes")

    rels = {}
    for name in ("candidate", "attestation", "manifest"):
        path_key, sha_key = f"{name}Path", f"{name}Sha256"
        rel = p.get(path_key)
        expected = p.get(sha_key)
        if not isinstance(rel, str) or not rel or not is_hex(expected, 64):
            raise DiagnosticError(f"pointer {name} path/hash missing")
        rec = artifact_record(rel, git.read_blob(metadata_commit, rel))
        if rec["sha256"] != str(expected).lower():
            raise DiagnosticError(f"{name} SHA-256 mismatch")
        if prov.get(path_key) != rel or prov.get(sha_key) != rec["sha256"]:
            raise DiagnosticError(f"provenance does not bind exact {name}")
        _same_identity(rec["raw"], source_commit, package, name)
        rels[name] = rec

    candidate = rels["candidate"]["raw"]
    att = rels["attestation"]["raw"]
    if candidate.get("schema") != "wof-owner-oneclick-package-v1":
        raise DiagnosticError("candidate schema mismatch")
    if candidate.get("sourceCommit") != source_commit or candidate.get("packageVersion") != package:
        raise DiagnosticError("candidate exact identity mismatch")
    if att.get("schema") != "wof-alpha-final-canonical-candidate-attestation-v1":
        raise DiagnosticError("attestation schema mismatch")
    if att.get("candidatePath") not in (None, rels["candidate"]["path"]):
        raise DiagnosticError("attestation candidate path mismatch")
    if att.get("candidateSha256") not in (None, rels["candidate"]["sha256"]):
        raise DiagnosticError("attestation candidate SHA mismatch")

    runtime_pins = prov.get("runtimePins") if isinstance(prov.get("runtimePins"), Mapping) else {}
    return {
        "state": "PASS",
        "metadataCommit": metadata_commit,
        "metadataTree": git.tree(metadata_commit),
        "sourceCommit": source_commit,
        "sourceTree": git.tree(source_commit),
        "packageVersion": package,
        "selectedFileCount": p.get("selectedFileCount"),
        "pointer": {k: v for k, v in pointer.items() if k != "raw"},
        "provenance": {k: v for k, v in provenance.items() if k != "raw"},
        "candidate": {k: v for k, v in rels["candidate"].items() if k != "raw"},
        "attestation": {k: v for k, v in rels["attestation"].items() if k != "raw"},
        "manifest": {k: v for k, v in rels["manifest"].items() if k != "raw"},
        "runtimePins": runtime_pins,
        "requiredTestedCommits": p.get("requiredTestedCommits") or prov.get("requiredTestedCommits"),
        "safety": dict(SAFETY),
    }


def verify_source_checkout(source_checkout: Path, source_commit: str) -> dict[str, Any]:
    git = GitReader(source_checkout)
    head = git.head()
    if head != source_commit:
        raise DiagnosticError(f"source checkout HEAD mismatch: expected={source_commit} actual={head}")
    dirty = git.status()
    if dirty:
        raise DiagnosticError(f"source checkout must be clean: {dirty[:8]}")
    return {"path": str(source_checkout.resolve()), "head": head, "tree": git.tree(head), "clean": True}


def verify_dedicated_python() -> dict[str, Any]:
    if os.name != "nt":
        raise DiagnosticError("live P43 execution requires the existing Windows WOF dedicated venv; non-Windows execution is test-only")
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise DiagnosticError("LOCALAPPDATA missing; cannot resolve existing WOF dedicated venv")
    expected = (Path(local) / "WOF Alpha Current Main" / "venv" / "Scripts" / "python.exe").resolve()
    actual = Path(sys.executable).resolve()
    if not expected.is_file():
        raise DiagnosticError(f"existing WOF dedicated venv Python missing: {expected}; no install/fallback allowed")
    if actual != expected:
        raise DiagnosticError(f"P43 must run with existing WOF dedicated venv Python: expected={expected} actual={actual}")
    return {"python": str(actual), "dedicated": True, "installPerformed": False, "globalEnvironmentChanged": False}


@dataclass
class GateLedger:
    rows: list[dict[str, Any]]
    sequence: int = 0

    def __init__(self) -> None:
        self.rows = []
        self.sequence = 0

    def transition(self, gate: str, state: str, reason: str | None = None, detail: Any = None) -> dict[str, Any]:
        if state not in {"PENDING", "PASS", "FAIL", "BLOCKED", "SKIPPED"}:
            raise DiagnosticError(f"invalid gate state: {state}")
        self.sequence += 1
        row = {"seq": self.sequence, "atUtc": utc_now(), "gate": gate, "state": state, "reason": reason, "detail": detail}
        self.rows.append(row)
        return row

    def first_failure(self) -> dict[str, Any] | None:
        return next((r for r in self.rows if r["state"] in {"FAIL", "BLOCKED"}), None)

    def passed_before_first_failure(self) -> list[str]:
        first = self.first_failure()
        ceiling = first["seq"] if first else 10**18
        out: list[str] = []
        for row in self.rows:
            if row["seq"] >= ceiling:
                break
            if row["state"] == "PASS" and row["gate"] not in out:
                out.append(row["gate"])
        return out

    def latest(self) -> dict[str, str]:
        latest: dict[str, str] = {}
        for row in self.rows:
            latest[row["gate"]] = row["state"]
        return latest


class EventTimeline:
    def __init__(self) -> None:
        self._seq = 0
        self.rows: list[dict[str, Any]] = []

    def add(self, kind: str, data: Any) -> None:
        self._seq += 1
        self.rows.append({"seq": self._seq, "atUtc": utc_now(), "kind": kind, "data": data})


def validate_p16(raw: Mapping[str, Any], binding: Mapping[str, Any], association: Mapping[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    if raw.get("schema") != P16_SCHEMA or raw.get("version") != 1:
        return False, "P16_SCHEMA_OR_VERSION_MISMATCH", {}
    if raw.get("packageVersion") != binding.get("packageVersion"):
        return False, "P16_PACKAGE_MISMATCH", {}
    if raw.get("visibleProof") != "NOT_PROVEN":
        return False, "P16_VISIBLE_PROOF_BOUNDARY_MISMATCH", {}
    world = raw.get("world") if isinstance(raw.get("world"), Mapping) else {}
    runtime = raw.get("runtime") if isinstance(raw.get("runtime"), Mapping) else {}
    canonical = raw.get("canonical") if isinstance(raw.get("canonical"), Mapping) else {}
    safety = raw.get("safety") if isinstance(raw.get("safety"), Mapping) else {}
    if world.get("accepted") is not True:
        return False, "P16_WORLD_NOT_ACCEPTED", {}
    if world.get("sha256") != EXPECTED_WORLD_SHA256:
        return False, "P16_WORLD_IDENTITY_MISMATCH", {}
    if not isinstance(world.get("pageTargetId"), str) or world.get("pageTargetId") != association.get("pageTargetId"):
        return False, "P16_PAGE_TARGET_MISMATCH", {}
    if not isinstance(world.get("workerTargetId"), str) or world.get("workerTargetId") != association.get("workerTargetId"):
        return False, "P16_WORKER_TARGET_MISMATCH", {}
    state = canonical.get("state")
    if not isinstance(state, str) or state in {"WAITING_WOF", "VERIFYING_WORLD"}:
        return False, f"P16_CANONICAL_STATE_NOT_USABLE:{state or 'MISSING'}", {}
    for field, key in (("runtimeEpoch", "epoch"), ("authorityKey", "authorityKey"), ("rendererEpoch", "rendererEpoch")):
        if not isinstance(runtime.get(key), str) or not runtime.get(key):
            return False, f"P16_{field.upper()}_MISSING", {}
    authority = runtime.get("rendererAuthority")
    if not (isinstance(authority, str) and authority) and not (isinstance(authority, Mapping) and authority):
        return False, "P16_RENDERER_AUTHORITY_MISSING", {}
    if safety.get("readOnly") is not True or safety.get("ramWrites") != 0 or safety.get("inputInjection") is not False:
        return False, "P16_SAFETY_MISMATCH", {}
    return True, "USABLE", {
        "worldSha256": world.get("sha256"),
        "pageTargetId": world.get("pageTargetId"),
        "workerTargetId": world.get("workerTargetId"),
        "runtimeEpoch": runtime.get("epoch"),
        "rendererEpoch": runtime.get("rendererEpoch"),
        "authorityKey": runtime.get("authorityKey"),
        "rendererAuthority": authority,
        "canonicalState": state,
        "canonicalReason": canonical.get("reason"),
    }


def validate_p17(raw: Mapping[str, Any], binding: Mapping[str, Any]) -> tuple[str, str]:
    if raw.get("schema") != P17_SCHEMA:
        return "FAIL", "P17_SCHEMA_MISMATCH"
    candidate = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
    if candidate.get("sourceCommit") != binding.get("sourceCommit"):
        return "FAIL", "P17_SOURCE_COMMIT_MISMATCH"
    if candidate.get("packageVersion") != binding.get("packageVersion"):
        return "FAIL", "P17_PACKAGE_MISMATCH"
    if candidate.get("contentSha256") != (binding.get("candidate") or {}).get("sha256"):
        return "FAIL", "P17_CANDIDATE_SHA_MISMATCH"
    if raw.get("visibleProof") != "NOT_PROVEN":
        return "FAIL", "P17_VISIBLE_PROOF_BOUNDARY_MISMATCH"
    safety = raw.get("safety") if isinstance(raw.get("safety"), Mapping) else {}
    if safety.get("alphaLiveMoved") is not False:
        return "FAIL", "P17_ALPHA_LIVE_MOVED"
    decision = raw.get("automaticDecision")
    if decision == P17_READY:
        return "PASS", str(decision)
    if decision in P17_FAILED:
        return "FAIL", str(decision)
    if decision in P17_BLOCKED or isinstance(decision, str):
        return "BLOCKED", str(decision)
    return "BLOCKED", "P17_AUTOMATIC_DECISION_MISSING"


def summarize_p39(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {
            "classification": P37_CLASSIFICATION,
            "state": "NOT_PRESENT",
            "visible": False,
            "visiblePlayers": [],
            "players": {p: {"state": "NOT_PRESENT", "visible": False, "stale": None, "lost": None, "ambiguous": None, "reacquireCount": None} for p in ("P1", "P2", "P3")},
            "authorityEligible": False,
        }
    controller = raw.get("controller") if isinstance(raw.get("controller"), Mapping) else {}
    tracks = controller.get("tracks") if isinstance(controller.get("tracks"), Mapping) else {}
    visible = set(raw.get("visiblePlayers") or [])
    players: dict[str, Any] = {}
    for player in ("P1", "P2", "P3"):
        track = tracks.get(player) if isinstance(tracks.get(player), Mapping) else {}
        state = str(track.get("state") or "UNAVAILABLE")
        players[player] = {
            "state": state,
            "visible": player in visible,
            "stale": controller.get("visibleFresh") is False and bool(raw.get("enabled")),
            "lost": state == "LOST",
            "ambiguous": state == "AMBIGUOUS",
            "pendingReacquire": state == "PENDING_REACQUIRE",
            "reacquireCount": track.get("reacquireCount"),
            "x": track.get("x"),
            "y": track.get("y"),
            "ageMs": track.get("ageMs"),
            "acquisition": track.get("acquisition"),
            "ambiguityReason": track.get("ambiguityReason"),
        }
    return {
        "classification": P37_CLASSIFICATION,
        "schema": raw.get("schema"),
        "state": raw.get("state"),
        "enabled": raw.get("enabled"),
        "visible": bool(visible),
        "visiblePlayers": sorted(visible),
        "visibleFresh": controller.get("visibleFresh"),
        "controllerState": controller.get("state"),
        "players": players,
        "rendererSourceProof": raw.get("rendererSourceProof"),
        "authorityEligible": False,
        "productAuthority": raw.get("productAuthority"),
        "safety": raw.get("safety"),
    }


def classify_p42_snapshot(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or raw.get("present") is not True:
        return {"state": "P42_CORRELATION_PROBE_NOT_PRESENT", "schema": P42_SCHEMA, "present": False, "authorityEligible": False, "raw": raw if isinstance(raw, Mapping) else None}
    return {
        "state": "P42_CORRELATION_PROBE_PRESENT",
        "schema": P42_SCHEMA,
        "present": True,
        "authorityEligible": False,
        "surface": raw.get("surface"),
        "bundle": raw.get("bundle"),
        "error": raw.get("error"),
    }


def actor_generation_pairs(bundle: Mapping[str, Any]) -> list[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for event in bundle.get("events") or []:
        if not isinstance(event, Mapping):
            continue
        assoc = event.get("actorAssociation")
        if not isinstance(assoc, Mapping) or assoc.get("explicit") is not True or assoc.get("generationBound") is not True:
            continue
        player, generation = assoc.get("player"), assoc.get("generation")
        if player in {"P1", "P2", "P3"} and isinstance(generation, str) and generation:
            found.add((player, generation))
    return sorted(found)


def _p36_source_discovery_expr() -> str:
    return r"""(()=>{const SC='wof-native-marker-renderer-submit-source-v1',allowed=new Set(['SOURCE_TRACED_POINTER','DIRECT_RENDER_HOOK','EXPORTED_RENDERER_POINTER']);const roots=[['self',globalThis],['self.Module',globalThis.Module],['self.Module.asm',globalThis.Module&&globalThis.Module.asm]];const out=[];const nonempty=x=>typeof x==='string'&&x.trim().length>0;function errs(s){if(!s||typeof s!=='object')return['DIRECT_SOURCE_MISSING'];const e=[];if(s.schema!==SC)e.push('DIRECT_SOURCE_SCHEMA_INVALID');if(!allowed.has(s.derivationKind))e.push('DIRECT_SOURCE_DERIVATION_UNQUALIFIED');if(s.guessed!==false)e.push('DIRECT_SOURCE_GUESSED_OR_UNSPECIFIED');if(s.displayedFrameCausalLink!==true)e.push('DISPLAYED_FRAME_CAUSAL_LINK_MISSING');if(s.coordinateAuthority!=='NATIVE_RENDERER_OBJECT_384X224')e.push('NATIVE_COORDINATE_AUTHORITY_MISSING');for(const f of ['screenshotCoordinatesUsed','ocrCoordinatesUsed','templateCoordinatesUsed','worldProjectionCoordinatesUsed'])if(s[f]!==false)e.push(f.toUpperCase()+'_FORBIDDEN');if(!Array.isArray(s.sourceTrace)||s.sourceTrace.length<2||s.sourceTrace.some(x=>!nonempty(x)))e.push('SOURCE_TRACE_INCOMPLETE');if(!nonempty(s.instrumentationId))e.push('DIRECT_SOURCE_INSTRUMENTATIONID_MISSING');if(!nonempty(s.hookSite))e.push('DIRECT_SOURCE_HOOKSITE_MISSING');if(s.readOnly!==true||s.ramWrites!==0||s.inputInjection!==false)e.push('DIRECT_SOURCE_SAFETY_BOUNDARY_INVALID');if(s.ownerSelectionRequired!==false)e.push('OWNER_SELECTION_FORBIDDEN');if(s.manualSeedRequired!==false)e.push('MANUAL_SEED_FORBIDDEN');if(typeof s.subscribe!=='function')e.push('DIRECT_SOURCE_SUBSCRIBE_HOOK_MISSING');return e;}for(const [rn,r] of roots){if(!r||typeof r!=='object')continue;for(const key of ['__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__','WOFNativeMarkerRendererSubmitSourceV1']){let s=null;try{s=r[key]}catch(ex){out.push({path:rn+'.'+key,present:false,readError:String(ex&&ex.message||ex)});continue}if(!s||typeof s!=='object'){out.push({path:rn+'.'+key,present:false});continue}const rejectionReasons=errs(s);out.push({path:rn+'.'+key,present:true,schema:s.schema,derivationKind:s.derivationKind,guessed:s.guessed,displayedFrameCausalLink:s.displayedFrameCausalLink,coordinateAuthority:s.coordinateAuthority,screenshotCoordinatesUsed:s.screenshotCoordinatesUsed,ocrCoordinatesUsed:s.ocrCoordinatesUsed,templateCoordinatesUsed:s.templateCoordinatesUsed,worldProjectionCoordinatesUsed:s.worldProjectionCoordinatesUsed,sourceTrace:Array.isArray(s.sourceTrace)?s.sourceTrace.slice(0,32):s.sourceTrace,instrumentationId:s.instrumentationId,hookSite:s.hookSite,readOnly:s.readOnly,ramWrites:s.ramWrites,inputInjection:s.inputInjection,ownerSelectionRequired:s.ownerSelectionRequired,manualSeedRequired:s.manualSeedRequired,subscribeType:typeof s.subscribe,rejectionReasons,qualified:rejectionReasons.length===0});}}return{schema:'wof-p43-p36-source-discovery-raw-v1',candidates:out,qualifiedCount:out.filter(x=>x.qualified).length,readOnly:true,ramWrites:0,inputInjection:false};})()"""


def _p9_probe_expr() -> str:
    return r"""(()=>{const h=globalThis.WOFALPHAHUD,e=globalThis.WOFAlphaCanonicalAnchorEnvelope,p=globalThis.WOFAlphaCanonicalOverlayPlan;let status=null,error=null;try{status=typeof h?.status==='function'?h.status():null}catch(ex){error=String(ex&&ex.stack||ex)}const required=['bindCanonicalOverlayAuthority','ingestCanonicalAnchorEnvelope','clearCanonicalOverlayAuthority','status'];const missing=[];if(!e)missing.push('WOFAlphaCanonicalAnchorEnvelope');if(!p)missing.push('WOFAlphaCanonicalOverlayPlan');if(!h)missing.push('WOFALPHAHUD');for(const k of required)if(typeof h?.[k]!=='function')missing.push('WOFALPHAHUD.'+k);return{schema:'wof-p43-p9-gate-probe-v1',present:missing.length===0,missing,status,error,readOnly:true,ramWrites:0,inputInjection:false};})()"""


def _p39_probe_expr() -> str:
    return r"""(()=>{try{const h=globalThis.WOFALPHAAUTOBASELINEHUD;if(!h||typeof h.status!=='function')return null;return h.status();}catch(ex){return{schema:'wof-alpha-auto-baseline-visible-hud-v1',classification:'UNVERIFIED_AUTO_BASELINE',state:'STATUS_ERROR',error:String(ex&&ex.stack||ex),rendererSourceProof:null,authorityEligibility:{p29Pass:false,p32NativeMarkerQualification:false,p36RendererSourceTrace:false,p34RetryReadiness:false,promotion:false},safety:{readOnly:true,ramWrites:0,inputInjection:false}};}})()"""


def _p42_probe_expr() -> str:
    return r"""(()=>{const wanted='wof-gstyphoon-renderer-correlation-probe-v1',names=Object.getOwnPropertyNames(globalThis).filter(k=>/WOF/i.test(k)&&/CORRELATION/i.test(k)&&/PROBE/i.test(k)).slice(0,64),hits=[];for(const k of names){let v;try{v=globalThis[k]}catch(_){continue}if(!v||(typeof v!=='object'&&typeof v!=='function'))continue;let schema=null;try{schema=v.schema||(typeof v.status==='function'&&v.status()?.schema)}catch(_){}if(schema===wanted)hits.push([k,v]);}if(hits.length===0)return{present:false,searched:names};if(hits.length>1)return{present:true,error:'AMBIGUOUS_P42_CORRELATION_PROBE_SURFACES',surfaces:hits.map(x=>x[0]),bundle:null};const [surface,v]=hits[0];try{let bundle=null;if(typeof v.result==='function')bundle=v.result();else if(typeof v.bundle==='function')bundle=v.bundle();else if(typeof v.status==='function')bundle=v.status();else bundle=v;return{present:true,surface,bundle};}catch(ex){return{present:true,surface,error:String(ex&&ex.stack||ex),bundle:null};}})()"""


def _normalize_console_event(event: Mapping[str, Any], session_to_page: Mapping[str, str]) -> dict[str, Any]:
    params = event.get("params") if isinstance(event.get("params"), Mapping) else {}
    method = event.get("method")
    session_id = event.get("sessionId")
    out = {"method": method, "sessionId": session_id, "pageTargetId": session_to_page.get(str(session_id or "")), "params": params}
    if method == "Runtime.consoleAPICalled":
        args = params.get("args") if isinstance(params.get("args"), list) else []
        out["consoleType"] = params.get("type")
        out["text"] = " ".join(str(a.get("value") if isinstance(a, Mapping) and "value" in a else a.get("description") if isinstance(a, Mapping) else a) for a in args)
    elif method == "Runtime.exceptionThrown":
        details = params.get("exceptionDetails") if isinstance(params.get("exceptionDetails"), Mapping) else {}
        out["text"] = str(details.get("text") or "")
        out["exception"] = details
    return out


def _safe_eval(session: Any, expression: str, timeout: float = 5.0) -> tuple[Any, str | None]:
    try:
        return session.evaluate(expression, timeout=timeout), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _write_artifact(root: Path, name: str, payload: Any, *, pretty: bool = True) -> dict[str, Any]:
    data = pretty_bytes(payload) if pretty else canonical_bytes(payload)
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": str(path), "sha256": sha256_bytes(data), "size": len(data)}


def archive_file(root: Path, source: Path, name: str, max_bytes: int = MAX_LOG_BYTES) -> dict[str, Any]:
    source = source.expanduser().resolve()
    if not source.is_file():
        return {"state": "NOT_PRESENT", "source": str(source)}
    size = source.stat().st_size
    with source.open("rb") as fh:
        if size > max_bytes:
            fh.seek(size - max_bytes)
            data = fh.read(max_bytes)
            truncated = True
            offset = size - max_bytes
        else:
            data = fh.read()
            truncated = False
            offset = 0
    dest = root / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {"state": "CAPTURED", "source": str(source), "path": str(dest), "sha256": sha256_bytes(data), "capturedBytes": len(data), "sourceBytes": size, "truncated": truncated, "sourceOffset": offset}


def _load_optional_json(path: Path | None) -> tuple[dict[str, Any] | None, str | None]:
    if path is None:
        return None, "NOT_SUPPLIED"
    try:
        return load_json_bytes(path.expanduser().resolve().read_bytes(), str(path)), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def run_p36_producer(source_checkout: Path, bundle: Mapping[str, Any], identity: Mapping[str, Any]) -> dict[str, Any]:
    render_dir = source_checkout / "parallel" / "RENDER_AUTHORITY_V2"
    module_file = render_dir / "native_marker_renderer_submit_source_trace.py"
    if not module_file.is_file():
        return {"state": "BLOCKED", "reason": "P36_PRODUCER_NOT_PRESENT_IN_EXACT_SOURCE", "results": []}
    before_path = list(sys.path)
    sys.path.insert(0, str(render_dir))
    try:
        sys.modules.pop("native_marker_renderer_submit_source_trace", None)
        module = importlib.import_module("native_marker_renderer_submit_source_trace")
        binding = module.ProducerBinding(runtime_epoch=str(identity["runtimeEpoch"]), renderer_epoch=str(identity["rendererEpoch"]), authority_key=str(identity["authorityKey"]))
        pairs = actor_generation_pairs(bundle)
        if not pairs:
            return {"state": "BLOCKED", "reason": "NO_EXPLICIT_ACTOR_GENERATION_EVENTS", "results": []}
        results = []
        for player, generation in pairs:
            result = module.produce_native_marker_proof(bundle, player=player, generation=generation, binding=binding)
            results.append({"player": player, "generation": generation, "producer": result, "qualification": result.get("qualification") if isinstance(result, Mapping) else None})
        ready = [r for r in results if isinstance(r["producer"], Mapping) and r["producer"].get("state") == "READY_FOR_BOUNDED_LIVE_VERIFICATION"]
        return {"state": "PASS" if ready else "BLOCKED", "reason": "EXISTING_P32_QUALIFIER_ACCEPTED" if ready else "NO_P36_PRODUCER_RESULT_ACCEPTED", "results": results}
    except Exception as exc:
        return {"state": "FAIL", "reason": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc(), "results": []}
    finally:
        sys.path[:] = before_path


def build_human_receipt(receipt: Mapping[str, Any]) -> str:
    first = receipt.get("firstFailingGate")
    passed = receipt.get("passedBeforeFirstFailure") or []
    first_text = "NONE" if not first else f"{first.get('gate')} — {first.get('state')} — {first.get('reason')}"
    lines = [
        "# P43 Bounded Zero-Click Live Diagnostic Receipt", "",
        f"- Receipt schema: `{receipt.get('schema')}`",
        f"- sourceCommit: `{((receipt.get('candidateBinding') or {}).get('sourceCommit'))}`",
        f"- packageVersion: `{((receipt.get('candidateBinding') or {}).get('packageVersion'))}`",
        f"- First failing gate: **{first_text}**",
        f"- Gates already successful before first failure: {', '.join(passed) if passed else 'none'}",
        f"- P42: `{((receipt.get('p42') or {}).get('state'))}`",
        f"- P37/P39 classification: `{P37_CLASSIFICATION}`",
        f"- P36 teardown reason: `{((receipt.get('p36') or {}).get('teardownReason'))}`",
        f"- Safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `alphaLiveMoved={str((receipt.get('safety') or {}).get('alphaLiveMoved')).lower()}`",
        "", "## Gate timeline", "",
    ]
    for row in receipt.get("gateTimeline") or []:
        lines.append(f"- #{row.get('seq')} `{row.get('gate')}` → **{row.get('state')}** — {row.get('reason') or ''}")
    lines += ["", "## Raw evidence", ""]
    for key, value in (receipt.get("artifacts") or {}).items():
        if isinstance(value, Mapping) and value.get("path"):
            lines.append(f"- {key}: `{value.get('path')}` SHA-256 `{value.get('sha256')}`")
    lines += ["", "This receipt is diagnostic evidence only. It does not promote alpha-live or weaken P29/P32/P36 authority criteria.", ""]
    return "\n".join(lines)


def run_live_diagnostic(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    output = args.output_root.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    gates, events = GateLedger(), EventTimeline()
    errors: list[dict[str, Any]] = []
    artifacts: dict[str, Any] = {}
    metadata_git = GitReader(args.repo_root)
    alpha_before = {"local": metadata_git.rev("refs/heads/alpha-live"), "remote": metadata_git.rev("refs/remotes/origin/alpha-live")}
    client = None
    page_sessions: list[Any] = []
    worker_session = None
    p36_bundle: dict[str, Any] = {}
    p36_teardown = "NOT_STARTED"
    p39_samples: list[dict[str, Any]] = []
    p42_final = classify_p42_snapshot(None)
    target_capture: dict[str, Any] = {}
    association: dict[str, Any] = {}
    identity: dict[str, Any] = {}
    console_events: list[dict[str, Any]] = []
    session_to_page: dict[str, str] = {}
    browser_cursor = 0
    environment = None
    p36_discovery = None
    p36_discovery_error = None

    def record_error(where: str, exc: BaseException) -> None:
        row = {"atUtc": utc_now(), "where": where, "type": type(exc).__name__, "message": str(exc), "repr": repr(exc), "traceback": traceback.format_exc()}
        errors.append(row)
        events.add("exception", row)

    gates.transition("CANDIDATE_BINDING", "PENDING", "VERIFYING_EXACT_METADATA_AND_SOURCE")
    try:
        binding = verify_candidate_binding(metadata_git, metadata_commit=args.metadata_commit, source_commit=args.source_commit, pointer_path=args.pointer, provenance_path=args.provenance)
        binding["sourceCheckout"] = verify_source_checkout(args.source_checkout, args.source_commit)
        gates.transition("CANDIDATE_BINDING", "PASS", "EXACT_CANDIDATE_METADATA_SOURCE_AND_CHECKOUT_BOUND")
    except Exception as exc:
        record_error("CANDIDATE_BINDING", exc)
        gates.transition("CANDIDATE_BINDING", "FAIL", str(exc))
        binding = {"state": "FAIL", "sourceCommit": args.source_commit, "metadataCommit": args.metadata_commit, "packageVersion": None, "candidate": {}}

    gates.transition("DEDICATED_RUNTIME_ENVIRONMENT", "PENDING", "VERIFYING_EXISTING_WOF_VENV_NO_INSTALL")
    if binding.get("state") == "PASS":
        try:
            environment = verify_dedicated_python()
            gates.transition("DEDICATED_RUNTIME_ENVIRONMENT", "PASS", "EXISTING_WOF_DEDICATED_VENV_CONFIRMED", environment)
        except Exception as exc:
            record_error("DEDICATED_RUNTIME_ENVIRONMENT", exc)
            gates.transition("DEDICATED_RUNTIME_ENVIRONMENT", "FAIL", str(exc))
    else:
        gates.transition("DEDICATED_RUNTIME_ENVIRONMENT", "SKIPPED", "NOT_REACHED_AFTER_CANDIDATE_BINDING_FAILURE")

    gates.transition("BROWSER_ENDPOINT", "PENDING", "CONNECTING_EXISTING_DEDICATED_BROWSER")
    try:
        if gates.latest().get("DEDICATED_RUNTIME_ENVIRONMENT") != "PASS":
            raise DiagnosticError("dedicated WOF runtime environment gate did not pass")
        if not args.browser_websocket_url:
            raise DiagnosticError("explicit --browser-websocket-url required; harness does not launch/install a browser")
        pylaunch = args.source_checkout / "parallel" / "PYLAUNCH"
        sys.path.insert(0, str(pylaunch))
        from wof_launcher.cdp import CdpClient
        from wof_launcher.discovery_v2 import discover
        client = CdpClient(args.browser_websocket_url, timeout=min(5.0, args.duration))
        client.connect()
        browser_cursor = client.event_cursor()
        gates.transition("BROWSER_ENDPOINT", "PASS", "EXISTING_BROWSER_CONNECTED_READ_ONLY")
        events.add("browser_connected", {"websocket": args.browser_websocket_url})

        raw_targets = client.request("Target.getTargets").get("targetInfos") or []
        page_targets = [dict(t) for t in raw_targets if isinstance(t, Mapping) and t.get("type") == "page"]
        for page in page_targets:
            try:
                session = client.attach(str(page.get("targetId") or ""))
                session.request("Runtime.enable")
                page_sessions.append(session)
                session_to_page[str(session.session_id)] = str(page.get("targetId") or "")
            except Exception as exc:
                errors.append({"atUtc": utc_now(), "where": "PAGE_CONSOLE_ATTACH", "pageTargetId": page.get("targetId"), "message": f"{type(exc).__name__}: {exc}"})
        target_capture["allPageTargets"] = page_targets
        target_capture["allTargetCount"] = len(raw_targets)
        target_capture["rawTargets"] = raw_targets[:128]

        gates.transition("PAGE_WORKER_WASM_ASSOCIATION", "PENDING", "RUNNING_P31_AUTHORITATIVE_DISCOVERY")
        choice = discover(client, identity_timeout=min(20.0, max(2.0, args.duration / 2)))
        target_capture["discoveryDiagnostics"] = choice.diagnostics
        target_capture["discoveryReason"] = choice.reason
        target_capture["selectedPage"] = choice.page
        target_capture["selectedWorker"] = choice.worker
        target_capture["selectedWorkerProbe"] = choice.worker_probe
        target_capture["selectedIdentity"] = choice.identity
        if not choice.page or not choice.worker or not choice.identity or choice.identity.get("ok") is not True:
            raise DiagnosticError(choice.reason or "authoritative Page/Worker/WASM association unavailable")
        association = {"pageTargetId": choice.page.get("targetId"), "workerTargetId": choice.worker.get("targetId"), "worldIdentity": choice.identity, "authorityPath": (choice.diagnostics or {}).get("path")}
        gates.transition("PAGE_WORKER_WASM_ASSOCIATION", "PASS", "UNIQUE_AUTHORITATIVE_PAGE_WORKER_WASM_ASSOCIATION", association)
        worker_session = client.attach(str(association["workerTargetId"]))
        worker_session.request("Runtime.enable")

        gates.transition("P16_GATE", "PENDING", "WAITING_FOR_EXACT_P16_EVIDENCE")
        p16_raw, p16_err = _load_optional_json(args.p16_evidence)
        if p16_raw is None:
            gates.transition("P16_GATE", "BLOCKED", f"P16_EVIDENCE_{p16_err}")
        else:
            artifacts["p16Raw"] = _write_artifact(output, "raw/P16_EVIDENCE.json", p16_raw)
            ok, reason, identity = validate_p16(p16_raw, binding, association)
            gates.transition("P16_GATE", "PASS" if ok else "FAIL", reason, identity or p16_raw.get("canonical"))
        if not identity:
            identity = {"runtimeEpoch": None, "rendererEpoch": None, "authorityKey": None, "pageTargetId": association.get("pageTargetId"), "workerTargetId": association.get("workerTargetId")}

        gates.transition("P9_GATE", "PENDING", "READING_CANONICAL_P9_P8_HUD_SEAM")
        page_session = next((s for s in page_sessions if str(s.target_id) == str(association.get("pageTargetId"))), None)
        if page_session is None:
            page_session = client.attach(str(association["pageTargetId"]))
            page_session.request("Runtime.enable")
            page_sessions.append(page_session)
            session_to_page[str(page_session.session_id)] = str(association["pageTargetId"])
        p9_raw, p9_error = _safe_eval(page_session, _p9_probe_expr())
        target_capture["p9Probe"] = p9_raw
        if p9_error:
            gates.transition("P9_GATE", "FAIL", p9_error)
        elif isinstance(p9_raw, Mapping) and p9_raw.get("present") is True:
            gates.transition("P9_GATE", "PASS", "P9_P8_MAINTAINED_HUD_CANONICAL_SEAM_PRESENT", p9_raw)
        else:
            gates.transition("P9_GATE", "FAIL", "P9_CANONICAL_SEAM_MISSING", p9_raw)

        gates.transition("P36_SOURCE_GATE", "PENDING", "CAPTURING_RAW_SOURCE_DISCOVERY_AND_DIRECT_SUBMITS")
        p36_discovery, p36_discovery_error = _safe_eval(worker_session, _p36_source_discovery_expr())
        target_capture["p36SourceDiscoveryRaw"] = p36_discovery
        if p36_discovery_error:
            errors.append({"atUtc": utc_now(), "where": "P36_RAW_SOURCE_DISCOVERY", "message": p36_discovery_error})
        try:
            source_js = GitReader(args.source_checkout).read_blob(args.source_commit, P36_WORKER_REL).decode("utf-8")
            worker_session.evaluate(f"(0,eval)({json.dumps(source_js)});true", timeout=15.0)
            if not all(isinstance(identity.get(k), str) and identity.get(k) for k in ("runtimeEpoch", "rendererEpoch", "authorityKey")):
                gates.transition("P36_SOURCE_GATE", "BLOCKED", "P36_BINDING_UNAVAILABLE_FROM_P16")
            else:
                start_value = worker_session.evaluate("globalThis.WOFNATIVEMARKERSUBMITSOURCETRACEV1.start(" + json.dumps({"runtimeEpoch": identity["runtimeEpoch"], "rendererEpoch": identity["rendererEpoch"], "authorityKey": identity["authorityKey"]}) + ")", timeout=8.0)
                events.add("p36_start", start_value)
                if isinstance(start_value, Mapping) and start_value.get("state") in {"BLOCKED", "REJECTED"}:
                    gates.transition("P36_SOURCE_GATE", "BLOCKED" if start_value.get("state") == "BLOCKED" else "FAIL", str(start_value.get("reason")), start_value)
                else:
                    gates.transition("P36_SOURCE_GATE", "PASS", "P36_BOUNDED_SOURCE_OBSERVER_STARTED", start_value)
        except Exception as exc:
            record_error("P36_SOURCE_GATE", exc)
            gates.transition("P36_SOURCE_GATE", "FAIL", str(exc))

        deadline = time.monotonic() + max(0.1, min(args.duration, 60.0))
        while client is not None and time.monotonic() < deadline:
            browser_cursor, new_events = client.wait_for_events(browser_cursor, timeout=min(0.1, max(0.0, deadline - time.monotonic())), predicate=lambda e: e.get("method") in {"Runtime.consoleAPICalled", "Runtime.exceptionThrown"})
            for event in new_events:
                if len(console_events) < MAX_CONSOLE_EVENTS:
                    console_events.append(_normalize_console_event(event, session_to_page))
            if page_session is not None:
                p39_raw, p39_error = _safe_eval(page_session, _p39_probe_expr(), timeout=2.0)
                summary = summarize_p39(p39_raw)
                summary["sampleAtUtc"] = utc_now()
                if p39_error:
                    summary["probeError"] = p39_error
                p39_samples.append(summary)
                p42_raw, _ = _safe_eval(page_session, _p42_probe_expr(), timeout=2.0)
                p42_final = classify_p42_snapshot(p42_raw)
            if worker_session is not None:
                p42_worker, _ = _safe_eval(worker_session, _p42_probe_expr(), timeout=2.0)
                worker_p42 = classify_p42_snapshot(p42_worker)
                if worker_p42.get("present") is True:
                    p42_final = worker_p42
                status, _ = _safe_eval(worker_session, "globalThis.WOFNATIVEMARKERSUBMITSOURCETRACEV1?.status?.()||null", timeout=2.0)
                if isinstance(status, Mapping) and status.get("terminal") is True:
                    p36_teardown = str(status.get("reason") or "P36_TERMINAL")
                    break
        if p36_teardown == "NOT_STARTED":
            p36_teardown = "P43_BOUNDED_DURATION_REACHED"
        if worker_session is not None:
            _, seal_error = _safe_eval(worker_session, "globalThis.WOFNATIVEMARKERSUBMITSOURCETRACEV1?.seal?.('P43_BOUNDED_TEARDOWN')||null", timeout=3.0)
            final_status, final_status_error = _safe_eval(worker_session, "globalThis.WOFNATIVEMARKERSUBMITSOURCETRACEV1?.status?.()||null", timeout=3.0)
            target_capture["p36FinalStatus"] = final_status
            result, result_error = _safe_eval(worker_session, "globalThis.WOFNATIVEMARKERSUBMITSOURCETRACEV1?.result?.()||null", timeout=3.0)
            if isinstance(result, Mapping):
                p36_bundle = dict(result)
                p36_teardown = str(result.get("reason") or p36_teardown)
            if seal_error or final_status_error or result_error:
                errors.append({"atUtc": utc_now(), "where": "P36_TEARDOWN", "message": seal_error or final_status_error or result_error})
        artifacts["p36RawBundle"] = _write_artifact(output, "raw/P36_DIRECT_RENDERER_SUBMIT_BUNDLE.json", p36_bundle or {"state": "NOT_AVAILABLE"})
        artifacts["p36SourceDiscovery"] = _write_artifact(output, "raw/P36_SOURCE_DISCOVERY.json", p36_discovery or {"schema": P36_RAW_DISCOVERY_SCHEMA, "candidates": [], "error": p36_discovery_error})
        producer = run_p36_producer(args.source_checkout, p36_bundle, identity) if p36_bundle else {"state": "BLOCKED", "reason": "P36_RAW_BUNDLE_UNAVAILABLE", "results": []}
        artifacts["p36Producer"] = _write_artifact(output, "raw/P36_PRODUCER_AND_UNCHANGED_P32_RESULTS.json", producer)
        gates.transition("P36_PRODUCER_P32_GATE", "PASS" if producer.get("state") == "PASS" else ("FAIL" if producer.get("state") == "FAIL" else "BLOCKED"), str(producer.get("reason")), {"resultCount": len(producer.get("results") or [])})

        gates.transition("P17_GATE", "PENDING", "READING_EXISTING_P17_ACCEPTANCE_BUNDLE")
        p17_raw, p17_err = _load_optional_json(args.p17_bundle)
        if p17_raw is None:
            gates.transition("P17_GATE", "BLOCKED", f"P17_BUNDLE_{p17_err}")
        else:
            artifacts["p17Raw"] = _write_artifact(output, "raw/P17_ACCEPTANCE_BUNDLE.json", p17_raw)
            state, reason = validate_p17(p17_raw, binding)
            gates.transition("P17_GATE", state, reason, {"automaticDecision": p17_raw.get("automaticDecision"), "reasons": p17_raw.get("reasons")})

    except Exception as exc:
        record_error("LIVE_DIAGNOSTIC", exc)
        latest = gates.latest()
        if latest.get("BROWSER_ENDPOINT") == "PENDING":
            gates.transition("BROWSER_ENDPOINT", "FAIL", str(exc))
        elif latest.get("PAGE_WORKER_WASM_ASSOCIATION") == "PENDING":
            gates.transition("PAGE_WORKER_WASM_ASSOCIATION", "FAIL", str(exc))
    finally:
        if worker_session is not None:
            try:
                worker_session.evaluate("globalThis.WOFNATIVEMARKERSUBMITSOURCETRACEV1?.stop?.('P43_FINAL_TEARDOWN');true", timeout=2.0)
            except Exception:
                pass
            try:
                worker_session.close()
            except Exception:
                pass
        for session in page_sessions:
            try:
                session.close()
            except Exception:
                pass
        if client is not None:
            try:
                client.close()
            except Exception:
                pass

    for required_gate in ("PAGE_WORKER_WASM_ASSOCIATION", "P16_GATE", "P9_GATE", "P36_SOURCE_GATE", "P36_PRODUCER_P32_GATE", "P17_GATE"):
        if required_gate not in gates.latest():
            gates.transition(required_gate, "SKIPPED", "NOT_REACHED_AFTER_EARLIER_FAILURE")
    if "p36RawBundle" not in artifacts:
        artifacts["p36RawBundle"] = _write_artifact(output, "raw/P36_DIRECT_RENDERER_SUBMIT_BUNDLE.json", {"state": "NOT_REACHED", "events": [], "teardownReason": p36_teardown})
    if "p36SourceDiscovery" not in artifacts:
        artifacts["p36SourceDiscovery"] = _write_artifact(output, "raw/P36_SOURCE_DISCOVERY.json", {"schema": P36_RAW_DISCOVERY_SCHEMA, "state": "NOT_REACHED", "candidates": [], "rejectionReasons": ["NOT_REACHED_AFTER_EARLIER_FAILURE"]})
    if "p36Producer" not in artifacts:
        artifacts["p36Producer"] = _write_artifact(output, "raw/P36_PRODUCER_AND_UNCHANGED_P32_RESULTS.json", {"state": "BLOCKED", "reason": "NOT_REACHED_AFTER_EARLIER_FAILURE", "results": []})

    artifacts["targetsAssociation"] = _write_artifact(output, "raw/TARGETS_AND_ASSOCIATION.json", target_capture)
    artifacts["browserConsole"] = _write_artifact(output, "raw/BROWSER_PAGE_CONSOLE_EVENTS.json", console_events)
    artifacts["p39Timeline"] = _write_artifact(output, "raw/P37_P39_TRACKER_TIMELINE.json", p39_samples or [summarize_p39(None)])
    if p42_final.get("present") is True:
        artifacts["p42Correlation"] = _write_artifact(output, "raw/P42_CORRELATION_BUNDLE.json", p42_final)
        p42_final["artifact"] = artifacts["p42Correlation"]
    artifacts["errors"] = _write_artifact(output, "raw/EXCEPTIONS_AND_ERRORS.json", errors)
    artifacts["eventTimeline"] = _write_artifact(output, "raw/EVENT_TIMELINE.json", events.rows)
    artifacts["gateTimeline"] = _write_artifact(output, "raw/GATE_TRANSITION_TIMELINE.json", gates.rows)

    raw_logs: list[dict[str, Any]] = []
    if args.runtime_log is not None:
        raw_logs.append(archive_file(output, args.runtime_log, "raw/logs/RUNTIME.log"))
    for index, log in enumerate(args.staging_log or []):
        raw_logs.append(archive_file(output, log, f"raw/logs/STAGING_{index:02d}.log"))
    artifacts["rawLogsIndex"] = _write_artifact(output, "raw/RAW_LOGS_INDEX.json", raw_logs)

    alpha_after = {"local": metadata_git.rev("refs/heads/alpha-live"), "remote": metadata_git.rev("refs/remotes/origin/alpha-live")}
    alpha_moved = alpha_before != alpha_after
    safety = {**SAFETY, "alphaLiveMoved": alpha_moved, "alphaLiveBefore": alpha_before, "alphaLiveAfter": alpha_after, "promotionPerformed": False, "realGameLaunchedByHarness": False, "globalEnvironmentChanged": False, "installPerformed": False}
    if alpha_moved:
        gates.transition("ALPHA_LIVE_SAFETY", "FAIL", "ALPHA_LIVE_REF_CHANGED_DURING_CAPTURE", {"before": alpha_before, "after": alpha_after})
    else:
        gates.transition("ALPHA_LIVE_SAFETY", "PASS", "ALPHA_LIVE_UNCHANGED")

    first = gates.first_failure()
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "version": 2,
        "generatedAtUtc": utc_now(),
        "candidateBinding": binding,
        "dedicatedRuntimeEnvironment": environment,
        "allPageTargets": target_capture.get("allPageTargets") or [],
        "targetDiscovery": target_capture,
        "authoritativeAssociation": association,
        "runtimeAuthority": identity,
        "gateTimeline": gates.rows,
        "gateLatestState": gates.latest(),
        "firstFailingGate": first,
        "passedBeforeFirstFailure": gates.passed_before_first_failure(),
        "p36": {"sourceDiscoveryRaw": p36_discovery, "rawBundleArtifact": artifacts.get("p36RawBundle"), "producerArtifact": artifacts.get("p36Producer"), "teardownReason": p36_teardown, "eventCount": len(p36_bundle.get("events") or []) if isinstance(p36_bundle, Mapping) else 0},
        "p37p39": {"classification": P37_CLASSIFICATION, "samplesArtifact": artifacts.get("p39Timeline"), "latest": p39_samples[-1] if p39_samples else summarize_p39(None), "authorityEligible": False},
        "p42": p42_final,
        "rawLogs": raw_logs,
        "errors": errors,
        "artifacts": artifacts,
        "safety": safety,
        "realWofAcceptance": "NOT_RUN_BY_P43_IMPLEMENTATION_TASK",
        "ownerVisualAcceptance": "NOT_RUN",
        "promotionPerformed": False,
    }
    receipt_artifact = _write_artifact(output, "P43_DIAGNOSTIC_RECEIPT.json", receipt)
    artifacts["receipt"] = receipt_artifact
    human = build_human_receipt(receipt).encode("utf-8")
    human_path = output / "P43_DIAGNOSTIC_RECEIPT.md"
    human_path.write_bytes(human)
    artifacts["humanReceipt"] = {"path": str(human_path), "sha256": sha256_bytes(human), "size": len(human)}
    receipt["artifacts"] = artifacts
    artifacts["receipt"] = _write_artifact(output, "P43_DIAGNOSTIC_RECEIPT.json", receipt)
    return receipt, 0 if first is None and not alpha_moved else 2


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="P43 bounded zero-click live diagnostic harness. Observation only; does not launch the game or promote alpha-live.")
    p.add_argument("--repo-root", type=Path, required=True, help="Metadata/harness repository; no implicit HEAD is used.")
    p.add_argument("--source-checkout", type=Path, required=True, help="Existing clean checkout whose HEAD must equal --source-commit.")
    p.add_argument("--source-commit", required=True)
    p.add_argument("--metadata-commit", required=True)
    p.add_argument("--pointer", required=True)
    p.add_argument("--provenance", required=True)
    p.add_argument("--browser-websocket-url", required=True)
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--p16-evidence", type=Path)
    p.add_argument("--p17-bundle", type=Path)
    p.add_argument("--runtime-log", type=Path)
    p.add_argument("--staging-log", type=Path, action="append", default=[])
    p.add_argument("--duration", type=float, default=15.0)
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not (0.1 <= args.duration <= 60.0):
        raise SystemExit("--duration must be in [0.1, 60] seconds")
    receipt, rc = run_live_diagnostic(args)
    first = receipt.get("firstFailingGate")
    print(f"receipt={receipt.get('artifacts', {}).get('receipt', {}).get('path')}")
    print(f"firstFailingGate={first.get('gate') if isinstance(first, Mapping) else 'NONE'}")
    print("passedBeforeFirstFailure=" + ",".join(receipt.get("passedBeforeFirstFailure") or []))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
