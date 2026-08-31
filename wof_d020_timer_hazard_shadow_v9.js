(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const M=_0x515056.HEAPU8,romBase=C.base,SW=!!C.swap16,ROMMAX=Math.min(0x100000,M.length-romBase);
const r8=o=>M[romBase+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const validRom=v=>v>=0x2000&&v<ROMMAX&&(v&1)===0;
const h=(x,n=6)=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(n,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const gate={
 dispatcher25C8:r16(0x25C8)===0x3228&&r16(0x25D0)===0x287B&&r16(0x25D4)===0x2874,
 handoff247C:r16(0x247C)===0x2C5C&&r16(0x247E)===0x215C&&r16(0x2482)===0x321C,
 d0_20Source:r16(0x6A62)===0x7014&&r16(0x6A64)===0x4EB8&&r16(0x6A66)===0x25C8,
 attackField:true
};
function parseDescriptor(at){
 if(!validRom(at)||at+14>ROMMAX)return null;
 const frameEnd=r32(at)>>>0,value30=r32(at+4)>>>0,timerRaw=r16(at+8)>>>0;
 if(!validRom(frameEnd))return null;
 const flagged=!!(timerRaw&0x8000),timer=flagged?(timerRaw&0x7fff):timerRaw;
 const next=flagged?(r32(at+10)>>>0):((at+10)>>>0);
 if(!validRom(next))return null;
 return {at,frameEnd,value30,timerRaw,flagged,timer,next};
}
function typeMap(type){
 if(type<0||type>=47)return null;
 const table=r32(0x25DC+type*4)>>>0;if(!validRom(table))return null;
 const p=r32(table+20)>>>0,d20=parseDescriptor(p);return {type,table,d20};
}
const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS={0:'P1',4:'P2',8:'P3'},VALIDPTR={0xBE1C:'P1',0xBEFC:'P2',0xBFDC:'P3'},PBASE={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC};
const maps=new Map();const getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
function descMatches(s,d){return !!d&&s.frameEnd12===d.frameEnd&&s.value30===d.value30&&s.nextDesc2C===d.next&&s.timer34<=d.timer;}
function snap(slot){
 const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;
 const frame=U32(a+0x12),next=U32(a+0x2C);if(frame===0&&next===0)return null;
 const target7E=U16(a+0x7E),ptr=U16(a+0x6A),pn=VALIDPTR[ptr]||null,map=getMap(type);
 const s={slot,type,target7E,target:PLAYERS[target7E]||null,ptr6A:ptr,ptr6AValid:!!pn,ptr6APlayer:pn,selected29:pn?B(PBASE[pn]+0x29):null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),timer34:U16(a+0x34),attack:U16(a+0x70),body:U16(a+0x6E),frameEnd12:frame,nextDesc2C:next,value30:U32(a+0x30)};
 s.inD20=descMatches(s,map?.d20);s.d20Exact=!!(s.inD20&&map?.d20&&s.timer34===map.d20.timer);return s;
}
function mini(s){return {target:s.target,target7E:s.target7E,ptr6A:hw(s.ptr6A),ptr6AValid:s.ptr6AValid,ptr6APlayer:s.ptr6APlayer,selected29:s.selected29,state99:s.state99,action2A:s.action2A,b2B:s.b2B,timer:s.timer34,attack:s.attack,body:s.body,frameEnd:h(s.frameEnd12,8),next:h(s.nextDesc2C,8),value30:h(s.value30,8)};}
const DURATION=120000,INTERVAL=20,MAX_EXACT=30,MAX_FOLLOW=1200,POST_ACTIVE=60,HORIZONS=[100,250,500,1000],THRESHOLDS=[12,6,3,1],start=performance.now();
const prev=new Map(),active=new Map(),done=[];let seq=0,exactEntries=0;
function finish(w,t,reason){if(w.done)return;w.done=true;w.endAt=t;w.endRel=t-w.entryAt;w.endReason=reason;done.push(w);active.delete(w.slot);}
function addExposure(w,s,t,trigger){
 const rel=t-w.entryAt,e={rel,trigger,type:s.type,target:s.target,target7E:s.target7E,state99:s.state99,action2A:s.action2A,b2B:s.b2B,timer:s.timer34,frameEnd:h(s.frameEnd12,8),next:h(s.nextDesc2C,8),value30:h(s.value30,8),ptr6A:hw(s.ptr6A),ptr6AValid:s.ptr6AValid};
 e.globalKey=trigger;
 e.typeKey='T'+s.type+'|'+trigger;
 e.ctrlKey='T'+s.type+'|'+trigger+'|S'+s.state99+'|A'+s.action2A+'|B'+s.b2B;
 e.descKey='T'+s.type+'|'+trigger+'|'+e.frameEnd+'|'+e.next+'|'+e.value30;
 w.exposures.push(e);return e;
}
function markThresholds(w,s,t){
 if(!s.inD20||s.attack!==0)return;
 for(const th of THRESHOLDS){const key='LE'+th;if(s.timer34<=th&&!w.thresholdSeen.has(key)){w.thresholdSeen.add(key);addExposure(w,s,t,key);}}
}
function startWatch(s,t){
 const old=active.get(s.slot);if(old)finish(old,t,'retrigger');
 const w={id:++seq,slot:s.slot,type:s.type,entryAt:t,entryTarget:s.target,firstAttack:null,targetSwitches:[],thresholdSeen:new Set(),ctrlSeen:new Set(),exposures:[],last:s,done:false};
 addExposure(w,s,t,'ENTRY');markThresholds(w,s,t);active.set(s.slot,w);exactEntries++;
}
function update(w,s,t){
 const rel=t-w.entryAt,p=w.last;
 if(s.type!==w.type){finish(w,t,'typeChanged');return;}
 if(s.target7E!==p.target7E)w.targetSwitches.push({rel,from:p.target,to:s.target,ptrFrom:hw(p.ptr6A),ptrTo:hw(s.ptr6A),action2A:s.action2A});
 if(p.inD20&&s.inD20&&s.attack===0&&(s.state99!==p.state99||s.action2A!==p.action2A||s.b2B!==p.b2B)){
   const ck='S'+s.state99+'|A'+s.action2A+'|B'+s.b2B;
   if(!w.ctrlSeen.has(ck)){w.ctrlSeen.add(ck);addExposure(w,s,t,'CTRL_CHANGE');}
 }
 markThresholds(w,s,t);
 if(p.inD20&&!s.inD20&&s.attack===0&&!w.exitSeen){w.exitSeen=true;addExposure(w,s,t,'D20_EXIT');}
 if(!w.firstAttack&&p.attack===0&&s.attack!==0)w.firstAttack={rel,attack:s.attack,target:s.target,target7E:s.target7E,state:mini(s)};
 w.last=s;
 if(w.firstAttack&&rel>=w.firstAttack.rel+POST_ACTIVE)finish(w,t,'activeConfirmed');
 else if(rel>=MAX_FOLLOW)finish(w,t,'horizonComplete');
}
await new Promise(resolve=>{const id=setInterval(()=>{
 const t=Math.round(performance.now()-start);
 for(let i=0;i<SLOTS;i++){
   const s=snap(i),p=prev.get(i)||null;
   if(!s){const w=active.get(i);if(w)finish(w,t,'slotGone');prev.delete(i);continue;}
   if(s.d20Exact&&(!p||!p.inD20))startWatch(s,t);
   const w=active.get(i);if(w)update(w,s,t);
   prev.set(i,s);
 }
 if(t>=DURATION||(exactEntries>=MAX_EXACT&&active.size===0&&done.length>=MAX_EXACT)){
   clearInterval(id);for(const w of [...active.values()])finish(w,t,'captureEnd');resolve();
 }
},INTERVAL);});
function outcome(w,e,H){
 if(w.firstAttack){const lead=w.firstAttack.rel-e.rel;if(lead<0)return 'censored';return lead<=H?'hit':'miss';}
 const follow=w.endRel-e.rel;return follow>=H?'miss':'censored';
}
function aggregate(keyName){
 const A={};
 for(const w of done){const seen=new Set();for(const e of w.exposures){const k=e[keyName];if(!k||seen.has(k))continue;seen.add(k);const a=(A[k]??={key:k,trigger:e.trigger,type:w.type,exposures:0,horizons:{},leadSamples:[],targetHits:{}});a.exposures++;
   if(w.firstAttack){const lead=w.firstAttack.rel-e.rel;if(lead>=0)a.leadSamples.push(lead);}
   for(const H of HORIZONS){const o=outcome(w,e,H),x=(a.horizons[H]??={hit:0,miss:0,censored:0});x[o]++;if(o==='hit'){const z=(a.targetHits[H]??={correct:0,total:0});z.total++;if(e.target7E===w.firstAttack.target7E)z.correct++;}}
 }}
 return Object.values(A).map(a=>{a.leadSamples.sort((x,y)=>x-y);for(const H of HORIZONS){const x=a.horizons[H],den=x.hit+x.miss;x.evaluable=den;x.rate=den?+(x.hit/den).toFixed(3):null;const z=a.targetHits[H]||{correct:0,total:0};x.targetCorrectRate=z.total?+(z.correct/z.total).toFixed(3):null;}return a;});
}
function rank(arr,H,minEval=2){return arr.filter(a=>a.horizons[H].evaluable>=minEval).sort((a,b)=>(b.horizons[H].rate-a.horizons[H].rate)||(b.horizons[H].evaluable-a.horizons[H].evaluable)||((a.leadSamples[0]??99999)-(b.leadSamples[0]??99999))).slice(0,40);}
const globalAgg=aggregate('globalKey'),typeAgg=aggregate('typeKey'),ctrlAgg=aggregate('ctrlKey'),descAgg=aggregate('descKey');
const rows=done.map(w=>({id:w.id,slot:w.slot,type:w.type,entryTarget:w.entryTarget,outcome:w.firstAttack?'active':w.endReason,leadToActiveMs:w.firstAttack?.rel??null,activeTarget:w.firstAttack?.target??null,targetSwitches:w.targetSwitches,exposures:w.exposures,endRel:w.endRel}));
const out={version:'wof-d020-timer-hazard-shadow-v9',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationRequestedMs:DURATION,intervalMs:INTERVAL,maxExact:MAX_EXACT,maxFollowMs:MAX_FOLLOW,horizonsMs:HORIZONS,timerThresholds:THRESHOLDS,model:{stage1:'exact D0=20 entry = type-conditioned ATTACK_READY',stage2:'prospectively test one exposure per D0 episode when live D0=20 timer first reaches <=12/6/3/1; also observe D0 exit and control-state changes',predictionHorizon:'0-1000ms only; watches without active are closed after >=1200ms because later attacks are irrelevant to the requested horizon',targetPolicy:'enemy+0x7E authoritative; +0x6A only supporting cache when BE1C/BEFC/BFDC'},totals:{exactEntries,completed:done.length,active:done.filter(w=>w.firstAttack).length,horizonComplete:done.filter(w=>w.endReason==='horizonComplete'&&!w.firstAttack).length,retrigger:done.filter(w=>w.endReason==='retrigger'&&!w.firstAttack).length,slotGone:done.filter(w=>w.endReason==='slotGone'&&!w.firstAttack).length},globalTriggerStats:globalAgg,typeTriggerStats:typeAgg,candidates:{type100:rank(typeAgg,100),type250:rank(typeAgg,250),control100:rank(ctrlAgg,100),control250:rank(ctrlAgg,250),descriptor100:rank(descAgg,100),descriptor250:rank(descAgg,250)},rows,note:'Episode-level timer-hazard shadow. Each threshold contributes at most one exposure per exact D0=20 episode, reducing repeated-sample bias. Promote a timer/control rule only if prospective short-horizon precision repeats across independent episodes.'};
self.__WOF_D020_TIMER_HAZARD_SHADOW_V9=out;
console.log('=== D0=20 TIMER HAZARD SHADOW V9 JSON ===');console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('WOF_D020_TIMER_HAZARD_SHADOW_V9_ERROR',e);throw e;});