(()=>{
'use strict';
const VERSION='wof-alpha-v1-dual-live-proof-worker-recovery-v2';
const CHANNEL='wof-alpha-v1-dual-live-proof-recovery-v2';
const G=globalThis;
try{G.WOFAlphaV1DualProofWorker?.stop?.();}catch(_){}
const mod=G._0x515056,M=mod?.HEAPU8,R=mod?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM base unavailable');
const binding=G.__WOF_ALPHA_REAL_ADAPTER_BINDING||null;
const bc=new BroadcastChannel(CHANNEL);
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const F16=a=>S32(a)/65536;
const PLAYER_BASES={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC};
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
let running=true,timer=0,seq=0,lastProfiles=null,rebindBusy=false;
function players(sampleAt){
  const out={};
  for(const [name,a] of Object.entries(PLAYER_BASES)){
    const present=!!B(a);
    out[name]=present?{present:true,x:F16(a+4),y:F16(a+8),z:F16(a+12),sampleAt,confidence:1,epoch:binding?.runtimeEpoch||null,projectionEpoch:binding?.runtimeEpoch||null}:{present:false,sampleAt,confidence:1,epoch:binding?.runtimeEpoch||null,projectionEpoch:binding?.runtimeEpoch||null};
  }
  return out;
}
function enemies(sampleAt){
  const out=[];
  for(let i=0;i<SLOTS;i++){
    const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)continue;
    const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(!frameEnd&&!next)continue;
    out.push({slot:i,sourceId:'enemy-slot-'+i,type,target7E:U16(a+0x7E),enemyX:F16(a+4),enemyY:F16(a+8),enemyZ:F16(a+12),sampleAt,confidence:1,epoch:binding?.runtimeEpoch||null,projectionEpoch:binding?.runtimeEpoch||null});
  }
  return out;
}
function commonCamera(){
  try{
    const s=G.WOFHUDANCHOR?.result?.();
    const c=s?.lockedCamera||s?.camera?.selected||null;
    return c?{address:c.address??null,read:c.read??'u16be',value:Number.isFinite(c.value)?c.value:null}:null;
  }catch(_){return null;}
}
function post(kind,payload={}){try{bc.postMessage({schema:CHANNEL,kind,version:VERSION,at:Date.now(),...payload});}catch(_){} }
function snapshot(){
  const at=Date.now(),camera=commonCamera();
  post('live-snapshot',{seq:++seq,binding:binding?{session:binding.session,runtimeEpoch:binding.runtimeEpoch,pairGeneration:binding.pairGeneration,pairNonce:binding.pairNonce,launcherIdentitySha:binding.launcherIdentitySha,channel:binding.channel}:null,
    camera,players:players(at),enemies:enemies(at),alphaTransportStatus:G.__WOF_ALPHA_REAL_TRANSPORT?.status?.()||null});
}
function validCandidateProfiles(payload){
  const p=payload?.playerProfile,e=payload?.enemyProfile;
  if(!p||!e||p.proofOnlyRuntimeBinding!==true||e.proofOnlyRuntimeBinding!==true)return{ok:false,reason:'PROOF_ONLY_PROFILE_TAG_MISSING'};
  if(p.evidenceClass!=='REAL_BROWSER_WOF_BOUNDED_DYNAMIC_LIVE_PROOF'||e.evidenceClass!=='REAL_BROWSER_WOF_BOUNDED_DYNAMIC_LIVE_PROOF')return{ok:false,reason:'REAL_LIVE_EVIDENCE_GUARD_MISSING'};
  const pv=G.WOFAlphaPlayerHeadWarning?.validateProofProfile?.(p),ev=G.WOFAlphaEnemyTargetLabels?.validateProofProfile?.(e);
  if(!pv?.ok)return{ok:false,reason:pv?.reason||'PLAYER_PROFILE_REJECTED'};
  if(!ev?.ok)return{ok:false,reason:ev?.reason||'ENEMY_PROFILE_REJECTED'};
  if(!binding||!G.WOFAlphaTransportAuthority?.install)return{ok:false,reason:'ALPHA_TRANSPORT_INSTALL_API_UNAVAILABLE'};
  return{ok:true};
}
async function reinstallWithProfiles(payload){
  if(rebindBusy)return{ok:false,reason:'REBIND_BUSY'};
  const valid=validCandidateProfiles(payload);if(!valid.ok)return valid;
  rebindBusy=true;
  const originalFetch=G.fetch;
  if(typeof originalFetch!=='function'){rebindBusy=false;return{ok:false,reason:'FETCH_UNAVAILABLE'};}
  const playerProfile=JSON.parse(JSON.stringify(payload.playerProfile)),enemyProfile=JSON.parse(JSON.stringify(payload.enemyProfile));
  const responseFor=value=>({ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(value)),text:async()=>JSON.stringify(value)});
  G.fetch=async function(input,init){
    const url=String(input?.url||input||'');
    if(url.includes('/product/alpha/wof_alpha_player_head_projection.json'))return responseFor(playerProfile);
    if(url.includes('/product/alpha/wof_alpha_enemy_head_projection.json'))return responseFor(enemyProfile);
    return originalFetch.call(this,input,init);
  };
  try{
    const status=await G.WOFAlphaTransportAuthority.install(G,binding);
    lastProfiles={playerProfile,enemyProfile,proofId:payload.proofId||playerProfile.proofId,installedAt:Date.now()};
    return{ok:true,status,lastProfiles:{proofId:lastProfiles.proofId,installedAt:lastProfiles.installedAt}};
  }catch(error){return{ok:false,reason:String(error?.message||error)};}
  finally{G.fetch=originalFetch;rebindBusy=false;}
}
async function authorityGap(ms){
  if(!lastProfiles)return{ok:false,reason:'NO_LIVE_BOUND_PROFILES'};
  const duration=Math.max(350,Math.min(900,Number(ms)||450));
  try{G.__WOF_ALPHA_REAL_TRANSPORT?.stop?.('proof-authority-gap');}catch(_){}
  post('authority-gap-start',{durationMs:duration});
  await new Promise(resolve=>setTimeout(resolve,duration));
  const result=await reinstallWithProfiles({...lastProfiles,proofId:lastProfiles.proofId});
  post('authority-gap-end',{durationMs:duration,result});
  return result;
}
bc.onmessage=e=>{
  const m=e.data;if(m?.schema!==CHANNEL)return;
  if(m.kind==='request-snapshot')snapshot();
  else if(m.kind==='bind-live-profiles')reinstallWithProfiles(m).then(result=>post('bind-live-profiles-result',{requestId:m.requestId||null,result}));
  else if(m.kind==='exercise-authority-gap')authorityGap(m.durationMs).then(result=>post('exercise-authority-gap-result',{requestId:m.requestId||null,result}));
};
timer=setInterval(snapshot,50);snapshot();
G.WOFAlphaV1DualProofWorker={version:VERSION,status(){return{running,seq,rebindBusy,binding:!!binding,lastProfiles:lastProfiles?{proofId:lastProfiles.proofId,installedAt:lastProfiles.installedAt}:null};},stop(){if(!running)return;running=false;if(timer)clearInterval(timer);try{bc.close();}catch(_){}try{delete G.WOFAlphaV1DualProofWorker;}catch(_){}}};
console.log('✅ Alpha V1 dual live-proof Worker observer ready');
})();
