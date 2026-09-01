(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v61',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-050:98 signals=96 strict+2 clean realLate,0 hard miss. T16 72/72 strict lead9.7..21.2ms with A6432=71/A4832=1 and target/side72/72; T20 4/4 A5136 lead599.4..989.7ms; D867 18/18 A3232 lead79.7..110.1ms across T9/T36/T33; D881 2/2 A3232 lead109.7/110.8ms. Existing T18 A5440/A5424 each produced one correct target/side-stable tail hit at138.6/128.5ms, proving legacy90ms is not causal; no demotion.',
 wof050:'Batch b-f8bbda7c-fae valid:3 joined/3 complete/0 error/0 interrupted,readOnly=true,ramWrites=0,36000 polls/104337 enemy samples/495 ACTIVE edges,player histogram[112,0,868,488]. All embedded WOF-050R validations passed.',
 t23State:'WOF-047 remains latest positive T23 sequence evidence:8 resolved cycles=A4792 3/A4920 3/A5888 2. WOF-049 five rooms and WOF-050 three rooms all had t23Samples0/attackZeroStarts0/activeEdges0/resolvedCycles0 and no T23 in aggregate type census. This is scene/room coverage absence, not failure; no promotion.',
 newCandidate:'WOF-050 broad same-cycle miner found T18 A4704 signature S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736 in18 resolved attack-zero cycles, targetSame18/18,sideSame18/18,last-seen lead29.6..51.1ms median40.5. WOF-051 adds a once-per-zero-cycle prospective level-arm candidate at80ms horizon/250ms tail, expected A4704.',
 traceInstrumentation:'Keep active-edge retarget logging fix plus exact timer-bearing tails and timer-normalized TM* final/tail2/tail3, transition pair/triple frequencies by activeAttack.',
 collectorState:'Dual-mode coordinator proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-051 uses fresh IndexedDB v13.',
 nextExperiment:'WOF-051 continues all production audits and T23 ordered tracing, while directly prospectively validating T18_4704_BODY4728_A4_B2_TM1_LEVEL_80. Prefer up to5 rooms. Do not promote the new candidate until repeated direct forward confirmations exist.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v51.js',
 nextCopyId:'WOF-051',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V51 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms or T18 legacy90ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules. Zero coverage is not forward failure. Same-cycle discovery is not production proof.',
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
