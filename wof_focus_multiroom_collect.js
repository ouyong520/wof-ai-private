(async()=>{
'use strict';
try{await self.__WOF_FOCUS_MULTIROOM?.finish?.('restart');}catch(_){}
const CFG={db:'wof-focus-multiroom-v1',store:'sessions',durationMs:10*60*1000,sampleMs:100,checkpointMs:10000,maxValuesPerOffset:64,maxSwitchEvents:160};
const PLAYERS={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC},PN=['P1','P2','P3'],PI={P1:0,P2:1,P3:2};
const POOL=0xFFC0BC,STRIDE=0xE0,N=20;
const M=_0x515056?.HEAPU8,R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!M||!R)throw new Error('CPS RAM unavailable');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))],U16=a=>((B(a)<<8)|B(a+1))>>>0,U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0,S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;},W=v=>v/65536,clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const player=n=>{const b=PLAYERS[n];return B(b)?{n,x:W(S32(b+4)),y:W(S32(b+8)),hp:B(b+0x83)}:null;};
const actor=slot=>{const b=POOL+slot*STRIDE;if(!B(b))return null;return{slot,b,type:U16(b+0x20),x:W(S32(b+4)),y:W(S32(b+8)),attack:U16(b+0x70),state:[B(b+0x28),B(b+0x29),B(b+0x2A),B(b+0x2B)]};};
function openDb(){return new Promise((res,rej)=>{const q=indexedDB.open(CFG.db,1);q.onupgradeneeded=()=>{const db=q.result;if(!db.objectStoreNames.contains(CFG.store)){const s=db.createObjectStore(CFG.store,{keyPath:'id'});s.createIndex('startedAt','startedAt',{unique:false});}};q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error);});}
function put(db,row){return new Promise((res,rej)=>{const tx=db.transaction(CFG.store,'readwrite');tx.objectStore(CFG.store).put(row);tx.oncomplete=()=>res();tx.onerror=()=>rej(tx.error);});}
const id=()=>{try{return crypto.randomUUID().slice(0,8)}catch(_){return Math.random().toString(36).slice(2,10)}};
const H=Array.from({length:N},()=>({last:null,dist:{},ema:{P1:0,P2:0,P3:0},target:null,conf:0,lastTargetAt:0,lastMoveAt:0}));
const WS=Array.from({length:STRIDE/2},()=>({total:0,targets:[0,0,0],exact:0,wrongPlayer:0,values:new Map()}));
const playerCountHist=[0,0,0,0],switches=[],typeTargets=new Map();
let running=true,samples=0,strongLabels=0,startedAt=Date.now(),sampleTimer=null,checkpointTimer=null,finishing=false;
function infer(slot,o,ps,now){const h=H[slot],live=PN.filter(n=>ps[n]);if(!live.length){h.target=null;h.conf=0;h.last={x:o.x,y:o.y};return h;}if(h.last){const mx=o.x-h.last.x,my=o.y-h.last.y,m=Math.hypot(mx,my);for(const n of live){const p=ps[n],d=Math.hypot(p.x-o.x,p.y-o.y),pd=h.dist[n];let q=0;if(m>=.08&&d>=1){const dx=p.x-o.x,dy=p.y-o.y,align=(mx*dx+my*dy)/(m*d),gain=pd==null?0:(pd-d)/Math.max(.08,m);q=.62*clamp(align,-1,1)+.38*clamp(gain,-1,1);h.lastMoveAt=now;}h.ema[n]=h.ema[n]*.78+q*.22;h.dist[n]=d;}for(const n of PN)if(!ps[n])h.ema[n]*=.9;
  let ranked=live.map(n=>[n,h.ema[n]]).sort((a,b)=>b[1]-a[1]),best=ranked[0],second=ranked[1]?.[1]??-.5,margin=best[1]-second,conf=live.length===1?clamp((best[1]-.05)/.55,0,1):clamp((best[1]-.02)/.55,0,1)*clamp((margin-.04)/.30,0,1);
  const prev=h.target;if(conf>=.58&&best[1]>=.18){h.target=best[0];h.conf=conf;h.lastTargetAt=now;if(prev&&prev!==h.target&&switches.length<CFG.maxSwitchEvents){switches.push({t:+((now-startedAt)/1000).toFixed(2),slot:o.slot,type:o.type,from:prev,to:h.target,conf:+conf.toFixed(2),attack:o.attack,words:Array.from({length:STRIDE/2},(_,i)=>U16(o.b+i*2))});}}else if(now-h.lastTargetAt>900){h.target=null;h.conf=0;}
 }h.last={x:o.x,y:o.y};return h;}
function addValue(s,v,ti){let a=s.values.get(v);if(!a){if(s.values.size>=CFG.maxValuesPerOffset)return;a=[0,0,0];s.values.set(v,a);}a[ti]++;}
function learn(o,h,liveCount){if(liveCount<2||!h.target||h.conf<.62)return;const ti=PI[h.target];strongLabels++;for(let off=0;off<STRIDE;off+=2){const s=WS[off>>1],v=U16(o.b+off);s.total++;s.targets[ti]++;if(v===(PLAYERS[h.target]&0xffff))s.exact++;else if(PN.some(n=>n!==h.target&&v===(PLAYERS[n]&0xffff)))s.wrongPlayer++;addValue(s,v,ti);}const k=String(o.type),t=typeTargets.get(k)||[0,0,0];t[ti]++;typeTargets.set(k,t);}
function tick(){if(!running)return;const now=Date.now(),ps=Object.fromEntries(PN.map(n=>[n,player(n)])),live=PN.filter(n=>ps[n]).length;playerCountHist[live]++;for(let slot=0;slot<N;slot++){const o=actor(slot);if(!o){H[slot]={last:null,dist:{},ema:{P1:0,P2:0,P3:0},target:null,conf:0,lastTargetAt:0,lastMoveAt:0};continue;}const h=infer(slot,o,ps,now);learn(o,h,live);}samples++;}
function snap(){const words=WS.map((s,i)=>{const vals=[...s.values.entries()].map(([v,c])=>({v,c})).sort((a,b)=>b.c.reduce((x,y)=>x+y,0)-a.c.reduce((x,y)=>x+y,0)).slice(0,20);return{offset:i*2,total:s.total,targets:s.targets,exact:s.exact,wrongPlayer:s.wrongPlayer,values:vals};});return{version:'focus-multiroom-v1',samples,strongLabels,playerCountHist:[...playerCountHist],words,switches:[...switches],typeTargets:Object.fromEntries(typeTargets)};}
const db=await openDb(),sid='focus-'+id(),row={id:sid,schema:'wof-focus-multiroom-v1',status:'running',startedAt,latestAt:startedAt,plannedEndAt:startedAt+CFG.durationMs,completedAt:null,worker:String(self.location?.href||''),checkpoints:[],final:null};await put(db,row);
async function checkpoint(){row.latestAt=Date.now();row.checkpoints.push({at:row.latestAt,samples,strongLabels,playerCountHist:[...playerCountHist]});if(row.checkpoints.length>72)row.checkpoints.shift();await put(db,row);}
async function finish(reason='complete'){if(finishing)return;finishing=true;running=false;if(sampleTimer)clearInterval(sampleTimer);if(checkpointTimer)clearInterval(checkpointTimer);row.status=reason==='complete'?'complete':'stopped';row.completedAt=Date.now();row.latestAt=row.completedAt;row.final=snap();await put(db,row);try{db.close()}catch(_){}console.log('✅ Focus multiroom结束',sid,row.status,'strongLabels',strongLabels);}
sampleTimer=setInterval(tick,CFG.sampleMs);tick();checkpointTimer=setInterval(()=>{checkpoint().catch(console.error);if(Date.now()>=row.plannedEndAt)finish('complete').catch(console.error);},CFG.checkpointMs);
self.__WOF_FOCUS_MULTIROOM={version:'focus-multiroom-v1',id:sid,get running(){return running},status(){return{id:sid,running,samples,strongLabels,playerCountHist:[...playerCountHist],seconds:+((Date.now()-startedAt)/1000).toFixed(1)}},snapshot:snap,finish};
console.log('🟢 Focus multiroom collector started',sid,'| 10分钟 | 只用>=2玩家且高置信追击样本学习焦点字段');
return self.__WOF_FOCUS_MULTIROOM.status();
})().catch(e=>console.error('❌ Focus multiroom collector failed',e));