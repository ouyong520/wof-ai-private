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
  const p20=r32(table+20)>>>0;
  return {type,table,d20:parseDescriptor(p20)};
}
const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS={0:{name:'P1',base:0xFFBE1C,low:0xBE1C},4:{name:'P2',base:0xFFBEFC,low:0xBEFC},8:{name:'P3',base:0xFFBFDC,low:0xBFDC}};
const LOW={0xBE1C:PLAYERS[0],0xBEFC:PLAYERS[4],0xBFDC:PLAYERS[8]};
const maps=new Map();const getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
function phase20(a,d){
  if(!d)return null;
  const frame=U32(a+0x12),v30=U32(a+0x30),next=U32(a+0x2C),timer=U16(a+0x34);
  if(frame!==d.frameEnd||v30!==d.value30||next!==d.next||timer>d.timer)return null;
  return {descriptor:d.at,frameEnd:d.frameEnd,next:d.next,startTimer:d.timer,timerNow:timer,exactStart:timer===d.timer};
}
function snap(slot){
  const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;
  const frame=U32(a+0x12),next=U32(a+0x2C);if(frame===0&&next===0)return null;
  const map=getMap(type),p20=phase20(a,map?.d20||null),target7E=U16(a+0x7E),tp=PLAYERS[target7E]||null,ptr=U16(a+0x6A),sp=LOW[ptr]||null;
  return {slot,type,target7E,target:tp?.name||null,ptr6A:ptr,selectedPlayer:sp?.name||null,selected29:sp?B(sp.base+0x29):null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),timer34:U16(a+0x34),attack:U16(a+0x70),body:U16(a+0x6E),frameEnd12:frame,nextDesc2C:next,phase20:p20};
}
const DURATION=60000,INTERVAL=20,MAX_EXACT=12,MAX_WATCH=1000,POST_ACTIVE=120,start=performance.now();
const prev=new Map(),active=new Map(),done=[];let seq=0,exactEntries=0;
function finish(w,t,reason){if(w.done)return;w.done=true;w.endAt=t;w.endReason=reason;done.push(w);active.delete(w.slot);}
function startWatch(s,t){
  const old=active.get(s.slot);if(old)finish(old,t,'retrigger');
  const w={id:++seq,slot:s.slot,type:s.type,descriptor:h(s.phase20.descriptor),entryAt:t,startTimer:s.phase20.startTimer,expectedNaturalMs:+(s.phase20.startTimer*1000/60).toFixed(1),entryTarget:s.target,entryAction:s.action2A,entrySelected29:s.selected29,entryPtr6A:hw(s.ptr6A),stage2:null,targetSwitches:[],selected29Changes:[],firstAttack:null,phaseExit:null,last:s,done:false};
  active.set(s.slot,w);exactEntries++;
}
function update(w,s,t){
  const rel=t-w.entryAt,p=w.last;
  if(s.type!==w.type){finish(w,t,'typeChanged');return;}
  if(!w.phaseExit&&p.phase20&&!s.phase20)w.phaseExit={rel,lastTimer:p.timer34};
  if(s.target7E!==p.target7E)w.targetSwitches.push({rel,from:p.target,to:s.target,ptrFrom:hw(p.ptr6A),ptrTo:hw(s.ptr6A),action2A:s.action2A,timer:s.timer34});
  if(s.selected29!==p.selected29)w.selected29Changes.push({rel,from:p.selected29,to:s.selected29,target:s.target,action2A:s.action2A,timer:s.timer34});
  if(!w.stage2&&p.attack===0&&s.attack===0&&p.action2A!==s.action2A&&p.phase20){
    const early=(p.timer34>2);
    if(early)w.stage2={rel,from:p.action2A,to:s.action2A,timer:p.timer34,target:s.target,selected29:s.selected29};
  }
  if(!w.firstAttack&&p.attack===0&&s.attack!==0){
    w.firstAttack={rel,attack:s.attack,target:s.target,action2A:s.action2A,selected29:s.selected29,timerBefore:p.timer34,stage2ToActiveMs:w.stage2?rel-w.stage2.rel:null};
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
    const entered=s.phase20&&s.phase20.exactStart&&(!p||!p.phase20||p.phase20.descriptor!==s.phase20.descriptor);
    if(entered)startWatch(s,t);
    const w=active.get(i);if(w)update(w,s,t);
    prev.set(i,s);
  }
  const completedExact=done.length;
  if(t>=DURATION||(exactEntries>=MAX_EXACT&&active.size===0&&completedExact>=MAX_EXACT)){
    clearInterval(id);for(const w of [...active.values()])finish(w,t,'captureEnd');resolve();
  }
 },INTERVAL);
});
const rows=done.map(w=>({id:w.id,slot:w.slot,type:w.type,startTimer:w.startTimer,expectedNaturalMs:w.expectedNaturalMs,active:!!w.firstAttack,leadToActiveMs:w.firstAttack?.rel??null,entryTarget:w.entryTarget,activeTarget:w.firstAttack?.target??null,entryTargetCorrect:w.firstAttack? w.entryTarget===w.firstAttack.target:null,targetSwitches:w.targetSwitches,stage2:w.stage2,stage2ToActiveMs:w.firstAttack?.stage2ToActiveMs??null,attack:w.firstAttack?.attack??0,phaseExit:w.phaseExit,endReason:w.endReason}));
const activeRows=rows.filter(r=>r.active),stage2Rows=activeRows.filter(r=>r.stage2&&r.stage2ToActiveMs!=null),leadVals=activeRows.map(r=>r.leadToActiveMs).sort((a,b)=>a-b),s2Vals=stage2Rows.map(r=>r.stage2ToActiveMs).sort((a,b)=>a-b);
const med=a=>a.length?a[Math.floor(a.length/2)]:null;
const byType={};for(const r of rows){const k='T'+r.type;(byType[k]??={entries:0,active:0,noActive:0,leads:[],stage2:0,targetSwitches:0});byType[k].entries++;if(r.active){byType[k].active++;byType[k].leads.push(r.leadToActiveMs);}else byType[k].noActive++;if(r.stage2)byType[k].stage2++;if(r.targetSwitches.length)byType[k].targetSwitches++;}
const out={version:'wof-d020-two-stage-shadow-v4',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationRequestedMs:DURATION,intervalMs:INTERVAL,maxExact:MAX_EXACT,model:{stage1:'exact D0=20 entry = ATTACK_READY early warning',stage2:'action2A changes early while still D0=20 and attack==0 = IMMINENT escalation',targetPolicy:'use live enemy+0x7E/+0x6A target; retarget warning immediately if target switches'},totals:{exactEntries,completed:rows.length,active:activeRows.length,noActive:rows.filter(r=>!r.active).length,stage2Triggered:rows.filter(r=>r.stage2).length,targetSwitchWatches:rows.filter(r=>r.targetSwitches.length).length,entryTargetCorrect:activeRows.filter(r=>r.entryTargetCorrect).length},leadSummary:{count:leadVals.length,minMs:leadVals[0]??null,medianMs:med(leadVals),maxMs:leadVals.length?leadVals[leadVals.length-1]:null,valuesMs:leadVals},stage2Summary:{count:s2Vals.length,minMs:s2Vals[0]??null,medianMs:med(s2Vals),maxMs:s2Vals.length?s2Vals[s2Vals.length-1]:null,valuesMs:s2Vals},byType,rows,note:'Shadow validation only. No RAM writes. Intended to test whether D0=20 is a low-false-positive early warning and whether an early action2A transition provides a stronger imminent-active signal.'};
self.__WOF_D020_TWO_STAGE_SHADOW_V4=out;
console.log('=== D0=20 TWO-STAGE SHADOW V4 JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_D020_TWO_STAGE_SHADOW_V4_ERROR',e);throw e;});