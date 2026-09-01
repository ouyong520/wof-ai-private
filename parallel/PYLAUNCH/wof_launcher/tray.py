from __future__ import annotations

import json
import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

from .state import LauncherStatus, StatusStore


class TrayApp:
    def __init__(self, status: StatusStore, *, reconnect: Callable[[], None], open_game: Callable[[], None], quit_app: Callable[[], None]) -> None:
        self.status = status
        self.reconnect_action = reconnect
        self.open_game_action = open_game
        self.quit_action = quit_app
        self.icon = None
        self._settings_thread: threading.Thread | None = None

    def _make_image(self, state: str):
        from PIL import Image, ImageDraw

        colors = {
            "CONNECTED": (36, 160, 80, 255),
            "WAITING_WOF": (214, 154, 30, 255),
            "ERROR": (190, 55, 55, 255),
            "DISCONNECTED": (110, 110, 110, 255),
        }
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((4, 4, 60, 60), fill=colors.get(state, colors["DISCONNECTED"]))
        draw.text((18, 21), "W", fill=(255, 255, 255, 255))
        return image

    @staticmethod
    def _yes(value: bool) -> str:
        return "OK" if value else "--"

    def refresh(self) -> None:
        if not self.icon:
            return
        snap = self.status.get()
        try:
            self.icon.icon = self._make_image(snap.state)
            self.icon.title = f"WOF Future Danger - {snap.state} - READ ONLY"
            self.icon.update_menu()
        except Exception:
            pass

    def _menu(self):
        import pystray

        def text(fn):
            return lambda _item: fn(self.status.get())

        return pystray.Menu(
            pystray.MenuItem("Open status", lambda *_: self.show_diagnostics(), default=True),
            pystray.MenuItem(text(lambda s: f"Connection: {s.state}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"Browser: {self._yes(s.browser_connected)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"WOF page: {self._yes(s.wof_page_found)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"Worker: {self._yes(s.worker_found)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"WASM / heap: {self._yes(s.wasm_module_found and s.heap_found)}"), None, enabled=False),
            pystray.MenuItem(text(lambda s: f"World 921031: {self._yes(s.world_921031)}"), None, enabled=False),
            pystray.MenuItem("READ ONLY / RAM writes: 0", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Reconnect", lambda *_: self.reconnect_action()),
            pystray.MenuItem("Launch / Open game", lambda *_: self.open_game_action()),
            pystray.MenuItem("Settings", lambda *_: self.show_settings()),
            pystray.MenuItem("Diagnostics / Logs", lambda *_: self.show_diagnostics()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Future Danger (reserved)", None, enabled=False),
            pystray.MenuItem("HUD (reserved)", None, enabled=False),
            pystray.MenuItem("Sound (reserved)", None, enabled=False),
            pystray.MenuItem("Hotkeys (reserved)", None, enabled=False),
            pystray.MenuItem("Assist Mode (NOT IMPLEMENTED)", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("About", lambda *_: self.show_about()),
            pystray.MenuItem("Quit", lambda *_: self._quit()),
        )

    def run(self) -> None:
        import pystray

        snap = self.status.get()
        self.icon = pystray.Icon("wof_future_danger", self._make_image(snap.state), "WOF Future Danger - READ ONLY", self._menu())
        self.icon.run()

    def _quit(self) -> None:
        self.quit_action()
        if self.icon:
            self.icon.stop()

    def show_settings(self) -> None:
        if self._settings_thread and self._settings_thread.is_alive():
            return
        self._settings_thread = threading.Thread(target=self._settings_window, name="wof-settings", daemon=True)
        self._settings_thread.start()

    def _settings_window(self) -> None:
        root = tk.Tk()
        root.title("WOF Future Danger - Settings")
        root.geometry("560x420")
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        general = ttk.Frame(notebook); notebook.add(general, text="General")
        ttk.Label(general, text="Foundation mode: attach through localhost CDP after the game starts normally.").pack(anchor="w", padx=12, pady=12)
        ttk.Label(general, text="Browser profile / game URL are configured by CLI in this foundation build.").pack(anchor="w", padx=12)
        ttk.Label(general, text="Start minimized: tray is the default behavior.").pack(anchor="w", padx=12, pady=(10, 0))
        ttk.Label(general, text="Start with Windows: reserved for packaging stage.").pack(anchor="w", padx=12)
        ttk.Button(general, text="Reconnect now", command=self.reconnect_action).pack(anchor="w", padx=12, pady=12)

        future = ttk.Frame(notebook); notebook.add(future, text="Future Danger")
        ttk.Label(future, text="Future Danger toggle: reserved for post-foundation integration.").pack(anchor="w", padx=12, pady=12)
        ttk.Label(future, text="HUD / warning sound options: reserved, not active.").pack(anchor="w", padx=12)

        hotkeys = ttk.Frame(notebook); notebook.add(hotkeys, text="Hotkeys")
        ttk.Label(hotkeys, text="Reserved only. No gameplay hotkeys or input injection exist in this build.").pack(anchor="w", padx=12, pady=12)

        assist = ttk.Frame(notebook); notebook.add(assist, text="Assist Mode")
        ttk.Label(assist, text="NOT IMPLEMENTED - one-key moves / command injection are outside foundation scope.").pack(anchor="w", padx=12, pady=12)

        diagnostics = ttk.Frame(notebook); notebook.add(diagnostics, text="Diagnostics")
        text = tk.Text(diagnostics, wrap="word", height=16)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        snap = self.status.get().snapshot()
        text.insert("1.0", json.dumps(snap, indent=2, ensure_ascii=False))
        text.configure(state="disabled")

        ttk.Label(root, text="READ ONLY · RAM writes 0 · Input injection disabled").pack(pady=(0, 8))
        root.mainloop()

    def show_diagnostics(self) -> None:
        snap: LauncherStatus = self.status.get()
        self._message("Diagnostics", json.dumps(snap.snapshot(), indent=2, ensure_ascii=False))

    def show_about(self) -> None:
        self._message("About", "WOF Future Danger Python Launcher Foundation\nRead-only CDP attachment prototype\nAssist Mode is not implemented.")

    @staticmethod
    def _message(title: str, body: str) -> None:
        def run() -> None:
            root = tk.Tk(); root.withdraw()
            from tkinter import messagebox
            messagebox.showinfo(title, body)
            root.destroy()
        threading.Thread(target=run, daemon=True).start()
