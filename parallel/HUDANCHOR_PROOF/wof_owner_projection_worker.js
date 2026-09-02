(()=>{
'use strict';
const VERSION='wof-owner-projection-proof-v1',CHANNEL='wof-owner-projection-proof-v1',G=globalThis,SAMPLE_TARGET=80;
const READY_STABLE_SAMPLES=20,AMBIGUOUS_ACTIVE_SAMPLE_LIMIT=1200,EVENT_LIMIT=64;
try{G.WOFOWNERPROJECTION?.stop?.();}catch(_){}
const mod=G._0x515056,M=mod?.HEAPU8,R=mod?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!M||!R)throw new Error('CPS RAM base unavailable');
const PB={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC},ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0,U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0,S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;},W=v=>v/65536;
const player=n=>{const a=PB[n];return a&&B(a)?{name:n,x:W(S32(a+4)),y:W(S32(a+8)),z:W(S32(a+12))}:null;};
function enemies(){const out=[];for(let i=0;i<SLOTS;i++){const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)continue;const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(!frameEnd&&!next)continue;const target7E=U16(a+0x7E);if(![0,4,8].includes(target7E))continue;out.push({slot:i,type,target7E,x:W(S32(a+4)),y:W(S32(a+8)),z:W(S32(a+12))});}return out;}
const START=0,END=0xBE00,STEP=2,N=(END-START)/STEP,last=new Uint16Array(N),minv=new Uint16Array(N),maxv=new Uint16Array(N),changes=new Uint32Array(N),valid=new Uint32Array(N),strong=new Uint32Array(N),follow=new Uint32Array(N),smooth=new Uint32Array(N);minv.fill(0xffff);
let samples=0,activeTicks=0,inactiveTicks=0,prevPX=null,running=true,timer=null,locked=null,started=Date.now(),lastSentAt=0,lastUsableAt=0,pausedReason='WAITING_FOR_ACTIVE_P1',sequence=0;
let candidateGeneration=0,candidateStability=null,readyAuthority=null,lockRejectReason=null,lockRequestSequence=0;
const sessionId='camera-session-'+started.toString(36)+'-'+Math.floor(Math.random()*0x100000000).toString(36),events=[];
const bc=new BroadcastChannel(CHANNEL),round=(v,n=3)=>v==null?null:Number.isFinite(+v)?+(+v).toFixed(n):null;
function idx(a){const v=typeof a==='string'?parseInt(a,16):+a;return Number.isFinite(v)&&v>=0xFF0000&&v<0xFFBE00&&!((v-0xFF0000)&1)?(v-0xFF0000)/2:null;}
function event(kind,payload={}){const e={eventId:sessionId+':'+kind+':'+(events.length?events[events.length-1].ordinal+1:1),ordinal:events.length?events[events.length-1].ordinal+1:1,kind,at:Date.now(),sequence,samples,...payload};events.push(e);if(events.length>EVENT_LIMIT)events.shift();return e;}
function rows(limit=8){const p=player('P1');if(!p)return[];const out=[];for(let i=0,off=START;i<N;i++,off+=STEP){const ch=changes[i],rng=maxv[i]-minv[i];if(samples<10||rng<4||valid[i]<samples*.55)continue;const vr=valid[i]/samples,sr=strong[i]/samples,fr=ch?follow[i]/ch:0,sm=samples>1?smooth[i]/(samples-1):0,score=vr*4+sr*3+Math.min(1,rng/96)*1.5+Math.min(1,ch/20)*1.2+fr*1.5+sm*.3;out.push({address:'0x'+(0xFF0000+off).toString(16).toUpperCase(),read:'u16be',value:last[i],screenX:round(p.x-last[i],2),range:rng,changes:ch,valid:round(vr),strong:round(sr),follow:round(fr),score:round(score)});}out.sort((a,b)=>b.score-a.score||a.address.localeCompare(b.address));return out.slice(0,limit);}
function rawQuality(r){
  const a=r[0],b=r[1],gap=a&&b?a.score-b.score:null;
  if(pausedReason)return{ok:false,samples,targetSamples:SAMPLE_TARGET,remainingSamples:Math.max(0,SAMPLE_TARGET-samples),topAddress:a?.address||null,topScore:a?.score??null,scoreGap:round(gap),reason:pausedReason,conditioning:'PAUSED_PLAYER_INACTIVE',continuable:true};
  const ok=!!a&&samples>=SAMPLE_TARGET&&a.range>=8&&a.changes>=5&&a.valid>=.70&&a.strong>=.45&&a.follow>=.55&&(gap==null||gap>=.10);
  let reason=ok?null:!a?'NO_CANDIDATE':samples<SAMPLE_TARGET?'NEED_MORE_SAMPLES':a.range<8?'CAMERA_RANGE_TOO_SMALL':a.changes<5?'CAMERA_TOO_STATIC':a.valid<.70?'SCREEN_X_IMPLAUSIBLE':a.strong<.45?'SCREEN_X_WEAK':a.follow<.55?'CAMERA_FOLLOW_WEAK':'CANDIDATE_AMBIGUOUS';
  if(reason==='CANDIDATE_AMBIGUOUS'&&activeTicks>=AMBIGUOUS_ACTIVE_SAMPLE_LIMIT)reason='CANDIDATE_AMBIGUOUS_LIMIT_REACHED';
  const conditioning=ok?'INSTANT_CANDIDATE_OK':reason==='NEED_MORE_SAMPLES'?'UNDER_TARGET':['CAMERA_RANGE_TOO_SMALL','CAMERA_TOO_STATIC'].includes(reason)?'LOW_CONTRAST_OR_DUPLICATE':reason==='CANDIDATE_AMBIGUOUS'?'AMBIGUOUS_CANDIDATES':reason==='CANDIDATE_AMBIGUOUS_LIMIT_REACHED'?'AMBIGUOUS_BOUNDED_STOP':reason==='CAMERA_FOLLOW_WEAK'?'WEAK_OR_CONFOUNDED_MOTION':'REUSABLE_PARTIAL';
  return{ok,samples,targetSamples:SAMPLE_TARGET,remainingSamples:Math.max(0,SAMPLE_TARGET-samples),topAddress:a?.address||null,topScore:a?.score??null,scoreGap:round(gap),reason,conditioning,continuable:reason!=='CANDIDATE_AMBIGUOUS_LIMIT_REACHED'};
}
function beginCandidate(a,q){candidateGeneration++;candidateStability={generation:candidateGeneration,address:a.address,firstSample:samples,lastSample:samples,qualifiedSamples:1,minScoreGap:q.scoreGap,minRange:a.range,minChanges:a.changes,minValid:a.valid,minStrong:a.strong,minFollow:a.follow,lastReason:null};event('CANDIDATE_GENERATION',{candidateGeneration,address:a.address,reason:'QUALIFIED_STREAK_STARTED'});}
function updateCandidate(r,q){
  if(readyAuthority)return;
  const a=r[0];
  if(!q.ok||!a){if(candidateStability){event('CANDIDATE_STREAK_RESET',{candidateGeneration:candidateStability.generation,address:candidateStability.address,reason:q.reason||'NOT_QUALIFIED'});candidateStability=null;}return;}
  if(!candidateStability||candidateStability.address!==a.address||candidateStability.lastSample!==samples-1){if(candidateStability)event('CANDIDATE_STREAK_RESET',{candidateGeneration:candidateStability.generation,address:candidateStability.address,reason:'TOP_CANDIDATE_CHANGED'});beginCandidate(a,q);}else{
    const c=candidateStability;c.lastSample=samples;c.qualifiedSamples++;c.minScoreGap=c.minScoreGap==null?q.scoreGap:Math.min(c.minScoreGap,q.scoreGap??c.minScoreGap);c.minRange=Math.min(c.minRange,a.range);c.minChanges=Math.min(c.minChanges,a.changes);c.minValid=Math.min(c.minValid,a.valid);c.minStrong=Math.min(c.minStrong,a.strong);c.minFollow=Math.min(c.minFollow,a.follow);
  }
  if(candidateStability&&candidateStability.qualifiedSamples>=READY_STABLE_SAMPLES){
    const c=candidateStability;const authorityGeneration=c.generation;
    readyAuthority={state:'READY',authorityId:sessionId+':ready:'+authorityGeneration+':'+c.address,authorityGeneration,candidateGeneration:c.generation,address:c.address,read:'u16be',createdAt:Date.now(),createdSequence:sequence+1,sampleStart:c.firstSample,sampleEnd:c.lastSample,stableSamples:c.qualifiedSamples,proofWindow:{minScoreGap:round(c.minScoreGap),minRange:c.minRange,minChanges:c.minChanges,minValid:round(c.minValid),minStrong:round(c.minStrong),minFollow:round(c.minFollow)},latchPolicy:'LATCHED_VERIFIED_CANDIDATE_UNTIL_RUNTIME_REPLACEMENT'};
    event('READY_CREATED',{authorityId:readyAuthority.authorityId,authorityGeneration,address:readyAuthority.address,candidateGeneration:c.generation,sampleStart:c.firstSample,sampleEnd:c.lastSample,stableSamples:c.qualifiedSamples});
  }
}
function authoritativeQuality(raw){
  if(!readyAuthority){const stable=candidateStability;return{...raw,ok:false,ready:false,clickReady:false,conditioning:raw.ok?'STABILIZING_READY_WINDOW':raw.conditioning,reason:raw.ok?'READY_STABILITY_WINDOW':raw.reason,continuable:raw.continuable,stableSamples:stable?.qualifiedSamples||0,requiredStableSamples:READY_STABLE_SAMPLES,candidateGeneration:stable?.generation||candidateGeneration,authorityGeneration:null,authorityId:null,authorityAddress:null};}
  const p=player('P1');return{ok:true,ready:true,clickReady:!!p,samples,targetSamples:SAMPLE_TARGET,remainingSamples:0,topAddress:readyAuthority.address,topScore:null,scoreGap:readyAuthority.proofWindow.minScoreGap,reason:p?'CAMERA_READY_LATCHED':'WAITING_FOR_ACTIVE_P1',conditioning:p?'READY_LATCHED':'READY_LATCHED_WAITING_FOR_ACTIVE_P1',continuable:false,stableSamples:readyAuthority.stableSamples,requiredStableSamples:READY_STABLE_SAMPLES,candidateGeneration:readyAuthority.candidateGeneration,authorityGeneration:readyAuthority.authorityGeneration,authorityId:readyAuthority.authorityId,authorityAddress:readyAuthority.address,proofSampleStart:readyAuthority.sampleStart,proofSampleEnd:readyAuthority.sampleEnd,latchPolicy:readyAuthority.latchPolicy};
}
function guidance(q){
  const common='已保留当前有效样本；不要重启、不要重新打包、不要重新执行菜单 6。';
  if(q.ready&&q.clickReady)return{actionZh:'Camera 稳定 authority 已锁定。现在只点击一次 P1 头顶上方希望警告中心出现的位置。',nextCommandZh:`下一步：消费 Camera authority #${q.authorityGeneration}；无需继续卷屏或运行新命令。`};
  if(q.ready&&!q.clickReady)return{actionZh:'Camera 稳定 authority 已锁定，但 P1 当前不在活动场景。回到可控制 P1 的房间后再点击；不要重新校准。',nextCommandZh:'下一步：让 P1 回到活动场景，保持当前窗口打开。'};
  if(q.reason==='WAITING_FOR_ACTIVE_P1')return{actionZh:'P1 当前不在活动场景。进入/回到可控制 P1 的房间后继续当前校准。'+common,nextCommandZh:'下一步：让 P1 出现在场景中并保持当前真人验证窗口打开。'};
  if(q.reason==='READY_STABILITY_WINDOW')return{actionZh:`瞬时候选已满足阈值，但尚未形成稳定 authority（${q.stableSamples}/${q.requiredStableSamples}）。继续同一段正常左右卷屏，不要点击。`+common,nextCommandZh:'下一步：继续当前窗口，直到稳定 authority 明确显示 READY。'};
  if(q.reason==='NEED_MORE_SAMPLES')return{actionZh:`继续正常左右移动并让背景明显滚动；有效样本 ${q.samples}/${q.targetSamples}，还需 ${q.remainingSamples}。`+common,nextCommandZh:'下一步：继续当前游戏中的左右移动；Camera READY 后按画面提示点击一次 P1 头顶。'};
  if(q.reason==='CAMERA_RANGE_TOO_SMALL')return{actionZh:'样本数量已够，但 camera 取值跨度太小。继续向左右更远处移动，让背景产生明显卷屏；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口做更大幅度左右卷屏，不要重新开始校准。'};
  if(q.reason==='CAMERA_TOO_STATIC')return{actionZh:'样本数量已够，但重复/静止样本过多。持续左右走动并经过会卷屏的区域；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口制造连续 camera 变化。'};
  if(q.reason==='CAMERA_FOLLOW_WEAK')return{actionZh:'camera 候选与 P1 运动相关性不足。只做清晰左右移动，暂时避免复杂纵深/跳跃；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口做单一左右卷屏动作。'};
  if(q.reason==='CANDIDATE_AMBIGUOUS')return{actionZh:'出现多个接近的 camera 候选。继续跨更长距离左右卷屏以拉开候选；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口做更长距离左右卷屏。'};
  if(q.reason==='CANDIDATE_AMBIGUOUS_LIMIT_REACHED')return{actionZh:'多个 camera 候选在 bounded 采样上限内仍无法唯一化。停止继续无限卷屏，不要点击 P1；本次证据会保留并自动进入结果包。',nextCommandZh:'下一步：结束本次真人校准并保留自动 evidence/ZIP；不要猜 camera 常量。'};
  if(q.reason==='SCREEN_X_IMPLAUSIBLE'||q.reason==='SCREEN_X_WEAK')return{actionZh:'当前样本对屏幕 X 的约束不足。让 P1 在可见区域内左右移动并触发卷屏；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口保持 P1 可见并左右卷屏。'};
  return{actionZh:'继续当前校准并保持 P1 可见；现有样本不会丢失。',nextCommandZh:'下一步：继续当前真人验证窗口，不要重新运行工具。'};
}
function readyCam(){if(!readyAuthority)return null;const i=idx(readyAuthority.address);return i==null?null:{address:readyAuthority.address,read:'u16be',value:last[i],authorityId:readyAuthority.authorityId,authorityGeneration:readyAuthority.authorityGeneration,candidateGeneration:readyAuthority.candidateGeneration,createdSequence:readyAuthority.createdSequence};}
function lockedCam(){if(!locked)return null;const i=idx(locked.address);return i==null?null:{address:locked.address,read:'u16be',value:last[i],authorityId:locked.authorityId,authorityGeneration:locked.authorityGeneration,lockedAt:locked.lockedAt,lockRequestSequence:locked.lockRequestSequence};}
function snap(){const top=rows(),raw=rawQuality(top),q=authoritativeQuality(raw);return{schema:CHANNEL,kind:'state',version:VERSION,workerSessionId:sessionId,sequence,snapshotId:sessionId+':'+sequence,sentAt:Date.now(),samples,seconds:round((Date.now()-started)/1000,1),players:{P1:player('P1'),P2:player('P2'),P3:player('P3')},enemies:enemies(),cameraTop:top,cameraRawQuality:raw,cameraQuality:q,cameraAuthority:readyAuthority?{...readyAuthority}:null,candidateStability:candidateStability?{...candidateStability}:null,readyCamera:readyCam(),guidance:guidance(q),sampling:{activeTicks,inactiveTicks,lastUsableAt,pausedReason,retainedSamples:samples,continuable:!readyAuthority&&raw.continuable,ambiguousActiveSampleLimit:AMBIGUOUS_ACTIVE_SAMPLE_LIMIT},lockedCamera:lockedCam(),lockRejectReason,authorityTimeline:events.slice(),safety:{readOnly:true,ramWrites:0,inputInjection:false}};}
function send(){sequence++;const m=snap();bc.postMessage(m);lastSentAt=m.sentAt;return m;}
function tick(){
  if(!running)return;
  const p=player('P1');
  if(!p){inactiveTicks++;pausedReason='WAITING_FOR_ACTIVE_P1';prevPX=null;send();return;}
  activeTicks++;pausedReason=null;lastUsableAt=Date.now();
  const dpx=prevPX==null?0:p.x-prevPX;
  for(let i=0,off=START;i<N;i++,off+=STEP){const v=U16(0xFF0000+off),old=last[i];if(v<minv[i])minv[i]=v;if(v>maxv[i])maxv[i]=v;if(samples&&v!==old){const dv=v-old;changes[i]++;if(Math.abs(dv)<=8)smooth[i]++;if(Math.abs(dpx)>=.2&&Math.sign(dv)===Math.sign(dpx))follow[i]++;}const sx=p.x-v;if(sx>=-48&&sx<=432)valid[i]++;if(sx>=8&&sx<=376)strong[i]++;last[i]=v;}
  samples++;prevPX=p.x;const top=rows(),raw=rawQuality(top);updateCandidate(top,raw);send();
}
function acceptLock(m){
  lockRequestSequence++;
  const expected=readyAuthority,reason=!expected?'NO_READY_AUTHORITY':m.authorityId!==expected.authorityId?'AUTHORITY_ID_MISMATCH':Number(m.authorityGeneration)!==expected.authorityGeneration?'AUTHORITY_GENERATION_MISMATCH':String(m.address||'').toUpperCase()!==expected.address.toUpperCase()?'AUTHORITY_ADDRESS_MISMATCH':null;
  if(reason){lockRejectReason={reason,at:Date.now(),requestSequence:lockRequestSequence,requestedAuthorityId:m.authorityId||null,requestedAuthorityGeneration:m.authorityGeneration??null,requestedAddress:m.address||null};event('LOCK_REJECTED',lockRejectReason);send();return;}
  locked={address:expected.address,authorityId:expected.authorityId,authorityGeneration:expected.authorityGeneration,lockedAt:Date.now(),lockRequestSequence};lockRejectReason=null;event('CAMERA_LOCKED',{authorityId:expected.authorityId,authorityGeneration:expected.authorityGeneration,address:expected.address,lockRequestSequence});send();
}
bc.onmessage=e=>{const m=e.data;if(m?.schema!==CHANNEL)return;if(m.kind==='lock-camera')acceptLock(m);else if(m.kind==='unlock-camera'){if(locked)event('CAMERA_UNLOCKED',{authorityId:locked.authorityId,authorityGeneration:locked.authorityGeneration,address:locked.address});locked=null;send();}else if(m.kind==='request-state')send();};
timer=setInterval(tick,100);tick();
G.WOFOWNERPROJECTION={version:VERSION,mode:'worker',result:snap,status(){const s=snap();return{running,samples,lastSentAt,workerSessionId:sessionId,sequence,locked:s.lockedCamera,sampling:s.sampling,cameraQuality:s.cameraQuality,cameraRawQuality:s.cameraRawQuality,cameraAuthority:s.cameraAuthority,candidateStability:s.candidateStability,readyCamera:s.readyCamera,guidance:s.guidance,authorityTimeline:s.authorityTimeline,lockRejectReason:s.lockRejectReason,safety:s.safety};},stop(){if(!running)return;running=false;if(readyAuthority){event('READY_REVOKED',{authorityId:readyAuthority.authorityId,authorityGeneration:readyAuthority.authorityGeneration,address:readyAuthority.address,reason:'WORKER_RUNTIME_STOP'});readyAuthority={...readyAuthority,state:'REVOKED',revokedAt:Date.now(),revokeReason:'WORKER_RUNTIME_STOP'};try{send();}catch(_){}}if(timer)clearInterval(timer);try{bc.close();}catch(_){}try{delete G.WOFOWNERPROJECTION;}catch(_){}}};
})();
