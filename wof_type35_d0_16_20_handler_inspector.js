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
const raw=(lo,hi,marks={})=>{const a=[];for(let p=lo;p<=hi;p+=2)a.push({at:h(p),word:hw(r16(p)),mark:marks[p]||''});return a;};
const marks={
  0x81856:'TYPE35 D0=20 HANDLER',
  0x81864:'TYPE35 D0=16 HANDLER',
  0x81876:'TYPE35 D0=0 HANDLER',
  0x81884:'TYPE35 D0=4 HANDLER',
  0x81892:'TYPE35 D0=24 HANDLER',
  0x818CA:'TYPE35 D0=8 HANDLER',
  0x81906:'TYPE35 D0=12 HANDLER'
};
const typeBase=0x81774;
const typeEntries=[];for(let i=0;i<7;i++)typeEntries.push({d0:i*4,entryAt:h(typeBase+i*4),target:h(r32(typeBase+i*4))});
const gate={
  moveq16:r16(0x6A10)===0x7010,
  jsr16:r16(0x6A12)===0x4EB8&&r16(0x6A14)===0x25C8,
  moveq20:r16(0x6A62)===0x7014,
  jsr20:r16(0x6A64)===0x4EB8&&r16(0x6A66)===0x25C8,
  type35D0_16:r32(typeBase+16)===0x00081864,
  type35D0_20:r32(typeBase+20)===0x00081856
};
const controlWords=[];
for(let p=0x81840;p<=0x81940;p+=2){
  const w=r16(p);let kind='';
  if(w===0x4E75)kind='RTS';
  else if(w===0x4EB8)kind='JSR abs.W';
  else if(w===0x4EB9)kind='JSR abs.L';
  else if(w===0x4EF8)kind='JMP abs.W';
  else if(w===0x4EF9)kind='JMP abs.L';
  else if((w&0xFF00)===0x6000)kind='BRA';
  else if((w&0xF000)===0x6000)kind='Bcc';
  else if((w&0xF100)===0x7000)kind='MOVEQ';
  if(kind)controlWords.push({at:h(p),word:hw(w),kind});
}
const out={
  version:'wof-type35-d0-16-20-handler-inspector-v1',readOnly:true,ramWrites:0,
  gate,gateStrict:Object.values(gate).every(Boolean),
  provenDispatches:[
    {callAt:'0x006A12',d0:16,type35Entry:'0x081784',handler:'0x081864'},
    {callAt:'0x006A64',d0:20,type35Entry:'0x081788',handler:'0x081856'}
  ],
  type35Entries:typeEntries,
  raw81840To81940:raw(0x81840,0x81940,marks),
  controlWordCandidates:controlWords,
  note:'Known handler entry addresses are authoritative boundaries. controlWordCandidates are only hints; do not treat arbitrary even-address words as decoded instructions.'
};
self.__WOF_TYPE35_D0_16_20_HANDLER_INSPECTOR=out;
console.log('=== TYPE35 D0 16/20 HANDLER INSPECTOR JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_TYPE35_D0_16_20_HANDLER_INSPECTOR_ERROR',e);throw e;});
