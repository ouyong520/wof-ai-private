from __future__ import annotations

from typing import Any, Callable

from .state import StatusStore
from .tray import TrayApp

MEASUREMENT_STATE_ZH = {
    "STARTING": "正在启动 / 等待 WOF",
    "WAITING_FOR_WOF": "等待 WOF",
    "EXACT_WORLD_LOCKED": "World 921031 已锁定",
    "CAMERA_PREPARING": "正在自动找 P1",
    "HEAD_ACQUIRING": "正在自动找 P1",
    "ONE_CLICK_REQUIRED": "需要一次点击 P1 真实头部",
    "HEAD_TRACKING": "正在建立头顶显示",
    "MEASURING": "正在建立头顶显示",
    "RUNNING": "正在建立头顶显示",
    "RUNTIME_REDISCOVERY": "暂时丢失，恢复中",
    "COMPLETE": "本次运行完成",
    "BLOCKED": "BLOCKED",
}

LIVE_ACCEPTANCE_PHASE = "P1_DRAW_READY_ENEMY_LIVE_CHECK"


class MeasurementPublisher:
    def __init__(self, store: StatusStore, on_change: Callable[[], None] | None = None) -> None:
        self.store = store
        self.on_change = on_change
        self._payload: dict[str, Any] = {}

    def publish(self, state: str, **payload: Any) -> None:
        self._payload = {**self._payload, **payload, "measurementState": state}
        exact = state not in {"STARTING", "WAITING_FOR_WOF", "BLOCKED"} and bool(self._payload.get("worldSha256"))
        updates = {
            "state": state,
            "browser_connected": bool(self._payload.get("browserConnected")),
            "browser_name": self._payload.get("browserName"),
            "browser_endpoint": self._payload.get("browserEndpoint"),
            "wof_page_found": bool(self._payload.get("wofPageFound")),
            "page_target_id": self._payload.get("pageTargetId"),
            "page_url": self._payload.get("pageUrl"),
            "worker_found": bool(self._payload.get("workerFound")),
            "worker_target_id": self._payload.get("workerTargetId"),
            "wasm_module_found": bool(self._payload.get("wasmFound")),
            "heap_found": bool(self._payload.get("heapFound")),
            "world_921031": exact,
            "identity_sha256": self._payload.get("worldSha256"),
            "alpha_status": {"renderAuthorityV3": dict(self._payload)},
            "read_only": True,
            "ram_writes": 0,
            "input_injection": False,
            "last_error": self._payload.get("blockedReason") if state == "BLOCKED" else None,
        }
        self.store.update(**updates)
        if self.on_change:
            try:
                self.on_change()
            except Exception:
                pass


class MeasurementTrayApp(TrayApp):
    def __init__(self, status: StatusStore, *, quit_app: Callable[[], None]) -> None:
        super().__init__(status, reconnect=lambda: None, open_game=lambda: None, quit_app=quit_app)
        self._last_terminal = None

    @staticmethod
    def _measurement(s) -> dict[str, Any]:
        a = s.alpha_status if isinstance(s.alpha_status, dict) else {}
        v = a.get("renderAuthorityV3") if isinstance(a, dict) else None
        return v if isinstance(v, dict) else {}

    @staticmethod
    def _overlay_proof(m: dict[str, Any], vis: dict[str, Any]) -> tuple[bool, bool, dict[str, Any]]:
        del vis
        overlay = m.get("productionOverlay") if isinstance(m.get("productionOverlay"), dict) else {}
        visible = overlay.get("visible") is True
        drawn = bool(
            visible
            and int(overlay.get("drawCount") or 0) > 0
            and overlay.get("drawHooked") is True
            and overlay.get("drawnCurrentTracker") is True
            and overlay.get("diagnosticMarkerSuppressed") is True
            and overlay.get("readOnly") is True
            and overlay.get("ramWrites") == 0
            and overlay.get("inputInjection") is False
        )
        return visible, drawn, overlay

    @staticmethod
    def _relative_enemy(m: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
        direct = m.get("relativeEnemy")
        if isinstance(direct, dict):
            return direct
        nested = overlay.get("relativeEnemy")
        return nested if isinstance(nested, dict) else {}

    @classmethod
    def _owner_product_state(cls, s) -> str:
        m = cls._measurement(s)
        state = str(m.get("measurementState") or s.state)
        vis = m.get("visual") if isinstance(m.get("visual"), dict) else {}
        visual_state = str(vis.get("state") or "")
        if state == "BLOCKED":
            return "BLOCKED"
        if state in {"STARTING", "WAITING_FOR_WOF"}:
            return "等待 WOF"
        if state == "ONE_CLICK_REQUIRED" or visual_state == "ONE_CLICK_REQUIRED":
            return "需要一次点击 P1 真实头部"
        if (
            state == "RUNTIME_REDISCOVERY"
            or visual_state in {"REACQUIRING", "LOST_TIMEOUT"}
            or int(vis.get("lostFrames") or 0) > 0
        ):
            return "暂时丢失，恢复中"
        overlay_visible, overlay_drawn, _overlay = cls._overlay_proof(m, vis)
        if overlay_visible and overlay_drawn:
            return "头顶已显示"
        if state in {"EXACT_WORLD_LOCKED", "CAMERA_PREPARING", "HEAD_ACQUIRING", "HEAD_TRACKING", "MEASURING", "RUNNING"}:
            return "正在自动找 P1"
        if visual_state in {"CAMERA_PREPARING", "HEAD_ACQUIRING", "HEAD_TRACKING"}:
            return "正在自动找 P1"
        return "BLOCKED"

    @classmethod
    def _format_status(cls, s) -> str:
        m = cls._measurement(s)
        owner_state = cls._owner_product_state(s)
        lines = [
            f"产品状态：{owner_state}",
            f"浏览器：{'已连接' if s.browser_connected else '未连接'}" + (f"（{s.browser_name}）" if s.browser_name else ""),
            f"WOF 页面：{'已找到' if s.wof_page_found else '未找到'}",
            f"Worker / WASM：{'已找到' if s.worker_found and s.wasm_module_found and s.heap_found else '等待中'}",
            f"游戏版本：{'World 921031 已确认' if s.world_921031 else '未确认'}",
            "只读模式：开启",
            "游戏内存写入：0",
            "输入注入：关闭",
        ]
        vis = m.get("visual") if isinstance(m.get("visual"), dict) else {}
        if vis:
            lines += [
                "",
                f"P1 状态：{MEASUREMENT_STATE_ZH.get(str(vis.get('state') or ''), str(vis.get('state') or ''))}",
                f"头部样本：{vis.get('templateCount', 0)} / {vis.get('templateMinimum', 3)} · 连续跟踪帧：{vis.get('trackedFrames', 0)}",
                f"Owner 点击：{vis.get('ownerClickCount', 0)} / fallback 上限 {vis.get('ownerClickMaximum', 1)}（正常预期 0）",
            ]
            if vis.get("confidence") is not None:
                lines.append(f"视觉置信度：{float(vis['confidence']):.3f}")
            if vis.get("autoSeedAttemptCount") is not None and not vis.get("seedSource"):
                lines.append(f"自动头部 seed：{vis.get('autoSeedAttemptCount', 0)} / {vis.get('autoSeedMaximumFrames', 0)}")
            if vis.get("seedSource"):
                lines.append("头部 seed 来源：" + str(vis.get("seedSource")))
            if vis.get("actionZh"):
                lines.append("当前只需做一件事：" + str(vis["actionZh"]))
            if int(vis.get("lostFrames") or 0) > 0:
                lines.append("产品状态：暂时丢失，恢复中；头顶标记已隐藏，恢复后会自动重新出现。")
        overlay_visible, overlay_drawn, overlay = cls._overlay_proof(m, vis)
        if m.get("productionOverlayEnabled") is not None:
            lines.append("正式头顶显示：" + ("已启用" if m.get("productionOverlayEnabled") is True else "未启用"))
        if m.get("productionOverlaySuppressed") is not None:
            lines.append("正式头顶显示抑制：" + ("是" if m.get("productionOverlaySuppressed") is True else "否"))
        if overlay:
            lines.append("正式头顶可见：" + ("是" if overlay_visible else "否"))
            lines.append("正式头顶实际 draw：" + ("已确认" if overlay_drawn else "等待中"))
            if overlay.get("trackerGeneration") is not None:
                lines.append("P1 draw generation：" + str(overlay.get("trackerGeneration")) + " · baseline=" + str(overlay.get("drawBaseline")))
            if overlay.get("diagnosticMarkerSuppressed") is not None:
                lines.append("diagnostic 白点：" + ("已强制隐藏" if overlay.get("diagnosticMarkerSuppressed") is True else "未确认隐藏"))
            if overlay.get("hudSource"):
                lines.append("正式 renderer：" + str(overlay.get("hudSource")))
        relative_enemy = cls._relative_enemy(m, overlay)
        if relative_enemy:
            fit = relative_enemy.get("fit") if isinstance(relative_enemy.get("fit"), dict) else {}
            lines += [
                "",
                "怪物头顶阶段：中性圆点几何验收（不是最终 1P/2P/3P 标签）",
                f"怪物输入：{relative_enemy.get('inputSource') or 'NONE'}",
                f"怪物实时 drawCount：{int(relative_enemy.get('drawCount') or 0)}（只证明发生绘制，不证明位置正确）",
                "怪物数据 freshness："
                + ("enemy=新鲜" if relative_enemy.get("enemyFresh") is True else "enemy=过期/缺失")
                + " · "
                + ("player=新鲜" if relative_enemy.get("playerFresh") is True else "player=过期/缺失")
                + " · "
                + ("tracker=新鲜" if relative_enemy.get("trackerFresh") is True else "tracker=过期/缺失"),
            ]
            if fit:
                lines.append(
                    "怪物几何 fit："
                    + ("READY" if fit.get("ok") is True else "等待中")
                    + f" · model={fit.get('model')} · sign={fit.get('sign')} · residual={fit.get('residual')} · samples={fit.get('sampleCount')}"
                )
            if relative_enemy.get("suppressedReason"):
                lines.append("怪物未绘制原因：" + str(relative_enemy.get("suppressedReason")))
        if m.get("runtimeRediscoveryCount"):
            lines.append(f"运行时自动重发现：{m['runtimeRediscoveryCount']} 次")
        if m.get("blockedReason"):
            lines += ["", "BLOCKED：" + str(m["blockedReason"])]
        if m.get("browserEntrySource"):
            lines.append("浏览器入口：" + str(m["browserEntrySource"]))
        if s.page_url:
            lines.append("页面地址：" + s.page_url)
        if s.identity_sha256:
            lines.append("World SHA-256：" + s.identity_sha256)
        return "\n".join(lines)

    @classmethod
    def _human_hint(cls, s) -> str:
        m = cls._measurement(s)
        state = str(m.get("measurementState") or s.state)
        vis = m.get("visual") if isinstance(m.get("visual"), dict) else {}
        owner_state = cls._owner_product_state(s)
        if owner_state == "等待 WOF":
            return "请正常进入 WOF；工具会自动等待，不需要 DevTools，也不会把空白浏览器当成功。"
        if owner_state == "正在自动找 P1":
            return str(vis.get("actionZh") or "正在自动识别 P1 身份并定位真实场景头部；安全唯一时无需点击。")
        if owner_state == "需要一次点击 P1 真实头部":
            return str(vis.get("actionZh") or "自动定位无法安全唯一确认；请只点一次场景中 P1 人物真实头部。")
        if owner_state == "暂时丢失，恢复中":
            return "头顶标记已隐藏；保持正常游戏，恢复后会自动重新出现。"
        if owner_state == "头顶已显示":
            return str(vis.get("actionZh") or "maintained Alpha HUD 已确认当前 P1 可见周期发生真实 draw；正常玩即可，丢失时会隐藏并自动恢复。")
        if state == "BLOCKED":
            return str(m.get("blockedReason") or "当前路径已 BLOCKED；不会回退到 diagnostic-only 或 overlay-suppressed 路径。")
        return owner_state

    def _make_image(self, state: str):
        from PIL import Image, ImageDraw
        if state == "COMPLETE":
            fill = (36, 160, 80, 255)
        elif state == "BLOCKED":
            fill = (190, 55, 55, 255)
        elif state in {"WAITING_FOR_WOF", "ONE_CLICK_REQUIRED", "HEAD_ACQUIRING", "RUNTIME_REDISCOVERY"}:
            fill = (214, 154, 30, 255)
        else:
            fill = (55, 120, 190, 255)
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((4, 4, 60, 60), fill=fill)
        draw.text((18, 21), "W", fill=(255, 255, 255, 255))
        return image

    def refresh(self) -> None:
        if not self.icon:
            return
        snap = self.status.get()
        m = self._measurement(snap)
        state = str(m.get("measurementState") or snap.state)
        owner_state = self._owner_product_state(snap)
        try:
            self.icon.icon = self._make_image(state)
            self.icon.title = f"WOF Alpha - {owner_state} - 只读"
            self.icon.update_menu()
            if state in {"COMPLETE", "BLOCKED"} and self._last_terminal != state:
                text = "本次头顶显示运行已完成。" if state == "COMPLETE" else "当前路径已 BLOCKED，请打开状态查看精确原因。"
                try:
                    self.icon.notify(text, "WOF Alpha")
                except Exception:
                    pass
                self._last_terminal = state
        except Exception:
            pass

    def _menu(self):
        import pystray

        def text(fn):
            return lambda _item: fn(self.status.get())

        return pystray.Menu(
            pystray.MenuItem("打开状态", lambda *_: self.show_diagnostics(), default=True),
            pystray.MenuItem(text(lambda s: "产品状态：" + self._owner_product_state(s)), None, enabled=False),
            pystray.MenuItem(text(lambda s: "World 921031：" + ("已确认" if s.world_921031 else "等待中")), None, enabled=False),
            pystray.MenuItem("只读 / RAM writes 0 / input injection 0", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("状态与诊断", lambda *_: self.show_diagnostics()),
            pystray.MenuItem("退出状态工具", lambda *_: self._quit()),
        )
