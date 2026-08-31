(async()=>{
'use strict';
const VERSION='wof-singleplayer-pause-probe-v2';
if(self.__WOF_SINGLEPLAYER_PAUSE_V2_RUNNING)throw new Error('pause probe v2 already running');
self.__WOF_SINGLEPLAYER_PAUSE_V2_RUNNING=true;
try{
  const MOD=_0x515056,M=MOD?.HEAPU8,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;
  if(!M||!R)throw new Error('CPS RAM unavailable; run in gstyphoon.js Worker console');
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
  const U16=a=>((B(a)<<8)|B(a+1))>>>0;
  const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
  const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
  const P1=0xFFBE1C,P2=0xFFBEFC,P3=0xFFBFDC,POOL=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const hashBytes=(ranges,step=1)=>{let h=2166136261>>>0;for(const [a,len] of ranges){for(let i=0;i<len;i+=step){h^=B(a+i);h=Math.imul(h,16777619)>>>0;}}return h>>>0;};
  const actorRanges=[[P1,STRIDE],[P2,STRIDE],[P3,STRIDE],...Array.from({length:SLOTS},(_,s)=>[POOL+s*STRIDE,STRIDE])];
  const actorHash=()=>hashBytes(actorRanges,1);
  const ramHash=()=>hashBytes([[0xFF0000,0x10000]],8);
  const activeEnemies=()=>{let n=0;for(let s=0;s<SLOTS;s++){const a=POOL+s*STRIDE,type=U16(a+0x20),x=S32(a+4),y=S32(a+8);if(type!==0||x!==0||y!==0)n++;}return n;};
  const snap=()=>({
    actor:actorHash(),ram:ramHash(),
    p1x:S32(P1+4),p1y:S32(P1+8),p1a:B(P1+0x2A),p1self:U16(P1+0x7C),
    p2self:U16(P2+0x7C),p3self:U16(P3+0x7C),activeEnemies:activeEnemies()
  });
  const INTERVAL=100,DURATION=16000;
  const samples=[];let start=performance.now(),last=start,saidPause=false,saidResume=false;
  console.log('=== SINGLEPLAYER PAUSE PROBE V2 START ===');
  console.log('0-4秒：保持1P正常战斗并主动移动；4-10秒：暂停；10-16秒：恢复并继续移动。不要开2P。');
  while(performance.now()-start<DURATION){
    await sleep(INTERVAL);
    const now=performance.now(),t=Math.round(now-start),dt=Math.round(now-last);last=now;
    if(!saidPause&&t>=4000){saidPause=true;console.log('>>> NOW PAUSE: 现在暂停，保持到约10秒');}
    if(!saidResume&&t>=10000){saidResume=true;console.log('>>> NOW RESUME: 现在解除暂停并继续移动');}
    samples.push({t,dt,...snap()});
  }
  const phaseOf=t=>t<4000?'baseline':t<10000?'pause':'resume';
  function phaseStats(name){
    const a=samples.filter(s=>phaseOf(s.t)===name);let actorChanges=0,ramChanges=0,p1PosChanges=0,maxGap=0;
    for(let i=1;i<a.length;i++){
      if(a[i].actor!==a[i-1].actor)actorChanges++;
      if(a[i].ram!==a[i-1].ram)ramChanges++;
      if(a[i].p1x!==a[i-1].p1x||a[i].p1y!==a[i-1].p1y)p1PosChanges++;
      if(a[i].dt>maxGap)maxGap=a[i].dt;
    }
    return{name,samples:a.length,actorChanges,ramChanges,p1PosChanges,maxGapMs:maxGap,first:a[0]||null,last:a[a.length-1]||null};
  }
  const baseline=phaseStats('baseline'),pause=phaseStats('pause'),resume=phaseStats('resume');
  const ids={p1:U16(P1+0x7C),p2:U16(P2+0x7C),p3:U16(P3+0x7C)};
  const mappingOk=ids.p1===0&&ids.p2===4&&ids.p3===8;
  const baselineActive=baseline.actorChanges>=2||baseline.p1PosChanges>=2||baseline.ramChanges>=2;
  const resumeActive=resume.actorChanges>=2||resume.p1PosChanges>=2||resume.ramChanges>=2;
  const workerSuspended=pause.maxGapMs>=800;
  let classification='UNCLASSIFIED';
  if(!mappingOk)classification='RAM_MAPPING_UNVERIFIED';
  else if(!baselineActive)classification='BASELINE_NOT_ACTIVE';
  else if(!resumeActive)classification='RESUME_NOT_ACTIVE';
  else if(workerSuspended)classification='WORKER_OR_SCHEDULER_SUSPENDED_DURING_PAUSE';
  else if(pause.actorChanges<=1&&pause.ramChanges<=1)classification='CPU_OR_GAME_RAM_FROZEN_WHILE_WORKER_ALIVE';
  else if(pause.actorChanges<=1&&pause.ramChanges>1)classification='GAME_LOGIC_PAUSE_ACTORS_FROZEN_GLOBAL_RAM_STILL_ALIVE';
  else classification='PAUSE_DID_NOT_FULLY_FREEZE_OR_TIMING_MISSED';
  const out={version:VERSION,readOnly:true,ramWrites:0,durationMs:DURATION,intervalMs:INTERVAL,classification,mappingOk,playerSelfIndex:ids,baselineActive,resumeActive,phaseStats:{baseline,pause,resume},note:'Valid pause classification requires active baseline and active resume. If either is false, do not infer pause semantics.'};
  self.__WOF_SINGLEPLAYER_PAUSE_PROBE_V2=out;
  console.log('=== SINGLEPLAYER PAUSE PROBE V2 VERDICT ===');console.table([{classification,mappingOk,baselineActive,resumeActive,baselineActorChanges:baseline.actorChanges,pauseActorChanges:pause.actorChanges,resumeActorChanges:resume.actorChanges,pauseRamChanges:pause.ramChanges,pauseMaxGapMs:pause.maxGapMs}]);
  console.log('=== SINGLEPLAYER PAUSE PROBE V2 JSON ===');console.log(JSON.stringify(out,null,2));
  return out;
}finally{self.__WOF_SINGLEPLAYER_PAUSE_V2_RUNNING=false;}
})().catch(e=>{console.error('WOF_SINGLEPLAYER_PAUSE_PROBE_V2_ERROR',e);throw e;});
