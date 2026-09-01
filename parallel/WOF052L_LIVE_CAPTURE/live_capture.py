from __future__ import annotations

import argparse
import inspect
import re
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = next((p for p in (HERE, *HERE.parents) if (p / "parallel").is_dir()), HERE)
BROWSER_FLEET_DIR = REPO_ROOT / "parallel" / "BROWSER_FLEET"
RECORDER_DIR = REPO_ROOT / "parallel" / "WOF052L_RECORDER"
ANALYSIS_DIR = REPO_ROOT / "parallel" / "WOF052L_ANALYSIS"
for path in (BROWSER_FLEET_DIR, RECORDER_DIR, ANALYSIS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

EXPECTED_WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
STATUS_RE = re.compile(
    r"Live rooms\s+(?P<live>\d+)\s+\|\s+Completed\s+(?P<completed>\d+)\s+\|\s+"
    r"T18 samples\s+(?P<t18>\d+)\s+\|\s+Candidate\s+(?P<candidate>\d+)\s+\|\s+"
    r"A4704\s+(?P<a4704>\d+)\s+\|\s+A4712\s+(?P<a4712>\d+)\s+\|\s+T23\s+(?P<t23>\d+)"
)


def _safe_source(obj: Any) -> str:
    try:
        return inspect.getsource(obj)
    except (OSError, TypeError):
        return ""


def recorder_discovery_v2_ready(recorder_module: ModuleType) -> tuple[bool, str]:
    methods = set(getattr(recorder_module, "READ_ONLY_METHODS", set()) or set())
    if getattr(recorder_module, "WORLD_SHA256", None) != EXPECTED_WORLD_SHA256:
        return False, "Recorder 的 World 921031 SHA-256 门槛不是当前黄金值。"
    forbidden = {m for m in methods if str(m).startswith("Input.")}
    forbidden.update({"Runtime.callFunctionOn", "Page.addScriptToEvaluateOnNewDocument"} & methods)
    if forbidden:
        return False, "Recorder 只读 CDP 白名单出现禁止方法：" + ", ".join(sorted(forbidden))
    if "Target.setAutoAttach" not in methods:
        return False, "Recorder 尚未启用 page-session Target.setAutoAttach discovery-v2。"
    if getattr(recorder_module, "_WOF052L_DISCOVERY_V2_INSTALLED", False) is True:
        return True, "WOF-052L Recorder discovery-v2 已安装并具备长采集准入条件。"
    source = "\n".join(
        [
            _safe_source(getattr(recorder_module, "CdpClient", None)),
            _safe_source(getattr(getattr(recorder_module, "RecorderManager", None), "discover", None)),
        ]
    )
    topology_tokens = ("attachedToTarget", "autoAttach", "setAutoAttach", "iframe", "related")
    if not any(token in source for token in topology_tokens):
        return False, "Recorder 尚未发现 related target / iframe -> Worker 的 discovery-v2 实现。"
    return True, "WOF-052L Recorder discovery-v2 已具备长采集准入条件。"


def parse_status_line(line: str) -> dict[str, int]:
    match = STATUS_RE.search(line)
    if not match:
        return {k: 0 for k in ("live", "completed", "t18", "candidate", "a4704", "a4712", "t23")}
    return {key: int(value) for key, value in match.groupdict().items()}


def aggregate_supervisor(supervisor: Any) -> dict[str, int]:
    totals = {k: 0 for k in ("live", "completed", "t18", "candidate", "a4704", "a4712", "t23")}
    for child in list(supervisor.children.values()):
        parsed = parse_status_line(child.manager.status_line())
        for key, value in parsed.items():
            totals[key] += value
    return totals


def choose_room_count(value: str | None) -> int:
    text = (value or "").strip()
    if not text:
        return 10
    count = int(text)
    if count not in {1, 5, 10}:
        raise ValueError("房间数量只接受 1、5 或 10。")
    return count


def build_recorder_args(manifest_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        output_dir=None,
        reset_output=False,
        cdp_host="127.0.0.1",
        cdp_port=None,
        browser="auto",
        no_launch_browser=True,
        game_url=None,
        self_test=False,
        fleet_manifest=str(manifest_path),
        ignore_browser_fleet=False,
    )


def start_analysis_watch(output_dir: Path) -> subprocess.Popen[str] | None:
    analyzer = ANALYSIS_DIR / "analyzer.py"
    if not analyzer.is_file():
        print("自动分析器：未安装，采集仍可继续。")
        return None
    check = subprocess.run(
        [sys.executable, str(analyzer), "--self-test"],
        cwd=str(ANALYSIS_DIR),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
    )
    if check.returncode != 0:
        print("自动分析器：自检未通过，本次只采集不自动分析。")
        detail = (check.stdout or "").strip()
        if detail:
            print("技术详情：" + detail[-800:])
        return None
    print("自动分析器：已通过自检，将随采集结果自动刷新。")
    return subprocess.Popen(
        [sys.executable, str(analyzer), str(output_dir), "--watch", "--interval", "5"],
        cwd=str(ANALYSIS_DIR),
        text=True,
    )


def _stop_analysis(proc: subprocess.Popen[str] | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=8)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def main() -> int:
    try:
        import recorder
        import discovery_v2_sync
        discovery_v2_sync.install(recorder)
        import fleet_recorder
        from owner_zh_cn import choose_output_dir_zh
        from fleet_owner_zh_cn import ChineseFleetManager
    except Exception as exc:
        print("无法加载 Browser Fleet / WOF-052L Recorder discovery-v2 组件。")
        print("游戏本身没有受到影响。")
        print(f"技术详情：{exc}")
        return 2

    ready, reason = recorder_discovery_v2_ready(recorder)
    print("WOF-052L 10 房间长采集 — 启动预检")
    print("只读模式：开启｜游戏内存写入：0｜游戏输入注入：无｜window.Worker 替换：无")
    if not ready:
        print("\n当前禁止开始长采集，避免白跑。")
        print(reason)
        print("精确阻断：WOF-052L Recorder discovery-v2 尚未仓库侧 READY。")
        return 3
    print("Recorder discovery-v2：已就绪")

    recorder.choose_output_dir = choose_output_dir_zh
    try:
        output_dir = recorder.resolve_output_dir(None, False)
    except SystemExit as exc:
        print(f"没有可用的保存目录：{exc}")
        return 4

    try:
        count = choose_room_count(input("请输入要打开的房间数量 [1/5/10，默认 10]："))
    except (ValueError, TypeError) as exc:
        print(f"房间数量无效：{exc}")
        return 5

    manager = ChineseFleetManager()
    try:
        print(f"正在启动 {count} 个独立浏览器房间……")
        manager.start(count)
        manager.refresh_status()
        manager.write_manifest()
    except Exception as exc:
        print("Browser Fleet 启动失败；没有开始 Recorder 长采集。")
        print("游戏本身没有受到影响。")
        print(f"技术详情：{exc}")
        return 6

    args = build_recorder_args(manager.manifest_path)
    supervisor = fleet_recorder.FleetSupervisor(output_dir, args, manager.manifest_path)
    supervisor.sync_manifest()
    analysis_proc = start_analysis_watch(output_dir)

    print("\n10 房间长采集入口已启动。")
    print("请在各浏览器窗口正常进入 WOF；无需 DevTools、Worker Console 或粘贴 JS。")
    print("房间关闭/刷新只结束该房间；其他房间继续，新房间会自动加入。")
    print("按 Ctrl+C 停止采集并完成最终 JSON；浏览器窗口默认保留。\n")

    try:
        while True:
            supervisor.sync_manifest()
            try:
                manager.refresh_status()
                manager.write_manifest()
            except Exception:
                pass
            totals = aggregate_supervisor(supervisor)
            browser_online = sum(1 for runtime in manager.instances.values() if runtime.browser_ok)
            print(
                "\r"
                f"在线浏览器 {browser_online}/{count}｜正在采集 {totals['live']}｜已完成 {totals['completed']}｜"
                f"T18 {totals['t18']}｜candidate {totals['candidate']}｜A4704 {totals['a4704']}｜"
                f"A4712 {totals['a4712']}｜T23 {totals['t23']}｜只读 开启｜RAM writes 0".ljust(190),
                end="",
                flush=True,
            )
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n正在安全停止长采集并写入最终结果……")
    finally:
        supervisor.stop_all()
        final_index = supervisor.write_final_index()
        _stop_analysis(analysis_proc)
        try:
            analyzer = ANALYSIS_DIR / "analyzer.py"
            if analyzer.is_file():
                subprocess.run([sys.executable, str(analyzer), str(output_dir)], cwd=str(ANALYSIS_DIR), timeout=60)
        except Exception as exc:
            print(f"最终自动分析未完成，但采集 JSON 已保存。技术详情：{exc}")
        print(f"多房间最终合并 JSON：{final_index}")
        print(f"保存目录：{output_dir}")
        print("浏览器窗口保持打开；如需全部关闭，请使用 Browser Fleet 的“全部关闭”。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
