(async()=>{
'use strict';
const COPY_ID='WOF-029';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-t16-wait-then-terminal-b4-validator-v29';
const MARKER='=== WOF FUTURE DANGER T16 WAIT THEN TERMINAL B4 VALIDATOR V29 JSON ===';
console.log(`[${COPY_ID}] ${PROJECT} ${VERSION}`);
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
if(!good(self._0x515056)){
  const until=performance.now()+8000;let hit=null;
  while(performance.now()<until&&!hit){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){hit={k,v};break}}if(!hit)await new Promise(r=>setTimeout(r,50));}
  if(!hit)throw new Error(`[${COPY_ID}] WASM module not found. Select the live gstyphoon.js Worker.`);
  self._0x515056=hit.v;self.__WOF_MODULE_GLOBAL_KEY=hit.k;
}
const MOD=self._0x515056,M=MOD.HEAPU8,R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error(`[${COPY_ID}] CPS RAM base missing`);
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const validT16Slots=()=>{const out=[];for(let i=0;i<SLOTS;i++){const a=ENEMY+i*STRIDE;if(U16(a+0x20)!==16)continue;const fe=U32(a+0x12),nx=U32(a+0x2C);if(!fe&&!nx)continue;out.push({slot:i,frameEnd:fe,next:nx,target7E:U16(a+0x7E),attack:U16(a+0x70)});}return out;};
const waitStart=performance.now(),WAIT_TIMEOUT=180000,STABLE_POLLS=3,WAIT_INTERVAL=50;let stableKey='',stableCount=0,found=null;
console.log(`[${COPY_ID}] waiting for LIVE T16 (same validity rule as V27: type16 plus frameEnd/next active object)`);
await new Promise((resolve,reject)=>{const id=setInterval(()=>{const slots=validT16Slots();const key=slots.map(x=>x.slot).join(',');if(slots.length){if(key===stableKey)stableCount++;else{stableKey=key;stableCount=1;}if(stableCount>=STABLE_POLLS){found=slots;clearInterval(id);resolve();return;}}else{stableKey='';stableCount=0;}if(performance.now()-waitStart>=WAIT_TIMEOUT){clearInterval(id);reject(new Error(`[${COPY_ID}] no LIVE T16 within ${WAIT_TIMEOUT/1000}s`));}},WAIT_INTERVAL);});
const waitMs=Math.round((performance.now()-waitStart)*10)/10;
console.log(`[${COPY_ID}] LIVE T16 confirmed after ${waitMs}ms`,found);
const raw='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_t16_terminal_b4_validator_v27.js?x='+Date.now();
const resp=await fetch(raw,{cache:'no-store'});if(!resp.ok)throw new Error(`[${COPY_ID}] fetch V27 failed ${resp.status}`);
const v27=await(0,eval)(await resp.text());
const out=JSON.parse(JSON.stringify(v27));
out.copyId=COPY_ID;out.project=PROJECT;out.version=VERSION;out.expectedMarker=MARKER;out.waitForLiveT16={waitMs,stablePollsRequired:STABLE_POLLS,waitIntervalMs:WAIT_INTERVAL,foundAtStart:found,validity:'type==16 and (frameEnd!=0 or next!=0), stable for 3 polls'};
if(out.diagnostics)out.diagnostics.copyId=COPY_ID;
if(out.model)out.model.wrapperPurpose='Avoid stale/inactive type16 false positives and start V27 immediately after a live T16 is confirmed.';
self.__WOF_V29_RESULT=out;
console.log(MARKER);console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('[WOF-029] ERROR',e);throw e;});