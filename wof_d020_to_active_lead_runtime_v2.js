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
  flaggedNext:r16(0x249E)===0x0241&&r16(0x24A0)===0x7FFF&&r16(0x24A6)===0x2854&&r16(0x24A8)===0x214C,
  d0_20Source:r16(0x6A62)===0x7014&&r16(0x6A64)===0x4EB8&&r16(0x6A66)===0x25C8,
  attackFieldBaseline:true
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
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS={
  0:{name:'P1',base:0xFFBE1C,low:0xBE1C},
  4:{name:'P2',base:0xFFBEFC,low:0xBEFC},
  8:{name:'P3',base:0xFFBFDC,low:0xBFDC}
};
const LOW={0xBE1C:PLAYERS[0],0xBEFC:PLAYERS[4],0xBFDC:PLAYERS[8]};
const maps=new Map();
const getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
function phase20(a,d){
  if(!d)return null;
  const frame=U32(a+0x12),v30=U32(a+0x30),next=U32(a+0x2C),timer=U16(a+0x34);
  if(frame!==d.frameEnd||v30!==d.value30||next!==d.next||timer>d.timer)return null;
  return {descriptor:d.at,frameEnd:d.frameEnd,next:d.next,startTimer:d.timer,timerNow:timer,exactStart:timer===d.timer};
}
function hpSnap(){return {P1:B(0xFFBE1C+0x83),P2:B(0xFFBEFC+0x83),P3:B(0xFFBFDC+0x83)};}
function snap(slot){
  const a=ENEMY+slot*STRIDE,type=U16(a+0x20);
  if(type>=47)return null;
  const frame=U32(a+0x12),next=U32(a+0x2C),x=S32(a+4),y=S32(a+8),z=S32(a+0x0C);
  if(x===0&&frame===0&&next===0)return null;
  const map=getMap(type),p20=phase20(a,map?.d20||null),ptr=U16(a+0x6A),pl=LOW[ptr]||null,target=U16(a+0x7E),tp=PLAYERS[target]||null;
  return {
    slot,base:a,type,target7E:target,targetName:tp?.name||null,ptr6A:ptr,selectedPlayer:pl?.name||null,
    selectedPlayer29:pl?B(pl.base+0x29):null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),
    frameEnd12:frame,nextDesc2C:next,value30:U32(a+0x30),timer34:U16(a+0x34),
    body:U16(a+0x6E),attack:U16(a+0x70),x,y,z,phase20:p20
  };
}
function mini(s){return {
  target:s.targetName,target7E:s.target7E,ptr6A:hw(s.ptr6A),selectedPlayer:s.selectedPlayer,selectedPlayer29:s.selectedPlayer29,
  state99:s.state99,action2A:s.action2A,b2B:s.b2B,attack:s.attack,body:s.body,
  frameEnd12:h(s.frameEnd12,8),nextDesc2C:h(s.nextDesc2C,8),value30:h(s.value30,8),timer34:s.timer34,
  x:+(s.x/65536).toFixed(2),y:+(s.y/65536).toFixed(2),z:+(s.z/65536).toFixed(2)
};}
function semSig(s){return [s.target7E,s.ptr6A,s.selectedPlayer29,s.state99,s.action2A,s.b2B,s.attack,s.body,s.frameEnd12,s.nextDesc2C,s.value30,s.phase20?1:0].join('|');}
const DURATION=20000,INTERVAL=20,MAX_WATCH=1800,POST_ACTIVE=400,start=performance.now();
const activeWatches=new Map(),completed=[],prevSlot=new Map();
let prevHP=hpSnap(),watchSeq=0,totalPhaseSamples=0,exactEntries=0,midPhaseStarts=0;
function finish(w,t,reason){
  if(w.done)return;w.done=true;w.endAt=t;w.durationMs=t-w.entryAt;w.endReason=reason;
  if(w.firstAttack)w.leadToActiveMs=w.firstAttack.rel;
  completed.push(w);if(completed.length>40)completed.shift();activeWatches.delete(w.slot);
}
function startWatch(s,t,mid){
  const old=activeWatches.get(s.slot);if(old)finish(old,t,'retrigger');
  const w={id:++watchSeq,slot:s.slot,type:s.type,descriptor:h(s.phase20.descriptor),entryAt:t,exactEntry:!mid,midPhase:!!mid,startTimer:s.phase20.startTimer,timerAtEntry:s.timer34,
    entry:mini(s),attackAtEntry:s.attack,targetAtEntry:s.targetName,selectedPlayerAtEntry:s.selectedPlayer,selectedPlayer29AtEntry:s.selectedPlayer29,
    firstAttack:null,phaseExit:null,targetSwitches:[],selected29Changes:[],actionChanges:[],hpDrops:[],timeline:[{rel:0,kind:mid?'MID_PHASE_START':'D0_20_ENTRY',...mini(s)}],lastSig:semSig(s),last:s,done:false};
  activeWatches.set(s.slot,w);if(mid)midPhaseStarts++;else exactEntries++;
}
function updateWatch(w,s,t,hp){
  const rel=t-w.entryAt,prev=w.last;
  if(s.type!==w.type){finish(w,t,'typeChanged');return;}
  if(!w.phaseExit&&!s.phase20&&prev.phase20){w.phaseExit={rel,state:mini(s)};w.timeline.push({rel,kind:'D0_20_EXIT',...mini(s)});}
  if(s.target7E!==prev.target7E){const e={rel,from:prev.targetName,to:s.targetName,ptrFrom:hw(prev.ptr6A),ptrTo:hw(s.ptr6A),selectedPlayer29:s.selectedPlayer29,action2A:s.action2A};w.targetSwitches.push(e);w.timeline.push({rel,kind:'TARGET_SWITCH',...e,...mini(s)});}
  if(s.selectedPlayer29!==prev.selectedPlayer29){const e={rel,from:prev.selectedPlayer29,to:s.selectedPlayer29,target:s.targetName,action2A:s.action2A};w.selected29Changes.push(e);w.timeline.push({rel,kind:'SELECTED29_CHANGE',...e,...mini(s)});}
  if(s.action2A!==prev.action2A){const e={rel,from:prev.action2A,to:s.action2A,target:s.targetName,selectedPlayer29:s.selectedPlayer29};w.actionChanges.push(e);w.timeline.push({rel,kind:'ACTION2A_CHANGE',...e,...mini(s)});}
  if(!w.firstAttack&&prev.attack===0&&s.attack!==0){w.firstAttack={rel,attack:s.attack,target:s.targetName,selectedPlayer:s.selectedPlayer,selectedPlayer29:s.selectedPlayer29,state:mini(s)};w.timeline.push({rel,kind:'ACTIVE_ATTACK_START',...mini(s)});}
  const sig=semSig(s);if(sig!==w.lastSig&&w.timeline.length<80){w.lastSig=sig;}
  w.last=s;
  if(rel>=MAX_WATCH)finish(w,t,'timeout');
  else if(w.firstAttack&&rel>=w.firstAttack.rel+POST_ACTIVE)finish(w,t,'activeFollowupComplete');
}
await new Promise(resolve=>{
  const id=setInterval(()=>{
    const t=Math.round(performance.now()-start),hp=hpSnap();
    const drops=[];for(const p of ['P1','P2','P3'])if(hp[p]<prevHP[p])drops.push({player:p,from:prevHP[p],to:hp[p],delta:prevHP[p]-hp[p]});
    for(let i=0;i<SLOTS;i++){
      const s=snap(i),prev=prevSlot.get(i)||null;
      if(!s){const w=activeWatches.get(i);if(w)finish(w,t,'slotGone');prevSlot.delete(i);continue;}
      if(s.phase20)totalPhaseSamples++;
      const entered=s.phase20&&(!prev||!prev.phase20||prev.phase20.descriptor!==s.phase20.descriptor);
      if(entered){const mid=!s.phase20.exactStart;startWatch(s,t,mid);}
      const w=activeWatches.get(i);if(w)updateWatch(w,s,t,hp);
      prevSlot.set(i,s);
    }
    if(drops.length){for(const w of activeWatches.values())for(const d of drops){const e={rel:t-w.entryAt,...d,currentTarget:w.last?.targetName||null,targetMatch:(w.last?.targetName===d.player)};w.hpDrops.push(e);w.timeline.push({kind:'HP_DROP',...e});}}
    prevHP=hp;
    if(t>=DURATION){clearInterval(id);for(const w of [...activeWatches.values()])finish(w,t,'captureEnd');resolve();}
  },INTERVAL);
});
const exact=completed.filter(w=>w.exactEntry),leadRows=exact.filter(w=>w.attackAtEntry===0&&w.firstAttack).map(w=>({id:w.id,slot:w.slot,type:w.type,leadMs:w.leadToActiveMs,targetAtEntry:w.targetAtEntry,targetAtActive:w.firstAttack.target,targetSwitched:w.targetSwitches.length>0,selected29AtEntry:w.selectedPlayer29AtEntry,selected29AtActive:w.firstAttack.selectedPlayer29,attack:w.firstAttack.attack}));
const nums=leadRows.map(x=>x.leadMs).sort((a,b)=>a-b),med=nums.length?nums[Math.floor(nums.length/2)]:null;
const byType={};for(const w of exact){const k='T'+w.type;(byType[k]??={entries:0,activeLeads:[],targetSwitchDuringWatch:0,hpDrops:0});byType[k].entries++;if(w.firstAttack&&w.attackAtEntry===0)byType[k].activeLeads.push(w.leadToActiveMs);if(w.targetSwitches.length)byType[k].targetSwitchDuringWatch++;byType[k].hpDrops+=w.hpDrops.length;}
const out={version:'wof-d020-to-active-lead-runtime-v2',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationMs:DURATION,intervalMs:INTERVAL,watchWindowMs:MAX_WATCH,
  attackField:'enemy+0x70 U16; active start = 0 -> nonzero (same convention as prior Future AI)',
  totals:{totalPhaseSamples,exactEntries,midPhaseStarts,completedWatches:completed.length,exactWatches:exact.length,activeLeadCount:leadRows.length,targetSwitchWatches:exact.filter(w=>w.targetSwitches.length).length,hpDropWatches:exact.filter(w=>w.hpDrops.length).length},
  leadSummary:{minMs:nums.length?nums[0]:null,medianMs:med,maxMs:nums.length?nums[nums.length-1]:null,valuesMs:nums},byType,leadRows,watches:completed,
  note:'Measures exact D0=20 descriptor entry to enemy+0x70 active attack start. Target/action/selected-player state is tracked independently because AI target selection can change while a descriptor is already playing.'};
self.__WOF_D020_TO_ACTIVE_LEAD_RUNTIME_V2=out;
console.log('=== D0=20 TO ACTIVE LEAD RUNTIME V2 JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_D020_TO_ACTIVE_LEAD_RUNTIME_V2_ERROR',e);throw e;});