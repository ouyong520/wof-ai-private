from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fleet_manager import FleetManager


STATUS_ZH = {
    "OK": "已就绪",
    "WAIT": "等待中",
    "DOWN": "未连接",
    "READY": "已就绪",
    "MISSING": "缺失",
}


def status_zh(value: object) -> str:
    text = str(value or "WAIT").upper()
    return STATUS_ZH.get(text, str(value or "等待中"))


def human_error(detail: object) -> str:
    text = str(detail or "").strip()
    low = text.lower()
    if not text:
        return ""
    if "executable not found" in low:
        return "未找到 Chrome 或 Edge 浏览器。"
    if "already in use" in low or "port" in low and "use" in low:
        return "浏览器调试端口已被占用。"
    if "browser exited" in low:
        return "这个浏览器房间已经退出。"
    if "target list unavailable" in low:
        return "暂时无法读取这个浏览器房间的页面状态。"
    if "target list malformed" in low:
        return "浏览器返回的页面状态格式异常。"
    if "unknown fleet instance" in low:
        return "没有找到这个房间编号。"
    return "这个浏览器房间出现了问题，但其他房间不会受到影响。"


def print_error(detail: object, *, action: str = "操作") -> None:
    print(f"{action}未完成。")
    print(human_error(detail))
    print("游戏本身没有受到影响。")
    print(f"技术详情：{detail}")


class ChineseFleetManager(FleetManager):
    def configure_interactive(self) -> None:
        current = self.settings
        print("WOF 多房间浏览器管理器 — 首次设置")
        print("如果暂时不想自动打开游戏页面，网址直接留空即可。")
        browser = input(f"浏览器 [auto/chrome/edge]（当前：{current.browser}）：").strip().lower()
        if browser in {"auto", "chrome", "edge"}:
            current.browser = browser
        url = input(f"WOF 游戏/页面网址（当前：{current.game_url or '未设置'}）：").strip()
        if url:
            current.game_url = url
        elif current.game_url is None:
            current.game_url = None
        current.save(self.settings_path)
        self.settings = current
        print(f"设置已保存：{self.settings_path}")

    def print_status(self) -> None:
        self.refresh_status()
        self.write_manifest()
        print()
        print("WOF 多房间浏览器管理器")
        print(f"浏览器程序：{self.browser_executable or '自动查找'}")
        print(f"共享状态文件：{self.manifest_path}")
        print("只读模式：开启｜游戏内存写入：0｜游戏输入注入：无｜window.Worker 替换：无")
        print("-" * 88)
        print("编号  端口   浏览器      WOF 页面     Worker       PID      独立配置")
        for runtime in sorted(self.instances.values(), key=lambda item: item.instance_id):
            browser = "已连接" if runtime.browser_ok else "未连接"
            page = "已找到" if runtime.page_ok else "等待中"
            worker = "已找到" if runtime.worker_ok else "等待中"
            pid = str(runtime.pid or "-")
            print(
                f"{runtime.instance_id:>2}    {runtime.port:<5}  {browser:<8}  {page:<10}  "
                f"{worker:<10}  {pid:<7}  {runtime.profile_dir.name}"
            )
            if runtime.last_error:
                print(f"      {human_error(runtime.last_error)}")
                print(f"      技术详情：{runtime.last_error}")
        print("-" * 88)
        print(
            f"浏览器实例：{len(self.instances)}｜已连接：{sum(1 for x in self.instances.values() if x.browser_ok)}｜"
            f"WOF 页面已找到：{sum(1 for x in self.instances.values() if x.page_ok)}｜"
            f"Worker 已找到：{sum(1 for x in self.instances.values() if x.worker_ok)}"
        )

    def interactive(self) -> None:
        self.print_status()
        print("[S] 刷新状态  [R] 重启一个房间  [X] 关闭一个房间  [A] 全部关闭并退出  [Q] 退出管理器但保留浏览器")
        while True:
            command = input("请输入命令：").strip().lower()
            if command in {"s", "status", "状态", "刷新"}:
                self.print_status()
            elif command in {"r", "restart", "重启"}:
                value = input("请输入要重启的房间编号：").strip()
                try:
                    self.restart(int(value))
                except Exception as exc:
                    print_error(exc, action="重启")
                self.print_status()
            elif command in {"x", "close", "stop", "关闭"}:
                value = input("请输入要关闭的房间编号：").strip()
                try:
                    self.stop_one(int(value))
                except Exception as exc:
                    print_error(exc, action="关闭")
                self.print_status()
            elif command in {"a", "all", "stop-all", "全部"}:
                print("正在关闭全部浏览器房间……")
                self.stop_all()
                print("全部浏览器房间已关闭。")
                break
            elif command in {"q", "quit", "退出"}:
                print("管理器已退出，已打开的浏览器房间会继续保留。")
                break
            elif command:
                print("无法识别这个命令。请输入 S、R、X、A 或 Q。")
        self._stop.set()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WOF 多房间浏览器管理器（独立配置 + 本机 CDP）")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start", help="启动多个互相独立的浏览器房间")
    start.add_argument("count", type=int, help="要启动的浏览器房间数量（1-50）")
    start.add_argument("--interactive", action="store_true", help="启动后进入中文管理菜单")
    start.add_argument("--game-url", help="可选：启动时打开的 WOF 页面网址")
    start.add_argument("--browser", choices=["auto", "chrome", "edge"], help="浏览器类型")
    start.add_argument("--base-port", type=int, help="第一个本机 CDP 端口")
    sub.add_parser("configure", help="保存浏览器和游戏网址默认设置")
    sub.add_parser("status", help="查看已保存的浏览器集群状态")
    return parser.parse_args()


def status_from_manifest(path: Path) -> int:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("暂时没有可用的浏览器集群状态。")
        print("请先双击 RUN_WOF_FLEET.cmd 启动浏览器房间。")
        print(f"技术详情：{exc}")
        return 1
    instances = payload.get("instances") if isinstance(payload, dict) else None
    if not isinstance(instances, list):
        print("浏览器集群状态文件格式异常。")
        print(f"技术详情：{path}")
        return 1
    print("WOF 多房间浏览器状态")
    print(f"状态文件：{path}")
    print("只读模式：开启｜游戏内存写入：0｜游戏输入注入：无｜window.Worker 替换：无")
    for item in instances:
        if not isinstance(item, dict):
            continue
        st = item.get("status") if isinstance(item.get("status"), dict) else {}
        print(
            f"房间 {item.get('id', '?')}｜端口 {item.get('port', '?')}｜"
            f"浏览器：{status_zh(st.get('browser'))}｜页面：{status_zh(st.get('page'))}｜Worker：{status_zh(st.get('worker'))}"
        )
        if st.get("error"):
            print(f"  {human_error(st.get('error'))}")
            print(f"  技术详情：{st.get('error')}")
    return 0


def main() -> int:
    args = parse_args()
    manager = ChineseFleetManager()
    if args.command == "configure":
        manager.configure_interactive()
        return 0
    if args.command == "status":
        return status_from_manifest(manager.manifest_path)
    if args.browser:
        manager.settings.browser = args.browser
    if args.game_url:
        manager.settings.game_url = args.game_url
    if args.base_port:
        manager.settings.base_port = args.base_port
    manager.settings.save(manager.settings_path)
    try:
        print(f"正在启动 {args.count} 个互相独立的 WOF 浏览器房间……")
        manager.start(args.count)
    except (RuntimeError, ValueError) as exc:
        print_error(exc, action="启动浏览器集群")
        return 2
    if args.interactive:
        try:
            manager.interactive()
        except KeyboardInterrupt:
            print()
            print("浏览器管理器已停止；已打开的浏览器窗口会继续保留。")
            manager._stop.set()
    else:
        manager.print_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
