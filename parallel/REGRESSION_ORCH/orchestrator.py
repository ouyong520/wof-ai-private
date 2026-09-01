from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[1]
MANIFEST_PATH = HERE / "manifest.json"
SUMMARY_PATH = HERE / "REGRESSION_SUMMARY.json"
TEXT_PATH = HERE / "回归结果.txt"
LOG_ROOT = HERE / "logs"

STATUS_ZH = {
    "PASS": "通过",
    "FAIL": "失败",
    "SKIPPED": "跳过",
    "BLOCKED": "受阻",
    "NOT_RUN": "未运行",
}


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_repo_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    root_resolved = root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"路径越界：{relative}") from exc
    return candidate


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "wof-regression-orchestrator-manifest-v1":
        raise ValueError("manifest schema 不匹配")
    if not isinstance(data.get("suites"), list):
        raise ValueError("manifest suites 缺失")
    return data


def current_platform_key() -> str:
    if sys.platform.startswith("win"):
        return "win32"
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "darwin"
    return sys.platform


def resolve_argv(argv: list[str]) -> list[str]:
    resolved: list[str] = []
    for token in argv:
        if token == "{python}":
            resolved.append(sys.executable)
        elif token == "{node}":
            resolved.append(shutil.which("node") or "node")
        elif token == "{cmd}":
            resolved.append(os.environ.get("COMSPEC") or shutil.which("cmd") or "cmd.exe")
        else:
            resolved.append(token)
    return resolved


def display_command(argv: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(argv)
    return shlex.join(argv)


def executable_missing(name: str) -> bool:
    if name == "python":
        return not bool(sys.executable)
    if name == "cmd":
        return current_platform_key() == "win32" and not (os.environ.get("COMSPEC") or shutil.which("cmd"))
    return shutil.which(name) is None


def run_command(
    root: Path,
    command: dict[str, Any],
    suite_id: str,
    log_handle: Any,
    default_timeout: int,
) -> dict[str, Any]:
    cwd_rel = command.get("cwd", ".")
    cwd = safe_repo_path(root, cwd_rel)
    argv = resolve_argv(list(command["argv"]))
    timeout = int(command.get("timeoutSeconds", default_timeout))
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")

    display = display_command(argv)
    log_handle.write(f"\n===== 命令：{display} =====\n")
    log_handle.write(f"工作目录：{cwd}\n")
    log_handle.flush()

    started = time.perf_counter()
    try:
        cp = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        output = cp.stdout or ""
        log_handle.write(output)
        duration = round(time.perf_counter() - started, 3)
        status = "PASS" if cp.returncode == 0 else "FAIL"
        return {
            "status": status,
            "returnCode": cp.returncode,
            "durationSeconds": duration,
            "command": display,
            "cwd": cwd_rel,
        }
    except subprocess.TimeoutExpired as exc:
        duration = round(time.perf_counter() - started, 3)
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", "replace")
        log_handle.write(str(output))
        log_handle.write(f"\n[超时] {timeout} 秒\n")
        return {
            "status": "FAIL",
            "returnCode": None,
            "durationSeconds": duration,
            "command": display,
            "cwd": cwd_rel,
            "reasonZh": f"命令超过 {timeout} 秒超时。",
        }
    except OSError as exc:
        duration = round(time.perf_counter() - started, 3)
        log_handle.write(f"\n[无法启动] {exc}\n")
        return {
            "status": "BLOCKED",
            "returnCode": None,
            "durationSeconds": duration,
            "command": display,
            "cwd": cwd_rel,
            "reasonZh": f"命令无法启动：{exc}",
        }


def run_suite(root: Path, suite: dict[str, Any], log_dir: Path) -> dict[str, Any]:
    suite_id = str(suite["id"])
    name_zh = str(suite["nameZh"])
    platforms = suite.get("platforms") or []
    current = current_platform_key()
    if platforms and current not in platforms:
        return {
            "id": suite_id,
            "nameZh": name_zh,
            "status": "SKIPPED",
            "durationSeconds": 0.0,
            "safetyCritical": bool(suite.get("safetyCritical")),
            "platformOptional": bool(suite.get("platformOptional")),
            "reasonZh": f"当前平台 {current} 不适用；允许平台：{', '.join(platforms)}。",
            "log": None,
            "commands": [],
            "failedCommands": [],
        }

    missing_paths = [
        path for path in suite.get("requiredPaths", [])
        if not safe_repo_path(root, path).exists()
    ]
    missing_executables = [
        name for name in suite.get("requiredExecutables", [])
        if executable_missing(name)
    ]
    if missing_paths or missing_executables:
        reasons: list[str] = []
        if missing_paths:
            reasons.append("缺少文件：" + "、".join(missing_paths))
        if missing_executables:
            reasons.append("缺少命令：" + "、".join(missing_executables))
        return {
            "id": suite_id,
            "nameZh": name_zh,
            "status": "BLOCKED",
            "durationSeconds": 0.0,
            "safetyCritical": bool(suite.get("safetyCritical")),
            "platformOptional": bool(suite.get("platformOptional")),
            "reasonZh": "；".join(reasons),
            "log": None,
            "commands": [],
            "failedCommands": [],
        }

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{suite_id}.log"
    started = time.perf_counter()
    command_results: list[dict[str, Any]] = []
    default_timeout = int(suite.get("timeoutSeconds", 180))
    with log_path.open("w", encoding="utf-8", newline="\n") as log_handle:
        log_handle.write(f"WOF Regression Orchestrator\nSuite: {name_zh} ({suite_id})\n")
        for command in suite.get("commands", []):
            command_results.append(
                run_command(root, command, suite_id, log_handle, default_timeout)
            )

    statuses = [row["status"] for row in command_results]
    if any(status == "FAIL" for status in statuses):
        status = "FAIL"
    elif any(status == "BLOCKED" for status in statuses):
        status = "BLOCKED"
    else:
        status = "PASS"
    failed_commands = [
        row["command"] for row in command_results if row["status"] in {"FAIL", "BLOCKED"}
    ]
    duration = round(time.perf_counter() - started, 3)
    return {
        "id": suite_id,
        "nameZh": name_zh,
        "status": status,
        "durationSeconds": duration,
        "safetyCritical": bool(suite.get("safetyCritical")),
        "platformOptional": bool(suite.get("platformOptional")),
        "reasonZh": None,
        "log": log_path.relative_to(root).as_posix(),
        "commands": command_results,
        "failedCommands": failed_commands,
    }


def is_test_candidate(path: Path) -> bool:
    name = path.name.lower()
    if path.suffix.lower() == ".py":
        return name.startswith("test_") or name.endswith("_test.py")
    if path.suffix.lower() in {".js", ".mjs", ".cjs"}:
        return (
            name.startswith("test_")
            or "regression" in name
            or "retest" in name
            or name.endswith("_test.js")
            or name.endswith("_test.mjs")
        )
    return False


def discover_candidates(root: Path) -> list[str]:
    found: set[str] = set()
    parallel = root / "parallel"
    if parallel.exists():
        for path in parallel.rglob("*"):
            if path.is_file() and is_test_candidate(path):
                found.add(path.relative_to(root).as_posix())
    product_alpha = root / "product" / "alpha"
    if product_alpha.exists():
        for path in product_alpha.glob("*"):
            if path.is_file() and is_test_candidate(path):
                found.add(path.relative_to(root).as_posix())
    return sorted(found)


def under_any_root(path: str, roots: list[str]) -> bool:
    normalized = path.replace("\\", "/").rstrip("/")
    for root in roots:
        prefix = root.replace("\\", "/").rstrip("/")
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return True
    return False


def build_allowlist_guard(root: Path, manifest: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    candidates = discover_candidates(root)
    allowlisted = set(manifest.get("allowlistedTestPaths", []))
    guard_roots = list(manifest.get("guardRoots", []))
    guarded_unknown = [
        path for path in candidates
        if under_any_root(path, guard_roots) and path not in allowlisted
    ]
    outside_unknown = [
        path for path in candidates
        if not under_any_root(path, guard_roots) and path not in allowlisted
    ]
    if guarded_unknown:
        guard = {
            "id": "allowlist_guard",
            "nameZh": "测试 Allowlist 安全门",
            "status": "BLOCKED",
            "durationSeconds": 0.0,
            "safetyCritical": True,
            "platformOptional": False,
            "reasonZh": "发现目标 lane 新测试，但尚未显式纳入 allowlist：" + "、".join(guarded_unknown),
            "log": None,
            "commands": [],
            "failedCommands": [],
            "unallowlisted": guarded_unknown,
        }
    else:
        guard = {
            "id": "allowlist_guard",
            "nameZh": "测试 Allowlist 安全门",
            "status": "PASS",
            "durationSeconds": 0.0,
            "safetyCritical": True,
            "platformOptional": False,
            "reasonZh": None,
            "log": None,
            "commands": [],
            "failedCommands": [],
            "unallowlisted": [],
        }
    return guard, outside_unknown


def compute_offline_overall(suites: list[dict[str, Any]]) -> str:
    effective = [
        suite for suite in suites
        if not (suite["status"] == "SKIPPED" and suite.get("platformOptional"))
    ]
    if any(suite["status"] == "FAIL" for suite in effective):
        return "FAIL"
    if any(suite["status"] == "BLOCKED" for suite in effective):
        return "BLOCKED"
    if any(suite["status"] == "SKIPPED" for suite in effective):
        return "BLOCKED"
    return "PASS"


def compute_overall(offline_overall: str, manual_proofs: list[dict[str, Any]]) -> str:
    if offline_overall == "FAIL":
        return "FAIL"
    if offline_overall == "BLOCKED":
        return "BLOCKED"
    if any(item.get("status") in {"NOT_RUN", "BLOCKED"} for item in manual_proofs):
        return "BLOCKED"
    return offline_overall


def write_outputs(root: Path, summary: dict[str, Any]) -> None:
    SUMMARY_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "WOF 全仓库回归结果",
        "=" * 60,
        f"时间：{summary['generatedAt']}",
        f"平台：{summary['platform']['system']} / {summary['platform']['python']}",
        f"离线总结果：{summary['offlineOverall']} / {STATUS_ZH.get(summary['offlineOverall'], summary['offlineOverall'])}",
        f"全局结果：{summary['overall']} / {STATUS_ZH.get(summary['overall'], summary['overall'])}",
        "",
        "说明：全局结果会因为真人 Browser proof 按设计未运行而显示 BLOCKED；",
        "      仓库侧 READY 以离线总结果 PASS 且 allowlist 安全门 PASS 为准。",
        "",
        "离线 suites：",
    ]
    for suite in summary["suites"]:
        status = suite["status"]
        line = (
            f"- [{status}/{STATUS_ZH.get(status, status)}] {suite['nameZh']} "
            f"({suite['durationSeconds']:.3f}s)"
        )
        if suite.get("log"):
            line += f" | 日志：{suite['log']}"
        lines.append(line)
        if suite.get("reasonZh"):
            lines.append(f"  原因：{suite['reasonZh']}")
        for command in suite.get("failedCommands", []):
            lines.append(f"  失败命令：{command}")

    lines.extend(["", "真人证明（本编排器不自动执行）："])
    for proof in summary["manualProofs"]:
        status = proof.get("status", "NOT_RUN")
        lines.append(
            f"- [{status}/{STATUS_ZH.get(status, status)}] {proof['nameZh']}：{proof.get('reasonZh', '')}"
        )

    outside = summary.get("discoveredUntrustedOutsideGuard", [])
    lines.extend(["", "未自动执行的其他 parallel 测试候选："])
    if outside:
        lines.extend(f"- {path}" for path in outside)
    else:
        lines.append("- 无")

    lines.extend([
        "",
        "安全边界：read-only；ramWrites=0；no gameplay input injection；",
        "no Worker replacement；不自动进入游戏；不修改 product/alpha/**。",
        "",
    ])
    TEXT_PATH.write_text("\n".join(lines), encoding="utf-8")


def run(root: Path) -> dict[str, Any]:
    manifest = load_manifest()
    root = root.resolve()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_dir = LOG_ROOT / run_id
    suites: list[dict[str, Any]] = []

    print("WOF 全仓库离线回归开始")
    print(f"仓库：{root}")
    for suite in manifest["suites"]:
        print(f"\n[运行] {suite['nameZh']}")
        result = run_suite(root, suite, log_dir)
        suites.append(result)
        print(f"[{result['status']}] {suite['nameZh']} ({result['durationSeconds']:.3f}s)")
        if result.get("reasonZh"):
            print(f"  {result['reasonZh']}")

    guard, outside_unknown = build_allowlist_guard(root, manifest)
    suites.append(guard)
    print(f"\n[{guard['status']}] {guard['nameZh']}")
    if guard.get("reasonZh"):
        print(f"  {guard['reasonZh']}")

    manual_proofs = list(manifest.get("manualProofs", []))
    offline_overall = compute_offline_overall(suites)
    overall = compute_overall(offline_overall, manual_proofs)
    summary = {
        "schema": "wof-regression-summary-v1",
        "generatedAt": utc_now(),
        "runId": run_id,
        "repository": "ouyong520/wof-ai-private",
        "repoRoot": str(root),
        "platform": {
            "key": current_platform_key(),
            "system": platform.platform(),
            "python": sys.version.split()[0],
            "node": shutil.which("node"),
            "git": shutil.which("git"),
        },
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "workerReplacement": False,
            "autoEnterGame": False,
            "productionRuleChanges": False,
        },
        "offlineOverall": offline_overall,
        "overall": overall,
        "repositorySideReady": offline_overall == "PASS" and guard["status"] == "PASS",
        "suites": suites,
        "manualProofs": manual_proofs,
        "discoveredUntrustedOutsideGuard": outside_unknown,
        "outputs": {
            "summary": SUMMARY_PATH.relative_to(root).as_posix(),
            "text": TEXT_PATH.relative_to(root).as_posix(),
            "logDirectory": log_dir.relative_to(root).as_posix(),
        },
    }
    write_outputs(root, summary)
    print("\n" + "=" * 60)
    print(f"离线总结果：{offline_overall}")
    print(f"全局结果：{overall}（真人 proof 按设计未自动运行）")
    print(f"JSON：{SUMMARY_PATH}")
    print(f"中文结果：{TEXT_PATH}")
    return summary


def main() -> int:
    _configure_console()
    parser = argparse.ArgumentParser(description="WOF 全仓库回归编排器")
    parser.add_argument("--repo-root", default=str(DEFAULT_ROOT), help="仓库根目录")
    parser.add_argument("--ci", action="store_true", help="CI 模式；离线结果非 PASS 时返回非零")
    args = parser.parse_args()
    root = Path(args.repo_root)
    try:
        summary = run(root)
    except Exception as exc:
        print(f"编排器自身失败：{exc}", file=sys.stderr)
        return 2
    return 0 if summary["offlineOverall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
