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
  for(let d0=0;d0<=24;d0+=4){const p=r32(table+d0)>>>0,desc=parseDescriptor(p);if(desc)roots.push({d0,p,desc});}
  const d20=roots.find(x=>x.d0===20)?.desc||null;
  return {type,table,roots,d20};
}
const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS={0:{name:'P1',base:0xFFBE1C},4:{name:'P2',base:0xFFBEFC},8:{name:'P3',base:0xFFBFDC}};
const LOW={0xBE1C:PLAYERS[0],0xBEFC:PLAYERS[4],0xBFDC:PLAYERS[8]};
const maps=new Map();const getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
function descMatches(s,d){return !!d&&s.frameEnd12===d.frameEnd&&s.value30===d.value30&&s.nextDesc2C===d.next&&s.timer34<=d.timer;}
function phase20(s,map){if(!map?.d20||!descMatches(s,map.d20))return null;return {descriptor:map.d20.at,startTimer:map.d20.timer,exactStart:s.timer34===map.d20.timer};}
function snap(slot){
  const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;
  const frame=U32(a+0x12),next=U32(a+0x2C);if(frame===0&&next===0)return null;
  const target7E=U16(a+0x7E),tp=PLAYERS[target7E]||null,ptr=U16(a+0x6A),sp=LOW[ptr]||null;
  const s={slot,type,target7E,target:tp?.name||null,ptr6A:ptr,selectedPlayer:sp?.name||null,selected29:sp?B(sp.base+0x29):null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),timer34:U16(a+0x34),attack:U16(a+0x70),body:U16(a+0x6E),frameEnd12:frame,nextDesc2C:next,value30:U32(a+0x30)};
  s.phase20=phase20(s,getMap(type));
  return s;
}
function stateMini(s){return {target:s.target,ptr6A:hw(s.ptr6A),selected29:s.selected29,state99:s.state99,action2A:s.action2A,b2B:s.b2B,timer:s.timer34,attack:s.attack,body:s.body,frameEnd:h(s.frameEnd12,8),next:h(s.nextDesc2C,8),value30:h(s.value30,8)};}
function descSig(s){return s.frameEnd12+'|'+s.nextDesc2C+'|'+s.value30;}
function resolveDescriptor(map,s,prev){
  if(map){
    for(const r of map.roots)if(descMatches(s,r.desc))return {descriptorAt:r.desc.at,source:'level2-root',d0:r.d0,startTimer:r.desc.timer};
  }
  if(prev&&validRom(prev.nextDesc2C)){
    const d=parseDescriptor(prev.nextDesc2C);
    if(descMatches(s,d))return {descriptorAt:d.at,source:'chain-next',d0:null,startTimer:d.timer};
  }
  return {descriptorAt:null,source:'unresolved',d0:null,startTimer:null};
}
const DURATION=60000,INTERVAL=20,MAX_EXACT=10,MAX_WATCH=1400,POST_ACTIVE=80,start=performance.now();
const prevSlots=new Map(),watches=new Map(),done=[];let seq=0,exactEntries=0;
function finish(w,t,reason){if(w.done)return;w.done=true;w.endAt=t;w.endReason=reason;done.push(w);watches.delete(w.slot);}
function startWatch(s,t){
  const old=watches.get(s.slot);if(old)finish(old,t,'retrigger');
  const w={id:++seq,slot:s.slot,type:s.type,entryAt:t,startTimer:s.phase20.startTimer,entryTarget:s.target,entryAction:s.action2A,entrySelected29:s.selected29,firstAttack:null,targetSwitches:[],nodes:[{rel:0,descriptorAt:h(s.phase20.descriptor),source:'D0=20',d0:20,...stateMini(s)}],last:s,lastDescSig:descSig(s),done:false};
  watches.set(s.slot,w);exactEntries++;
}
function update(w,s,t){
  const rel=t-w.entryAt,p=w.last,map=getMap(w.type);
  if(s.type!==w.type){finish(w,t,'typeChanged');return;}
  if(s.target7E!==p.target7E)w.targetSwitches.push({rel,from:p.target,to:s.target,ptrFrom:hw(p.ptr6A),ptrTo:hw(s.ptr6A),action2A:s.action2A});
  const sig=descSig(s);
  if(sig!==w.lastDescSig){
    const rr=resolveDescriptor(map,s,p);
    w.nodes.push({rel,descriptorAt:rr.descriptorAt==null?null:h(rr.descriptorAt),source:rr.source,d0:rr.d0,startTimer:rr.startTimer,...stateMini(s)});
    w.lastDescSig=sig;
  }
  if(!w.firstAttack&&p.attack===0&&s.attack!==0){
    const preNodes=w.nodes.filter(n=>n.rel<=rel&&n.attack===0);
    const lastPre=preNodes.length?preNodes[preNodes.length-1]:null;
    w.firstAttack={rel,attack:s.attack,target:s.target,action2A:s.action2A,lastPreNodeRel:lastPre?.rel??0,lastPreToActiveMs:lastPre?rel-lastPre.rel:null,lastPreDescriptor:lastPre?.descriptorAt??null,lastPreSource:lastPre?.source??null,lastPreD0:lastPre?.d0??null,state:stateMini(s)};
  }
  w.last=s;
  if(w.firstAttack&&rel>=w.firstAttack.rel+POST_ACTIVE)finish(w,t,'activeConfirmed');
  else if(rel>=MAX_WATCH)finish(w,t,'timeout');
}
await new Promise(resolve=>{
 const id=setInterval(()=>{
   const t=Math.round(performance.now()-start);
   for(let i=0;i<SLOTS;i++){
     const s=snap(i),p=prevSlots.get(i)||null;
     if(!s){const w=watches.get(i);if(w)finish(w,t,'slotGone');prevSlots.delete(i);continue;}
     const entered=s.phase20?.exactStart&&(!p?.phase20||p.phase20.descriptor!==s.phase20.descriptor);
     if(entered)startWatch(s,t);
     const w=watches.get(i);if(w)update(w,s,t);
     prevSlots.set(i,s);
   }
   if(t>=DURATION||(exactEntries>=MAX_EXACT&&watches.size===0&&done.length>=MAX_EXACT)){
     clearInterval(id);for(const w of [...watches.values()])finish(w,t,'captureEnd');resolve();
   }
 },INTERVAL);
});
const rows=done.map(w=>({id:w.id,slot:w.slot,type:w.type,startTimer:w.startTimer,entryTarget:w.entryTarget,active:!!w.firstAttack,leadToActiveMs:w.firstAttack?.rel??null,activeTarget:w.firstAttack?.target??null,targetSwitches:w.targetSwitches,firstAttack:w.firstAttack,nodes:w.nodes,endReason:w.endReason}));
const activeRows=rows.filter(r=>r.active),noActive=rows.filter(r=>!r.active),lastPreVals=activeRows.map(r=>r.firstAttack.lastPreToActiveMs).filter(v=>v!=null).sort((a,b)=>a-b);
const med=a=>a.length?a[Math.floor(a.length/2)]:null;
const candidates={};
for(const r of activeRows){const f=r.firstAttack;if(!f)continue;const key='T'+r.type+'|'+(f.lastPreDescriptor||'unresolved')+'|'+(f.lastPreD0==null?'chain':'D0='+f.lastPreD0);const c=(candidates[key]??={type:r.type,descriptor:f.lastPreDescriptor,d0:f.lastPreD0,source:f.lastPreSource,count:0,leadsToActive:[]});c.count++;if(f.lastPreToActiveMs!=null)c.leadsToActive.push(f.lastPreToActiveMs);}
for(const c of Object.values(candidates))c.leadsToActive.sort((a,b)=>a-b);
const out={version:'wof-d020-postchain-stage2-v5',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationRequestedMs:DURATION,intervalMs:INTERVAL,maxExact:MAX_EXACT,model:{stage1:'exact D0=20 entry = ATTACK_READY',stage2Search:'follow actual descriptor transitions after D0=20 and identify the last pre-active descriptor/state before enemy+0x70 becomes nonzero',resolution:'prefer type level2 roots D0=0..24; otherwise prove natural chain-next by parsing previous enemy+0x2C pointer and matching the resulting descriptor fingerprint'},totals:{exactEntries,completed:rows.length,active:activeRows.length,noActive:noActive.length,targetSwitchWatches:rows.filter(r=>r.targetSwitches.length).length},lastPreLeadSummary:{count:lastPreVals.length,minMs:lastPreVals[0]??null,medianMs:med(lastPreVals),maxMs:lastPreVals.length?lastPreVals[lastPreVals.length-1]:null,valuesMs:lastPreVals},stage2Candidates:Object.values(candidates),rows,note:'Read-only post-D0=20 chain tracing. The goal is to replace the sparse action-change Stage2 with a descriptor/state transition that occurs closer to active attack.'};
self.__WOF_D020_POSTCHAIN_STAGE2_V5=out;
console.log('=== D0=20 POSTCHAIN STAGE2 V5 JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_D020_POSTCHAIN_STAGE2_V5_ERROR',e);throw e;});