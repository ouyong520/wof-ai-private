(async()=>{
'use strict';
const EXPECTED_SHA='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
async function ensureModule(){
  if(good(globalThis._0x515056))return globalThis._0x515056;
  const until=performance.now()+8000;
  while(performance.now()<until){
    for(const k of Object.getOwnPropertyNames(globalThis)){
      let v;try{v=globalThis[k];}catch(_){continue;}
      if(good(v))return v;
    }
    await sleep(50);
  }
  return null;
}
const MOD=await ensureModule();
if(!MOD)return {ok:false,reason:'WASM module not ready',readOnly:true,ramWrites:0,inputInjection:false};
const M=MOD.HEAPU8;
const RAM=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!RAM||RAM+0x10000>M.length)return {ok:false,reason:'CPS RAM base missing/outside heap',readOnly:true,ramWrites:0,inputInjection:false};
const LOGICAL_BYTES=0x100000,VECTOR_SP=0x00FF62EE,VECTOR_PC=0x0000754A,DISPATCH_OFFSET=0x25DC;
const DISPATCH=[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2],MAX_DELTA=0x1000;
const rawAt=p=>M[p]>>>0;
const m8=(b,s,o)=>M[b+(s?(o^1):o)]>>>0;
const m32=(b,s,o)=>(m8(b,s,o)*0x1000000+m8(b,s,o+1)*0x10000+m8(b,s,o+2)*0x100+m8(b,s,o+3))>>>0;
const direct=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A],swapped=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
const match=(p,a)=>{if(p<0||p+a.length>M.length)return false;for(let i=0;i<a.length;i++)if(rawAt(p+i)!==a[i])return false;return true;};
const verify=(base,swap)=>{
  if(base<0||base+LOGICAL_BYTES>M.length)return null;
  if(m32(base,swap,0)!==VECTOR_SP||m32(base,swap,4)!==VECTOR_PC)return null;
  const vals=DISPATCH.map((_,i)=>m32(base,swap,DISPATCH_OFFSET+i*4));
  const ds=vals.map((v,i)=>(v-DISPATCH[i])|0),d=ds[0];
  if(!ds.every(x=>x===d)||Math.abs(d)>MAX_DELTA)return null;
  return {base,swap,delta:d,vals};
};
const found=[],seen=new Set(),add=z=>{if(!z)return;const k=z.base+'|'+z.swap;if(!seen.has(k)){seen.add(k);found.push(z);}};
const chunk=0x40000;
for(let start=0;start<M.length;start+=chunk){
  const end=Math.min(M.length-8,start+chunk+8);
  for(let p=start;p<end;p++){
    if(rawAt(p)===direct[0]&&match(p,direct))add(verify(p,false));
    if(rawAt(p)===swapped[0]&&match(p,swapped))add(verify(p,true));
  }
  if(start&&start%(chunk*16)===0)await sleep(0);
}
found.sort((a,b)=>a.base-b.base||Number(a.swap)-Number(b.swap));
if(found.length!==1)return {ok:false,reason:'ROM locator candidate count '+found.length,candidateCount:found.length,readOnly:true,ramWrites:0,inputInjection:false};
if(!globalThis.crypto?.subtle?.digest)return {ok:false,reason:'Web Crypto SHA-256 unavailable',candidateCount:1,readOnly:true,ramWrites:0,inputInjection:false};
const c=found[0],logical=new Uint8Array(LOGICAL_BYTES);
for(let i=0;i<LOGICAL_BYTES;i++)logical[i]=M[c.base+(c.swap?(i^1):i)]>>>0;
const digest=await globalThis.crypto.subtle.digest('SHA-256',logical);
const sha256=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
const identity={ok:sha256===EXPECTED_SHA,reason:sha256===EXPECTED_SHA?'exact World 921031 full CPU-logical SHA-256':'full CPU-logical SHA-256 mismatch',sha256,expectedSha256:EXPECTED_SHA,description:'Warriors of Fate (World 921031)',locator:{heapBase:c.base,swap16:c.swap,uniformDelta:c.delta,dispatchEntries:c.vals}};
return {ok:identity.ok,reason:identity.reason,identity,readOnly:true,ramWrites:0,inputInjection:false};
})()
