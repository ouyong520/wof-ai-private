(function(root,factory){
'use strict';
const api=factory();
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaFieldAdapter=api;
})(typeof self!=='undefined'?self:globalThis,function(){
'use strict';
const VERSION='wof-alpha-field-adapter-v1';
const RELEASE='wof-alpha-rc3';
const SCHEMA='wof-alpha-v2';
const TRANSPORT='wof-alpha-safe-transport-v1';
const CORE_VERSION='wof-alpha-core-rc3';
const LABELS_VERSION='wof-alpha-enemy-target-labels-v1';
const PLAYER_HEAD_VERSION='wof-alpha-player-head-warning-v1';
const GOLDEN_SHA='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const IDENTITY_SIGNATURE='wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8';
const LOGICAL_BYTES=0x100000;
const PLAYER_SPATIAL_PUBLISH_MS=20;
const HEX32=/^[0-9a-f]{32}$/;
const SAFETY=Object.freeze({readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false,blobRewrite:false,gamePostMessageControl:false,heapWrites:false,assistMode:false});
const PLAYER_LOCAL_IDENTITY=Object.freeze([
  Object.freeze({name:'P1',base:0xFFBE1C,expectedSelfIndex:0}),
  Object.freeze({name:'P2',base:0xFFBEFC,expectedSelfIndex:4}),
  Object.freeze({name:'P3',base:0xFFBFDC,expectedSelfIndex:8})
]);

function moduleGood(v){return !!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);}
async function findModule(scope){
  if(moduleGood(scope._0x515056))return scope._0x515056;
  const until=(scope.performance?.now?.()||Date.now())+8000;
  while((scope.performance?.now?.()||Date.now())<until){
    for(const k of Object.getOwnPropertyNames(scope)){
      let v;try{v=scope[k];}catch(_){continue;}
      if(moduleGood(v)){scope._0x515056=v;return v;}
    }
    await new Promise(resolve=>setTimeout(resolve,50));
  }
  return null;
}
function validBinding(b){
  const l=b?.launcherLocator;
  return !!b&&b.release===RELEASE&&b.schema===SCHEMA&&b.transportVersion===TRANSPORT&&
    HEX32.test(String(b.session||''))&&HEX32.test(String(b.pairNonce||''))&&
    Number.isInteger(b.pairGeneration)&&b.pairGeneration>0&&HEX32.test(String(b.runtimeEpoch||''))&&
    b.launcherIdentitySha===GOLDEN_SHA&&typeof b.channel==='string'&&b.channel==='WOF_ALPHA_'+b.session&&
    !!l&&Number.isInteger(l.heapBase)&&l.heapBase>=0&&typeof l.swap16==='boolean';
}
function sameAuthority(a,b){return !!a&&!!b&&a.runtimeEpoch===b.runtimeEpoch&&a.session===b.session&&a.pairGeneration===b.pairGeneration&&a.pairNonce===b.pairNonce;}
function createTickAuthorityGate(binding){
  if(!validBinding(binding))throw new Error('invalid field adapter binding');
  const current=Object.freeze({runtimeEpoch:binding.runtimeEpoch,session:binding.session,pairGeneration:binding.pairGeneration,pairNonce:binding.pairNonce});
  let active=true,inFlight=null,tickAuthoritySeq=0,skippedTicks=0;
  return{
    start(){if(!active)return null;if(inFlight){skippedTicks++;return null;}inFlight=Object.freeze({...current,tickAuthorityId:++tickAuthoritySeq});return inFlight;},
    finish(a){if(!active||!inFlight||!a||a.tickAuthorityId!==inFlight.tickAuthorityId||!sameAuthority(a,inFlight)||!sameAuthority(a,current))return false;inFlight=null;return true;},
    revoke(){active=false;inFlight=null;},
    status(){return{active,inFlight:!!inFlight,queueDepth:0,skippedTicks,...current};}
  };
}
function classifyPlayerLocalIdentity(presenceByte,selfIndex,expectedSelfIndex){
  if(!Number.isInteger(presenceByte)||presenceByte<0||presenceByte>255||!Number.isInteger(selfIndex)||selfIndex<0||selfIndex>0xffff||!Number.isInteger(expectedSelfIndex)){
    return{state:'UNKNOWN',applicable:false,ok:false,reason:'malformed-player-local-identity'};
  }
  if(presenceByte!==0){
    if(selfIndex===expectedSelfIndex)return{state:'ACTIVE',applicable:true,ok:true,reason:'active-exact-self-index'};
    return{state:'UNKNOWN',applicable:true,ok:false,reason:'active-self-index-mismatch'};
  }
  if(selfIndex===0)return{state:'INACTIVE',applicable:false,ok:true,reason:'inactive-zeroed-self-index'};
  if(selfIndex===expectedSelfIndex)return{state:'INACTIVE',applicable:false,ok:true,reason:'inactive-retained-exact-self-index'};
  return{state:'UNKNOWN',applicable:false,ok:false,reason:'inactive-contradictory-self-index'};
}
function evaluatePlayerLocalIdentities(readU8,readU16){
  const players=PLAYER_LOCAL_IDENTITY.map(spec=>{
    const presenceByte=readU8(spec.base),selfIndex=readU16(spec.base+0x7C),classification=classifyPlayerLocalIdentity(presenceByte,selfIndex,spec.expectedSelfIndex);
    return{name:spec.name,base:spec.base,presenceByte,selfIndex,expectedSelfIndex:spec.expectedSelfIndex,...classification};
  });
  const bad=players.filter(p=>!p.ok);
  return{ok:bad.length===0,players,selfIndexes:players.map(p=>p.selfIndex),activePlayers:players.filter(p=>p.state==='ACTIVE').map(p=>p.name),inactivePlayers:players.filter(p=>p.state==='INACTIVE').map(p=>p.name),badPlayers:bad.map(p=>p.name)};
}
async function verifySelectedIdentity(scope,mod,binding){
  if(!moduleGood(mod)||!validBinding(binding))return{ok:false,reason:'module/binding mismatch',...SAFETY};
  if(!scope.crypto?.subtle?.digest)return{ok:false,reason:'Web Crypto SHA-256 unavailable',...SAFETY};
  const M=mod.HEAPU8,base=binding.launcherLocator.heapBase,swap=!!binding.launcherLocator.swap16;
  if(base<0||base+LOGICAL_BYTES>M.length)return{ok:false,reason:'launcher-selected ROM locator is outside current heap',...SAFETY};
  const logical=new Uint8Array(LOGICAL_BYTES);
  for(let i=0;i<LOGICAL_BYTES;i++)logical[i]=M[base+(swap?(i^1):i)]>>>0;
  const digest=await scope.crypto.subtle.digest('SHA-256',logical);
  const sha256=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(sha256!==GOLDEN_SHA)return{ok:false,reason:'detector-local selected ROM SHA-256 mismatch',sha256,expectedSha256:GOLDEN_SHA,...SAFETY};
  const R=mod.HEAPU32[0x2e39e4>>>2]>>>0;
  if(!R||R+0x10000>M.length)return{ok:false,reason:'CPS RAM window unavailable',sha256,...SAFETY};
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
  const U16=a=>((B(a)<<8)|B(a+1))>>>0;
  const localIdentity=evaluatePlayerLocalIdentities(B,U16);
  if(!localIdentity.ok){
    const bad=localIdentity.players.filter(p=>!p.ok).map(p=>`${p.name}:${p.state}:${p.reason}:present=${p.presenceByte}:self=${p.selfIndex}:expected=${p.expectedSelfIndex}`).join(', ');
    return{ok:false,reason:'P1/P2/P3 local identity contradictory: '+bad,sha256,selfIndexes:localIdentity.selfIndexes,playerLifecycle:localIdentity.players,...SAFETY};
  }
  return{ok:true,reason:'detector-local exact SHA-256 plus lifecycle-aware strict local identity',sha256,expectedSha256:GOLDEN_SHA,locator:{heapBase:base,swap16:swap},selfIndexes:localIdentity.selfIndexes,playerLifecycle:localIdentity.players,activePlayers:localIdentity.activePlayers,inactivePlayers:localIdentity.inactivePlayers,localIdentitySemantics:'active-exact/inactive-zeroed-or-retained-exact/unknown-fail-closed-v1',...SAFETY};
}
function stableWarningsHash(warnings){return JSON.stringify((warnings||[]).map(w=>[w.ruleId,w.slot,w.target7E,w.sourceSide,w.threatSide,w.attack,w.publication,w.evidence]));}
function markerTargetHash(markers,projectionOk){return (projectionOk?'ok|':'invalid|')+JSON.stringify((markers||[]).map(m=>[m.slot,m.target7E,m.target]));}

async function install(scope,binding){
  if(!validBinding(binding))throw new Error('正式 field adapter 绑定无效');
  const previous=scope.__WOF_ALPHA_REAL_TRANSPORT;
  if(previous&&typeof previous.stop==='function'&&previous.stop('field-reinstall')!==true)throw new Error('旧 observer 未安全停止');
  const core=scope.WOFAlphaCore,labelApi=scope.WOFAlphaEnemyTargetLabels,playerHeadApi=scope.WOFAlphaPlayerHeadWarning;
  if(core?.VERSION!==CORE_VERSION||core?.SCHEMA!==SCHEMA)throw new Error('package-selected Alpha core 未预载或身份不匹配');
  if(labelApi?.VERSION!==LABELS_VERSION)throw new Error('package-selected enemy label module 未预载或身份不匹配');
  if(playerHeadApi?.VERSION!==PLAYER_HEAD_VERSION)throw new Error('package-selected player warning module 未预载或身份不匹配');
  const mod=await findModule(scope);if(!mod)throw new Error('WASM 模块未找到');
  const identity=await verifySelectedIdentity(scope,mod,binding);if(!identity.ok)throw new Error('检测器本地 World 921031 身份校验失败：'+identity.reason);
  const profiles=scope.__WOF_ALPHA_FIELD_PROFILES||{};
  const enemyValid=labelApi.validateProofProfile?.(profiles.enemy||null);
  const projectionProfile=enemyValid?.ok?Object.freeze({...profiles.enemy}):null;
  const playerValid=playerHeadApi.validateProofProfile?.(profiles.player||null);
  const playerProjectionProfile=playerValid?.ok?Object.freeze({...profiles.player}):null;
  const markerSetupError=projectionProfile?null:(enemyValid?.reason||'ENEMY_HEAD_PROJECTION_UNPROVED');
  const playerProjectionError=playerProjectionProfile?null:(playerValid?.reason||'PLAYER_HEAD_PROJECTION_UNPROVED');

  const gate=createTickAuthorityGate(binding),M=mod.HEAPU8,R=mod.HEAPU32[0x2e39e4>>>2]>>>0;
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
  const U16=a=>((B(a)<<8)|B(a+1))>>>0;
  const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
  const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
  const F16=a=>S32(a)/65536;
  const X=a=>Math.round(F16(a+4));
  const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC};
  const PLAYER_BASES=Object.freeze({P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC});
  function snap(i){
    const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)return null;
    const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(!frameEnd&&!next)return null;
    const target7E=U16(a+0x7E),pb=PBASE[target7E],enemyX=X(a),targetX=pb?X(pb):null;
    return{slot:i,type,target7E,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd,next,value30:U32(a+0x30),timer34:U16(a+0x34),payload6C:U16(a+0x6C),enemyX,targetX,enemyWorldX:F16(a+0x04),enemyY:F16(a+0x08),enemyZ:F16(a+0x0C)};
  }
  function markerSnapshot(rows,sampleAt){
    if(!projectionProfile)return null;
    try{
      const cameraRaw=U16(projectionProfile.cameraAddress),cameraX=cameraRaw*projectionProfile.cameraSign*projectionProfile.cameraScale;
      if(!Number.isFinite(cameraX))throw new Error('camera sample non-finite');
      const projection={...projectionProfile,epoch:binding.runtimeEpoch,sampleAt,confidence:1,cameraRaw,cameraX},markers=[];
      for(const s of rows){
        const target=core.TARGETS[s.target7E]||null;
        if(!target||![s.enemyWorldX,s.enemyY,s.enemyZ].every(Number.isFinite)||!Number.isFinite(projectionProfile.enemyHeadOffsetsByType?.[String(s.type)]))continue;
        markers.push({slot:s.slot,sourceId:'enemy-slot-'+s.slot,type:s.type,target7E:s.target7E,target,enemyX:s.enemyWorldX,enemyY:s.enemyY,enemyZ:s.enemyZ,sampleAt,confidence:1,epoch:binding.runtimeEpoch,projectionEpoch:binding.runtimeEpoch});
      }
      return{projection,markers,projectionOk:true,error:null};
    }catch(error){return{projection:null,markers:[],projectionOk:false,error:String(error?.message||error)};}
  }
  function playerSpatialSnapshot(sampleAt){
    const players={};
    for(const [name,base] of Object.entries(PLAYER_BASES)){
      const present=!!B(base);
      players[name]=present?{present:true,x:F16(base+0x04),y:F16(base+0x08),z:F16(base+0x0C),sampleAt,confidence:1,epoch:binding.runtimeEpoch,projectionEpoch:binding.runtimeEpoch}:{present:false,sampleAt,confidence:1,epoch:binding.runtimeEpoch,projectionEpoch:binding.runtimeEpoch};
    }
    let projection=null,error=playerProjectionError;
    if(playerProjectionProfile){
      try{const cameraRaw=U16(playerProjectionProfile.cameraAddress),built=playerHeadApi.buildProjectionSnapshot(playerProjectionProfile,{cameraRaw,epoch:binding.runtimeEpoch,sampleAt});projection=built?.ok?built.projection:null;error=built?.ok?null:(built?.reason||'PLAYER_HEAD_PROJECTION_BUILD_FAILED');}catch(e){error=String(e?.message||e);}
    }
    return{players,projection,error};
  }

  const bc=new scope.BroadcastChannel(binding.channel),engine=core.createEngine();
  let running=true,timer=0,polls=0,lastError=null,lastHash=null,lastPublishedAt=null,seq=0,markerSeq=0,lastMarkerTargetHash=null,lastMarkerPublishedAt=null,lastMarkerError=markerSetupError,playerSpatialSeq=0,lastPlayerSpatialPublishedAt=null,lastPlayerSpatialError=playerProjectionError;
  const nowMono=()=>Number(scope.performance?.now?.()||Date.now());
  const envelope=(kind,payload={})=>({schema:SCHEMA,kind,release:RELEASE,coreVersion:CORE_VERSION,transportVersion:TRANSPORT,session:binding.session,pairGeneration:binding.pairGeneration,pairNonce:binding.pairNonce,runtimeEpoch:binding.runtimeEpoch,identitySignature:IDENTITY_SIGNATURE,sentAt:Date.now(),...SAFETY,...payload});
  const postDiag=reason=>{try{bc.postMessage(envelope('diag',{status:'DISABLED',code:'runtime-exception',reason:String(reason||'检测器已禁用')}));}catch(_){}};
  function beginTick(){
    if(!running)return;const authority=gate.start();if(!authority)return;const sampledAt=nowMono(),sampleAtEpoch=Date.now();let rows=[],playerSpatial=null;
    try{for(let i=0;i<SLOTS;i++){const s=snap(i);if(s)rows.push(s);}playerSpatial=playerSpatialSnapshot(sampleAtEpoch);}catch(error){if(gate.finish(authority)){lastError=String(error?.message||error);running=false;postDiag('只读快照失败：'+lastError);}return;}
    Promise.resolve().then(()=>engine.step(rows,sampledAt)).then(state=>{
      if(!gate.finish(authority))return;polls++;
      const warnings=Array.isArray(state?.warnings)?state.warnings:[],hash=stableWarningsHash(warnings),changed=hash!==lastHash,heartbeat=lastPublishedAt===null||sampledAt-lastPublishedAt>=250,statePublished=changed||heartbeat;
      if(statePublished){seq++;bc.postMessage(envelope('state',{seq,warnings,sampleAt:sampleAtEpoch}));lastHash=hash;lastPublishedAt=sampledAt;}
      const spatialHeartbeat=lastPlayerSpatialPublishedAt===null||sampledAt-lastPlayerSpatialPublishedAt>=PLAYER_SPATIAL_PUBLISH_MS;
      if(playerSpatial&&(statePublished||(warnings.length>0&&spatialHeartbeat))){playerSpatialSeq++;lastPlayerSpatialError=playerSpatial.error;bc.postMessage(envelope('player-head-spatial',{playerSpatialSeq,sampleAt:sampleAtEpoch,players:playerSpatial.players,projection:playerSpatial.projection}));lastPlayerSpatialPublishedAt=sampledAt;}
      const markerState=markerSnapshot(rows,sampleAtEpoch);
      if(markerState){lastMarkerError=markerState.error;const targetHash=markerTargetHash(markerState.markers,markerState.projectionOk),changedTarget=targetHash!==lastMarkerTargetHash,followHeartbeat=lastMarkerPublishedAt===null||sampledAt-lastMarkerPublishedAt>=50;if(changedTarget||followHeartbeat){markerSeq++;bc.postMessage(envelope('enemy-target-markers',{markerSeq,markers:markerState.markers,projection:markerState.projection}));lastMarkerTargetHash=targetHash;lastMarkerPublishedAt=sampledAt;}}
    }).catch(error=>{if(!gate.finish(authority))return;lastError=String(error?.message||error);running=false;engine.reset();postDiag('检测器运行异常：'+lastError);});
  }
  timer=setInterval(beginTick,10);beginTick();
  const runtime={version:VERSION,release:RELEASE,running:true,identitySignature:IDENTITY_SIGNATURE,identity,...SAFETY,
    stop(){if(!running&&gate.status().active===false)return true;running=false;runtime.running=false;try{clearInterval(timer);}catch(_){}gate.revoke();try{engine.reset();}catch(_){}try{bc.close();}catch(_){}return true;},
    status(){return{version:VERSION,release:RELEASE,running:running&&gate.status().active,identitySignature:IDENTITY_SIGNATURE,identity,...SAFETY,polls,lastError,playerHeadWarning:{moduleReady:true,projectionReady:!!playerProjectionProfile,proofId:playerProjectionProfile?.proofId??null,playerSpatialSeq,lastError:lastPlayerSpatialError,holdMs:0,smoothing:false,maxPublishHz:1000/PLAYER_SPATIAL_PUBLISH_MS,maxSpatialAgeMs:playerHeadApi.MAX_PLAYER_AGE_MS??80},enemyTargetLabels:{moduleReady:true,projectionReady:!!projectionProfile,proofId:projectionProfile?.proofId??null,markerSeq,lastError:lastMarkerError,holdMs:0,smoothing:false,maxPublishHz:20},...gate.status()};}};
  scope.__WOF_ALPHA_REAL_TRANSPORT=runtime;return runtime.status();
}
return{VERSION,RELEASE,SCHEMA,TRANSPORT,GOLDEN_SHA,IDENTITY_SIGNATURE,SAFETY,PLAYER_LOCAL_IDENTITY,validBinding,classifyPlayerLocalIdentity,evaluatePlayerLocalIdentities,verifySelectedIdentity,createTickAuthorityGate,install};
});
