(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const M=_0x515056.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const h=(x,n=6)=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(n,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const hl=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(8,'0');
const rawWords=(lo,hi,marks={})=>{const a=[];for(let p=lo;p<=hi;p+=2)a.push({at:h(p),word:hw(r16(p)),mark:marks[p]||''});return a;};
const struct=a=>({
  at:h(a),
  firstLong:hl(r32(a)),
  words:Array.from({length:16},(_,i)=>({at:h(a+i*2),word:hw(r16(a+i*2))})),
  longs:Array.from({length:8},(_,i)=>({at:h(a+i*4),long:hl(r32(a+i*4))}))
});

const d20=0x81856,d16=0x81864;
const p20=r32(d20)>>>0,p16=r32(d16)>>>0;
const likelyRomPtr=v=>v<MAX&&(v&1)===0&&v>=0x2000;
const gate={
  d20Entry:r32(0x81788)===d20,
  d16Entry:r32(0x81784)===d16,
  firstLongSame:p20===p16,
  firstLongLooksRomPointer:likelyRomPtr(p20),
  dispatcher25C8Present:r16(0x25C8)!==0x0000,
  handoff247CPresent:r16(0x247C)!==0x0000
};
const ptrTargets=[...new Set([p20,p16].filter(likelyRomPtr))];
const ptrWindows=ptrTargets.map(p=>({target:h(p),raw:rawWords(Math.max(0,p-0x10),Math.min(MAX-2,p+0x60),{[p]:'FIRST LONG TARGET'})}));
const out={
  version:'wof-dispatch-247c-a4-structure-probe-v1',readOnly:true,ramWrites:0,
  gate,
  d0Map:[
    {d0:16,type35Entry:'0x081784',a4After25C8:'0x081864',firstLong:h(p16)},
    {d0:20,type35Entry:'0x081788',a4After25C8:'0x081856',firstLong:h(p20)}
  ],
  interpretationWarning:'0x81856/0x81864 are A4 values selected by 0x25C8, but raw bytes look like pointer/data structures, not direct 68000 code. Do not call them final handlers until 0x247C semantics are decoded.',
  raw2470To25DC:rawWords(0x2470,0x25DC,{0x247C:'KNOWN 25C8 HANDOFF TARGET',0x25B6:'DISPATCHER 25B6',0x25C8:'DISPATCHER 25C8',0x25DC:'TYPE POINTER TABLE'}),
  structures:{d0_20:struct(d20),d0_16:struct(d16)},
  sharedFirstLong:{d0_20:h(p20),d0_16:h(p16),same:p20===p16,looksRomPointer:likelyRomPtr(p20)},
  firstLongTargetWindows:ptrWindows,
  note:'Decode forward from the known instruction boundary 0x247C. Do not decode arbitrary even addresses. The purpose is to establish how A4-selected structures are consumed and whether their first long (currently expected near 0x825D0) is the actual executable routine pointer.'
};
self.__WOF_DISPATCH_247C_A4_STRUCTURE_PROBE=out;
console.log('=== DISPATCH 247C A4 STRUCTURE PROBE JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_DISPATCH_247C_A4_STRUCTURE_PROBE_ERROR',e);throw e;});
