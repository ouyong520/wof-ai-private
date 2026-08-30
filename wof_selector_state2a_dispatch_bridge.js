(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16;
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const STATE99=[0x010BBC,0x010BD0,0x010BE4,0x010BF8,0x010C0C];
const state99IndexMap=[
  {indexByte:0,target:0x010BBC},{indexByte:2,target:0x010BD0},{indexByte:4,target:0x010BE4},
  {indexByte:6,target:0x010BD0},{indexByte:8,target:0x010BF8},{indexByte:10,target:0x010C0C},
  {indexByte:12,target:0x010BD0},{indexByte:14,target:0x010BD0},{indexByte:16,target:0x010BD0}
];
function sig(t){return [r16(t),r16(t+2),r16(t+4),r16(t+6),r16(t+8),r16(t+10)];}
const blocks=[];const routes=[];
for(const t of STATE99){
  const S=sig(t), valid=S[0]===0x1028&&S[1]===0x002A&&S[2]===0x323B&&S[3]===0x0006&&S[4]===0x4EFB&&S[5]===0x1002;
  const tableBase=t+0x0C, entries=[];
  for(let i=0;i<4;i++){
    const at=tableBase+i*2,w=r16(at),dst=(tableBase+s16(w))>>>0;
    entries.push({indexByte:i*2,at:h(at),word:hw(w),signed:s16(w),target:h(dst)});
    for(const s of state99IndexMap.filter(x=>x.target===t)) routes.push({state99IndexByte:s.indexByte,state99Target:h(t),action2AIndexByte:i*2,tableAt:h(at),word:hw(w),finalTarget:h(dst)});
  }
  blocks.push({target:h(t),validPattern:valid,tableBase:h(tableBase),entries});
}
const to10EC6=routes.filter(x=>x.finalTarget==='0x010EC6');
const bridgeChecks=[
  {at:0x010EC6,words:[0x0C68,0x0000,0x0002],name:'CMPI.W #0,2(A0)'},
  {at:0x010ECC,words:[0x6604],name:'BNE 0x010ED2'},
  {at:0x010ECE,words:[0x4EB8,0x1B02],name:'JSR 0x001B02'},
  {at:0x010ED2,words:[0x4A28,0x002B],name:'TST.B 43(A0)'},
  {at:0x010ED6,words:[0x6630],name:'BNE 0x010F08'},
  {at:0x010F08,words:[0x3228,0x0040],name:'MOVE.W 64(A0),D1'},
  {at:0x010F0C,words:[0xD368,0x0004],name:'ADD.W D1,4(A0)'},
  {at:0x010F10,words:[0x5328,0x001F],name:'SUBQ.B #1,31(A0)'},
  {at:0x010F14,words:[0x6646],name:'BNE 0x010F5C'},
  {at:0x010F16,words:[0x7000],name:'MOVEQ #0,D0'},
  {at:0x010F24,words:[0x0828,0x0004,0x0072],name:'BTST #4,114(A0)'},
  {at:0x010F2A,words:[0x6720],name:'BEQ 0x010F4C'},
  {at:0x010F2C,words:[0x4EB8,0x1426],name:'JSR 0x001426'},
  {at:0x010F30,words:[0x650E],name:'BCS 0x010F40'},
  {at:0x010F40,words:[0x317C,0x0600,0x002A],name:'MOVE.W #0x0600,42(A0)'},
  {at:0x010F46,words:[0x7018],name:'MOVEQ #24,D0'},
  {at:0x010F48,words:[0x4EF8,0x25C8],name:'JMP 0x0025C8'}
].map(x=>({...x,at:h(x.at),actual:x.words.map((_,i)=>hw(r16(parseInt(h(x.at),16)+i*2))),ok:x.words.every((w,i)=>r16(parseInt(h(x.at),16)+i*2)===w)}));
const strictBridgeOk=bridgeChecks.every(x=>x.ok);
const allPatterns=blocks.every(x=>x.validPattern);
const uniqueFinal=[...new Set(routes.map(x=>x.finalTarget))].sort();
const verdict={state99Blocks:blocks.length,allState2APatternsValid:allPatterns,routes:routes.length,uniqueFinalTargets:uniqueFinal.length,routesTo10EC6:to10EC6.length,strictBridge10EC6To10F48:strictBridgeOk,bridgeD0:'MOVEQ #24,D0',dispatcher:'0x0025C8',provenRoute:to10EC6[0]?'state99='+to10EC6[0].state99IndexByte+', action2A='+to10EC6[0].action2AIndexByte+' -> 0x010EC6 -> 0x010F48 -> 0x0025C8':''};
const out={version:'wof-selector-state2a-dispatch-bridge-v1',verdict,blocks,routes,to10EC6,uniqueFinalTargets:uniqueFinal,bridgeChecks};
self.__WOF_SELECTOR_STATE2A_BRIDGE=out;
console.log('=== SELECTOR STATE2A DISPATCH BRIDGE VERDICT ===');console.table([verdict]);
console.log('=== STATE2A BLOCKS ===');console.dir(blocks,{depth:null});
console.log('=== ROUTES TO 10EC6 ===');console.table(to10EC6);
console.log('=== STRICT 10EC6 -> 10F48 BRIDGE ===');console.table(bridgeChecks.map(x=>({at:x.at,name:x.name,ok:x.ok,actual:x.actual.join(' ')})));
console.log('=== SELECTOR STATE2A DISPATCH BRIDGE JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_STATE2A_BRIDGE_ERROR',e);throw e;});