from __future__ import annotations

import argparse
import builtins
import json
import re
from pathlib import Path

import toolkit

_ORIGINAL_PRINT = builtins.print
_ORIGINAL_INPUT = builtins.input

EXACT = {
    "\n WOF Windows Operator Toolkit\n": "\n WOF Windows 操作工具箱\n",
    "Project :": "项目目录：", "Results :": "结果目录：",
    "READ ONLY / RAM writes: 0 / input injection: 0": "只读模式：开启 / 游戏内存写入：0 / 游戏输入注入：0",
    "Recorder:": "采集器：", "| Fleet:": "| 浏览器集群：",
    "READY": "已就绪", "MISSING": "缺失", "PASS": "通过", "FAIL": "失败", "BLOCKED": "受阻", "ATTENTION": "需要关注",
    "1 Update Project": "1 更新项目", "2 Start Python Launcher": "2 启动 Python Launcher", "3 Start Multi-Room Recorder": "3 启动多房间采集器",
    "4 Start Browser Fleet": "4 启动多房间浏览器", "5 Run Regression": "5 运行回归测试", "6 Run Live Proof": "6 打开 WOF 头顶显示",
    "6 运行真人浏览器验证": "6 打开 WOF 头顶显示",
    "7 Collect Diagnostics": "7 收集诊断信息", "8 Package Results": "8 自动整理并打包结果", "8 打包结果": "8 自动整理并打包结果",
    "9 Open Results Folder": "9 打开结果目录", "0 Exit": "0 退出",
    "\n[Update Project]": "\n[更新项目]", "\n[Start Python Launcher]": "\n[启动 Python Launcher]", "\n[Start Multi-Room Recorder]": "\n[启动多房间采集器]",
    "\n[Start Browser Fleet]": "\n[启动多房间浏览器工具]", "\n[Run Regression]": "\n[运行回归测试]", "\n[Run Live Proof]": "\n[打开 WOF 头顶显示]",
    "\n[Collect Diagnostics]": "\n[收集诊断信息]", "\n[Package Results]": "\n[自动整理并打包结果]", "\n[Open Results Folder]": "\n[打开结果目录]",
    "Git was not found. Install Git for Windows, then reopen Toolkit.": "未找到 Git。请安装 Git for Windows，然后重新打开工具箱。",
    "This is not a Git checkout. Open Toolkit from the WOF project folder.": "当前目录不是 Git 项目。请从 WOF 项目目录打开工具箱。",
    "Local changes exist, so Toolkit will not pull over them. Your work is preserved.": "发现本地未提交修改。为了保护你的工作，工具箱不会自动覆盖或拉取这些文件。",
    "Detached Git commit detected. Fetch succeeded; auto-pull was skipped safely.": "检测到 detached Git commit。远端信息已更新，但为了安全已跳过自动 pull。",
    "PYLAUNCH is missing. Use 1 Update Project first.": "没有找到 PYLAUNCH。请先选择 1“更新项目”。",
    "Python Launcher started. Look for the WOF tray icon.": "Python Launcher 已启动。请查看 Windows 右下角的 WOF 托盘图标。",
    "Overall:": "总体结果：", "\nSaved:": "\n已保存：",
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
        ("Started: ", "已启动："), ("Could not start: ", "启动失败。技术详情："), ("Recorder output: ", "采集器结果目录："),
        ("Diagnostics saved: ", "诊断信息已保存："), ("Package ready: ", "结果包已生成："), ("Opened: ", "已打开："),
        ("WOF Toolkit could not validate project root:", "WOF 工具箱无法确认项目根目录："),
    ]
    for old, new in prefixes:
        if text.startswith(old):
            return new + text[len(old):]
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
    return _ORIGINAL_PRINT(*(translate_text(x) if isinstance(x, str) else x for x in args), **kwargs)


def translate_prompt(prompt: str) -> str:
    if prompt == "Choose 0-9: ":
        return "请选择 0-9："
    if prompt == "\nPress Enter to return to WOF Toolkit...":
        return "\n按回车返回 WOF 工具箱……"
    return prompt


def translated_input(prompt: str = ""):
    return _ORIGINAL_INPUT(translate_prompt(prompt))


def _read_package_manifest(root: Path) -> dict | None:
    for path in (root / "PACKAGE_MANIFEST.json", root / "parallel" / "OWNER_ONECLICK" / "package_manifest.json"):
        if not path.is_file():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if isinstance(value, dict):
            return value
    return None


def _visible_overlay_package_gate(root: Path) -> tuple[bool, str, dict | None]:
    manifest = _read_package_manifest(root)
    if manifest is None:
        return False, "正式包清单缺失；不会回退到 diagnostic-only 路径。", None
    components = manifest.get("components")
    render = components.get("renderAuthorityV3") if isinstance(components, dict) else None
    if not isinstance(render, dict):
        return False, "正式包没有选择 Alpha 顶部显示 runtime。", manifest
    source = str(manifest.get("sourceCommit") or "")
    slice_a = str(render.get("sliceARuntimeCommit") or "")
    checks = [
        (re.fullmatch(r"[0-9a-f]{40}", source) is not None, "package source commit 未固定"),
        (re.fullmatch(r"[0-9a-f]{40}", slice_a) is not None, "Slice A exact runtime commit 尚未 pin"),
        (render.get("selectedNormalPath") == "production-top-overlay", "正式 normal path 未选择 production top overlay"),
        (render.get("productionOverlayEnabled") is True, "productionOverlayEnabled 仍未启用"),
        (render.get("productionOverlaySuppressed") is False, "productionOverlaySuppressed 仍在启用或未证明为 false"),
        (render.get("diagnosticOnly") is False, "当前候选仍可能是 diagnostic-only"),
        (render.get("whiteAcquisitionMarkerIsProduct") is False, "白色 acquisition marker 不能作为正式产品"),
        (render.get("automaticSeedRequiredBeforeFallback") is True, "零点击自动获取必须先于点击 fallback"),
        (int(render.get("ownerClickFallbackMaximumPerAuthorityGeneration", -1)) == 1, "一次点击 fallback 上限未锁定为 1"),
    ]
    safety = manifest.get("safety") if isinstance(manifest.get("safety"), dict) else {}
    checks += [
        (safety.get("readOnly") is True, "readOnly 未保持 true"),
        (safety.get("ramWrites") == 0, "ramWrites 未保持 0"),
        (safety.get("inputInjection") is False, "inputInjection 未保持 false"),
        (safety.get("manualCalibration") is False, "manualCalibration 必须为 false"),
        (safety.get("legacyProjectionSelected") is False, "legacyProjectionSelected 必须为 false"),
    ]
    for ok, reason in checks:
        if not ok:
            return False, reason, manifest
    return True, f"production top overlay 已选择；Slice A={slice_a[:12]} source={source[:12]}", manifest


class ChineseToolkit(toolkit.Toolkit):
    """Owner-facing integration surface for the immutable packaged runtime."""

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

    def proof(self):
        print("\n[打开 WOF 头顶显示]")
        ready, reason, _manifest = _visible_overlay_package_gate(self.root)
        if not ready:
            print("BLOCKED：当前安装包还没有选中可发布的 production 顶部显示路径。")
            print("不会启动旧 diagnostic-only、空浏览器成功态或 production overlay 被 suppress 的路径。")
            print("技术详情：" + reason)
            return
        entry = self.root / "parallel/PYLAUNCH/render_authority_measurement_entry.py"
        if not entry.is_file():
            print("BLOCKED：正式顶部显示入口缺失。请先选择 1“更新项目”。")
            return
        pyw = Path(toolkit.sys.executable).with_name("pythonw.exe")
        exe = pyw if toolkit.os.name == "nt" and pyw.exists() else Path(toolkit.sys.executable)
        cmd = [str(exe), str(entry), "--root", str(self.root), "--output-root", str(self.results)]
        try:
            toolkit.subprocess.Popen(cmd, cwd=str(entry.parent), env=toolkit.os.environ.copy())
        except Exception as exc:
            print("BLOCKED：WOF 头顶显示启动失败。")
            print("游戏本身没有受到影响。")
            print("技术详情：" + str(exc))
            return
        print("WOF 头顶显示已启动。右下角托盘状态会持续可见；不需要打开终端或 DevTools。")
        print("菜单 6 会优先复用已经打开的 WOF；没有可复用会话时会进入正常 WOF 等待，不会把空白浏览器当成功。")
        print("状态顺序会明确显示：等待 WOF → 正在自动找 P1 → 安全唯一时 0 点击进入头顶显示。")
        print("自动获取失败后才允许最多一次点击场景中 P1 真实头部；白色 acquisition marker 不是正式产品。")
        print("正式状态会显示“头顶已显示”；识别暂时丢失时显示“暂时丢失，恢复中”，标记隐藏，恢复后自动重现。")
        print("若正式 production overlay 未建立或 authority 不安全，会显示 BLOCKED，不会回退到旧 projection/人工 calibration。")
        print("只读模式：开启 / 游戏内存写入：0 / 输入注入：关闭。")
        print("本次选择：" + reason)

    def package(self):
        print("\n[自动整理并打包结果]")
        try:
            return super().package()
        except Exception as exc:
            print("结果打包没有完成。原始诊断/验证文件都仍然保留。")
            print("游戏本身没有受到影响。")
            print(f"技术详情：{exc}")
            return None


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
