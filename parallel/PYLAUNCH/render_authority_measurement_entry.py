from __future__ import annotations

import argparse
import importlib.util
import os
import threading
from pathlib import Path
from typing import Any

from wof_launcher import discovery_v2 as discovery_module
from wof_launcher.browser import BrowserEndpoint, probe_endpoint_diagnostic
from wof_launcher.cdp import CdpClient
from wof_launcher.fleet import discover_fleet_instances
from wof_launcher.probe_v2 import IDENTITY_PROBE as FIELD_IDENTITY_PROBE
from wof_launcher.reentry_discovery import recover_page_only
from wof_launcher.render_measurement_ui import MeasurementPublisher, MeasurementTrayApp
from wof_launcher.state import StatusStore

ATTACH_ONLY_ENV = "WOF_ALPHA_MENU6_ATTACH_ONLY"


def _load_runner(root: Path):
    runner=root/"parallel/RENDER_AUTHORITY_V3/measurement_runner.py"
    if not runner.is_file(): raise RuntimeError("render authority V3 measurement runner missing")
    spec=importlib.util.spec_from_file_location("wof_render_authority_v3_runner",runner)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load render authority V3 runner")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def _accepted(choice: Any) -> bool:
    return bool(
        choice
        and choice.page
        and choice.worker
        and choice.worker_probe
        and choice.worker_probe.get("moduleOk") is True
        and choice.identity
        and choice.identity.get("ok") is True
    )


def _existing_endpoint_candidates(host: str, port: int) -> list[tuple[BrowserEndpoint, str]]:
    rows: list[tuple[BrowserEndpoint, str]] = []
    seen: set[tuple[str, int]] = set()
    endpoint, _ = probe_endpoint_diagnostic(host, port)
    if endpoint is not None:
        rows.append((endpoint, "existing-pylaunch-cdp"))
        seen.add((endpoint.host, int(endpoint.port)))
    for fleet in discover_fleet_instances(None, live_only=True):
        key = (fleet.host, int(fleet.port))
        if key in seen:
            continue
        candidate, _ = probe_endpoint_diagnostic(fleet.host, fleet.port)
        if candidate is None:
            continue
        rows.append((candidate, f"existing-browser-fleet-{fleet.instance_id}"))
        seen.add(key)
    return rows


def _probe_reusable_wof(host: str, port: int) -> tuple[BrowserEndpoint | None, str | None, dict[str, Any]]:
    """Find an already-open exact WOF page without launching, restoring or navigating."""
    candidates = _existing_endpoint_candidates(host, port)
    diagnostic: dict[str, Any] = {
        "candidateEndpointCount": len(candidates),
        "browserLaunchAttempted": False,
        "navigationAttempted": False,
        "staleGameUrlIgnored": True,
        "discoveryReason": "NO_REUSABLE_WOF_SESSION",
    }
    discovery_module.IDENTITY_PROBE = FIELD_IDENTITY_PROBE
    for endpoint, entry_source in candidates:
        client = CdpClient(endpoint.websocket_url, timeout=5.0)
        identity_cache: dict[str, dict] = {}
        try:
            client.connect()
            choice = recover_page_only(
                client,
                discovery_module.discover(client, identity_cache=identity_cache),
                identity_cache=identity_cache,
            )
            diagnostic.update(
                {
                    "wofPageFound": choice.page is not None,
                    "workerFound": choice.worker is not None,
                    "wasmFound": bool(choice.worker_probe and choice.worker_probe.get("moduleOk")),
                    "heapFound": bool(choice.worker_probe and choice.worker_probe.get("heapOk")),
                    "discoveryReason": str(getattr(choice, "reason", None) or "NO_EXACT_WOF_ON_ENDPOINT"),
                }
            )
            if _accepted(choice):
                diagnostic.update(
                    {
                        "browserEntrySource": entry_source,
                        "pageTargetId": str(choice.page.get("targetId")),
                        "pageUrl": str(choice.page.get("url") or ""),
                        "workerTargetId": str(choice.worker.get("targetId")),
                    }
                )
                return endpoint, entry_source, diagnostic
        except Exception as exc:
            diagnostic["discoveryReason"] = f"ENDPOINT_SCAN_{type(exc).__name__}"
        finally:
            try:
                client.close()
            except Exception:
                pass
    return None, None, diagnostic


def _waiting_payload(diagnostic: dict[str, Any]) -> dict[str, Any]:
    payload = dict(diagnostic)
    payload.update(
        {
            "browserConnected": bool(diagnostic.get("candidateEndpointCount")),
            "wofPageFound": False,
            "workerFound": False,
            "wasmFound": False,
            "heapFound": False,
            "browserEntrySource": "attach-only-existing-wof",
            "browserLaunchAttempted": False,
            "navigationAttempted": False,
            "staleGameUrlIgnored": True,
        }
    )
    return payload


def parse_args()->argparse.Namespace:
    p=argparse.ArgumentParser(description="WOF Render Authority V3 owner-visible entry")
    p.add_argument("--root",required=True);p.add_argument("--output-root",required=True);p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=9223);p.add_argument("--browser",choices=["auto","chrome","edge"],default="auto");p.add_argument("--browser-path");p.add_argument("--game-url");return p.parse_args()


def main()->int:
    args=parse_args();root=Path(args.root).expanduser().resolve();output_root=Path(args.output_root).expanduser().resolve();output_root.mkdir(parents=True,exist_ok=True)
    store=StatusStore();stop=threading.Event();publisher=MeasurementPublisher(store)
    def request_stop()->None: stop.set()
    tray=MeasurementTrayApp(store,quit_app=request_stop);publisher.on_change=tray.refresh
    publisher.publish("STARTING",browserConnected=False,wofPageFound=False,workerFound=False,wasmFound=False,heapFound=False,browserLaunchAttempted=False,navigationAttempted=False,staleGameUrlIgnored=True)
    result={"code":None}
    def worker()->None:
        previous_attach_only=os.environ.get(ATTACH_ONLY_ENV);os.environ[ATTACH_ONLY_ENV]="1"
        try:
            runner=_load_runner(root)
            while not stop.is_set():
                endpoint,entry_source,diagnostic=_probe_reusable_wof(args.host,args.port)
                if endpoint is None:
                    publisher.publish("WAITING_FOR_WOF",**_waiting_payload(diagnostic))
                    stop.wait(0.8);continue
                publisher.publish("WAITING_FOR_WOF",browserConnected=True,browserEntrySource=entry_source,**diagnostic)
                code=int(runner.run(root,output_root,endpoint.host,endpoint.port,args.browser,args.browser_path,None,lambda state,payload:publisher.publish(state,**payload),stop) or 0)
                if code in {3,4,5,6} and not stop.is_set():
                    publisher.publish("WAITING_FOR_WOF",browserConnected=False,wofPageFound=False,workerFound=False,wasmFound=False,heapFound=False,browserEntrySource="attach-only-existing-wof",discoveryReason="REUSABLE_WOF_DISAPPEARED",browserLaunchAttempted=False,navigationAttempted=False,staleGameUrlIgnored=True)
                    stop.wait(0.8);continue
                result["code"]=code;return
            result["code"]=0
        except Exception as exc:
            publisher.publish("BLOCKED",blockedReason=f"V3 启动失败：{type(exc).__name__}: {exc}")
            result["code"]=12
        finally:
            if previous_attach_only is None:
                os.environ.pop(ATTACH_ONLY_ENV,None)
            else:
                os.environ[ATTACH_ONLY_ENV]=previous_attach_only
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
