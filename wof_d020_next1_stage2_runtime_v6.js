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
  const d20ptr=r32(table+20)>>>0,d20=parseDescriptor(d20ptr);if(!d20)return {type,table,d20:null,next1:null,next2:null};
  const next1=parseDescriptor(d20.next);
  const next2=next1?parseDescriptor(next1.next):null;
  return {type,table,d20,next1,next2};
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
function snap(slot){
  const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;
  const frame=U32(a+0x12),next=U32(a+0x2C);if(frame===0&&next===0)return null;
  const target7E=U16(a+0x7E),tp=PLAYERS[target7E]||null,ptr=U16(a+0x6A),sp=LOW[ptr]||null,map=getMap(type);
  const s={slot,type,target7E,target:tp?.name||null,ptr6A:ptr,selectedPlayer:sp?.name||null,selected29:sp?B(sp.base+0x29):null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),timer34:U16(a+0x34),attack:U16(a+0x70),body:U16(a+0x6E),frameEnd12:frame,nextDesc2C:next,value30:U32(a+0x30)};
  s.inD20=descMatches(s,map?.d20);s.inNext1=descMatches(s,map?.next1);s.inNext2=descMatches(s,map?.next2);
  s.d20Exact=!!(s.inD20&&map?.d20&&s.timer34===map.d20.timer);
  return s;
}
function mini(s){return {target:s.target,ptr6A:hw(s.ptr6A),selected29:s.selected29,state99:s.state99,action2A:s.action2A,b2B:s.b2B,timer:s.timer34,attack:s.attack,body:s.body,frameEnd:h(s.frameEnd12,8),next:h(s.nextDesc2C,8),value30:h(s.value30,8)};}
const DURATION=75000,INTERVAL=20,MAX_EXACT=12,MAX_WATCH=1800,POST_ACTIVE=80,start=performance.now();
const prev=new Map(),active=new Map(),done=[];let seq=0,exactEntries=0;
function finish(w,t,reason){if(w.done)return;w.done=true;w.endAt=t;w.endReason=reason;done.push(w);active.delete(w.slot);}
function startWatch(s,t,map){
  const old=active.get(s.slot);if(old)finish(old,t,'retrigger');
  const w={id:++seq,slot:s.slot,type:s.type,entryAt:t,entryTarget:s.target,startTimer:map.d20.timer,d20:h(map.d20.at),next1:map.next1?{at:h(map.next1.at),timer:map.next1.timer,timerRaw:'0x'+map.next1.timerRaw.toString(16).toUpperCase().padStart(4,'0'),value30:h(map.next1.value30,8),next:h(map.next1.next)}:null,next2:map.next2?{at:h(map.next2.at),timer:map.next2.timer,value30:h(map.next2.value30,8),next:h(map.next2.next)}:null,next1Entry:null,next1Exit:null,next2Entry:null,firstAttack:null,targetSwitches:[],events:[{rel:0,kind:'D0_20_ENTRY',...mini(s)}],last:s,done:false};
  active.set(s.slot,w);exactEntries++;
}
function update(w,s,t){
  const rel=t-w.entryAt,p=w.last;
  if(s.type!==w.type){finish(w,t,'typeChanged');return;}
  if(s.target7E!==p.target7E){const e={rel,from:p.target,to:s.target,ptrFrom:hw(p.ptr6A),ptrTo:hw(s.ptr6A),action2A:s.action2A};w.targetSwitches.push(e);w.events.push({kind:'TARGET_SWITCH',...e});}
  if(!w.next1Entry&&!p.inNext1&&s.inNext1){w.next1Entry={rel,state:mini(s)};w.events.push({rel,kind:'NEXT1_ENTRY',...mini(s)});}
  if(w.next1Entry&&!w.next1Exit&&p.inNext1&&!s.inNext1){w.next1Exit={rel,lastTimer:p.timer34,state:mini(s)};w.events.push({rel,kind:'NEXT1_EXIT',...mini(s)});}
  if(!w.next2Entry&&!p.inNext2&&s.inNext2){w.next2Entry={rel,state:mini(s)};w.events.push({rel,kind:'NEXT2_ENTRY',...mini(s)});}
  if(!w.firstAttack&&p.attack===0&&s.attack!==0){
    w.firstAttack={rel,attack:s.attack,target:s.target,state:mini(s),next1ToActiveMs:w.next1Entry?rel-w.next1Entry.rel:null,next2ToActiveMs:w.next2Entry?rel-w.next2Entry.rel:null,activeBeforeNext1:!w.next1Entry};
    w.events.push({rel,kind:'ACTIVE_ATTACK_START',...mini(s)});
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
    const map=getMap(s.type);
    const entered=s.d20Exact&&(!p||!p.inD20);
    if(entered)startWatch(s,t,map);
    const w=active.get(i);if(w)update(w,s,t);
    prev.set(i,s);
  }
  if(t>=DURATION||(exactEntries>=MAX_EXACT&&active.size===0&&done.length>=MAX_EXACT)){
    clearInterval(id);for(const w of [...active.values()])finish(w,t,'captureEnd');resolve();
  }
 },INTERVAL);
});
const rows=done.map(w=>({id:w.id,slot:w.slot,type:w.type,startTimer:w.startTimer,d20:w.d20,next1:w.next1,next2:w.next2,entryTarget:w.entryTarget,active:!!w.firstAttack,leadToActiveMs:w.firstAttack?.rel??null,activeTarget:w.firstAttack?.target??null,targetSwitches:w.targetSwitches,next1Entered:!!w.next1Entry,next1EntryRel:w.next1Entry?.rel??null,next1Exit:w.next1Exit,next1ToActiveMs:w.firstAttack?.next1ToActiveMs??null,next2Entered:!!w.next2Entry,next2EntryRel:w.next2Entry?.rel??null,next2ToActiveMs:w.firstAttack?.next2ToActiveMs??null,activeBeforeNext1:!!w.firstAttack?.activeBeforeNext1,attack:w.firstAttack?.attack??0,events:w.events,endReason:w.endReason}));
const activeRows=rows.filter(r=>r.active),nextRows=activeRows.filter(r=>r.next1Entered&&r.next1ToActiveMs!=null),beforeRows=activeRows.filter(r=>r.activeBeforeNext1),vals=nextRows.map(r=>r.next1ToActiveMs).sort((a,b)=>a-b);const med=a=>a.length?a[Math.floor(a.length/2)]:null;
const byType={};for(const r of rows){const k='T'+r.type;(byType[k]??={entries:0,active:0,noActive:0,next1Entered:0,activeBeforeNext1:0,next1Leads:[],within100:0,targetSwitches:0,next1Static:r.next1});const b=byType[k];b.entries++;if(r.active)b.active++;else b.noActive++;if(r.next1Entered)b.next1Entered++;if(r.activeBeforeNext1)b.activeBeforeNext1++;if(r.next1ToActiveMs!=null){b.next1Leads.push(r.next1ToActiveMs);if(r.next1ToActiveMs<=100)b.within100++;}if(r.targetSwitches.length)b.targetSwitches++;}
for(const b of Object.values(byType))b.next1Leads.sort((a,b)=>a-b);
const out={version:'wof-d020-next1-stage2-runtime-v6',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationRequestedMs:DURATION,intervalMs:INTERVAL,maxExact:MAX_EXACT,model:{stage1:'exact D0=20 entry = ATTACK_READY',stage2Candidate:'enter the explicit descriptor pointed to by D0=20.next',question:'is D0=20.next a universal IMMINENT state, a per-type IMMINENT state, or can active preempt before next1?'},totals:{exactEntries,completed:rows.length,active:activeRows.length,noActive:rows.filter(r=>!r.active).length,next1Entered:rows.filter(r=>r.next1Entered).length,activeAfterNext1:nextRows.length,activeBeforeNext1:beforeRows.length,targetSwitchWatches:rows.filter(r=>r.targetSwitches.length).length},next1LeadSummary:{count:vals.length,minMs:vals[0]??null,medianMs:med(vals),maxMs:vals.length?vals[vals.length-1]:null,within100ms:vals.filter(v=>v<=100).length,valuesMs:vals},byType,rows,note:'Read-only validation of the explicit D0=20.next descriptor as Stage2. A universal rule is not assumed; results are grouped by enemy type and separately count attacks that start before next1 is ever entered.'};
self.__WOF_D020_NEXT1_STAGE2_RUNTIME_V6=out;
console.log('=== D0=20 NEXT1 STAGE2 RUNTIME V6 JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_D020_NEXT1_STAGE2_RUNTIME_V6_ERROR',e);throw e;});