(function(root,factory){
'use strict';
const api=factory();
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaTransportAuthority=api;
const binding=root.__WOF_ALPHA_REAL_ADAPTER_BINDING;
if(binding)api.install(root,binding).catch(error=>{
  try{root.__WOF_ALPHA_REAL_TRANSPORT={running:false,lastError:String(error?.message||error),readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false};}catch(_){}
});
})(typeof self!=='undefined'?self:globalThis,function(){
'use strict';
const RELEASE='wof-alpha-rc3';
const SCHEMA='wof-alpha-v2';
const TRANSPORT='wof-alpha-safe-transport-v1';
const CORE_VERSION='wof-alpha-core-rc3';
const GOLDEN_SHA='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const IDENTITY_SIGNATURE='wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/product/alpha/';
const HEX32=/^[0-9a-f]{32}$/;
const SAFETY=Object.freeze({readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false,blobRewrite:false,gamePostMessageControl:false,heapWrites:false,assistMode:false});

function validBinding(b){
  return !!b&&b.release===RELEASE&&b.schema===SCHEMA&&b.transportVersion===TRANSPORT&&HEX32.test(String(b.session||''))&&
    HEX32.test(String(b.pairNonce||''))&&Number.isInteger(b.pairGeneration)&&b.pairGeneration>0&&HEX32.test(String(b.runtimeEpoch||''))&&
    b.launcherIdentitySha===GOLDEN_SHA&&typeof b.channel==='string'&&b.channel==='WOF_ALPHA_'+b.session;
}
function sameAuthority(a,b){
  return !!a&&!!b&&a.runtimeEpoch===b.runtimeEpoch&&a.session===b.session&&a.pairGeneration===b.pairGeneration&&a.pairNonce===b.pairNonce;
}
function createTickAuthorityGate(binding){
  if(!validBinding(binding))throw new Error('invalid transport binding');
  const current=Object.freeze({runtimeEpoch:binding.runtimeEpoch,session:binding.session,pairGeneration:binding.pairGeneration,pairNonce:binding.pairNonce});
  let active=true,inFlight=null,tickAuthoritySeq=0,skippedTicks=0;
  return{
    start(){
      if(!active)return null;
      if(inFlight){skippedTicks++;return null;}
      inFlight=Object.freeze({...current,tickAuthorityId:++tickAuthoritySeq});
      return inFlight;
    },
    finish(authority){
      if(!active||!inFlight||!authority||authority.tickAuthorityId!==inFlight.tickAuthorityId||!sameAuthority(authority,inFlight)||!sameAuthority(authority,current))return false;
      inFlight=null;return true;
    },
    revoke(){active=false;inFlight=null;},
    status(){return{active,inFlight:!!inFlight,queueDepth:0,skippedTicks,...current};},
    matchesEnvelope(m){return !!m&&m.session===current.session&&m.pairGeneration===current.pairGeneration&&m.pairNonce===current.pairNonce;}
  };
}

function moduleGood(v){return !!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);}
async function findModule(scope){
  if(moduleGood(scope._0x515056))return scope._0x515056;
  const until=(scope.performance?.now?.()||Date.now())+8000;
  while((scope.performance?.now?.()||Date.now())<until){
    for(const k of Object.getOwnPropertyNames(scope)){
      let v;try{v=scope[k];}catch(_){continue;}
      if(moduleGood(v)){scope._0x515056=v;scope.__WOF_MODULE_GLOBAL_KEY=k;return v;}
    }
    await new Promise(resolve=>setTimeout(resolve,50));
  }
  return null;
}
async function ensureCore(scope){
  if(scope.WOFAlphaCore?.VERSION===CORE_VERSION)return scope.WOFAlphaCore;
  if(typeof scope.fetch!=='function')throw new Error('核心加载接口不可用');
  const response=await scope.fetch(RAW+'wof_alpha_core.js?transport='+encodeURIComponent(TRANSPORT)+'&x='+Date.now(),{cache:'no-store'});
  if(!response.ok)throw new Error('核心加载失败 HTTP '+response.status);
  (0,eval)(await response.text());
  if(scope.WOFAlphaCore?.VERSION!==CORE_VERSION||scope.WOFAlphaCore?.SCHEMA!==SCHEMA)throw new Error('核心身份不匹配');
  return scope.WOFAlphaCore;
}
async function localIdentity(scope,mod,binding){
  try{
    if(!moduleGood(mod)||binding.launcherIdentitySha!==GOLDEN_SHA)return{ok:false,reason:'模块或 Discovery 身份不匹配',...SAFETY};
    const M=mod.HEAPU8,LOGICAL_BYTES=0x100000,VECTOR_SP=0x00FF62EE,VECTOR_PC=0x0000754A,DISPATCH_OFFSET=0x25DC;
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
      return{base,swap,delta:d,vals};
    };
    const found=[],seen=new Set(),add=z=>{if(!z)return;const k=z.base+'|'+z.swap;if(!seen.has(k)){seen.add(k);found.push(z);}};
    const chunk=0x40000;
    for(let start=0;start<M.length;start+=chunk){
      const end=Math.min(M.length-8,start+chunk+8);
      for(let p=start;p<end;p++){
        if(rawAt(p)===direct[0]&&match(p,direct))add(verify(p,false));
        if(rawAt(p)===swapped[0]&&match(p,swapped))add(verify(p,true));
      }
      if(start&&start%(chunk*16)===0)await new Promise(resolve=>setTimeout(resolve,0));
    }
    found.sort((a,b)=>a.base-b.base||Number(a.swap)-Number(b.swap));
    if(found.length!==1)return{ok:false,reason:'ROM 定位候选数量 '+found.length,candidateCount:found.length,...SAFETY};
    if(!scope.crypto?.subtle?.digest)return{ok:false,reason:'当前原生 Worker 不支持 Web Crypto SHA-256',candidateCount:1,...SAFETY};
    const c=found[0],logical=new Uint8Array(LOGICAL_BYTES);
    for(let i=0;i<LOGICAL_BYTES;i++)logical[i]=M[c.base+(c.swap?(i^1):i)]>>>0;
    const digest=await scope.crypto.subtle.digest('SHA-256',logical);
    const sha256=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
    if(sha256!==GOLDEN_SHA)return{ok:false,reason:'当前原生 Worker 的完整 CPU 逻辑 ROM SHA-256 不匹配',sha256,expectedSha256:GOLDEN_SHA,candidateCount:1,...SAFETY};

    const R=mod.HEAPU32[0x2e39e4>>>2]>>>0;
    if(!R||R+0x10000>M.length)return{ok:false,reason:'CPS RAM 窗口不可用',sha256,expectedSha256:GOLDEN_SHA,candidateCount:1,...SAFETY};
    const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
    const U16=a=>((B(a)<<8)|B(a+1))>>>0;
    const selfIndexes=[U16(0xFFBE1C+0x7C),U16(0xFFBEFC+0x7C),U16(0xFFBFDC+0x7C)];
    if(selfIndexes[0]!==0||selfIndexes[1]!==4||selfIndexes[2]!==8)return{ok:false,reason:'P1/P2/P3 本地身份不匹配',sha256,expectedSha256:GOLDEN_SHA,candidateCount:1,...SAFETY};
    return{ok:true,reason:'exact World 921031 detector-local full CPU-logical SHA-256',identitySignature:IDENTITY_SIGNATURE,sha256,expectedSha256:GOLDEN_SHA,logicalBytes:LOGICAL_BYTES,locator:{heapBase:c.base,swap16:c.swap,uniformDelta:c.delta,dispatchEntries:c.vals},selfIndexes,...SAFETY};
  }catch(error){return{ok:false,reason:String(error?.message||error),...SAFETY};}
}
function stableWarningsHash(warnings){
  return JSON.stringify((warnings||[]).map(w=>[w.ruleId,w.slot,w.target7E,w.sourceSide,w.threatSide,w.attack,w.publication,w.evidence]));
}

async function install(scope,binding){
  if(!validBinding(binding))throw new Error('正式传输绑定无效');
  const previous=scope.__WOF_ALPHA_REAL_TRANSPORT;
  if(previous&&typeof previous.stop==='function'&&previous.stop('reinstall')!==true)throw new Error('旧 observer 未安全停止');
  const gate=createTickAuthorityGate(binding);
  const core=await ensureCore(scope);
  const mod=await findModule(scope);
  if(!mod)throw new Error('WASM 模块未找到');
  const identity=await localIdentity(scope,mod,binding);
  if(!identity.ok||identity.sha256!==GOLDEN_SHA)throw new Error('检测器本地 World 921031 身份校验失败：'+identity.reason);

  const M=mod.HEAPU8,R=mod.HEAPU32[0x2e39e4>>>2]>>>0;
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
  const U16=a=>((B(a)<<8)|B(a+1))>>>0;
  const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
  const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
  const X=a=>Math.round(S32(a+4)/65536);
  const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC};
  function snap(i){
    const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)return null;
    const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(!frameEnd&&!next)return null;
    const target7E=U16(a+0x7E),pb=PBASE[target7E],enemyX=X(a),targetX=pb?X(pb):null;
    return{slot:i,type,target7E,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),
      frameEnd,next,value30:U32(a+0x30),timer34:U16(a+0x34),payload6C:U16(a+0x6C),enemyX,targetX};
  }

  const bc=new scope.BroadcastChannel(binding.channel);
  const engine=core.createEngine();
  let running=true,timer=0,polls=0,lastError=null,lastHash=null,lastPublishedAt=null,seq=0;
  const nowMono=()=>Number(scope.performance?.now?.()||Date.now());
  const envelope=(kind,payload={})=>({schema:SCHEMA,kind,release:RELEASE,coreVersion:CORE_VERSION,transportVersion:TRANSPORT,
    session:binding.session,pairGeneration:binding.pairGeneration,pairNonce:binding.pairNonce,identitySignature:IDENTITY_SIGNATURE,sentAt:Date.now(),...SAFETY,...payload});
  const postDiag=reason=>{try{bc.postMessage(envelope('diag',{status:'DISABLED',code:'runtime-exception',reason:String(reason||'检测器已禁用')}));}catch(_){}};

  function beginTick(){
    if(!running)return;
    const authority=gate.start();
    if(!authority)return;
    let rows=[];
    try{for(let i=0;i<SLOTS;i++){const s=snap(i);if(s)rows.push(s);}}
    catch(error){
      if(gate.finish(authority)){lastError=String(error?.message||error);running=false;postDiag('只读快照失败：'+lastError);}
      return;
    }
    const sampledAt=nowMono();
    Promise.resolve().then(()=>engine.step(rows,sampledAt)).then(state=>{
      if(!gate.finish(authority))return;
      polls++;
      const warnings=Array.isArray(state?.warnings)?state.warnings:[];
      const hash=stableWarningsHash(warnings),changed=hash!==lastHash,heartbeat=lastPublishedAt===null||sampledAt-lastPublishedAt>=250;
      if(changed||heartbeat){
        seq++;
        bc.postMessage(envelope('state',{seq,warnings}));
        lastHash=hash;lastPublishedAt=sampledAt;
      }
    }).catch(error=>{
      if(!gate.finish(authority))return;
      lastError=String(error?.message||error);running=false;engine.reset();postDiag('检测器运行异常：'+lastError);
    });
  }

  timer=setInterval(beginTick,10);
  beginTick();
  const runtime={
    version:TRANSPORT,release:RELEASE,running:true,identitySignature:IDENTITY_SIGNATURE,identity,...SAFETY,
    stop(){
      if(!running&&gate.status().active===false)return true;
      running=false;runtime.running=false;try{clearInterval(timer);}catch(_){};gate.revoke();try{engine.reset();}catch(_){};try{bc.close();}catch(_){};return true;
    },
    status(){return{version:TRANSPORT,release:RELEASE,running:running&&gate.status().active,identitySignature:IDENTITY_SIGNATURE,identity,...SAFETY,polls,lastError,...gate.status()};}
  };
  scope.__WOF_ALPHA_REAL_TRANSPORT=runtime;
  return runtime.status();
}

return{RELEASE,SCHEMA,TRANSPORT,GOLDEN_SHA,IDENTITY_SIGNATURE,SAFETY,validBinding,sameAuthority,createTickAuthorityGate,install};
});