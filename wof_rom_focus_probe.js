(()=>{
'use strict';
try{self.WOFFOCUSROM?.stop?.();}catch(_){}
const M=_0x515056?.HEAPU8;if(!M)throw new Error('HEAPU8 unavailable');
const SIG1_OFF=0x100,SIG1=[0x23,0xFC,0x00,0x00,0x03,0x86,0x00,0xFF,0x00,0x08,0x60,0x00,0x00,0x82];
const SIG2_OFF=0x426,SIG2=[0x4B,0xF8,0x80,0x00,0x20,0x7C,0x00,0xFF,0x00,0x00,0x30,0x3C,0x3F,0xFF];
const matchAt=(p,s)=>{if(p<0||p+s.length>M.length)return false;for(let i=0;i<s.length;i++)if(M[p+i]!==s[i])return false;return true;};
function findRom(){let p=0;while((p=M.indexOf(SIG1[0],p))>=0){const b=p-SIG1_OFF;if(b>=0&&matchAt(p,SIG1)&&matchAt(b+SIG2_OFF,SIG2))return b;p++;}return-1;}
const base=findRom();if(base<0)throw new Error('WOF 68000 ROM signature not found');
const MAX=Math.min(0x100000,M.length-base),TBL=0x25DC,NT=47;
const r8=o=>M[base+o]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const sx8=v=>v&0x80?v-0x100:v,sx16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const hex=(o,n=32)=>Array.from({length:Math.max(0,Math.min(n,MAX-o))},(_,i)=>r8(o+i).toString(16).toUpperCase().padStart(2,'0')).join(' ');
const TYPES=Array.from({length:NT},(_,type)=>({type,entry:r32(TBL+type*4)}));
const unique=[...new Map(TYPES.filter(x=>x.entry<MAX).map(x=>[x.entry,{entry:x.entry,types:[]}])).values()];for(const x of TYPES){const u=unique.find(y=>y.entry===x.entry);if(u)u.types.push(x.type);}
const PLAYER={P1:0x00FFBE1C,P2:0x00FFBEFC,P3:0x00FFBFDC},LOWS=Object.fromEntries(Object.entries(PLAYER).map(([k,v])=>[k,v&0xffff]));
function nearType(off){let best=null;for(const u of unique){const d=Math.abs(off-u.entry);if(!best||d<best.d)best={entry:u.entry,types:u.types,d};}return best;}
function hasWordAround(off,w,rad=32){for(let p=Math.max(0,off-rad)&~1;p+1<Math.min(MAX,off+rad);p+=2)if(r16(p)===w)return true;return false;}
function playerRefs(){const longRefs=[],wordRefs=[];for(let o=0;o+4<=MAX;o+=2){const v=r32(o);for(const [name,a] of Object.entries(PLAYER))if(v===a){const nt=nearType(o);longRefs.push({player:name,off:h(o),prev:hw(o>=2?r16(o-2):0),hasE0:hasWordAround(o,0x00E0,48),nearTypes:nt?.types?.join('/')||'',distance:nt?.d??null,ctx:hex(Math.max(0,o-8),24)});}}
  for(let o=0;o+2<=MAX;o+=2){const v=r16(o);for(const [name,a] of Object.entries(LOWS))if(v===a){const nt=nearType(o);wordRefs.push({player:name,off:h(o),prev:hw(o>=2?r16(o-2):0),hasE0:hasWordAround(o,0x00E0,48),nearTypes:nt?.types?.join('/')||'',distance:nt?.d??null,ctx:hex(Math.max(0,o-8),20)});}}
  return{longRefs,wordRefs};
}
function callsIn(start,span=0x700){const end=Math.min(MAX,start+span),out=[];for(let p=start&~1;p+2<end;p+=2){const w=r16(p);if(w===0x4EB9||w===0x4EF9){const t=r32(p+2);if(t<MAX)out.push({at:p,target:t,kind:w===0x4EB9?'JSR.L':'JMP.L'});}else if((w&0xFF00)===0x6100){const d8=w&255;let t;if(d8===0&&p+4<=end)t=p+2+sx16(r16(p+2));else t=p+2+sx8(d8);if(t>=0&&t<MAX)out.push({at:p,target:t,kind:'BSR'});}}return out;}
function scoreHelper(t,refs){let l=0,w=0,e0=0;for(const x of refs.longRefs){const o=parseInt(x.off,16);if(Math.abs(o-t)<=0x300)l++;}for(const x of refs.wordRefs){const o=parseInt(x.off,16);if(Math.abs(o-t)<=0x300)w++;}for(let p=Math.max(0,t-0x100)&~1;p+1<Math.min(MAX,t+0x300);p+=2)if(r16(p)===0x00E0)e0++;return{longHits:l,wordHits:w,strideHits:e0};}
function commonHelpers(refs){const m=new Map();for(const u of unique){const seen=new Set();for(const c of callsIn(u.entry)){if(seen.has(c.target))continue;seen.add(c.target);let z=m.get(c.target);if(!z){z={target:c.target,callers:new Set(),kinds:new Set()};m.set(c.target,z);}z.callers.add(u.entry);z.kinds.add(c.kind);}}
  const rows=[];for(const z of m.values()){const s=scoreHelper(z.target,refs),callerTypes=[];for(const e of z.callers){const u=unique.find(x=>x.entry===e);if(u)callerTypes.push(...u.types);}const score=z.callers.size*2+s.longHits*12+s.wordHits*2+Math.min(4,s.strideHits);if(z.callers.size>=2||s.longHits||s.wordHits>=2)rows.push({target:h(z.target),callerGroups:z.callers.size,types:[...new Set(callerTypes)].sort((a,b)=>a-b).join(','),kinds:[...z.kinds].join('/'),...s,score,ctx:hex(z.target,32)});}rows.sort((a,b)=>b.score-a.score||b.callerGroups-a.callerGroups);return rows;}
function typeRows(){return TYPES.map(x=>({type:x.type,entry:h(x.entry),valid:x.entry<MAX,sharedWith:TYPES.filter(y=>y.entry===x.entry&&y.type!==x.type).map(y=>y.type).join(',')}));}
function routine(type,span=0x700){const x=TYPES[type];if(!x)return null;const cs=callsIn(x.entry,span).map(c=>({at:h(c.at),target:h(c.target),kind:c.kind}));console.log('type',type,'entry',h(x.entry));console.table(cs);return{type,entry:h(x.entry),calls:cs,hex:hex(x.entry,96)};}
function dump(off,n=128){off=typeof off==='string'?parseInt(off,16):off;const row={off:h(off),hex:hex(off,n)};console.log(row.off,row.hex);return row;}
function result(){const vectors={sp:h(r32(0)),pc:h(r32(4)),romBaseHeap:'0x'+base.toString(16).toUpperCase(),romBytes:MAX,dispatchTable:h(TBL)};const refs=playerRefs(),helpers=commonHelpers(refs),types=typeRows();console.log('=== ROM vectors / type table ===');console.log(vectors);console.table(types);console.log('=== direct 32-bit P1/P2/P3 refs ===');console.table(refs.longRefs.slice(0,80));console.log('=== low-16 P1/P2/P3 refs ===');console.table(refs.wordRefs.slice(0,120));console.log('=== common helper candidates ===');console.table(helpers.slice(0,50));const out={version:'rom-focus-probe-v1',vectors,types,longRefs:refs.longRefs,wordRefs:refs.wordRefs,helpers:helpers.slice(0,100)};self.__WOF_ROM_FOCUS_LAST=out;return out;}
self.WOFFOCUSROM={version:'rom-focus-probe-v1',base,MAX,result,routine,dump,calls(type,span){return routine(type,span)},stop(){console.log('⛔ ROM focus probe stopped (static probe, nothing to detach)');}};
console.log('✅ WOF ROM focus probe v1 loaded');console.log('ROM heap base=0x'+base.toString(16).toUpperCase(),'SP='+h(r32(0)),'PC='+h(r32(4)),'dispatch='+h(TBL));console.log('运行 WOFFOCUSROM.result()');
})();