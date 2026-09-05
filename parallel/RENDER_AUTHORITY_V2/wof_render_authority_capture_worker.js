(()=>{
'use strict';
const G=globalThis;
const SCHEMA='wof-render-authority-capture-v2';
const WORLD_SHA='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const SAFETY={readOnly:true,ramWrites:0,inputInjection:false,overlayEnabled:false,guessedConstantsAccepted:false};
const DURATION_MS=30000,TICK_MS=250,MAX_EVENTS=96,MAX_REGIONS=24,REGION_BYTES=128,SCAN_BYTES=0x20000;
const MAX_TIMELINE=96,TIMELINE_REGIONS=8,TIMELINE_ENTRIES=16;
try{G.WOFRENDERAUTHV2?.stop?.('reinstall');}catch(_){}
const goodModule=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
const u16be=(M,p)=>((M[p]<<8)|M[p+1])>>>0;
const u16le=(M,p)=>(M[p]|(M[p+1]<<8))>>>0;
const hex=(M,p,n)=>{const e=Math.min(M.length,p+n);let s='';for(let i=p;i<e;i++)s+=M[i].toString(16).padStart(2,'0');return s;};
function moduleOf(){try{if(goodModule(G._0x515056))return {key:'_0x515056',mod:G._0x515056};}catch(_){}for(const k of Object.getOwnPropertyNames(G)){let v;try{v=G[k];}catch(_){continue;}if(goodModule(v))return {key:k,mod:v};}return null;}
function decodeEntries(M,p,swap,count=TIMELINE_ENTRIES){const rd=swap?u16le:u16be,rows=[];for(let i=0;i<count;i++){const q=p+i*8;if(q+7>=M.length)break;const x=rd(M,q),y=rd(M,q+2),tile=rd(M,q+4),attr=rd(M,q+6);rows.push({entryIndex:i,xWord:x,yWord:y,tileWord:tile,attrWord:attr,x9:x&0x1ff,y9:y&0x1ff,endMarker:(attr&0xff00)===0xff00});}return rows;}
function structuralScore(M,p,swap){const rows=decodeEntries(M,p,swap,8);let good=0,moving=0,nonzero=0,markers=0;for(const row of rows){if(row.x9<0x1a0&&row.y9<0x120)good++;if((row.xWord|row.yWord)!==0)moving++;if(row.tileWord!==0&&row.tileWord!==0xffff&&row.attrWord!==0xffff)nonzero++;if(row.endMarker)markers++;}return good*3+moving+nonzero+Math.min(2,markers);}
function regionRow(M,p,swap){return {heapOffset:p,byteOrder:swap?'LE16':'BE16',structuralScore:structuralScore(M,p,swap),rawHex:hex(M,p,REGION_BYTES),authority:'UNVERIFIED_CANDIDATE_ONLY'};}
function topStructuralRegions(M,start,end,limit=6){const top=[],s=Math.max(0,start&~1),e=Math.min(M.length-REGION_BYTES,end);for(let p=s;p<e;p+=8){for(const swap of [false,true]){const score=structuralScore(M,p,swap);if(score<31)continue;const row=regionRow(M,p,swap);top.push(row);top.sort((a,b)=>b.structuralScore-a.structuralScore||a.heapOffset-b.heapOffset);if(top.length>limit)top.length=limit;}}return top;}
function snapshotRegion(M,row){const swap=row.byteOrder==='LE16';return {heapOffset:row.heapOffset,byteOrder:row.byteOrder,structuralScore:structuralScore(M,row.heapOffset,swap),authority:'UNVERIFIED_CANDIDATE_ONLY',entries:decodeEntries(M,row.heapOffset,swap,TIMELINE_ENTRIES)};}
function surface(mod){const names=[];for(const k of Object.getOwnPropertyNames(mod)){let v;try{v=mod[k];}catch(_){continue;}const t=ArrayBuffer.isView(v)?`${v.constructor?.name||'TypedArray'}:${v.byteLength}`:typeof v;if(/cps|obj|sprite|gfx|render|video|frame|ram|mem/i.test(k)||typeof v==='number')names.push({name:k,type:t,value:typeof v==='number'&&Number.isFinite(v)?v:undefined});if(names.length>=256)break;}return names;}
function makeActors(M,R){if(!Number.isInteger(R)||R<=0||R+0x10000>M.length)return ()=>({players:[],enemies:[],ramBase:R||null});const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0,U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0,S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;},W=v=>v/65536;const PB=[['P1',0xFFBE1C],['P2',0xFFBEFC],['P3',0xFFBFDC]],ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,prev=new Map(),gen=new Map();const lifecycle=(key,sig,active)=>{const old=prev.get(key);if(active&&old!==sig)gen.set(key,(gen.get(key)||0)+1);prev.set(key,active?sig:null);return gen.get(key)||0;};return ()=>{const players=[];for(const [name,a] of PB){const active=!!B(a),sig=active?`${U16(a+0x20)}:${U32(a+0x12)}:${U32(a+0x2c)}`:'inactive',g=lifecycle(name,sig,active);if(active)players.push({name,generation:g,type:U16(a+0x20),x:W(S32(a+4)),y:W(S32(a+8)),z:W(S32(a+12))});}const enemies=[];for(let i=0;i<SLOTS;i++){const a=ENEMY+i*STRIDE,type=U16(a+0x20),frameEnd=U32(a+0x12),next=U32(a+0x2c),active=type<47&&!!(frameEnd||next),sig=active?`${type}:${frameEnd}:${next}`:'inactive',g=lifecycle('E'+i,sig,active);if(active)enemies.push({slot:i,generation:g,type,target7E:U16(a+0x7e),x:W(S32(a+4)),y:W(S32(a+8)),z:W(S32(a+12))});}return {players,enemies,ramBase:R};};}
let state=null,timer=null;
function stop(reason='stopped'){if(timer){clearInterval(timer);timer=null;}if(state&&!state.terminal){state.terminal=true;state.state='STOPPED';state.stopReason=reason;state.endedAt=Date.now();}return true;}
function start(binding){
  stop('restart');
  if(!binding||binding.worldSha256!==WORLD_SHA||typeof binding.runtimeEpoch!=='string'||binding.runtimeEpoch.length<16||typeof binding.rendererEpoch!=='string'||binding.rendererEpoch.length<16||typeof binding.authorityKey!=='string'||!binding.authorityKey)throw new Error('exact World/runtime/renderer authority binding invalid');
  const found=moduleOf();if(!found)throw new Error('exact Worker/WASM module unavailable');
  const M=found.mod.HEAPU8,R=found.mod.HEAPU32?.[0x2e39e4>>>2]>>>0,actors=makeActors(M,R),started=Date.now(),events=[],regions=new Map(),heapBytes=M.length,continuousActorFeed=binding.continuousActorFeed===true;
  state={schema:SCHEMA,state:'MEASURING',terminal:false,captureComplete:false,captureCompletedAt:null,continuousActorFeed,startedAt:started,endedAt:null,runtimeEpoch:binding.runtimeEpoch,rendererEpoch:binding.rendererEpoch,authorityKey:binding.authorityKey,worldSha256:binding.worldSha256,moduleKey:found.key,heapBytes,ramBase:R||null,moduleSurface:surface(found.mod),sampleCount:0,scanBytes:0,actorSamples:[],currentActors:{players:[],enemies:[],ramBase:R||null,sampleAt:started},candidateRegions:[],candidateTimeline:[],p1Lifecycle:{active:false,generation:0,type:null,x:null,y:null,z:null},rendererSourceQualification:'UNVERIFIED_CANDIDATE_ONLY',canonicalNativeContract:{width:384,height:224,accepted:false,reason:'exact renderer/object source not yet proven'},ownerActionZh:'正常玩；无需点头、点脚、人工校准或选择 Y/Y-Z/Y+Z。',measurementRequired:'exact runtime renderer/object table time-series plus screenshot verification',...SAFETY};
  const addEvent=(kind,payload={})=>{events.push({at:Date.now(),kind,...payload});if(events.length>MAX_EVENTS)events.shift();};addEvent('MEASUREMENT_STARTED',{durationMs:DURATION_MS,continuousActorFeed,rendererEpoch:binding.rendererEpoch});
  let tick=0;
  const sample=()=>{
    if(!state||state.terminal)return;
    if(state.runtimeEpoch!==binding.runtimeEpoch||state.rendererEpoch!==binding.rendererEpoch||state.authorityKey!==binding.authorityKey){stop('authority-generation-mismatch');return;}
    const now=Date.now(),a=actors(),p1=a.players.find(p=>p.name==='P1');state.currentActors={...a,sampleAt:now};state.p1Lifecycle=p1?{active:true,generation:p1.generation,type:p1.type,x:p1.x,y:p1.y,z:p1.z}:{active:false,generation:state.p1Lifecycle?.generation||0,type:null,x:null,y:null,z:null};state.sampleCount++;
    if(!state.captureComplete){
      if(state.actorSamples.length<80||state.sampleCount%4===0)state.actorSamples.push({at:now,...a});if(state.actorSamples.length>120)state.actorSamples.shift();
      const localStart=Math.max(0,Math.min(M.length-SCAN_BYTES,(R||0)-0x400000+((tick*SCAN_BYTES)%0x800000))),globalStart=Math.max(0,Math.floor(((tick%120)/120)*Math.max(0,M.length-SCAN_BYTES)));
      for(const base of [localStart,globalStart]){for(const row of topStructuralRegions(M,base,base+SCAN_BYTES)){const key=row.byteOrder+':'+row.heapOffset,prior=regions.get(key);if(!prior||prior.structuralScore<=row.structuralScore)regions.set(key,{...row,firstSeenAt:prior?.firstSeenAt||now,lastSeenAt:now});}}
      const ranked=[...regions.values()].sort((x,y)=>y.structuralScore-x.structuralScore||x.heapOffset-y.heapOffset).slice(0,MAX_REGIONS);regions.clear();for(const r of ranked)regions.set(r.byteOrder+':'+r.heapOffset,r);state.candidateRegions=ranked;state.scanBytes+=SCAN_BYTES*2;
      if(tick%2===0&&ranked.length){state.candidateTimeline.push({at:now,sequence:state.sampleCount,runtimeEpoch:state.runtimeEpoch,rendererEpoch:state.rendererEpoch,authorityKey:state.authorityKey,p1Lifecycle:{...state.p1Lifecycle},regions:ranked.slice(0,TIMELINE_REGIONS).map(r=>snapshotRegion(M,r))});if(state.candidateTimeline.length>MAX_TIMELINE)state.candidateTimeline.shift();}
      tick++;
      if(now-started>=DURATION_MS){
        state.captureComplete=true;state.captureCompletedAt=now;state.resultVerdict='BOUNDED_CAPTURE_READY_FOR_RENDER_AUTHORITY_ANALYSIS';addEvent('MEASUREMENT_COMPLETE',{samples:state.sampleCount,candidates:ranked.length,timelineFrames:state.candidateTimeline.length});
        if(continuousActorFeed){state.state='ANCHOR_STREAMING';}
        else{state.terminal=true;state.state='MEASUREMENT_COMPLETE';state.endedAt=now;state.events=events.slice();clearInterval(timer);timer=null;}
      }
    }
  };
  timer=setInterval(sample,TICK_MS);sample();return status();
}
function status(){if(!state)return {schema:SCHEMA,state:'IDLE',terminal:false,...SAFETY};return {schema:SCHEMA,state:state.state,terminal:state.terminal,captureComplete:state.captureComplete,captureCompletedAt:state.captureCompletedAt,continuousActorFeed:state.continuousActorFeed,startedAt:state.startedAt,endedAt:state.endedAt,runtimeEpoch:state.runtimeEpoch,rendererEpoch:state.rendererEpoch,authorityKey:state.authorityKey,worldSha256:state.worldSha256,moduleKey:state.moduleKey,heapBytes:state.heapBytes,ramBase:state.ramBase,sampleCount:state.sampleCount,scanBytes:state.scanBytes,candidateCount:state.candidateRegions.length,candidateTimelineFrames:state.candidateTimeline.length,p1Lifecycle:state.p1Lifecycle,actors:state.currentActors,rendererSourceQualification:state.rendererSourceQualification,canonicalNativeContract:state.canonicalNativeContract,ownerActionZh:state.ownerActionZh,measurementRequired:state.measurementRequired,...SAFETY};}
function result(){return state&&(state.captureComplete||state.terminal)?JSON.parse(JSON.stringify({...state,events:state.events||[]})):null;}
G.WOFRENDERAUTHV2={schema:SCHEMA,start,status,result,stop,_test:{u16be,u16le,decodeEntries,structuralScore,topStructuralRegions,snapshotRegion}};
})();