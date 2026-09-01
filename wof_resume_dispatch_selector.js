(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v60',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-049 five-room audit stayed clean:106/106 strict,0 jitter,0 realLate,0 hard miss. T16 31/31 lead10.0..21.6ms; T20 4/4 A5136 lead430.2..629.1ms; D867 13/13 A3232 lead29.9..120.1ms across T9/T33 and P1/P2/P3; D881 4/4 A3232 lead100.0..108.8ms; T24 19/19 A5440 and21/21 A5424; T18 7/7 A5440 and7/7 A5424.',
 wof049:'Batch b-106c5a3c-819 valid:5 joined/5 complete/0 error/0 interrupted,readOnly=true,ramWrites=0,60000 polls/194328 enemy samples/1166 ACTIVE edges,player histogram[27,1087,196,1134],room peaks3/1/3/1/3. Embedded WOF-049R identity passed.',
 t23State:'WOF-047 remains latest positive T23 sequence evidence:8 resolved cycles=A4792 3/A4920 3/A5888 2 and single states are attack-ambiguous. WOF-049 sampled five rooms but every dedicated tracer had t23Samples0,attackZeroStarts0,activeEdges0,resolvedCycles0,t23CycleTraces[],sequenceSummary.totalCycles0; aggregate type census also had no T23. This is scene/room coverage absence, not failure; no promotion.',
 traceInstrumentation:'Keep active-edge retarget logging fix plus exact timer-bearing tails and timer-normalized TM* final/tail2/tail3, transition pair/triple frequencies by activeAttack. WOF-049 had zero T23 in all five rooms so these T23 summaries again were not exercised.',
 collectorState:'Dual-mode coordinator proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-050 uses fresh IndexedDB v12.',
 nextExperiment:'WOF-050 is a semantic coverage repeat. Run up to5 rooms in parallel. Main objective is simply to obtain at least one real T23 room with repeated A4792/A4920/A5888 cycles; then compare ordered exact-TM and TM* families and only afterwards build a prospective discriminator. Continue production audits unchanged.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v50.js',
 nextCopyId:'WOF-050',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V50 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules. Zero coverage is not forward failure. Do not promote from sparse T23 traces.',
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
