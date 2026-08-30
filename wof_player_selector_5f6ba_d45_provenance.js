(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const ENTRY=0x05F6BA,ALT=0x05F6C2;
const exact=[
 [0x05F6BA,8,'MOVE.L #0,120(A0)'],
 [0x05F6C2,8,'MOVE.L #0,124(A0)'],
 [0x05F6CA,4,'BTST #0,D0'],
 [0x05F6CE,2,'BEQ 0x05F6D4'],
 [0x05F6D0,4,'MOVE.L D2,120(A0)'],
 [0x05F6D4,4,'BTST #1,D0'],
 [0x05F6D8,2,'BEQ 0x05F6DE'],
 [0x05F6DA,4,'MOVE.L D3,120(A0)'],
 [0x05F6DE,4,'BTST #3,D0'],
 [0x05F6E2,2,'BEQ 0x05F6E8'],
 [0x05F6E4,4,'MOVE.L D4,124(A0)'],
 [0x05F6E8,4,'BTST #2,D0'],
 [0x05F6EC,2,'BEQ 0x05F6F2'],
 [0x05F6EE,4,'MOVE.L D5,124(A0)'],
 [0x05F6F2,2,'RTS']
];
const expectedWords={0x05F6BA:0x217C,0x05F6C2:0x217C,0x05F6CA:0x0800,0x05F6CE:0x6704,0x05F6D0:0x2142,0x05F6D4:0x0800,0x05F6D8:0x6704,0x05F6DA:0x2143,0x05F6DE:0x0800,0x05F6E2:0x6704,0x05F6E4:0x2144,0x05F6E8:0x0800,0x05F6EC:0x6704,0x05F6EE:0x2145,0x05F6F2:0x4E75};
const strict=exact.map(([at,len,text])=>({at:h(at),word:hw(r16(at)),expected:hw(expectedWords[at]),match:r16(at)===expectedWords[at],len,text}));
function directTarget(p){
 const w=r16(p);
 if(w===0x4EB8||w===0x4EF8){return {kind:w===0x4EB8?'JSR.W':'JMP.W',len:4,target:s16(r16(p+2))&0xFFFFFF};}
 if(w===0x4EB9||w===0x4EF9){return {kind:w===0x4EB9?'JSR.L':'JMP.L',len:6,target:r32(p+2)&0xFFFFFF};}
 if(w===0x4EBA||w===0x4EFA){return {kind:w===0x4EBA?'JSR.PC':'JMP.PC',len:4,target:(p+2+s16(r16(p+2)))>>>0};}
 if((w&0xFF00)===0x6100){const d=w&255,disp=d===0?s16(r16(p+2)):s8(d);return {kind:'BSR',len:d===0?4:2,target:(p+2+disp)>>>0};}
 return null;
}
const refs=[];
for(let p=0;p<MAX-6;p+=2){const q=directTarget(p);if(q&&(q.target===ENTRY||q.target===ALT))refs.push({at:h(p),word:hw(r16(p)),kind:q.kind,target:h(q.target),entry:q.target===ENTRY?'full':'alt'});}
const literal32=[];for(let p=0;p<MAX-3;p+=2){const v=r32(p)&0xFFFFFF;if(v===ENTRY||v===ALT)literal32.push({at:h(p),value:h(v)});}
function rawWindow(at,before=0x30,after=0x20){const a=[];for(let p=Math.max(0,at-before)&~1;p<=Math.min(MAX-2,at+after);p+=2)a.push({at:h(p),word:hw(r16(p)),mark:p===at?'CALL':''});return a;}
function regDef(p){
 const w=r16(p);
 if((w&0xF100)===0x7000){const d=(w>>9)&7;if([0,2,3,4,5].includes(d))return {reg:'D'+d,text:'MOVEQ #'+s8(w&255)+',D'+d,len:2};}
 const g=w>>>12;if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;if(dm===0&&[0,2,3,4,5].includes(dr)){
   let len=2,src='EA';
   if(sm<=4){src=sm===0?'D'+sr:sm===1?'A'+sr:'(A'+sr+')';}
   else if(sm===5){len=4;src=s16(r16(p+2))+'(A'+sr+')';}
   else if(sm===7&&sr===4){len=size==='L'?6:4;src='#'+(size==='L'?h(r32(p+2)):hw(r16(p+2)));}
   else if(sm===7&&sr===0){len=4;src=hw(r16(p+2))+'.W';}
   else if(sm===7&&sr===1){len=6;src=h(r32(p+2))+'.L';}
   else if(sm===7&&(sr===2||sr===3)){len=4;src='PC-relative';}
   else if(sm===6){len=4;src='indexed(A'+sr+')';}
   return {reg:'D'+dr,text:'MOVE.'+size+' '+src+',D'+dr,len};
 }}
 if((w&0xFFC0)===0x42C0){const d=w&7;if([0,2,3,4,5].includes(d))return {reg:'D'+d,text:'CLR.W D'+d,len:2};}
 return null;
}
function defsBefore(at){const out=[];for(let p=Math.max(0,at-0x80)&~1;p<at;p+=2){const d=regDef(p);if(d)out.push({at:h(p),reg:d.reg,text:d.text,dist:at-p});}return out.sort((a,b)=>a.dist-b.dist).slice(0,30);}
const callers=refs.map(x=>{const at=parseInt(x.at,16);return {...x,defs:defsBefore(at),window:rawWindow(at)};});
const pre=[];for(let p=ENTRY-0x30;p<ENTRY;p+=2)pre.push({at:h(p),word:hw(r16(p))});
const preTail=pre.slice(-12).map(x=>x.word);
const strictValid=strict.every(x=>x.match);
const verdict={entry:h(ENTRY),strictValid,strictInstructions:strict.length,directRefs:refs.length,fullEntryRefs:refs.filter(x=>x.entry==='full').length,altEntryRefs:refs.filter(x=>x.entry==='alt').length,literal32Refs:literal32.length,topCaller:refs[0]?.at||'',topCallerKind:refs[0]?.kind||'',preEntryTail:preTail.join(' '),d45Writes:'0x05F6E4 D4 -> +0x7C | 0x05F6EE D5 -> +0x7C'};
const out={version:'wof-player-selector-5f6ba-d45-provenance-v1',verdict,strict,refs,literal32,callers,preEntry:pre};
self.__WOF_SELECTOR_5F6BA_D45=out;
console.log('=== 5F6BA D4/D5 PROVENANCE VERDICT ===');console.table([verdict]);
console.log('=== 5F6BA STRICT FUNCTION ===');console.table(strict);
console.log('=== 5F6BA DIRECT REFS ===');console.table(refs);
console.log('=== 5F6BA D4/D5 PROVENANCE JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_5F6BA_D45_ERROR',e);throw e;});