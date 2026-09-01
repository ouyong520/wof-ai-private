from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "wof-unified-windows-live-proof-v1"
STOP_CONDITION = "UNIFIED LIVE PROOF READY \u2014 ONE OWNER WOF RUN REMAINS"
ADMISSION_MARKERS = (
    "World 921031 \u5df2\u786e\u8ba4 / Discovery V2 / \u53ea\u8bfb\u6a21\u5f0f",
    "World 921031 \u5df2\u786e\u8ba4 / \u53ea\u8bfb\u6a21\u5f0f",
)
FATAL_MARKER = "WOF-052L \u91c7\u96c6\u5668\u6ca1\u6709\u6b63\u5e38\u5b8c\u6210"
READINESS = {
    "pylaunch": "FIX READY - one real Windows proof remains",
    "browserFleet": "BROWSER FLEET DISCOVERY V2 READY",
    "recorder": "DISCOVERY V2 repository-ready",
    "longCapture": "READY FOR 10-ROOM LONG CAPTURE",
    "analysis": "repository-ready",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def local_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def choose_free_port(start: int = 9423, end: int = 9499) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                pass
    raise RuntimeError("no free localhost proof CDP port in 9423..9499")


def normalize_fleet(manifest: dict[str, Any] | None) -> dict[str, Any]:
    out = {
        "available": False,
        "browser": False,
        "page": False,
        "workerIndicator": False,
        "workerAuthority": "cheap-indicator-only",
        "world921031Authoritative": False,
        "readOnly": None,
        "ramWrites": None,
        "inputInjection": None,
        "windowWorkerReplacement": None,
        "detail": None,
        "instance": None,
    }
    if not manifest:
        return out
    rows = manifest.get("instances")
    row = rows[0] if isinstance(rows, list) and rows and isinstance(rows[0], dict) else {}
    st = row.get("status") if isinstance(row.get("status"), dict) else {}
    out.update({
        "available": bool(row),
        "browser": st.get("browser") == "OK",
        "page": st.get("page") == "OK",
        "workerIndicator": st.get("worker") == "OK",
        "workerAuthority": manifest.get("workerStatusAuthority"),
        "world921031Authoritative": bool(manifest.get("world921031IdentityAuthoritative")),
        "readOnly": manifest.get("readOnly"),
        "ramWrites": manifest.get("ramWrites"),
        "inputInjection": manifest.get("inputInjection"),
        "windowWorkerReplacement": manifest.get("windowWorkerReplacement"),
        "detail": st.get("detail") or st.get("error"),
        "instance": {
            "id": row.get("id"), "host": row.get("host"), "port": row.get("port"),
            "profileDir": row.get("profileDir"), "pid": row.get("pid"),
            "workerDiscovery": st.get("workerDiscovery"),
            "relatedTopologyCount": st.get("relatedTopologyCount"),
        } if row else None,
    })
    return out


def normalize_pylaunch(proof: dict[str, Any] | None) -> dict[str, Any]:
    out = {
        "available": False, "automatedPass": False, "browser": False, "page": False,
        "worker": False, "wasmHeap": False, "world921031": False, "readOnly": None,
        "ramWrites": None, "inputInjection": None, "worldSha256": None,
        "identityReason": None, "discoveryPath": None, "lastError": None,
        "targetTopology": None,
    }
    if not proof:
        return out
    c = proof.get("checks") if isinstance(proof.get("checks"), dict) else {}
    out.update({
        "available": True,
        "automatedPass": proof.get("automatedResult") == "PASS",
        "browser": c.get("Browser") == "OK",
        "page": c.get("WOF page") == "OK",
        "worker": c.get("Worker") == "OK",
        "wasmHeap": c.get("WASM / heap") == "OK",
        "world921031": c.get("World 921031") == "OK",
        "readOnly": proof.get("readOnly"),
        "ramWrites": proof.get("ramWrites"),
        "inputInjection": proof.get("inputInjection"),
        "worldSha256": proof.get("worldSha256"),
        "identityReason": proof.get("identityReason"),
        "discoveryPath": proof.get("discoveryPath"),
        "lastError": proof.get("lastError"),
        "targetTopology": proof.get("targetTopology"),
    })
    return out


@dataclass
class RecorderEvidence:
    admitted: bool = False
    admission_line: str | None = None
    fatal: bool = False
    fatal_line: str | None = None
    lines: list[str] = field(default_factory=list)

    def feed(self, line: str) -> None:
        text = line.strip()
        if not text:
            return
        self.lines.append(text)
        self.lines[:] = self.lines[-120:]
        if any(mark in text for mark in ADMISSION_MARKERS):
            self.admitted = True
            self.admission_line = text
        if FATAL_MARKER in text:
            self.fatal = True
            self.fatal_line = text


def safety_ok(fleet: dict[str, Any], pylaunch: dict[str, Any], recorder: RecorderEvidence) -> bool:
    return bool(
        fleet.get("readOnly") is True and fleet.get("ramWrites") == 0
        and fleet.get("inputInjection") is False and fleet.get("windowWorkerReplacement") is False
        and pylaunch.get("readOnly") is True and pylaunch.get("ramWrites") == 0
        and pylaunch.get("inputInjection") is False and recorder.admitted
    )


def automated_ready(fleet: dict[str, Any], pylaunch: dict[str, Any], recorder: RecorderEvidence) -> bool:
    return bool(
        fleet.get("browser") and fleet.get("page") and fleet.get("workerIndicator")
        and fleet.get("workerAuthority") == "cheap-indicator-only"
        and fleet.get("world921031Authoritative") is False
        and pylaunch.get("automatedPass") and pylaunch.get("world921031")
        and recorder.admitted and safety_ok(fleet, pylaunch, recorder)
    )


def build_status(*, run_id: str, run_dir: Path, fleet_manifest: dict[str, Any] | None,
                 pylaunch_proof: dict[str, Any] | None, recorder: RecorderEvidence,
                 playability: str, stage: str, blockers: list[str],
                 process_state: dict[str, Any] | None = None) -> dict[str, Any]:
    fleet = normalize_fleet(fleet_manifest)
    pylaunch = normalize_pylaunch(pylaunch_proof)
    auto = automated_ready(fleet, pylaunch, recorder)
    passed = auto and playability == "CONFIRMED"
    result = "PASS" if passed else ("BLOCKED" if blockers else "WAITING")
    summary = (
        "\u771f\u4eba\u77ed\u9a8c\u8bc1\u901a\u8fc7\uff1a\u5df2\u5177\u5907 10 \u623f\u95f4\u957f\u91c7\u96c6\u6761\u4ef6\u3002\u4e0d\u4f1a\u81ea\u52a8\u5f00\u59cb\u957f\u91c7\u96c6\u3002"
        if passed else
        "\u771f\u4eba\u77ed\u9a8c\u8bc1\u672a\u5b8c\u6210\uff1b\u5df2\u4fdd\u7559\u5df2\u53d6\u5f97\u8bc1\u636e\u3002"
        if blockers else
        "\u6b63\u5728\u7b49\u5f85 WOF / Worker / WASM / World 921031 / Recorder \u51c6\u5165\u3002"
    )
    safe = safety_ok(fleet, pylaunch, recorder)
    return {
        "schema": SCHEMA, "runId": run_id, "updatedAtUtc": utc_now(), "stage": stage,
        "repository": {"result": "PASS", "liveProofClaimed": False,
                       "readiness": READINESS, "stopCondition": STOP_CONDITION},
        "live": {
            "result": result, "automatedChecksReady": auto,
            "ownerPlayabilityConfirmation": playability,
            "fleetDiscoveryV2": fleet, "pylaunchAuthoritativeProof": pylaunch,
            "recorderDiscoveryV2Admission": {
                "admitted": recorder.admitted, "evidence": recorder.admission_line,
                "fatal": recorder.fatal, "fatalEvidence": recorder.fatal_line,
                "recentOutput": recorder.lines[-30:],
            },
            "safety": {"pass": safe, "readOnly": True if safe else None,
                       "ramWrites": 0 if safe else None,
                       "inputInjection": False if safe else None,
                       "workerReplacement": False, "blobWorker": False},
            "processes": process_state or {}, "blockers": blockers,
        },
        "overallResult": result, "tenRoomLongCaptureReady": passed,
        "longCaptureAutoStarted": False, "ownerSummaryZh": summary,
        "ownerReturn": {"json": str(run_dir / "UNIFIED_LIVE_PROOF_STATUS.json"),
                        "alternative": "\u6700\u7ec8\u4e2d\u6587\u72b6\u6001\u622a\u56fe"},
    }


def reader(proc: subprocess.Popen[str], prefix: str, evidence: RecorderEvidence | None,
           q: "queue.Queue[tuple[str, str]]") -> None:
    if proc.stdout is None:
        return
    for raw in proc.stdout:
        line = raw.rstrip("\r\n")
        if evidence is not None:
            evidence.feed(line)
        q.put((prefix, line))


def start_child(cmd: list[str], cwd: Path) -> subprocess.Popen[str]:
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0
    return subprocess.Popen(cmd, cwd=str(cwd), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", bufsize=1,
                            creationflags=flags)


def stop_child(proc: subprocess.Popen[str] | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        if os.name == "nt" and hasattr(signal, "CTRL_BREAK_EVENT"):
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            proc.wait(timeout=8)
            return
    except Exception:
        pass
    try:
        proc.terminate(); proc.wait(timeout=5)
    except Exception:
        try: proc.kill()
        except Exception: pass


def run_live(root: Path) -> int:
    fleet_dir = root / "parallel" / "BROWSER_FLEET"
    py_dir = root / "parallel" / "PYLAUNCH"
    rec_dir = root / "parallel" / "WOF052L_RECORDER"
    for p in (fleet_dir, py_dir, rec_dir):
        sys.path.insert(0, str(p))
    from fleet_owner_zh_cn import ChineseFleetManager

    local = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("TEMP") or ".")
    base = local / "WOF Future Danger" / "UnifiedLiveProof"
    run_id = f"{local_stamp()}-{uuid.uuid4().hex[:6]}"
    run_dir = base / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    status_path = run_dir / "UNIFIED_LIVE_PROOF_STATUS.json"
    latest = base / "UNIFIED_LIVE_PROOF_STATUS.json"
    manifest = run_dir / "fleet" / "instances.json"
    settings = run_dir / "fleet" / "settings.json"
    profiles = run_dir / "fleet" / "Profiles"
    pyproof = run_dir / "PYLAUNCH_WINDOWS_PROOF_STATUS.json"
    rec_out = run_dir / "recorder"
    evidence = RecorderEvidence(); blockers: list[str] = []
    q: "queue.Queue[tuple[str, str]]" = queue.Queue()
    playability = "NOT_READY"; pyproc = None; recproc = None; terminal = None

    class ProofFleet(ChineseFleetManager):
        def _profile_for(self, instance_id: int) -> Path:
            return profiles / f"Proof_{instance_id:02d}"

    mgr = ProofFleet(settings_path=settings, manifest_path=manifest, poll_seconds=1.0)
    mgr.settings.base_port = choose_free_port(); mgr.settings.browser = "auto"; mgr.settings.game_url = None
    mgr.settings.save(settings)

    def persist(stage: str) -> dict[str, Any]:
        value = build_status(run_id=run_id, run_dir=run_dir, fleet_manifest=load_json(manifest),
                             pylaunch_proof=load_json(pyproof), recorder=evidence,
                             playability=playability, stage=stage, blockers=list(blockers),
                             process_state={"launcherExitCode": pyproc.poll() if pyproc else None,
                                            "recorderExitCode": recproc.poll() if recproc else None,
                                            "fleetManifest": str(manifest)})
        atomic_write_json(status_path, value)
        try: shutil.copy2(status_path, latest)
        except OSError: pass
        return value

    print("\n============================================================")
    print("  WOF \u7edf\u4e00 Windows \u771f\u4eba\u77ed\u9a8c\u8bc1")
    print("============================================================")
    print("\u53ea\u8bfb\u6a21\u5f0f\uff1a\u5f00\u542f | RAM writes: 0 | input injection: none")
    print("\u4e0d\u9700\u8981 DevTools / Worker Console / \u7c98\u8d34 JavaScript\u3002")
    persist("STARTING")
    try:
        print("\u6b63\u5728\u542f\u52a8 1 \u4e2a\u4e13\u7528 WOF \u6d4f\u89c8\u5668\u623f\u95f4...")
        mgr.start(1); mgr.print_status(); persist("BROWSER_STARTED")
        pyproc = start_child([sys.executable, "-u", str(py_dir / "launcher.py"),
                              "--fleet-instance", "1", "--fleet-manifest", str(manifest),
                              "--no-tray", "--proof-json", str(pyproof)], py_dir)
        recproc = start_child([sys.executable, "-u", str(rec_dir / "owner_v2_zh_cn.py"),
                               "--output-dir", str(rec_out), "--fleet-manifest", str(manifest),
                               "--no-launch-browser"], rec_dir)
        threading.Thread(target=reader, args=(pyproc, "PYLAUNCH", None, q), daemon=True).start()
        threading.Thread(target=reader, args=(recproc, "RECORDER", evidence, q), daemon=True).start()
        print("\u8bf7\u5728\u4e13\u7528\u6d4f\u89c8\u5668\u4e2d\u6b63\u5e38\u8fdb\u5165\u4e00\u4e2a WOF \u623f\u95f4\uff0c\u5176\u4ed6\u68c0\u67e5\u81ea\u52a8\u5b8c\u6210\u3002")
        last = 0.0
        while True:
            while True:
                try: prefix, line = q.get_nowait()
                except queue.Empty: break
                if any(x in line for x in ("\u5df2\u786e\u8ba4", "\u5931\u8d25", "ERROR")):
                    print(f"[{prefix}] {line}")
            py = normalize_pylaunch(load_json(pyproof))
            if pyproc.poll() is not None and not py.get("automatedPass"):
                msg = f"PYLAUNCH exited early (code={pyproc.returncode})"
                if msg not in blockers: blockers.append(msg)
            if recproc.poll() is not None and not evidence.admitted:
                msg = f"Recorder exited early (code={recproc.returncode})"
                if msg not in blockers: blockers.append(msg)
            if evidence.fatal and evidence.fatal_line:
                msg = "Recorder fatal: " + evidence.fatal_line
                if msg not in blockers: blockers.append(msg)
            if time.monotonic() - last >= 2:
                f = normalize_fleet(load_json(manifest)); p = normalize_pylaunch(load_json(pyproof))
                print("\rBrowser:%s | Page:%s | Fleet Worker:%s | World:%s | Recorder:%s      " % (
                    "OK" if f["browser"] else "WAIT", "OK" if f["page"] else "WAIT",
                    "OK" if f["workerIndicator"] else "WAIT", "OK" if p["world921031"] else "WAIT",
                    "OK" if evidence.admitted else "WAIT"), end="", flush=True)
                last = time.monotonic()
            value = persist("LIVE_WAITING")
            if value["live"]["automatedChecksReady"]:
                print("\n\n\u81ea\u52a8\u53ea\u8bfb\u9a8c\u8bc1\u5168\u90e8\u901a\u8fc7\u3002")
                ans = input("\u5f53\u524d WOF \u623f\u95f4\u4ecd\u80fd\u6b63\u5e38\u8fd0\u884c\uff1f\u6b63\u5e38\u8f93\u5165 Y\uff0c\u5f02\u5e38\u8f93\u5165 N\uff1a").strip().lower()
                playability = "CONFIRMED" if ans in {"y", "yes", "\u662f", "\u6b63\u5e38"} else "FAILED"
                if playability == "FAILED": blockers.append("Owner confirmed gameplay abnormal")
                terminal = persist("COMPLETE" if playability == "CONFIRMED" else "BLOCKED")
                break
            if blockers:
                terminal = persist("BLOCKED"); break
            time.sleep(0.5)
    except KeyboardInterrupt:
        blockers.append("Owner interrupted live proof"); terminal = persist("INTERRUPTED")
    except Exception as exc:
        blockers.append(f"unified live proof error: {exc}"); terminal = persist("BLOCKED")
    finally:
        stop_child(recproc); stop_child(pyproc)
        try: mgr._stop.set(); mgr.stop_all()
        except Exception: pass

    final = terminal or persist("BLOCKED")
    # Do not recompute from the post-cleanup Fleet manifest; preserve terminal evidence.
    atomic_write_json(status_path, final)
    try: shutil.copy2(status_path, latest)
    except OSError: pass
    print("\n============================================================")
    print("PASS - 10-room long capture ready" if final["overallResult"] == "PASS" else "Live short proof not complete")
    print("long capture auto-start: NO")
    print("JSON: " + str(status_path))
    print("============================================================")
    try:
        if os.name == "nt": os.startfile(run_dir)  # type: ignore[attr-defined]
    except Exception: pass
    return 0 if final["overallResult"] == "PASS" else 2


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WOF unified Windows live proof")
    p.add_argument("--project-root", required=True)
    return p.parse_args()


def main() -> int:
    root = Path(parse_args().project_root).expanduser().resolve()
    required = [root / "parallel" / "PYLAUNCH" / "launcher.py",
                root / "parallel" / "BROWSER_FLEET" / "fleet_owner_zh_cn.py",
                root / "parallel" / "WOF052L_RECORDER" / "owner_v2_zh_cn.py"]
    if any(not p.is_file() for p in required):
        print("required WOF proof tools missing")
        return 3
    return run_live(root)


if __name__ == "__main__":
    raise SystemExit(main())
