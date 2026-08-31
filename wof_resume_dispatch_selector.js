(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v50',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'T16 exact B4 remains a strong imminent-danger shadow, but WOF-039 proved attack identity is not exclusive: 26/26 <=40ms danger hits, yet 25 were A6432 and 1 was A4840. T20 B0->B255 remains a strong coarse A5136 early-warning candidate: WOF-039 23/23 expected attack/target/side, zero hard miss, lead442.1..780.8ms; old 700ms horizon was too tight for 3 samples. D867BA and D8811E descriptor-family TM6 rules are now forward-supported production-shadow-candidates.',
 wof039:'Valid WOF-039 batch b-cab8bed7-fd3: 3 joined/3 complete/0 errors/0 interrupted, readOnly=true, ramWrites=0, 105571 enemy samples, 515 ACTIVE edges. All three captured rooms were 3-player rooms; the attempted 2P room was excluded by the flawed v39 45s join window. D867BA_3232_TM6_120:6/6 strict, A3232 6/6,target/side6/6, types T9=5,T36=1, two rooms, lead90.2..120ms. D8811E_3232_TM6_120:3/3 strict,A3232/target/side3/3,T11=3,lead99.6..119.3ms. T20 A5136:23 signals,20 strict<=700ms+3 late but within tail, all23 A5136/target/side, P1=11,P2=4,P3=8. T23 and T24 exact rules had zero entry coverage.',
 collectorCorrection:'WOF-039 batch transport was operational but workflow-wrong: 45s join window blocked later rooms and Worker cannot download through document. WOF-040 replaces it with one dual-mode script and a fresh IndexedDB v2 batch. ROOM Worker mode joins without a short timeout and collects; TOP mode manually finalizes all settled rooms and downloads exactly ONE merged JSON. 1P/2P/3P accepted; closed rooms become interrupted after stale heartbeat.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 embeddedValidator:'WOF-038 is still embedded for comparable rule evidence while collector workflow is stabilized.',
 nextScript:'wof_future_danger_multiroom_coordinator_v40.js',
 nextCopyId:'WOF-040',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V40 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not treat retrospective fixed-lag samples as forward timing proof. Do not claim T16 B4 is exclusively A6432 after WOF-039. Do not treat T20 700ms as a causal boundary. Do not restore broad T16 FAST/MID,broad T30_FAST,absDx130,or ambiguous T24 TM3/TM4 rules.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});