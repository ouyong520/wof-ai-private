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
STOP_CONDITION = "UNIFIED LIVE PROOF READY — ONE OWNER WOF RUN REMAINS"
ADMISSION_MARKERS = (
    "World 921031 已确认 / Discovery V2 / 只读模式",
    "World 921031 已确认 / 只读模式",
)
FATAL_MARKERS = (
    "WOF-052L 采集器没有正常完成",
    "已安全拒绝采集",
)
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
    raise RuntimeError("没有可用的本机 Proof CDP 端口（9423..9499）")


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
    # Current authority. A fatal event explicitly revokes these fields.
    admitted: bool = False
    admission_line: str | None = None
    fatal: bool = False
    fatal_line: str | None = None
    generation: int = 0
    admission_generation: int | None = None
    fatal_generation: int | None = None

    # Historical evidence is retained for diagnostics but never satisfies readiness.
    ever_admitted: bool = False
    last_admission_line: str | None = None
    ever_fatal: bool = False
    last_fatal_line: str | None = None
    lines: list[str] = field(default_factory=list)

    @property
    def current_healthy(self) -> bool:
        return self.admitted and not self.fatal

    @property
    def current_health(self) -> str:
        if self.fatal:
            return "FATAL"
        if self.admitted:
            return "HEALTHY"
        return "WAITING"

    def feed(self, line: str) -> None:
        text = line.strip()
        if not text:
            return
        self.lines.append(text)
        self.lines[:] = self.lines[-120:]

        if any(mark in text for mark in ADMISSION_MARKERS):
            self.generation += 1
            self.admitted = True
            self.admission_line = text
            self.admission_generation = self.generation
            self.fatal = False
            self.fatal_line = None
            self.ever_admitted = True
            self.last_admission_line = text

        if any(mark in text for mark in FATAL_MARKERS):
            self.generation += 1
            self.fatal = True
            self.fatal_line = text
            self.fatal_generation = self.generation
            self.admitted = False
            self.admission_line = None
            self.admission_generation = None
            self.ever_fatal = True
            self.last_fatal_line = text


def normalize_process_health(process_state: dict[str, Any] | None) -> dict[str, Any]:
    health_known = process_state is not None
    state = dict(process_state or {})
    launcher_required = bool(state.get("launcherRequired", False))
    recorder_required = bool(state.get("recorderRequired", False))
    launcher_exit = state.get("launcherExitCode")
    recorder_exit = state.get("recorderExitCode")
    launcher_live = None if not launcher_required else launcher_exit is None
    recorder_live = None if not recorder_required else recorder_exit is None
    healthy = bool(
        health_known
        and (not launcher_required or launcher_live is True)
        and (not recorder_required or recorder_live is True)
    )
    state.update({
        "healthKnown": health_known,
        "launcherRequired": launcher_required,
        "recorderRequired": recorder_required,
        "launcherLive": launcher_live,
        "recorderLive": recorder_live,
        "healthy": healthy,
    })
    return state


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def current_blockers(blockers: list[str], recorder: RecorderEvidence,
                     process_state: dict[str, Any] | None) -> tuple[list[str], dict[str, Any]]:
    effective = list(blockers)
    process = normalize_process_health(process_state)
    if recorder.fatal:
        detail = recorder.fatal_line or recorder.last_fatal_line or "Recorder 当前处于 fatal 状态"
        _append_unique(effective, "Recorder 致命状态：" + detail)
    if process.get("launcherRequired") and process.get("launcherLive") is False:
        _append_unique(effective, f"PYLAUNCH 子进程已退出（code={process.get('launcherExitCode')}）")
    if process.get("recorderRequired") and process.get("recorderLive") is False:
        _append_unique(effective, f"Recorder 子进程已退出（code={process.get('recorderExitCode')}）")
    return effective, process


def safety_ok(fleet: dict[str, Any], pylaunch: dict[str, Any], recorder: RecorderEvidence) -> bool:
    return bool(
        fleet.get("readOnly") is True and fleet.get("ramWrites") == 0
        and fleet.get("inputInjection") is False and fleet.get("windowWorkerReplacement") is False
        and pylaunch.get("readOnly") is True and pylaunch.get("ramWrites") == 0
        and pylaunch.get("inputInjection") is False and recorder.current_healthy
    )


def automated_ready(fleet: dict[str, Any], pylaunch: dict[str, Any], recorder: RecorderEvidence,
                    process_state: dict[str, Any] | None = None,
                    blockers: list[str] | None = None) -> bool:
    effective_blockers, process = current_blockers(list(blockers or []), recorder, process_state)
    return bool(
        not effective_blockers and process.get("healthy") is True
        and fleet.get("browser") and fleet.get("page") and fleet.get("workerIndicator")
        and fleet.get("workerAuthority") == "cheap-indicator-only"
        and fleet.get("world921031Authoritative") is False
        and pylaunch.get("automatedPass") and pylaunch.get("world921031")
        and recorder.current_healthy and safety_ok(fleet, pylaunch, recorder)
    )


def build_status(*, run_id: str, run_dir: Path, fleet_manifest: dict[str, Any] | None,
                 pylaunch_proof: dict[str, Any] | None, recorder: RecorderEvidence,
                 playability: str, stage: str, blockers: list[str],
                 process_state: dict[str, Any] | None = None) -> dict[str, Any]:
    fleet = normalize_fleet(fleet_manifest)
    pylaunch = normalize_pylaunch(pylaunch_proof)
    effective_blockers, process = current_blockers(blockers, recorder, process_state)
    auto = automated_ready(fleet, pylaunch, recorder, process_state, effective_blockers)
    owner_prompt_eligible = auto and playability == "NOT_READY"
    passed = bool(not effective_blockers and auto and playability == "CONFIRMED")
    result = "BLOCKED" if effective_blockers else ("PASS" if passed else "WAITING")
    summary = (
        "真人短验证通过：已具备 10 房间长采集条件。不会自动开始长采集。"
        if passed else
        "真人短验证已阻断；已保留未受影响分支的正证据和精确 blocker。"
        if effective_blockers else
        "正在等待 WOF / Worker / WASM / World 921031 / Recorder 当前准入。"
    )
    safe = safety_ok(fleet, pylaunch, recorder)
    return {
        "schema": SCHEMA, "runId": run_id, "updatedAtUtc": utc_now(), "stage": stage,
        "repository": {"result": "PASS", "liveProofClaimed": False,
                       "readiness": READINESS, "stopCondition": STOP_CONDITION},
        "live": {
            "result": result, "automatedChecksReady": auto,
            "ownerPromptEligible": owner_prompt_eligible,
            "ownerPlayabilityConfirmation": playability,
            "fleetDiscoveryV2": fleet, "pylaunchAuthoritativeProof": pylaunch,
            "recorderDiscoveryV2Admission": {
                "admitted": recorder.admitted, "evidence": recorder.admission_line,
                "fatal": recorder.fatal, "fatalEvidence": recorder.fatal_line,
                "currentHealth": recorder.current_health,
                "generation": recorder.generation,
                "admissionGeneration": recorder.admission_generation,
                "fatalGeneration": recorder.fatal_generation,
                "history": {
                    "everAdmitted": recorder.ever_admitted,
                    "lastAdmissionEvidence": recorder.last_admission_line,
                    "everFatal": recorder.ever_fatal,
                    "lastFatalEvidence": recorder.last_fatal_line,
                },
                "recentOutput": recorder.lines[-30:],
            },
            "safety": {"pass": safe, "readOnly": True if safe else None,
                       "ramWrites": 0 if safe else None,
                       "inputInjection": False if safe else None,
                       "workerReplacement": False, "blobWorker": False},
            "processes": process, "blockers": effective_blockers,
        },
        "overallResult": result, "tenRoomLongCaptureReady": passed,
        "longCaptureAutoStarted": False, "ownerSummaryZh": summary,
        "ownerReturn": {"json": str(run_dir / "UNIFIED_LIVE_PROOF_STATUS.json"),
                        "alternative": "最终中文状态截图"},
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
        try:
            proc.kill()
        except Exception:
            pass


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
    evidence = RecorderEvidence()
    blockers: list[str] = []
    q: "queue.Queue[tuple[str, str]]" = queue.Queue()
    playability = "NOT_READY"
    pyproc = None
    recproc = None
    terminal = None

    class ProofFleet(ChineseFleetManager):
        def _profile_for(self, instance_id: int) -> Path:
            return profiles / f"Proof_{instance_id:02d}"

    mgr = ProofFleet(settings_path=settings, manifest_path=manifest, poll_seconds=1.0)
    mgr.settings.base_port = choose_free_port()
    mgr.settings.browser = "auto"
    mgr.settings.game_url = None
    mgr.settings.save(settings)

    def process_snapshot() -> dict[str, Any]:
        return {
            "launcherRequired": pyproc is not None,
            "recorderRequired": recproc is not None,
            "launcherExitCode": pyproc.poll() if pyproc else None,
            "recorderExitCode": recproc.poll() if recproc else None,
            "fleetManifest": str(manifest),
        }

    def observe_failures() -> None:
        if pyproc is not None and pyproc.poll() is not None:
            _append_unique(blockers, f"PYLAUNCH 子进程已退出（code={pyproc.returncode}）")
        if recproc is not None and recproc.poll() is not None:
            _append_unique(blockers, f"Recorder 子进程已退出（code={recproc.returncode}）")
        if evidence.fatal:
            detail = evidence.fatal_line or evidence.last_fatal_line or "未知 fatal"
            _append_unique(blockers, "Recorder 致命状态：" + detail)

    def persist(stage: str) -> dict[str, Any]:
        value = build_status(run_id=run_id, run_dir=run_dir, fleet_manifest=load_json(manifest),
                             pylaunch_proof=load_json(pyproof), recorder=evidence,
                             playability=playability, stage=stage, blockers=list(blockers),
                             process_state=process_snapshot())
        atomic_write_json(status_path, value)
        try:
            shutil.copy2(status_path, latest)
        except OSError:
            pass
        return value

    print("\n============================================================")
    print("  WOF 统一 Windows 真人短验证")
    print("============================================================")
    print("只读模式：开启 | RAM writes: 0 | input injection: none")
    print("不需要 DevTools / Worker Console / 粘贴 JavaScript。")
    persist("STARTING")
    try:
        print("正在启动 1 个专用 WOF 浏览器房间...")
        mgr.start(1)
        mgr.print_status()
        persist("BROWSER_STARTED")
        pyproc = start_child([sys.executable, "-u", str(py_dir / "launcher.py"),
                              "--fleet-instance", "1", "--fleet-manifest", str(manifest),
                              "--no-tray", "--proof-json", str(pyproof)], py_dir)
        recproc = start_child([sys.executable, "-u", str(rec_dir / "owner_v2_zh_cn.py"),
                               "--output-dir", str(rec_out), "--fleet-manifest", str(manifest),
                               "--no-launch-browser"], rec_dir)
        threading.Thread(target=reader, args=(pyproc, "PYLAUNCH", None, q), daemon=True).start()
        threading.Thread(target=reader, args=(recproc, "RECORDER", evidence, q), daemon=True).start()
        print("请在专用浏览器中正常进入一个 WOF 房间，其他检查自动完成。")
        last = 0.0
        while True:
            while True:
                try:
                    prefix, line = q.get_nowait()
                except queue.Empty:
                    break
                if any(x in line for x in ("已确认", "失败", "ERROR", "拒绝")):
                    print(f"[{prefix}] {line}")

            observe_failures()
            if time.monotonic() - last >= 2:
                f = normalize_fleet(load_json(manifest))
                p = normalize_pylaunch(load_json(pyproof))
                print("\rBrowser:%s | Page:%s | Fleet Worker:%s | World:%s | Recorder:%s      " % (
                    "OK" if f["browser"] else "WAIT", "OK" if f["page"] else "WAIT",
                    "OK" if f["workerIndicator"] else "WAIT", "OK" if p["world921031"] else "WAIT",
                    "OK" if evidence.current_healthy else "WAIT"), end="", flush=True)
                last = time.monotonic()

            value = persist("LIVE_WAITING")
            if value["live"]["ownerPromptEligible"]:
                # Re-check immediately before asking so a just-exited child cannot rely on stale PASS.
                observe_failures()
                value = persist("PLAYABILITY_GATE")
                if not value["live"]["ownerPromptEligible"]:
                    terminal = persist("BLOCKED")
                    break
                print("\n\n自动只读验证当前全部通过。")
                ans = input("当前 WOF 房间仍能正常运行？正常输入 Y，异常输入 N：").strip().lower()
                playability = "CONFIRMED" if ans in {"y", "yes", "是", "正常"} else "FAILED"
                if playability == "FAILED":
                    _append_unique(blockers, "Owner 确认游戏运行异常")
                # Any automatic lane may regress while the owner is answering. Re-check all current state.
                observe_failures()
                recheck = persist("FINAL_RECHECK")
                if playability == "CONFIRMED" and not recheck["live"]["automatedChecksReady"]:
                    _append_unique(blockers, "Owner 确认期间自动检查不再保持当前 PASS")
                terminal = persist("COMPLETE" if playability == "CONFIRMED" and not blockers else "BLOCKED")
                break
            if value["live"]["blockers"]:
                terminal = persist("BLOCKED")
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        _append_unique(blockers, "Owner 中断了真人短验证")
        terminal = persist("INTERRUPTED")
    except Exception as exc:
        _append_unique(blockers, f"统一真人短验证错误：{exc}")
        terminal = persist("BLOCKED")
    finally:
        stop_child(recproc)
        stop_child(pyproc)
        try:
            mgr._stop.set()
            mgr.stop_all()
        except Exception:
            pass

    final = terminal or persist("BLOCKED")
    # Do not recompute from the post-cleanup Fleet manifest; preserve terminal evidence.
    atomic_write_json(status_path, final)
    try:
        shutil.copy2(status_path, latest)
    except OSError:
        pass
    print("\n============================================================")
    print("PASS - 已具备 10 房间长采集条件" if final["overallResult"] == "PASS" else "真人短验证未通过")
    print("自动开始长采集：否")
    print("JSON：" + str(status_path))
    print("============================================================")
    try:
        if os.name == "nt":
            os.startfile(run_dir)  # type: ignore[attr-defined]
    except Exception:
        pass
    return 0 if final["overallResult"] == "PASS" else 2


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WOF 统一 Windows 真人短验证")
    p.add_argument("--project-root", required=True)
    return p.parse_args()


def main() -> int:
    root = Path(parse_args().project_root).expanduser().resolve()
    required = [root / "parallel" / "PYLAUNCH" / "launcher.py",
                root / "parallel" / "BROWSER_FLEET" / "fleet_owner_zh_cn.py",
                root / "parallel" / "WOF052L_RECORDER" / "owner_v2_zh_cn.py"]
    if any(not p.is_file() for p in required):
        print("缺少统一真人短验证所需的 WOF 工具文件")
        return 3
    return run_live(root)


if __name__ == "__main__":
    raise SystemExit(main())
