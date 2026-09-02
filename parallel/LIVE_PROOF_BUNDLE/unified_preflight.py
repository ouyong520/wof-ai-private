from __future__ import annotations

import argparse, hashlib, json, os, re, subprocess, sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SCHEMA = "wof-unified-live-proof-preflight-v1"
DISCOVERY_CONTRACT_VERSION = "wof-discovery-v2-hardened-capabilities-v1"
GATE_SELECTOR_VERSION = "wof-unified-current-successor-gates-v1"
STOP_CONDITION = "UNIFIED LIVE PROOF PREFLIGHT HARDENING READY — OWNER NOT NEEDED FOR REPOSITORY CHECKS"
SNAPSHOT_MAX_AGE_SECONDS = 15 * 60
SNAPSHOT_FUTURE_TOLERANCE_SECONDS = 120
PASS, BLOCKED = "PASS", "BLOCKED"

PYLAUNCH_SUCCESSOR_MARKER = "PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED"
PYLAUNCH_SUCCESSOR_STAGE = "PYLAUNCH_STARTUP_ATTESTATION_QA_V1"
PYLAUNCH_SUCCESSOR_MD = "parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.md"
PYLAUNCH_SUCCESSOR_JSON = "parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.json"
PYLAUNCH_SUCCESSOR_CLAIM = "parallel/PM/STAGE_CLAIMS/PYLAUNCH_STARTUP_ATTESTATION_QA_V1.json"
PYLAUNCH_PINNED_PRODUCTION = (
    "parallel/PYLAUNCH/wof_launcher/browser.py",
    "parallel/PYLAUNCH/wof_launcher/monitor.py",
    "parallel/PYLAUNCH/wof_launcher/discovery_v2.py",
)
RECORDER_SUCCESSOR_MARKER = "PASS — RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA — READY FOR CURRENT-HEAD UNIFIED PREFLIGHT"
RECORDER_SUCCESSOR_STAGE = "UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1"
RECORDER_SUCCESSOR_MD = "parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.md"
RECORDER_SUCCESSOR_JSON = "parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.json"
RECORDER_SUCCESSOR_CLAIM = "parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1.json"
RECORDER_PINNED_PRODUCTION = "parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py"

@dataclass(frozen=True)
class RegressionSpec:
    component: str
    cwd: str
    entrypoint: str

REQUIRED_FILES = {
    "liveProof": (
        "parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py",
        "parallel/LIVE_PROOF_BUNDLE/unified_preflight.py",
        "parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py",
        "parallel/LIVE_PROOF_BUNDLE/test_unified_live_proof.py",
        "parallel/LIVE_PROOF_BUNDLE/test_unified_preflight.py",
        "parallel/LIVE_PROOF_BUNDLE/RUN_WOF_UNIFIED_LIVE_PROOF.cmd",
        "parallel/LIVE_PROOF_BUNDLE/FRESHNESS_FIX_STATUS.json",
    ),
    "browserFleet": (
        "parallel/BROWSER_FLEET/fleet_manager.py", "parallel/BROWSER_FLEET/fleet_discovery_v2.py",
        "parallel/BROWSER_FLEET/fleet_owner_zh_cn.py", "parallel/BROWSER_FLEET/DISCOVERY_CONTRACT.md",
        "parallel/BROWSER_FLEET/RESULT.md", "parallel/BROWSER_FLEET/tests/test_fleet_discovery_v2.py",
        "parallel/BROWSER_FLEET/tests/test_fleet_manager_v2.py",
    ),
    "pylaunch": (
        "parallel/PYLAUNCH/launcher.py", "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd",
        "parallel/PYLAUNCH/wof_launcher/discovery_v2.py", "parallel/PYLAUNCH/wof_launcher/cdp.py",
        "parallel/PYLAUNCH/wof_launcher/browser.py", "parallel/PYLAUNCH/wof_launcher/monitor.py",
        "parallel/PYLAUNCH/DISCOVERY_V2_HARDENING_RESULT.md",
        "parallel/PYLAUNCH/tests/test_discovery_v2.py", "parallel/PYLAUNCH/tests/test_endpoint_hardening.py",
        "parallel/PYLAUNCH/tests/test_parentframe_authority.py",
        PYLAUNCH_SUCCESSOR_MD, PYLAUNCH_SUCCESSOR_JSON, PYLAUNCH_SUCCESSOR_CLAIM,
    ),
    "recorder": (
        "parallel/WOF052L_RECORDER/owner_v2_zh_cn.py", "parallel/WOF052L_RECORDER/owner_zh_cn.py",
        "parallel/WOF052L_RECORDER/discovery_v2_sync.py", "parallel/WOF052L_RECORDER/hardening_v2.py",
        "parallel/WOF052L_RECORDER/DISCOVERY_V2_HARDENING_RESULT.md",
        "parallel/WOF052L_RECORDER/test_discovery_v2_sync.py", "parallel/WOF052L_RECORDER/test_fleet_recorder.py",
    ),
    "successorQa": (RECORDER_SUCCESSOR_MD, RECORDER_SUCCESSOR_JSON, RECORDER_SUCCESSOR_CLAIM),
}
REGRESSIONS = (
    RegressionSpec("liveProof", "parallel/LIVE_PROOF_BUNDLE", "test_unified_live_proof.py"),
    RegressionSpec("liveProof", "parallel/LIVE_PROOF_BUNDLE", "test_unified_preflight.py"),
    RegressionSpec("browserFleet", "parallel/BROWSER_FLEET", "tests/test_fleet_discovery_v2.py"),
    RegressionSpec("browserFleet", "parallel/BROWSER_FLEET", "tests/test_fleet_manager_v2.py"),
    RegressionSpec("pylaunch", "parallel/PYLAUNCH", "tests/test_discovery_v2.py"),
    RegressionSpec("pylaunch", "parallel/PYLAUNCH", "tests/test_endpoint_hardening.py"),
    RegressionSpec("pylaunch", "parallel/PYLAUNCH", "tests/test_parentframe_authority.py"),
    RegressionSpec("recorder", "parallel/WOF052L_RECORDER", "test_discovery_v2_sync.py"),
    RegressionSpec("recorder", "parallel/WOF052L_RECORDER", "test_fleet_recorder.py"),
)
STATUS_GATES = (
    ("browserFleet", "parallel/BROWSER_FLEET/RESULT.md", "BROWSER FLEET DISCOVERY V2 READY"),
    ("pylaunch", "parallel/PYLAUNCH/DISCOVERY_V2_HARDENING_RESULT.md", "PYLAUNCH DISCOVERY V2 HARDENING READY"),
    ("recorder", "parallel/WOF052L_RECORDER/DISCOVERY_V2_HARDENING_RESULT.md", "WOF052L RECORDER DISCOVERY V2 HARDENING READY"),
)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def _utc(value: Any):
    if not isinstance(value, str): return None
    try:
        d = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except ValueError: return None

def _text(path: Path):
    try: return path.read_text(encoding="utf-8")
    except OSError: return None

def _json(path: Path):
    try: v = json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as e: return None, f"读取失败：{e}"
    except ValueError as e: return None, f"JSON 格式错误：{e}"
    return (v, None) if isinstance(v, dict) else (None, "JSON 顶层必须是 object")

def _blob_sha(path: Path):
    try: data = path.read_bytes()
    except OSError as e: return None, f"读取 production blob 失败：{e}"
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest(), None

def _row(checks, component, name, ok, severity, detail, *, path=None, command=None, commit=None, tests=None):
    r = {"component": component, "check": name, "result": PASS if ok else BLOCKED,
         "severity": None if ok else severity, "detail": detail}
    for k, v in (("path", path), ("command", command), ("commit", commit), ("tests", tests)):
        if v is not None: r[k] = v
    checks.append(r)

def _current_block(text: str):
    pats = (r"^\s*(?:#+\s*)?(?:\*\*)?BLOCKED\s*[—-]", r"^\s*(?:#+\s*)?(?:\*\*)?SUPERSEDED(?:\s|\*|$)",
            r"^\s*(?:VERDICT|STATUS|STATE)\s*:\s*(?:\*\*)?(?:BLOCKED|SUPERSEDED)\b")
    for line in text.splitlines()[:100]:
        if any(re.search(p, line, re.I) for p in pats): return line.strip()[:500]
    return None

def _git_manifest(root: Path):
    try:
        p = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        sha = p.stdout.strip().lower()
        if p.returncode or not re.fullmatch(r"[0-9a-f]{40}", sha): return None, "本地目录没有可验证的 40 位 git HEAD"
        q = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", "parallel/LIVE_PROOF_BUNDLE",
                            "parallel/BROWSER_FLEET", "parallel/PYLAUNCH", "parallel/WOF052L_RECORDER"], capture_output=True, text=True, timeout=10)
        if q.returncode or q.stdout.strip(): return None, "相关 component 工作树不干净，不能证明同一 snapshot"
        return {"source":"local-git-head", "snapshotCommit":sha, "resolvedAtUtc":_now(),
                "components":{k:sha for k in ("liveProof","browserFleet","pylaunch","recorder")}}, None
    except (OSError, subprocess.SubprocessError) as e: return None, f"无法读取本地 git snapshot：{e}"

def _snapshot(root, manifest_path, checks):
    manifest, err = _json(manifest_path) if manifest_path else _git_manifest(root)
    if err or manifest is None:
        _row(checks, "snapshot", "snapshot-manifest", False, "P0", err or "snapshot manifest 不可读", path=str(manifest_path) if manifest_path else None)
        return None, None
    sha = str(manifest.get("snapshotCommit") or "").lower(); valid = bool(re.fullmatch(r"[0-9a-f]{40}", sha))
    _row(checks, "snapshot", "snapshot-commit", valid, "P0", f"snapshot commit={sha}" if valid else "snapshotCommit 不是 40 位 SHA", commit=sha if valid else None)
    if not valid: return None, manifest
    d = _utc(manifest.get("resolvedAtUtc")); age = (datetime.now(timezone.utc)-d).total_seconds() if d else None
    fresh = age is not None and -SNAPSHOT_FUTURE_TOLERANCE_SECONDS <= age <= SNAPSHOT_MAX_AGE_SECONDS
    _row(checks, "snapshot", "snapshot-freshness", fresh, "P0", f"snapshot age={round(age,1)}s" if fresh else f"snapshot stale/future：age={age}", commit=sha)
    comps = manifest.get("components") if isinstance(manifest.get("components"), dict) else {}
    mixed = [k for k in ("liveProof","browserFleet","pylaunch","recorder") if str(comps.get(k) or "").lower()!=sha]
    _row(checks, "snapshot", "single-component-commit", not mixed, "P0", "所有子组件同一 commit" if not mixed else "mixed component commits："+", ".join(mixed), commit=sha)
    return sha, manifest

def _required(root, checks, commit):
    for c, paths in REQUIRED_FILES.items():
        missing=[p for p in paths if not (root/p).is_file()]
        _row(checks,c,"required-files-and-entrypoints",not missing,"P0","required files present" if not missing else "缺少："+", ".join(missing),commit=commit)

def _successor_pylaunch(root, checks, commit):
    text = _text(root / PYLAUNCH_SUCCESSOR_MD)
    blocked = _current_block(text) if text is not None else None
    md_ok = text is not None and blocked is None and PYLAUNCH_SUCCESSOR_MARKER in text
    _row(checks, "pylaunch", "startup-attestation-successor-result-md", md_ok, "P1",
         blocked or ("current Startup Attestation successor PASS" if md_ok else "当前 Startup Attestation successor RESULT.md 缺失/PASS marker 不匹配"),
         path=PYLAUNCH_SUCCESSOR_MD, commit=commit)

    machine, err = _json(root / PYLAUNCH_SUCCESSOR_JSON)
    pins = machine.get("validatedProductBlobs") if isinstance(machine, dict) and isinstance(machine.get("validatedProductBlobs"), dict) else {}
    machine_ok = err is None and isinstance(machine, dict) and machine.get("schema") == "wof-pylqa-result-v1" and machine.get("stageId") == PYLAUNCH_SUCCESSOR_STAGE and machine.get("status") == PASS and machine.get("decision") == PYLAUNCH_SUCCESSOR_MARKER
    _row(checks, "pylaunch", "startup-attestation-successor-machine-result", machine_ok, "P1",
         "Startup Attestation machine PASS semantics valid" if machine_ok else (err or "Startup Attestation machine result schema/stage/PASS decision 不匹配"),
         path=PYLAUNCH_SUCCESSOR_JSON, commit=commit)

    claim, claim_err = _json(root / PYLAUNCH_SUCCESSOR_CLAIM)
    claim_ok = claim_err is None and isinstance(claim, dict) and claim.get("stageId") == PYLAUNCH_SUCCESSOR_STAGE and claim.get("state") == "COMPLETE" and claim.get("result") == PYLAUNCH_SUCCESSOR_MARKER
    _row(checks, "pylaunch", "startup-attestation-successor-claim", claim_ok, "P1",
         "successor claim COMPLETE + PASS semantics valid" if claim_ok else (claim_err or "Startup Attestation claim 不是 COMPLETE+PASS；不能仅凭 COMPLETE 放行"),
         path=PYLAUNCH_SUCCESSOR_CLAIM, commit=commit)

    mismatches=[]
    for rel in PYLAUNCH_PINNED_PRODUCTION:
        expected = pins.get(rel)
        actual, blob_err = _blob_sha(root / rel)
        if blob_err or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{40}", expected) or actual != expected:
            mismatches.append(f"{rel}: expected={expected!r}, current={actual!r}, error={blob_err!r}")
    _row(checks, "pylaunch", "startup-attestation-current-production-blobs", machine_ok and not mismatches, "P1",
         "Startup Attestation successor pins match current browser/monitor/discovery blobs" if machine_ok and not mismatches else "Startup Attestation successor production pin stale/missing："+"; ".join(mismatches or ["machine result invalid"]),
         path=PYLAUNCH_SUCCESSOR_JSON, commit=commit)

def _successor_recorder(root, checks, commit):
    text = _text(root / RECORDER_SUCCESSOR_MD)
    blocked = _current_block(text) if text is not None else None
    md_ok = text is not None and blocked is None and RECORDER_SUCCESSOR_MARKER in text
    _row(checks, "liveProof", "recorder-inflight-successor-result-md", md_ok, "P1",
         blocked or ("current Recorder in-flight atomicity successor PASS" if md_ok else "当前 Recorder in-flight successor RESULT.md 缺失/PASS marker 不匹配"),
         path=RECORDER_SUCCESSOR_MD, commit=commit)

    machine, err = _json(root / RECORDER_SUCCESSOR_JSON)
    prod = machine.get("production") if isinstance(machine, dict) and isinstance(machine.get("production"), dict) else {}
    safety = machine.get("safety") if isinstance(machine, dict) and isinstance(machine.get("safety"), dict) else {}
    machine_ok = err is None and isinstance(machine, dict) and machine.get("schema") == "wof-unified-live-proof-recorder-inflight-atomicity-fresh-qa-v1" and machine.get("stageId") == RECORDER_SUCCESSOR_STAGE and machine.get("result") == PASS and machine.get("stopCondition") == RECORDER_SUCCESSOR_MARKER and prod.get("path") == RECORDER_PINNED_PRODUCTION and safety.get("readOnly") is True and safety.get("ramWrites") == 0 and safety.get("inputInjection") is False and safety.get("longCaptureAutoStarted") is False and safety.get("ownerAction") == "NO"
    _row(checks, "liveProof", "recorder-inflight-successor-machine-result", machine_ok, "P1",
         "Recorder successor machine PASS + safety semantics valid" if machine_ok else (err or "Recorder successor machine result/safety semantics 不匹配"),
         path=RECORDER_SUCCESSOR_JSON, commit=commit)

    claim, claim_err = _json(root / RECORDER_SUCCESSOR_CLAIM)
    claim_ok = claim_err is None and isinstance(claim, dict) and claim.get("stageId") == RECORDER_SUCCESSOR_STAGE and claim.get("state") == "COMPLETE" and claim.get("stopCondition") == RECORDER_SUCCESSOR_MARKER
    _row(checks, "liveProof", "recorder-inflight-successor-claim", claim_ok, "P1",
         "successor claim COMPLETE + PASS semantics valid" if claim_ok else (claim_err or "Recorder successor claim 不是 COMPLETE+PASS；不能仅凭 COMPLETE 放行"),
         path=RECORDER_SUCCESSOR_CLAIM, commit=commit)

    expected = prod.get("blob")
    actual, blob_err = _blob_sha(root / RECORDER_PINNED_PRODUCTION)
    blob_ok = machine_ok and isinstance(expected, str) and bool(re.fullmatch(r"[0-9a-f]{40}", expected)) and actual == expected
    _row(checks, "liveProof", "recorder-inflight-current-production-blob", blob_ok, "P1",
         "Recorder successor pin matches current unified_live_proof.py" if blob_ok else f"Recorder successor production pin stale/missing：expected={expected!r}, current={actual!r}, error={blob_err!r}",
         path=RECORDER_PINNED_PRODUCTION, commit=commit)

def _statuses(root, checks, commit):
    for c, rel, marker in STATUS_GATES:
        t=_text(root/rel)
        if t is None: _row(checks,c,"required-result-status",False,"P1","required RESULT/status 缺失或不可读",path=rel,commit=commit); continue
        b=_current_block(t); ok=b is None and marker in t
        _row(checks,c,"required-result-status",ok,"P1",b or (f"required marker: {marker}" if ok else f"缺少 required PASS marker: {marker}"),path=rel,commit=commit)
    fixrel="parallel/LIVE_PROOF_BUNDLE/FRESHNESS_FIX_STATUS.json"; fix,e=_json(root/fixrel)
    if e: ok=False; detail=e
    else:
        f=fix.get("fixes") if isinstance(fix.get("fixes"),dict) else {}; v=fix.get("validation") if isinstance(fix.get("validation"),dict) else {}; comb=v.get("combined") if isinstance(v.get("combined"),dict) else {}
        ok=fix.get("state")=="COMPLETE" and comb.get("result")=="PASS" and f.get("readOnly") is True and f.get("ramWrites")==0 and f.get("inputInjection") is False and f.get("windowWorkerReplacement") is False and f.get("longCaptureAutoStarted") is False
        detail="freshness fix status + safety valid" if ok else "freshness fix status/safety 字段不匹配"
    _row(checks,"liveProof","freshness-fix-status-json",ok,"P1",detail,path=fixrel,commit=commit)
    _successor_pylaunch(root, checks, commit)
    _successor_recorder(root, checks, commit)

def _has(text, *markers): return text is not None and all(m in text for m in markers)

def _contracts(root, checks, commit):
    rel="parallel/BROWSER_FLEET/fleet_discovery_v2.py"; t=_text(root/rel); ok=_has(t,"Target.setAutoAttach","LIGHT_RUNTIME_PROBE","moduleOk","readOnly","ramWrites","inputInjection")
    _row(checks,"browserFleet","discovery-v2-capabilities",ok,"P1",DISCOVERY_CONTRACT_VERSION if ok else "Browser Fleet Discovery V2 capability 缺失",path=rel,commit=commit)
    rel="parallel/PYLAUNCH/wof_launcher/discovery_v2.py"; t=_text(root/rel) or ""; fn=re.search(r"def _worker_compatible\(.*?(?=\n\ndef |\Z)",t,re.S)
    ok=_has(t,"Target.setAutoAttach","Page.getFrameTree","parentFrameId","IDENTITY_PROBE","WORKER_TYPES") and bool(fn and "in WORKER_TYPES" in fn.group(0) and "return True" in fn.group(0))
    _row(checks,"pylaunch","discovery-v2-capabilities",ok,"P1",DISCOVERY_CONTRACT_VERSION if ok else "旧/不完整 Discovery：拒绝 direct-gstyphoon-only authority",path=rel,commit=commit)
    owner=_text(root/"parallel/WOF052L_RECORDER/owner_v2_zh_cn.py") or ""; sync=_text(root/"parallel/WOF052L_RECORDER/discovery_v2_sync.py") or ""; hard=_text(root/"parallel/WOF052L_RECORDER/hardening_v2.py") or ""
    ok=_has(owner+sync+hard,"discovery_v2_sync.install","hardening_v2.install","Target.setAutoAttach","parentFrameId","CROSS_PAGE_AMBIGUITY","runtime+identity are authority")
    _row(checks,"recorder","discovery-v2-capabilities",ok,"P1",DISCOVERY_CONTRACT_VERSION if ok else "Recorder hardened Discovery V2 capability 缺失",path="parallel/WOF052L_RECORDER/hardening_v2.py",commit=commit)

def _ux_safety(root, checks, commit):
    entries=("parallel/LIVE_PROOF_BUNDLE/RUN_WOF_UNIFIED_LIVE_PROOF.cmd","parallel/BROWSER_FLEET/fleet_owner_zh_cn.py","parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd","parallel/WOF052L_RECORDER/owner_zh_cn.py")
    bad=[p for p in entries if not (_text(root/p) and re.search(r"[\u3400-\u9fff]",_text(root/p) or ""))]
    _row(checks,"ownerUx","simplified-chinese-entrypoints",not bad,"P1","中文 owner entrypoints present" if not bad else "English-only/missing owner entry: "+", ".join(bad),commit=commit)
    reqs=(("browserFleet","parallel/BROWSER_FLEET/DISCOVERY_CONTRACT.md",('"readOnly": true','"ramWrites": 0','"inputInjection": false','"windowWorkerReplacement": false','"workerStatusAuthority": "cheap-indicator-only"','"world921031IdentityAuthoritative": false')),
          ("pylaunch","parallel/PYLAUNCH/DISCOVERY_V2_HARDENING_RESULT.md",('"readOnly": true','"ramWrites": 0','"inputInjection": false','"workerReplacement": false','"urlRewrite": false')),
          ("recorder","parallel/WOF052L_RECORDER/DISCOVERY_V2_HARDENING_RESULT.md",("readOnly=true","ramWrites=0","inputInjection=false","no `window.Worker` replacement")))
    for c,rel,marks in reqs:
        ok=_has(_text(root/rel),*marks); _row(checks,c,"safety-declarations",ok,"P0","readOnly / ramWrites=0 / inputInjection=false / no Worker replacement" if ok else "safety declaration mismatch",path=rel,commit=commit)

def _run_regression(root: Path, spec: RegressionSpec):
    cmd=[sys.executable,"-m","unittest","-v",spec.entrypoint]; env=dict(os.environ); env.update(PYTHONUTF8="1",PYTHONIOENCODING="utf-8")
    try:
        p=subprocess.run(cmd,cwd=str(root/spec.cwd),capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=180,env=env); out=(p.stdout or "")+"\n"+(p.stderr or ""); m=re.findall(r"Ran\s+(\d+)\s+tests?",out)
        tests=int(m[-1]) if m else len(re.findall(r"^\s*def test_",_text(root/spec.cwd/spec.entrypoint) or "",re.M))
        return {"returncode":p.returncode,"tests":tests,"output":out[-4000:],"command":" ".join(cmd)}
    except (OSError,subprocess.SubprocessError) as e: return {"returncode":125,"tests":0,"output":str(e),"command":" ".join(cmd)}

def _regressions(root, checks, commit, runner):
    total=passed=0
    for s in REGRESSIONS:
        rel=str(Path(s.cwd)/s.entrypoint)
        if not (root/rel).is_file(): _row(checks,s.component,"offline-regression",False,"P1","required regression entrypoint missing",path=rel,commit=commit,tests=0); continue
        r=runner(root,s); n=int(r.get("tests") or 0); total+=n; ok=r.get("returncode")==0 and n>0; passed+=int(ok)
        detail=f"offline regression PASS ({n} tests)" if ok else f"offline regression command failed rc={r.get('returncode')}；{str(r.get('output') or '')[-1200:]}"
        _row(checks,s.component,"offline-regression",ok,"P1",detail,path=rel,command=str(r.get("command") or s.entrypoint),commit=commit,tests=n)
    return total,passed

def _write(path: Path, value):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(tmp,path)

def default_status_path():
    return Path(os.environ.get("LOCALAPPDATA") or os.environ.get("TEMP") or ".")/"WOF Future Danger"/"UnifiedLiveProof"/"UNIFIED_PREFLIGHT_STATUS.json"

def run_preflight(root: Path, *, snapshot_manifest: Path|None=None, status_out: Path|None=None, regression_runner: Callable=_run_regression):
    root=root.expanduser().resolve(); checks=[]; commit,manifest=_snapshot(root,snapshot_manifest,checks); _required(root,checks,commit); _statuses(root,checks,commit); _contracts(root,checks,commit); _ux_safety(root,checks,commit); tests,passed=_regressions(root,checks,commit,regression_runner)
    blockers=[{"severity":r.get("severity") or "P1","component":r.get("component"),"check":r.get("check"),"commit":r.get("commit"),"path":r.get("path"),"command":r.get("command"),"detailZh":r.get("detail")} for r in checks if r.get("result")==BLOCKED]
    result=PASS if not blockers else BLOCKED; out=status_out or default_status_path(); summary="仓库侧预检全部通过；允许进入真人短验证。不会自动开始 10 房间长采集。" if result==PASS else "仓库侧预检已阻断；未启动 Browser，也不需要 Owner 进入 WOF。请先关闭 repository-side P0/P1 blocker。"
    status={"schema":SCHEMA,"gateSelectorVersion":GATE_SELECTOR_VERSION,"updatedAtUtc":_now(),"result":result,"stopCondition":STOP_CONDITION,"discoveryContractVersion":DISCOVERY_CONTRACT_VERSION,
            "snapshot":{"commit":commit,"source":manifest.get("source") if isinstance(manifest,dict) else None,"resolvedAtUtc":manifest.get("resolvedAtUtc") if isinstance(manifest,dict) else None,"sameCommitRequired":True},
            "checks":checks,"blockers":blockers,"regression":{"commands":len(REGRESSIONS),"commandsPassed":passed,"testsObserved":tests},
            "gates":{"repositoryChecksPassed":result==PASS,"browserLaunchAllowed":result==PASS,"ownerWofEntryAllowed":result==PASS,"liveStageAllowed":result==PASS,"longCaptureAutoStarted":False},
            "safety":{"readOnly":True,"ramWrites":0,"inputInjection":False,"windowWorkerReplacement":False},"ownerActionRequired":False,"ownerSummaryZh":summary,
            "remainingOnlyRealWindowsWofCanProve":["真实 Chrome/Edge loopback CDP endpoint","真实 WOF page/iframe/Worker/WASM/World 921031 topology 与精确身份","只读 probe 期间真实游戏可玩性","短 proof PASS 后仍不自动开始 10-room long capture"],"statusPath":str(out)}
    _write(out,status); return status

def main():
    a=argparse.ArgumentParser(description="WOF 统一真人验证 repository-side preflight"); a.add_argument("--project-root",required=True); a.add_argument("--snapshot-manifest"); a.add_argument("--status-out"); x=a.parse_args(); s=run_preflight(Path(x.project_root),snapshot_manifest=Path(x.snapshot_manifest).resolve() if x.snapshot_manifest else None,status_out=Path(x.status_out).resolve() if x.status_out else None)
    print("\n============================================================\n  WOF 统一真人验证 — 仓库侧预检\n============================================================"); print(s["ownerSummaryZh"]); print("Snapshot commit："+str(s["snapshot"]["commit"] or "UNKNOWN")); print(f"离线 regression：{s['regression']['commands']} 个命令 / {s['regression']['testsObserved']} 个测试")
    for b in s["blockers"]: print(f"- [{b['severity']}] {b['component']} / {b['check']}：{b['detailZh']}")
    print("JSON："+s["statusPath"]+"\n============================================================"); return 0 if s["result"]==PASS else 20

if __name__ == "__main__": raise SystemExit(main())
