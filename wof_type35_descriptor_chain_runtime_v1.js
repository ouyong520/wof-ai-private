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

// Exact 68000 semantics from known instruction boundary 0x247C.
const handoffGate={
  moveaFrameEnd:r16(0x247C)===0x2C5C,
  moveLong30:r16(0x247E)===0x215C&&r16(0x2480)===0x0030,
  moveWordTimer:r16(0x2482)===0x321C,
  bmi:r16(0x2484)===0x6B00&&r16(0x2486)===0x0018,
  storeTimerNormal:r16(0x2488)===0x3141&&r16(0x248A)===0x0034,
  storeNextNormal:r16(0x248C)===0x214C&&r16(0x248E)===0x002C,
  storeFrameEnd:r16(0x2490)===0x214E&&r16(0x2492)===0x0012,
  copyPayload:r16(0x2494)===0x49E8&&r16(0x2496)===0x006C&&r16(0x2498)===0x38E6&&r16(0x249A)===0x28E6,
  maskTimerFlag:r16(0x249E)===0x0241&&r16(0x24A0)===0x7FFF,
  storeTimerFlagged:r16(0x24A2)===0x3141&&r16(0x24A4)===0x0034,
  loadExplicitNext:r16(0x24A6)===0x2854,
  storeExplicitNext:r16(0x24A8)===0x214C&&r16(0x24AA)===0x002C
};

function parseDescriptor(at){
  if(!validRom(at)||at+14>ROMMAX)return {at:h(at),valid:false};
  const frameEnd=r32(at)>>>0;
  const value30=r32(at+4)>>>0;
  const timerRaw=r16(at+8)>>>0;
  const flagged=!!(timerRaw&0x8000);
  const timer=flagged?(timerRaw&0x7fff):timerRaw;
  const next=flagged?(r32(at+10)>>>0):((at+10)>>>0);
  const recLen=flagged?14:10;
  const payload=(validRom(frameEnd)&&frameEnd>=6)?{
    sourceRange:h(frameEnd-6)+'..'+h(frameEnd-1),
    toEnemy6CWord:hw(r16(frameEnd-2)),
    toEnemy6ELong:h(r32(frameEnd-6),8)
  }:null;
  return {at:h(at),valid:true,frameEnd:h(frameEnd),value30:h(value30,8),timerRaw:hw(timerRaw),flagged,timer,next:h(next),nextKind:flagged?'explicit-pointer':'inline',recordLen:recLen,payload};
}
function chain(start,max=12){
  const out=[],seen=new Set();let p=start>>>0;
  for(let i=0;i<max;i++){
    if(seen.has(p)){out.push({at:h(p),loop:true});break;}
    seen.add(p);
    const d=parseDescriptor(p);out.push(d);
    if(!d.valid)break;
    const n=parseInt(d.next,16)>>>0;
    if(!validRom(n)){out.push({at:h(n),invalidNext:true});break;}
    p=n;
  }
  return out;
}
const staticProof={
  d0_20:parseDescriptor(0x81856),
  d0_16:parseDescriptor(0x81864),
  d0_20_chain:chain(0x81856),
  d0_16_chain:chain(0x81864)
};

// Live RAM: transition-only capture for any active type35 object.
const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
function snap(slot){
  const a=ENEMY+slot*STRIDE;
  const type=U16(a+0x20);
  if(type!==35)return null;
  const s={slot,base:h(a,8),type,target7E:U16(a+0x7E),ptr6A:hw(U16(a+0x6A)),state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),frameEnd12:h(U32(a+0x12),8),nextDesc2C:h(U32(a+0x2C),8),value30:h(U32(a+0x30),8),timer34:U16(a+0x34),callback64:h(U32(a+0x64),8),payload6C:hw(U16(a+0x6C)),payload6E:h(U32(a+0x6E),8)};
  if(U32(a+0x12)===0x825D0&&U32(a+0x30)===0){
    if(U32(a+0x2C)===0x817CC)s.descriptorFingerprint='D0=20 family / timed path via 0x81856';
    else if(U32(a+0x2C)===0x81864)s.descriptorFingerprint='D0=16 family / hold-self path via 0x81864';
  }
  return s;
}
const events=[],last=new Map(),start=performance.now(),DURATION=10000,INTERVAL=20;
await new Promise(resolve=>{
  const id=setInterval(()=>{
    const t=Math.round(performance.now()-start);
    for(let i=0;i<SLOTS;i++){
      const s=snap(i);if(!s)continue;
      const key=JSON.stringify(s);
      if(last.get(i)!==key){events.push({t,...s});last.set(i,key);if(events.length>240)events.shift();}
    }
    if(t>=DURATION){clearInterval(id);resolve();}
  },INTERVAL);
});
const seenSlots=[...new Set(events.map(e=>e.slot))];
const fingerprints={d0_20:events.filter(e=>e.descriptorFingerprint?.startsWith('D0=20')).length,d0_16:events.filter(e=>e.descriptorFingerprint?.startsWith('D0=16')).length};
const out={version:'wof-type35-descriptor-chain-runtime-v1',readOnly:true,ramWrites:0,handoffGate,handoffStrict:Object.values(handoffGate).every(Boolean),descriptorFormat:{offset0:'frame/payload end pointer -> A6, also stored enemy+0x12',offset4:'long -> enemy+0x30',offset8:'word timer/flag; bit15 means explicit-next record',normalNext:'inline descriptor at current A4 after 10-byte record',flaggedNext:'mask bit15, store timer to enemy+0x34, load explicit long pointer at +0x0A into enemy+0x2C',payloadCopy:'word from frameEnd-2 -> enemy+0x6C; long from frameEnd-6 -> enemy+0x6E'},staticProof,dynamic:{durationMs:DURATION,intervalMs:INTERVAL,type35SlotsSeen:seenSlots,fingerprints,eventCount:events.length,events},note:'0x25C8 selects action descriptors, not executable handlers. This probe follows descriptor chains and checks their exact runtime fingerprints on live type35 enemies.'};
self.__WOF_TYPE35_DESCRIPTOR_CHAIN_RUNTIME_V1=out;
console.log('=== TYPE35 DESCRIPTOR CHAIN RUNTIME V1 JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_TYPE35_DESCRIPTOR_CHAIN_RUNTIME_V1_ERROR',e);throw e;});