(async()=>{
'use strict';
const RELEASE='wof-alpha-rc3';
const SCHEMA='wof-alpha-v2';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/product/alpha/';
const scope=typeof window!=='undefined'&&window===globalThis?window:self;
const cfg=scope.__WOF_ALPHA_CONFIG;
if(!cfg||cfg.release!==RELEASE||typeof cfg.session!=='string'||cfg.session.length<16||typeof cfg.channel!=='string'||cfg.schema!==SCHEMA){
  throw new Error('WOF Alpha RC3 requires the session-bound RC3 bootstrap; refusing unpaired or stale load');
}
const SESSION=cfg.session,CHANNEL=cfg.channel;
const load=async name=>{
  const r=await fetch(RAW+name+'?rc3='+encodeURIComponent(RELEASE)+'&x='+Date.now(),{cache:'no-store'});
  if(!r.ok)throw new Error('fetch '+name+' '+r.status);
  (0,eval)(await r.text());
};

if(typeof window!=='undefined'&&window===globalThis){
  try{window.WOFALPHAHUD?.dispose?.();}catch(_){}
  await load('wof_alpha_hud_model.js');
  await load('wof_alpha_hud.js');
  window.WOFALPHA={release:RELEASE,schema:SCHEMA,session:SESSION,mode:'page',status:()=>window.WOFALPHAHUD?.status?.()||null};
  return window.WOFALPHA;
}

try{self.__WOF_ALPHA_RUNTIME?.stop?.();}catch(_){}
await load('wof_alpha_core.js');
const C=self.WOFAlphaCore;
if(!C||C.VERSION!=='wof-alpha-core-rc3'||C.SCHEMA!==SCHEMA)throw new Error('RC3 core identity mismatch');

const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
async function moduleFind(){
  if(good(self._0x515056))return self._0x515056;
  const until=performance.now()+8000;
  while(performance.now()<until){
    for(const k of Object.getOwnPropertyNames(self)){
      let v;try{v=self[k];}catch(_){continue;}
      if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}
    }
    await new Promise(r=>setTimeout(r,50));
  }
  return null;
}
const MOD=await moduleFind();
const bc=new BroadcastChannel(CHANNEL);
const post=(kind,payload={})=>bc.postMessage({schema:SCHEMA,session:SESSION,kind,release:RELEASE,sentAt:Date.now(),...payload});
if(!MOD){
  post('diag',{status:'DISABLED',reason:'WASM module not found'});
  self.__WOF_ALPHA_RUNTIME={release:RELEASE,running:false,readOnly:true,ramWrites:0,inputInjection:false,session:SESSION,stop(){try{bc.close();}catch(_){}}};
  return self.__WOF_ALPHA_RUNTIME;
}
const M=MOD.HEAPU8,R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const X=a=>Math.round(S32(a+4)/65536);

function m8(base,swap,o){return M[base+(swap?(o^1):o)]>>>0;}
function m32(base,swap,o){return (m8(base,swap,o)*0x1000000+m8(base,swap,o+1)*0x10000+m8(base,swap,o+2)*0x100+m8(base,swap,o+3))>>>0;}
async function locateRomCandidate(){
  const direct=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A],swapped=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
  const expected=C.ROM_IDENTITY.dispatchEntries,off=C.ROM_IDENTITY.dispatchOffset,logicalBytes=C.ROM_IDENTITY.logicalBytes;
  const rawAt=p=>M[p]>>>0;
  const match=(p,a)=>{if(p<0||p+a.length>M.length)return false;for(let i=0;i<a.length;i++)if(rawAt(p+i)!==a[i])return false;return true;};
  const verify=(base,swap)=>{
    if(base<0||base+logicalBytes>M.length)return null;
    if(m32(base,swap,0)!==C.ROM_IDENTITY.vectorSp||m32(base,swap,4)!==C.ROM_IDENTITY.vectorPc)return null;
    if(base+off+expected.length*4>M.length)return null;
    const vals=expected.map((_,i)=>m32(base,swap,off+i*4));
    const deltas=vals.map((v,i)=>(v-expected[i])|0),d=deltas[0];
    if(!deltas.every(x=>x===d)||Math.abs(d)>C.ROM_IDENTITY.maxUniformDelta)return null;
    return{base,swap,vals,delta:d};
  };
  const found=[];
  const seen=new Set();
  const add=z=>{if(!z)return;const k=z.base+'|'+z.swap;if(!seen.has(k)){seen.add(k);found.push(z);}};
  const chunk=0x40000;
  for(let start=0;start<M.length;start+=chunk){
    const end=Math.min(M.length-8,start+chunk+8);
    for(let p=start;p<end;p++){
      if(rawAt(p)===direct[0]&&match(p,direct))add(verify(p,false));
      if(rawAt(p)===swapped[0]&&match(p,swapped))add(verify(p,true));
    }
    if(start&&start%(chunk*16)===0)await new Promise(r=>setTimeout(r,0));
  }
  found.sort((a,b)=>a.base-b.base||Number(a.swap)-Number(b.swap));
  const selected=found.length===1?found[0]:null;
  return{
    selected,
    locator:{
      source:'browser-wasm-rom',candidateCount:found.length,selectedHeapBase:selected?.base??null,swap16:selected?.swap??null,
      vectorSp:C.ROM_IDENTITY.vectorSp,vectorPc:C.ROM_IDENTITY.vectorPc,dispatchOffset:off,
      dispatchEntries:selected?.vals??null,uniformDelta:selected?.delta??null
    }
  };
}
function hex(bytes){return Array.from(new Uint8Array(bytes),x=>x.toString(16).padStart(2,'0')).join('');}
async function hashLogicalProgram(candidate){
  if(!candidate)throw new Error('ROM locator did not produce exactly one candidate');
  if(!self.crypto?.subtle?.digest)throw new Error('Web Crypto SHA-256 unavailable');
  const n=C.ROM_IDENTITY.logicalBytes,logical=new Uint8Array(n),base=candidate.base,swap=candidate.swap;
  for(let i=0;i<n;i++)logical[i]=M[base+(swap?(i^1):i)]>>>0;
  const digestPromise=self.crypto.subtle.digest('SHA-256',logical);
  const timeout=new Promise((_,reject)=>setTimeout(()=>reject(new Error('SHA-256 timeout')),5000));
  const digest=await Promise.race([digestPromise,timeout]);
  return hex(digest);
}

let selfIndexes=null;
try{selfIndexes=[U16(0xFFBE1C+0x7C),U16(0xFFBEFC+0x7C),U16(0xFFBFDC+0x7C)];}catch(_){}
let identityPromise=null;
function establishIdentityOnce(){
  if(identityPromise)return identityPromise;
  identityPromise=(async()=>{
    let located=null;
    try{located=await locateRomCandidate();}
    catch(e){
      return C.validateIdentityProbe({moduleOk:good(MOD),ramBase:R,ramWithinHeap:!!R&&R+0x10000<=M.length,selfIndexes,
        romLocator:null,romIdentity:{source:'browser-wasm-rom',logicalBytes:C.ROM_IDENTITY.logicalBytes,hashStatus:'error',sha256:'',error:String(e?.message||e)}});
    }
    let romIdentity={source:'browser-wasm-rom',logicalBytes:C.ROM_IDENTITY.logicalBytes,hashStatus:'pending',sha256:''};
    if(located.selected){
      try{
        romIdentity={...romIdentity,hashStatus:'accepted',sha256:await hashLogicalProgram(located.selected)};
      }catch(e){
        romIdentity={...romIdentity,hashStatus:'error',error:String(e?.message||e)};
      }
    }
    return C.validateIdentityProbe({moduleOk:good(MOD),ramBase:R,ramWithinHeap:!!R&&R+0x10000<=M.length,selfIndexes,
      romLocator:located.locator,romIdentity});
  })();
  return identityPromise;
}
const identity=await establishIdentityOnce();
if(!identity.ok){
  post('diag',{status:'DISABLED',reason:'identity-fail: '+identity.reasons.join('; '),identity});
  self.__WOF_ALPHA_RUNTIME={
    release:RELEASE,running:false,readOnly:true,ramWrites:0,inputInjection:false,session:SESSION,identity,
    stop(){try{bc.close();}catch(_){}},status(){return{release:RELEASE,running:false,session:SESSION,identity,readOnly:true,ramWrites:0,inputInjection:false};}
  };
  return self.__WOF_ALPHA_RUNTIME;
}

const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC};
function snap(i){
  const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)return null;
  const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(!frameEnd&&!next)return null;
  const target7E=U16(a+0x7E),pb=PBASE[target7E],enemyX=X(a),targetX=pb?X(pb):null;
  return{slot:i,type,target7E,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),
    frameEnd,next,value30:U32(a+0x30),timer34:U16(a+0x34),payload6C:U16(a+0x6C),enemyX,targetX};
}
const engine=C.createEngine();
let running=true,polls=0,lastError=null;
const tick=()=>{
  if(!running)return;
  try{
    const rows=[];for(let i=0;i<SLOTS;i++){const s=snap(i);if(s)rows.push(s);}
    const state=engine.step(rows,performance.now());post('state',{...state,identitySignature:identity.signature});polls++;
  }catch(e){
    lastError=String(e?.stack||e);running=false;engine.reset();post('diag',{status:'DISABLED',reason:'runtime exception: '+lastError});
  }
};
const timer=setInterval(tick,10);tick();
self.__WOF_ALPHA_RUNTIME={
  release:RELEASE,session:SESSION,identity,readOnly:true,ramWrites:0,inputInjection:false,
  stop(){running=false;clearInterval(timer);engine.reset();try{bc.close();}catch(_){}},
  status(){return{release:RELEASE,running,session:SESSION,identity,readOnly:true,ramWrites:0,inputInjection:false,polls,lastError,engine:engine.diagnostics()};}
};
console.log('✅ WOF Alpha RC3 detector running · exact wof / World 921031 identity',identity.signature,'session',SESSION.slice(0,8));
return self.__WOF_ALPHA_RUNTIME;
})().catch(e=>{console.error('WOF_ALPHA_RC3_LOADER_ERROR',e);throw e;});
