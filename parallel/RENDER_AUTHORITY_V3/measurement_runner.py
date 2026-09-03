from __future__ import annotations

import argparse
import json
import os
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
from wof_launcher.production_p1_overlay import ProductionP1Overlay
from wof_launcher.reentry_discovery import recover_page_only
from wof_launcher.render_authority_capture import RenderAuthorityCapture
from wof_launcher.runtime_authority import RuntimeAuthorityGuard

SAFETY={"readOnly":True,"ramWrites":0,"inputInjection":False,"manualCalibration":False,"legacyProjectionSelected":False,"productionOverlayEnabled":True}
SCHEMA="wof-render-authority-owner-visible-session-v3"
ZERO_CLICK_EVIDENCE_SCHEMA="alpha-v3-runtime-p1-zero-click-evidence-v1"
VISUAL_GRACE_SECONDS=12.0
OWNER_FLOW="MENU6_REUSE_WOF_STATUS_W2_ZERO_CLICK_FIRST_OR_ONE_CLICK_MAX_SAME_TRACKER_PRODUCTION_TOP_OF_HEAD_OVERLAY_HIDE_RECOVER_REENTRY"
PRODUCTION_OVERLAY_SOURCE="product/alpha/wof_alpha_hud.js"
LIVE_ACCEPTANCE_HOLD_ENV="WOF_ALPHA_LIVE_ACCEPTANCE_HOLD"
LIVE_ACCEPTANCE_PHASE="P1_DRAW_READY_ENEMY_LIVE_CHECK"

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
        expr="""(()=>{try{window.WOFOWNERPROJECTION?.stop?.()}catch(_){}try{delete window.__WOF_OWNER_MARKER_SNAPSHOT__}catch(_){}const cs=[...document.querySelectorAll('canvas')].map((c,i)=>{const r=c.getBoundingClientRect();return {index:i,width:c.width,height:c.height,clientWidth:r.width,clientHeight:r.height,left:r.left,top:r.top}});return {href:String(location.href),title:String(document.title||''),canvases:cs,legacyProjectionStopped:true,existingProductionHudPreserved:true,ownerStatusUiDisposed:false,readOnly:true,ramWrites:0,inputInjection:false};})()"""
        value=session.evaluate(expr,timeout=10.0);return value if isinstance(value,dict) else {"readOnly":True,"ramWrites":0,"inputInjection":False}
    finally:session.close()

def _accepted(choice)->bool:
    return bool(choice.page and choice.worker and choice.worker_probe and choice.worker_probe.get("moduleOk") is True and choice.identity and choice.identity.get("ok") is True)

def _zero_click_identity_evidence(remote:Any)->dict[str,Any]|None:
    """Accept only an explicit read-only semantic-evidence envelope.

    Current exact-runtime capture may legitimately provide no such envelope; in
    that case the W2 tracker gate fails closed and only its bounded one-click
    fallback may be offered. Lifecycle.type is never copied into HUD evidence.
    """
    if not isinstance(remote,dict):
        return None
    evidence=remote.get("p1ZeroClickEvidence")
    if not isinstance(evidence,dict) or evidence.get("schema")!=ZERO_CLICK_EVIDENCE_SCHEMA:
        return None
    if evidence.get("readOnly") is not True or evidence.get("ramWrites")!=0 or evidence.get("inputInjection") is not False:
        return None
    hud=evidence.get("hudIdentityCandidates")
    scene=evidence.get("sceneHeadCandidates")
    if not isinstance(hud,list) or not isinstance(scene,list):
        return None
    return {"hudIdentityCandidates":[dict(row) for row in hud if isinstance(row,dict)],"sceneHeadCandidates":[dict(row) for row in scene if isinstance(row,dict)]}

def _visual_with_overlay(visual:dict[str,Any],overlay:dict[str,Any])->dict[str,Any]:
    out=dict(visual);out["productionOverlayEnabled"]=True;out["productionOverlayVisible"]=overlay.get("visible") is True;out["productionOverlaySource"]=PRODUCTION_OVERLAY_SOURCE;out["productionOverlay"]=dict(overlay);return out

def _owner_click_pending(visual:Any)->bool:
    if not isinstance(visual,dict) or str(visual.get("state") or "")!="ONE_CLICK_REQUIRED":
        return False
    try:
        count=int(visual.get("ownerClickCount") or 0);maximum=max(1,int(visual.get("ownerClickMaximum") or 1))
    except (TypeError,ValueError):
        return True
    return count<maximum

def run(root:Path,output_root:Path,host:str="127.0.0.1",port:int=9223,browser:str="auto",browser_path:str|None=None,game_url:str|None=None,status_callback:Callable[[str,dict[str,Any]],None]|None=None,stop_event:threading.Event|None=None)->int:
    root=root.resolve();output_root=output_root.resolve();stop_event=stop_event or threading.Event();live_acceptance_hold=os.environ.get(LIVE_ACCEPTANCE_HOLD_ENV)=="1"
    stamp=datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")+"_"+secrets.token_hex(4);session_dir=output_root/f"render_authority_v3_{stamp}";zip_path=output_root/"packages"/f"WOF_LIVE_ACCEPTANCE_{session_dir.name}.zip";session_dir.mkdir(parents=True,exist_ok=True)
    events:list[dict[str,Any]]=[];started=datetime.now().astimezone().isoformat(timespec="seconds");shared:dict[str,Any]={"runtimeRediscoveryCount":0,"browserConnected":False,"wofPageFound":False,"workerFound":False,"wasmFound":False,"heapFound":False,"semanticIdentityContract":"W2_FAIL_CLOSED","semanticIdentityEvidenceAvailable":False,"productionOverlayEnabled":True,"productionOverlaySuppressed":False,"productionOverlaySource":PRODUCTION_OVERLAY_SOURCE,"liveAcceptanceHoldAfterP1":live_acceptance_hold,"liveAcceptancePhase":None,"p1LiveGateReady":False}
    def event(kind:str,**payload:Any)->None:
        events.append({"at":datetime.now().astimezone().isoformat(timespec="milliseconds"),"kind":kind,**payload})
        if len(events)>200:del events[:-200]
        _write(session_dir/"EVENTS.json",{"schema":SCHEMA,"events":events,"safety":SAFETY})
    def publish(state:str,**payload:Any)->None:
        shared.update(payload);snap={**shared,"measurementState":state,"safety":SAFETY};_write(session_dir/"OWNER_STATUS.json",{"schema":SCHEMA,**snap})
        if status_callback:
            try:status_callback(state,dict(snap))
            except Exception:pass
    def blocked(reason:str,code:int,**extra:Any)->int:
        event("BLOCKED",reason=reason,**extra);summary={"schema":SCHEMA,"startedAt":started,"endedAt":datetime.now().astimezone().isoformat(timespec="seconds"),"verdict":"BLOCKED","blockedReason":reason,"ownerFlow":OWNER_FLOW,"semanticIdentityContract":"W2_FAIL_CLOSED","productionOverlayEnabled":True,"productionOverlaySuppressed":False,"productionOverlaySource":PRODUCTION_OVERLAY_SOURCE,"liveAcceptanceHoldAfterP1":live_acceptance_hold,"safety":SAFETY,"zipPath":str(zip_path),**extra};_write(session_dir/"SESSION_SUMMARY.json",summary);_zip_dir(session_dir,zip_path);publish("BLOCKED",blockedReason=reason,zipPath=str(zip_path),**extra);return code
    publish("STARTING");event("SESSION_STARTED",ownerFlow=OWNER_FLOW,ownerClickExpectedNormal=0,ownerClickFallbackMaximumPerAuthorityGeneration=1,semanticIdentityContract="W2_FAIL_CLOSED",productionOverlaySource=PRODUCTION_OVERLAY_SOURCE,liveAcceptanceHoldAfterP1=live_acceptance_hold)
    endpoint,rejection=probe_endpoint_diagnostic(host,port);browser_proc=None;entry_source="existing-pylaunch-cdp" if endpoint else None
    if endpoint is None:
        fleet=select_fleet_instance(None,live_only=True)
        if fleet:
            candidate,rej=probe_endpoint_diagnostic(fleet.host,fleet.port)
            if candidate:endpoint=candidate;host=fleet.host;port=fleet.port;entry_source=f"existing-browser-fleet-{fleet.instance_id}"
            elif rej:rejection=rej
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
    verified_text=lambda rel:(root/rel).read_text(encoding="utf-8")
    guard=RuntimeAuthorityGuard();identity_cache:dict[str,dict]={};capture=RenderAuthorityCapture(verified_text);visual=P1HeadVisualTracker(session_dir/"head_visual");overlay=ProductionP1Overlay(verified_text)
    accepted=None;authority_key=None;runtime_epoch=None;page_surface=None;terminal_capture=None;terminal_seen_at=None;p1_live_gate_ready=False
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
                page_id=str(choice.page.get("targetId"));page_surface=_page_cleanup_and_surface(client,page_id);publish("CAMERA_PREPARING",pageSurface=page_surface)
                visual.bind(client,page_id,authority_key,runtime_epoch);overlay.bind(client,page_id,authority_key,runtime_epoch);capture.ensure_started(client,choice,authority_key,runtime_epoch);terminal_capture=None;terminal_seen_at=None;p1_live_gate_ready=False;shared.update({"p1LiveGateReady":False,"liveAcceptancePhase":None})
            healthy,reason,diag=guard.healthy(client,accepted)
            if not healthy:
                event("RUNTIME_REDISCOVERY",reason=reason,diagnostics=diag);shared["runtimeRediscoveryCount"]=int(shared.get("runtimeRediscoveryCount") or 0)+1;publish("RUNTIME_REDISCOVERY",rediscoveryReason=reason,p1LiveGateReady=False,liveAcceptancePhase=None)
                overlay.dispose();visual.dispose();capture.stop_runtime(client);guard.clear();identity_cache.clear();accepted=None;authority_key=None;runtime_epoch=None;terminal_capture=None;terminal_seen_at=None;p1_live_gate_ready=False;time.sleep(0.4);continue
            polled=capture.poll(client,authority_key,runtime_epoch);remote=polled.get("remote") if isinstance(polled,dict) else None
            lifecycle=remote.get("p1Lifecycle") if isinstance(remote,dict) else None
            identity_evidence=_zero_click_identity_evidence(remote)
            raw_visual=visual.poll(lifecycle,identity_evidence);overlay_status=overlay.update(raw_visual,getattr(visual,"_layout",None),visual._last_frame_size());v=_visual_with_overlay(raw_visual,overlay_status)
            sample_count=int(remote.get("sampleCount") or 0) if isinstance(remote,dict) else 0;candidate_count=int(remote.get("candidateCount") or 0) if isinstance(remote,dict) else 0
            shared["semanticIdentityEvidenceAvailable"]=identity_evidence is not None
            if polled.get("state")=="ERROR":return blocked("Render Authority 只读采集失败："+str(polled.get("error") or "unknown"),7,visual=v,productionOverlay=overlay_status)
            vstate=str(v.get("state") or "CAMERA_PREPARING")
            state=vstate if vstate in {"CAMERA_PREPARING","HEAD_ACQUIRING","ONE_CLICK_REQUIRED","HEAD_TRACKING"} and not v.get("qualified") else "MEASURING"
            publish(state,visual=v,productionOverlay=overlay_status,productionOverlayVisible=overlay_status.get("visible") is True,sampleCount=sample_count,candidateCount=candidate_count)
            capture_result=polled.get("result") if isinstance(polled,dict) else None
            if terminal_capture is None and isinstance(capture_result,dict):
                terminal_capture=capture_result;terminal_seen_at=None;event("CAPTURE_CORE_COMPLETE",sampleCount=sample_count,candidateCount=candidate_count,captureState=polled.get("state"))
            if terminal_capture is not None:
                if _owner_click_pending(v):
                    terminal_seen_at=None;publish("ONE_CLICK_REQUIRED",visual=v,productionOverlay=overlay_status,productionOverlayVisible=False,sampleCount=sample_count,candidateCount=candidate_count,ownerActionRequired="CLICK_P1_REAL_HEAD_ONCE");time.sleep(0.18);continue
                if terminal_seen_at is None:
                    terminal_seen_at=time.monotonic();event("P1_VISUAL_GRACE_STARTED",visualState=vstate,ownerClickCount=int(v.get("ownerClickCount") or 0))
                if visual.qualified() and overlay.visible_and_drawn():
                    result=terminal_capture
                    if not isinstance(result,dict):return blocked("terminal capture result missing",8,visual=v,productionOverlay=overlay_status)
                    final_visual=_visual_with_overlay(visual.result(),overlay.status());result["pageSurface"]=page_surface;result["sessionSafety"]=SAFETY;_write(session_dir/"RENDER_AUTHORITY_CAPTURE_RESULT.json",result);_write(session_dir/"P1_HEAD_VISUAL_RESULT.json",final_visual);_write(session_dir/"PRODUCTION_P1_OVERLAY_RESULT.json",overlay.status())
                    if live_acceptance_hold:
                        if not p1_live_gate_ready:
                            p1_live_gate_ready=True;event("P1_LIVE_GATE_READY",productionOverlayDrawCount=overlay.status().get("drawCount"),relativeEnemy=overlay_status.get("relativeEnemy"));_write(session_dir/"P1_LIVE_GATE_READY.json",{"schema":SCHEMA,"at":datetime.now().astimezone().isoformat(timespec="seconds"),"sourceCommit":os.environ.get("WOF_ALPHA_ACCEPTANCE_COMMIT"),"verdict":"P1_PRODUCTION_DRAW_READY_FOR_HUMAN_GEOMETRY_CHECK","visual":final_visual,"productionOverlay":overlay.status(),"relativeEnemy":overlay_status.get("relativeEnemy"),"safety":SAFETY})
                        publish("RUNNING",visual=v,productionOverlay=overlay_status,productionOverlayVisible=True,sampleCount=sample_count,candidateCount=candidate_count,p1LiveGateReady=True,liveAcceptancePhase=LIVE_ACCEPTANCE_PHASE,relativeEnemy=overlay_status.get("relativeEnemy"));time.sleep(0.18);continue
                    summary={"schema":SCHEMA,"startedAt":started,"endedAt":datetime.now().astimezone().isoformat(timespec="seconds"),"verdict":"OWNER_VISIBLE_P1_TOP_OF_HEAD_PRODUCT_LOOP_READY","ownerFlow":OWNER_FLOW,"ownerClickExpectedNormal":0,"ownerClickFallbackMaximumPerAuthorityGeneration":1,"semanticIdentityContract":"W2_FAIL_CLOSED","semanticIdentityEvidenceAvailable":bool(visual.status().get("semanticIdentityEvidenceAvailable")),"worldSha256":result.get("worldSha256"),"runtimeEpoch":result.get("runtimeEpoch"),"authorityKey":result.get("authorityKey"),"sampleCount":result.get("sampleCount"),"candidateCount":len(result.get("candidateRegions") or []),"visual":final_visual,"productionOverlay":overlay.status(),"legacyProjectionUsed":False,"manualProjectionCalibrationUsed":False,"productionOverlaySuppressed":False,"productionOverlayEnabled":True,"productionOverlaySource":PRODUCTION_OVERLAY_SOURCE,"automaticPackaging":True,"safety":SAFETY,"zipPath":str(zip_path)}
                    _write(session_dir/"SESSION_SUMMARY.json",summary);event("COMPLETE",zipPath=str(zip_path),productionOverlayDrawCount=overlay.status().get("drawCount"));_zip_dir(session_dir,zip_path);(session_dir/"FINAL_ZIP.txt").write_text(str(zip_path)+"\n",encoding="utf-8");publish("COMPLETE",visual=final_visual,productionOverlay=overlay.status(),productionOverlayVisible=True,zipPath=str(zip_path),sampleCount=sample_count,candidateCount=candidate_count);return 0
                if live_acceptance_hold and p1_live_gate_ready:
                    publish("RUNNING",visual=v,productionOverlay=overlay_status,productionOverlayVisible=overlay_status.get("visible") is True,sampleCount=sample_count,candidateCount=candidate_count,p1LiveGateReady=True,liveAcceptancePhase=LIVE_ACCEPTANCE_PHASE,relativeEnemy=overlay_status.get("relativeEnemy"));time.sleep(0.18);continue
                if terminal_seen_at is not None and time.monotonic()-terminal_seen_at>=VISUAL_GRACE_SECONDS:
                    if visual.qualified() and not overlay.visible_and_drawn():reason="P1 tracker 已达到门槛，但 maintained Alpha production HUD 在有界窗口内未观察到真实 WebGL 头顶 draw；不能宣称 Owner 可见。"
                    else:reason="P1 头部视觉 authority 在有界窗口内未达到安全多样本/连续跟踪门槛。"
                    final_visual=_visual_with_overlay(visual.result(),overlay.status());_write(session_dir/"P1_HEAD_VISUAL_RESULT.json",final_visual);_write(session_dir/"PRODUCTION_P1_OVERLAY_RESULT.json",overlay.status());return blocked(reason,9,visual=final_visual,productionOverlay=overlay.status(),sampleCount=sample_count,candidateCount=candidate_count)
                publish("RUNNING",visual=v,productionOverlay=overlay_status,productionOverlayVisible=overlay_status.get("visible") is True,sampleCount=sample_count,candidateCount=candidate_count)
            time.sleep(0.18)
        final_visual=_visual_with_overlay(visual.status(),overlay.status())
        if live_acceptance_hold and p1_live_gate_ready:
            relative_enemy=overlay.status().get("relativeEnemy");event("OWNER_STOPPED_AFTER_P1_LIVE_GATE",relativeEnemy=relative_enemy);summary={"schema":SCHEMA,"startedAt":started,"endedAt":datetime.now().astimezone().isoformat(timespec="seconds"),"verdict":"P1_DRAW_READY_ENEMY_LIVE_CHECK_ENDED_UNADJUDICATED","ownerFlow":OWNER_FLOW,"sourceCommit":os.environ.get("WOF_ALPHA_ACCEPTANCE_COMMIT"),"p1LiveGateReady":True,"liveAcceptancePhase":LIVE_ACCEPTANCE_PHASE,"visual":final_visual,"productionOverlay":overlay.status(),"relativeEnemy":relative_enemy,"humanGeometryJudgmentRequired":True,"safety":SAFETY,"zipPath":str(zip_path)};_write(session_dir/"SESSION_SUMMARY.json",summary);_zip_dir(session_dir,zip_path);return 131
        event("OWNER_STOPPED");return blocked("Owner 已退出 V3 状态工具，采集已安全停止。",130,visual=final_visual,productionOverlay=overlay.status())
    except Exception as exc:
        final_visual=_visual_with_overlay(visual.status(),overlay.status());return blocked(f"V3 自动采集发生错误：{type(exc).__name__}: {exc}",10,visual=final_visual,productionOverlay=overlay.status())
    finally:
        try:overlay.dispose()
        except Exception:pass
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
