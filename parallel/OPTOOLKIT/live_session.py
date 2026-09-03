from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def _package_version(root: Path) -> str | None:
    for p in (root / "PACKAGE_MANIFEST.json", root / "parallel" / "OWNER_ONECLICK" / "package_manifest.json"):
        value = _read_json(p)
        if value:
            v = value.get("packageVersion")
            return str(v) if v else None
    return None


def _extract_projection_result(status: dict[str, Any] | None) -> dict[str, Any] | None:
    if not status: return None
    alpha = status.get("alphaStatus") or status.get("alpha_status")
    if not isinstance(alpha, dict): return None
    recovery = alpha.get("projectionRecovery")
    if not isinstance(recovery, dict): return None
    result = recovery.get("proofResult")
    return result if isinstance(result, dict) else None


def _durable_live_evidence(status: dict[str, Any] | None) -> dict[str, Any]:
    value = status or {}; events = value.get("significantEvents")
    if not isinstance(events, list): events = []
    return {
        "lastAcceptedAuthority": value.get("lastAcceptedAuthority") if isinstance(value.get("lastAcceptedAuthority"), dict) else None,
        "lastAlphaFailure": value.get("lastAlphaFailure") if isinstance(value.get("lastAlphaFailure"), dict) else None,
        "lastCalibrationProgress": value.get("lastCalibrationProgress") if isinstance(value.get("lastCalibrationProgress"), dict) else None,
        "significantEvents": [x for x in events[-96:] if isinstance(x, dict)],
    }


def _safe_upload(root: Path, zip_path: Path, session_dir: Path) -> dict[str, Any]:
    uploader = root / "parallel" / "OWNER_ONECLICK" / "upload_live_evidence.py"
    if not uploader.is_file(): return {"attempted": False, "status": "LOCAL_ONLY_NO_REPOSITORY_DEFINED_SECURE_UPLOADER"}
    try:
        cp = subprocess.run([sys.executable, str(uploader), "--zip", str(zip_path), "--session-dir", str(session_dir)], cwd=str(uploader.parent), text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180, check=False, env=os.environ.copy())
    except Exception as exc:
        return {"attempted": True, "status": "UPLOAD_FAILED_LOCAL_ZIP_RETAINED", "detail": str(exc)}
    return {"attempted": True, "status": "UPLOADED" if cp.returncode == 0 else "UPLOAD_FAILED_LOCAL_ZIP_RETAINED", "returnCode": cp.returncode, "detail": (cp.stdout or cp.stderr or "")[-1000:]}


def _zip_session(session_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True); partial = zip_path.with_suffix(zip_path.suffix + ".partial")
    try:
        partial.unlink(missing_ok=True)
        with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(session_dir.rglob("*")):
                if p.is_file(): zf.write(p, arcname=p.relative_to(session_dir).as_posix())
        os.replace(partial, zip_path)
    finally:
        partial.unlink(missing_ok=True)


def run_session(root: Path, session_dir: Path) -> int:
    root=root.resolve(); session_dir=session_dir.resolve(); session_dir.mkdir(parents=True,exist_ok=True)
    results_root=session_dir.parent; packages=results_root/"packages"; zip_path=packages/f"WOF_LIVE_ACCEPTANCE_{session_dir.name}.zip"
    proof_json=session_dir/"WINDOWS_PROOF_STATUS.json"; stdout_path=session_dir/"launcher.stdout.txt"; stderr_path=session_dir/"launcher.stderr.txt"; launcher=root/"parallel"/"PYLAUNCH"/"launcher.py"
    started=datetime.now().astimezone().isoformat(timespec="seconds"); rc=127; launch_error=None
    try:
        with stdout_path.open("w",encoding="utf-8") as out, stderr_path.open("w",encoding="utf-8") as err:
            cp=subprocess.run([sys.executable,str(launcher),"--proof-json",str(proof_json),"--activate-alpha","--package-root",str(root)],cwd=str(launcher.parent),env=os.environ.copy(),stdout=out,stderr=err,check=False); rc=cp.returncode
    except Exception as exc:
        launch_error=str(exc); stderr_path.write_text((stderr_path.read_text(encoding="utf-8",errors="replace") if stderr_path.exists() else "")+"\n"+launch_error+"\n",encoding="utf-8")
    status=_read_json(proof_json); projection=_extract_projection_result(status); durable=_durable_live_evidence(status)
    if projection is not None: _write_json(session_dir/"PROJECTION_PROOF_RESULT.json",projection)
    if durable["lastCalibrationProgress"] is not None: _write_json(session_dir/"CALIBRATION_PROGRESS.json",durable["lastCalibrationProgress"])
    if durable["significantEvents"]: _write_json(session_dir/"SIGNIFICANT_EVENTS.json",{"schema":"wof-live-acceptance-significant-events-v1","events":durable["significantEvents"],"safety":SAFETY})
    final_state=str((status or {}).get("launcherState") or (status or {}).get("state") or "UNKNOWN")
    final_disconnected=final_state in {"ERROR","DISCONNECTED"} or not bool((status or {}).get("checks",{}).get("Browser")=="OK")
    had_significant=any((durable["lastAcceptedAuthority"],durable["lastAlphaFailure"],durable["lastCalibrationProgress"],durable["significantEvents"]))
    outcome="ENDED_WITH_RETAINED_SIGNIFICANT_LIVE_STATE" if final_disconnected and had_significant else ("ENDED_DISCONNECTED_WITHOUT_ACCEPTED_LIVE_STATE" if final_disconnected else "ENDED_WITH_LIVE_STATUS")
    summary={"schema":"wof-live-acceptance-auto-evidence-v3","startedAt":started,"endedAt":datetime.now().astimezone().isoformat(timespec="seconds"),"packageVersion":_package_version(root),"launcherReturnCode":rc,"launcherError":launch_error,"finalState":final_state,"finalSnapshotDisconnected":final_disconnected,"sessionOutcome":outcome,"projectionVerdict":projection.get("verdict") if projection else None,"projectionProofSchema":projection.get("schema") if projection else None,"lastAcceptedAuthority":durable["lastAcceptedAuthority"],"lastAlphaFailure":durable["lastAlphaFailure"],"lastCalibrationProgress":durable["lastCalibrationProgress"],"significantEventCount":len(durable["significantEvents"]),"partialEvidenceRetained":True,"authoritativeZipKind":"WOF_LIVE_ACCEPTANCE","authoritativeZipPath":str(zip_path),"genericWofResultsZipIsAuthoritativeLiveProof":False,"zipPath":str(zip_path),"safety":SAFETY}
    _write_json(session_dir/"SESSION_SUMMARY.json",summary)
    try:
        _zip_session(session_dir,zip_path); upload=_safe_upload(root,zip_path,session_dir)
    except Exception as exc:
        upload={"attempted":False,"status":"PACKAGING_FAILED_RAW_EVIDENCE_RETAINED","detail":str(exc)}
    summary["upload"]=upload; summary["zipReady"]=zip_path.is_file(); _write_json(session_dir/"SESSION_SUMMARY.json",summary)
    if zip_path.is_file():
        try:_zip_session(session_dir,zip_path)
        except Exception:pass
    for name in ("FINAL_ZIP.txt","AUTHORITATIVE_LIVE_ACCEPTANCE_ZIP.txt"):
        (session_dir/name).write_text(str(zip_path)+"\n",encoding="utf-8")
    return 0 if zip_path.is_file() else 4


def main() -> int:
    parser=argparse.ArgumentParser(description="WOF live acceptance auto evidence supervisor"); parser.add_argument("--root",required=True); parser.add_argument("--session-dir",required=True); args=parser.parse_args(); return run_session(Path(args.root),Path(args.session_dir))
if __name__=="__main__": raise SystemExit(main())
