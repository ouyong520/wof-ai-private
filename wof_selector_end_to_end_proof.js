(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16;
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const hl=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(8,'0');
const chk=(at,words,name)=>({at:h(at),name,actual:words.map((_,i)=>hw(r16(at+i*2))),ok:words.every((w,i)=>r16(at+i*2)===w)});

const selectorChecks=[
 chk(0x010E66,[0x3228,0x007E],'MOVE.W 126(A0),D1'),
 chk(0x010E6A,[0x43FA,0xFE8C],'LEA 0x010CF8,A1'),
 chk(0x010E6E,[0x2271,0x1000],'MOVE.L 0(A1,D1.W),A1'),
 chk(0x010E72,[0x3B49,0x01FA],'MOVE.W A1,506(A5)'),
 chk(0x010E76,[0x6100,0x0DAE],'BSR 0x011C26'),
 chk(0x010E94,[0x4EB8,0x5CC6],'JSR 0x005CC6'),
 chk(0x010E98,[0x6100,0x0D72],'BSR 0x011C0C'),
 chk(0x010EA4,[0x4EB8,0x12AE],'JSR 0x0012AE'),
 chk(0x010EA8,[0x1028,0x0099],'MOVE.B 153(A0),D0'),
 chk(0x010EAC,[0x323B,0x0006],'MOVE.W state99Table(PC,D0.W),D1'),
 chk(0x010EB0,[0x4EFB,0x1002],'JMP state99Target(PC,D1.W)')
];

const playerTable=[0,4,8].map((idx,i)=>({player:'P'+(i+1),indexByte:idx,at:h(0x010CF8+idx),value:hl(r32(0x010CF8+idx))}));
const playerTableOk=playerTable[0].value==='0x00FFBE1C'&&playerTable[1].value==='0x00FFBEFC'&&playerTable[2].value==='0x00FFBFDC';

const state99Entry={indexByte:0,at:h(0x010EB4),word:hw(r16(0x010EB4)),target:h(0x010EB4+((r16(0x010EB4)&0x8000)?r16(0x010EB4)-0x10000:r16(0x010EB4)))};
const state99BlockChecks=[
 chk(0x010BBC,[0x1028,0x002A],'MOVE.B 42(A0),D0'),
 chk(0x010BC0,[0x323B,0x0006],'MOVE.W action2ATable(PC,D0.W),D1'),
 chk(0x010BC4,[0x4EFB,0x1002],'JMP action2ATarget(PC,D1.W)')
];
const actionAt=0x010BCA,actionWord=r16(actionAt),actionSigned=actionWord&0x8000?actionWord-0x10000:actionWord;
const action2AEntry={indexByte:2,at:h(actionAt),word:hw(actionWord),target:h(0x010BC8+actionSigned)};

const bridgeChecks=[
 chk(0x010EC6,[0x0C68,0x0000,0x0002],'CMPI.W #0,2(A0)'),
 chk(0x010ECC,[0x6604],'BNE 0x010ED2'),
 chk(0x010ECE,[0x4EB8,0x1B02],'JSR 0x001B02'),
 chk(0x010ED2,[0x4A28,0x002B],'TST.B 43(A0)'),
 chk(0x010ED6,[0x6630],'BNE 0x010F08'),
 chk(0x010F08,[0x3228,0x0040],'MOVE.W 64(A0),D1'),
 chk(0x010F0C,[0xD368,0x0004],'ADD.W D1,4(A0)'),
 chk(0x010F10,[0x5328,0x001F],'SUBQ.B #1,31(A0)'),
 chk(0x010F14,[0x6646],'BNE 0x010F5C'),
 chk(0x010F16,[0x7000],'MOVEQ #0,D0'),
 chk(0x010F24,[0x0828,0x0004,0x0072],'BTST #4,114(A0)'),
 chk(0x010F2A,[0x6720],'BEQ 0x010F4C'),
 chk(0x010F2C,[0x4EB8,0x1426],'JSR 0x001426'),
 chk(0x010F30,[0x650E],'BCS 0x010F40'),
 chk(0x010F40,[0x317C,0x0600,0x002A],'MOVE.W #0x0600,42(A0)'),
 chk(0x010F46,[0x7018],'MOVEQ #24,D0'),
 chk(0x010F48,[0x4EF8,0x25C8],'JMP 0x0025C8')
];

const selectorStrict=selectorChecks.every(x=>x.ok);
const state99Strict=state99Entry.target==='0x010BBC'&&state99BlockChecks.every(x=>x.ok);
const actionStrict=action2AEntry.target==='0x010EC6';
const bridgeStrict=bridgeChecks.every(x=>x.ok);
const verdict={
 selectorStrict,playerTableOk,state99Strict,action2AStrict:actionStrict,bridgeStrict,
 selectorField:'enemy+0x7E',playerIndexValues:'0/4/8',playerTable:'0x010CF8',
 state99Field:'enemy+0x99',state99Value:0,action2AField:'enemy+0x2A',action2AValue:2,
 d0:'24',dispatcher:'0x0025C8',
 endToEndStructuralProof:selectorStrict&&playerTableOk&&state99Strict&&actionStrict&&bridgeStrict,
 provenRoute:'enemy+0x7E -> P1/P2/P3 table -> A1 -> state99=0 -> action2A=2 -> 0x010EC6 -> MOVEQ #24,D0 -> 0x010F48 -> 0x0025C8'
};
const out={version:'wof-selector-end-to-end-proof-v1',verdict,playerTable,selectorChecks,state99Entry,state99BlockChecks,action2AEntry,bridgeChecks};
self.__WOF_SELECTOR_END_TO_END=out;
console.log('=== SELECTOR END-TO-END VERDICT ===');console.table([verdict]);
console.log('=== PLAYER TABLE ===');console.table(playerTable);
console.log('=== SELECTOR CHECKS ===');console.table(selectorChecks);
console.log('=== STATE99 / ACTION2A ===');console.table([state99Entry,action2AEntry]);
console.log('=== FINAL BRIDGE ===');console.table(bridgeChecks);
console.log('=== SELECTOR END-TO-END JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_END_TO_END_ERROR',e);throw e;});
