from __future__ import annotations

from typing import Any

from .probe import WORLD_DESCRIPTION, WORLD_SHA256


def select_unique_exact_candidate(candidate_diagnostics: list[dict[str, Any]], expected_sha256: str = WORLD_SHA256) -> dict[str, Any]:
    """Mirror the field probe's fail-closed exact-match decision for deterministic self-checks."""
    exact = [row for row in candidate_diagnostics if isinstance(row, dict) and row.get("sha256") == expected_sha256]
    if len(exact) == 0:
        raise ValueError("no ROM locator candidate matched exact World 921031 full CPU-logical SHA-256")
    if len(exact) > 1:
        raise ValueError(f"ambiguous exact World 921031 ROM locator matches {len(exact)}")
    return dict(exact[0])


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
if(found.length===0)return {{ok:false,reason:'ROM locator candidate count 0',moduleOk:true,moduleKey:key,heapBytes:M.length,candidateCount:0,exactMatchCount:0,candidateDiagnostics:[],readOnly:true,ramWrites:0,inputInjection:false}};
if(!self.crypto?.subtle?.digest)return {{ok:false,reason:'Web Crypto SHA-256 unavailable',moduleOk:true,moduleKey:key,heapBytes:M.length,candidateCount:found.length,exactMatchCount:0,readOnly:true,ramWrites:0,inputInjection:false}};
const candidateDiagnostics=[];
for(const c of found){{
  const logical=new Uint8Array(LOGICAL_BYTES);
  for(let i=0;i<LOGICAL_BYTES;i++)logical[i]=M[c.base+(c.swap?(i^1):i)]>>>0;
  const digest=await self.crypto.subtle.digest('SHA-256',logical);
  const sha256=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
  candidateDiagnostics.push({{heapBase:c.base,swap16:c.swap,uniformDelta:c.delta,dispatchEntries:c.vals,sha256,exactMatch:sha256===EXPECTED}});
}}
const exact=candidateDiagnostics.filter(x=>x.exactMatch);
if(exact.length===0)return {{ok:false,reason:'no ROM locator candidate matched exact World 921031 full CPU-logical SHA-256',moduleOk:true,moduleKey:key,heapBytes:M.length,candidateCount:found.length,exactMatchCount:0,candidateDiagnostics,expectedSha256:EXPECTED,readOnly:true,ramWrites:0,inputInjection:false}};
if(exact.length>1)return {{ok:false,reason:'ambiguous exact World 921031 ROM locator matches '+exact.length,moduleOk:true,moduleKey:key,heapBytes:M.length,candidateCount:found.length,exactMatchCount:exact.length,candidateDiagnostics,expectedSha256:EXPECTED,readOnly:true,ramWrites:0,inputInjection:false}};
const selectedDiag=exact[0],c=found.find(x=>x.base===selectedDiag.heapBase&&x.swap===selectedDiag.swap16);
if(!c)return {{ok:false,reason:'exact ROM locator selection internal mismatch',moduleOk:true,moduleKey:key,heapBytes:M.length,candidateCount:found.length,exactMatchCount:1,candidateDiagnostics,expectedSha256:EXPECTED,readOnly:true,ramWrites:0,inputInjection:false}};
return {{
  ok:true,
  reason:'unique exact World 921031 full CPU-logical SHA-256 among '+found.length+' locator candidates',
  moduleOk:true,moduleKey:key,heapOk:true,heapBytes:M.length,candidateCount:found.length,exactMatchCount:1,
  candidateDiagnostics,
  locator:{{heapBase:c.base,swap16:c.swap,uniformDelta:c.delta,dispatchEntries:c.vals}},
  logicalBytes:LOGICAL_BYTES,sha256:EXPECTED,expectedSha256:EXPECTED,description:'{WORLD_DESCRIPTION}',
  readOnly:true,ramWrites:0,inputInjection:false
}};
}})()"""
