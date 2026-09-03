from __future__ import annotations

import argparse
import json
import secrets
import threading
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from wof_launcher.browser import find_browser, known_owner_game_url, launch_debug_browser, probe_endpoint_diagnostic, wait_for_endpoint_diagnostic
from wof_launcher.cdp import CdpClient
from wof_launcher import discovery_v2 as discovery_module
from wof_launcher.fleet import select_fleet_instance
from wof_launcher.head_visual_tracker import P1HeadVisualTracker
from wof_launcher.probe_v2 import IDENTITY_PROBE as FIELD_IDENTITY_PROBE
from wof_launcher.reentry_discovery import recover_page_only
from wof_launcher.render_authority_capture import RenderAuthorityCapture
from wof_launcher.runtime_authority import RuntimeAuthorityGuard

SAFETY={"readOnly":True,"ramWrites":0,"inputInjection":False,"manualCalibration":False,"legacyProjectionSelected":False,"productionOverlayEnabled":False}
SCHEMA="wof-render-authority-owner-visible-session-v3"
VISUAL_GRACE_SECONDS=12.0
OWNER_FLOW="MENU6_NORMAL_GAME_AUTO_P1_IDENTITY_BOUNDED_SCENE_HEAD_ZERO_CLICK_FIRST_FALLBACK_ONE_CLICK_MAX_NORMAL_PLAY_AUTO_COMPLETE"

def _write(path:Path,value:object)->None:
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def _zip_dir(session_dir:Path,zip_path:Path)->None:
    zip_path.parent.mkdir(parents=True,exist_ok=True);tmp=zip_path.with_suffix(zip_path.suffix+".partial");tmp.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(session_dir.rglob("*")):
                if p.is_file():zf.write(p,p.relative_to(session_dir).as_posix())
        tmp.replace(zip_path)
    finally:tmp.unlink(missing_ok=True)

def _page_cleanup_and_surface(client:CdpClient,target_id:str)->dict[str,Any]:
    session=client.attach(target_id)
    try:
        session.request("Runtime.enable")
        expr="""(()=>{try{window.WOFOWNERPROJECTION?.stop?.()}catch(_){}try{window.WOFALPHAHUD?.dispose?.()}catch(_){}try{delete window.__WOF_OWNER_MARKER_SNAPSHOT__}catch(_){}const cs=[...document.querySelectorAll('canvas')].map((c,i)=>{const r=c.getBoundingClientRect();return {index:i,width:c.width,height:c.height,clientWidth:r.width,clientHeight:r.height,left:r.left,top:r.top}});return {href:String(location.href),title:String(document.title||''),canvases:cs,legacyProjectionStopped:true,untrustedGameplayOverlayDisposed:true,ownerStatusUiDisposed:false,readOnly:true,ramWrites:0,inputInjection:false};})()"""
        value=session.evaluate(expr,timeout=10.0);return value if isinstance(value,dict) else {"readOnly":True,"ramWrites":0,"inputInjection":False}
    finally:session.close()

def _accepted(choice)->bool:
    return bool(choice.page and choice.worker and choice.worker_probe and choice.worker_probe.get("moduleOk") is True and choice.identity and choice.identity.get("ok") is True)

def run(root:Path,output_root:Path,host:str="127.0.0.1",port:int=9223,browser:str="auto",browser_path:str|None=None,game_url:str|None=None,status_callback:Callable[[str,dict[str,Any]],None]|None=None,stop_event:threading.Event|None=None)->int:
    root=root.resolve();output_root=output_root.resolve();stop_event=stop_event or threading.Event()
    stamp=datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")+"_"+secrets.token_hex(4);session_dir=output_root/f"render_authority_v3_{stamp}";zip_path=output_root/"packages"/f"WOF_LIVE_ACCEPTANCE_{session_dir.name}.zip";session_dir.mkdir(parents=True,exist_ok=True)
    events:list[dict[str,Any]]=[];started=datetime.now().astimezone().isoformat(timespec="seconds");shared:dict[str,Any]={"runtimeRediscoveryCount":0,"browserConnected":False,"wofPageFound":False,"workerFound":False,"wasmFound":False,"heapFound":False}
    def event(kind:str,**payload:Any)->None:
        events.append({"at":datetime.now().astimezone().isoformat(timespec="milliseconds"),"kind":kind,**payload})
        if len(events)>200: del events[:-200]
        _write(session_dir/"EVENTS.json",{"schema":SCHEMA,"events":events,"safety":SAFETY})
    def publish(state:str,**payload:Any)->None:
        shared.update(payload);snap={**shared,"measurementState":state,"safety":SAFETY};_write(session_dir/"OWNER_STATUS.json",{"schema":SCHEMA,**snap})
        if status_callback:
            try:status_callback(state,dict(snap))
            except Exception:pass
    def blocked(reason:str,code:int,**extra:Any)->int:
        event("BLOCKED",reason=reason,**extra);summary={"schema":SCHEMA,"startedAt":started,"endedAt":datetime.now().astimezone().isoformat(timespec="seconds"),"verdict":"BLOCKED","blockedReason":reason,"ownerFlow":OWNER_FLOW,"safety":SAFETY,"zipPath":str(zip_path),**extra};_write(session_dir/"SESSION_SUMMARY.json",summary);_zip_dir(session_dir,zip_path);publish("BLOCKED",blockedReason=reason,zipPath=str(zip_path),**extra);return code
    publish("STARTING");event("SESSION_STARTED",ownerFlow=OWNER_FLOW,ownerClickExpectedNormal=0,ownerClickFallbackMaximumPerAuthorityGeneration=1)
    endpoint,rejection=probe_endpoint_diagnostic(host,port);browser_proc=None;entry_source="existing-pylaunch-cdp" if endpoint else None
    if endpoint is None:
        fleet=select_fleet_instance(None,live_only=True)
        if fleet:
            candidate,rej=probe_endpoint_diagnostic(fleet.host,fleet.port)
            if candidate: endpoint=candidate;host=fleet.host;port=fleet.port;entry_source=f"existing-browser-fleet-{fleet.instance_id}"
            elif rej: rejection=rej
    if endpoint is None:
        exe=find_browser(browser,browser_path)
        if not exe:return blocked("未找到 Chrome/Edge；无法建立只读 WOF 浏览器入口。",3)
        resolved_url,url_source=known_owner_game_url(game_url)
        try:
            browser_proc=launch_debug_browser(exe,host=host,port=port,user_data_dir=None,game_url=resolved_url,restore_last_session=resolved_url is None)
            entry_source=("configured-"+str(url_source)) if resolved_url else "persistent-pylaunch-profile-restore"
            publish("WAITING_FOR_WOF",browserEntrySource=entry_source)
            endpoint,rejection=wait_for_endpoint_diagnostic(host,port,timeout=15.0)
        except Exception as exc:return blocked(f"无法启动/复用只读 WOF 浏览器：{exc}",4)
    if endpoint is None:return blocked(rejection or "浏览器调试端口不可用。",5)
    shared.update({"browserConnected":True,"browserName":endpoint.browser,"browserEndpoint":endpoint.http_base,"browserEntrySource":entry_source});publish("WAITING_FOR_WOF")
    client=CdpClient(endpoint.websocket_url,timeout=5.0)
    try:client.connect()
    except Exception as exc:return blocked(f"无法连接本机只读 CDP：{exc}",6)
    guard=RuntimeAuthorityGuard();identity_cache:dict[str,dict]={};capture=RenderAuthorityCapture(lambda rel:(root/rel).read_text(encoding="utf-8"));visual=P1HeadVisualTracker(session_dir/"head_visual")
    accepted=None;authority_key=None;runtime_epoch=None;page_surface=None;terminal_capture=None;terminal_seen_at=None
    try:
        while not stop_event.is_set():
            if accepted is None:
                discovery_module.IDENTITY_PROBE=FIELD_IDENTITY_PROBE
                choice=recover_page_only(client,discovery_module.discover(client,identity_cache=identity_cache),identity_cache=identity_cache)
                shared.update({"wofPageFound":choice.page is not None,"workerFound":choice.worker is not None,"wasmFound":bool(choice.worker_probe and choice.worker_probe.get("moduleOk")),"heapFound":bool(choice.worker_probe and choice.worker_probe.get("heapOk")),"pageTargetId":str(choice.page.get("targetId")) if choice.page else None,"pageUrl":str(choice.page.get("url") or "") if choice.page else None,"workerTargetId":str(choice.worker.get("targetId")) if choice.worker else None})
                if not _accepted(choice):
                    publish("WAITING_FOR_WOF",discoveryReason=choice.reason);time.sleep(0.8);continue
                fp=guard.accept(client,choice);authority_key=fp.key();runtime_epoch=secrets.token_hex(16);accepted=choice
                shared.update({"worldSha256":choice.identity.get("sha256"),"runtimeEpoch":runtime_epoch,"authorityKey":authority_key})
                publish("EXACT_WORLD_LOCKED");event("EXACT_WORLD_LOCKED",authorityKey=authority_key,runtimeEpoch=runtime_epoch,worldSha256=choice.identity.get("sha256"))
                page_surface=_page_cleanup_and_surface(client,str(choice.page.get("targetId")));publish("CAMERA_PREPARING",pageSurface=page_surface)
                visual.bind(client,str(choice.page.get("targetId")),authority_key,runtime_epoch);capture.ensure_started(client,choice,authority_key,runtime_epoch);terminal_capture=None;terminal_seen_at=None
            healthy,reason,diag=guard.healthy(client,accepted)
            if not healthy:
                event("RUNTIME_REDISCOVERY",reason=reason,diagnostics=diag);shared["runtimeRediscoveryCount"]=int(shared.get("runtimeRediscoveryCount") or 0)+1;publish("RUNTIME_REDISCOVERY",rediscoveryReason=reason)
                visual.dispose();capture.stop_runtime(client);guard.clear();identity_cache.clear();accepted=None;authority_key=None;runtime_epoch=None;terminal_capture=None;terminal_seen_at=None;time.sleep(0.4);continue
            polled=capture.poll(client,authority_key,runtime_epoch);remote=polled.get("remote") if isinstance(polled,dict) else None
            lifecycle=remote.get("p1Lifecycle") if isinstance(remote,dict) else None
            v=visual.poll(lifecycle);sample_count=int(remote.get("sampleCount") or 0) if isinstance(remote,dict) else 0;candidate_count=int(remote.get("candidateCount") or 0) if isinstance(remote,dict) else 0
            if polled.get("state")=="ERROR":return blocked("Render Authority 只读采集失败："+str(polled.get("error") or "unknown"),7,visual=v)
            vstate=str(v.get("state") or "CAMERA_PREPARING")
            state=vstate if vstate in {"CAMERA_PREPARING","HEAD_ACQUIRING","ONE_CLICK_REQUIRED","HEAD_TRACKING"} and not v.get("qualified") else "MEASURING"
            publish(state,visual=v,sampleCount=sample_count,candidateCount=candidate_count)
            if polled.get("state")=="MEASUREMENT_COMPLETE" and terminal_capture is None:
                terminal_capture=polled.get("result");terminal_seen_at=time.monotonic();event("CAPTURE_CORE_COMPLETE",sampleCount=sample_count,candidateCount=candidate_count)
            if terminal_capture is not None:
                if visual.qualified():
                    result=terminal_capture
                    if not isinstance(result,dict):return blocked("terminal capture result missing",8,visual=v)
                    result["pageSurface"]=page_surface;result["sessionSafety"]=SAFETY;_write(session_dir/"RENDER_AUTHORITY_CAPTURE_RESULT.json",result);_write(session_dir/"P1_HEAD_VISUAL_RESULT.json",visual.result())
                    summary={"schema":SCHEMA,"startedAt":started,"endedAt":datetime.now().astimezone().isoformat(timespec="seconds"),"verdict":"BOUNDED_CAPTURE_AND_P1_HEAD_VISUAL_AUTHORITY_READY","ownerFlow":OWNER_FLOW,"ownerClickExpectedNormal":0,"ownerClickFallbackMaximumPerAuthorityGeneration":1,"worldSha256":result.get("worldSha256"),"runtimeEpoch":result.get("runtimeEpoch"),"authorityKey":result.get("authorityKey"),"sampleCount":result.get("sampleCount"),"candidateCount":len(result.get("candidateRegions") or []),"visual":visual.result(),"legacyProjectionUsed":False,"manualProjectionCalibrationUsed":False,"productionOverlaySuppressed":True,"automaticPackaging":True,"safety":SAFETY,"zipPath":str(zip_path)}
                    _write(session_dir/"SESSION_SUMMARY.json",summary);event("COMPLETE",zipPath=str(zip_path));_zip_dir(session_dir,zip_path);(session_dir/"FINAL_ZIP.txt").write_text(str(zip_path)+"\n",encoding="utf-8");publish("COMPLETE",visual=visual.result(),zipPath=str(zip_path),sampleCount=sample_count,candidateCount=candidate_count);return 0
                if terminal_seen_at is not None and time.monotonic()-terminal_seen_at>=VISUAL_GRACE_SECONDS:
                    reason="P1 头部视觉 authority 在有界窗口内未达到安全多样本/连续跟踪门槛；未启用不可信 overlay。"
                    _write(session_dir/"P1_HEAD_VISUAL_RESULT.json",visual.result());return blocked(reason,9,visual=visual.result(),sampleCount=sample_count,candidateCount=candidate_count)
                publish("RUNNING",visual=v,sampleCount=sample_count,candidateCount=candidate_count)
            time.sleep(0.18)
        event("OWNER_STOPPED");return blocked("Owner 已退出 V3 状态工具，采集已安全停止。",130,visual=visual.status())
    except Exception as exc:
        return blocked(f"V3 自动采集发生错误：{type(exc).__name__}: {exc}",10,visual=visual.status())
    finally:
        try:visual.dispose()
        except Exception:pass
        try:capture.stop_runtime(client)
        except Exception:pass
        try:client.close()
        except Exception:pass
        _write(session_dir/"EVENTS.json",{"schema":SCHEMA,"events":events,"safety":SAFETY})
        if browser_proc is not None:event("BROWSER_LEFT_RUNNING_FOR_OWNER")

def main()->int:
    p=argparse.ArgumentParser(description="Alpha V1 Render Authority V3 owner-visible automatic measurement");p.add_argument("--root",required=True);p.add_argument("--output-root",required=True);p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=9223);p.add_argument("--browser",choices=["auto","chrome","edge"],default="auto");p.add_argument("--browser-path");p.add_argument("--game-url");a=p.parse_args();return run(Path(a.root),Path(a.output_root),a.host,a.port,a.browser,a.browser_path,a.game_url)
if __name__=="__main__":raise SystemExit(main())