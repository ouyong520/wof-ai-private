(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const M=_0x515056.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x30000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=(x,n=6)=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(n,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const words=(at,n)=>Array.from({length:n},(_,i)=>hw(r16(at+i*2)));
const check=(at,exp,name)=>{const act=exp.map((_,i)=>r16(at+i*2));return{at:h(at),name,expected:exp.map(hw),actual:act.map(hw),ok:act.every((v,i)=>v===exp[i])};};
const raw=(lo,hi,marks={})=>{const a=[];for(let p=lo;p<=hi;p+=2)a.push({at:h(p),word:hw(r16(p)),mark:marks[p]||''});return a;};

// 1) Exact selected-player pointer -> selectedPlayer+0x29 compare proof.
const reader65=[
  check(0x0065E2,[0x3268,0x006A],'MOVEA.W 106(A0),A1'),
  check(0x0065EA,[0x0C29,0x0004,0x0029],'CMPI.B #4,41(A1)'),
  check(0x0065F0,[0x673E],'BEQ +0x3E')
];
const reader68=[
  check(0x006834,[0x3268,0x006A],'MOVEA.W 106(A0),A1'),
  check(0x006838,[0x0C29,0x0004,0x0029],'CMPI.B #4,41(A1)'),
  check(0x00683E,[0x6710],'BEQ +0x10'),
  check(0x006850,[0x7000,0x1028,0x002A,0x323B,0x0006],'MOVEQ #0,D0; MOVE.B 42(A0),D0; action table load')
];
const branch65=(0x0065F2+s8(r16(0x0065F0)&0xff))>>>0;
const branch68=(0x006840+s8(r16(0x00683E)&0xff))>>>0;
const actionJmp68=(r16(0x00685A)===0x4EFB);
const actionExt68=r16(0x00685C);

// 2) 0x112C2 is a known action target and performs a +0x2B subdispatch.
const sub112=[
  check(0x0112C2,[0x1028,0x002B],'MOVE.B 43(A0),D0'),
  check(0x0112C6,[0x323B,0x000E],'MOVE.W table(PC,D0.W),D1'),
  check(0x0112CA,[0x4EBB,0x100A],'JSR table(PC,D1.W)')
];
const table112=0x0112D6;
const subEntries=[];
for(let idx=0;idx<=0x1E;idx+=2){const w=r16(table112+idx),t=(table112+s16(w))>>>0;subEntries.push({indexByte:idx,at:h(table112+idx),word:hw(w),target:h(t)});}

// 3) Direct incoming control-flow refs to the important readers/targets.
const ctlTargets=new Set([0x0065E2,0x006834,0x006850,0x0112C2,0x0112A2]);
const incoming=[];
for(let p=0;p<MAX-6;p+=2){const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let kind='',t=null,len=2;
  if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d);t=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;}
  else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';if(m===7&&r===0){t=s16(r16(p+2))&0xffffff;len=4;}else if(m===7&&r===1){t=r32(p+2)&0xffffff;len=6;}else if(m===7&&r===2){t=(p+2+s16(r16(p+2)))>>>0;len=4;}}
  if(t!=null&&ctlTargets.has(t))incoming.push({at:h(p),word:hw(w),kind,target:h(t),len});
}

// 4) Locate readers in the real 25B6/25C8 type-specific level2 handler tables.
// Both dispatchers use the same first-level type table at 0x25DC.
const TYPE_TABLE=0x0025DC,TYPES=47;
const typeBases=[];
for(let type=0;type<TYPES;type++){const ptr=r32(TYPE_TABLE+type*4)>>>0;typeBases.push({type,ptr});}
const byBase=new Map();for(const x of typeBases){if(!byBase.has(x.ptr))byBase.set(x.ptr,[]);byBase.get(x.ptr).push(x.type);}
const sorted=[...byBase.keys()].filter(x=>x>0&&x<MAX).sort((a,b)=>a-b);
const handlerTargets=new Set([0x0065E2,0x006834,0x006850,0x0112C2,0x0112A2]);
const handlerTableHits=[];
for(let i=0;i<sorted.length;i++){
  const b=sorted[i],next=sorted[i+1]??(b+0x200),end=Math.min(next,b+0x200,MAX-4);
  for(let q=b;q<end;q+=4){const v=r32(q)>>>0;if(handlerTargets.has(v))handlerTableHits.push({types:byBase.get(b),tableBase:h(b),entryAt:h(q),d0Offset:q-b,target:h(v)});}
}
const type35Base=typeBases.find(x=>x.type===35)?.ptr??0;
const type35Preview=[];if(type35Base>0&&type35Base<MAX){for(let off=0;off<0x80;off+=4)type35Preview.push({d0Offset:off,at:h(type35Base+off),target:h(r32(type35Base+off)>>>0),isFocus:handlerTargets.has(r32(type35Base+off)>>>0)});}

// 5) Literal long-pointer refs anywhere in ROM; useful when table boundary classification is ambiguous.
const literalRefs=[];for(let p=0;p<MAX-3;p+=2){const v=r32(p)>>>0;if(handlerTargets.has(v))literalRefs.push({at:h(p),target:h(v)});}

const verdict={
  version:'wof-selector-6a-action-causal-proof-v1',readOnly:true,ramWrites:0,
  reader65Strict:reader65.every(x=>x.ok),reader68Strict:reader68.every(x=>x.ok),
  selectedPlayerFieldCompare:'+0x29 == 4',
  branch65Target:h(branch65),branch68Target:h(branch68),
  branch68LandsOnActionDispatch:branch68===0x006850&&reader68[3].ok,
  actionDispatch68HasIndexedJmp:actionJmp68,
  sub112Strict:sub112.every(x=>x.ok),sub112TableBase:h(table112),
  directIncoming:incoming.length,handlerTableHits:handlerTableHits.length,literalRefs:literalRefs.length,
  type35TableBase:type35Base?h(type35Base):null,
  type35FocusHits:type35Preview.filter(x=>x.isFocus).length,
  causalBridgeStructuralProof:reader68.every(x=>x.ok)&&branch68===0x006850
};
const out={version:'wof-selector-6a-action-causal-proof-v1',verdict,reader65:{checks:reader65,branchTarget:h(branch65),raw:raw(0x0065D8,0x00663A,{0x0065E2:'PTR->A1',0x0065EA:'CMP PLAYER+29',0x0065F0:'BRANCH',0x006632:'ACTION READ'})},reader68:{checks:reader68,branchTarget:h(branch68),actionJmpWord:hw(r16(0x00685A)),actionJmpExt:hw(actionExt68),raw:raw(0x006828,0x006890,{0x006834:'PTR->A1',0x006838:'CMP PLAYER+29',0x00683E:'BRANCH',0x006850:'ACTION ENTRY',0x006852:'READ +2A'})},sub112:{checks:sub112,tableBase:h(table112),entries:subEntries,raw:raw(0x0112A0,0x011330,{0x0112AA:'PTR->A1',0x0112C2:'ACTION TARGET',0x0112D6:'SUBTABLE'})},incoming,handlerTableHits,literalRefs,type35Preview};
self.__WOF_SELECTOR_6A_ACTION_CAUSAL_PROOF=out;
console.log('=== SELECTOR 6A ACTION CAUSAL PROOF VERDICT ===');console.table([verdict]);
console.log('=== SELECTOR 6A ACTION CAUSAL PROOF JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_6A_ACTION_CAUSAL_PROOF_ERROR',e);throw e;});
