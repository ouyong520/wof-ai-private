from __future__ import annotations
import argparse,json,os,queue,subprocess,threading,time,urllib.error,urllib.request
from dataclasses import dataclass
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import websocket

SCHEMA="wof-worker-surface-diag-v1"
BROAD=[{"type":"browser","exclude":True},{"type":"tab","exclude":True},{}]
RELATED=[{"type":"page","exclude":True},{"type":"browser","exclude":True},{"type":"tab","exclude":True},{}]
SAFE={"Target.getTargets","Target.setDiscoverTargets","Target.attachToTarget","Target.detachFromTarget",
      "Target.setAutoAttach","Runtime.enable","Runtime.evaluate","Page.getFrameTree"}
WORKERS={"worker","shared_worker","service_worker","worklet","other"}
PAGES={"page","iframe","webview"}
ATTACHABLE=WORKERS|PAGES
PROBE=r"""(()=>{'use strict';const r=globalThis,g=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);let ks=[],n=null;for(const k of Object.getOwnPropertyNames(r)){if(ks.length>=8)break;let v;try{v=r[k]}catch(_){continue}if(g(v)){ks.push(String(k));try{if(n===null)n=v.HEAPU8.length>>>0}catch(_){}}}let href='',title='',gs=false;try{href=String(location?.href||'')}catch(_){}try{title=String(document?.title||'')}catch(_){}try{gs=!!(r.I_GF1TC&&r.I_fdC8Q&&typeof r.I_fdC8Q.drawArrays==='function')}catch(_){}return{href,title,globalClass:Object.prototype.toString.call(r),isWindow:typeof window!=='undefined'&&window===r,hasDocument:typeof document!=='undefined',workerLike:(()=>{try{return typeof WorkerGlobalScope!=='undefined'&&r instanceof WorkerGlobalScope}catch(_){return false}})(),gameSurface:gs,moduleOk:ks.length>0,moduleKeys:ks,heapBytes:n,readOnly:true,ramWrites:0,inputInjection:false}})()"""

def now(): return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
def write_json(p:Path,x:Any):
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name(p.name+f".tmp-{os.getpid()}")
    t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(t,p)
def http(url:str,timeout=.8):
    q=urllib.request.Request(url,headers={"User-Agent":"WOF-Worker-Surface-Audit/1.0"})
    with urllib.request.urlopen(q,timeout=timeout) as r:return json.loads(r.read().decode())
@dataclass(frozen=True)
class Endpoint:
    host:str; port:int; browser:str; ws:str
    @property
    def base(self):return f"http://{self.host}:{self.port}"
def endpoint(port:int)->Endpoint|None:
    try:d=http(f"http://127.0.0.1:{port}/json/version")
    except Exception:return None
    w=d.get("webSocketDebuggerUrl") if isinstance(d,dict) else None
    return Endpoint("127.0.0.1",port,str(d.get("Browser")or"Chromium"),w) if isinstance(w,str)and w.startswith("ws") else None
def find_endpoint():
    for p in [9223,9222,*range(9323,9373),*range(9224,9236)]:
        e=endpoint(p)
        if e:return e
    return None
def find_browser():
    e=os.environ; local=Path(e.get("LOCALAPPDATA","")); pf=Path(e.get("PROGRAMFILES",r"C:\Program Files")); p86=Path(e.get("PROGRAMFILES(X86)",r"C:\Program Files (x86)"))
    for p in [local/"Google/Chrome/Application/chrome.exe",pf/"Google/Chrome/Application/chrome.exe",p86/"Google/Chrome/Application/chrome.exe",pf/"Microsoft/Edge/Application/msedge.exe",p86/"Microsoft/Edge/Application/msedge.exe",local/"Microsoft/Edge/Application/msedge.exe"]:
        if p.is_file():return p
    return None
def launch():
    exe=find_browser()
    if not exe:return None
    root=Path(os.environ.get("LOCALAPPDATA",str(Path.home())))/"WOF Future Danger"/"BrowserProfile"; root.mkdir(parents=True,exist_ok=True)
    flags=getattr(subprocess,"CREATE_NEW_PROCESS_GROUP",0) if os.name=="nt" else 0
    return subprocess.Popen([str(exe),"--remote-debugging-address=127.0.0.1","--remote-debugging-port=9223",f"--user-data-dir={root}","--no-first-run","--no-default-browser-check","--new-window","about:blank"],close_fds=True,creationflags=flags)

class CdpError(RuntimeError):pass
class CDP:
    def __init__(self,ws):
        self.ws_url=ws;self.ws=None;self.closed=threading.Event();self.n=1;self.lock=threading.Lock();self.pending={};self.plock=threading.Lock();self.elock=threading.Lock();self.events=[];self.session_target={};self.info={}
    def connect(self):
        self.ws=websocket.create_connection(self.ws_url,timeout=5,suppress_origin=True);self.ws.settimeout(1)
        threading.Thread(target=self._rx,daemon=True,name="surface-cdp-rx").start()
    def _rx(self):
        try:
            while not self.closed.is_set():
                try:raw=self.ws.recv()
                except websocket.WebSocketTimeoutException:continue
                if not raw:break
                try:m=json.loads(raw)
                except ValueError:continue
                if isinstance(m.get("id"),int):
                    with self.plock:q=self.pending.pop(m["id"],None)
                    if q:q.put(m)
                    continue
                if not isinstance(m.get("method"),str):continue
                e={"at":now(),"method":m["method"],"sessionId":m.get("sessionId"),"params":m.get("params")or{}}
                self._index(e)
                with self.elock:
                    if len(self.events)<3000:self.events.append(e)
        except Exception:pass
        self.closed.set()
    def _index(self,e):
        p=e["params"];method=e["method"]
        if method in {"Target.targetCreated","Target.targetInfoChanged"}:
            i=p.get("targetInfo")
            if isinstance(i,dict)and i.get("targetId"):self.info[str(i["targetId"])]=dict(i)
        if method=="Target.attachedToTarget":
            sid=p.get("sessionId");i=p.get("targetInfo")
            if isinstance(sid,str)and isinstance(i,dict)and i.get("targetId"):
                self.session_target[sid]=str(i["targetId"]);self.info[str(i["targetId"])]=dict(i)
    def req(self,method,params=None,sid=None,timeout=6):
        if method not in SAFE:raise CdpError(f"只读策略阻止 {method}")
        if self.closed.is_set():raise CdpError("CDP 已断开")
        with self.lock:i=self.n;self.n+=1
        q=queue.Queue(maxsize=1)
        with self.plock:self.pending[i]=q
        m={"id":i,"method":method,"params":params or{}}
        if sid:m["sessionId"]=sid
        try:self.ws.send(json.dumps(m,separators=(",",":")));r=q.get(timeout=timeout)
        except Exception as ex:
            with self.plock:self.pending.pop(i,None)
            raise CdpError(f"{method}: {ex}") from ex
        if "error"in r:raise CdpError(f"{method}: {r['error']}")
        x=r.get("result")
        if not isinstance(x,dict):raise CdpError(f"{method}: 返回异常")
        return x
    def attach(self,tid):
        r=self.req("Target.attachToTarget",{"targetId":tid,"flatten":True},timeout=8);sid=r.get("sessionId")
        if not isinstance(sid,str):raise CdpError("attach 无 sessionId")
        self.session_target[sid]=tid;return sid
    def close(self):
        self.closed.set()
        try:self.ws.close()
        except Exception:pass

def compact(i):
    ks=("targetId","type","title","url","attached","parentId","openerId","openerFrameId","parentFrameId","browserContextId","subtype")
    return {k:i.get(k)for k in ks if k in i}
def hint(v):return any(x in str(v or"").lower()for x in("gstyphoon","warriors of fate","/wof","wof?","wof_"))
def gst(v):return"gstyphoon"in str(v or"").lower()

def classify(x):
    d=[v for v in x.get("directTargets",[])if isinstance(v,dict)];r=[v for v in x.get("relatedTargets",[])if isinstance(v,dict)];p=[v for v in x.get("probes",[])if isinstance(v,dict)];ev=x.get("events",[])
    ids={str(v.get("targetId")or"")for v in d};mw=[v for v in p if v.get("moduleOk")is True and v.get("targetType")in WORKERS];mp=[v for v in p if v.get("moduleOk")is True and v.get("targetType")in PAGES];out=[]
    if any(v.get("type")in{"worker","shared_worker"}and gst(v.get("url"))for v in d):out.append({"code":"DIRECT_GSTYPHOON_PRESENT","rank":1,"meaning":"原始 getTargets 已直接暴露 gstyphoon Worker；旧 proof 更像时序/旧过滤路径问题。"})
    if mw and not any(gst(v.get("targetUrl"))for v in mw):out.append({"code":"WORKER_URL_FILTER_MISMATCH","rank":1,"meaning":"找到 module-ready Worker，但 TargetInfo.url 不匹配 gstyphoon；当前 URL 前置过滤会漏掉。"})
    if any(str(v.get("targetId")or"")not in ids for v in mw):out.append({"code":"RELATED_TARGET_ONLY","rank":1,"meaning":"module-ready Worker 通过 related/auto-attach surface 出现，direct snapshot 未包含。"})
    if mp:out.append({"code":"RUNTIME_IN_PAGE_OR_FRAME_CONTEXT","rank":1,"meaning":"WASM/HEAP 位于 page/iframe execution context；只扫 Worker target 不足。"})
    created={};changed=False
    for e in ev:
        if not isinstance(e,dict):continue
        i=(e.get("params")or{}).get("targetInfo")
        if not isinstance(i,dict):continue
        tid=str(i.get("targetId")or"");url=str(i.get("url")or"")
        if e.get("method")=="Target.targetCreated":created[tid]=url
        elif e.get("method")=="Target.targetInfoChanged"and tid in created and created[tid]!=url:changed=True
    if changed:out.append({"code":"TARGET_INFO_LIFECYCLE","rank":2,"meaning":"targetCreated 后 URL/信息发生 targetInfoChanged；单次快照+URL过滤存在时序风险。"})
    if not mw and not mp:
        ws=[v for v in d+r if v.get("type")in WORKERS]
        out.append({"code":"WORKER_SURFACE_WITHOUT_MODULE"if ws else"NO_WORKER_SURFACE_OBSERVED","rank":2 if ws else 1,"meaning":"存在 Worker-like surface 但模块未就绪/不在该 context。"if ws else"direct discovery、related auto-attach 与 contexts 均未观察到 Worker-like runtime surface。"})
    return sorted(out,key=lambda z:(z["rank"],z["code"]))

class Audit:
    def __init__(self,e):
        self.e=e;self.c=CDP(e.ws);self.direct={};self.related={};self.probes=[];self.frames=[];self.errors=[];self.sessions={};self.probed=set();self.auto=set();self.eidx=0
    def start(self):
        self.c.connect()
        try:self.c.req("Target.setDiscoverTargets",{"discover":True,"filter":BROAD})
        except Exception as ex:self.errors.append(f"setDiscoverTargets: {ex}")
        self.snapshot();self.attach_initial()
    def snapshot(self):
        try:r=self.c.req("Target.getTargets",{"filter":BROAD})
        except Exception:r=self.c.req("Target.getTargets")
        for i in r.get("targetInfos")or[]:
            if isinstance(i,dict)and i.get("targetId"):self.direct[str(i["targetId"])]=compact(i);self.c.info[str(i["targetId"])]=dict(i)
    def attach_initial(self):
        for tid,i in list(self.direct.items()):
            t=str(i.get("type")or"")
            if t in ATTACHABLE and(t!="service_worker"or hint(i.get("url"))or hint(i.get("title"))):self.attach_probe(tid,i,"direct")
    def attach_probe(self,tid,i,source,sid=None):
        t=str(i.get("type")or"")
        if t not in ATTACHABLE:return
        if sid is None:
            try:sid=self.c.attach(tid)
            except Exception as ex:self.errors.append(f"attach {tid[:10]} {t}: {ex}");return
        self.sessions[sid]=tid;self.c.session_target[sid]=tid
        try:self.c.req("Runtime.enable",sid=sid)
        except Exception as ex:self.errors.append(f"Runtime.enable {tid[:10]}: {ex}")
        if t in PAGES:
            try:self.frames.append({"targetId":tid,"targetType":t,"frameTree":self.c.req("Page.getFrameTree",sid=sid).get("frameTree")})
            except Exception:pass
        self.probe(sid,tid,i,source,None,{})
        if sid not in self.auto:
            try:self.c.req("Target.setAutoAttach",{"autoAttach":True,"waitForDebuggerOnStart":False,"flatten":True,"filter":RELATED},sid=sid);self.auto.add(sid)
            except Exception:pass
    def probe(self,sid,tid,i,source,cid,aux):
        k=(sid,cid if cid is not None else"default")
        if k in self.probed or len(self.probes)>=500:return
        self.probed.add(k);q={"expression":PROBE,"returnByValue":True,"silent":True}
        if cid is not None:q["contextId"]=cid
        try:r=self.c.req("Runtime.evaluate",q,sid=sid)
        except Exception:return
        if r.get("exceptionDetails"):return
        v=(r.get("result")or{}).get("value")
        if isinstance(v,dict):self.probes.append({"at":now(),"source":source,"sessionId":sid,"targetId":tid,"targetType":str(i.get("type")or""),"targetUrl":str(i.get("url")or""),"targetTitle":str(i.get("title")or""),"parentId":i.get("parentId"),"parentFrameId":i.get("parentFrameId"),"openerId":i.get("openerId"),"contextId":cid,"contextAuxData":aux,**v})
    def events(self):
        with self.c.elock:es=list(self.c.events[self.eidx:]);self.eidx=len(self.c.events)
        for e in es:
            m=e.get("method");p=e.get("params")or{};outer=e.get("sessionId")
            if m in{"Target.targetCreated","Target.targetInfoChanged"}:
                i=p.get("targetInfo")
                if isinstance(i,dict)and i.get("targetId"):
                    tid=str(i["targetId"]);self.c.info[tid]=dict(i)
                    if tid in self.direct or m=="Target.targetCreated":self.direct[tid]=compact(i)
            elif m=="Target.attachedToTarget":
                sid=p.get("sessionId");i=p.get("targetInfo")
                if isinstance(sid,str)and isinstance(i,dict)and i.get("targetId"):
                    tid=str(i["targetId"]);self.related[tid]=compact(i);self.c.info[tid]=dict(i);self.attach_probe(tid,i,f"related:{outer or'root'}",sid)
            elif m=="Runtime.executionContextCreated":
                ctx=p.get("context")
                if not(isinstance(ctx,dict)and isinstance(ctx.get("id"),int)and isinstance(outer,str)):continue
                tid=self.c.session_target.get(outer)
                if tid:self.probe(outer,tid,self.c.info.get(tid)or self.direct.get(tid)or self.related.get(tid)or{},"execution-context",ctx["id"],ctx.get("auxData")if isinstance(ctx.get("auxData"),dict)else{})
    def refresh(self):
        self.snapshot();self.events()
        seen={v.get("targetId")for v in self.probes}
        for tid,i in list(self.direct.items()):
            t=str(i.get("type")or"")
            if tid not in seen and t in ATTACHABLE and(t!="service_worker"or hint(i.get("url"))or hint(i.get("title"))):self.attach_probe(tid,i,"direct-refresh")
        self.events()
    def signal(self):
        return any(hint(v.get("url"))or hint(v.get("title"))for v in list(self.direct.values())+list(self.related.values()))or any(v.get("gameSurface")is True or v.get("moduleOk")is True or hint(v.get("href"))for v in self.probes)
    def payload(self,start,status):
        try:hl=http(self.e.base+"/json/list")
        except Exception as ex:hl={"error":str(ex)}
        x={"schema":SCHEMA,"startedAt":start,"finishedAt":now(),"status":status,"browser":{"name":self.e.browser,"endpoint":self.e.base},"safety":{"readOnly":True,"ramWrites":0,"inputInjection":False,"workerReplacement":False,"allowedCdpMethods":sorted(SAFE)},"httpJsonList":hl,"directTargets":list(self.direct.values()),"relatedTargets":list(self.related.values()),"probes":self.probes,"frameTrees":self.frames,"events":list(self.c.events),"errors":self.errors}
        x["diagnosisHints"]=classify(x);x["summary"]={"directTargetCount":len(x["directTargets"]),"relatedTargetCount":len(x["relatedTargets"]),"probeCount":len(self.probes),"eventCount":len(x["events"]),"moduleProbeCount":sum(v.get("moduleOk")is True for v in self.probes),"gameSurfaceProbeCount":sum(v.get("gameSurface")is True for v in self.probes)};return x
    def close(self):
        try:self.c.req("Target.setDiscoverTargets",{"discover":False})
        except Exception:pass
        for sid in list(self.sessions):
            try:self.c.req("Target.detachFromTarget",{"sessionId":sid})
            except Exception:pass
        self.c.close()

def selftest():
    cases=[
      ({"directTargets":[{"targetId":"w","type":"worker","url":"x.js"}],"relatedTargets":[],"probes":[{"targetId":"w","targetType":"worker","targetUrl":"x.js","moduleOk":True}],"events":[]},"WORKER_URL_FILTER_MISMATCH"),
      ({"directTargets":[{"targetId":"p","type":"page"}],"relatedTargets":[{"targetId":"w","type":"worker"}],"probes":[{"targetId":"w","targetType":"worker","moduleOk":True}],"events":[]},"RELATED_TARGET_ONLY"),
      ({"directTargets":[{"targetId":"p","type":"page"}],"relatedTargets":[],"probes":[{"targetId":"p","targetType":"page","moduleOk":True}],"events":[]},"RUNTIME_IN_PAGE_OR_FRAME_CONTEXT")]
    for x,want in cases:assert want in{x["code"]for x in classify(x)}
    assert not any(x.startswith("Input.")for x in SAFE);print("SELF-TEST PASS — Worker Surface classifier / read-only policy");return 0

def main():
    a=argparse.ArgumentParser(description="WOF Chrome Worker Surface 一键只读诊断");a.add_argument("--output",default=str(Path(__file__).with_name("WORKER_SURFACE_DIAG.json")));a.add_argument("--wait-seconds",type=float,default=300);a.add_argument("--capture-seconds",type=float,default=12);a.add_argument("--self-test",action="store_true");z=a.parse_args()
    if z.self_test:return selftest()
    out=Path(z.output).resolve();start=now();e=find_endpoint()
    if not e:
        print("未发现可连接浏览器，正在启动专用 Chrome/Edge……")
        if not launch():write_json(out,{"schema":SCHEMA,"status":"ERROR_BROWSER_NOT_FOUND","safety":{"readOnly":True,"ramWrites":0,"inputInjection":False,"workerReplacement":False}});return 2
        end=time.monotonic()+10
        while time.monotonic()<end and not e:e=endpoint(9223);time.sleep(.2)
    if not e:write_json(out,{"schema":SCHEMA,"status":"ERROR_CDP_UNAVAILABLE","safety":{"readOnly":True,"ramWrites":0,"inputInjection":False,"workerReplacement":False}});return 3
    print(f"\n浏览器已连接：{e.browser} @ {e.base}\n请在这个浏览器正常进入 WOF 房间。\n不需要 DevTools、Worker Console 或粘贴 JS。\n诊断只读：RAM 写入 0，输入注入 0。\n")
    au=Audit(e);status="COMPLETE"
    try:
        au.start();deadline=time.monotonic()+max(1,z.wait_seconds);sig=None
        while time.monotonic()<deadline:
            au.refresh()
            if au.signal():sig=time.monotonic();print("已检测到 WOF/运行时信号，正在自动收集 Worker surface……");break
            print("\r等待 WOF 房间启动……".ljust(50),end="",flush=True);time.sleep(1)
        if sig is None:status="TIMEOUT_NO_WOF_SIGNAL";print("\n未检测到 WOF signal，仍保存完整 topology。")
        else:
            end=sig+max(2,z.capture_seconds)
            while time.monotonic()<end:au.refresh();time.sleep(.35)
        au.refresh();write_json(out,au.payload(start,status))
    except Exception as ex:write_json(out,{"schema":SCHEMA,"startedAt":start,"finishedAt":now(),"status":"ERROR","browser":{"name":e.browser,"endpoint":e.base},"safety":{"readOnly":True,"ramWrites":0,"inputInjection":False,"workerReplacement":False},"errors":[str(ex)]});return 4
    finally:
        try:au.close()
        except Exception:pass
    print(f"\n诊断完成。\n唯一需要返回的文件：{out}\n浏览器/游戏未被关闭。");return 0
if __name__=="__main__":raise SystemExit(main())
