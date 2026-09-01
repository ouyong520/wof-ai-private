from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .cdp import CdpClient, CdpError, CdpSession


WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
WORLD_DESCRIPTION = "Warriors of Fate (World 921031)"
GSTYPHOON_RE = re.compile(r"(?:^|[/\\])gstyphoon[^/?#]*\.js(?:[?#].*)?$", re.IGNORECASE)


LIGHT_WORKER_PROBE = r"""(()=>{
'use strict';
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
let mod=null,key=null;
try{if(good(self._0x515056)){mod=self._0x515056;key='_0x515056';}}catch(_){}
if(!mod){
  for(const k of Object.getOwnPropertyNames(self)){
    let v;try{v=self[k];}catch(_){continue;}
    if(good(v)){mod=v;key=k;break;}
  }
}
if(!mod)return {moduleOk:false,heapOk:false,readOnly:true,ramWrites:0,inputInjection:false};
const heap=mod.HEAPU8;
let ramBase=null,selfIndexes=null,ramWithinHeap=false;
try{
  ramBase=mod.HEAPU32[0x2e39e4>>>2]>>>0;
  ramWithinHeap=!!ramBase&&ramBase+0x10000<=heap.length;
  const B=a=>heap[ramBase+((((a-0xFF0000)&0xffff)^1))]>>>0;
  const U16=a=>((B(a)<<8)|B(a+1))>>>0;
  selfIndexes=[U16(0xFFBE1C+0x7C),U16(0xFFBEFC+0x7C),U16(0xFFBFDC+0x7C)];
}catch(_){}
return {moduleOk:true,moduleKey:key,heapOk:heap instanceof Uint8Array,heapBytes:heap.length,ramBase,ramWithinHeap,selfIndexes,readOnly:true,ramWrites:0,inputInjection:false};
})()"""


PAGE_PROBE = r"""(()=>({
  href:String(location.href),
  title:String(document.title||''),
  gameSurface:!!(window.I_GF1TC&&window.I_fdC8Q&&typeof window.I_fdC8Q.drawArrays==='function'),
  alphaBootstrap:!!(window.__WOF_ALPHA_BOOTSTRAP_RC5||window.__WOF_ALPHA_BOOTSTRAP_RC3),
  readOnly:true
}))()"""


IDENTITY_PROBE = rf"""(async()=>{{
'use strict';
const EXPECTED='{WORLD_SHA256}';
const LOGICAL_BYTES=0x100000;
const VECTOR_SP=0x00FF62EE,VECTOR_PC=0x0000754A,DISPATCH_OFFSET=0x25DC;
const DISPATCH=[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2],MAX_DELTA=0x1000;
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
let mod=null,key=null;
try{{if(good(self._0x515056)){{mod=self._0x515056;key='_0x515056';}}}}catch(_){{}}
if(!mod){{for(const k of Object.getOwnPropertyNames(self)){{let v;try{{v=self[k];}}catch(_){{continue;}}if(good(v)){{mod=v;key=k;break;}}}}}}
if(!mod)return {{ok:false,reason:'WASM module not found',moduleOk:false,readOnly:true,ramWrites:0,inputInjection:false}};
const M=mod.HEAPU8;
const rawAt=p=>M[p]>>>0;
const m8=(b,s,o)=>M[b+(s?(o^1):o)]>>>0;
const m32=(b,s,o)=>(m8(b,s,o)*0x1000000+m8(b,s,o+1)*0x10000+m8(b,s,o+2)*0x100+m8(b,s,o+3))>>>0;
const direct=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A],swapped=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
const match=(p,a)=>{{if(p<0||p+a.length>M.length)return false;for(let i=0;i<a.length;i++)if(rawAt(p+i)!==a[i])return false;return true;}};
const verify=(base,swap)=>{{
  if(base<0||base+LOGICAL_BYTES>M.length)return null;
  if(m32(base,swap,0)!==VECTOR_SP||m32(base,swap,4)!==VECTOR_PC)return null;
  const vals=DISPATCH.map((_,i)=>m32(base,swap,DISPATCH_OFFSET+i*4));
  const ds=vals.map((v,i)=>(v-DISPATCH[i])|0),d=ds[0];
  if(!ds.every(x=>x===d)||Math.abs(d)>MAX_DELTA)return null;
  return {{base,swap,delta:d,vals}};
}};
const found=[],seen=new Set();
const add=z=>{{if(!z)return;const k=z.base+'|'+z.swap;if(!seen.has(k)){{seen.add(k);found.push(z);}}}};
const chunk=0x40000;
for(let start=0;start<M.length;start+=chunk){{
  const end=Math.min(M.length-8,start+chunk+8);
  for(let p=start;p<end;p++){{
    if(rawAt(p)===direct[0]&&match(p,direct))add(verify(p,false));
    if(rawAt(p)===swapped[0]&&match(p,swapped))add(verify(p,true));
  }}
  if(start&&start%(chunk*16)===0)await new Promise(r=>setTimeout(r,0));
}}
found.sort((a,b)=>a.base-b.base||Number(a.swap)-Number(b.swap));
if(found.length!==1)return {{ok:false,reason:'ROM locator candidate count '+found.length,moduleOk:true,moduleKey:key,heapBytes:M.length,candidateCount:found.length,readOnly:true,ramWrites:0,inputInjection:false}};
if(!self.crypto?.subtle?.digest)return {{ok:false,reason:'Web Crypto SHA-256 unavailable',moduleOk:true,moduleKey:key,heapBytes:M.length,candidateCount:1,readOnly:true,ramWrites:0,inputInjection:false}};
const c=found[0],logical=new Uint8Array(LOGICAL_BYTES);
for(let i=0;i<LOGICAL_BYTES;i++)logical[i]=M[c.base+(c.swap?(i^1):i)]>>>0;
const digest=await self.crypto.subtle.digest('SHA-256',logical);
const sha256=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
return {{
  ok:sha256===EXPECTED,
  reason:sha256===EXPECTED?'exact World 921031 full CPU-logical SHA-256':'full CPU-logical SHA-256 mismatch',
  moduleOk:true,moduleKey:key,heapOk:true,heapBytes:M.length,candidateCount:1,
  locator:{{heapBase:c.base,swap16:c.swap,uniformDelta:c.delta,dispatchEntries:c.vals}},
  logicalBytes:LOGICAL_BYTES,sha256,expectedSha256:EXPECTED,description:'{WORLD_DESCRIPTION}',
  readOnly:true,ramWrites:0,inputInjection:false
}};
}})()"""


@dataclass(frozen=True)
class TargetChoice:
    page: dict[str, Any] | None
    worker: dict[str, Any] | None
    worker_probe: dict[str, Any] | None
    identity: dict[str, Any] | None
    reason: str | None = None


def is_gstyphoon_worker(target: dict[str, Any]) -> bool:
    return target.get("type") == "worker" and bool(GSTYPHOON_RE.search(str(target.get("url") or "")))


def choose_unique_supported_worker(candidates: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None:
    supported = [(t, p, i) for (t, p, i) in candidates if p.get("moduleOk") and i and i.get("ok") is True]
    if len(supported) == 1:
        t, p, i = supported[0]
        return t, p, i  # type: ignore[return-value]
    return None


def _probe_session(client: CdpClient, target_id: str, expression: str, *, await_promise: bool = False, timeout: float = 8.0) -> Any:
    session: CdpSession | None = None
    try:
        session = client.attach(target_id)
        session.request("Runtime.enable")
        return session.evaluate(expression, await_promise=await_promise, timeout=timeout)
    finally:
        if session:
            session.close()


def _find_page_for_worker(client: CdpClient, worker: dict[str, Any], page_targets: list[dict[str, Any]]) -> dict[str, Any] | None:
    opener = worker.get("openerId")
    if opener:
        linked = [t for t in page_targets if t.get("targetId") == opener]
        if len(linked) == 1:
            return linked[0]

    surfaced: list[dict[str, Any]] = []
    for target in page_targets:
        tid = str(target.get("targetId") or "")
        if not tid:
            continue
        try:
            probe = _probe_session(client, tid, PAGE_PROBE)
        except CdpError:
            continue
        if isinstance(probe, dict) and probe.get("gameSurface") is True:
            enriched = dict(target)
            enriched["wofPageProbe"] = probe
            surfaced.append(enriched)
    if len(surfaced) == 1:
        return surfaced[0]
    if len(surfaced) > 1:
        keyword = [
            t for t in surfaced
            if re.search(r"\bwof\b|warriors.?of.?fate", str(t.get("url") or "") + " " + str(t.get("title") or ""), re.I)
        ]
        if len(keyword) == 1:
            return keyword[0]
    return None


def _identity_for_worker(
    client: CdpClient,
    target_id: str,
    *,
    identity_timeout: float,
    identity_cache: dict[str, dict[str, Any]] | None,
) -> dict[str, Any]:
    cached = identity_cache.get(target_id) if identity_cache else None
    if isinstance(cached, dict):
        return cached
    try:
        identity = _probe_session(client, target_id, IDENTITY_PROBE, await_promise=True, timeout=identity_timeout)
    except CdpError as exc:
        identity = {"ok": False, "reason": str(exc), "readOnly": True, "ramWrites": 0, "inputInjection": False}
    if not isinstance(identity, dict):
        identity = {"ok": False, "reason": "identity probe returned malformed value", "readOnly": True, "ramWrites": 0, "inputInjection": False}
    sha = identity.get("sha256")
    if identity_cache is not None and isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha):
        identity_cache[target_id] = identity
    return identity


def discover(client: CdpClient, *, identity_timeout: float = 20.0, identity_cache: dict[str, dict[str, Any]] | None = None) -> TargetChoice:
    targets = client.request("Target.getTargets").get("targetInfos") or []
    if not isinstance(targets, list):
        raise CdpError("Target.getTargets returned malformed targetInfos")
    workers = [t for t in targets if isinstance(t, dict) and is_gstyphoon_worker(t)]
    pages = [t for t in targets if isinstance(t, dict) and t.get("type") == "page"]
    if not workers:
        return TargetChoice(None, None, None, None, "no gstyphoon worker target")

    light_rows: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for target in workers:
        target_id = str(target.get("targetId") or "")
        if not target_id:
            continue
        try:
            light = _probe_session(client, target_id, LIGHT_WORKER_PROBE)
        except CdpError as exc:
            light = {"moduleOk": False, "reason": str(exc), "readOnly": True, "ramWrites": 0, "inputInjection": False}
        light_rows.append((target, light if isinstance(light, dict) else {}))

    module_rows = [(t, p) for t, p in light_rows if p.get("moduleOk") is True]
    if not module_rows:
        if len(light_rows) == 1:
            target, light = light_rows[0]
            return TargetChoice(_find_page_for_worker(client, target, pages), target, light, None, "gstyphoon worker found; WASM module/heap not ready")
        return TargetChoice(None, None, None, None, f"gstyphoon workers found but no unique module-ready WOF worker: {len(workers)}")

    if len(module_rows) == 1:
        worker, light = module_rows[0]
        target_id = str(worker.get("targetId") or "")
        page = _find_page_for_worker(client, worker, pages)
        identity = _identity_for_worker(client, target_id, identity_timeout=identity_timeout, identity_cache=identity_cache)
        reason = None if identity.get("ok") is True and page else (
            "supported worker found; WOF page target ambiguous/not yet surfaced" if identity.get("ok") is True else str(identity.get("reason") or "World 921031 identity not accepted")
        )
        return TargetChoice(page, worker, light, identity, reason)

    supported: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for worker, light in module_rows:
        target_id = str(worker.get("targetId") or "")
        identity = _identity_for_worker(client, target_id, identity_timeout=identity_timeout, identity_cache=identity_cache)
        if identity.get("ok") is True:
            supported.append((worker, light, identity))
    if len(supported) != 1:
        return TargetChoice(None, None, None, None, f"ambiguous supported WOF workers: {len(supported)} of {len(module_rows)} module-ready")
    worker, light, identity = supported[0]
    page = _find_page_for_worker(client, worker, pages)
    reason = None if page else "supported worker found; WOF page target ambiguous/not yet surfaced"
    return TargetChoice(page, worker, light, identity, reason)
