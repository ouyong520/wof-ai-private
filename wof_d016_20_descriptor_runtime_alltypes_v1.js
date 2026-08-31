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
  d0_16Source:r16(0x6A10)===0x7010&&r16(0x6A12)===0x4EB8&&r16(0x6A14)===0x25C8,
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
  const table=r32(0x25DC+type*4)>>>0;
  if(!validRom(table))return null;
  const p16=r32(table+16)>>>0,p20=r32(table+20)>>>0;
  return {type,table,d16:parseDescriptor(p16),d20:parseDescriptor(p20)};
}

const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS={0xBE1C:{name:'P1',base:0xFFBE1C},0xBEFC:{name:'P2',base:0xFFBEFC},0xBFDC:{name:'P3',base:0xFFBFDC}};
const maps=new Map();
function getMap(type){if(!maps.has(type))maps.set(type,typeMap(type));return maps.get(type);}
function matchDesc(a,d,label){
  if(!d)return null;
  const frame=U32(a+0x12),v30=U32(a+0x30),next=U32(a+0x2C),timer=U16(a+0x34);
  if(frame!==d.frameEnd||v30!==d.value30||next!==d.next)return null;
  if(d.timer!==0&&timer>d.timer)return null;
  return {label,descriptor:h(d.at),startTimer:d.timer,timerNow:timer,frameEnd:h(d.frameEnd),next:h(d.next)};
}
function snap(slot){
  const a=ENEMY+slot*STRIDE,type=U16(a+0x20);
  if(type>=47)return null;
  const x=U32(a+4),frame=U32(a+0x12),next=U32(a+0x2C);
  if(x===0&&frame===0&&next===0)return null;
  const map=getMap(type),ptr=U16(a+0x6A),pl=PLAYERS[ptr]||null;
  const d20=map?matchDesc(a,map.d20,'D0=20'):null,d16=map?matchDesc(a,map.d16,'D0=16'):null;
  const phase=d20||d16;
  return {slot,base:h(a,8),type,target7E:U16(a+0x7E),ptr6A:hw(ptr),selectedPlayer:pl?.name||null,selectedPlayer29:pl?B(pl.base+0x29):null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),frameEnd12:h(frame,8),nextDesc2C:h(next,8),value30:h(U32(a+0x30),8),timer34:U16(a+0x34),payload6C:hw(U16(a+0x6C)),payload6E:h(U32(a+0x6E),8),phase};
}
function sig(s){return [s.type,s.target7E,s.ptr6A,s.selectedPlayer29,s.state99,s.action2A,s.b2B,s.frameEnd12,s.nextDesc2C,s.value30,s.payload6C,s.payload6E,s.phase?.label||'',s.phase?.descriptor||''].join('|');}
const DURATION=15000,INTERVAL=20,start=performance.now(),events=[],last=new Map(),typeCounts=new Map(),phaseCounts={'D0=16':0,'D0=20':0};
await new Promise(resolve=>{
 const id=setInterval(()=>{
   const t=Math.round(performance.now()-start);
   for(let i=0;i<SLOTS;i++){
     const s=snap(i);if(!s)continue;
     typeCounts.set(s.type,(typeCounts.get(s.type)||0)+1);
     const k=sig(s),prev=last.get(i);
     if(!prev||prev.k!==k){
       const ev={t,...s};events.push(ev);last.set(i,{k,s});
       if(s.phase)phaseCounts[s.phase.label]++;
       if(events.length>360)events.shift();
     }else{
       // preserve exact descriptor-entry timer when sampled without flooding every countdown tick
       if(s.phase&&s.timer34===s.phase.startTimer&&prev.s.timer34!==s.timer34){
         events.push({t,...s,entryTimerExact:true});if(events.length>360)events.shift();
       }
       last.set(i,{k,s});
     }
   }
   if(t>=DURATION){clearInterval(id);resolve();}
 },INTERVAL);
});
const mapOut=[...maps.entries()].filter(([,m])=>m).map(([type,m])=>({type,table:h(m.table),d0_16:m.d16?{descriptor:h(m.d16.at),frameEnd:h(m.d16.frameEnd),timer:m.d16.timer,next:h(m.d16.next)}:null,d0_20:m.d20?{descriptor:h(m.d20.at),frameEnd:h(m.d20.frameEnd),timer:m.d20.timer,next:h(m.d20.next)}:null}));
const out={version:'wof-d016-20-descriptor-runtime-alltypes-v1',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationMs:DURATION,intervalMs:INTERVAL,observedTypes:[...typeCounts.entries()].sort((a,b)=>a[0]-b[0]).map(([type,samples])=>({type,samples})),typeMaps:mapOut,phaseCounts,eventCount:events.length,events,note:'All-type runtime correlation. D0=16/20 descriptor fingerprints are derived from each observed enemy type table; events are emitted on semantic state/descriptor changes, not every timer decrement.'};
self.__WOF_D016_20_DESCRIPTOR_RUNTIME_ALLTYPES_V1=out;
console.log('=== D0 16/20 DESCRIPTOR RUNTIME ALLTYPES V1 JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_D016_20_DESCRIPTOR_RUNTIME_ALLTYPES_V1_ERROR',e);throw e;});