from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

from .state import LauncherStatus, StatusStore

STATE_ZH = {"CONNECTED": "已连接", "WAITING_WOF": "等待 WOF", "ERROR": "连接异常", "DISCONNECTED": "未连接"}


class TkUiDispatcher:
    """Own exactly one Tk interpreter/mainloop on exactly one thread.

    pystray menu callbacks may arrive on arbitrary threads. They must never create a
    Tk root/messagebox themselves (Python 3.13 can raise "main thread is not in main
    loop"). All Owner UI work is queued here and executed by the thread that owns the
    Tk mainloop. Errors are retained rather than silently killing a notification thread.
    """

    _STOP = object()

    def __init__(self, root_factory: Callable[[], object] | None = None) -> None:
        self._root_factory = root_factory or tk.Tk
        self._queue: queue.Queue[object] = queue.Queue()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()
        self._closed = threading.Event()
        self._closing = False
        self._last_error: str | None = None
        self._executed = 0

    def start(self) -> bool:
        with self._lock:
            if self._closing:
                return False
            if self._thread and self._thread.is_alive():
                return True
            self._ready.clear(); self._closed.clear()
            self._thread = threading.Thread(target=self._run, name="wof-tk-mainloop", daemon=True)
            self._thread.start()
        self._ready.wait(2.0)
        return self._thread is not None and self._thread.is_alive() and self._last_error is None

    def submit(self, fn: Callable[[object], None]) -> bool:
        if not callable(fn) or not self.start():
            return False
        self._queue.put(fn)
        return True

    def _run(self) -> None:
        root = None
        try:
            root = self._root_factory()
            self._root = root
            try: root.withdraw()
            except Exception: pass
            root.after(0, self._drain)
            self._ready.set()
            root.mainloop()
        except Exception as exc:
            self._last_error = f"{type(exc).__name__}: {exc}"
            self._ready.set()
        finally:
            if root is not None:
                try: root.destroy()
                except Exception: pass
            self._closed.set()

    def _drain(self) -> None:
        root = getattr(self, "_root", None)
        if root is None:
            return
        for _ in range(32):
            try: item = self._queue.get_nowait()
            except queue.Empty: break
            if item is self._STOP:
                try: root.quit()
                except Exception: pass
                return
            try:
                item(root)  # type: ignore[operator]
                self._executed += 1
            except Exception as exc:
                self._last_error = f"{type(exc).__name__}: {exc}"
        # close() is deliberately cross-thread: it may only enqueue _STOP, never call
        # Tk. Keep the owner-thread drain scheduled until that sentinel is consumed.
        # Conditioning this on _closing creates a race where close() sets _closing
        # just after an empty queue check, stranding _STOP and leaving mainloop alive.
        try: root.after(25, self._drain)
        except Exception as exc:
            self._last_error = f"{type(exc).__name__}: {exc}"

    def close(self) -> None:
        with self._lock:
            if self._closing:
                thread = self._thread
            else:
                self._closing = True
                thread = self._thread
                if thread and thread.is_alive(): self._queue.put(self._STOP)
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=2.0)

    def status(self) -> dict[str, object]:
        t = self._thread
        return {"running": bool(t and t.is_alive()), "closing": self._closing, "executed": self._executed, "lastError": self._last_error}


class TrayApp:
    def __init__(self, status: StatusStore, *, reconnect: Callable[[], None], open_game: Callable[[], None], quit_app: Callable[[], None]) -> None:
        self.status = status; self.reconnect_action = reconnect; self.open_game_action = open_game; self.quit_action = quit_app
        self.icon = None; self._ui = TkUiDispatcher(); self._settings_window_ref = None

    def _make_image(self, state: str):
        from PIL import Image, ImageDraw
        colors = {"CONNECTED": (36, 160, 80, 255), "WAITING_WOF": (214, 154, 30, 255), "ERROR": (190, 55, 55, 255), "DISCONNECTED": (110, 110, 110, 255)}
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0)); draw = ImageDraw.Draw(image)
        draw.ellipse((4, 4, 60, 60), fill=colors.get(state, colors["DISCONNECTED"])); draw.text((18, 21), "W", fill=(255, 255, 255, 255)); return image

    @staticmethod
    def _found(value: bool) -> str: return "已找到" if value else "未找到"

    @staticmethod
    def _connected(value: bool) -> str: return "已连接" if value else "未连接"

    @staticmethod
    def _human_hint(s: LauncherStatus) -> str:
        if s.last_error: return s.last_error
        if not s.browser_connected: return "Launcher 尚未连接到浏览器。游戏本身没有受到影响。"
        if not s.wof_page_found: return "尚未找到 WOF 游戏页面。游戏本身没有受到影响。请保持专用浏览器打开。"
        if not s.worker_found: return "未找到 WOF 游戏 Worker。游戏本身没有受到影响。请保持游戏房间打开，然后点击“重新连接”。"
        if not (s.wasm_module_found and s.heap_found): return "已找到 WOF Worker，但 WASM / 内存尚未就绪。游戏本身没有受到影响。"
        if not s.world_921031: return "已找到 WASM / 内存，但游戏版本尚未通过 World 921031 精确校验。游戏本身没有受到影响。"
        if s.alpha_requested and not s.alpha_running: return "World 921031 已确认；Alpha 正在严格验证本地身份或继续头顶校准。请按画面提示继续，不要重启验证流程。"
        return "自动验证已通过。请确认游戏仍可正常进入房间并操作。"

    @classmethod
    def _format_status(cls, s: LauncherStatus) -> str:
        lines = [
            f"连接状态：{STATE_ZH.get(s.state, s.state)}",
            f"浏览器：{cls._connected(s.browser_connected)}" + (f"（{s.browser_name}）" if s.browser_name else ""),
            f"WOF 页面：{cls._found(s.wof_page_found)}", f"Worker：{cls._found(s.worker_found)}",
            f"WASM / 内存：{cls._found(s.wasm_module_found and s.heap_found)}",
            f"游戏版本：{'World 921031 已确认' if s.world_921031 else '未确认'}",
            "只读模式：开启", f"游戏内存写入：{s.ram_writes}", f"输入注入：{'关闭' if not s.input_injection else '异常'}", "", cls._human_hint(s),
        ]
        progress = s.last_calibration_progress
        if isinstance(progress, dict) and not progress.get("terminal"):
            samples = progress.get("samples"); target = progress.get("targetSamples"); reason = progress.get("reason") or progress.get("recoveryState")
            lines.extend(("", f"头顶校准：samples {samples if samples is not None else '--'} / {target if target is not None else '--'} · {reason or '进行中'}"))
            if progress.get("actionZh"): lines.append(str(progress["actionZh"]))
            if progress.get("nextCommandZh"): lines.append(str(progress["nextCommandZh"]))
        if s.discovery_path: lines.extend(("", f"发现路径：{s.discovery_path}"))
        if s.identity_reason: lines.append(f"技术详情：{s.identity_reason}")
        if s.page_url: lines.append(f"页面地址：{s.page_url}")
        if s.worker_url: lines.append(f"Worker 地址：{s.worker_url}")
        if s.identity_sha256: lines.append(f"World SHA-256：{s.identity_sha256}")
        return "\n".join(lines)

    def refresh(self) -> None:
        if not self.icon: return
        snap = self.status.get()
        try:
            self.icon.icon = self._make_image(snap.state); self.icon.title = f"WOF Future Danger - {STATE_ZH.get(snap.state, snap.state)} - 只读模式"; self.icon.update_menu()
        except Exception: pass

    def _menu(self):
        import pystray
        def text(fn): return lambda _item: fn(self.status.get())
        return pystray.Menu(
            pystray.MenuItem("打开状态", lambda *_: self.show_diagnostics(), default=True),
            pystray.MenuItem(text(lambda s: f"连接状态：{STATE_ZH.get(s.state, s.state)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"浏览器：{self._connected(s.browser_connected)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"WOF 页面：{self._found(s.wof_page_found)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"Worker：{self._found(s.worker_found)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"WASM / 内存：{self._found(s.wasm_module_found and s.heap_found)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"游戏版本：{'World 921031 已确认' if s.world_921031 else '未确认'}"), None, enabled=False),
            pystray.MenuItem("只读模式：开启 / 游戏内存写入：0", None, enabled=False), pystray.Menu.SEPARATOR,
            pystray.MenuItem("重新连接", lambda *_: self.reconnect_action()), pystray.MenuItem("打开 / 启动游戏浏览器", lambda *_: self.open_game_action()),
            pystray.MenuItem("设置", lambda *_: self.show_settings()), pystray.MenuItem("状态与诊断", lambda *_: self.show_diagnostics()), pystray.Menu.SEPARATOR,
            pystray.MenuItem("Future Danger（预留）", None, enabled=False), pystray.MenuItem("HUD（预留）", None, enabled=False), pystray.MenuItem("声音（预留）", None, enabled=False),
            pystray.MenuItem("快捷键（预留）", None, enabled=False), pystray.MenuItem("辅助模式（未实现）", None, enabled=False), pystray.Menu.SEPARATOR,
            pystray.MenuItem("关于", lambda *_: self.show_about()), pystray.MenuItem("退出", lambda *_: self._quit()),
        )

    def run(self) -> None:
        import pystray
        snap = self.status.get(); self.icon = pystray.Icon("wof_future_danger", self._make_image(snap.state), "WOF Future Danger - 只读模式", self._menu())
        try: self.icon.run()
        finally: self._ui.close()

    def _quit(self) -> None:
        self.quit_action()
        if self.icon: self.icon.stop()
        self._ui.close()

    def show_settings(self) -> None:
        self._ui.submit(self._settings_window)

    def _settings_window(self, root) -> None:
        existing = self._settings_window_ref
        try:
            if existing is not None and existing.winfo_exists(): existing.deiconify(); existing.lift(); existing.focus_force(); return
        except Exception: self._settings_window_ref = None
        win = tk.Toplevel(root); self._settings_window_ref = win; win.title("WOF Future Danger - 设置"); win.geometry("620x460")
        notebook = ttk.Notebook(win); notebook.pack(fill="both", expand=True, padx=10, pady=10)
        general = ttk.Frame(notebook); notebook.add(general, text="常规")
        ttk.Label(general, text="工作方式：游戏正常启动后，Launcher 通过本机 CDP 只读连接。").pack(anchor="w", padx=12, pady=12)
        ttk.Label(general, text="浏览器配置和游戏地址由启动参数管理；普通使用无需手工设置。").pack(anchor="w", padx=12)
        ttk.Label(general, text="默认最小化到系统托盘，不显示大窗口。").pack(anchor="w", padx=12, pady=(10, 0)); ttk.Button(general, text="立即重新连接", command=self.reconnect_action).pack(anchor="w", padx=12, pady=12)
        future = ttk.Frame(notebook); notebook.add(future, text="Future Danger"); ttk.Label(future, text="Future Danger / HUD / 提示音：为后续安全集成预留，当前未启用。").pack(anchor="w", padx=12, pady=12)
        hotkeys = ttk.Frame(notebook); notebook.add(hotkeys, text="快捷键"); ttk.Label(hotkeys, text="仅预留。当前版本没有游戏快捷键，也没有任何输入注入。").pack(anchor="w", padx=12, pady=12)
        assist = ttk.Frame(notebook); notebook.add(assist, text="辅助模式"); ttk.Label(assist, text="未实现。一键出招 / 指令注入不属于当前 Launcher 范围。").pack(anchor="w", padx=12, pady=12)
        diagnostics = ttk.Frame(notebook); notebook.add(diagnostics, text="状态与诊断"); text = tk.Text(diagnostics, wrap="word", height=16); text.pack(fill="both", expand=True, padx=10, pady=10)
        snap = self.status.get(); text.insert("1.0", self._format_status(snap) + "\n\n技术诊断 JSON（仅用于反馈）：\n" + json.dumps(snap.snapshot(), indent=2, ensure_ascii=False)); text.configure(state="disabled")
        ttk.Label(win, text="只读模式 · 游戏内存写入 0 · 输入注入关闭").pack(pady=(0, 8))
        win.protocol("WM_DELETE_WINDOW", win.withdraw)

    def show_diagnostics(self) -> None:
        body = self._format_status(self.status.get())
        self._message("WOF 状态与诊断", body)

    def show_about(self) -> None:
        self._message("关于", "WOF Future Danger Python Launcher\n本机 CDP 只读连接\n不会写游戏内存，不会注入游戏输入。")

    def _message(self, title: str, body: str) -> None:
        def show(root) -> None:
            from tkinter import messagebox
            messagebox.showinfo(title, body, parent=root)
        self._ui.submit(show)
