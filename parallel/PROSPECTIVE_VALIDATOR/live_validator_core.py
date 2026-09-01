from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RECORDER_DIR = HERE.parent / "WOF052L_RECORDER"
if str(RECORDER_DIR) not in sys.path:
    sys.path.insert(0, str(RECORDER_DIR))

try:
    import recorder as recorder_core  # type: ignore
except ModuleNotFoundError:
    recorder_core = None  # available in-repo; allows standalone probe syntax tests

from validator import (
    ValidationError,
    compact_result,
    load_json,
    make_session,
    validate,
    validate_manifest,
)

CORPUS_SCHEMA = "wof-prospective-corpus-v1"
PROBE_VERSION = "wof-prospective-live-probe-v1"
DEFAULT_POLL = 0.5
DISCOVERY_INTERVAL = 1.0
CHECKPOINT_INTERVAL = 5.0

IDENTITY_JS = r"""(async()=>{
'use strict';
const EXPECTED_SHA='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
let MOD=null;
try{if(good(globalThis._0x515056))MOD=globalThis._0x515056;}catch(_){}
if(!MOD){for(const k of Object.getOwnPropertyNames(globalThis)){let v;try{v=globalThis[k];}catch(_){continue;}if(good(v)){MOD=v;break;}}}
if(!MOD)return {ok:false,reason:'WASM module not ready',readOnly:true,ramWrites:0,inputInjection:false};
const M=MOD.HEAPU8;
const LOGICAL_BYTES=0x100000,VECTOR_SP=0x00FF62EE,VECTOR_PC=0x0000754A,DISPATCH_OFFSET=0x25DC;
const DISPATCH=[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2],MAX_DELTA=0x1000;
const rawAt=p=>M[p]>>>0;
const m8=(b,s,o)=>M[b+(s?(o^1):o)]>>>0;
const m32=(b,s,o)=>(m8(b,s,o)*0x1000000+m8(b,s,o+1)*0x10000+m8(b,s,o+2)*0x100+m8(b,s,o+3))>>>0;
const direct=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A],swapped=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
const match=(p,a)=>{if(p<0||p+a.length>M.length)return false;for(let i=0;i<a.length;i++)if(rawAt(p+i)!==a[i])return false;return true;};
const verify=(base,swap)=>{if(base<0||base+LOGICAL_BYTES>M.length)return null;if(m32(base,swap,0)!==VECTOR_SP||m32(base,swap,4)!==VECTOR_PC)return null;const vals=DISPATCH.map((_,i)=>m32(base,swap,DISPATCH_OFFSET+i*4));const ds=vals.map((v,i)=>(v-DISPATCH[i])|0),d=ds[0];if(!ds.every(x=>x===d)||Math.abs(d)>MAX_DELTA)return null;return {base,swap,delta:d,vals};};
const found=[],seen=new Set(),add=z=>{if(!z)return;const k=z.base+'|'+z.swap;if(!seen.has(k)){seen.add(k);found.push(z);}};
const chunk=0x40000;
for(let start=0;start<M.length;start+=chunk){const end=Math.min(M.length-8,start+chunk+8);for(let p=start;p<end;p++){if(rawAt(p)===direct[0]&&match(p,direct))add(verify(p,false));if(rawAt(p)===swapped[0]&&match(p,swapped))add(verify(p,true));}if(start&&start%(chunk*16)===0)await new Promise(r=>setTimeout(r,0));}
found.sort((a,b)=>a.base-b.base||Number(a.swap)-Number(b.swap));
if(found.length!==1)return {ok:false,reason:'ROM locator candidate count '+found.length,candidateCount:found.length,readOnly:true,ramWrites:0,inputInjection:false};
if(!globalThis.crypto?.subtle?.digest)return {ok:false,reason:'Web Crypto SHA-256 unavailable',readOnly:true,ramWrites:0,inputInjection:false};
const c=found[0],logical=new Uint8Array(LOGICAL_BYTES);for(let i=0;i<LOGICAL_BYTES;i++)logical[i]=M[c.base+(c.swap?(i^1):i)]>>>0;
const digest=await globalThis.crypto.subtle.digest('SHA-256',logical);const sha256=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
return {ok:sha256===EXPECTED_SHA,sha256,expectedSha256:EXPECTED_SHA,description:'Warriors of Fate (World 921031)',reason:sha256===EXPECTED_SHA?'exact World 921031 full CPU-logical SHA-256':'full CPU-logical SHA-256 mismatch',readOnly:true,ramWrites:0,inputInjection:false};
})()"""


def build_probe_js(manifest: dict[str, Any]) -> str:
    manifest_text = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    return r"""(()=>{
'use strict';
const VERSION='__PROBE_VERSION__';
const MANIFEST=__MANIFEST__;
const old=globalThis.__WOF_PROSPECTIVE_VALIDATOR;
if(old&&typeof old.stop==='function'){try{old.stop();}catch(_){}}
let MOD=null;
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
try{if(good(globalThis._0x515056))MOD=globalThis._0x515056;}catch(_){}
if(!MOD){for(const k of Object.getOwnPropertyNames(globalThis)){let v;try{v=globalThis[k];}catch(_){continue;}if(good(v)){MOD=v;break;}}}
if(!MOD)return {ok:false,reason:'WASM module not ready',version:VERSION,readOnly:true,ramWrites:0,inputInjection:false};
const M=MOD.HEAPU8,RAM=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!RAM||RAM+0x10000>M.length)return {ok:false,reason:'CPS RAM base missing/outside heap',version:VERSION,readOnly:true,ramWrites:0,inputInjection:false};
const B=a=>M[RAM+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const X=a=>Math.round(S32(a+4)/65536),Y=a=>Math.round(S32(a+8)/65536);
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC},PN={0:'P1',4:'P2',8:'P3'};
const side=dx=>dx==null?null:dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
const hx=n=>(n>>>0).toString(16),fam=z=>String(z||'').replace(/\|TM[^|]*/,'|TM*'),r1=x=>Math.round(x*10)/10;
function snap(i){const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)return null;const fe=U32(a+0x12),nx=U32(a+0x2C);if(!fe&&!nx)return null;const t=U16(a+0x7E),pb=PBASE[t],ex=X(a),tx=pb?X(pb):null,dx=tx==null?null:tx-ex;return {slot:i,type,target7E:t,target:PN[t]||null,side:side(dx),x:ex,y:Y(a),state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd:fe,next:nx,value30:U32(a+0x30),timer34:U16(a+0x34),payload6C:U16(a+0x6C)};}
const sig=s=>`S${s.state99}/A${s.action2A}/B${s.b2B}|BODY${s.body}|FE${hx(s.frameEnd)}|NX${hx(s.next)}|V${hx(s.value30)}|TM${s.timer34}|P6C${s.payload6C}`;
const get=(o,p)=>{let v=o;for(const k of String(p).split('.')){if(v&&typeof v==='object'&&Object.prototype.hasOwnProperty.call(v,k))v=v[k];else return null;}return v;};
function pred(o,p){const a=get(o,p.path),op=p.op||'eq',e=p.value;if(op==='exists')return e===false?a==null:a!=null;if(op==='eq')return a===e;if(op==='ne')return a!==e;if(op==='in')return Array.isArray(e)&&e.includes(a);if(op==='not_in')return Array.isArray(e)&&!e.includes(a);if(a==null)return false;if(op==='lt')return a<e;if(op==='lte')return a<=e;if(op==='gt')return a>e;if(op==='gte')return a>=e;return false;}
const all=(o,ps)=>(ps||[]).every(p=>pred(o,p));
function smatch(s,m){if(m.signature!=null&&s.signature!==m.signature)return false;if(m.family!=null&&s.family!==m.family)return false;return all(s,m.predicates||[]);}
function ruleMatch(history,current){const rule=MANIFEST.rule||{};if(!all(current,rule.currentPredicates||[]))return false;const q=rule.sequence;if(!q)return true;const n=(q.kind==='tail3'||q.kind==='triple')?3:2;if(history.length<n)return false;const tail=history.slice(-n);return tail.every((s,i)=>smatch(s,q.states[i]));}
function category(attack,lead){const expected=(MANIFEST.outcome?.expectedAttacks||[]).includes(attack),w=MANIFEST.windows||{},strict=Number(w.strictMaxMs??150),jitter=Number(w.jitterMaxMs??Math.max(strict,220)),late=Number(w.lateMaxMs??Math.max(jitter,1000));if(!expected)return 'hardMiss';if(lead<=strict)return 'strict';if(lead<=jitter)return 'jitter';if(lead<=late)return 'late';return 'hardMiss';}
const hardMissMs=Number(MANIFEST.windows?.hardMissMs??1500),intervalMs=Number(MANIFEST.samplingMs??10),MAX_HISTORY=24,MAX_QUEUE=1024;
const prev=new Map(),hist=new Map(),armed=new Map(),suppressed=new Set(),queue=[];let running=true,timer=null,seq=0;
const counts={signal:0,strict:0,jitter:0,late:0,hardMiss:0,censored:0};
function emit(trace){queue.push({id:++seq,kind:'result',...trace});if(queue.length>MAX_QUEUE)queue.shift();}
function censor(slot,reason,now){const a=armed.get(slot);if(!a)return;armed.delete(slot);counts.censored++;emit({...a.trace,activeAttack:null,leadMs:r1(now-a.at),censored:true,category:'censored',censorReason:reason,targetStable:a.target7E===a.lastTarget7E,sideStable:a.side===a.lastSide,retargets:a.retargets});}
function arm(slot,s,h,t){counts.signal++;armed.set(slot,{at:t,target7E:s.target7E,lastTarget7E:s.target7E,side:s.side,lastSide:s.side,retargets:[],trace:{slot:s.slot,type:s.type,evidenceClass:'prospective',signalAtPerf:r1(t),current:{...s,signature:sig(s),family:fam(sig(s))},states:h.map(x=>({...x})),matchedSignatures:h.map(x=>x.signature),targetStart7E:s.target7E,targetStart:s.target,sideStart:s.side}});}
function tick(){if(!running)return;const t=performance.now();for(let i=0;i<SLOTS;i++){const s=snap(i),p=prev.get(i)||null;if(!s){censor(i,'slot-disappeared',t);hist.delete(i);suppressed.delete(i);prev.delete(i);continue;}if(p&&p.type!==s.type){censor(i,'slot-type-replaced',t);hist.delete(i);armed.delete(i);suppressed.delete(i);}
    let h=hist.get(i)||[];
    if(s.attack===0){if(!p||p.attack!==0||p.type!==s.type){h=[];hist.set(i,h);armed.delete(i);suppressed.delete(i);}const z=sig(s),state={...s,signature:z,family:fam(z)};if(!h.length||h[h.length-1].signature!==z){h.push(state);if(h.length>MAX_HISTORY)h.shift();}else h[h.length-1]=state;
      const a=armed.get(i);if(a){if(a.lastTarget7E!==s.target7E){a.retargets.push({relMs:r1(t-a.at),from7E:a.lastTarget7E,to7E:s.target7E});a.lastTarget7E=s.target7E;}a.lastSide=s.side;if(t-a.at>=hardMissMs){armed.delete(i);suppressed.add(i);counts.hardMiss++;emit({...a.trace,activeAttack:null,leadMs:r1(t-a.at),censored:false,category:'hardMiss',hardMissReason:'no-active-before-timeout',targetStable:a.target7E===a.lastTarget7E,sideStable:a.side===a.lastSide,retargets:a.retargets});}}
      if(!armed.has(i)&&!suppressed.has(i)&&ruleMatch(h,state))arm(i,s,h,t);
    } else if(p&&p.attack===0&&s.attack!==0){const a=armed.get(i);if(a){if(a.lastTarget7E!==s.target7E){a.retargets.push({relMs:r1(t-a.at),from7E:a.lastTarget7E,to7E:s.target7E,atActiveEdge:true});a.lastTarget7E=s.target7E;}a.lastSide=s.side;const lead=r1(t-a.at),cat=category(s.attack,lead);counts[cat]++;emit({...a.trace,activeAttack:s.attack,leadMs:lead,censored:false,category:cat,targetAtActive7E:s.target7E,targetAtActive:s.target,sideAtActive:s.side,targetStable:a.target7E===s.target7E,sideStable:a.side===s.side,retargets:a.retargets});armed.delete(i);}hist.delete(i);suppressed.delete(i);}
    prev.set(i,s);
  }}
timer=setInterval(tick,Math.max(5,intervalMs));
const api={version:VERSION,running:true,manifestId:MANIFEST.id,readOnly:true,ramWrites:0,inputInjection:false,windowWorkerReplacement:false,drain(){const events=queue.splice(0,queue.length);return {ok:true,events,status:this.status()};},status(){return {ok:true,version:VERSION,running,manifestId:MANIFEST.id,counts:{...counts},pending:[...armed.entries()].map(([slot,a])=>({...a.trace,slot,type:a.trace.type,leadMs:r1(performance.now()-a.at),targetStart7E:a.target7E,targetLast7E:a.lastTarget7E,sideStart:a.side,sideLast:a.lastSide,retargets:a.retargets})),readOnly:true,ramWrites:0,inputInjection:false,windowWorkerReplacement:false};},stop(){if(!running)return this.status();running=false;if(timer)clearInterval(timer);const now=performance.now();for(const slot of [...armed.keys()])censor(slot,'validator-stopped',now);this.running=false;return this.drain();}};
globalThis.__WOF_PROSPECTIVE_VALIDATOR=api;
return {ok:true,version:VERSION,manifestId:MANIFEST.id,readOnly:true,ramWrites:0,inputInjection:false,windowWorkerReplacement:false};
})()""".replace("__PROBE_VERSION__", PROBE_VERSION).replace("__MANIFEST__", manifest_text)


def fleet_manifest_path() -> Path:
    root = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
    return Path(root) / "WOF Future Danger" / "Fleet" / "instances.json"


def fleet_endpoints(path: Path) -> list[tuple[str, int, str]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(raw, dict) or raw.get("version") != "wof-browser-fleet-v1":
        return []
    if raw.get("readOnly") is not True or int(raw.get("ramWrites") or 0) != 0 or raw.get("inputInjection") is not False:
        return []
    out = []
    for item in raw.get("instances") or []:
        if not isinstance(item, dict):
            continue
        host = str(item.get("host") or "127.0.0.1")
        try:
            port = int(item.get("port"))
        except (TypeError, ValueError):
            continue
        if host not in {"127.0.0.1", "localhost"}:
            continue
        out.append((host, port, f"fleet-{item.get('id', port)}"))
    return out


def candidate_endpoints(manifest_path: Path | None, explicit_port: int | None) -> list[tuple[str, int, str]]:
    if recorder_core is None:
        raise RuntimeError("parallel/WOF052L_RECORDER/recorder.py not found")
    if explicit_port is not None:
        out = [("127.0.0.1", explicit_port, f"local-{explicit_port}")]
    else:
        out = fleet_endpoints(manifest_path or fleet_manifest_path())
        if not out:
            for port in recorder_core.candidate_ports(None):
                out.append(("127.0.0.1", int(port), f"local-{port}"))
    seen = set()
    unique = []
    for row in out:
        key = (row[0], row[1])
        if key not in seen:
            seen.add(key); unique.append(row)
    return unique


@dataclass
class Room:
    room_id: str
    target_id: str
    session: Any
    started_at: str
    pending: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Endpoint:
    host: str
    port: int
    label: str
    client: Any | None = None
    rooms: dict[str, Room] = field(default_factory=dict)
    last_discovery: float = 0.0

    def connect(self) -> bool:
        ep = recorder_core.probe_endpoint(self.host, self.port)
        if not ep:
            self.close_client()
            return False
        if self.client is not None and not self.client.closed:
            return True
        self.close_client()
        try:
            self.client = recorder_core.CdpClient(ep.websocket_url)
            self.client.connect()
            self.client.targets()
            return True
        except Exception:
            self.close_client()
            return False

    def close_client(self) -> None:
        if self.client is not None:
            try: self.client.close()
            except Exception: pass
        self.client = None

    def close(self) -> None:
        for room in list(self.rooms.values()):
            try: room.session.close()
            except Exception: pass
        self.rooms.clear()
        self.close_client()


class LiveValidator:
    def __init__(self, manifest: dict[str, Any], output: Path, fleet_manifest: Path | None, port: int | None):
        self.manifest = manifest
        self.session = make_session(manifest)
        self.output = output
        self.probe_js = build_probe_js(manifest)
        self.endpoints = [Endpoint(*x) for x in candidate_endpoints(fleet_manifest, port)]
        self.traces: list[dict[str, Any]] = []
        self.started = time.monotonic()
        self.last_checkpoint = 0.0

    def attach_room(self, endpoint: Endpoint, target: dict[str, Any]) -> None:
        if endpoint.client is None:
            return
        tid = str(target.get("targetId") or "")
        if not tid or tid in endpoint.rooms:
            return
        session = None
        try:
            session = endpoint.client.attach(tid)
            session.request("Runtime.enable", timeout=5.0)
            light = session.evaluate(recorder_core.LIGHT_PROBE, timeout=5.0)
            if not isinstance(light, dict) or light.get("moduleOk") is not True or light.get("ramWithinHeap") is not True:
                session.close(); return
            ident = session.evaluate(IDENTITY_JS, await_promise=True, timeout=45.0)
            if not isinstance(ident, dict) or ident.get("ok") is not True or ident.get("sha256") != recorder_core.WORLD_SHA256:
                session.close(); return
            boot = session.evaluate(self.probe_js, timeout=8.0)
            if not isinstance(boot, dict) or boot.get("ok") is not True:
                session.close(); return
            room_id = f"{endpoint.label}-{tid[:10]}-{uuid.uuid4().hex[:6]}"
            endpoint.rooms[tid] = Room(room_id=room_id, target_id=tid, session=session, started_at=recorder_core.utc_iso())
            print(f"+ 已连接房间 {room_id}｜World 921031｜只读")
        except Exception as exc:
            if session:
                try: session.close()
                except Exception: pass
            print(f"连接 Worker 失败但不影响游戏：{exc}")

    def ingest(self, room: Room, payload: dict[str, Any]) -> None:
        status = payload.get("status") if isinstance(payload, dict) else None
        if isinstance(status, dict):
            room.pending = list(status.get("pending") or [])
        for event in (payload.get("events") or []) if isinstance(payload, dict) else []:
            if not isinstance(event, dict) or event.get("kind") != "result":
                continue
            trace = dict(event)
            trace.pop("kind", None)
            trace["roomId"] = room.room_id
            trace["evidenceClass"] = "prospective"
            trace["startedAt"] = room.started_at
            self.traces.append(trace)
            room.events.append(trace)

    def finalize_room(self, endpoint: Endpoint, tid: str, reason: str, remote: bool) -> None:
        room = endpoint.rooms.pop(tid, None)
        if not room:
            return
        if remote:
            try:
                payload = room.session.evaluate("globalThis.__WOF_PROSPECTIVE_VALIDATOR ? globalThis.__WOF_PROSPECTIVE_VALIDATOR.stop() : null", timeout=5.0)
                if isinstance(payload, dict): self.ingest(room, payload)
            except Exception:
                pass
        if room.pending:
            for pending in room.pending:
                trace = dict(pending)
                trace.update({
                    "roomId": room.room_id, "evidenceClass": "prospective", "startedAt": room.started_at,
                    "activeAttack": None, "censored": True,
                    "targetStable": pending.get("targetStart7E") == pending.get("targetLast7E"),
                    "sideStable": pending.get("sideStart") == pending.get("sideLast"),
                    "retargets": pending.get("retargets") or [], "censorReason": reason,
                })
                self.traces.append(trace)
        try: room.session.close()
        except Exception: pass
        print(f"- 房间结束 {room.room_id}（{reason}）")

    def discover_and_poll(self, endpoint: Endpoint, now: float) -> None:
        if not endpoint.connect():
            for tid in list(endpoint.rooms):
                self.finalize_room(endpoint, tid, "browser-cdp-disconnect", remote=False)
            return
        if now - endpoint.last_discovery >= DISCOVERY_INTERVAL:
            endpoint.last_discovery = now
            try:
                targets = endpoint.client.targets()
            except Exception:
                for tid in list(endpoint.rooms):
                    self.finalize_room(endpoint, tid, "browser-cdp-disconnect", remote=False)
                endpoint.close_client(); return
            current = {str(t.get("targetId")): t for t in targets if isinstance(t, dict) and t.get("targetId")}
            for tid in list(endpoint.rooms):
                if tid not in current:
                    self.finalize_room(endpoint, tid, "worker-closed-or-reloaded", remote=False)
            for target in targets:
                if recorder_core.GSTYPHOON_RE.search(str(target.get("url") or "")) and target.get("type") == "worker":
                    self.attach_room(endpoint, target)
        for tid, room in list(endpoint.rooms.items()):
            try:
                payload = room.session.evaluate("globalThis.__WOF_PROSPECTIVE_VALIDATOR ? globalThis.__WOF_PROSPECTIVE_VALIDATOR.drain() : null", timeout=4.0)
                if not isinstance(payload, dict) or payload.get("ok") is not True:
                    raise RuntimeError("live probe drain malformed")
                self.ingest(room, payload)
            except Exception:
                self.finalize_room(endpoint, tid, "worker-cdp-error", remote=False)

    def corpus(self, final: bool) -> dict[str, Any]:
        return {
            "schema": CORPUS_SCHEMA,
            "runId": f"prospective-{self.session['candidateId']}",
            "candidateId": self.session["candidateId"],
            "candidateSha256": self.session["candidateSha256"],
            "frozenAt": self.session["frozenAt"],
            "evidenceClass": "prospective",
            "status": "complete" if final else "running",
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "windowWorkerReplacement": False},
            "traces": self.traces,
        }

    def write(self, final: bool) -> dict[str, Any]:
        self.output.parent.mkdir(parents=True, exist_ok=True)
        corpus = self.corpus(final)
        self.output.write_text(json.dumps(corpus, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = validate(self.manifest, self.traces, [{"path": str(self.output), "schema": CORPUS_SCHEMA, "traces": len(self.traces)}])
        result_path = self.output.with_name(self.output.stem + ".result.json")
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result

    def run(self) -> int:
        print(f"WOF 前瞻验证：{self.manifest['id']}")
        print("安全：只读模式开启｜游戏内存写入 0｜游戏输入注入 无｜window.Worker 替换 无")
        print("正在复用 Browser Fleet / localhost CDP。没有可用端点时只等待，不影响游戏。Ctrl+C 结束。")
        try:
            while True:
                now = time.monotonic()
                for endpoint in self.endpoints:
                    self.discover_and_poll(endpoint, now)
                if now - self.last_checkpoint >= CHECKPOINT_INTERVAL:
                    self.last_checkpoint = now
                    result = self.write(False)
                    p = result["prospective"]
                    rooms = sum(len(e.rooms) for e in self.endpoints)
                    print(f"\r在线房间 {rooms}｜signal {p['signal']}｜strict {p['strict']}｜jitter {p['jitter']}｜late {p['late']}｜hard miss {p['hardMiss']}｜censored {p['censored']}   ", end="", flush=True)
                time.sleep(DEFAULT_POLL)
        except KeyboardInterrupt:
            pass
        finally:
            for endpoint in self.endpoints:
                for tid in list(endpoint.rooms):
                    self.finalize_room(endpoint, tid, "validator-stopped", remote=True)
                endpoint.close()
        result = self.write(True)
        print("\n" + json.dumps(compact_result(result), ensure_ascii=False, indent=2))
        print(f"证据：{self.output}")
        print(f"结果：{self.output.with_name(self.output.stem + '.result.json')}")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="WOF 通用 live prospective validator（只读）")
    ap.add_argument("manifest", help="候选 manifest JSON")
    ap.add_argument("--output", help="统一 prospective corpus JSON 输出")
    ap.add_argument("--fleet-manifest", help="Browser Fleet instances.json；省略使用默认路径")
    ap.add_argument("--cdp-port", type=int, help="只连接指定 localhost CDP 端口")
    ap.add_argument("--dump-probe", help="仅输出生成的 JS probe 到文件并退出（测试用）")
    args = ap.parse_args()
    try:
        manifest = validate_manifest(load_json(args.manifest))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"候选 manifest 无效：{exc}")
        return 2
    if args.dump_probe:
        Path(args.dump_probe).write_text(build_probe_js(manifest) + "\n", encoding="utf-8")
        return 0
    if recorder_core is None:
        print("找不到 parallel/WOF052L_RECORDER/recorder.py，无法复用 CDP 基础设施。")
        return 2
    stamp = time.strftime("%Y%m%d_%H%M%S")
    output = Path(args.output).expanduser().resolve() if args.output else HERE / "results" / f"{stamp}_{manifest['id']}_live_corpus.json"
    fleet = Path(args.fleet_manifest).expanduser().resolve() if args.fleet_manifest else None
    return LiveValidator(manifest, output, fleet, args.cdp_port).run()


if __name__ == "__main__":
    raise SystemExit(main())
