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
 const roots=[];
 for(let d0=0;d0<=24;d0+=4){const p=r32(table+d0)>>>0,d=parseDescriptor(p);if(d)roots.push({d0,p,d});}
 const d20=roots.find(x=>x.d0===20)?.d||null;
 return {type,table,roots,d20};
}
const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS={0:{name:'P1'},4:{name:'P2'},8:{name:'P3'}};
const VALIDPTR={0xBE1C:'P1',0xBEFC:'P2',0xBFDC:'P3'};
const maps=new Map();const getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
function descMatches(s,d){return !!d&&s.frameEnd12===d.frameEnd&&s.value30===d.value30&&s.nextDesc2C===d.next&&s.timer34<=d.timer;}
function resolveRoot(map,s){if(!map)return null;for(const r of map.roots)if(descMatches(s,r.d))return {source:'level2-root',d0:r.d0,descriptorAt:r.d.at};return null;}
function snap(slot){
 const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;
 const frame=U32(a+0x12),next=U32(a+0x2C);if(frame===0&&next===0)return null;
 const target7E=U16(a+0x7E),ptr=U16(a+0x6A),map=getMap(type);
 const s={slot,type,target7E,target:PLAYERS[target7E]?.name||null,ptr6A:ptr,ptr6APlayer:VALIDPTR[ptr]||null,ptr6AValid:!!VALIDPTR[ptr],selected29:VALIDPTR[ptr]?B(({P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC})[VALIDPTR[ptr]]+0x29):null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),timer34:U16(a+0x34),attack:U16(a+0x70),body:U16(a+0x6E),frameEnd12:frame,nextDesc2C:next,value30:U32(a+0x30)};
 s.inD20=descMatches(s,map?.d20);s.d20Exact=!!(s.inD20&&map?.d20&&s.timer34===map.d20.timer);
 return s;
}
function semanticSig(s){return [s.frameEnd12,s.nextDesc2C,s.value30,s.state99,s.action2A,s.b2B,s.attack?1:0].join('|');}
function branchSig(s){return ['T'+s.type,h(s.frameEnd12,8),h(s.nextDesc2C,8),h(s.value30,8),'S'+s.state99,'A'+s.action2A,'B'+s.b2B].join('|');}
function mini(s){return {target:s.target,target7E:s.target7E,ptr6A:hw(s.ptr6A),ptr6AValid:s.ptr6AValid,ptr6APlayer:s.ptr6APlayer,selected29:s.selected29,state99:s.state99,action2A:s.action2A,b2B:s.b2B,timer:s.timer34,attack:s.attack,body:s.body,frameEnd:h(s.frameEnd12,8),next:h(s.nextDesc2C,8),value30:h(s.value30,8)};}
const DURATION=90000,INTERVAL=20,MAX_EXACT=20,MAX_WATCH=2200,POST_ACTIVE=80,start=performance.now();
const prev=new Map(),active=new Map(),done=[];let seq=0,exactEntries=0;
function finish(w,t,reason){if(w.done)return;w.done=true;w.endAt=t;w.endReason=reason;done.push(w);active.delete(w.slot);}
function addNode(w,s,t,kind){
 if(w.nodes.length>=40)return;
 const map=getMap(s.type),root=resolveRoot(map,s);
 const prevNode=w.nodes[w.nodes.length-1]||null;
 let chain=null;
 if(!root&&prevNode&&prevNode.nextRaw&&validRom(prevNode.nextRaw)){
   const d=parseDescriptor(prevNode.nextRaw);if(descMatches(s,d))chain={source:'chain-next',d0:null,descriptorAt:d.at};
 }
 const rr=root||chain||{source:'runtime-fingerprint',d0:null,descriptorAt:null};
 w.nodes.push({rel:t-w.entryAt,kind,branchSig:branchSig(s),source:rr.source,d0:rr.d0,descriptorAt:rr.descriptorAt==null?null:h(rr.descriptorAt),nextRaw:s.nextDesc2C,...mini(s)});
}
function startWatch(s,t){
 const old=active.get(s.slot);if(old)finish(old,t,'retrigger');
 const map=getMap(s.type),w={id:++seq,slot:s.slot,type:s.type,entryAt:t,startTimer:map?.d20?.timer??null,entryTarget:s.target,firstAttack:null,targetSwitches:[],nodes:[],last:s,lastSem:semanticSig(s),done:false};
 addNode(w,s,t,'D0_20_ENTRY');active.set(s.slot,w);exactEntries++;
}
function update(w,s,t){
 const rel=t-w.entryAt,p=w.last;
 if(s.type!==w.type){finish(w,t,'typeChanged');return;}
 if(s.target7E!==p.target7E)w.targetSwitches.push({rel,from:p.target,to:s.target,ptrFrom:hw(p.ptr6A),ptrTo:hw(s.ptr6A),action2A:s.action2A});
 const sem=semanticSig(s);
 if(sem!==w.lastSem&&s.attack===0){addNode(w,s,t,'PREACTIVE_STATE');w.lastSem=sem;}
 if(!w.firstAttack&&p.attack===0&&s.attack!==0){
   w.firstAttack={rel,attack:s.attack,target:s.target,state:mini(s)};
 }
 w.last=s;
 if(w.firstAttack&&rel>=w.firstAttack.rel+POST_ACTIVE)finish(w,t,'activeConfirmed');
 else if(rel>=MAX_WATCH)finish(w,t,'timeout');
}
await new Promise(resolve=>{
 const id=setInterval(()=>{
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
 },INTERVAL);
});
const rows=done.map(w=>({id:w.id,slot:w.slot,type:w.type,startTimer:w.startTimer,entryTarget:w.entryTarget,outcome:w.firstAttack?'active':w.endReason,leadToActiveMs:w.firstAttack?.rel??null,activeTarget:w.firstAttack?.target??null,targetSwitches:w.targetSwitches,nodes:w.nodes.map(({nextRaw,...x})=>x),endReason:w.endReason}));
const agg={};
for(const w of done){
 for(const n of w.nodes){
   if(n.attack!==0)continue;
   const k=n.branchSig,a=(agg[k]??={type:w.type,signature:k,source:n.source,d0:n.d0,descriptorAt:n.descriptorAt,visits:0,activeAfter:0,retriggerAfter:0,timeoutAfter:0,leadsToActive:[]});
   a.visits++;
   if(w.firstAttack){const lead=w.firstAttack.rel-n.rel;if(lead>=0){a.activeAfter++;a.leadsToActive.push(lead);}}
   else if(w.endReason==='retrigger')a.retriggerAfter++;
   else if(w.endReason==='timeout')a.timeoutAfter++;
 }
}
const med=a=>a.length?a[Math.floor(a.length/2)]:null;
const branchCandidates=Object.values(agg).map(a=>{
 a.leadsToActive.sort((x,y)=>x-y);const v=a.leadsToActive;
 return {...a,activeRateIgnoringRetrigger:+(a.activeAfter/Math.max(1,a.visits-a.retriggerAfter)).toFixed(3),minMs:v[0]??null,medianMs:med(v),maxMs:v.length?v[v.length-1]:null,within100:v.filter(x=>x<=100).length,within250:v.filter(x=>x<=250).length,within500:v.filter(x=>x<=500).length,within1000:v.filter(x=>x<=1000).length};
}).sort((a,b)=>(b.visits-a.visits)||((a.medianMs??99999)-(b.medianMs??99999)));
const byType={};for(const r of rows){const k='T'+r.type;(byType[k]??={entries:0,active:0,retrigger:0,timeout:0,within1000:0,leads:[]});const b=byType[k];b.entries++;if(r.outcome==='active'){b.active++;b.leads.push(r.leadToActiveMs);if(r.leadToActiveMs<=1000)b.within1000++;}else if(r.outcome==='retrigger')b.retrigger++;else if(r.outcome==='timeout')b.timeout++;}
for(const b of Object.values(byType))b.leads.sort((a,b)=>a-b);
const evaluable=rows.filter(r=>r.outcome!=='retrigger'),activeRows=rows.filter(r=>r.outcome==='active');
const out={version:'wof-d020-type-branch-learner-v7',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationRequestedMs:DURATION,intervalMs:INTERVAL,maxExact:MAX_EXACT,maxWatchMs:MAX_WATCH,model:{stage1:'D0=20 is an ATTACK_READY feature, not a guaranteed <=1000ms attack',stage2:'learn per-type runtime branch signatures after D0=20; no universal next1 assumption',targetPolicy:'enemy+0x7E is authoritative; enemy+0x6A is supporting selected-player cache only when value is BE1C/BEFC/BFDC'},totals:{exactEntries,completed:rows.length,active:activeRows.length,retrigger:rows.filter(r=>r.outcome==='retrigger').length,timeout:rows.filter(r=>r.outcome==='timeout').length,evaluable:evaluable.length,activeWithin1000:activeRows.filter(r=>r.leadToActiveMs<=1000).length},byType,branchCandidates:branchCandidates.slice(0,80),rows,note:'Read-only per-type branch learner. Use repeated branch signatures with high active rate and short lead as Stage2 candidates; retriggers are censored rather than counted as false positives.'};
self.__WOF_D020_TYPE_BRANCH_LEARNER_V7=out;
console.log('=== D0=20 TYPE BRANCH LEARNER V7 JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_D020_TYPE_BRANCH_LEARNER_V7_ERROR',e);throw e;});