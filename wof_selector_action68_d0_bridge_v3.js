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
const s16=v=>v&0x8000?v-0x10000:v;
const h=(x,n=6)=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(n,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const okCode=v=>v>=0x2000&&v<MAX&&(v&1)===0;
const raw=(lo,hi,marks={})=>{const a=[];for(let p=lo;p<=hi;p+=2)a.push({at:h(p),word:hw(r16(p)),mark:marks[p]||''});return a;};

const gate={
  ptrReader:r16(0x6834)===0x3268&&r16(0x6836)===0x006A,
  cmpPlayer29:r16(0x6838)===0x0C29&&r16(0x683A)===0x0004&&r16(0x683C)===0x0029,
  branchToAction:r16(0x683E)===0x6710,
  actionDispatch:r16(0x6850)===0x7000&&r16(0x6852)===0x1028&&r16(0x6854)===0x002A&&r16(0x6856)===0x323B&&r16(0x6858)===0x0006&&r16(0x685A)===0x4EFB&&r16(0x685C)===0x1002,
  jsr6A12:r16(0x6A12)===0x4EB8&&r16(0x6A14)===0x25C8,
  jsr6A64:r16(0x6A64)===0x4EB8&&r16(0x6A66)===0x25C8
};

const actionBase=0x685E;
const a0w=r16(actionBase),a2w=r16(actionBase+2);
const actionEntries=[
  {action2A:0,at:h(actionBase),word:hw(a0w),target:h((actionBase+s16(a0w))>>>0)},
  {action2A:2,at:h(actionBase+2),word:hw(a2w),target:h((actionBase+s16(a2w))>>>0)}
];
const exactTwoEntryTable=(parseInt(actionEntries[0].target,16)===actionBase+4);

const typeBase=0x81774;
const type35Raw=[];
for(let i=0;i<12;i++){const at=typeBase+i*4,v=r32(at)>>>0;type35Raw.push({slot:i,d0Offset:i*4,entryAt:h(at),target:h(v),validCode:okCode(v)});}
let prefixCount=0;while(prefixCount<type35Raw.length&&type35Raw[prefixCount].validCode)prefixCount++;
const type35Prefix=type35Raw.slice(0,prefixCount);

const marks1={0x6904:'ACTION2A=2 ENTRY',0x6A12:'JSR 25C8'};
const marks2={0x6A64:'JSR 25C8'};
const out={
  version:'wof-selector-action68-d0-bridge-v3',readOnly:true,ramWrites:0,
  gate,
  gateStrict:Object.values(gate).every(Boolean),
  action68:{base:h(actionBase),exactTwoEntryTable,entries:actionEntries},
  type35:{tableBase:h(typeBase),sharedTypes:[7,35],contiguousValidPrefixCount:prefixCount,prefix:type35Prefix,firstNonPrefix:type35Raw[prefixCount]||null,rawFirst12:type35Raw},
  raw6904To6A1A:raw(0x6904,0x6A1A,marks1),
  raw6A40To6A6C:raw(0x6A40,0x6A6C,marks2),
  note:'Do not infer instruction boundaries from every even address. These windows are for exact forward CFG decoding from the known action2A=2 entry 0x6904 and known JSR sites 0x6A12/0x6A64.'
};
self.__WOF_SELECTOR_ACTION68_D0_BRIDGE_V3=out;
console.log('=== SELECTOR ACTION68 D0 BRIDGE V3 JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_ACTION68_D0_BRIDGE_V3_ERROR',e);throw e;});
