from __future__ import annotations

import argparse, hashlib, json, os, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

VERIFY_SCHEMA = "wof-alpha-post-promotion-verification-v1"
CLOSE_SCHEMA = "wof-alpha-v1-final-close-bundle-v1"
POST_SCHEMA = "wof-alpha-post-promotion-owner-confirmation-v1"
P17_SCHEMA = "wof-alpha-final-acceptance-bundle-v1"
VISUAL_SCHEMA = "wof-alpha-owner-visual-confirmation-receipt-v1"
PLAN_SCHEMA = "wof-alpha-live-promotion-plan-v1"
PROMOTION_SCHEMA = "wof-alpha-live-promotion-result-v1"
W3_SCHEMA = "wof-render-source-qualification-v1"
P16_SCHEMA = "wof-alpha-canonical-owner-acceptance-evidence-v1"
P18_SCHEMA = "wof-alpha-canonical-draw-evidence-v1"

WAIT_P19 = "WAITING_FOR_P19_CANDIDATE"
WAIT_W3 = "WAITING_FOR_W3_LIVE_PASS"
WAIT_VISUAL = "WAITING_FOR_OWNER_VISUAL_PASS"
WAIT_PROMOTION = "WAITING_FOR_PROMOTION"
WAIT_PERMANENT = "WAITING_FOR_PERMANENT_CHANNEL_CONFIRMATION"
WAIT_POST = "WAITING_FOR_POST_PROMOTION_ACCEPTANCE"
REJECTED = "REJECTED_EVIDENCE_MISMATCH"
READY = "READY_TO_CLOSE"
FINAL = "ALPHA_V1_FINAL_COMPLETE"
RELEASE_MATCHED = "RELEASE_MATCHED"

REQUIRED_W1_FILES = (
    "WOF_ALPHA_TEST.cmd",
    "parallel/PYLAUNCH/owner_live_retest_loop.ps1",
    "parallel/PYLAUNCH/render_authority_measurement_entry.py",
    "parallel/PYLAUNCH/requirements.txt",
)
POINTER = Path("parallel/OWNER_ONECLICK/CANDIDATES/LATEST_FINAL_CANONICAL_CANDIDATE.json")
P17_NAME = "ALPHA_FINAL_ACCEPTANCE_BUNDLE.json"
P16_NAME = "ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.json"
P18_NAME = "ALPHA_CANONICAL_DRAW_EVIDENCE.json"
P22_NAME = "ALPHA_DYNAMIC_STATE_COVERAGE.json"
W3_NAME = "LATEST_W3_RENDER_SOURCE_QUALIFICATION.json"
POST_NAME = "ALPHA_POST_PROMOTION_OWNER_CONFIRMATION.json"

class GateError(RuntimeError): pass
class Waiting(GateError):
    def __init__(self, state: str, message: str): super().__init__(message); self.state = state
class Mismatch(GateError): pass

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def load(path: Path) -> dict[str, Any]:
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e: raise Waiting(WAIT_PROMOTION, f"missing evidence: {path}") from e
    except (OSError, json.JSONDecodeError) as e: raise Mismatch(f"unreadable JSON {path}: {e}") from e
    if not isinstance(value, dict): raise Mismatch(f"JSON root must be object: {path}")
    return value

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def canon_hash(value: Mapping[str, Any]) -> str:
    b = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return hashlib.sha256(b).hexdigest()

def safety(value: Any, source: str, *, unmoved=False) -> None:
    if not isinstance(value, Mapping): raise Mismatch(f"{source}: safety missing")
    for k, want in (("readOnly", True), ("ramWrites", 0), ("inputInjection", False)):
        if value.get(k) != want: raise Mismatch(f"{source}: safety {k}={value.get(k)!r}")
    for k in ("legacySpatialFallback", "screenshotProductionCoordinates", "worldProjectionProductionCoordinates", "guessedAddresses", "guessedRendererObjectAddress"):
        if k in value and value.get(k) is not False: raise Mismatch(f"{source}: forbidden safety flag {k}")
    if unmoved and value.get("alphaLiveMoved") is not False: raise Mismatch(f"{source}: alphaLiveMoved must be false")

def commit(value: Any, source: str) -> str:
    if not isinstance(value, str) or len(value) != 40 or any(c not in "0123456789abcdefABCDEF" for c in value):
        raise Mismatch(f"{source}: exact 40-hex commit required")
    return value.lower()

def resolve(repo: Path, value: str, parent: Path) -> Path:
    p = Path(value).expanduser()
    if p.is_absolute(): return p.resolve()
    q = (repo / p).resolve()
    return q if q.exists() else (parent / p).resolve()

def results_dir() -> Path: return Path.home() / "Documents" / "WOF_RESULTS"
def managed_repo() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home()/"AppData"/"Local"))) / "WOF_ALPHA_CURRENT_MAIN" / "repo"
def feedback_path() -> Path: return Path.home()/"Documents"/"WOF_RESULTS"/"LATEST_ALPHA_FEEDBACK.txt"
def desktop_launcher() -> Path: return Path.home()/"Desktop"/"WOF_ALPHA_TEST.cmd"

def candidate_from_pointer(repo: Path, pointer: Path | None = None) -> tuple[Path, Path]:
    p = (pointer or repo/POINTER).expanduser().resolve()
    if not p.is_file(): raise Waiting(WAIT_P19, f"P19 latest pointer missing: {p}")
    raw = load(p); cp = raw.get("candidatePath"); ap = raw.get("attestationPath")
    if not isinstance(cp, str) or not isinstance(ap, str): raise Mismatch("P19 pointer lacks candidatePath/attestationPath")
    c, a = resolve(repo, cp, p.parent), resolve(repo, ap, p.parent)
    if not c.is_file() or not a.is_file(): raise Waiting(WAIT_P19, "P19 candidate/attestation unavailable")
    if raw.get("candidateSha256") not in (None, sha(c)) or raw.get("attestationSha256") not in (None, sha(a)):
        raise Mismatch("P19 latest pointer hash mismatch")
    return c, a

def read_candidate(cpath: Path, apath: Path) -> dict[str, Any]:
    c, a = load(cpath), load(apath); source = commit(c.get("sourceCommit"), "candidate")
    package = c.get("packageVersion")
    if not isinstance(package, str) or not package: raise Mismatch("candidate packageVersion missing")
    safety(c.get("safety"), "candidate")
    conv = ((c.get("components") or {}).get("canonicalProductConvergence") or {})
    if conv and (conv.get("legacySpatialFallback") is not False or conv.get("alphaLivePromoted") is not False):
        raise Mismatch("candidate convergence safety/promotion claim invalid")
    csha, asha = sha(cpath), sha(apath)
    if a.get("schema") != "wof-alpha-final-canonical-candidate-attestation-v1" or a.get("version") != 1: raise Mismatch("attestation schema/version mismatch")
    if commit(a.get("sourceCommit"), "attestation") != source or a.get("packageVersion") != package or a.get("candidateSha256") != csha:
        raise Mismatch("candidate/attestation identity mismatch")
    safety(a.get("safety"), "attestation")
    return {"sourceCommit":source,"packageVersion":package,"candidateSha256":csha,"attestationSha256":asha}

def bundle_identity(raw: Mapping[str, Any]) -> dict[str, Any]:
    sections = []
    for key in ("w3Qualification","p16CanonicalRuntime","p18DrawEvidence"):
        sec = raw.get(key) if isinstance(raw.get(key), Mapping) else {}
        sections.append(sec.get("identity") if isinstance(sec.get("identity"), Mapping) else {})
    out = {}
    for field in ("worldSha256","pageTargetId","workerTargetId","authorityKey","runtimeEpoch","rendererEpoch","rendererAuthority"):
        vals = [s.get(field) for s in sections if s.get(field) not in (None,"")]
        if vals and any(v != vals[0] for v in vals[1:]): raise Mismatch(f"P17 identity mismatch: {field}")
        if vals: out[field] = vals[0]
    for field in ("worldSha256","pageTargetId","authorityKey","runtimeEpoch","rendererEpoch"):
        if not out.get(field): raise Mismatch(f"P17 identity missing {field}")
    return out

def require_identity(want: Mapping[str, Any], got: Mapping[str, Any], source: str) -> None:
    for k,v in want.items():
        if v not in (None,"") and got.get(k) not in (None,"",v): raise Mismatch(f"{source} identity mismatch {k}")

def read_bundle(path: Path, c: Mapping[str, Any]) -> dict[str, Any]:
    if not path.is_file(): raise Waiting(WAIT_W3, f"P17 bundle missing: {path}")
    r=load(path)
    if r.get("schema")!=P17_SCHEMA or r.get("version")!=1: raise Mismatch("P17 schema/version mismatch")
    d=r.get("automaticDecision")
    if d!="READY_FOR_OWNER_VISUAL_CONFIRMATION":
        if d in ("WAITING_W3_QUALIFICATION","W3_INCONCLUSIVE"): raise Waiting(WAIT_W3,f"P17 decision {d}")
        raise Mismatch(f"P17 decision {d!r}")
    safety(r.get("safety"),"P17",unmoved=True)
    ec=r.get("candidate") if isinstance(r.get("candidate"),Mapping) else {}
    if ec.get("sourceCommit")!=c["sourceCommit"] or ec.get("packageVersion")!=c["packageVersion"] or ec.get("contentSha256")!=c["candidateSha256"]: raise Mismatch("P17 candidate mismatch")
    w=r.get("w3Qualification") if isinstance(r.get("w3Qualification"),Mapping) else {}; ready=w.get("canonicalProducerReadiness") if isinstance(w.get("canonicalProducerReadiness"),Mapping) else {}; rs=ready.get("rendererSource") if isinstance(ready.get("rendererSource"),Mapping) else {}
    if w.get("status")!="PASS" or ready.get("ready") is not True or rs.get("proven") is not True: raise Waiting(WAIT_W3,"W3 live PASS/proven renderer missing")
    p16=r.get("p16CanonicalRuntime") if isinstance(r.get("p16CanonicalRuntime"),Mapping) else {}; p18=r.get("p18DrawEvidence") if isinstance(r.get("p18DrawEvidence"),Mapping) else {}
    if p16.get("canonicalState")!="HUD_INGEST_ACCEPTED" or p18.get("evidenceState")!="CANONICAL_DRAW_ACKNOWLEDGED": raise Mismatch("P16/P18 automatic evidence not ready")
    if r.get("visibleProof")!="NOT_PROVEN" or r.get("ownerVisualConfirmationRequired") is not True: raise Mismatch("P17 must precede Owner visual PASS")
    ic=r.get("identityConsistency") if isinstance(r.get("identityConsistency"),Mapping) else {}
    if ic.get("consistent") is not True or ic.get("mismatches") not in ([],(),None): raise Mismatch("P17 identityConsistency not clean")
    return {"raw":r,"sha256":sha(path),"identity":bundle_identity(r)}

def read_p16(path: Path, c: Mapping[str,Any], ident: Mapping[str,Any]) -> dict[str,Any]:
    if not path.is_file(): raise Waiting(WAIT_W3,"P16 evidence missing")
    r=load(path)
    if r.get("schema")!=P16_SCHEMA or r.get("version")!=1: raise Mismatch("P16 schema/version mismatch")
    safety(r.get("safety"),"P16"); st=((r.get("canonical") or {}).get("state"))
    if st!="HUD_INGEST_ACCEPTED": raise Mismatch("P16 not HUD_INGEST_ACCEPTED")
    if r.get("packageVersion") not in (None,c["packageVersion"]): raise Mismatch("P16 package mismatch")
    w=r.get("world") if isinstance(r.get("world"),Mapping) else {}; rt=r.get("runtime") if isinstance(r.get("runtime"),Mapping) else {}
    got={"worldSha256":w.get("sha256"),"pageTargetId":w.get("pageTargetId"),"workerTargetId":w.get("workerTargetId"),"authorityKey":rt.get("authorityKey"),"runtimeEpoch":rt.get("epoch"),"rendererEpoch":rt.get("rendererEpoch"),"rendererAuthority":rt.get("rendererAuthority")}
    require_identity(ident,got,"P16"); return {"sha256":sha(path),"state":st}

def read_p18(path: Path, c: Mapping[str,Any], ident: Mapping[str,Any]) -> dict[str,Any]:
    if not path.is_file(): raise Waiting(WAIT_W3,"P18 evidence missing")
    r=load(path)
    if r.get("schema")!=P18_SCHEMA or r.get("version")!=1: raise Mismatch("P18 schema/version mismatch")
    safety(r.get("safety"),"P18"); st=r.get("evidenceState") or r.get("state")
    if st!="CANONICAL_DRAW_ACKNOWLEDGED": raise Mismatch("P18 draw not acknowledged")
    if r.get("packageVersion") not in (None,c["packageVersion"]): raise Mismatch("P18 package mismatch")
    require_identity(ident,r.get("identity") if isinstance(r.get("identity"),Mapping) else {},"P18")
    return {"sha256":sha(path),"state":st}

def read_visual(path: Path|None,c:Mapping[str,Any],b:Mapping[str,Any])->dict[str,Any]:
    if path is None or not path.is_file(): raise Waiting(WAIT_VISUAL,"real P20 visual receipt missing")
    r=load(path)
    if r.get("schema")!=VISUAL_SCHEMA or r.get("version")!=1: raise Mismatch("visual receipt schema/version mismatch")
    if r.get("fixtureMode") is not False or r.get("promotionEligible") is not True or r.get("ownerVisualVerdict")!="PASS" or r.get("ownerAnswer")!="YES" or r.get("visualProof")!="OWNER_VISUAL_PASS": raise Waiting(WAIT_VISUAL,"visual receipt is not real promotion-eligible PASS")
    checks={"candidateSourceCommit":c["sourceCommit"],"packageVersion":c["packageVersion"],"candidateSha256":c["candidateSha256"],"candidateAttestationSha256":c["attestationSha256"],"acceptanceBundleSha256":b["sha256"]}
    for k,v in checks.items():
        if r.get(k)!=v: raise Mismatch(f"visual receipt mismatch {k}")
    if r.get("identity")!=b["identity"]: raise Mismatch("visual receipt identity mismatch")
    safety(r.get("safety"),"visual receipt",unmoved=True)
    if r["safety"].get("forcePushAllowed") is not False: raise Mismatch("visual receipt weakens no-force policy")
    return {"sha256":sha(path),"verdict":"PASS"}

def read_promotion(pp:Path|None,rp:Path|None,c:Mapping[str,Any],b:Mapping[str,Any],v:Mapping[str,Any])->dict[str,Any]:
    if pp is None or rp is None or not pp.is_file() or not rp.is_file(): raise Waiting(WAIT_PROMOTION,"P20 confirmed promotion artifacts missing")
    p,r=load(pp),load(rp)
    if p.get("schema")!=PLAN_SCHEMA or p.get("version")!=1 or p.get("state")!="READY": raise Mismatch("promotion plan schema/state mismatch")
    core=p.get("planCore") if isinstance(p.get("planCore"),Mapping) else {}; ph=canon_hash(core)
    if p.get("planHash")!=ph: raise Mismatch("promotion plan hash mismatch")
    want={"toCandidateCommit":c["sourceCommit"],"packageVersion":c["packageVersion"],"candidateSha256":c["candidateSha256"],"candidateAttestationSha256":c["attestationSha256"],"acceptanceBundleSha256":b["sha256"],"visualReceiptSha256":v["sha256"],"identity":b["identity"]}
    for k,x in want.items():
        if core.get(k)!=x: raise Mismatch(f"promotion plan mismatch {k}")
    old,target=commit(core.get("fromAlphaLiveCommit"),"promotion from"),commit(core.get("toCandidateCommit"),"promotion target")
    rb=core.get("rollback") if isinstance(core.get("rollback"),Mapping) else {}
    if old==target or rb.get("previousCommit")!=old or rb.get("preserveW1LastKnownGoodBehavior") is not True: raise Mismatch("rollback metadata mismatch")
    if core.get("compareAndSwapExpectedOld")!=old or core.get("fastForwardRequired") is not True or tuple(core.get("requiredW1Files") or ())!=REQUIRED_W1_FILES: raise Mismatch("promotion CAS/W1 contract mismatch")
    safety(core.get("safety"),"promotion plan")
    if core["safety"].get("forcePushAllowed") is not False or core["safety"].get("alphaLiveMovedAtPlan") is not False: raise Mismatch("promotion plan no-force invariant mismatch")
    if r.get("schema")!=PROMOTION_SCHEMA or r.get("version")!=1 or r.get("state")!="PROMOTED": raise Waiting(WAIT_PROMOTION,"promotion result is not PROMOTED")
    if r.get("planHash")!=ph or r.get("fromAlphaLiveCommit")!=old or r.get("toCandidateCommit")!=target or r.get("alphaLiveMoved") is not True or r.get("forcePushUsed") is not False or r.get("fastForwardOnly") is not True: raise Mismatch("promotion result mismatch")
    return {"planHash":ph,"planSha256":sha(pp),"resultSha256":sha(rp),"fromCommit":old,"targetCommit":target}

def git(repo:Path,*args:str)->subprocess.CompletedProcess[str]:
    return subprocess.run(["git","-C",str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def alpha_live(repo:Path,remote:str,branch:str)->str:
    cp=git(repo,"ls-remote","--heads",remote,f"refs/heads/{branch}")
    if cp.returncode: raise Waiting(WAIT_PROMOTION,f"cannot observe {remote}/{branch}")
    rows=[x.split() for x in cp.stdout.splitlines() if x.strip()]
    if len(rows)!=1: raise Waiting(WAIT_PROMOTION,"alpha-live missing/ambiguous")
    return commit(rows[0][0],"observed alpha-live")
def required_at(repo:Path,c:str)->list[str]: return [p for p in REQUIRED_W1_FILES if git(repo,"cat-file","-e",f"{c}:{p}").returncode]
def rollback(repo:Path,p:Mapping[str,Any])->dict[str,Any]:
    old,target=p["fromCommit"],p["targetCommit"]
    if old==target or git(repo,"cat-file","-e",f"{old}^{{commit}}").returncode or git(repo,"cat-file","-e",f"{target}^{{commit}}").returncode: raise Mismatch("rollback/target commit not resolvable")
    if required_at(repo,target) or required_at(repo,old): raise Mismatch("required W1 files missing at target/rollback")
    if git(repo,"merge-base","--is-ancestor",old,target).returncode: raise Mismatch("promotion is not fast-forward from rollback point")
    return {"previousCommit":old,"targetCommit":target,"requiredFilesAtTarget":True,"requiredFilesAtRollback":True,"fastForwardProven":True,"autoExecuted":False}
def parse_feedback(path:Path)->dict[str,str]:
    if not path.is_file(): return {}
    out={}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line:
            k,v=line.split("=",1); out.setdefault(k.strip(),v.strip())
    return out
def permanent(repo:Path,launcher:Path,feedback:Path,target:str,package:str)->dict[str,Any]:
    low=str(repo).replace("\\","/").lower()
    if "wof_alpha_staging" in low or "/owner_staging/" in low: raise Mismatch("P21 staging checkout cannot count as permanent W1 repo")
    if not (repo/".git").exists(): raise Waiting(WAIT_PERMANENT,f"permanent managed repo unavailable: {repo}")
    cp=git(repo,"rev-parse","--verify","HEAD")
    if cp.returncode: raise Waiting(WAIT_PERMANENT,"cannot read permanent managed HEAD")
    head=commit(cp.stdout.strip(),"managed HEAD")
    if head!=target: raise Waiting(WAIT_PERMANENT,f"permanent repo not converged: {head} != {target}")
    if required_at(repo,head): raise Mismatch("permanent managed release missing W1 files")
    if not launcher.is_file(): raise Waiting(WAIT_PERMANENT,f"permanent Desktop launcher missing: {launcher}")
    f=parse_feedback(feedback)
    for k in ("alphaLiveCommit","currentSha"):
        if f.get(k) and f[k].lower()!=target: raise Mismatch(f"W1 feedback {k} mismatch")
    if f.get("packageVersion") and f["packageVersion"]!=package: raise Mismatch("W1 feedback package mismatch")
    return {"managedHead":head,"managedRepo":str(repo.resolve()),"desktopLauncher":str(launcher.resolve()),"feedback":f}

def p22(path:Path|None,c:Mapping[str,Any],ident:Mapping[str,Any])->dict[str,Any]|None:
    if path is None or not path.is_file(): return None
    r=load(path); safety(r.get("safety"),"P22")
    for k,wants in (("candidateSourceCommit",c["sourceCommit"]),("sourceCommit",c["sourceCommit"]),("packageVersion",c["packageVersion"]),("candidateSha256",c["candidateSha256"])):
        if k in r and r.get(k) not in (None,wants): raise Mismatch(f"P22 mismatch {k}")
    if isinstance(r.get("identity"),Mapping): require_identity(ident,r["identity"],"P22")
    gaps=[]; matrix=r.get("coverageMatrix")
    if isinstance(r.get("coverageGaps"),list): gaps += [str(x) for x in r["coverageGaps"]]
    rows=matrix if isinstance(matrix,list) else [{"name":k,"status":v.get("status") if isinstance(v,Mapping) else v} for k,v in matrix.items()] if isinstance(matrix,Mapping) else []
    for row in rows:
        if isinstance(row,Mapping) and row.get("status") in ("NOT_OBSERVED","UNPROVEN_SIGNAL"): gaps.append(str(row.get("name") or row.get("category") or "unnamed-gap"))
    return {"sha256":sha(path),"coreAcceptance":r.get("coreAcceptance") or r.get("coreAcceptanceSummary"),"coverageGaps":sorted(set(gaps))}
def w3_hash(path:Path|None,ident:Mapping[str,Any])->tuple[str,str]:
    if path is None or not path.is_file(): raise Waiting(WAIT_W3,"explicit W3 live qualification artifact missing")
    r=load(path)
    if r.get("schema")=="wof-w3-long-qualification-latest-v1" and isinstance(r.get("qualificationJson"),str):
        q=Path(r["qualificationJson"]).expanduser(); path=q if q.is_absolute() else (path.parent/q).resolve(); r=load(path)
    if r.get("schema")!=W3_SCHEMA or r.get("status")!="PASS": raise Waiting(WAIT_W3,"explicit W3 live qualification is not PASS")
    if isinstance(r.get("captureIdentity"),Mapping): require_identity(ident,r["captureIdentity"],"W3")
    return sha(path),str(path.resolve())
def post_confirmation(path:Path|None,c:Mapping[str,Any],p:Mapping[str,Any],ident:Mapping[str,Any],perm:Mapping[str,Any],cov:Mapping[str,Any])->dict[str,Any]:
    if path is None or not path.is_file(): raise Waiting(WAIT_POST,"real post-promotion Owner confirmation missing")
    r=load(path)
    if r.get("schema")!=POST_SCHEMA or r.get("version")!=1: raise Mismatch("post-promotion confirmation schema/version mismatch")
    if r.get("fixtureMode") is not False: raise Waiting(WAIT_POST,"fixture confirmation cannot close Alpha V1")
    if r.get("realWofPostPromotionAcceptance")!="PASS" or r.get("ownerConfirmation")!="PASS": raise Waiting(WAIT_POST,"post-promotion real acceptance is not PASS")
    checks={"promotedCommit":p["targetCommit"],"managedRepoHead":perm["managedHead"],"packageVersion":c["packageVersion"],"candidateSha256":c["candidateSha256"],"promotionPlanHash":p["planHash"],"promotionResultSha256":p["resultSha256"]}
    for k,v in checks.items():
        if r.get(k)!=v: raise Mismatch(f"post-promotion confirmation mismatch {k}")
    if r.get("identity")!=ident: raise Mismatch("post-promotion confirmation identity mismatch")
    if r.get("p22EvidenceSha256") not in (None,cov["sha256"]): raise Mismatch("post-promotion confirmation P22 hash mismatch")
    safety(r.get("safety"),"post-promotion confirmation")
    return {"sha256":sha(path),"verdict":"PASS"}

def discover(root:Path,schema:str,predicate=lambda r:True)->Path|None:
    found=[]
    if root.is_dir():
        for path in sorted(root.glob("*.json")):
            try:r=load(path)
            except GateError:continue
            if r.get("schema")==schema and predicate(r): found.append(path.resolve())
    return found[0] if len(found)==1 else None

def atomic(path:Path,data:bytes)->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally: Path(tmp).unlink(missing_ok=True)

def waiting(state:str,reason:str,observed:str)->dict[str,Any]:
    core={"state":state,"reason":reason,"realWofPostPromotionAcceptance":"NOT_PROVEN","finalComplete":False,"safety":{"readOnly":True,"ramWrites":0,"inputInjection":False,"alphaLiveMovedByP23":False,"rollbackAutoExecuted":False}}
    return {"state":state,"verification":{"schema":VERIFY_SCHEMA,"version":1,"observedAtUtc":observed,"releaseMatchState":state,"projectCloseReadiness":state,"receiptCore":core,"receiptHash":canon_hash(core)},"closeBundle":None}
def verify(repo:Path,*,candidate_path:Path,attestation_path:Path,p17_path:Path,p16_path:Path,p18_path:Path,visual_path:Path|None,plan_path:Path|None,promotion_path:Path|None,observed_alpha:str|None,remote:str,branch:str,managed:Path,launcher:Path,feedback:Path,p22_path:Path|None=None,w3_path:Path|None=None,post_path:Path|None=None,observed_at:str|None=None)->dict[str,Any]:
    observed_at=observed_at or now(); c=read_candidate(candidate_path,attestation_path); b=read_bundle(p17_path,c); e16=read_p16(p16_path,c,b["identity"]); e18=read_p18(p18_path,c,b["identity"]); wh,ws=w3_hash(w3_path,b["identity"]); v=read_visual(visual_path,c,b); pr=read_promotion(plan_path,promotion_path,c,b,v)
    live=commit(observed_alpha,"observed alpha-live") if observed_alpha else alpha_live(repo,remote,branch)
    if live!=pr["targetCommit"]: raise Mismatch(f"current alpha-live {live} != promoted target {pr['targetCommit']}")
    rb=rollback(repo,pr); perm=permanent(managed,launcher,feedback,pr["targetCommit"],c["packageVersion"]); cov=p22(p22_path,c,b["identity"])
    if cov is None: raise Waiting(WAIT_POST,"P22 dynamic-state coverage evidence missing")
    post=post_confirmation(post_path,c,pr,b["identity"],perm,cov)
    core={"state":READY,"reason":"all exact release, permanent-channel, dynamic-state and post-promotion real gates are consistent","candidate":c,"alphaLive":{"beforeCommit":pr["fromCommit"],"afterCommit":pr["targetCommit"],"currentCommit":live},"promotion":{"planHash":pr["planHash"],"planSha256":pr["planSha256"],"resultSha256":pr["resultSha256"],"forcePushUsed":False,"fastForwardOnly":True},"ownerVisual":{"sha256":v["sha256"],"verdict":"PASS"},"evidence":{"w3":{"sha256":wh,"source":ws,"state":"PASS"},"p17":{"sha256":b["sha256"],"state":"READY_FOR_OWNER_VISUAL_CONFIRMATION"},"p16":e16,"p18":e18,"p22":cov},"identity":b["identity"],"permanentChannel":perm,"rollback":rb,"postPromotionOwnerConfirmation":post,"realWofPostPromotionAcceptance":"PASS","safety":{"readOnly":True,"ramWrites":0,"inputInjection":False,"legacySpatialFallback":False,"forcePushUsed":False,"alphaLiveMovedByP23":False,"rollbackAutoExecuted":False}}
    rh=canon_hash(core); verification={"schema":VERIFY_SCHEMA,"version":1,"observedAtUtc":observed_at,"releaseMatchState":RELEASE_MATCHED,"projectCloseReadiness":READY,"receiptCore":core,"receiptHash":rh}
    close_core={"finalState":FINAL,"releaseReceiptHash":rh,"promotedCommit":pr["targetCommit"],"packageVersion":c["packageVersion"],"candidateSha256":c["candidateSha256"],"attestationSha256":c["attestationSha256"],"managedRepoHead":perm["managedHead"],"rollbackCommit":rb["previousCommit"],"ownerVisualReceiptSha256":v["sha256"],"postPromotionConfirmationSha256":post["sha256"],"p22EvidenceSha256":cov["sha256"],"coverageGaps":cov["coverageGaps"],"safety":core["safety"]}
    close={"schema":CLOSE_SCHEMA,"version":1,"observedAtUtc":observed_at,"closeCore":close_core,"closeHash":canon_hash(close_core)}
    return {"state":FINAL,"verification":verification,"closeBundle":close}
def write_outputs(result:Mapping[str,Any],out:Path)->None:
    out.mkdir(parents=True,exist_ok=True); v=out/"ALPHA_POST_PROMOTION_VERIFICATION.json"; vm=v.with_suffix(".md"); atomic(v,(json.dumps(result["verification"],ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode())
    reason=result["verification"]["receiptCore"].get("reason",""); text=f"# Alpha V1 Post-Promotion Verification\n\n- State: **{result['state']}**\n- Reason: {reason}\n- Receipt hash: `{result['verification']['receiptHash']}`\n"
    atomic(vm,text.encode())
    cj=out/"ALPHA_V1_FINAL_CLOSE_BUNDLE.json"; cm=out/"ALPHA_V1_FINAL_CLOSE_BUNDLE.md"
    if result.get("closeBundle") is None: cj.unlink(missing_ok=True); cm.unlink(missing_ok=True)
    else: atomic(cj,(json.dumps(result["closeBundle"],ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()); atomic(cm,(text+f"- Final close hash: `{result['closeBundle']['closeHash']}`\n").encode())
def next_message(state:str)->str:
    return {WAIT_P19:"下一步：先确认 P19 最终候选与 attestation。",WAIT_W3:"下一步：完成一次 W3 有界正常游玩采样并得到真实 PASS。",WAIT_VISUAL:"下一步：P17 READY 后完成 P20 真实 Owner YES/PASS。",WAIT_PROMOTION:"下一步：由 P20 完成真实非强推 fast-forward promotion 并写 promotion result。",WAIT_PERMANENT:"下一步：运行现有 Desktop\\WOF_ALPHA_TEST.cmd，让永久 W1 仓库收敛到发布 commit。",WAIT_POST:"下一步：在永久通道完成真实发布后验收，并提供 P22 动态覆盖与 post-promotion Owner confirmation。",REJECTED:"下一步：先修复证据不一致；禁止继续 close 或猜测 PASS。",FINAL:"Alpha V1 全部真实发布与发布后证据一致，可关闭项目。"}.get(state,state)
def run(args:argparse.Namespace)->int:
    repo=args.repo_root.expanduser().resolve(); root=args.results_dir.expanduser().resolve(); out=args.output_dir.expanduser().resolve(); observed=args.observed_at or now()
    try:
        cp,ap=candidate_from_pointer(repo,args.candidate_pointer); c=read_candidate(cp,ap)
        p17=args.p17 or root/P17_NAME; bsha=sha(p17) if p17.is_file() else None
        visual=args.visual or discover(root,VISUAL_SCHEMA,lambda r:r.get("candidateSha256")==c["candidateSha256"] and (bsha is None or r.get("acceptanceBundleSha256")==bsha))
        plan=args.plan or discover(root,PLAN_SCHEMA,lambda r:isinstance(r.get("planCore"),Mapping) and r["planCore"].get("candidateSha256")==c["candidateSha256"])
        promotion=args.promotion or discover(root,PROMOTION_SCHEMA,lambda r:r.get("toCandidateCommit")==c["sourceCommit"])
        post=args.post or discover(root,POST_SCHEMA)
        result=verify(repo,candidate_path=cp,attestation_path=ap,p17_path=p17,p16_path=args.p16 or root/P16_NAME,p18_path=args.p18 or root/P18_NAME,visual_path=visual,plan_path=plan,promotion_path=promotion,observed_alpha=args.alpha_live,remote=args.remote,branch=args.branch,managed=args.managed.expanduser().resolve(),launcher=args.launcher.expanduser().resolve(),feedback=args.feedback.expanduser().resolve(),p22_path=args.p22 or root/P22_NAME,w3_path=args.w3 or root/W3_NAME,post_path=post,observed_at=observed)
        write_outputs(result,out); print(f"state={result['state']}\n{next_message(result['state'])}"); return 0
    except Waiting as e:
        result=waiting(e.state,str(e),observed); write_outputs(result,out); print(f"state={e.state}\n{next_message(e.state)}\nreason={e}"); return 2
    except Mismatch as e:
        result=waiting(REJECTED,str(e),observed); write_outputs(result,out); print(f"state={REJECTED}\n{next_message(REJECTED)}\nreason={e}"); return 4

# Stable names used by focused tests and downstream callers.
WAITING_FOR_P19_CANDIDATE=WAIT_P19; WAITING_FOR_W3_LIVE_PASS=WAIT_W3; WAITING_FOR_OWNER_VISUAL_PASS=WAIT_VISUAL; WAITING_FOR_PROMOTION=WAIT_PROMOTION; WAITING_FOR_PERMANENT_CHANNEL_CONFIRMATION=WAIT_PERMANENT; WAITING_FOR_POST_PROMOTION_ACCEPTANCE=WAIT_POST; REJECTED_EVIDENCE_MISMATCH=REJECTED; READY_TO_CLOSE=READY; ALPHA_V1_FINAL_COMPLETE=FINAL
DEFAULT_P17_NAME=P17_NAME; DEFAULT_P16_NAME=P16_NAME; DEFAULT_P18_NAME=P18_NAME; P22_DEFAULT_NAME=P22_NAME; DEFAULT_POST_CONFIRMATION=POST_NAME
P17_BUNDLE_SCHEMA=P17_SCHEMA; P20_RECEIPT_SCHEMA=VISUAL_SCHEMA; P20_PLAN_SCHEMA=PLAN_SCHEMA; P20_RESULT_SCHEMA=PROMOTION_SCHEMA; POST_ACCEPTANCE_SCHEMA=POST_SCHEMA
WaitingError=Waiting; MismatchError=Mismatch; _canonical_hash=canon_hash; _waiting_output=waiting
read_p22=p22; verify_permanent_channel=permanent
def verify_release(repo_root:Path,**kw):
    return verify(repo_root,candidate_path=kw['candidate_path'],attestation_path=kw['attestation_path'],p17_path=kw['p17_path'],p16_path=kw['p16_path'],p18_path=kw['p18_path'],visual_path=kw.get('visual_receipt_path'),plan_path=kw.get('promotion_plan_path'),promotion_path=kw.get('promotion_result_path'),observed_alpha=kw.get('observed_alpha_live'),remote=kw.get('remote','origin'),branch=kw.get('live_branch','alpha-live'),managed=kw['managed_repo'],launcher=kw['launcher'],feedback=kw['feedback_path'],p22_path=kw.get('p22_path'),w3_path=kw.get('w3_path'),post_path=kw.get('post_confirmation_path'),observed_at=kw.get('observed_at_utc'))

def parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="Alpha V1 P23 verification-only project-close harness"); p.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[2]); p.add_argument("--results-dir",type=Path,default=results_dir()); p.add_argument("--output-dir",type=Path,default=results_dir()); p.add_argument("--candidate-pointer",type=Path); p.add_argument("--p17",type=Path); p.add_argument("--p16",type=Path); p.add_argument("--p18",type=Path); p.add_argument("--p22",type=Path); p.add_argument("--w3",type=Path); p.add_argument("--visual",type=Path); p.add_argument("--plan",type=Path); p.add_argument("--promotion",type=Path); p.add_argument("--post",type=Path); p.add_argument("--remote",default="origin"); p.add_argument("--branch",default="alpha-live"); p.add_argument("--alpha-live"); p.add_argument("--managed",type=Path,default=managed_repo()); p.add_argument("--launcher",type=Path,default=desktop_launcher()); p.add_argument("--feedback",type=Path,default=feedback_path()); p.add_argument("--observed-at"); return p
def main(argv:Sequence[str]|None=None)->int: return run(parser().parse_args(argv))
if __name__=="__main__": raise SystemExit(main())
