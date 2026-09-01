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
RECORDER_ADMISSION_MARKERS = (
    "World 921031 已确认 / Discovery V2 / 只读模式",
    "World 921031 已确认 / 只读模式",
)
FATAL_RECORDER_MARKERS = (
    "WOF-052L 采集器没有正常完成",
    "已安全拒绝采集",
)
REPOSITORY_READINESS = {
    "pylaunch": "FIX READY — one real Windows proof remains",
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
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None

def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)

def choose_free_port(start: int = 9423, end: int = 9499) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("没有可用的本机 WOF proof CDP 端口（9423-9499）。")

def normalize_fleet(manifest: dict[str, Any] | None) -> dict[str, Any]:
    base = {
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
        return base
    rows = manifest.get("instances")
    row = rows[0] if isinstance(rows, list) and rows and isinstance(rows[0], dict) else {}
    status = row.get("status") if isinstance(row.get("status"), dict) else {}
    base.update(
        {
            "available": bool(row),
            "browser": status.get("browser") == "OK",
            "page": status.get("page") == "OK",
            "workerIndicator": status.get("worker") == "OK",
            "workerAuthority": manifest.get("workerStatusAuthority"),
            "world921031Authoritative": bool(manifest.get("world921031IdentityAuthoritative")),
            "readOnly": manifest.get("readOnly"),
            "ramWrites": manifest.get("ramWrites"),
            "inputInjection": manifest.get("inputInjection"),
            "windowWorkerReplacement": manifest.get("windowWorkerReplacement"),
            "detail": status.get("detail") or status.get("error"),
            "instance": {
                "id": row.get("id"),
                "host": row.get("host"),
                "port": row.get("port"),
                "profileDir": row.get("profileDir"),
                "pid": row.get("pid"),
                "workerDiscovery": status.get("workerDiscovery"),
                "relatedTopologyCount": status.get("relatedTopologyCount"),
            } if row else None,
        }
    )
    return base

def normalize_pylaunch(proof: dict[str, Any] | None) -> dict[str, Any]:
    base = {
        "available": False,
        "automatedPass": False,
        "browser": False,
        "page": False,
        "worker": False,
        "wasmHeap": False,
        "world921031": False,
        "readOnly": None,
        "ramWrites": None,
        "inputInjection": None,
        "worldSha256": None,
        "identityReason": None,
        "discoveryPath": None,
        "lastError": None,
        "targetTopology": None,
    }
    if not proof:
        return base
    checks = proof.get("checks") if isinstance(proof.get("checks"), dict) else {}
    base.update(
        {
            "available": True,
            "automatedPass": proof.get("automatedResult") == "PASS",
            "browser": checks.get("Browser") == "OK",
            "page": checks.get("WOF page") == "OK",
            "worker": checks.get("Worker") == "OK",
            "wasmHeap": checks.get("WASM / heap") == "OK",
            "world921031": checks.get("World 921031") == "OK",
            "readOnly": proof.get("readOnly"),
            "ramWrites": proof.get("ramWrites"),
            "inputInjection": proof.get("inputInjection"),
            "worldSha256": proof.get("worldSha256"),
            "identityReason": proof.get("identityReason"),
            "discoveryPath": proof.get("discoveryPath"),
            "lastError": proof.get("lastError"),
            "targetTopology": proof.get("targetTopology"),
        }
    )
    return base

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
        if len(self.lines) > 120:
            del self.lines[:-120]
        if any(marker in text for marker in RECORDER_ADMISSION_MARKERS):
            self.admitted = True
            self.admission_line = text
        if any(marker in text for marker in FATAL_RECORDER_MARKERS):
            self.fatal = True
            self.fatal_line = text

def safety_ok(fleet: dict[str, Any], pylaunch: dict[str, Any], recorder: RecorderEvidence) -> bool:
    return bool(
        fleet.get("readOnly") is True
        and fleet.get("ramWrites") == 0
        and fleet.get("inputInjection") is False
        and fleet.get("windowWorkerReplacement") is False
        and pylaunch.get("readOnly") is True
        and pylaunch.get("ramWrites") == 0
        and pylaunch.get("inputInjection") is False
        and recorder.admitted
    )

def automated_ready(fleet: dict[str, Any], pylaunch: dict[str, Any], recorder: RecorderEvidence) -> bool:
    return bool(
        fleet.get("browser")
        and fleet.get("page")
        and fleet.get("workerIndicator")
        and fleet.get("workerAuthority") == "cheap-indicator-only"
        and fleet.get("world921031Authoritative") is False
        and pylaunch.get("automatedPass")
        and pylaunch.get("world921031")
        and recorder.admitted
        and safety_ok(fleet, pylaunch, recorder)
    )

def build_status(
    *,
    run_id: str,
    run_dir: Path,
    fleet_manifest: dict[str, Any] | None,
    pylaunch_proof: dict[str, Any] | None,
    recorder: RecorderEvidence,
    playability: str,
    stage: str,
    blockers: list[str],
    process_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fleet = normalize_fleet(fleet_manifest)
    pylaunch = normalize_pylaunch(pylaunch_proof)
    auto_ready = automated_ready(fleet, pylaunch, recorder)
    live_pass = auto_ready and playability == "CONFIRMED"
    if live_pass:
        result = "PASS"
        summary = "真人短验证通过：已具备 10 房间长采集条件。不会自动开始长采集。"
    elif blockers:
        result = "BLOCKED"
        summary = "真人短验证未完成；已保留所有已取得证据。请只返回这个 JSON 或状态窗口截图。"
    else:
        result = "WAITING"
        summary = "正在等待 WOF 页面 / Worker / WASM / World 921031 / Recorder 准入。游戏本身不受影响。"
    return {
        "schema": SCHEMA,
        "runId": run_id,
        "updatedAtUtc": utc_now(),
        "stage": stage,
        "repository": {
            "result": "PASS",
            "liveProofClaimed": False,
            "readiness": REPOSITORY_READINESS,
            "stopCondition": STOP_CONDITION,
        },
        "live": {
            "result": result,
            "automatedChecksReady": auto_ready,
            "ownerPlayabilityConfirmation": playability,
            "fleetDiscoveryV2": fleet,
            "pylaunchAuthoritativeProof": pylaunch,
            "recorderDiscoveryV2Admission": {
                "admitted": recorder.admitted,
                "evidence": recorder.admission_line,
                "fatal": recorder.fatal,
                "fatalEvidence": recorder.fatal_line,
                "recentOutput": recorder.lines[-30:],
            },
            "safety": {
                "pass": safety_ok(fleet, pylaunch, recorder),
                "readOnly": True if safety_ok(fleet, pylaunch, recorder) else None,
                "ramWrites": 0 if safety_ok(fleet, pylaunch, recorder) else None,
                "inputInjection": False if safety_ok(fleet, pylaunch, recorder) else None,
                "workerReplacement": False,
                "blobWorker": False,
            },
            "processes": process_state or {},
            "blockers": blockers,
        },
        "overallResult": result,
        "tenRoomLongCaptureReady": live_pass,
        "longCaptureAutoStarted": False,
        "ownerSummaryZh": summary,
        "ownerReturn": {
            "json": str(run_dir / "UNIFIED_LIVE_PROOF_STATUS.json"),
            "alternative": "一张包含最终中文状态的截图",
        },
    }

def reader_thread(proc: subprocess.Popen[str], prefix: str, evidence: RecorderEvidence | None, out_queue: "queue.Queue[tuple[str, str]]") -> None:
    stream = proc.stdout
    if stream is None:
        return
    for raw in stream:
        line = raw.rstrip("\r\n")
        if evidence is not None:
            evidence.feed(line)
        out_queue.put((prefix, line))

def start_child(command: list[str], cwd: Path) -> subprocess.Popen[str]:
    flags = 0
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return subprocess.Popen(
        command,
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        creationflags=flags,
    )

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
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

def add_paths(project_root: Path) -> tuple[Path, Path, Path]:
    fleet_dir = project_root / "parallel" / "BROWSER_FLEET"
    pylaunch_dir = project_root / "parallel" / "PYLAUNCH"
    recorder_dir = project_root / "parallel" / "WOF052L_RECORDER"
    for path in (fleet_dir, pylaunch_dir, recorder_dir):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    return fleet_dir, pylaunch_dir, recorder_dir

def find_localappdata() -> Path:
    value = os.environ.get("LOCALAPPDATA")
    return Path(value) if value else Path(os.environ.get("TEMP", ".")) / "WOF_Future_Danger"

def run_live(project_root: Path) -> int:
    fleet_dir, pylaunch_dir, recorder_dir = add_paths(project_root)
    from fleet_owner_zh_cn import ChineseFleetManager

    base_root = find_localappdata() / "WOF Future Danger" / "UnifiedLiveProof"
    run_id = f"{local_stamp()}-{uuid.uuid4().hex[:6]}"
    run_dir = base_root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    status_path = run_dir / "UNIFIED_LIVE_PROOF_STATUS.json"
    stable_latest = base_root / "UNIFIED_LIVE_PROOF_STATUS.json"
    manifest_path = run_dir / "fleet" / "instances.json"
    settings_path = run_dir / "fleet" / "settings.json"
    profile_root = run_dir / "fleet" / "Profiles"
    pylaunch_proof_path = run_dir / "PYLAUNCH_WINDOWS_PROOF_STATUS.json"
    recorder_output = run_dir / "recorder"
    output_queue: "queue.Queue[tuple[str, str]]" = queue.Queue()
    recorder_evidence = RecorderEvidence()
    blockers: list[str] = []
    playability = "NOT_READY"
    launcher_proc: subprocess.Popen[str] | None = None
    recorder_proc: subprocess.Popen[str] | None = None

    class UnifiedProofFleetManager(ChineseFleetManager):
        def _profile_for(self, instance_id: int) -> Path:
            return profile_root / f"Proof_{instance_id:02d}"

    manager = UnifiedProofFleetManager(
        settings_path=settings_path,
        manifest_path=manifest_path,
        poll_seconds=1.0,
    )
    manager.settings.base_port = choose_free_port()
    manager.settings.browser = "auto"
    manager.settings.game_url = None
    manager.settings.save(settings_path)

    def persist(stage: str) -> dict[str, Any]:
        payload = build_status(
            run_id=run_id,
            run_dir=run_dir,
            fleet_manifest=load_json(manifest_path),
            pylaunch_proof=load_json(pylaunch_proof_path),
            recorder=recorder_evidence,
            playability=playability,
            stage=stage,
            blockers=list(blockers),
            process_state={
                "launcherExitCode": launcher_proc.poll() if launcher_proc else None,
                "recorderExitCode": recorder_proc.poll() if recorder_proc else None,
                "fleetManifest": str(manifest_path),
            },
        )
        atomic_write_json(status_path, payload)
        try:
            shutil.copy2(status_path, stable_latest)
        except OSError:
            pass
        return payload

    print()
    print("============================================================")
    print("  WOF 统一 Windows 真人短验证")
    print("============================================================")
    print("只读模式：开启｜游戏内存写入：0｜游戏输入注入：无")
    print("不需要 DevTools，不需要 Worker Console，不需要粘贴 JavaScript。")
    print()
    persist("STARTING")

    try:
        print("正在启动 1 个专用 WOF 浏览器房间……")
        manager.start(1)
        manager.print_status()
        persist("BROWSER_STARTED")

        launcher_cmd = [
            sys.executable,
            str(pylaunch_dir / "launcher.py"),
            "--fleet-instance", "1",
            "--fleet-manifest", str(manifest_path),
            "--no-tray",
            "--proof-json", str(pylaunch_proof_path),
        ]
        recorder_cmd = [
            sys.executable,
            str(recorder_dir / "owner_v2_zh_cn.py"),
            "--output-dir", str(recorder_output),
            "--fleet-manifest", str(manifest_path),
            "--no-launch-browser",
        ]
        launcher_proc = start_child(launcher_cmd, pylaunch_dir)
        recorder_proc = start_child(recorder_cmd, recorder_dir)
        threading.Thread(target=reader_thread, args=(launcher_proc, "PYLAUNCH", None, output_queue), daemon=True).start()
        threading.Thread(target=reader_thread, args=(recorder_proc, "RECORDER", recorder_evidence, output_queue), daemon=True).start()

        print()
        print("专用浏览器已打开。现在只需要在这个浏览器中正常进入一个 WOF 房间。")
        print("统一验证会自动检查：")
        print("  Browser / WOF 页面 / Worker / WASM / World 921031")
        print("  Browser Fleet Discovery V2")
        print("  WOF-052L Recorder Discovery V2 准入")
        print("  readOnly=true / ramWrites=0 / inputInjection=false")
        print()

        last_display = 0.0
        while True:
            while True:
                try:
                    prefix, line = output_queue.get_nowait()
                except queue.Empty:
                    break
                if line and ("已确认" in line or "失败" in line or "拒绝" in line or "ERROR" in line):
                    print(f"[{prefix}] {line}")

            fleet_manifest = load_json(manifest_path)
            pyproof = load_json(pylaunch_proof_path)
            fleet = normalize_fleet(fleet_manifest)
            pylaunch = normalize_pylaunch(pyproof)

            if launcher_proc.poll() is not None and not pylaunch.get("automatedPass"):
                msg = f"PYLAUNCH 已提前退出（code={launcher_proc.returncode}）。"
                if msg not in blockers:
                    blockers.append(msg)
            if recorder_proc.poll() is not None and not recorder_evidence.admitted:
                msg = f"WOF-052L Recorder 已提前退出（code={recorder_proc.returncode}）。"
                if msg not in blockers:
                    blockers.append(msg)
            if recorder_evidence.fatal and recorder_evidence.fatal_line:
                msg = f"Recorder 准入失败：{recorder_evidence.fatal_line}"
                if msg not in blockers:
                    blockers.append(msg)

            now = time.monotonic()
            if now - last_display >= 2.0:
                print(
                    "\r"
                    f"浏览器：{'已连接' if fleet['browser'] else '等待'}｜"
                    f"WOF 页面：{'已找到' if fleet['page'] else '等待'}｜"
                    f"Fleet Worker：{'已找到' if fleet['workerIndicator'] else '等待'}｜"
                    f"PYLAUNCH World：{'已确认' if pylaunch['world921031'] else '等待'}｜"
                    f"Recorder：{'已准入' if recorder_evidence.admitted else '等待'}      ",
                    end="",
                    flush=True,
                )
                last_display = now

            payload = persist("LIVE_WAITING")
            if payload["live"]["automatedChecksReady"]:
                print()
                print()
                print("自动只读验证全部通过。")
                print("请只确认最后一个真人事实：当前 WOF 房间是否仍能正常运行？")
                answer = input("正常请输入 Y；如果游戏异常请输入 N：").strip().lower()
                playability = "CONFIRMED" if answer in {"y", "yes", "是", "正常"} else "FAILED"
                if playability == "FAILED":
                    blockers.append("Owner 确认游戏当前不能正常运行。")
                payload = persist("COMPLETE" if playability == "CONFIRMED" else "BLOCKED")
                break

            if blockers:
                print()
                print()
                print("发现真人短验证阻断；其他已取得证据已经写入总 JSON。")
                persist("BLOCKED")
                break
            time.sleep(0.5)

    except KeyboardInterrupt:
        print()
        print("已停止真人短验证；当前已取得证据会保留。")
        blockers.append("Owner 中止了本次真人短验证。")
        persist("INTERRUPTED")
    except Exception as exc:
        print()
        print("统一真人验证没有正常完成，但游戏核心未被修改。")
        print(f"技术详情：{exc}")
        blockers.append(f"统一入口异常：{exc}")
        persist("BLOCKED")
    finally:
        stop_child(recorder_proc)
        stop_child(launcher_proc)
        try:
            manager._stop.set()
            manager.stop_all()
        except Exception:
            pass

    final = persist("COMPLETE" if playability == "CONFIRMED" and not blockers else "BLOCKED")
    print()
    print("============================================================")
    if final["overallResult"] == "PASS":
        print("  PASS — 已具备 10 房间长采集条件")
        print("  本工具没有自动开始一小时长采集。")
    else:
        print("  真人短验证未完成")
        print("  一处失败不会覆盖其他已取得证据。")
    print("============================================================")
    print(f"总结果 JSON：{status_path}")
    print("你最终只需要返回这个 JSON，或者发一张最终状态截图。")
    try:
        if os.name == "nt":
            os.startfile(run_dir)  # type: ignore[attr-defined]
    except Exception:
        pass
    return 0 if final["overallResult"] == "PASS" else 2

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WOF 统一 Windows 真人短验证")
    parser.add_argument("--project-root", required=True)
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    required = [
        project_root / "parallel" / "PYLAUNCH" / "launcher.py",
        project_root / "parallel" / "BROWSER_FLEET" / "fleet_owner_zh_cn.py",
        project_root / "parallel" / "WOF052L_RECORDER" / "owner_v2_zh_cn.py",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("统一真人验证缺少必要工具文件。")
        for path in missing:
            print(f"缺失：{path}")
        return 3
    return run_live(project_root)

if __name__ == "__main__":
    raise SystemExit(main())
