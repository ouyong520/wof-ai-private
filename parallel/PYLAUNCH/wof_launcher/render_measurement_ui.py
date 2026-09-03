from __future__ import annotations

from typing import Any, Callable

from .state import StatusStore
from .tray import TrayApp

MEASUREMENT_STATE_ZH = {
    "STARTING": "正在启动",
    "WAITING_FOR_WOF": "等待 WOF",
    "EXACT_WORLD_LOCKED": "World 921031 已锁定",
    "CAMERA_PREPARING": "Camera 自动准备",
    "HEAD_ACQUIRING": "正在自动识别/重新识别 P1 头部",
    "ONE_CLICK_REQUIRED": "自动定位未能安全唯一确认，需要一次场景 P1 头部 fallback",
    "HEAD_TRACKING": "P1 头部视觉跟踪中",
    "MEASURING": "采集中",
    "RUNNING": "运行中",
    "RUNTIME_REDISCOVERY": "运行时已更换，正在重新发现",
    "COMPLETE": "采集完成",
    "BLOCKED": "采集受阻",
}

class MeasurementPublisher:
    def __init__(self, store: StatusStore, on_change: Callable[[], None] | None = None) -> None:
        self.store=store; self.on_change=on_change; self._payload:dict[str,Any]={}
    def publish(self, state: str, **payload: Any) -> None:
        self._payload={**self._payload, **payload, "measurementState":state}
        exact=state not in {"STARTING","WAITING_FOR_WOF","BLOCKED"} and bool(self._payload.get("worldSha256"))
        updates={
            "state":state,
            "browser_connected":bool(self._payload.get("browserConnected")),
            "browser_name":self._payload.get("browserName"),
            "browser_endpoint":self._payload.get("browserEndpoint"),
            "wof_page_found":bool(self._payload.get("wofPageFound")),
            "page_target_id":self._payload.get("pageTargetId"),
            "page_url":self._payload.get("pageUrl"),
            "worker_found":bool(self._payload.get("workerFound")),
            "worker_target_id":self._payload.get("workerTargetId"),
            "wasm_module_found":bool(self._payload.get("wasmFound")),
            "heap_found":bool(self._payload.get("heapFound")),
            "world_921031":exact,
            "identity_sha256":self._payload.get("worldSha256"),
            "alpha_status":{"renderAuthorityV3":dict(self._payload)},
            "read_only":True,"ram_writes":0,"input_injection":False,
            "last_error":self._payload.get("blockedReason") if state=="BLOCKED" else None,
        }
        self.store.update(**updates)
        if self.on_change:
            try:self.on_change()
            except Exception:pass

class MeasurementTrayApp(TrayApp):
    def __init__(self, status: StatusStore, *, quit_app: Callable[[], None]) -> None:
        super().__init__(status,reconnect=lambda:None,open_game=lambda:None,quit_app=quit_app)
        self._last_terminal=None
    @staticmethod
    def _measurement(s) -> dict[str,Any]:
        a=s.alpha_status if isinstance(s.alpha_status,dict) else {}
        v=a.get("renderAuthorityV3") if isinstance(a,dict) else None
        return v if isinstance(v,dict) else {}
    @classmethod
    def _format_status(cls,s)->str:
        m=cls._measurement(s); state=str(m.get("measurementState") or s.state)
        lines=[f"采集状态：{MEASUREMENT_STATE_ZH.get(state,state)}",
               f"浏览器：{'已连接' if s.browser_connected else '未连接'}"+(f"（{s.browser_name}）" if s.browser_name else ""),
               f"WOF 页面：{'已找到' if s.wof_page_found else '未找到'}",
               f"Worker / WASM：{'已找到' if s.worker_found and s.wasm_module_found and s.heap_found else '等待中'}",
               f"游戏版本：{'World 921031 已确认' if s.world_921031 else '未确认'}",
               "只读模式：开启", "游戏内存写入：0", "输入注入：关闭"]
        vis=m.get("visual") if isinstance(m.get("visual"),dict) else {}
        if vis:
            lines += ["",f"P1 视觉状态：{MEASUREMENT_STATE_ZH.get(str(vis.get('state') or ''),str(vis.get('state') or ''))}",
                      f"头部样本：{vis.get('templateCount',0)} / {vis.get('templateMinimum',3)} · 连续跟踪帧：{vis.get('trackedFrames',0)}",
                      f"Owner 点击：{vis.get('ownerClickCount',0)} / fallback 上限 {vis.get('ownerClickMaximum',1)}（正常预期 0）"]
            if vis.get("confidence") is not None: lines.append(f"视觉置信度：{float(vis['confidence']):.3f}")
            if vis.get("autoSeedAttemptCount") is not None and not vis.get("seedSource"): lines.append(f"自动头部 seed：{vis.get('autoSeedAttemptCount',0)} / {vis.get('autoSeedMaximumFrames',0)}")
            if vis.get("seedSource"): lines.append("头部 seed 来源："+str(vis.get("seedSource")))
            if vis.get("actionZh"): lines.append("当前只需做一件事："+str(vis["actionZh"]))
            if int(vis.get("lostFrames") or 0)>0: lines.append("识别不稳时标记已自动隐藏；恢复后会自动重新显示。")
        if m.get("sampleCount") is not None: lines.append(f"采集进度：{m.get('sampleCount',0)} samples / {m.get('candidateCount',0)} structural candidates")
        if m.get("runtimeRediscoveryCount"): lines.append(f"运行时自动重发现：{m['runtimeRediscoveryCount']} 次")
        if m.get("zipPath"): lines += ["", "结果 ZIP："+str(m["zipPath"])]
        if m.get("blockedReason"): lines += ["", "BLOCKED："+str(m["blockedReason"])]
        if m.get("browserEntrySource"): lines.append("浏览器入口："+str(m["browserEntrySource"]))
        if s.page_url: lines.append("页面地址："+s.page_url)
        if s.identity_sha256: lines.append("World SHA-256："+s.identity_sha256)
        return "\n".join(lines)
    @classmethod
    def _human_hint(cls,s)->str:
        m=cls._measurement(s); state=str(m.get("measurementState") or s.state); vis=m.get("visual") if isinstance(m.get("visual"),dict) else {}
        if state=="WAITING_FOR_WOF": return "请正常进入 WOF；工具会自动等待，不需要 DevTools。"
        if state=="HEAD_ACQUIRING": return str(vis.get("actionZh") or "正在自动识别 P1 身份并定位场景头部；正常路径无需点击。")
        if state=="ONE_CLICK_REQUIRED": return str(vis.get("actionZh") or "自动定位无法安全唯一确认；请点一下场景中 P1 人物实际头部（只需一次）。")
        if state in {"HEAD_TRACKING","MEASURING","RUNNING"}: return str(vis.get("actionZh") or "正常玩即可；样本与证据会自动积累。")
        if state=="RUNTIME_REDISCOVERY": return "Worker/runtime 已变化；旧视觉位置已撤销，正在自动重发现。"
        if state=="COMPLETE": return "自动采集与打包已完成。"
        if state=="BLOCKED": return str(m.get("blockedReason") or "采集受阻。")
        return MEASUREMENT_STATE_ZH.get(state,state)
    def _make_image(self,state:str):
        from PIL import Image,ImageDraw
        if state=="COMPLETE": fill=(36,160,80,255)
        elif state=="BLOCKED": fill=(190,55,55,255)
        elif state in {"WAITING_FOR_WOF","ONE_CLICK_REQUIRED","HEAD_ACQUIRING","RUNTIME_REDISCOVERY"}: fill=(214,154,30,255)
        else: fill=(55,120,190,255)
        image=Image.new("RGBA",(64,64),(0,0,0,0));draw=ImageDraw.Draw(image);draw.ellipse((4,4,60,60),fill=fill);draw.text((18,21),"W",fill=(255,255,255,255));return image
    def refresh(self)->None:
        if not self.icon:return
        snap=self.status.get();m=self._measurement(snap);state=str(m.get("measurementState") or snap.state)
        try:
            self.icon.icon=self._make_image(state);self.icon.title=f"WOF Render Authority - {MEASUREMENT_STATE_ZH.get(state,state)} - 只读";self.icon.update_menu()
            if state in {"COMPLETE","BLOCKED"} and self._last_terminal!=state:
                text="采集完成，ZIP 已生成。" if state=="COMPLETE" else "采集受阻，请打开状态查看精确原因。"
                try:self.icon.notify(text,"WOF Render Authority")
                except Exception:pass
                self._last_terminal=state
        except Exception:pass
    def _menu(self):
        import pystray
        def text(fn):return lambda _item:fn(self.status.get())
        return pystray.Menu(
            pystray.MenuItem("打开状态",lambda *_:self.show_diagnostics(),default=True),
            pystray.MenuItem(text(lambda s:"采集状态："+MEASUREMENT_STATE_ZH.get(str(self._measurement(s).get('measurementState') or s.state),str(s.state))),None,enabled=False),
            pystray.MenuItem(text(lambda s:"World 921031："+("已确认" if s.world_921031 else "等待中")),None,enabled=False),
            pystray.MenuItem("只读 / RAM writes 0 / input injection 0",None,enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("状态与诊断",lambda *_:self.show_diagnostics()),
            pystray.MenuItem("退出状态工具",lambda *_:self._quit()),
        )
