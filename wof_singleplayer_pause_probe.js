(async()=>{
'use strict';
const VERSION='wof-singleplayer-pause-probe-v1';
if(self.__WOF_SINGLEPLAYER_PAUSE_RUNNING)throw new Error('pause probe already running');
self.__WOF_SINGLEPLAYER_PAUSE_RUNNING=true;
try{
  const MOD=_0x515056,M=MOD?.HEAPU8,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;
  if(!M||!R)throw new Error('CPS RAM unavailable; run in gstyphoon.js Worker console');
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
  const P1=0xFFBE1C,P2=0xFFBEFC,P3=0xFFBFDC,POOL=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const hashRange=(a,len,step=1)=>{let h=2166136261>>>0;for(let i=0;i<len;i+=step){h^=B(a+i);h=Math.imul(h,16777619)>>>0;}return h>>>0;};
  const actorHash=()=>{let h=2166136261>>>0;const add=(a,len)=>{for(let i=0;i<len;i++){h^=B(a+i);h=Math.imul(h,16777619)>>>0;}};add(P1,STRIDE);add(P2,STRIDE);add(P3,STRIDE);for(let s=0;s<SLOTS;s++)add(POOL+s*STRIDE,STRIDE);return h>>>0;};
  const ramHash=()=>hashRange(0xFF0000,0x10000,16);
  const snapKey=()=>({p1x:[B(P1+4),B(P1+5),B(P1+6),B(P1+7)].join(','),p1a:B(P1+0x2A),p2a:B(P2+0x2A),p3a:B(P3+0x2A)});
  const samples=[];const INTERVAL=50,DURATION=15000;let last=performance.now(),start=last;
  console.log('=== SINGLEPLAYER PAUSE PROBE START ===');
  console.log('15秒内：先正常战斗约3秒 -> 暂停约5秒 -> 恢复并继续战斗。不要开2P。');
  while(performance.now()-start<DURATION){
    await sleep(INTERVAL);const now=performance.now(),dt=now-last;last=now;
    samples.push({t:Math.round(now-start),dt:Math.round(dt),actor:actorHash(),ram:ramHash(),key:snapKey()});
  }
  const longestStable=(field)=>{let best={ms:0,start:0,end:0,samples:0},runStart=0;for(let i=1;i<samples.length;i++){
    if(samples[i][field]!==samples[i-1][field])runStart=i;const a=samples[runStart],b=samples[i],ms=b.t-a.t;if(ms>best.ms)best={ms,start:a.t,end:b.t,samples:i-runStart+1};
  }return best;};
  const actorStable=longestStable('actor'),ramStable=longestStable('ram');
  let maxGap={dt:0,t:0};for(const s of samples)if(s.dt>maxGap.dt)maxGap={dt:s.dt,t:s.t};
  const gapCount=samples.filter(s=>s.dt>=500).length;
  let classification='NO_CLEAR_PAUSE_DETECTED';
  if(maxGap.dt>=800)classification='WORKER_OR_SCHEDULER_SUSPENDED_DURING_PAUSE';
  else if(actorStable.ms>=1500&&ramStable.ms>=1500)classification='CPU_OR_GAME_RAM_FROZEN_WHILE_WORKER_ALIVE';
  else if(actorStable.ms>=1500&&ramStable.ms<1200)classification='GAME_LOGIC_PAUSE_ACTORS_FROZEN_GLOBAL_RAM_STILL_ALIVE';
  else if(actorStable.ms>=1500)classification='LIKELY_GAME_LOGIC_PAUSE_PARTIAL_RAM_ACTIVITY';
  const changes=[];for(let i=1;i<samples.length;i++)if(samples[i].actor!==samples[i-1].actor||samples[i].ram!==samples[i-1].ram||samples[i].dt>=500)changes.push({t:samples[i].t,dt:samples[i].dt,actorChanged:samples[i].actor!==samples[i-1].actor,ramChanged:samples[i].ram!==samples[i-1].ram});
  const out={version:VERSION,readOnly:true,ramWrites:0,durationMs:DURATION,intervalMs:INTERVAL,sampleCount:samples.length,classification,maxJsGap:maxGap,gapCount500ms:gapCount,longestActorStable:actorStable,longestSparseRamStable:ramStable,firstSample:samples[0]||null,lastSample:samples[samples.length-1]||null,changeEvents:changes.slice(0,120),note:'If classification is ambiguous, compare one 1P pause capture with one 2P capture; no broad ROM search is needed.'};
  self.__WOF_SINGLEPLAYER_PAUSE_PROBE=out;
  console.log('=== SINGLEPLAYER PAUSE PROBE VERDICT ===');console.table([{classification,maxGapMs:maxGap.dt,actorStableMs:actorStable.ms,ramStableMs:ramStable.ms,samples:samples.length}]);
  console.log('=== SINGLEPLAYER PAUSE PROBE JSON ===');console.log(JSON.stringify(out,null,2));
  return out;
}finally{self.__WOF_SINGLEPLAYER_PAUSE_RUNNING=false;}
})().catch(e=>{console.error('WOF_SINGLEPLAYER_PAUSE_PROBE_ERROR',e);throw e;});
