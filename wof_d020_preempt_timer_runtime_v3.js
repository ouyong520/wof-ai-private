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
const h=(x,n=6)=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(n,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const validRom=v=>v>=0x2000&&v<ROMMAX&&(v&1)===0;
const gate={
  dispatcher25C8:r16(0x25C8)===0x3228&&r16(0x25CA)===0x0020&&r16(0x25D0)===0x287B&&r16(0x25D4)===0x2874,
  handoff247C:r16(0x247C)===0x2C5C&&r16(0x247E)===0x215C&&r16(0x2480)===0x0030&&r16(0x2482)===0x321C,
  d0_20Source:r16(0x6A62)===0x7014&&r16(0x6A64)===0x4EB8&&r16(0x6A66)===0x25C8
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
  return {type,table,d20:parseDescriptor(r32(table+20)>>>0)};
}
const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS={0:{name:'P1',base:0xFFBE1C,low:0xBE1C},4:{name:'P2',base:0xFFBEFC,low:0xBEFC},8:{name:'P3',base:0xFFBFDC,low:0xBFDC}};
const LOW={0xBE1C:PLAYERS[0],0xBEFC:PLAYERS[4],0xBFDC:PLAYERS[8]};
const maps=new Map(),getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
function phase20(a,d){
  if(!d)return null;
  const frame=U32(a+0x12),v30=U32(a+0x30),next=U32(a+0x2C),timer=U16(a+0x34);
  if(frame!==d.frameEnd||v30!==d.value30||next!==d.next||timer>d.timer)return null;
  return {descriptor:d.at,startTimer:d.timer,timerNow:timer,exactStart:timer===d.timer,frameEnd:d.frameEnd,next:d.next};
}
function snap(slot){
  const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;
  const frame=U32(a+0x12),next=U32(a+0x2C),x=S32(a+4),y=S32(a+8),z=S32(a+0x0C);
  if(x===0&&frame===0&&next===0)return null;
  const map=getMap(type),p20=phase20(a,map?.d20||null),target=U16(a+0x7E),tp=PLAYERS[target]||null,ptr=U16(a+0x6A),sp=LOW[ptr]||null;
  return {slot,type,target7E:target,targetName:tp?.name||null,ptr6A:ptr,selectedPlayer:sp?.name||null,selectedPlayer29:sp?B(sp.base+0x29):null,
    state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),attack:U16(a+0x70),body:U16(a+0x6E),timer34:U16(a+0x34),
    frameEnd12:frame,nextDesc2C:next,value30:U32(a+0x30),x,y,z,phase20:p20};
}
function mini(s){return {target:s.targetName,target7E:s.target7E,ptr6A:hw(s.ptr6A),selectedPlayer:s.selectedPlayer,selectedPlayer29:s.selectedPlayer29,
  state99:s.state99,action2A:s.action2A,b2B:s.b2B,attack:s.attack,body:s.body,timer34:s.timer34,
  frameEnd12:h(s.frameEnd12,8),nextDesc2C:h(s.nextDesc2C,8),value30:h(s.value30,8),x:+(s.x/65536).toFixed(2),y:+(s.y/65536).toFixed(2),z:+(s.z/65536).toFixed(2)};}
const DURATION=45000,INTERVAL=20,MAX_EXACT=12,MAX_WATCH=1200,POST_ACTIVE=120;
const start=performance.now(),prevSlot=new Map(),watches=new Map(),completed=[];let seq=0,exactEntries=0;
function classify(w){
  const active=!!w.firstAttack,phaseExit=!!w.phaseExit,lastTimer=w.lastPhaseTimer;
  if(!active)return phaseExit?'phase-exit-no-active':'no-active';
  const preAction=w.actionChanges.some(e=>e.rel<w.firstAttack.rel);
  const preTarget=w.targetSwitches.some(e=>e.rel<w.firstAttack.rel);
  const nearNatural=(lastTimer!=null&&lastTimer<=2)||Math.abs(w.firstAttack.rel-w.expectedNaturalMs)<=40;
  if(preTarget&&!nearNatural)return 'target-switch-preempt';
  if(preAction&&!nearNatural)return 'early-action-preempt';
  if(!nearNatural)return 'early-other-preempt';
  return 'natural-expire';
}
function finish(w,t,reason){
  if(w.done)return;w.done=true;w.endAt=t;w.endReason=reason;w.durationMs=t-w.entryAt;w.classification=classify(w);
  if(w.firstAttack){w.leadToActiveMs=w.firstAttack.rel;w.leadRatio=+(w.firstAttack.rel/w.expectedNaturalMs).toFixed(3);}
  completed.push(w);watches.delete(w.slot);
}
function startWatch(s,t){
  const old=watches.get(s.slot);if(old)finish(old,t,'retrigger');
  const st=s.phase20.startTimer;
  const w={id:++seq,slot:s.slot,type:s.type,descriptor:h(s.phase20.descriptor),entryAt:t,startTimer:st,expectedNaturalMs:+(st*1000/60).toFixed(1),
    entry:mini(s),targetAtEntry:s.targetName,selected29AtEntry:s.selectedPlayer29,actionAtEntry:s.action2A,
    timerTrace:[{rel:0,timer:s.timer34,action2A:s.action2A,target:s.targetName,attack:s.attack}],lastTimer:s.timer34,lastPhaseTimer:s.timer34,
    targetSwitches:[],selected29Changes:[],actionChanges:[],firstAttack:null,phaseExit:null,last:s,done:false};
  watches.set(s.slot,w);exactEntries++;
}
function updateWatch(w,s,t){
  const rel=t-w.entryAt,prev=w.last;if(s.type!==w.type){finish(w,t,'typeChanged');return;}
  if(s.phase20){w.lastPhaseTimer=s.timer34;if(s.timer34!==w.lastTimer){w.timerTrace.push({rel,timer:s.timer34,action2A:s.action2A,target:s.targetName,attack:s.attack});w.lastTimer=s.timer34;}}
  if(!w.phaseExit&&!s.phase20&&prev.phase20)w.phaseExit={rel,lastTimerBeforeExit:prev.timer34,state:mini(s)};
  if(s.target7E!==prev.target7E)w.targetSwitches.push({rel,from:prev.targetName,to:s.targetName,ptrFrom:hw(prev.ptr6A),ptrTo:hw(s.ptr6A),selected29:s.selectedPlayer29,action2A:s.action2A});
  if(s.selectedPlayer29!==prev.selectedPlayer29)w.selected29Changes.push({rel,from:prev.selectedPlayer29,to:s.selectedPlayer29,target:s.targetName,action2A:s.action2A});
  if(s.action2A!==prev.action2A)w.actionChanges.push({rel,from:prev.action2A,to:s.action2A,target:s.targetName,selected29:s.selectedPlayer29,timer:s.timer34});
  if(!w.firstAttack&&prev.attack===0&&s.attack!==0)w.firstAttack={rel,attack:s.attack,target:s.targetName,selectedPlayer:s.selectedPlayer,selected29:s.selectedPlayer29,action2A:s.action2A,lastTimerBeforeActive:prev.timer34,state:mini(s)};
  w.last=s;
  if(rel>=MAX_WATCH)finish(w,t,'timeout');
  else if(w.firstAttack&&rel>=w.firstAttack.rel+POST_ACTIVE)finish(w,t,'activeCaptured');
}
await new Promise(resolve=>{
  const id=setInterval(()=>{
    const t=Math.round(performance.now()-start);
    for(let i=0;i<SLOTS;i++){
      const s=snap(i),prev=prevSlot.get(i)||null;
      if(!s){const w=watches.get(i);if(w)finish(w,t,'slotGone');prevSlot.delete(i);continue;}
      const entered=s.phase20?.exactStart&&(!prev?.phase20||prev.phase20.descriptor!==s.phase20.descriptor);
      if(entered)startWatch(s,t);
      const w=watches.get(i);if(w)updateWatch(w,s,t);
      prevSlot.set(i,s);
    }
    const doneExact=completed.filter(w=>w.firstAttack||w.phaseExit).length;
    if(t>=DURATION||(doneExact>=MAX_EXACT&&t>=10000)){
      clearInterval(id);for(const w of [...watches.values()])finish(w,t,'captureEnd');resolve();
    }
  },INTERVAL);
});
const useful=completed.filter(w=>w.firstAttack),leads=useful.map(w=>w.leadToActiveMs).sort((a,b)=>a-b);
const classes={};for(const w of completed)classes[w.classification]=(classes[w.classification]||0)+1;
const byType={};for(const w of completed){const k='T'+w.type;(byType[k]??={entries:0,active:0,leads:[],classes:{}});const b=byType[k];b.entries++;if(w.firstAttack){b.active++;b.leads.push(w.leadToActiveMs);}b.classes[w.classification]=(b.classes[w.classification]||0)+1;}
const rows=completed.map(w=>({id:w.id,slot:w.slot,type:w.type,startTimer:w.startTimer,expectedNaturalMs:w.expectedNaturalMs,leadToActiveMs:w.leadToActiveMs??null,leadRatio:w.leadRatio??null,
  classification:w.classification,lastPhaseTimer:w.lastPhaseTimer,phaseExit:w.phaseExit?{rel:w.phaseExit.rel,lastTimerBeforeExit:w.phaseExit.lastTimerBeforeExit}:null,
  targetAtEntry:w.targetAtEntry,targetAtActive:w.firstAttack?.target||null,actionAtEntry:w.actionAtEntry,actionAtActive:w.firstAttack?.action2A??null,attack:w.firstAttack?.attack||0,
  targetSwitches:w.targetSwitches,selected29Changes:w.selected29Changes,actionChanges:w.actionChanges,timerTrace:w.timerTrace}));
const out={version:'wof-d020-preempt-timer-runtime-v3',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationRequestedMs:DURATION,intervalMs:INTERVAL,maxExact:MAX_EXACT,
  totals:{exactEntries,completed:completed.length,active:useful.length,classes},
  leadSummary:{count:leads.length,minMs:leads[0]??null,medianMs:leads.length?leads[Math.floor(leads.length/2)]:null,maxMs:leads.length?leads[leads.length-1]:null,valuesMs:leads},
  byType,rows,note:'Classifies D0=20 -> active transitions as natural-expire vs early preemption using the last observed descriptor timer plus action/target changes. No RAM writes.'};
self.__WOF_D020_PREEMPT_TIMER_RUNTIME_V3=out;
console.log('=== D0=20 PREEMPT TIMER RUNTIME V3 JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_D020_PREEMPT_TIMER_RUNTIME_V3_ERROR',e);throw e;});