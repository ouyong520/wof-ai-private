from __future__ import annotations

import builtins
import re
from pathlib import Path

import fleet_recorder
import recorder


_ORIGINAL_PRINT = builtins.print


def _translate_status_line(text: str) -> str:
    if not text.startswith("Browser ") or "Live rooms" not in text:
        return text
    out = text
    out = out.replace("Browser OK", "浏览器 已连接")
    out = out.replace("Browser WAIT", "浏览器 等待中")
    out = out.replace("Live rooms", "在线房间")
    out = out.replace("Completed", "已完成房间")
    out = out.replace("T18 samples", "T18 样本")
    out = out.replace("Candidate", "候选周期")
    out = out.replace("T23", "T23 周期")
    out = out.replace("READ ONLY / RAM writes 0", "只读模式 开启 / 游戏内存写入 0")
    return out


def translate_text(text: str) -> str:
    if not text:
        return text
    if text.startswith("\r"):
        return "\r" + translate_text(text[1:])
    if text.startswith("Browser ") and "Live rooms" in text:
        return _translate_status_line(text)

    exact = {
        "First run: choose a folder for WOF-052L JSON output.": "首次使用：请选择 WOF-052L JSON 保存目录。",
        "WOF-052L Automatic Multi-Room Event Recorder": "WOF-052L 自动多房间事件采集器",
        "Safety: READ ONLY / RAM writes 0 / no input injection": "安全状态：只读模式开启 / 游戏内存写入 0 / 无游戏输入注入",
        "Press Ctrl+C to stop and write final merged JSON.\n": "按 Ctrl+C 停止采集，并写入最终合并 JSON。\n",
        "\nStopping recorder...": "\n正在停止采集器……",
        "WOF-052L Browser Fleet supervisor": "WOF-052L 多房间浏览器采集管理器",
        "Safety: READ ONLY / RAM writes 0 / no input injection / no window.Worker replacement": "安全状态：只读模式开启 / 游戏内存写入 0 / 无游戏输入注入 / 不替换 window.Worker",
        "Press Ctrl+C to stop all recorder workers and finalize JSON.\n": "按 Ctrl+C 停止全部采集房间，并完成最终 JSON。\n",
        "\nStopping fleet recorder...": "\n正在停止多房间采集器……",
        "Browser Fleet manifest has no entries; using original WOF-052L single-CDP mode.": "没有发现 Browser Fleet 房间，将使用原有 WOF-052L 单浏览器模式。",
        "SELF-TEST PASS — WOF-052L recorder invariants and sequence aggregation": "自检通过 — WOF-052L 采集器安全约束与序列汇总正常",
    }
    if text in exact:
        return exact[text]

    if text.startswith("Save folder: "):
        return "保存目录：" + text[len("Save folder: "):]
    if text.startswith("Run: "):
        return "本次运行：" + text[len("Run: "):]
    if text.startswith("\nFinal merged JSON: "):
        return "\n最终合并 JSON 已保存：" + text[len("\nFinal merged JSON: "):]
    if text.startswith("Fleet manifest: "):
        return "浏览器集群状态文件：" + text[len("Fleet manifest: "):]
    if text.startswith("\nFleet merged JSON: "):
        return "\n多房间合并 JSON 已保存：" + text[len("\nFleet merged JSON: "):]

    m = re.match(r"\nLaunched debug browser on (.+)\. Open WOF rooms in that browser\.$", text)
    if m:
        return f"\n已启动可连接的浏览器：{m.group(1)}。请在这个浏览器中正常打开 WOF 房间。"

    if text.startswith("\nBrowser: WAITING for Chrome/Edge CDP"):
        return "\n浏览器：等待连接 Chrome/Edge。采集器会继续等待，游戏本身不受影响。"
    if text.startswith("\nBrowser: OK — "):
        return "\n浏览器：已连接 — " + text[len("\nBrowser: OK — "):]
    if text.startswith("\nCDP connect failed: "):
        detail = text[len("\nCDP connect failed: "):]
        return f"\n暂时无法连接浏览器调试接口。游戏本身不受影响。\n技术详情：{detail}"

    m = re.match(r"\nSkip worker ([^:]+): (.*)$", text, re.S)
    if m:
        return f"\n已跳过 Worker {m.group(1)}，因为它没有通过当前采集条件。\n技术详情：{m.group(2)}"
    m = re.match(r"\nSkip worker ([^:]+): World SHA mismatch$", text)
    if m:
        return f"\n已跳过 Worker {m.group(1)}：游戏版本身份不匹配。"
    m = re.match(r"\n\+ Room (.+) attached — exact World 921031 / READ ONLY$", text)
    if m:
        return f"\n+ 房间 {m.group(1)} 已连接 — World 921031 已确认 / 只读模式"
    m = re.match(r"\nAttach ([^ ]+) failed safely: (.*)$", text, re.S)
    if m:
        return f"\n连接 Worker {m.group(1)} 失败；其他房间会继续运行，游戏本身不受影响。\n技术详情：{m.group(2)}"
    m = re.match(r"\n- Room (.+) finalized \(([^)]+)\) T18cand=(.*)$", text)
    if m:
        return f"\n- 房间 {m.group(1)} 已完成｜原因代码：{m.group(2)}｜T18 候选周期：{m.group(3)}"

    m = re.match(r"\nFleet #(\d+): WAITING (.+); other rooms continue\.$", text)
    if m:
        return f"\n集群房间 #{m.group(1)}：等待浏览器 {m.group(2)}；其他房间继续运行。"
    m = re.match(r"\nFleet #(\d+): CDP connect failed safely: (.*)$", text, re.S)
    if m:
        return f"\n集群房间 #{m.group(1)}：浏览器连接失败；其他房间继续运行。\n技术详情：{m.group(2)}"
    m = re.match(r"\nFleet #(\d+): Browser OK — (.*)$", text, re.S)
    if m:
        return f"\n集群房间 #{m.group(1)}：浏览器已连接 — {m.group(2)}"
    m = re.match(r"\nWOF-052L fleet recorder #(\d+) -> (.*)$", text, re.S)
    if m:
        return f"\nWOF-052L 集群采集房间 #{m.group(1)} -> {m.group(2)}"

    if text.startswith("Fleet entries ") and "Recorder workers" in text:
        out = text.replace("Fleet entries", "集群房间")
        out = out.replace("Recorder workers", "采集进程")
        out = out.replace("READ ONLY / RAM writes 0", "只读模式 开启 / 游戏内存写入 0")
        return out

    return text


def translated_print(*args, **kwargs):
    converted = tuple(translate_text(x) if isinstance(x, str) else x for x in args)
    return _ORIGINAL_PRINT(*converted, **kwargs)


def choose_output_dir_zh() -> Path:
    chosen = ""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        chosen = filedialog.askdirectory(title="请选择 WOF-052L JSON 保存目录")
        root.destroy()
    except Exception:
        pass
    if not chosen:
        print("首次使用：请选择 WOF-052L JSON 保存目录。")
        chosen = input("保存目录：").strip().strip('"')
    if not chosen:
        raise SystemExit("没有选择保存目录。")
    return Path(chosen).expanduser().resolve()


def localized_parser():
    parser = fleet_recorder.build_parser()
    parser.description = "WOF-052L 自动多房间只读事件采集器"
    help_by_dest = {
        "output_dir": "设置并记住 JSON 保存目录",
        "reset_output": "忘记已保存的目录，下次重新选择",
        "cdp_host": "浏览器 CDP 主机（默认 127.0.0.1）",
        "cdp_port": "优先使用的 Chrome/Edge CDP 端口；不填时自动扫描常用端口",
        "browser": "需要自动启动浏览器时使用的浏览器类型",
        "no_launch_browser": "只连接已经运行的 CDP 浏览器，不自动启动浏览器",
        "game_url": "可选：采集器启动浏览器时自动打开的游戏网址",
        "self_test": "运行离线自检后退出",
        "fleet_manifest": "可选：Browser Fleet instances.json 路径",
        "ignore_browser_fleet": "忽略 Browser Fleet，强制使用原有单浏览器模式",
        "help": "显示这份中文帮助并退出",
    }
    for action in parser._actions:
        if action.dest in help_by_dest:
            action.help = help_by_dest[action.dest]
    return parser


def main() -> int:
    builtins.print = translated_print
    recorder.choose_output_dir = choose_output_dir_zh
    try:
        args = localized_parser().parse_args()
        if args.self_test:
            return recorder.run_self_test()

        output_dir = recorder.resolve_output_dir(args.output_dir, args.reset_output)
        manifest_path = (
            Path(args.fleet_manifest).expanduser().resolve()
            if args.fleet_manifest
            else fleet_recorder.default_fleet_manifest()
        )
        entries = [] if args.ignore_browser_fleet else fleet_recorder.load_fleet_entries(manifest_path)
        if not entries:
            print("Browser Fleet manifest has no entries; using original WOF-052L single-CDP mode.")
            recorder.RecorderManager(output_dir, args).run()
            return 0

        supervisor = fleet_recorder.FleetSupervisor(output_dir, args, manifest_path)
        for endpoint in entries:
            supervisor.start_endpoint(endpoint)
        return supervisor.run()
    except KeyboardInterrupt:
        print("\n已收到停止命令，正在安全结束采集……")
        return 130
    except SystemExit:
        raise
    except Exception as exc:
        print("WOF-052L 采集器没有正常完成。")
        print("游戏本身没有受到影响；没有进行游戏内存写入或输入注入。")
        print(f"技术详情：{exc}")
        return 2
    finally:
        builtins.print = _ORIGINAL_PRINT


if __name__ == "__main__":
    raise SystemExit(main())
