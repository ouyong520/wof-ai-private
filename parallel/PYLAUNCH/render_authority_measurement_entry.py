from __future__ import annotations

import argparse
import importlib.util
import threading
from pathlib import Path

from wof_launcher.render_measurement_ui import MeasurementPublisher, MeasurementTrayApp
from wof_launcher.state import StatusStore


def _load_runner(root: Path):
    runner=root/"parallel/RENDER_AUTHORITY_V3/measurement_runner.py"
    if not runner.is_file(): raise RuntimeError("render authority V3 measurement runner missing")
    spec=importlib.util.spec_from_file_location("wof_render_authority_v3_runner",runner)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load render authority V3 runner")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def parse_args()->argparse.Namespace:
    p=argparse.ArgumentParser(description="WOF Render Authority V3 owner-visible entry")
    p.add_argument("--root",required=True);p.add_argument("--output-root",required=True);p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=9223);p.add_argument("--browser",choices=["auto","chrome","edge"],default="auto");p.add_argument("--browser-path");p.add_argument("--game-url");return p.parse_args()

def main()->int:
    args=parse_args();root=Path(args.root).expanduser().resolve();output_root=Path(args.output_root).expanduser().resolve();output_root.mkdir(parents=True,exist_ok=True)
    store=StatusStore();stop=threading.Event();publisher=MeasurementPublisher(store)
    def request_stop()->None: stop.set()
    tray=MeasurementTrayApp(store,quit_app=request_stop);publisher.on_change=tray.refresh
    publisher.publish("STARTING",browserConnected=False,wofPageFound=False,workerFound=False,wasmFound=False,heapFound=False)
    result={"code":None}
    def worker()->None:
        try:
            runner=_load_runner(root)
            result["code"]=int(runner.run(root,output_root,args.host,args.port,args.browser,args.browser_path,args.game_url,lambda state,payload:publisher.publish(state,**payload),stop) or 0)
        except Exception as exc:
            publisher.publish("BLOCKED",blockedReason=f"V3 启动失败：{type(exc).__name__}: {exc}")
            result["code"]=12
    thread=threading.Thread(target=worker,name="wof-render-authority-v3",daemon=True);thread.start()
    try:
        tray.run()
    except ImportError as exc:
        stop.set()
        try:
            import tkinter as tk
            from tkinter import messagebox
            r=tk.Tk();r.withdraw();messagebox.showerror("WOF Render Authority BLOCKED",f"缺少托盘依赖：{exc}\n请重新运行 WOF 一键工具完成依赖安装。",parent=r);r.destroy()
        except Exception: pass
        return 13
    finally:
        stop.set();thread.join(timeout=3.0)
    return int(result["code"] or 0)

if __name__=="__main__":raise SystemExit(main())
