(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const M=_0x515056.HEAPU8,base=C.base,SW=!!C.swap16;
const MAX=Math.min(0x200000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s16=v=>v&0x8000?v-0x10000:v;
const h=(x,n=6)=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(n,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const okAddr=v=>v>=0x2000&&v<MAX&&(v&1)===0;

const FOCUS=new Set([0x0065E2,0x006834,0x006850,0x0112A2,0x0112C2]);

// exact bridge checks retained
const bridge={
  reader65:r16(0x65E2)===0x3268&&r16(0x65E4)===0x006A&&r16(0x65EA)===0x0C29&&r16(0x65EC)===0x0004&&r16(0x65EE)===0x0029,
  reader68:r16(0x6834)===0x3268&&r16(0x6836)===0x006A&&r16(0x6838)===0x0C29&&r16(0x683A)===0x0004&&r16(0x683C)===0x0029,
  branch68:r16(0x683E)===0x6710,
  actionEntry68:r16(0x6850)===0x7000&&r16(0x6852)===0x1028&&r16(0x6854)===0x002A&&r16(0x6856)===0x323B&&r16(0x6858)===0x0006&&r16(0x685A)===0x4EFB&&r16(0x685C)===0x1002
};

function parseRelWordTable(baseAddr,label){
  const first=r16(baseAddr);let count=(first>0&&first<=0x80&&(first&1)===0)?(first>>>1):0;
  if(count<1||count>32)count=0;
  const entries=[];
  for(let i=0;i<count;i++){
    const at=baseAddr+i*2,w=r16(at),target=(baseAddr+s16(w))>>>0;
    entries.push({indexByte:i*2,at:h(at),word:hw(w),target:h(target),validTarget:okAddr(target)});
  }
  return{label,base:h(baseAddr),firstWord:hw(first),inferredCount:count,entries};
}
const action65=parseRelWordTable(0x663E,'0x6630 action2A dispatch');
const action68=parseRelWordTable(0x685E,'0x6850 action2A dispatch');
const sub112=parseRelWordTable(0x112D6,'0x112C2 +0x2B subdispatch');

// 47-type first-level table shared by 25B6/25C8
const TYPE_TABLE=0x25DC,TYPES=47;
const typeRows=[];
for(let type=0;type<TYPES;type++){
  const at=TYPE_TABLE+type*4,ptr=r32(at)>>>0;
  typeRows.push({type,at:h(at),tableBase:ptr<h(MAX)?h(ptr):h(ptr),ptr,valid:okAddr(ptr)});
}
const byBase=new Map();
for(const x of typeRows.filter(x=>x.valid)){
  if(!byBase.has(x.ptr))byBase.set(x.ptr,[]);
  byBase.get(x.ptr).push(x.type);
}
const bases=[...byBase.keys()].sort((a,b)=>a-b);
const ranges=[];
for(let i=0;i<bases.length;i++){
  const b=bases[i],next=bases[i+1]??Math.min(MAX,b+0x400);
  const end=Math.min(next,b+0x400,MAX);
  ranges.push({base:b,end,types:byBase.get(b)});
}

const tableHits=[];
let totalEntries=0;
for(const rg of ranges){
  for(let q=rg.base;q+3<rg.end;q+=4){
    const v=r32(q)>>>0;
    // Stop only on obviously impossible data after at least one entry; ranges are bounded by next known table anyway.
    totalEntries++;
    if(FOCUS.has(v))tableHits.push({types:rg.types,tableBase:h(rg.base),entryAt:h(q),d0Offset:q-rg.base,target:h(v)});
  }
}

const type35=typeRows.find(x=>x.type===35);
const rg35=type35?ranges.find(r=>r.base===type35.ptr):null;
const type35Entries=[];
if(rg35){
  for(let q=rg35.base;q+3<rg35.end;q+=4){
    const v=r32(q)>>>0;
    type35Entries.push({d0Offset:q-rg35.base,entryAt:h(q),target:h(v),focus:FOCUS.has(v),validCode:okAddr(v)});
  }
}

// Full-ROM literal refs and classify whether they lie inside a known level2 range.
function classifyRef(p){
  const rg=ranges.find(r=>p>=r.base&&p<r.end);
  return rg?{kind:'level2-table',types:rg.types,tableBase:h(rg.base),d0Offset:p-rg.base}:{kind:'other'};
}
const literalRefs=[];
for(let p=0;p+3<MAX;p+=2){
  const v=r32(p)>>>0;
  if(FOCUS.has(v))literalRefs.push({at:h(p),target:h(v),...classifyRef(p)});
}

// Nearby direct dispatcher exits from the action targets (compact diagnostic only).
function directDispatchRefs(lo,hi){
  const out=[];
  for(let p=lo;p+3<=hi&&p+3<MAX;p+=2){
    const w=r16(p),x=r16(p+2);
    if(w===0x4EF8&&(x===0x25B6||x===0x25C8))out.push({at:h(p),kind:'JMP abs.W',target:h(x)});
    if(w===0x4EB8&&(x===0x25B6||x===0x25C8))out.push({at:h(p),kind:'JSR abs.W',target:h(x)});
  }
  return out;
}
const actionTargetDiagnostics=[];
for(const t of [...action65.entries,...action68.entries].map(x=>parseInt(x.target,16)).filter(okAddr)){
  actionTargetDiagnostics.push({target:h(t),dispatchRefs:directDispatchRefs(t,Math.min(MAX-4,t+0x180))});
}

const verdict={
  version:'wof-selector-6a-action-handler-map-v2',readOnly:true,ramWrites:0,
  romScanLimit:h(MAX),
  priorBugFixed:'v1 capped ROM at 0x30000 while type35 table is above 0x80000',
  bridgeStrict:Object.values(bridge).every(Boolean),
  typeTableBase:h(TYPE_TABLE),validTypePointers:typeRows.filter(x=>x.valid).length,uniqueLevel2Tables:ranges.length,totalLevel2SlotsScanned:totalEntries,
  handlerTableHits:tableHits.length,
  type35TableBase:type35?h(type35.ptr):null,
  type35Slots:type35Entries.length,
  type35FocusHits:type35Entries.filter(x=>x.focus).length,
  action65Count:action65.inferredCount,action68Count:action68.inferredCount,sub112Count:sub112.inferredCount,
  literalRefs:literalRefs.length,
  literalRefsInLevel2:literalRefs.filter(x=>x.kind==='level2-table').length
};

const out={
  version:'wof-selector-6a-action-handler-map-v2',verdict,bridge,
  actionTables:{action65,action68,sub112},
  focusTableHits:tableHits,
  type35:{type:35,tableBase:type35?h(type35.ptr):null,range:rg35?{start:h(rg35.base),end:h(rg35.end),types:rg35.types}:null,entries:type35Entries},
  literalRefs,
  actionTargetDiagnostics
};
self.__WOF_SELECTOR_6A_ACTION_HANDLER_MAP_V2=out;
console.log('=== SELECTOR 6A ACTION HANDLER MAP V2 VERDICT ===');console.table([verdict]);
console.log('=== SELECTOR 6A ACTION HANDLER MAP V2 JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_6A_ACTION_HANDLER_MAP_V2_ERROR',e);throw e;});
