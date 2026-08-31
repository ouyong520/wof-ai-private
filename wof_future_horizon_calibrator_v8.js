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
 const roots=[];for(let d0=0;d0<=24;d0+=4){const p=r32(table+d0)>>>0,d=parseDescriptor(p);if(d)roots.push({d0,p,d});}
 return {type,table,roots,d20:roots.find(x=>x.d0===20)?.d||null};
}
const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS={0:'P1',4:'P2',8:'P3'},VALIDPTR={0xBE1C:'P1',0xBEFC:'P2',0xBFDC:'P3'};
const PBASE={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC};
const maps=new Map();const getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
function descMatches(s,d){return !!d&&s.frameEnd12===d.frameEnd&&s.value30===d.value30&&s.nextDesc2C===d.next&&s.timer34<=d.timer;}
function resolveRoot(map,s){if(!map)return null;for(const r of map.roots)if(descMatches(s,r.d))return {source:'level2-root',d0:r.d0,descriptorAt:r.d.at};return null;}
function snap(slot){
 const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;
 const frame=U32(a+0x12),next=U32(a+0x2C);if(frame===0&&next===0)return null;
 const target7E=U16(a+0x7E),ptr=U16(a+0x6A),pn=VALIDPTR[ptr]||null,map=getMap(type);
 const s={slot,type,target7E,target:PLAYERS[target7E]||null,ptr6A:ptr,ptr6AValid:!!pn,ptr6APlayer:pn,selected29:pn?B(PBASE[pn]+0x29):null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),timer34:U16(a+0x34),attack:U16(a+0x70),body:U16(a+0x6E),frameEnd12:frame,nextDesc2C:next,value30:U32(a+0x30)};
 s.inD20=descMatches(s,map?.d20);s.d20Exact=!!(s.inD20&&map?.d20&&s.timer34===map.d20.timer);return s;
}
const timerBucket=t=>t<=1?'1':t<=3?'2-3':t<=6?'4-6':t<=12?'7-12':t<=24?'13-24':'25+';
const baseSig=s=>['T'+s.type,h(s.frameEnd12,8),h(s.nextDesc2C,8),h(s.value30,8),'S'+s.state99,'A'+s.action2A,'B'+s.b2B].join('|');
const descSig=s=>['T'+s.type,h(s.frameEnd12,8),h(s.nextDesc2C,8),h(s.value30,8)].join('|');
const ctrlSig=s=>['T'+s.type,'S'+s.state99,'A'+s.action2A,'B'+s.b2B].join('|');
const sampleSig=s=>baseSig(s)+'|TB'+timerBucket(s.timer34);
const semanticSig=s=>[s.frameEnd12,s.nextDesc2C,s.value30,s.state99,s.action2A,s.b2B,timerBucket(s.timer34),s.attack?1:0].join('|');
function mini(s){return {target:s.target,target7E:s.target7E,ptr6A:hw(s.ptr6A),ptr6AValid:s.ptr6AValid,ptr6APlayer:s.ptr6APlayer,selected29:s.selected29,state99:s.state99,action2A:s.action2A,b2B:s.b2B,timer:s.timer34,timerBucket:timerBucket(s.timer34),attack:s.attack,body:s.body,frameEnd:h(s.frameEnd12,8),next:h(s.nextDesc2C,8),value30:h(s.value30,8)};}
const DURATION=90000,INTERVAL=20,MAX_EXACT=20,MAX_WATCH=3200,POST_ACTIVE=80,HORIZONS=[100,250,500,1000],start=performance.now();
const prev=new Map(),active=new Map(),done=[];let seq=0,exactEntries=0;
function finish(w,t,reason){if(w.done)return;w.done=true;w.endAt=t;w.endRel=t-w.entryAt;w.endReason=reason;done.push(w);active.delete(w.slot);}
function classifySource(w,s){const map=getMap(s.type),root=resolveRoot(map,s);if(root)return root;const p=w.samples[w.samples.length-1];if(p&&p.nextRaw&&validRom(p.nextRaw)){const d=parseDescriptor(p.nextRaw);if(descMatches(s,d))return {source:'chain-next',d0:null,descriptorAt:d.at};}return {source:'runtime-fingerprint',d0:null,descriptorAt:null};}
function addSample(w,s,t,kind){
 const rel=t-w.entryAt,rr=classifySource(w,s),ex={rel,kind,exactKey:sampleSig(s),baseKey:baseSig(s),descKey:descSig(s),ctrlKey:ctrlSig(s)+'|TB'+timerBucket(s.timer34),source:rr.source,d0:rr.d0,descriptorAt:rr.descriptorAt==null?null:h(rr.descriptorAt),nextRaw:s.nextDesc2C,...mini(s)};
 w.samples.push(ex);
}
function startWatch(s,t){
 const old=active.get(s.slot);if(old)finish(old,t,'retrigger');
 const w={id:++seq,slot:s.slot,type:s.type,entryAt:t,entryTarget:s.target,samples:[],firstAttack:null,targetSwitches:[],last:s,lastSem:semanticSig(s),done:false};
 addSample(w,s,t,'D0_20_ENTRY');active.set(s.slot,w);exactEntries++;
}
function update(w,s,t){
 const rel=t-w.entryAt,p=w.last;if(s.type!==w.type){finish(w,t,'typeChanged');return;}
 if(s.target7E!==p.target7E)w.targetSwitches.push({rel,from:p.target,to:s.target,ptrFrom:hw(p.ptr6A),ptrTo:hw(s.ptr6A),action2A:s.action2A});
 const sem=semanticSig(s);if(sem!==w.lastSem&&s.attack===0){addSample(w,s,t,'PREACTIVE_SAMPLE');w.lastSem=sem;}
 if(!w.firstAttack&&p.attack===0&&s.attack!==0)w.firstAttack={rel,attack:s.attack,target:s.target,target7E:s.target7E,state:mini(s)};
 w.last=s;
 if(w.firstAttack&&rel>=w.firstAttack.rel+POST_ACTIVE)finish(w,t,'activeConfirmed');else if(rel>=MAX_WATCH)finish(w,t,'timeout');
}
await new Promise(resolve=>{const id=setInterval(()=>{
 const t=Math.round(performance.now()-start);
 for(let i=0;i<SLOTS;i++){
  const s=snap(i),p=prev.get(i)||null;if(!s){const w=active.get(i);if(w)finish(w,t,'slotGone');prev.delete(i);continue;}
  if(s.d20Exact&&(!p||!p.inD20))startWatch(s,t);
  const w=active.get(i);if(w)update(w,s,t);prev.set(i,s);
 }
 if(t>=DURATION||(exactEntries>=MAX_EXACT&&active.size===0&&done.length>=MAX_EXACT)){clearInterval(id);for(const w of [...active.values()])finish(w,t,'captureEnd');resolve();}
},INTERVAL);});
function horizonOutcome(w,e,H){
 if(w.firstAttack){const lead=w.firstAttack.rel-e.rel;if(lead<0)return 'censored';return lead<=H?'hit':'miss';}
 const follow=w.endRel-e.rel;if(follow>=H)return 'miss';return 'censored';
}
function aggregate(keyName){
 const A={};
 for(const w of done){const seen=new Set();for(const e of w.samples){const k=e[keyName];if(!k||seen.has(k))continue;seen.add(k);const a=(A[k]??={key:k,type:w.type,source:e.source,d0:e.d0,descriptorAt:e.descriptorAt,watches:0,horizons:{},targetHits:{},leadSamples:[]});a.watches++;
   if(w.firstAttack){const lead=w.firstAttack.rel-e.rel;if(lead>=0)a.leadSamples.push(lead);}
   for(const H of HORIZONS){const o=horizonOutcome(w,e,H),x=(a.horizons[H]??={hit:0,miss:0,censored:0});x[o]++;if(o==='hit'){const z=(a.targetHits[H]??={correct:0,total:0});z.total++;if(e.target7E===w.firstAttack.target7E)z.correct++;}}
 }}
 return Object.values(A).map(a=>{a.leadSamples.sort((x,y)=>x-y);for(const H of HORIZONS){const x=a.horizons[H],den=x.hit+x.miss;x.evaluable=den;x.rate=den?+(x.hit/den).toFixed(3):null;const z=a.targetHits[H]||{correct:0,total:0};x.targetCorrectRate=z.total?+(z.correct/z.total).toFixed(3):null;}return a;});
}
function rank(arr,H){return arr.filter(a=>a.horizons[H].evaluable>=2).sort((a,b)=>(b.horizons[H].rate-a.horizons[H].rate)||(b.horizons[H].evaluable-a.horizons[H].evaluable)||(a.leadSamples[0]??99999)-(b.leadSamples[0]??99999)).slice(0,30);}
const exact=aggregate('exactKey'),desc=aggregate('descKey'),ctrl=aggregate('ctrlKey');
const stage1={};for(const w of done){const k='T'+w.type,b=(stage1[k]??={type:w.type,entries:0,outcomes:{active:0,timeout:0,retrigger:0,slotGone:0,typeChanged:0,captureEnd:0},horizons:{}});b.entries++;const oc=w.firstAttack?'active':w.endReason;b.outcomes[oc]=(b.outcomes[oc]||0)+1;for(const H of HORIZONS){const o=horizonOutcome(w,w.samples[0],H),x=(b.horizons[H]??={hit:0,miss:0,censored:0});x[o]++;}}
for(const b of Object.values(stage1))for(const H of HORIZONS){const x=b.horizons[H],den=x.hit+x.miss;x.evaluable=den;x.rate=den?+(x.hit/den).toFixed(3):null;}
const nearActiveExamples=done.filter(w=>w.firstAttack).map(w=>({id:w.id,type:w.type,leadFromD20:w.firstAttack.rel,entryTarget:w.entryTarget,activeTarget:w.firstAttack.target,targetSwitched:w.targetSwitches.length>0,lastSamples:w.samples.filter(e=>e.rel<=w.firstAttack.rel).slice(-5).map(({nextRaw,...e})=>({...e,toActiveMs:w.firstAttack.rel-e.rel}))}));
const rows=done.map(w=>({id:w.id,slot:w.slot,type:w.type,outcome:w.firstAttack?'active':w.endReason,leadToActiveMs:w.firstAttack?.rel??null,entryTarget:w.entryTarget,activeTarget:w.firstAttack?.target??null,targetSwitches:w.targetSwitches.length,sampleCount:w.samples.length,endRel:w.endRel}));
const out={version:'wof-future-horizon-calibrator-v8',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationRequestedMs:DURATION,intervalMs:INTERVAL,maxExact:MAX_EXACT,maxWatchMs:MAX_WATCH,horizonsMs:HORIZONS,model:{stage1:'D0=20 is a type-conditioned ATTACK_READY feature',stage2:'promote per-type state signatures only by prospective horizon precision',censoring:'retrigger/slotGone/typeChanged/captureEnd are censored when follow-up is shorter than the tested horizon; they are not automatic false positives',targetPolicy:'enemy+0x7E authoritative; +0x6A only supporting cache when BE1C/BEFC/BFDC'},totals:{exactEntries,completed:done.length,active:done.filter(w=>w.firstAttack).length,timeout:done.filter(w=>w.endReason==='timeout'&&!w.firstAttack).length,retrigger:done.filter(w=>w.endReason==='retrigger'&&!w.firstAttack).length,slotGone:done.filter(w=>w.endReason==='slotGone'&&!w.firstAttack).length},stage1ByType:stage1,candidates:{exactTimer100:rank(exact,100),exactTimer250:rank(exact,250),exactTimer500:rank(exact,500),descriptor250:rank(desc,250),controlTimer250:rank(ctrl,250)},nearActiveExamples,rows,note:'Prospective horizon calibration for Future Danger. A candidate is useful only if repeated exposures retain high hit rate at the requested horizon; post-hoc eventual-active rate is not sufficient.'};
self.__WOF_FUTURE_HORIZON_CALIBRATOR_V8=out;
console.log('=== FUTURE HORIZON CALIBRATOR V8 JSON ===');console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('WOF_FUTURE_HORIZON_CALIBRATOR_V8_ERROR',e);throw e;});