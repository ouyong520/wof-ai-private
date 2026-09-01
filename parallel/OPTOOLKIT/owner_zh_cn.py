from __future__ import annotations

import argparse
import builtins
from pathlib import Path

import toolkit


_ORIGINAL_PRINT = builtins.print
_ORIGINAL_INPUT = builtins.input


EXACT = {
    "\n WOF Windows Operator Toolkit\n": "\n WOF Windows 操作工具箱\n",
    "Project :": "项目目录：",
    "Results :": "结果目录：",
    "READ ONLY / RAM writes: 0 / input injection: 0": "只读模式：开启 / 游戏内存写入：0 / 游戏输入注入：0",
    "Recorder:": "采集器：",
    "| Fleet:": "| 浏览器集群：",
    "READY": "已就绪",
    "MISSING": "缺失",
    "PASS": "通过",
    "FAIL": "失败",
    "BLOCKED": "受阻",
    "ATTENTION": "需要关注",
    "1 Update Project": "1 更新项目",
    "2 Start Python Launcher": "2 启动 Python Launcher",
    "3 Start Multi-Room Recorder": "3 启动多房间采集器",
    "4 Start Browser Fleet": "4 启动多房间浏览器",
    "5 Run Regression": "5 运行回归测试",
    "6 Run Live Proof": "6 运行真人 Windows 验证",
    "7 Collect Diagnostics": "7 收集诊断信息",
    "8 Package Results": "8 自动整理并打包结果",
    "9 Open Results Folder": "9 打开结果目录",
    "0 Exit": "0 退出",
    "\n[Update Project]": "\n[更新项目]",
    "\n[Start Python Launcher]": "\n[启动 Python Launcher]",
    "\n[Start Multi-Room Recorder]": "\n[启动多房间采集器]",
    "\n[Start Browser Fleet]": "\n[启动多房间浏览器]",
    "\n[Run Regression]": "\n[运行回归测试]",
    "\n[Run Live Proof]": "\n[运行真人 Windows 验证]",
    "\n[Collect Diagnostics]": "\n[收集诊断信息]",
    "\n[Package Results]": "\n[自动整理并打包结果]",
    "\n[Open Results Folder]": "\n[打开结果目录]",
    "Git was not found. Install Git for Windows, then reopen Toolkit.": "未找到 Git。请安装 Git for Windows，然后重新打开工具箱。",
    "This is not a Git checkout. Open Toolkit from the WOF project folder.": "当前目录不是 Git 项目。请从 WOF 项目目录打开工具箱。",
    "Local changes exist, so Toolkit will not pull over them. Your work is preserved.": "发现本地未提交修改。为了保护你的工作，工具箱不会自动覆盖或拉取这些文件。",
    "Detached Git commit detected. Fetch succeeded; auto-pull was skipped safely.": "检测到 detached Git commit。远端信息已更新，但为了安全已跳过自动 pull。",
    "PYLAUNCH is missing. Use 1 Update Project first.": "没有找到 PYLAUNCH。请先选择 1“更新项目”。",
    "Python Launcher started. Look for the WOF tray icon.": "Python Launcher 已启动。请查看 Windows 右下角的 WOF 托盘图标。",
    "Overall:": "总体结果：",
    "\nSaved:": "\n已保存：",
    "No game RAM write or gameplay input was attempted by Toolkit.": "工具箱没有进行游戏内存写入，也没有发送游戏输入。",
    "No game RAM write or gameplay input was sent.": "没有进行游戏内存写入，也没有发送游戏输入。",
}


def translate_text(text: str) -> str:
    if text in EXACT:
        return EXACT[text]
    if not text:
        return text

    prefixes = [
        ("Git fetch failed. Check network/login.\n", "Git 更新远端信息失败。请检查网络或登录状态。\n技术详情："),
        ("Fast-forward update was not possible. No local file was overwritten.\n", "无法安全快进更新；没有覆盖任何本地文件。\n技术详情："),
        ("Project updated: ", "项目已更新："),
        ("Reopen WOF_TOOLKIT.cmd after this session so pulled Toolkit/dependency updates are loaded.", "本次操作结束后，请重新打开 WOF_TOOLKIT.cmd，以加载刚更新的工具和依赖。"),
        ("Multi-Room Recorder is missing. Use 1 Update Project first.", "没有找到多房间采集器。请先选择 1“更新项目”。"),
        ("Browser Fleet is missing. Use 1 Update Project first.", "没有找到多房间浏览器工具。请先选择 1“更新项目”。"),
        ("Started: ", "已启动："),
        ("Could not start: ", "启动失败。技术详情："),
        ("Recorder output: ", "采集器结果目录："),
        ("Diagnostics saved: ", "诊断信息已保存："),
        ("Package ready: ", "结果包已生成："),
        ("Opened: ", "已打开："),
        ("WOF Toolkit could not validate project root:", "WOF 工具箱无法确认项目根目录："),
    ]
    for old, new in prefixes:
        if text.startswith(old):
            return new + text[len(old):]

    if text.startswith("Live Proof started using existing PYLAUNCH. Enter WOF normally; no DevTools/JS paste.\nProof JSON:"):
        return text.replace(
            "Live Proof started using existing PYLAUNCH. Enter WOF normally; no DevTools/JS paste.\nProof JSON:",
            "真人 Windows 验证已使用现有 PYLAUNCH 启动。请正常进入 WOF，不需要 DevTools，也不需要粘贴 JS。\n验证 JSON：",
            1,
        )
    if text.startswith("This action timed out."):
        return "本次操作超时。没有进行游戏内存写入，也没有发送游戏输入。"
    if text.startswith("Toolkit could not complete this action:"):
        detail = text.split(":", 1)[1].strip() if ":" in text else text
        return f"工具箱没有完成这项操作。\n技术详情：{detail}"
    if text.startswith("Please choose a number from 0 to 9."):
        return "请输入 0 到 9 之间的菜单编号。"
    if text.startswith("alpha_product:"):
        return text.replace("alpha_product:", "Alpha 产品回归：", 1)
    if text.startswith("rc5_independent_bootstrap:"):
        return text.replace("rc5_independent_bootstrap:", "RC5 独立 bootstrap 回归：", 1)
    if text.startswith("wof052l_self_test:"):
        return text.replace("wof052l_self_test:", "WOF-052L 自检：", 1)
    if text.startswith("pylaunch_unittest:"):
        return text.replace("pylaunch_unittest:", "PYLAUNCH 单元测试：", 1)
    if text.startswith("browser_fleet_unittest:"):
        return text.replace("browser_fleet_unittest:", "Browser Fleet 单元测试：", 1)
    if text.startswith("toolkit_unittest:"):
        return text.replace("toolkit_unittest:", "Operator Toolkit 单元测试：", 1)
    if "BLOCKED (Node.js not found)" in text:
        return text.replace("BLOCKED (Node.js not found)", "受阻（未找到 Node.js）")
    if text.endswith(": MISSING"):
        return text[:-len(": MISSING")] + "：缺失"
    return text


def translated_print(*args, **kwargs):
    converted = tuple(translate_text(x) if isinstance(x, str) else x for x in args)
    return _ORIGINAL_PRINT(*converted, **kwargs)


def translate_prompt(prompt: str) -> str:
    if prompt == "Choose 0-9: ":
        return "请选择 0-9："
    if prompt == "\nPress Enter to return to WOF Toolkit...":
        return "\n按回车返回 WOF 工具箱……"
    return prompt


def translated_input(prompt: str = ""):
    return _ORIGINAL_INPUT(translate_prompt(prompt))


class ChineseToolkit(toolkit.Toolkit):
    """Only changes owner-facing launch/integration surfaces; core Toolkit behavior stays in toolkit.py."""

    def component(self, key):
        if key == "recorder":
            print("\n[启动多房间采集器]")
            entry = self.root / "parallel/WOF052L_RECORDER/owner_zh_cn.py"
            if not entry.is_file():
                print("没有找到多房间采集器中文入口。请先选择 1“更新项目”。")
                return
            out = self.results / "recorder"
            out.mkdir(parents=True, exist_ok=True)
            ok, detail = self.spawn(entry, ["--output-dir", str(out)])
            if ok:
                print("已启动：" + detail)
                print("采集器结果目录：" + str(out))
            else:
                print("启动失败。")
                print("游戏本身没有受到影响。")
                print("技术详情：" + detail)
            return
        return super().component(key)

    def package(self):
        print("\n[自动整理并打包结果]")
        entry = self.root / "parallel/EVIDENCE_INGESTOR/ingestor.py"
        if not entry.is_file():
            print("没有找到自动结果整理器。请先选择 1“更新项目”。")
            return
        try:
            cp = toolkit.run([toolkit.sys.executable, str(entry), "--root", str(self.results), "--package"], entry.parent, 600)
        except Exception as exc:
            print("自动结果整理没有完成。原始证据和游戏本身都没有受到影响。")
            print(f"技术详情：{exc}")
            return
        if cp.stdout:
            print(cp.stdout.rstrip())
        if cp.returncode in (0, 1):
            if cp.returncode == 1:
                print("整理已完成，但发现严重安全或身份异常。请查看生成的“结果汇总.txt”。")
            return
        print("自动结果整理没有完成。原始证据和游戏本身都没有受到影响。")
        if cp.stderr:
            print("技术详情：" + cp.stderr[-1500:])


def main() -> int:
    parser = argparse.ArgumentParser(description="WOF Windows 操作工具箱 — 简体中文 owner 界面")
    parser.add_argument("--root", required=True, help="WOF 项目根目录")
    args = parser.parse_args()
    root = Path(args.root)
    if not (root / "parallel/PYLAUNCH").is_dir() or not (root / "product/alpha").is_dir():
        print("无法确认 WOF 项目目录。")
        print(f"技术详情：{root}")
        return 2

    builtins.print = translated_print
    builtins.input = translated_input
    try:
        return ChineseToolkit(root).loop()
    except KeyboardInterrupt:
        print("\n已退出 WOF 工具箱。游戏本身没有受到影响。")
        return 130
    except Exception as exc:
        print("WOF 工具箱发生了未预期的问题。")
        print("游戏本身没有受到影响，也没有进行游戏内存写入或输入注入。")
        print(f"技术详情：{exc}")
        return 2
    finally:
        builtins.print = _ORIGINAL_PRINT
        builtins.input = _ORIGINAL_INPUT


if __name__ == "__main__":
    raise SystemExit(main())
