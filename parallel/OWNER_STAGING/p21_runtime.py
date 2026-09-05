from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Mapping, Sequence
import urllib.error
import urllib.request

from p21_candidate import StagingError, is_hex, load_json, run_git, sha256_file

RUNTIME_REL = Path("parallel/PYLAUNCH/render_authority_measurement_entry.py")
P18_MODULE = "wof_launcher.canonical_draw_evidence"


def default_results_dir() -> Path:
    return Path.home() / "Documents" / "WOF_RESULTS"


def default_staging_root() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    return Path(local) / "WOF_ALPHA_STAGING" if local else Path(tempfile.gettempdir()) / "WOF_ALPHA_STAGING"


def default_permanent_repo() -> Path | None:
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        return None
    path = Path(local) / "WOF_ALPHA_CURRENT_MAIN" / "repo"
    return path if path.exists() else None


def resolve_python(explicit: Path | None = None) -> str:
    if explicit is not None:
        value = str(explicit.expanduser().resolve())
        if not Path(value).is_file():
            raise StagingError(f"explicit Python not found: {value}")
        return value
    local = os.environ.get("LOCALAPPDATA")
    if local:
        managed = Path(local) / "WOF Alpha Current Main" / "venv" / "Scripts" / "python.exe"
        if managed.is_file():
            return str(managed)
    return sys.executable


def create_staging_worktree(repo_root: Path, source_commit: str, staging_root: Path) -> dict[str, Any]:
    root, base = repo_root.expanduser().resolve(), staging_root.expanduser().resolve()
    base.mkdir(parents=True, exist_ok=True)
    run_id = f"{source_commit[:12]}-{int(time.time())}-{os.getpid()}"
    run_dir, checkout = base / run_id, base / run_id / "checkout"
    if run_dir.exists():
        raise StagingError(f"staging run already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    try:
        run_git(root, "worktree", "add", "--detach", str(checkout), source_commit)
        head = run_git(checkout, "rev-parse", "HEAD").stdout.strip().lower()
        if head != source_commit:
            raise StagingError(f"staging HEAD mismatch: expected {source_commit}, got {head}")
        if run_git(checkout, "status", "--porcelain").stdout.strip():
            raise StagingError("new staging worktree is unexpectedly dirty")
        return {"runId": run_id, "runDir": str(run_dir), "checkout": str(checkout), "resolvedHead": head}
    except Exception:
        run_git(root, "worktree", "remove", "--force", str(checkout), check=False)
        shutil.rmtree(run_dir, ignore_errors=True)
        raise


def cleanup_staging_worktree(repo_root: Path, staging_root: Path, run_dir: Path, checkout: Path) -> dict[str, Any]:
    root, base = repo_root.expanduser().resolve(), staging_root.expanduser().resolve()
    rd, co = run_dir.expanduser().resolve(), checkout.expanduser().resolve()
    for target, label in ((rd, "runDir"), (co, "checkout")):
        try:
            target.relative_to(base)
        except ValueError as exc:
            raise StagingError(f"refusing cleanup outside bounded staging root: {label}={target}") from exc
    remove = run_git(root, "worktree", "remove", "--force", str(co), check=False)
    if co.exists() and remove.returncode != 0:
        shutil.rmtree(co, ignore_errors=True)
    if rd.exists():
        shutil.rmtree(rd, ignore_errors=True)
    if rd.exists() or co.exists():
        raise StagingError(f"bounded staging cleanup failed: {rd}")
    return {"state": "CLEAN", "idempotent": True}


def runtime_environment(candidate: Mapping[str, Any], base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(base or os.environ)
    env.update({
        "WOF_ALPHA_ACCEPTANCE_COMMIT": str(candidate["sourceCommit"]),
        "WOF_ALPHA_ACCEPTANCE_PACKAGE_VERSION": str(candidate["packageVersion"]),
        "WOF_ALPHA_ACCEPTANCE_MODE": "STAGED_PREPROMOTION",
        "WOF_ALPHA_STAGING_SOURCE": "1", "WOF_ALPHA_LIVE_ACCEPTANCE_HOLD": "1",
        "WOF_ALPHA_OWNER_NAVIGATES": "1",
    })
    for key in ("WOF_ALPHA_CURRENT_MAIN_SOURCE", "WOF_ALPHA_MENU6_ATTACH_ONLY", "WOF_ALPHA_FIXED_DRAW_SMOKE"):
        env.pop(key, None)
    return env


def build_runtime_command(python_exe: str, checkout: Path, output_root: Path, browser: str = "chrome") -> list[str]:
    entry = checkout / RUNTIME_REL
    if not entry.is_file():
        raise StagingError(f"candidate runtime entry missing: {entry}")
    return [python_exe, str(entry), "--root", str(checkout), "--output-root", str(output_root), "--browser", browser]


def start_runtime(command: Sequence[str], env: Mapping[str, str], log_path: Path) -> subprocess.Popen[bytes]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("ab")
    try:
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0
        proc = subprocess.Popen(list(command), env=dict(env), stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
    finally:
        log.close()
    time.sleep(1.0)
    if proc.poll() is not None:
        raise StagingError(f"staged Alpha runtime exited during startup with code {proc.returncode}")
    return proc


def stop_runtime(proc: subprocess.Popen[Any] | None) -> dict[str, Any]:
    if proc is None:
        return {"stopped": True, "pid": None, "exitCode": None}
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait(timeout=5)
    return {"stopped": proc.poll() is not None, "pid": proc.pid, "exitCode": proc.returncode}


def _powershell_json(script: str) -> Any:
    cp = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script], text=True, encoding="utf-8",
        errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if cp.returncode:
        raise StagingError(cp.stderr.strip() or "PowerShell process discovery failed")
    return json.loads(cp.stdout.strip()) if cp.stdout.strip() else []


def discover_permanent_alpha_runtimes(permanent_repo: Path) -> list[dict[str, Any]]:
    if os.name != "nt":
        return []
    escaped = str(permanent_repo.resolve()).replace("'", "''")
    script = (
        "$p=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^pythonw?\\.exe$' -and "
        "$_.CommandLine -like '*render_authority_measurement_entry.py*' -and $_.CommandLine -like '*" + escaped + "*' } | "
        "Select-Object ProcessId,ExecutablePath,CommandLine); $p | ConvertTo-Json -Compress"
    )
    raw = _powershell_json(script)
    if isinstance(raw, Mapping): raw = [raw]
    return [dict(x) for x in raw if isinstance(x, Mapping)] if isinstance(raw, list) else []


def stop_permanent_alpha_runtimes(rows: Sequence[Mapping[str, Any]]) -> list[int]:
    if os.name != "nt": return []
    stopped: list[int] = []
    for row in rows:
        pid = row.get("ProcessId")
        if not isinstance(pid, int) or pid <= 0: continue
        cp = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction Stop"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if cp.returncode: raise StagingError(f"cannot stop Alpha-owned permanent runtime pid={pid}")
        stopped.append(pid)
    return stopped


def restart_permanent_runtime(permanent_repo: Path, permanent_head: str, output_root: Path, browser: str) -> dict[str, Any]:
    local = os.environ.get("LOCALAPPDATA")
    py = Path(local) / "WOF Alpha Current Main" / "venv" / "Scripts" / "python.exe" if local else Path("")
    entry = permanent_repo / RUNTIME_REL
    if not is_hex(permanent_head, 40) or not local or not py.is_file() or not entry.is_file():
        return {"restarted": False, "reason": "deterministic permanent runtime inputs unavailable", "restoreAction": "Run Desktop\\WOF_ALPHA_TEST.cmd to restore the permanent Alpha runtime."}
    cmd = [str(py), str(entry), "--root", str(permanent_repo), "--output-root", str(output_root), "--browser", browser]
    env = dict(os.environ)
    env.update({"WOF_ALPHA_CURRENT_MAIN_SOURCE": "1", "WOF_ALPHA_ACCEPTANCE_COMMIT": permanent_head, "WOF_ALPHA_LIVE_ACCEPTANCE_HOLD": "1", "WOF_ALPHA_OWNER_NAVIGATES": "1"})
    for key in ("WOF_ALPHA_STAGING_SOURCE", "WOF_ALPHA_ACCEPTANCE_MODE", "WOF_ALPHA_ACCEPTANCE_PACKAGE_VERSION", "WOF_ALPHA_MENU6_ATTACH_ONLY", "WOF_ALPHA_FIXED_DRAW_SMOKE"):
        env.pop(key, None)
    try:
        proc = start_runtime(cmd, env, output_root / "P21_PERMANENT_RUNTIME_RESTORE.log")
        return {"restarted": True, "pid": proc.pid, "command": cmd, "restoreAction": None}
    except Exception as exc:
        return {"restarted": False, "reason": f"{type(exc).__name__}: {exc}", "restoreAction": "Run Desktop\\WOF_ALPHA_TEST.cmd to restore the permanent Alpha runtime."}


def discover_browser_websocket(host: str, port: int, timeout: float = 3.0) -> str | None:
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/json/version", timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None
    value = raw.get("webSocketDebuggerUrl") if isinstance(raw, Mapping) else None
    return value if isinstance(value, str) and value.startswith("ws") else None


def collect_p18_from_p16(python_exe: str, checkout: Path, p16_path: Path, output_path: Path, browser_ws: str) -> dict[str, Any]:
    p16 = load_json(p16_path)
    world = p16.get("world") if isinstance(p16.get("world"), Mapping) else {}
    runtime = p16.get("runtime") if isinstance(p16.get("runtime"), Mapping) else {}
    required = {"pageTargetId": world.get("pageTargetId"), "authorityKey": runtime.get("authorityKey"), "runtimeEpoch": runtime.get("epoch"), "rendererEpoch": runtime.get("rendererEpoch")}
    if any(not isinstance(v, str) or not v for v in required.values()):
        return {"state": "SKIPPED_P16_IDENTITY_INCOMPLETE", "output": str(output_path)}
    cmd = [python_exe, "-m", P18_MODULE, "--browser-websocket-url", browser_ws, "--page-target-id", str(required["pageTargetId"]), "--authority-key", str(required["authorityKey"]), "--runtime-epoch", str(required["runtimeEpoch"]), "--renderer-epoch", str(required["rendererEpoch"]), "--output", str(output_path)]
    if isinstance(world.get("pageUrl"), str) and world.get("pageUrl"): cmd.extend(["--page-url", str(world["pageUrl"])])
    if isinstance(world.get("sha256"), str) and world.get("sha256"): cmd.extend(["--world-sha256", str(world["sha256"])])
    cp = subprocess.run(cmd, cwd=checkout / "parallel/PYLAUNCH", text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if output_path.is_file():
        raw = load_json(output_path)
        return {"state": raw.get("evidenceState"), "path": str(output_path), "sha256": sha256_file(output_path), "exitCode": cp.returncode, "reason": raw.get("reason")}
    return {"state": "COLLECTOR_FAILED", "output": str(output_path), "exitCode": cp.returncode, "stderr": cp.stderr[-1000:]}
